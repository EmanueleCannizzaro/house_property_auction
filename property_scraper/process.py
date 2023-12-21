

from bs4 import BeautifulSoup
from datetime import date, datetime
from glob import glob
from gspread import service_account
import json
#import linkcheck
from multiprocessing import Pool
import os
import pandas as pd
import subprocess
from subprocess import run
from tqdm.auto import tqdm



class Store:
    
    DEFAULT_CREDENTIALS = os.path.expanduser('~/gspreadscraper.json')
    DEFAULT_WORKBOOK = '1BRloTbcVOFAL9up2wIsvaAjFuJep9f3TWQwp_f02ntw'
    
    def __init__(self, name:str=None, credentials:str=None, workbook:str=None):
        self.name = name
        self.credentials = credentials
        self.workbook = workbook
        
        if not self.credentials:
           self.credentials = self.DEFAULT_CREDENTIALS
        gc = service_account(filename=self.credentials)
        
        if not self.workbook:
            self.workbook = self.DEFAULT_WORKBOOK

        workbook = gc.open_by_key(self.workbook)

class Configurator:
    def __init__(elf, name:str=None):
        self.name = name


class Extractor:
    def __init__(elf, name:str=None):
        self.name = name


class Fixer:
    def __init__(elf, name:str=None):
        self.name = name


class Checker:
    def __init__(elf, name:str=None):
        self.name = name


def is_downloaded(filename:str):
    return os.path.exists(filename)

def is_fixed(filename:str):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            text = f.read()
            if 'dettaglio_annuncio.page?' in text:
                return False
            else:
                return True
    else:
        return False
    
def get_parameter(key, url):
    parameters = get_parameters(url)
    if key in parameters.keys():
        return parameters[key][0]
    else:
        return None
    
def get_datetime(text):
    _datetime = text.split('.')[0].split('_')[-2]
    _datetime = datetime.strptime(_datetime, '%Y%m%d%H%M%S')
    return _datetime

def linkchecker(search_engine:str, urls:set, url_rootname:str, rootname:str):
    stdout_filename = f'../demos/{rootname}_linkchecker-output.txt'
    stderr_filename = f'../demos/{rootname}_linkchecker-error.txt'
    
    if os.path.exists(stdout_filename):
        os.remove(stdout_filename)
    if os.path.exists(stderr_filename):
        os.remove(stderr_filename)

    with open(stdout_filename, 'a') as of:
        with open(stderr_filename, 'a') as ef:
            pbar = tqdm(urls)
            for url in pbar:
                pbar.set_description(f"{url}")
                cmd = f"/usr/bin/linkchecker --verbose --output=csv {url_rootname}{url}"
                subprocess.run(cmd.split(' '), stdout=of, stderr=ef)

def read(filename:str, index:list=['id']):
    df = pd.read_csv(filename, header=None)
    display(df.head())
    print(f'The length of the original table is : {len(df):10}')
    df = df.drop_duplicates(keep='first')
    df.columns = list(df.loc[0].values)
    df = df.drop([0])    
    print(f'The length of the cleaned table with removed duplicates is : {len(df):10}')
    df = df.set_index(index)
    df = df.sort_index()
    _filename = filename.replace('.csv', '.temp.csv')
    if _filename == filename:
       raise ValueError(f'Please check the file {filename} as it should have a ".csv" extension.') 
    df.to_csv(_filename)
    df = pd.read_csv(_filename).set_index(index)
    os.remove(_filename)
    print(df.dtypes)
    display(df.head())
    return df

def repair_url(url, root:str='https://pvp.giustizia.it'):
    #/ -> 
    #http://localhost/pvp/pvp_property_LTT2515471.html -> /pvp/it/dettaglio_annuncio.page?geo=raggio&ordinamento=data_vendita_decre&view=tab&frame4_item=10565&searchresults=true&contentId=LTT2515471&elementiPerPagina=50&ordine_localita=a_z&raggio=25&tipo_bene=immobili
    if url.startswith('/'):
        _url = os.path.join(root, url)
        return _url
    elif url.startswith('http://localhost/pvp/pvp_property_'):
        contentId = url.split('_')[2].split('.')[0]
        #print(contentId)
        _url = f"{root}/pvp/it/dettaglio_annuncio.page?geo=raggio&ordinamento=data_vendita_decre&view=tab&frame4_item=10565&searchresults=true&contentId={contentId}&elementiPerPagina=50&ordine_localita=a_z&raggio=25&tipo_bene=immobili"
        return _url
    else:
        return url
    
def get_links(filename:str) -> list:
    links = set()
    with open(filename, 'r') as f:
        content = f.read()
        soup = BeautifulSoup(content)
        #pbar = tqdm(soup.find_all('a', href=True), position=0)
        #for link in pbar:
        for link in soup.find_all('a', {"href": True}):
            url = link['href']
            if not url.startswith('#'):
                links.add(link['href'])
    links = sorted(links)
    return links

def fix_broken_links(filename:str) -> list:
    with open(filename, 'r') as f:
        content = f.read()
        soup = BeautifulSoup(content)
        for link in soup.find_all('a', {"href": True}):
            url = repair_url(link['href'])
            if url != link['href']:
                link['href'] = url
    with open(filename, 'w') as f:
        f.write(soup.prettify())
        
def is_search_downloaded(filename:str):
    links = get_links(filename)
    rootname = os.path.dirname(filename)
    
    to_be_fixed = f'/dettaglio_annuncio.page?'
    keys = ['contentId']

    #pbar = tqdm(links, position=0)
    #for url in pbar:
    for url in links:
        if (to_be_fixed in url) or (f"{search_engine}_property_LTT" in url):
            if to_be_fixed in url:
                basename = get_filename_from_identifier(url, keys, f"{search_engine}_property")        
            elif f"{search_engine}_property_LTT" in url: 
                basename = os.path.basename(url)
            _filename = os.path.join(rootname, basename)
            if not os.path.exists(_filename):
                print(f"{url} -> {basename} -> {_filename}")
                return False
    return True

def searches_to_be_downloaded(missing):
    
    '''
    # / -> https://pvp.giustizia.it/
    #    
    # http://localhost/pvp/pvp_property_LTT2515471.html -> /pvp/it/dettaglio_annuncio.page?geo=raggio&
    #   ordinamento=data_vendita_decre&view=tab&frame4_item=10565&searchresults=true&contentId=LTT2515471&
    #   elementiPerPagina=50&ordine_localita=a_z&raggio=25&tipo_bene=immobili
    #
    '''
    
    urls = set()
    pbar = tqdm(missing, position= 0)
    for basename in pbar:
        filename = os.path.join(rootname, 'pvp', basename)
        pbar.set_description(basename)
        is_downloaded = is_search_downloaded(filename)
        if not is_downloaded:
            print(basename)
            fix_broken_links(filename)
            links = get_links(filename)
            #print('\n'.join(links[:1]))
            urls.add(basename)
    return sorted(urls)

