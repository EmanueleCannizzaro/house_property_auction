
import logging
from autologging import logged, TRACE, traced

from bs4 import BeautifulSoup
import pandas as pd
import requests
from tqdm.auto import tqdm

from property_scraper import DEFAULT_HTML_PARSER, MAX_TIMEOUT, PVP_URL_ROOTNAME, add_classes, sleep_randomly
from property_scraper.pvp_property import PVPProperty
from property_scraper.page import Page


@logged(logging.getLogger("property_scraper"))
class PVPPage(Page):
    
    URL_ROOTNAME = PVP_URL_ROOTNAME
    URL_ABSOLUTE_FLAG = False
    #SCRAPABLE_TAGS = ['div', 'a', 'span', 'button', 'ul', 'li']
    SCRAPABLE_CLASSES = {}
    #SCRAPABLE_HYPERLINK_CLASSES = [
    #    "in-card__title",
    #]
    SCRAPABLE_USELESS_CLASSES = [
        'full',
        'glyphicon-remove', 
        'fi', 
        'glyphicon-menu-right', 
        'visible-xs', 
        'more', 
        'col-md-9', 
        'modal-body', 
        'user-action', 
        'glyphicon-remove', 
        'fi', 
        'glyphicon-menu-right', 
        'visible-xs',
        'rel',
        'desc-lista',
        'col-md-8',
        'col-sm-8',
        'margin-top-20',
        'tile-dettaglio'        
    ]
    SCRAPABLE_CLASSES_WITH_DEFAULT_VALUE = {
    }
    '''
    SCRAPABLE_BY_VALUE = {
        'span': {
            #'Data di vendita': 'inline margin-left-10 font-green',
            #'Modalità Consegna': 'margin-left-10 inline font-black',
            #'Offerta minima': 'margin-left-10 inline font-blue',
            #'Rialzo minimo': 'margin-left-10 inline font-blue',
            #'N° Procedura': 'margin-left-10 inline font-black'
            #"Prezzo base d'asta": 'font-blue font18 inline margin-left-10'
            'Data di vendita': 'font-green',
            'Modalità Consegna': 'font-black',
            'Offerta minima': 'font-blue',
            'Rialzo minimo': 'font-blue',
            'N° Procedura': 'font-black',
            "Prezzo base d'asta": 'font-blue'
        }
    }
    '''
    RENAMED_COLUMNS = {
        'anagrafica-risultato_href': 'URL',
        'anagrafica-risultato_text': 'Indirizzo',
        'black_text': 'Lotto',
        #'font-green_text': 'Data di vendita',
        #'font-black_text': 'Modalità Consegna',
        #'margin-left-10 inline font-blue_text': 'Offerta minima',
        #'margin-left-10 inline font-blue_text': 'Rialzo minimo',
        #'margin-left-10': 'N° Procedura',
        #'font18_text': "Prezzo base d'asta"
    }
      
    def __init__(self, name:str=None):
        super(PVPPage, self).__init__()
        self.property = PVPProperty()

    '''
    txt = 'Data di vendita'
    _dates = [x.find('span', {'class': 'inline margin-left-10 font-green'}).text for x in soup.find_all('span', text=txt)]
    txt = 'Modalità Consegna'
    _auction_types = [x.find('span', {'class': 'margin-left-10 inline font-black'}).text for x in soup.find_all('span', text=txt)]
    txt = 'Offerta minima'
    _lowest_prices = [x.find('span', {'class': 'margin-left-10 inline font-blue'}).text for x in soup.find_all('span', text=txt)]
    txt = 'Rialzo minimo'
    _minimum raises = [x.find('span', {'class': 'margin-left-10 inline font-blue'}).text for x in soup.find_all('span', text=txt)]
    txt = 'N° Procedura'
    _references = [x.find('span', {'class': 'margin-left-10 inline font-black'}).text for x in soup.find_all('span', text=txt)]
    '''
