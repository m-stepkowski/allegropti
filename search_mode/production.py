# - *- coding: utf- 8 - *-

import pandas as pd
import numpy as np
import math
from suds.client import Client
from .models import Result
import slots


class Allegro:
    
    def __init__(self):
        self.api_key = "24a4466e"
        self.login = "Mathieu4"
        self.resultSize = 1000
        self.country_code = 1  # Poland
        self.country_id = 1  # Poland
        self.endpoint = 'https://webapi.allegro.pl/service.php?wsdl'
        self.client = Client(self.endpoint)

    def get_categories(self):
        # Pobieranie listy kategorii
        cat_list = self.client.service.doGetCatsData(self.country_code, 0, self.api_key).catsList.item
                   
        # Tworzenie struktury i umieszczenie w niej id i nazwy kategorii
        cats = []
     
        for cat in cat_list:
            cats.append({'categoryId': cat.catId, 'catName': cat.catName, 'catParent': cat.catParent})

        categories = pd.DataFrame(data=cats, columns=['categoryId', 'catName', 'catParent'])

        # Dodanie informacji o nadrzednej kategorii
        categories = pd.merge(left=categories, right=categories, left_on='catParent', right_on='categoryId',
                               suffixes=('', '_par'))[['categoryId', 'catName', 'catName_par']]
        
        return categories
        
    def download_auctions(self, filtr_query, pageNumber):
        # Pobieram informacje o produktach (maksymalnie w jednej iteracji 1000 produktow)
        result = self.client.service.doGetItemsList(self.api_key, self.country_code, filtr_query, 
                                      resultScope = 3, resultSize=self.resultSize, 
                                      resultOffset=pageNumber)
        
        #Licze ile jest aukcji i czy potrzeba pobrac wiecej informacji jesli jest to 1 iteracja
        if pageNumber == 0:
            # Jest to tez informacja o ilosci wszystkich aukcji, nawet tych bez oferty
            auc_cnt = result.itemsCount
            pages=int(math.ceil(auc_cnt/self.resultSize))
        
        # Informacje o znalezionych produktach
        a = result.itemsList[0]

        for i in range(0, len(a)):
            b = a[i]
            if i == 0:
                for j in range(0, len(b.priceInfo.item)):
                    results_tab = np.array([[b.itemId, b.bidsCount, b.categoryId, b.conditionInfo, b.priceInfo.item[j].priceType, b.priceInfo.item[j].priceValue]])
            else:
                for j in range(0, len(b.priceInfo.item)):
                    results_tab = np.concatenate((results_tab, np.array([[b.itemId, b.bidsCount, b.categoryId, b.conditionInfo, b.priceInfo.item[j].priceType, b.priceInfo.item[j].priceValue]])), axis=0)
        
        if pageNumber == 0:
            return results_tab, pages, auc_cnt
        else:
            return results_tab
        
    def search(self, fraza):
        #do tej tablicy mozna dopisac co sie chce i dowolnie edytowac
        tablica = {'search': fraza}
        filtr_query = self.client.factory.create('ArrayOfFilteroptionstype')

        for i in tablica:
            filtr = self.client.factory.create('FilterOptionsType')
            filtr.filterId = i
            filtrAOS = self.client.factory.create('ArrayOfString')
            filtrAOS.item = tablica[i]
            filtr.filterValueId = filtrAOS
            filtr_query.item.append(filtr)

        # Pobieram informacje o produktach
        wyniki_tab, pages, auc_cnt = self.download_auctions(filtr_query, 0)
        
        # Jesli jest wiecej niz 1000 rekordow - pobieram kolejne paczki
        if pages > 1:
            for r in range(1, pages-1):
                # Ze wzgledow wydajnosciowych przestaje pobierac paczki danych po maksymalnie 20 iteracjach
                if r > 20:
                    break
                b = self.download_auctions(filtr_query, r)
                wyniki_tab = np.concatenate((wyniki_tab, b), axis=0)
        
        # Odlozenie informacji o wyszukanych produktach    
        tab = pd.DataFrame(data=wyniki_tab, columns=['ItemId', 'bidsCount', 'categoryId', 'conditionInfo', 
                                                   'priceType', 'priceValue'])

        # Zmiana typu niektorych zmiennych na numeryczne
        tab['priceValue'] = tab['priceValue'].astype(float)
        tab['bidsCount'] = tab['bidsCount'].astype(int)
        tab['categoryId'] = tab['categoryId'].astype(int)

        # Wybranie aukcji, gdzie pojawily sie oferty kupna
        # Pominiecie cen z dostawa
        tab = tab[(tab.bidsCount > 0) & (tab.priceType != 'withDelivery')]

        # Zliczenie ilosci aukcji z co najmniej jedna oferta
        auc_off_cnt = len(tab)

        # Jesli mam jakiekolwiek rekordy wykonuje dalsze polecenia
        if auc_off_cnt > 0:

            # Sumowanie liczby ofert w danych kategoriach
            group_sum = tab[['categoryId','bidsCount']].groupby(['categoryId']).sum().reset_index()
            tab = pd.merge(left=tab, right=group_sum, left_on='categoryId', right_on='categoryId', 
                           suffixes=('_tab', '_grp'))

            # Wyliczenie udzialu ofert aukcji w danej kategorii
            tab['grp_pct']=(tab['bidsCount_tab']/tab['bidsCount_grp']).round(decimals=2)

            # Obliczenie prawdopodobienstwa kupna jako iloczyn udzialu w kategorii oraz udzialu aukcji
            # z ofertami do wszystkich aukcji dla danego wyszukiwania
            tab['prob_all']=( tab['grp_pct'] * ( auc_off_cnt / auc_cnt) ).round(decimals=2)

            # Utworzenie pustej tabeli na wyniki optymalizacji
            final_result = pd.DataFrame(columns=['categoryId', 'priceType', 'priceValue'])

            # Wybranie rekordow dla kazdej kategorii z osobna i wybranie najlepszej opcji przy pomocy 
            # algorytmu Multi-armed bandit
            for c in tab['categoryId'].unique():
                tab_cat = tab[tab.categoryId == c]
                # W optymalizacji bierzemy pod uwage tylko kategorie, gdzie jest wiecej niz jedna aukcja
                if len(tab_cat) > 1:
                    mab = slots.MAB(probs = tab_cat['prob_all'].tolist(), payouts = tab_cat['priceValue'].tolist(), live=False)
                    mab.run(strategy = 'eps_greedy', trials = 10000)
                    which = mab.best()
                    final_result.loc[len(final_result)]=[tab_cat[['categoryId', 'priceType', 'priceValue']].iloc[[0]].values[0][0],
                                     tab_cat[['categoryId', 'priceType', 'priceValue']].iloc[[0]].values[0][1],
                                        tab_cat[['categoryId', 'priceType', 'priceValue']].iloc[[0]].values[0][2]] 
                # Jesli mamy tylko jedna obserwacje, to staje sie ona optimum 
                else:
                    final_result.loc[len(final_result)]=[tab_cat[['categoryId', 'priceType', 'priceValue']].iloc[[0]].values[0][0],
                                     tab_cat[['categoryId', 'priceType', 'priceValue']].iloc[[0]].values[0][1],
                                        tab_cat[['categoryId', 'priceType', 'priceValue']].iloc[[0]].values[0][2]]

            # Pobranie informacji o kategoriach
            categories = self.get_categories()

            # Laczenie danych z informacja o kategoriach
            final = pd.merge(left=final_result, right=categories, left_on='categoryId', right_on='categoryId')

            # Sortowanie od najwyzszej kwoty
            final = final.sort(['priceValue'], ascending=False).reset_index()

            # Zmiana nazw kolumn zbioru do wyswietlenia
            final_show = final[['catName_par', 'catName', 'priceType', 'priceValue']].rename(columns={'catName_par': 'Kategoria', 
                                           'catName': 'Podkategoria', 'priceType': 'Rodzaj aukcji',
                                           'priceValue': 'Optymalna kwota wystawienia'})
            
            # Zainsertowanie informacji z wynikami optymalizacji do modelu
            for index, row in final.iterrows():
                r = Result(search_text=fraza, price_type=str(row['priceType']) ,category_id=int(row['categoryId']), value=float(row['priceValue']))
                r.save()
            
            # Utworzenie html z tabela ze srednimi
            html = final_show.to_html(classes='table-hover')

        # Jesli nie mam zadnej pobranej aukcji wyswietlam odpowiedni komunikat
        else:
            html = '<center><h3>Brak wyników wyszukiwania. Spróbuj ponownie, wprowadzając inną frazę na stronie głównej</h3><center>'


        # Zwracam html do pokazania na stronie
        return html
