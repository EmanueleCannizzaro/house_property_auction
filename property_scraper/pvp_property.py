
import logging
from autologging import logged, TRACE, traced

from bs4 import BeautifulSoup
from datetime import datetime
from lxml import etree, html
import numpy as np
import pandas as pd
import re
from tqdm import tqdm 

from property_scraper import DEFAULT_HTML_PARSER, PVP_URL_ROOTNAME
from property_scraper.property import Property


class PVPProperty(Property):

    URL_ROOTNAME = PVP_URL_ROOTNAME

    '''
    KEYWORDS = [
        'Inserzione N. ',
        'Dettaglio',
        'DETTAGLIO LOTTO',
        'LOTTO UNICO',
        'PUBBLICATO ANCHE IN',
        'Sito pubblicità',
        'DETTAGLIO VENDITA',
        'Gestore vendita telematica',
        'Beni inclusi nel lotto',
        'Prenota visita immobile',
        'Dettaglio',
        'DESCRIZIONE',
        'DETTAGLIO PROCEDURA',
        'REFERENTI',
        'ALLEGATI'
    ]
    '''
    
    SCRAPABLE_USELESS_CLASSES = [
        'slider-thumbs',
        'mask-overlay',  
        'hidden-xs',  
        'user-action',  
        'full-screen-image',  
        'logo-repubblica',  
        'img-responsive',  
        'flaticon-printer',  
        'close-image',  
        'glyphicon-menu-right',  
        'fi',  
        'close-menu',  
        'glyphicon-menu-down',  
        'glyphicon-map-marker',  
        'visible-xs',  
        'inline',  
        'glyphicon-plus',  
        'navbar-brand',  
        'col-xs-10',  
        'col-md-12',  
        'repubblica-cont',  
        'slider-thumbs', 
        'mask-overlay', 
        'hidden-xs', 
        'user-action', 
        'full-screen-image', 
        'logo-repubblica', 
        'img-responsive', 
        'flaticon-printer', 
        'close-image', 
        'glyphicon-menu-right', 
        'fi', 
        'close-menu', 
        'glyphicon-menu-down', 
        'glyphicon-map-marker', 
        'visible-xs', 
        'inline', 
        'glyphicon-plus', 
        'navbar-brand', 
        'col-xs-10', 
        'col-md-12',      
        'repubblica-cont'
    ]
  
    def __init__(self, name:str=None):
        super(PVPProperty, self).__init__()
        
    def get_property(self, response):
        content = response.body

        soup = BeautifulSoup(content, 'html.parser')            
        data = {}
    
        index = int(soup.find('h1', {'class': 'page-name'}).text.strip().split(' ')[-1])
        
        data['Title'], data['Description'] = [x.text.strip() for x in soup.find_all('p')][:2]
        
        urls = []
        for x in soup.find_all('a', {'class': 'btn'}):
            href = x['href']
            if not href.startswith('http'):
                href = self.URL_ROOTNAME + href
            if href not in urls:
                urls.append(href)
        try:
            data['Link a gestore vendita telematica'] = urls[0]
        except:
            data['Link a gestore vendita telematica'] = None
        try:
            data["Link per prenotazione della visita dell'immobile"] = urls[1]
        except:
            data["Link per prenotazione della visita dell'immobile"] = None
        
        urls = []
        for x in soup.find_all('div', {'class': 'info-box'}):
            for y in x.find_all('a'):
                href = y['href']
                if href.startswith('/'):
                    href = self.URL_ROOTNAME + href
                if href not in urls:
                    urls.append(href)
        data["Sito di vendita all'asta"] = ''
        data['Allegati'] = ''
        for url in urls:
            if url.lower().endswith('.pdf'):
                key = 'Allegati'
            else:
                key = "Sito di vendita all'asta"
            if data[key]:
                data[key] += f', {url}'
            else:
                data[key] += url

        data['Tipologia del lotto'], data['Dettaglio'] = [x.text.strip() for x in soup.find_all('div', {'class': 'anagrafica-dato'})][:2]
        
        _keys = [x.text.strip() for x in soup.find_all('div', {'class': 'anagrafica-dato'})][2:]
        _values = [x.text.strip() for x in soup.find_all('div', {'class': 'anagrafica-risultato'})]    
        kix, vix = 0, 0
        for ix in range(len(_keys)):
            k = _keys[kix]
            if k == 'Tipologia' :
                if 'Tipologia di vendita' in data.keys():
                    k += ' del lotto'
                else:
                    k += ' di vendita'
            if ix == 7:
                vix += 1
            data[k] = _values[vix]
            kix += 1
            vix += 1
            
        _df = pd.DataFrame(data, index=[index])
        _df.index.name = 'Reference'
            
        MISSING_COLUMNS = ['Link a gestore vendita telematica', 'Vani', 'Delegato alla vendita', 'Curatore', 'Superficie', 'Giudice']
        for cid in MISSING_COLUMNS:
            if cid not in _df.columns:
                _df[cid] = ''
        
        return _df
