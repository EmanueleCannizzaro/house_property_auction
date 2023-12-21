
import logging
from autologging import logged, TRACE, traced

from bs4 import BeautifulSoup
from datetime import datetime
import os
import pandas as pd
#import pprint
import re
#import requests
#from selenium import webdriver
from tqdm import tqdm 
#from urllib.parse import urljoin

from property_scraper import DEFAULT_HTML_PARSER, LOCALHOST_URL_ROOTNAME, MAX_TIMEOUT, RIGHTMOVE_URL_ROOTNAME, add_classes, remove_duplicated_whitespaces, sleep_randomly, to_currency


@logged(logging.getLogger("property_scraper"))
class Page():
    
    SCRAPABLE_CLASSES = {}
    SCRAPABLE_USELESS_CLASSES = []
    SCRAPABLE_CLASSES_WITH_DEFAULT_VALUE = {}
    RENAMED_COLUMNS = {}
    
    def __init__(self, name:str=None):
        self.name = name
        self.properties = None
    
    @staticmethod
    def get_all_tags(soup, exclude:list=[]):
        _classes = {}
        for child in soup.findChildren(None, recursive=True):
            key = child.name
            if key not in _classes.keys():
                _classes[key] = set()
            add_classes(_classes[key], child, exclude)
        classes = _classes.copy()
        for key in _classes.keys():
            if not _classes[key]:
                del classes[key]
        return classes

    def get_all_relevant_tags(self, soup, no_of_expected_items:int, exclude:list=[]):
        tags = self.get_all_tags(soup, exclude)
        relevant_tag = {}
        for key in tags.keys():
            for myclass in tags[key]:
                blocks = soup.find_all(key, {'class': myclass})
                if len(blocks) == no_of_expected_items:
                    if key not in relevant_tag.keys():
                        relevant_tag[key] = []
                    relevant_tag[key].append(myclass)
        return relevant_tag

    def get_properties(self, response, no_of_items):
        content = response.body
        data = {}
        soup = BeautifulSoup(content, 'html.parser')
        self.SCRAPABLE_CLASSES = self.get_all_relevant_tags(soup, no_of_items, self.SCRAPABLE_USELESS_CLASSES)
        for tag_key in self.SCRAPABLE_CLASSES.keys():
            for class_key in self.SCRAPABLE_CLASSES[tag_key]:
                #self.__log.info(f"{tag_key} -> {class_key}")
                for y in soup.find_all(tag_key, {"class": class_key}):
                    if hasattr(y, 'text'):
                        data[f"{class_key}_text"] = [x.text.strip() for x in soup.find_all(tag_key, {"class": class_key})]
                    if tag_key == 'a':
                        try:
                            data[f"{class_key}_href"] = [x['href'] for x in soup.find_all(tag_key, {"class": class_key})]
                            data[f"{class_key}_href"] = remove_duplicated_whitespaces(data[f"{class_key}_href"])
                        except:
                            pass
                    else:                            
                        try:
                            data[f"{class_key}_href"] = [x.find("a", href=True)["href"].strip() for x in soup.find_all(tag_key, {"class": class_key})]
                            data[f"{class_key}_href"] = remove_duplicated_whitespaces(data[f"{class_key}_href"])
                        except:
                            pass
                    if f"{class_key}_href" in data.keys():
                        if not self.URL_ABSOLUTE_FLAG:
                            data[f"{class_key}_href"] = [f'{self.URL_ROOTNAME}{x}' for x in data[f"{class_key}_href"]]
                        data[f"{class_key}_href"] = [f'{self.URL_ROOTNAME}{x}' if x.startswith('/') else x for x in data[f"{class_key}_href"]]
                        data[f"{class_key}_href"] = remove_duplicated_whitespaces(data[f"{class_key}_href"])
                    break

        for key in data.keys():
            if key not in self.SCRAPABLE_CLASSES_WITH_DEFAULT_VALUE.keys():
                data[key] = [x for x in data[key] if x]
            else:
                data[key] = [x for x in data[key] if x != self.SCRAPABLE_CLASSES_WITH_DEFAULT_VALUE[key]]
            data[key] = remove_duplicated_whitespaces(data[key])
                
        for key in data.keys():
            if len(data[key]) > no_of_items:
                data[key] = data[key][:no_of_items]
                print(f":::WARNING::: More values than expected have been found!")                
        
        for tag_key in self.SCRAPABLE_BY_VALUE.keys():
            print(tag_key)
            for value_key in self.SCRAPABLE_BY_VALUE[tag_key]:
                #print(tag_key, value_key)
                class_key = self.SCRAPABLE_BY_VALUE[tag_key][value_key]
                #print(tag_key, value_key, class_key)                
                #s = f"//{tag_key}[contains(text(), {value_key})]/{tag_key}/text()"
                #data[value_key] = response.xpath(s).getall()
                
        data["N° Procedura"] = remove_duplicated_whitespaces(response.xpath('//span[contains(text(), "N° Procedura")]/span/text()').getall())
        data["Data di vendita"] = remove_duplicated_whitespaces(response.xpath('//span[contains(text(), "Data di vendita")]/span/text()').getall())
        data["Modalità Consegna"] = remove_duplicated_whitespaces(response.xpath('//span[contains(text(), "Modalità Consegna")]/span/text()').getall())
        # To be fixed as it generate an error: decimal.InvalidOperation: [<class 'decimal.ConversionSyntax'>]
        data["Offerta minima"] = to_currency(remove_duplicated_whitespaces(response.xpath('//span[contains(text(), "Offerta minima")]/span/text()').getall()))
        data["Rialzo minimo"] = to_currency(remove_duplicated_whitespaces(response.xpath('//span[contains(text(), "Rialzo minimo")]/span/text()').getall()))
        data["Prezzo base d'asta"] = to_currency(remove_duplicated_whitespaces(response.xpath('//span[contains(text(), "Prezzo base d\'asta")]/span/text()').getall()))
        
        #for tag_key in self.SCRAPABLE_BY_VALUE.keys():
        #    for value_key in self.SCRAPABLE_BY_VALUE[tag_key]:
        #        print(data[value_key])

                
        # Store the data in a Pandas DataFrame:
        #data = data + [floorplan_urls] if get_floorplans else data
        if all([len(data[key]) == no_of_items for key in data.keys()]):
            results = pd.DataFrame(data)
        else:
            outputs = []
            for key in data.keys():                
                if len(data[key]) != no_of_items:                    
                    outputs.append(f"{key} -> {len(data[key])} vs. {no_of_items}")
                    print(f"{key} -> " + ', '.join(data[key]))
            print('\n'.join(outputs))
            results = pd.DataFrame(None, columns=list(data.keys()))
        
        results = results.rename(columns=self.RENAMED_COLUMNS)        

        results['Id'] = ''
        results['Search Id'] = ''
        results['URL'] = [response.url]
        results['Filename'] = ''
        results['Basename'] = results[['Filename']].apply(lambda x: os.path.basename(x[0]), axis=1)
        results['Localhost URL'] = results[['Basename']].apply(lambda x: os.path.join(LOCALHOST_URL_ROOTNAME, self.name, x[0]), axis=1)
        results['Downloaded?'] = False
        results['Relative HRef Fixed?'] = False
        results['Response Status Code'] = [200]

        # Add column with datetime when the search was run (i.e. now):
        now = datetime.now()
        results["Data della ricerca"] = str(now)
        
        #results["Offerta minima"] = results["Offerta minima"].astype(int)
        #results["Rialzo minimo"] = results["Rialzo minimo"].astype(int)
        #results["Prezzo base d'asta"] = results["Prezzo base d'asta"].astype(int)
        results["Data di vendita"] = pd.to_datetime(results["Data di vendita"]).dt.strftime('%Y-%m-%d %H:%M:%S')
        results["Data della ricerca"] = pd.to_datetime(results["Data della ricerca"]).dt.strftime('%Y-%m-%d %H:%M:%S')
        results['Hyperlink'] = results['Hyperlink'].astype(str)
        results['Indirizzo'] = results['Indirizzo'].astype(str)
        results['Lotto'] = results['Lotto'].astype(str)

        return results
        
    '''
    def get_properties(self, urls:list):
        dfs = []
        pbar = tqdm(urls)
        for url in pbar:
            r = requests.get(url, timeout=MAX_TIMEOUT)
            # Requests to scrape lots of pages eventually get status 400, so:
            if r.status_code != 200:
                raise ValueError('The request status code is {r.status_code}.')

            _df = self.property.get_data(content)
            dfs.append(_df)
            sleep_randomly()
        return pd.concat(dfs)
    '''
