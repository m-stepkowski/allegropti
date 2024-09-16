# - *- coding: utf- 8 - *-

import pandas as pd
import numpy as np
import math
from suds.client import Client
from .models import Result
import slots


class Allegro:

    def __init__(self):
        self.api_key = "API_KEY"
        self.login = "LOGIN"
        self.resultSize = 1000
        self.country_code = 1  # Poland
        self.country_id = 1  # Poland
        self.endpoint = 'https://webapi.allegro.pl/service.php?wsdl'
        self.client = Client(self.endpoint)

    def get_categories(self):
        # Retrieving the list of categories
        cat_list = self.client.service.doGetCatsData(self.country_code, 0, self.api_key).catsList.item

        # Creating a structure and placing category id and name in it
        cats = []

        for cat in cat_list:
            cats.append({'categoryId': cat.catId, 'catName': cat.catName, 'catParent': cat.catParent})

        categories = pd.DataFrame(data=cats, columns=['categoryId', 'catName', 'catParent'])

        # Adding information about the parent category
        categories = pd.merge(left=categories, right=categories, left_on='catParent', right_on='categoryId',
                               suffixes=('', '_par'))[['categoryId', 'catName', 'catName_par']]

        return categories

    def download_auctions(self, filtr_query, pageNumber):
        # Retrieving information about products (maximum 1000 products in one iteration)
        result = self.client.service.doGetItemsList(self.api_key, self.country_code, filtr_query,
                                      resultScope = 3, resultSize=self.resultSize,
                                      resultOffset=pageNumber)

        # Calculating how many auctions there are and if more information needs to be retrieved if it's the 1st iteration
        if pageNumber == 0:
            # This is also information about the number of all auctions, even those without an offer
            auc_cnt = result.itemsCount
            pages=int(math.ceil(auc_cnt/self.resultSize))

        # Information about found products
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
        # You can add whatever you want to this array and edit it freely
        tablica = {'search': fraza}
        filtr_query = self.client.factory.create('ArrayOfFilteroptionstype')

        for i in tablica:
            filtr = self.client.factory.create('FilterOptionsType')
            filtr.filterId = i
            filtrAOS = self.client.factory.create('ArrayOfString')
            filtrAOS.item = tablica[i]
            filtr.filterValueId = filtrAOS
            filtr_query.item.append(filtr)

        # Retrieving information about products
        wyniki_tab, pages, auc_cnt = self.download_auctions(filtr_query, 0)

        # If there are more than 1000 records - retrieving next batches
        if pages > 1:
            for r in range(1, pages-1):
                # For performance reasons, stop retrieving data batches after a maximum of 20 iterations
                if r > 20:
                    break
                b = self.download_auctions(filtr_query, r)
                wyniki_tab = np.concatenate((wyniki_tab, b), axis=0)

        # Storing information about searched products
        tab = pd.DataFrame(data=wyniki_tab, columns=['ItemId', 'bidsCount', 'categoryId', 'conditionInfo',
                                                   'priceType', 'priceValue'])

        # Changing the type of some variables to numeric
        tab['priceValue'] = tab['priceValue'].astype(float)
        tab['bidsCount'] = tab['bidsCount'].astype(int)
        tab['categoryId'] = tab['categoryId'].astype(int)

        # Selecting auctions where purchase offers appeared
        # Skipping prices with delivery
        tab = tab[(tab.bidsCount > 0) & (tab.priceType != 'withDelivery')]

        # Counting the number of auctions with at least one offer
        auc_off_cnt = len(tab)

        # If we have any records, perform further commands
        if auc_off_cnt > 0:

            # Summing the number of offers in given categories
            group_sum = tab[['categoryId','bidsCount']].groupby(['categoryId']).sum().reset_index()
            tab = pd.merge(left=tab, right=group_sum, left_on='categoryId', right_on='categoryId',
                           suffixes=('_tab', '_grp'))

            # Calculating the share of auction offers in a given category
            tab['grp_pct']=(tab['bidsCount_tab']/tab['bidsCount_grp']).round(decimals=2)

            # Calculating the probability of purchase as the product of the share in the category and the share of auctions
            # with offers to all auctions for a given search
            tab['prob_all']=( tab['grp_pct'] * ( auc_off_cnt / auc_cnt) ).round(decimals=2)

            # Creating an empty table for optimization results
            final_result = pd.DataFrame(columns=['categoryId', 'priceType', 'priceValue'])

            # Selecting records for each category separately and choosing the best option using
            # the Multi-Armed Bandit algorithm
            for c in tab['categoryId'].unique():
                tab_cat = tab[tab.categoryId == c]
                # In optimization, we consider only categories where there is more than one auction
                if len(tab_cat) > 1:
                    mab = slots.MAB(probs = tab_cat['prob_all'].tolist(), payouts = tab_cat['priceValue'].tolist(), live=False)
                    mab.run(strategy = 'eps_greedy', trials = 10000)
                    which = mab.best()
                    final_result.loc[len(final_result)]=[tab_cat[['categoryId', 'priceType', 'priceValue']].iloc[[0]].values[0][0],
                                     tab_cat[['categoryId', 'priceType', 'priceValue']].iloc[[0]].values[0][1],
                                        tab_cat[['categoryId', 'priceType', 'priceValue']].iloc[[0]].values[0][2]]
                # If we have only one observation, it becomes the optimum
                else:
                    final_result.loc[len(final_result)]=[tab_cat[['categoryId', 'priceType', 'priceValue']].iloc[[0]].values[0][0],
                                     tab_cat[['categoryId', 'priceType', 'priceValue']].iloc[[0]].values[0][1],
                                        tab_cat[['categoryId', 'priceType', 'priceValue']].iloc[[0]].values[0][2]]

            # Retrieving information about categories
            categories = self.get_categories()

            # Joining data with category information
            final = pd.merge(left=final_result, right=categories, left_on='categoryId', right_on='categoryId')

            # Sorting from the highest amount
            final = final.sort(['priceValue'], ascending=False).reset_index()

            # Changing column names of the set to display
            final_show = final[['catName_par', 'catName', 'priceType', 'priceValue']].rename(columns={'catName_par': 'Category',
                                           'catName': 'Subcategory', 'priceType': 'Auction type',
                                           'priceValue': 'Optimal listing amount'})

            # Inserting information with optimization results into the model
            for index, row in final.iterrows():
                r = Result(search_text=fraza, price_type=str(row['priceType']) ,category_id=int(row['categoryId']), value=float(row['priceValue']))
                r.save()

            # Creating html with a table of averages
            html = final_show.to_html(classes='table-hover')

        # If I don't have any retrieved auction, I display an appropriate message
        else:
            html = '<center><h3>No search results. Try again by entering a different phrase on the main page</h3><center>'


        # Returning html to show on the page
        return html
