# - *- coding: utf- 8 - *-

import pandas as pd
import numpy as np
from suds.client import Client


class Allegro:
    
    def __init__(self):
        self.api_key = "24a4466e"
        self.login = "Mathieu4"
        self.country_code = 1  # Poland
        self.country_id = 1  # Poland
        self.endpoint = 'https://webapi.allegro.pl/service.php?wsdl'
        self.client = Client(self.endpoint)
    def wyszukaj(self, fraza):
        #do tej tablicy mozna dopisac co sie chce i dowolnie edytowac
        tablica = {'condition':'new', 'search': fraza}
        filtr_query = self.client.factory.create('ArrayOfFilteroptionstype')

        for i in tablica:
            filtr = self.client.factory.create('FilterOptionsType')
            filtr.filterId = i
            filtrAOS = self.client.factory.create('ArrayOfString')
            filtrAOS.item = tablica[i]
            filtr.filterValueId = filtrAOS
            filtr_query.item.append(filtr)

        # Pobieram informacje o produktach (niestety maksymalnie mozna pobrac informacje o 1000 produktow)
        wynik = self.client.service.doGetItemsList(self.api_key, self.country_code, filtr_query, 
                                      resultScope = 3, resultSize=1000)

        # Informacje o znalezionych produktach
        a = wynik.itemsList[0]

        for i in range(0, len(a)):
            b = a[i]
            if i == 0:
                for j in range(0, len(b.priceInfo.item)):
                    wyniki_tab = np.array([[b.itemId, b.bidsCount, b.categoryId, b.conditionInfo, b.priceInfo.item[j].priceType, b.priceInfo.item[j].priceValue]])
            else:
                for j in range(0, len(b.priceInfo.item)):
                    wyniki_tab = np.concatenate((wyniki_tab, np.array([[b.itemId, b.bidsCount, b.categoryId, b.conditionInfo, b.priceInfo.item[j].priceType, b.priceInfo.item[j].priceValue]])), axis=0)
        
        # Odlozenie informacji o wyszukanych produktach    
        tab = pd.DataFrame(data=wyniki_tab, columns=['ItemId', 'bidsCount', 'categoryId', 'conditionInfo', 
                                                   'priceType', 'priceValue'])

        # Zmiana typu zmiennej z cena na 'float'
        tab['priceValue'] = tab['priceValue'].astype(float)

        # Pobranie informacji o sredniej cenie produktu w zaleznosci od typu ceny
        srednia = tab[['priceType','priceValue']].groupby('priceType').mean().round(decimals=2)
        
        # Utworzenie html z tabela ze srednimi
        html = srednia.to_html()

        # Zwracam html do pokazania na stronie
        return html  
                                        
