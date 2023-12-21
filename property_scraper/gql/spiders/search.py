# -*- coding: utf-8 -*-

import logging
import sys

from autologging import logged, traced
from datetime import datetime
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import json
#from math import floor 
import os
import pandas as pd
import scrapy
from scrapy import Spider
from tqdm.auto import tqdm


@traced
@logged
class GraphQLSearchSpider():
    URL = "https://www.encheres-publiques.com/back/graphql"
    NUMBER_OF_EXPECTED_RESULTS = 100
    QUERY_EVENEMENT_TOTAL = """
        query ($filters: EvenementFiltersInput) {
            result: evenements(filters: $filters) {
                filters {
                    type_de_vente(count: true)
                    __typename
                }
                __typename
            }
        }
    """
    QUERY_EVENEMENT_SEARCH = """
        query (
            $filters: EvenementFiltersInput
            $cursor: ID
            $sort: EvenementSortEnum
            $reverse: Boolean
        ) {
            evenements: evenements(
                filters: $filters
                first: 100
                cursor: $cursor
                sort: $sort
                reverse: $reverse
            ) {
                collection {
                    id
                    edit
                    titre
                    cover
                    statut
                    type
                    nbr_total_lots
                    prive
                    suivi
                    ouverture_date
                    fermeture_date
                    nbr_vues
                    nbr_suivis
                    organisateur {
                        id
                        nom
                        avatar
                        live
                        categorie
                        online
                        adresse {
                            id
                            text
                            ville
                            ville_slug
                            __typename
                        }
                        __typename
                    }
                    mosaique {
                        collection {
                            id
                            nom
                            mise_en_avant
                            photo
                            __typename
                        }
                        total
                        __typename
                    }
                    adresse {
                        id
                        ville
                        ville_slug
                        region
                        __typename
                    }
                    __typename
                }
                total
                __typename
            }
        }
    """
    QUERY_LOT_TOTAL = """
        query ($filters: LotFiltersInput) {
            result: lots(filters: $filters) {
                filters {
                    type_de_vente(count: true)
                    __typename
                }
                __typename
            }
        }
    """
    QUERY_LOT_SEARCH = """
        query (
            $filters: LotFiltersInput
            $cursor: ID
            $sort: LotSortEnum
            $reverse: Boolean
        ) {
            lots: lots(
                filters: $filters
                first: 100
                cursor: $cursor
                sort: $sort
                reverse: $reverse
            ) {
                collection {
                    id
                    en_surenchere
                    statut
                    resultat          
                    termine
                    edit
                    suivi
                    nom
                    categorie
                    sous_categorie
                    appel_offres
                    adresse_defaut {
                        id
                        ville
                        ville_slug
                        __typename
                    }
                    criteres_resume
                    numero
                    prive
                    en_surenchere
                    ouverture_date
                    fermeture_reelle_date
                    nbr_vues
                    nbr_suivis
                    nbr_photos
                    mise_a_prix
                    estimation_basse
                    estimation_haute
                    prix_adjuge
                    mise_en_avant
                    vendeur {
                        id
                        avatar
                        live
                        nom
                        suivi
                        categorie
                        online
                        adresse {
                            id
                            ville
                            ville_slug
                            __typename
                        }
                        messages_desactives
                        __typename
                    }
                    photo
                    evenement {
                        id
                        edit
                        type_de_vente
                        type
                        ouverture_date
                        fermeture_date
                        __typename
                    }
                    __typename
                }
                total
                __typename
            }      
        }
    """
    
    def __init__(self, name:str='gql_spider'):
        self.name = name
        # Select your transport with a defined url endpoint
        self.transport = AIOHTTPTransport(url=self.URL)
        # Create a GraphQL client using the defined transport
        self.client = Client(transport=self.transport, fetch_schema_from_transport=False)        

    def create_parameters(self, cursor:str, query_type:str='lot', place:str="partout", termine:bool=False):
        if query_type == 'lot':
            _parameters = {
                "sort": "ouverture_date",
                "reverse": False,
                "filters": {
                    "place": place,
                    "categorie": "immobilier",
                    "sous_categorie": "",
                    "encheres_format_de_vente": "",
                    "favoris_profil": False,
                    "ventes": None, #"volontaires", "judiciaires"
                    "termine": termine
                }
            }
        elif query_type == 'evenement':
            _parameters = {
                "sort": "ouverture_date",
                "reverse": False,
                "filters": {
                    "place": place,
                    "categorie": "immobilier",
                    "sous_categorie": "",
                    "favoris_profil": False,
                    "ventes": "",
                    "type": "",
                    "periode": "tous"
                }
            }
        
        if cursor:
            _parameters["cursor"] = cursor
        return _parameters

    def execute_query(self, query:str):
        # Provide a GraphQL query
        result = gql(query)
        return result

    @staticmethod
    def fix_dates(df:pd.DataFrame):
        date_columns = ['ouverture_date', 'fermeture_reelle_date', 'evenement.ouverture_date', 'evenement.fermeture_date']
        for cid in date_columns:
            if cid in df.columns:
                df[cid] = pd.to_datetime(df[cid], unit='s')
        return df
    
    async def get_encheres(self):
        query_total = self.execute_query(self.QUERY_LOT_TOTAL)
        parameters = self.create_parameters(None)
        # Execute the query on the transport
        encheres = await self.client.execute_async(query_total, variable_values=parameters)
        #print(len(encheres))
        self.__log.info(json.dumps(encheres, indent=4))
        for key in encheres['result']['filters']['type_de_vente'].keys():
            self.__log.info(f"{key} -> {encheres['result']['filters']['type_de_vente'][key]}")
        cursor = None
        ix = 0
        counter = 0
        _results = []
        _dfs = []
        query = self.execute_query(self.QUERY_LOT_SEARCH)
        while True:
            # Execute the query on the transport
            parameters = self.create_parameters(cursor)
            result = await self.client.execute_async(query, variable_values=parameters)
            if ix == 0:
                total = result['lots']['total']
                pbar = tqdm(total=total)
            _results.append(result['lots']['collection'])
            _dfs.append(pd.json_normalize(_results[-1]))
            number_of_results = len(result['lots']['collection'])
            counter += number_of_results
            cursor = result['lots']['collection'][-1]['id']
            pbar.set_description(f"{counter} / {total} -> cursor : {cursor}")
            self.__log.info(f"{counter} / {total} -> cursor : {cursor}")
            pbar.update(number_of_results)
            ix += 1
            if number_of_results != self.NUMBER_OF_EXPECTED_RESULTS:
                break
        encheres = pd.concat(_dfs)
        encheres = self.fix_dates(encheres)
        return encheres
    
    async def get_resultats(self):
        query_total = self.execute_query(self.QUERY_LOT_TOTAL)
        cursor = None
        parameters = self.create_parameters(cursor, place="", termine=True)
        # Execute the query on the transport
        resultats = await self.client.execute_async(query_total, variable_values=parameters)
        #print(len(resultats))
        self.__log.info(json.dumps(resultats, indent=4))
        for key in resultats['result']['filters']['type_de_vente'].keys():
            self.__log.info(f"{key} -> {resultats['result']['filters']['type_de_vente'][key]}")
        ix = 0
        counter = 0
        _results = []
        _dfs = []
        query = self.execute_query(self.QUERY_LOT_SEARCH)
        while True:
            # Execute the query on the transport
            parameters = self.create_parameters(cursor, place="", termine=True)
            result = await self.client.execute_async(query, variable_values=parameters)
            if ix == 0:
                total = result['lots']['total']
                pbar = tqdm(total=total)
            _results.append(result['lots']['collection'])
            _dfs.append(pd.json_normalize(_results[-1]))
            number_of_results = len(result['lots']['collection'])
            counter += number_of_results
            cursor = result['lots']['collection'][-1]['id']
            pbar.set_description(f"{counter} / {total} -> cursor : {cursor}")
            self.__log.info(f"{counter} / {total} -> cursor : {cursor}")
            pbar.update(number_of_results)
            ix += 1
            if number_of_results != self.NUMBER_OF_EXPECTED_RESULTS:
                break
        results = pd.concat(_dfs)
        results = self.fix_dates(results)
        return results
    
    async def get_evenements(self):
        query_total = self.execute_query(self.QUERY_EVENEMENT_TOTAL)
        cursor = None
        parameters = self.create_parameters(cursor, query_type='evenement', place="")
        # Execute the query on the transport
        evenements = await self.client.execute_async(query_total, variable_values=parameters)
        #print(len(evenements))
        self.__log.info(json.dumps(evenements, indent=4))
        for key in evenements['result']['filters']['type_de_vente'].keys():
            self.__log.warning(f"{key} -> {evenements['result']['filters']['type_de_vente'][key]}")
        ix = 0
        counter = 0
        _results = []
        _dfs = []
        query = self.execute_query(self.QUERY_EVENEMENT_SEARCH)
        while True:
            # Execute the query on the transport
            parameters = self.create_parameters(cursor, query_type='evenement', place="")
            result = await self.client.execute_async(query, variable_values=parameters)
            #print(json.dumps(result, indent=4))
            if ix == 0:
                total = result['evenements']['total']
                pbar = tqdm(total=total)
            _results.append(result['evenements']['collection'])
            _dfs.append(pd.json_normalize(_results[-1]))
            number_of_results = len(result['evenements']['collection'])
            counter += number_of_results
            cursor = result['evenements']['collection'][-1]['id']
            pbar.set_description(f"{counter} / {total} -> cursor : {cursor}")
            self.__log.info(f"{counter} / {total} -> cursor : {cursor}")
            pbar.update(number_of_results)
            ix += 1
            if number_of_results != self.NUMBER_OF_EXPECTED_RESULTS:
                break
        results = pd.concat(_dfs)
        results = self.fix_dates(results)
        return results
     

if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.settings import Settings
    from scrapy.utils.log import configure_logging
    
    #logging.disable(logging.CRITICAL)
    configure_logging()
    
    # Load the settings file
    settings = Settings()
    settings_module_path = 'property_scraper.gql.settings'
    # Replace with your actual settings module path
    settings.setmodule(settings_module_path)

    # Create a crawler process with the loaded settings
    process = CrawlerProcess(settings)

    # Add your spider(s) to the crawler process
    process.crawl(GraphQLSearchSpider)

    # Start the crawler process    
    process.start()

