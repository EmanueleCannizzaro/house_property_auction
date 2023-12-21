
import logging
from autologging import logged, TRACE, traced

from bs4 import BeautifulSoup
from datetime import datetime
import json
from lxml import etree, html
from lxml.etree import tostring
import numpy as np
import pandas as pd
import re
import requests
from time import sleep
from tqdm.auto import tqdm

from property_scraper import DEFAULT_GEOCODE_ENGINE, DEFAULT_HTML_PARSER, PVP_URL_ROOTNAME
from property_scraper.io import get_worksheet
from property_scraper.pvp_page import PVPPage
from property_scraper.scraper import Scraper


@logged(logging.getLogger("property_scraper"))
class PVPScraper(Scraper):
    """The `PVP` webscraper collects structured data on properties
    returned by a search performed on www.rightmove.co.uk

    An instance of the class provides attributes to access data from the search
    results, the most useful being `get_results`, which returns all results as a
    Pandas DataFrame object.

    The query to rightmove can be renewed by calling the `refresh_data` method.
    """
    
    URL_ROOTNAME = PVP_URL_ROOTNAME

    KEYS = [
        'indirizzo',
        'tipo_bene',
        'categoria',
        'geo',
        'lat',
        'lng',
        'raggio',
        'prezzo_da',
        'prezzo_a',
        'tribunale',
        'procedura',
        'anno',
        'idInserzione',
        'ricerca_libera',
        'disponibilita',
        'ordinamento',
        'ordine_localita',
        'view',
        'elementiPerPagina'
    ]
    SHEETNAMES = {
        'Search': 'pvp_search',
        'Search Summary': 'pvp_summary',
        'Search Details': 'pvp_details',
        'Database': 'pvp'
    }
    HEADERS = {
        'Search': [
            'Filename', 
            'Basename', 
            'Id',
            'Localhost URL', 
            'Downloaded?', 
            'Relative HRef Fixed?', 
            'Response Status Code',
            'Motore di Ricerca', 
            'Location', 
            'Page Id', 
            'Number of Results', 
            'Number of Pages', 
            'Number of Results per Page', 
            'URL'
        ],
        'Search Summary': [
            'Id',
            'Search Id', 
            'Localhost URL',
            'Filename',
            'Indirizzo',
            'Lotto',
            'Data di vendita', 
            'Modalità Consegna', 
            'Offerta minima', 
            'Rialzo minimo', 
            'N° Procedura',
            "Prezzo base d'asta",
            'Data della ricerca',
            'URL'
        ],
        'Search Details': [
            'Title', 'Description', 'Link a gestore vendita telematica', "Sito di vendita all'asta", 'Allegati', 
            'Tipologia del lotto', 'Dettaglio', 'Tipologia di vendita', 'Data di vendita', 
            "Prezzo base d'asta", 'Offerta minima', 'Rialzo minimo', 'Modalità di vendita', 'Termine presentazione offerta', 
            'Superficie', 'Vani', 'Tipo Procedura', 'N° Procedura', 'Tribunale', 'Lotto nr.', 
            'Pubblicato sul Portale il', 'Delegato alla vendita', 
            'Custode', 'Telefono mobile custode', 'Telefono custode', 'Email custode', 'Giudice', 
            'Curatore'],
        'Database': []
    }
        
    HEADERS['Search'] += KEYS
    
    # There are 25 results per page.
    NUMBER_OF_RESULTS_PER_PAGE = 50
    ## Rightmove will return a maximum of 42 results pages
    MAXIMUM_NUMBER_OF_PAGES = 42
    ##PROTOCOLS = ["http", "https"]
    PROPERTY_TYPES = ["property-to-rent", "vendita-case", "new-homes-for-sale"]    
    
    NUMBER_OF_RESULTS = {
        'tag' : 'span', 
        'attribute': 'class',
        'value': 'font-green'
    }

    SEARCH_NAMES = {
        'basename': 'Basename',
        'filename': 'Filename',
        'id': 'Identificativo',
        'is_downloaded': 'Scaricato?',
        'is_relative_href_fixed': 'Hyperlink relativo riparato?',
        'location': "Localita' estratta dal nome del file",
        'number_of_pages': 'Numero di Pagine',
        'number_of_results': 'Numero di Risultati',
        'number_of_results_per_page': 'Numero di Risultati per Pagina',
        'page_id': 'Identificativo della Pagina',
        'response_status_code': 'Codice dello Stato della Risposta',
        'spider_name': 'Nome del Ragno',
        'url': 'URL',
        'url_localhost': 'Localhost URL',

        #'data_della_ricerca': 'Data della ricerca',
        #'data_di_vendita': 'Data di vendita',
        'elementiPerPagina': 'Numero di Elementi per Pagina',
        'frame4_item': 'Frame4 Item',
        #'frame4_item': 'Frame4 item',
        'geo': 'Geolocazione',
        'id': 'Identificativo',
        #'indirizzo': 'Indirizzo',
        "localita'": "Localita'",
        #'lotto': 'Lotto',
        #'modalita_consegna': 'Modalità consegna',
        'nazione': 'Nazione',
        #'numero_di_procedura': 'Numero della procedura',
        #'offerta_minima': 'Offerta minima',
        'ordinamento': 'Ordinamento',
        "ordine_localita'": "Ordine Localita'",
        #'ordine_localita': "Ordine localita'",
        #'prezzo_base': 'Prezzo Base',
        'raggio': 'Raggio',
        #'rialzo_minimo': 'Rialzo minimo',
        'search_id': 'Identificativo della ricerca',
        'tipo_bene': 'Tipo del Bene',
        #'tipo_bene': 'Tipo del bene',
        'view': 'Vista'
    }
    
    SEARCH_PROPERTY_NAMES = SEARCH_NAMES
    SEARCH_PROPERTY_NAMES['data_della_ricerca'] = 'Data della ricerca'
    SEARCH_PROPERTY_NAMES['indirizzo'] = 'Indirizzo'
    SEARCH_PROPERTY_NAMES['lotto'] = 'Lotto'
    SEARCH_PROPERTY_NAMES['modalita_consegna'] = 'Modalità consegna'
    SEARCH_PROPERTY_NAMES['numero_di_procedura'] = 'Numero della procedura'
    SEARCH_PROPERTY_NAMES['offerta_minima'] = 'Offerta minima'
    SEARCH_PROPERTY_NAMES['prezzo_base'] = 'Prezzo base'
    SEARCH_PROPERTY_NAMES['rialzo_minimo'] = 'Rialzo minimo'
    
    PROPERTY_NAMES = SEARCH_PROPERTY_NAMES
    PROPERTY_NAMES['allegati'] = 'Allegati'
    PROPERTY_NAMES['allegati_url'] = 'Allegati URL'
    PROPERTY_NAMES['bene_descrizione'] = 'Descrizione del bene'
    PROPERTY_NAMES['bene_disponibilita'] = 'Disponibilit del bene'
    PROPERTY_NAMES['bene_foglio'] = 'Foglio'
    PROPERTY_NAMES['bene_particella'] = 'Particella'
    PROPERTY_NAMES['bene_piano'] = 'Piano'
    PROPERTY_NAMES['bene_sub'] = 'Sub'
    PROPERTY_NAMES['bene_tipologia'] = 'Tipologia'
    PROPERTY_NAMES['custode'] = 'Custode'
    PROPERTY_NAMES['custode_email'] = 'Email del custode'
    PROPERTY_NAMES['custode_telefono'] = 'Telefono del custode'
    PROPERTY_NAMES['custode_telefono_mobile'] = 'Telefono mobile del custode'
    PROPERTY_NAMES['data_di_vendita'] = 'Data di vendita'
    PROPERTY_NAMES['data_pubblicazione_sul_portale'] = 'Data pubblicazione sul portale'
    PROPERTY_NAMES['delegato_alla_vendita'] = 'Delegato alla vendita'
    PROPERTY_NAMES['descrizione'] = 
    PROPERTY_NAMES['dettaglio'] = 
    PROPERTY_NAMES['dettaglio_lotto'] = 
    PROPERTY_NAMES['esecuzione	filename'] = 
    PROPERTY_NAMES['id'] = 
    PROPERTY_NAMES['indirizzo'] = 
    PROPERTY_NAMES['inserzione'] = 
    PROPERTY_NAMES['is_downloaded'] = 
    PROPERTY_NAMES['is_relative_href_fixed'] = 
    PROPERTY_NAMES['luogo_vendita'] = 
    PROPERTY_NAMES['modalita_di_vendita'] = 
    PROPERTY_NAMES['numero_lotto'] = 
    PROPERTY_NAMES['numero_procedura'] = 
    PROPERTY_NAMES['pubblicato_in'] = 
    PROPERTY_NAMES['pubblicato_in_url'] = 
    PROPERTY_NAMES['response_status_code'] = 
    PROPERTY_NAMES['termine_presentazione_offerta'] = 
    PROPERTY_NAMES['tipo_procedura'] = 
    PROPERTY_NAMES['tipologia'] = 'Tipologia'
    PROPERTY_NAMES['tribunale'] = 'Tribunale'

    # worksheets = {}
    # worksheets['Search'] = get_worksheet(scraper.SHEETNAMES['Search'])
    ##worksheets['Search'].clear()
    ##worksheets['Search'].append_row(scraper.HEADERS['Search'])

    # worksheets['Search Summary'] = get_worksheet(scraper.SHEETNAMES['Search Summary'])
    ##worksheets['Search Summary'].clear()
    ##worksheets['Search Summary'].append_row(scraper.HEADERS['Search Summary'])

    #worksheets['Search Details'] = get_worksheet(scraper.SHEETNAMES['Search Details'])
    ## worksheets['Search Details'].clear()
    ## worksheets['Search Details'].append_row(scraper.HEADERS['Search Details'])

    '''
    basename = os.path.basename(filename)
    property = self.property.get_property(response)
    property['Filename'] = filename
    property['Basename'] = basename
    property['Id'] = basename
    _COLUMNS = self.worksheets['Search Details'].row_values(1)
    if not property.empty:
        self.worksheets['Search Details'].append_rows(property[_COLUMNS].values.tolist())
    '''


    def __init__(self, name:str=None):
        super(PVPScraper, self).__init__()
        self.page = PVPPage()
        
        self._property_type = self.PROPERTY_TYPES[1]

    def set_url(self, parameters:dict):        
        _url = f"{self.URL_ROOTNAME}/pvp/en/risultati_ricerca.page?"        
        count = 0
        for ix in range(len(self.KEYS)):
            key = self.KEYS[ix]
            if key in parameters.keys():
                if parameters[key]:
                    if count > 0:
                        _url += f"&{key}={parameters[key]}"
                    else:
                        _url += f"{key}={parameters[key]}"
                    count += 1
        return _url

    def read_parameters(self, filename:str):
        _parameters = super(PVPScraper, self).read_parameters(filename)
        self.location = _parameters["indirizzo"]
        self.country = _parameters["paese"]
        self.property_type = _parameters["vendita_o_affitto"]
        if hasattr(self, 'REGIONS'):
            self.region = self.REGIONS[_parameters['location']]
        return _parameters

    #SHEETNAMES['Database']


    '''

    def get_next_search_page(self, ix):
        return str(self.url)

    def get_results(self, engine:str=DEFAULT_HTML_PARSER):
        """Build a Pandas DataFrame with all results returned by the search."""

        # Iterate through all pages scraping results:
        _pages = []
        self.status_code, self.content = self.get_request(self.url)
        _page = self.page.get_page(self.content, self._property_type, self.number_of_batches[0], engine)
        _pages.append(_page)
        pbar = tqdm(range(1, self.number_of_pages), position=0)
        for ix in pbar:
            # Create the URL of the specific results page:
            _url = f"{str(self.url)}&index={ix * self.NUMBER_OF_RESULTS_PER_PAGE}"
            self.__log.info(f"{_url}")

            # Make the request:
            self.status_code, self.content = self.get_request(_url)
            _page = self.page.get_page(self.content, self._property_type, self.number_of_batches[ix], engine)
            _pages.append(_page)
            
            sleep(self.WAITING_TIME)

        # Concatenate the temporary DataFrame with the full DataFrame:
        _results = pd.concat(_pages)
        _results = _results.drop_duplicates(keep='first')
        _results = _results.reset_index()
        return _results
        
    def scrape(self, html_engine:str=DEFAULT_HTML_PARSER, map_engine:str=DEFAULT_GEOCODE_ENGINE, api_key:str=None):
        """Initialize the scraper with a URL from the results of a property
        search performed on www.rightmove.co.uk.

        Args:
            url (str): full HTML link to a page of rightmove search results.
            get_floorplans (bool): optionally scrape links to the individual
                floor plan images for each listing (be warned this drastically
                increases runtime so is False by default).
        """

        self.status_code, self.content = self.get_request(self.url)
        
        self.__log.info(f"Found {self.number_of_results} results in {self.number_of_pages} pages.")
        self.__log.info("Number of branches is : " + ", ".join([str(x) for x in self.number_of_batches]))
        
        _results = self.get_results(html_engine)
        self.__log.info('\n'.join(sorted([str(x) for x in _results['Hyperlink'].unique()])))
        _results = self.fix_results(_results)
        _results = self.enrich_results(_results, html_engine, map_engine, api_key)
        return _results
    '''