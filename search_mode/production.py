# - *- coding: utf- 8 - *-

import pandas as pd
import numpy as np
import math
from suds.client import Client


class Allegro:
    
    def __init__(self):
        self.api_key = "24a4466e"
        self.login = "Mathieu4"
        self.resultSize = 1000
        self.country_code = 1  # Poland
        self.country_id = 1  # Poland
        self.endpoint = 'https://webapi.allegro.pl/service.php?wsdl'
        self.client = Client(self.endpoint)
        
    def download_auctions(self, filtr_query, pageNumber):
        # Pobieram informacje o produktach (maksymalnie w jednej iteracji 1000 produktow)
        result = self.client.service.doGetItemsList(self.api_key, self.country_code, filtr_query, 
                                      resultScope = 3, resultSize=self.resultSize, 
                                      resultOffset=pageNumber)
        
        #Licze ile jest aukcji i czy potrzeba pobrac wiecej informacji jesli jest to 1 iteracja
        if pageNumber == 0:
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
            return results_tab, pages
        else:
            return results_tab
        
    def wyszukaj(self, fraza):
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
        wyniki_tab, pages = self.download_auctions(filtr_query, 0)
        
        # Jesli jest wiecej niz 1000 rekordow - pobieram kolejne paczki
        if pages > 1:
            for r in range(1, pages-1):
                 b = self.download_auctions(filtr_query, r)
                 wyniki_tab = np.concatenate((wyniki_tab, b), axis=0)
        
        # Odlozenie informacji o wyszukanych produktach    
        tab = pd.DataFrame(data=wyniki_tab, columns=['ItemId', 'bidsCount', 'categoryId', 'conditionInfo', 
                                                   'priceType', 'priceValue'])

        # Zmiana typu zmiennej z cena na 'float'
        tab['priceValue'] = tab['priceValue'].astype(float)

        # Pobranie informacji o sredniej cenie produktu w zaleznosci od typu ceny
        srednia = tab[['priceType','priceValue']].groupby('priceType').mean().round(decimals=2)
        
        # Utworzenie html z tabela ze srednimi
        html = srednia.to_html(classes='table-hover')

        # Zwracam html do pokazania na stronie
        return html
