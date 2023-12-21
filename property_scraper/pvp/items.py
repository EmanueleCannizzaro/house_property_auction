# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from datetime import datetime, date
import re
#import scrapy
from pydantic import BaseModel, validator
from scrapy.item import Item, Field
#from scrapy.loader.processors import Join, MapCompose, TakeFirst
from itemloaders.processors import MapCompose, TakeFirst
from typing import List, Optional
from urllib.parse import urljoin
from w3lib.html import remove_tags

from property_scraper import PVP_URL_ROOTNAME


def remove_inserzione(text):
    return text.replace('Inserzione N.', '')

def title(text):
    return text.title()

def strip(text):
    s = text.strip()
    s = s.replace('\n', '').replace('\r', '')
    s = re.sub("\s\s+", " ", s)
    return s

def join_allegati(l):
    if isinstance(l, list):
        return '::'.join([strip(x) for x in l if strip(x)])
    else:
        return l

def remove_null(value):
    if value:
        return value
    else:
        return None

def remove_currency(value):
    return float(value.replace('.', '').replace(',', '.').replace('€', '').strip())

def fix_relative_hyperlink(url:str):
    if url.startswith('/'):
        return urljoin(PVP_URL_ROOTNAME, url)
    else:
        return url

def description_in(d):
    return d.strip()

def description_out(d):
    labels = d[0:3]
    values = d[3:]
    output = {
        labels[0]: "".join(values[0]),
        labels[1]: " ".join(values[1:-1]),
        labels[2]: "".join(values[-1])
    }
    return output


class PVPSearchItem(Item):
    items = {
        'css': {
            'location': None,
            'number_of_pages': None,
            'number_of_results': None,
            'number_of_results_per_page': None,
            'page_id': None,
            'url': 'div.anagrafica-risultato a::attr(href)',
        },
        'xpath': {
        },
        'value': {
            'basename': None,
            'filename': None,
            'id': None,
            'is_downloaded': None,
            'is_relative_href_fixed': None,
            'response_status_code': None,
            'spider_name': None,
            'url_localhost': None,
        }
    }

    '''def __init__(self):
        super(PVPSearchItem, self).__init__()
        # Add these attributes dynamically
        for tkey in self.items.keys():
            for key in self.items[tkey].keys():
                pass
                #setattr(self, key, Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst()))
    '''
    basename = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    filename = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    id = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    is_downloaded = Field(input_processor=MapCompose(bool), output_processor=TakeFirst())
    is_relative_href_fixed = Field(input_processor=MapCompose(bool), output_processor=TakeFirst())
    location = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    number_of_pages = Field(input_processor=MapCompose(int), output_processor=TakeFirst())
    number_of_results = Field(input_processor=MapCompose(int), output_processor=TakeFirst())
    number_of_results_per_page = Field(input_processor=MapCompose(int), output_processor=TakeFirst())
    page_id = Field(input_processor=MapCompose(int), output_processor=TakeFirst())
    response_status_code = Field(input_processor=MapCompose(int), output_processor=TakeFirst())
    spider_name = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    url = Field(input_processor=MapCompose(remove_tags, strip, fix_relative_hyperlink), output_processor=TakeFirst())
    url_localhost = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())


class PVPSearchModel(BaseModel):
    basename : str
    filename : str
    id : str
    is_downloaded : bool
    is_relative_href_fixed : bool
    location : str
    number_of_pages : int
    number_of_results : int
    number_of_results_per_page : int
    page_id : int
    response_status_code : int
    spider_name :str
    url : str
    url_localhost : str

    @validator('basename')
    def validate_basename(cls, value):
        if '/' in value:
            raise ValueError('Basename cannot contain folder.')
        return value

    @validator('filename')
    def validate_filename(cls, value):
        if value is None:
            raise ValueError('Filename cannot be null.')
        return value

    @validator('id')
    def validate_id(cls, value):
        if value is None:
            raise ValueError('Id cannot be null.')
        return value

    @validator('is_downloaded')
    def validate_is_downloaded(cls, value):
        if value not in [True, False]:
            raise ValueError('Is_downloaded must be a boolean.')
        return value

    @validator('is_relative_href_fixed')
    def validate_is_relative_href_fixed(cls, value):
        if value not in [True, False]:
            raise ValueError('Is_relative_href_fixed must be a boolean.')
        return value

    @validator('number_of_pages')
    def validate_number_of_pages(cls, value):
        if value <= 0:
            raise ValueError('Number of pages must be greater than zero.')
        return value

    @validator('number_of_results')
    def validate_number_of_results(cls, value):
        if value <= 0:
            raise ValueError('Number of results must be greater than zero.')
        return value

    @validator('number_of_results_per_page')
    def validate_number_of_results_per_page(cls, value):
        if value <= 0:
            raise ValueError('Number of results_per_page must be greater than zero.')
        return value

    @validator('page_id')
    def validate_page_id(cls, value):
        if value <= 0:
            raise ValueError('Page_id must be greater than zero.')
        return value
    
    @validator('response_status_code')
    def validate_response_status_code(cls, value):
        if value <= 0:
            raise ValueError('Response_status_code must be greater than zero.')
        return value
    
    @validator('spider_name')
    def validate_spider_name(cls, value):
        if value <= 0:
            raise ValueError('Spider_name must be greater than zero.')
        return value
    
    @validator('url')
    def validate_url(cls, value):
        #if value <= 0:
        #    raise ValueError('Url must be greater than zero.')
        return value
    
    @validator('url_localhost')
    def validate_url_localhost(cls, value):
        #if value <= 0:
        #    raise ValueError('Url_localhost must be greater than zero.')
        return value

class PVPSearchPropertyItem(Item):
    items = {
        'css': {
        },
        'xpath': {
            'categoria': '//span[@class="categoria"]/text()',
            'data_di_vendita': '//span[contains(text(), "Data di vendita")]//span[@class="inline margin-left-10 font-green"]/text()',
            'indirizzo': '//div[@class="anagrafica-risultato"]/a/text()',
            'lotto': '//span[@class="black"]/text()',
            'modalita_consegna': '//span[contains(text(), "Modalità Consegna")]//span[@class="margin-left-10 inline font-black"]/text()',
            'numero_di_procedura': '//span[contains(text(), "N° Procedura")]//span[@class="margin-left-10 inline font-black"]/text()',
            'offerta_minima': '//span[contains(text(), "Offerta minima")]//span[@class="margin-left-10 inline font-blue"]/text()',
            "prezzo_base": '//span[contains(text(), "Prezzo base d")]//span[@class="font-blue font18 inline margin-left-10"]/text()',
            'rialzo_minimo': '//span[contains(text(), "Rialzo minimo")]//span[@class="margin-left-10 inline font-blue"]/text()',
            'url': '//div[@class="anagrafica-risultato"]/a/@href',
        }
    }
    items['value'] = PVPSearchItem().items['value']
    #items['value']['data_della_ricerca'] = None
    items['value']['search_id'] = None

    '''
    def __init__(self):
        super(PVPSearchPropertyItem, self).__init__()
        # Add these attributes dynamically
        for tkey in self.items.keys():
            if tkey != 'value':
                for key in self.items[tkey].keys():
                    print(key)
                    #setattr(self, key, Field(output_processor=TakeFirst()))
    '''

    basename = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    filename = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    id = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    is_downloaded = Field(input_processor=MapCompose(bool), output_processor=TakeFirst())
    is_relative_href_fixed = Field(input_processor=MapCompose(bool), output_processor=TakeFirst())
    response_status_code = Field(input_processor=MapCompose(int), output_processor=TakeFirst())
    search_id = Field(output_processor=TakeFirst())
    spider_name = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    url = Field(input_processor=MapCompose(remove_tags, strip, fix_relative_hyperlink), output_processor=TakeFirst())
    url_localhost = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())

    '''
    basename = Field(output_processor=TakeFirst())
    filename = Field(output_processor=TakeFirst())
    id = Field(output_processor=TakeFirst())
    is_downloaded = Field(input_processor=MapCompose(bool), output_processor=TakeFirst())
    is_relative_href_fixed = Field(input_processor=MapCompose(bool), output_processor=TakeFirst())
    response_status_code = Field(input_processor=MapCompose(int), output_processor=TakeFirst())
    search_id = Field(output_processor=TakeFirst())
    spider_name = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    url = Field(input_processor=MapCompose(remove_tags, strip, fix_relative_hyperlink), output_processor=TakeFirst())
    url_localhost = Field(output_processor=TakeFirst())
    '''

    #data_della_ricerca = Field(output_processor=TakeFirst())
    categoria = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    data_di_vendita = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    indirizzo = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    lotto = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    modalita_consegna = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    numero_di_procedura = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    offerta_minima = Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())
    prezzo_base = Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())
    rialzo_minimo = Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())


class PVPSearchPropertyModel(BaseModel):
    basename : str
    #data_della_ricerca : date
    filename : str
    id : str
    is_downloaded : bool
    is_relative_href_fixed : bool
    response_status_code : int
    search_id : str
    spider_name : str
    url : str
    url_localhost : str
    
    categoria : str
    data_di_vendita : date
    indirizzo : str
    lotto : str
    modalita_consegna : str
    numero_di_procedura : str
    offerta_minima : float
    prezzo_base : float
    rialzo_minimo : float

    @validator('prezzo_base')
    def validate_prezzo_base(cls, value):
        if value <= 0:
            raise ValueError('Prezzo base must be greater than zero.')
        return value


class PVPPropertyItem(Item):

    '''
    To do:

    1. Aggiungere parser per "Eventi significativi ed esiti", that is http://localhost:8001/pvp/pvp_property_LTT514660.html

    '''

    items = {
        'css': {
        },
        'xpath': {
            'inserzione': '//h1[contains(text(), "Inserzione N.")]/text()',
            
            'lotto_titolo': '//h3[contains(text(), "Dettaglio lotto")]/following::div[@class="row"][position()=1]/div[contains(@class, "anagrafica-dato")]/text()',
            'lotto_descrizione': '//h3[contains(text(), "Dettaglio lotto")]/following::div[@class="row"][position()=2]/div[contains(@class, "anagrafica-dato")]/text()',
            #'esecuzione': '//h3[contains(text(), "Dettaglio lotto")]/parent/div[@class="row"]/div[contains(@class, "anagrafica-dato")][contains(text(), "Esecuzione")]/following::div[contains(@class, "anagrafica-risultato")]/div/text()',
            
            'tipologia': '//h3[contains(text(), "Dettaglio Vendita")]/following-sibling::div[@class="row"]/div[contains(@class, "anagrafica-dato")][contains(text(), "Tipologia")]/following-sibling::div[contains(@class, "anagrafica-risultato")]/text()',
            'data_di_vendita': '//h3[contains(text(), "Dettaglio Vendita")]/following-sibling::div[@class="row"]/div[contains(@class, "anagrafica-dato")][contains(text(), "Data di vendita")]/following-sibling::div[contains(@class, "anagrafica-risultato")]/text()',
            'luogo_vendita': '//h3[contains(text(), "Dettaglio Vendita")]/following-sibling::div[@class="row"]/div[contains(@class, "anagrafica-dato")][contains(text(), "Luogo vendita")]/following-sibling::div[contains(@class, "anagrafica-risultato")]/text()',
            'prezzo_base': '''//h3[contains(text(), "Dettaglio Vendita")]/following-sibling::div[@class="row"]/div[contains(@class, "anagrafica-dato")][contains(text(), "Prezzo base d'asta")]/following-sibling::div[contains(@class, "anagrafica-risultato")]/text()''',
            'offerta_minima': '//h3[contains(text(), "Dettaglio Vendita")]/following-sibling::div[@class="row"]/div[contains(@class, "anagrafica-dato")][contains(text(), "Offerta minima")]/following-sibling::div[contains(@class, "anagrafica-risultato")]/text()',
            'rialzo_minimo': '//h3[contains(text(), "Dettaglio Vendita")]/following-sibling::div[@class="row"]/div[contains(@class, "anagrafica-dato")][contains(text(), "Rialzo minimo")]/following-sibling::div[contains(@class, "anagrafica-risultato")]/text()',
            'modalita_di_vendita': '//h3[contains(text(), "Dettaglio Vendita")]/following-sibling::div[@class="row"]/div[contains(@class, "anagrafica-dato")][contains(text(), "Modalità di vendita")]/following-sibling::div[contains(@class, "anagrafica-risultato")]/text()',
            'termine_presentazione_offerta': '//h3[contains(text(), "Dettaglio Vendita")]/following-sibling::div[@class="row"]/div[contains(@class, "anagrafica-dato")][contains(text(), "Termine presentazione offerta")]/following-sibling::div[contains(@class, "anagrafica-risultato")]/text()',
            
            'pubblicato_in': '//h3[contains(text(), "Pubblicato anche in")]/parent::div/div[@class="info-row"]/span/a[position()=1]/text()',
            'pubblicato_in_url': '//h3[contains(text(), "Pubblicato anche in")]/parent::div/div[@class="info-row"]/span/a[position()=1]/@href',
            
            #Beni inclusi nel lotto
            'indirizzo': '//section[@id="beni-lotto"]//div[@class="anagrafica-risultato"]/text()',
            'bene_descrizione': '//section[@id="beni-lotto"]/div/div/div/p[position()=1]/text()',
            
            'bene_tipologia': '//div[contains(@class, "anagrafica-tribunale")]/div/div[contains(@class, "anagrafica-dato")][contains(text(), "Tipologia")]/following-sibling::div[contains(@class, "anagrafica-risultato")]/text()',
            'bene_disponibilita': '//div[contains(@class, "anagrafica-tribunale")]/div/div[contains(@class, "anagrafica-dato")][contains(text(), "Disponibilita")]/following-sibling::div[contains(@class, "anagrafica-risultato")]/text()',
            'bene_vani': '//div[contains(@class, "anagrafica-tribunale")]/div/div[contains(@class, "anagrafica-dato")][contains(text(), "Vani")]/following-sibling::div[contains(@class, "anagrafica-risultato")]/text()',
            'bene_piano': '//div[contains(@class, "anagrafica-tribunale")]/div/div[contains(@class, "anagrafica-dato")][contains(text(), "Piano")]/following-sibling::div[contains(@class, "anagrafica-risultato")]/text()',
            'bene_foglio': '//div[contains(@class, "anagrafica-tribunale")]/div/div[contains(@class, "anagrafica-dato")][contains(text(), "Foglio")]/following-sibling::div[contains(@class, "anagrafica-risultato")]/text()',
            'bene_particella': '//div[contains(@class, "anagrafica-tribunale")]/div[contains(@class, "anagrafica-dato")][contains(text(), "Particella")]/following-sibling::div[contains(@class, "anagrafica-risultato")]/text()',
            'bene_sub': '//div[contains(@class, "anagrafica-tribunale")]/div/div[contains(@class, "anagrafica-dato")][contains(text(), "Sub")]//following-sibling::div[contains(@class, "anagrafica-risultato")]/text()',
            
            'descrizione': '//h2[contains(text(), "DESCRIZIONE")]/following::p/text()',
            
            #Eventi significativi ed esiti
            #Descrizione tabella
            #Data	Tipologia	Note
            #19/12/2018	Avviso di rettifica	data di vendita : 4/04/2019 ore 09:30
            #24/12/2018	Avviso di rettifica	data di vendita ; 04/04/2019 ore 9:30
            
            'eventi_data': '//table[@class="table"]/tbody/tr/td[position()=1]',
            'eventi_tipologia': '//table[@class="table"]/tbody/tr/td[position()=2]',
            'eventi_note': '//table[@class="table"]/tbody/tr/td[position()=3]',
                        
            'tipo_procedura': '//h3[contains(text(), "Dettaglio Procedura")]/following::div[@class="row"]/div[contains(@class, "anagrafica-dato")][contains(text(), "Tipo Procedura")]/following::div[contains(@class, "anagrafica-risultato")]/text()',
            'numero_procedura': '//h3[contains(text(), "Dettaglio Procedura")]/following::div[@class="row"]/div[contains(@class, "anagrafica-dato")][contains(text(), "N° Procedura")]/following::div[contains(@class, "anagrafica-risultato")]/text()',
            'tribunale': '//h3[contains(text(), "Dettaglio Procedura")]/following::div[@class="row"]/div[contains(@class, "anagrafica-dato")][contains(text(), "Tribunale")]/following::div[contains(@class, "anagrafica-risultato")]/text()',
            'numero_lotto': '//h3[contains(text(), "Dettaglio Procedura")]/following::div[@class="row"]/div[contains(@class, "anagrafica-dato")][contains(text(), "Lotto nr.")]/following::div[contains(@class, "anagrafica-risultato")]/text()',
            'data_pubblicazione_sul_portale': '//h3[contains(text(), "Dettaglio Procedura")]/following::div[@class="row"]/div[contains(@class, "anagrafica-dato")][contains(text(), "Pubblicato sul Portale il")]/following::div[contains(@class, "anagrafica-risultato")]/text()',
            
            #REFERENTI
            'delegato_alla_vendita': '//h3[contains(text(), "Dettaglio Procedura")]/following::div[@class="row"]/div[contains(@class, "anagrafica-dato")][contains(text(), "Delegato alla vendita")]/following::div[contains(@class, "anagrafica-risultato")]/span/text()',
            'custode': '//h3[contains(text(), "Dettaglio Procedura")]/following::div[@class="row"]/div[contains(@class, "anagrafica-dato")][contains(text(), "Custode")]/following::div[contains(@class, "anagrafica-risultato")]/span/text()',
            'custode_telefono_mobile': '//h3[contains(text(), "Dettaglio Procedura")]/following::div[@class="row"]/div[contains(@class, "anagrafica-dato")][contains(text(), "Telefono mobile custode")]/following::div[contains(@class, "anagrafica-risultato")]/span/text()',
            'custode_telefono': '//h3[contains(text(), "Dettaglio Procedura")]/following::div[@class="row"]/div[contains(@class, "anagrafica-dato")][contains(text(), "Telefono custode")]/following::div[contains(@class, "anagrafica-risultato")]/span/text()',
            'custode_email': '//h3[contains(text(), "Dettaglio Procedura")]/following::div[@class="row"]/div[contains(@class, "anagrafica-dato")][contains(text(), "Email custode")]/following::div[contains(@class, "anagrafica-risultato")]/span/text()',
            'giudice': '//h3[contains(text(), "Dettaglio Procedura")]/following::div[@class="row"]/div[contains(@class, "anagrafica-dato")][contains(text(), "Giudice")]/following::div[contains(@class, "anagrafica-risultato")]/span/text()',
            
            'allegati': '//div[@class="info-box"]/h3[contains(text(), "ALLEGATI")]/parent::div/div[@class="info-row"]/span/a/text()',
            'allegati_url' : '//div[@class="info-box"]/h3[contains(text(), "ALLEGATI")]/parent::div/div[@class="info-row"]/span/a/@href',
        },
        'value': PVPSearchItem().items['value']
    }

    '''
    def __init__(self):
        super(PVPPropertyItem, self).__init__()
        # Add these attributes dynamically
        for tkey in self.items.keys():
            if tkey != 'value':
                for key in self.items[tkey].keys():
                    pass
                    #setattr(self, key, Field(output_processor=TakeFirst()))
    '''

    basename = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    filename = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    id = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    is_downloaded = Field(input_processor=MapCompose(bool), output_processor=TakeFirst())
    is_relative_href_fixed = Field(input_processor=MapCompose(bool), output_processor=TakeFirst())
    response_status_code = Field(input_processor=MapCompose(int), output_processor=TakeFirst())
    spider_name = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    url = Field(input_processor=MapCompose(remove_tags, strip, fix_relative_hyperlink), output_processor=TakeFirst())
    url_localhost = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())

    dettaglio = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    inserzione = Field(input_processor=MapCompose(remove_tags, strip, remove_inserzione, int), output_processor=TakeFirst())
    lotto_titolo = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    lotto_descrizione = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    esecuzione = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    tipologia = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    data_di_vendita = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    luogo_vendita = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    prezzo_base = Field(input_processor=MapCompose(remove_tags, strip, remove_currency), output_processor=TakeFirst())
    offerta_minima = Field(input_processor=MapCompose(remove_tags, strip, remove_currency), output_processor=TakeFirst())
    rialzo_minimo = Field(input_processor=MapCompose(remove_tags, strip, remove_currency), output_processor=TakeFirst())
    modalita_di_vendita = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    termine_presentazione_offerta = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    pubblicato_in = Field(input_processor=MapCompose(strip, remove_tags, remove_null), output_processor=MapCompose())
    pubblicato_in_url = Field(input_processor=MapCompose(strip, remove_tags), output_processor=MapCompose())
    indirizzo = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    bene_descrizione = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    bene_tipologia = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    bene_disponibilita = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    bene_vani = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    bene_piano = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    bene_foglio = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    bene_particella = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    bene_sub = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    
    eventi_data = Field(input_processor=MapCompose(strip, remove_tags, remove_null), output_processor=MapCompose())
    eventi_tipologia = Field(input_processor=MapCompose(strip, remove_tags, remove_null), output_processor=MapCompose())
    eventi_note = Field(input_processor=MapCompose(strip, remove_tags, remove_null), output_processor=MapCompose())
    
    descrizione = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    tipo_procedura = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    numero_procedura = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    tribunale = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    numero_lotto = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    data_pubblicazione_sul_portale = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    delegato_alla_vendita = Field(input_processor=MapCompose(remove_tags, strip, title), output_processor=TakeFirst())
    giudice = Field(input_processor=MapCompose(remove_tags, strip, title), output_processor=TakeFirst())
    custode = Field(input_processor=MapCompose(remove_tags, strip, title), output_processor=TakeFirst())
    custode_telefono_mobile = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    custode_telefono = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    custode_email = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    allegati = Field(input_processor=MapCompose(strip, remove_tags, remove_null), output_processor=MapCompose())
    allegati_url = Field(input_processor=MapCompose(), output_processor=MapCompose())

    #self.siti = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    #"title": "h1#page-name::text",
    #"price": "span#ContentPlaceHolder1_DetailsFormView_Shillings::text",
    #"location": "span#ContentPlaceHolder1_DetailsFormView_LocationLabel::text",
    #"bedrooms": "span#ContentPlaceHolder1_DetailsFormView_BedsInWordsLabel::text",
    #"district": "span#ContentPlaceHolder1_DetailsFormView_DistrictLabel::text",
    #"status": "span#ContentPlaceHolder1_DetailsFormView_StatusLabel::text",
    #"bathrooms": "span#ContentPlaceHolder1_DetailsFormView_BathsInWordsLabel::text",
    #"category": "span#ContentPlaceHolder1_DetailsFormView_CategoryLabel::text",
    #"agent": "span#ContentPlaceHolder1_DetailsFormView_AgentLabel::text",
    #"agent_contact": "span#ContentPlaceHolder1_FormView1_TelephoneLabel::text",
    #"agent_email": "span#ContentPlaceHolder1_FormView1_ContactEmailLabel::text",
    #"agent_company": "span#ContentPlaceHolder1_FormView1_CompanyLabel::text",

    # define the fields for your item here like:
    #number_of_results = int(scrapy.Field(.replace(' Annunci', '')))
    #hyperlink = Field(input_processor=MapCompose(remove_tags), output_processor=TakeFirst())
    #price = scrapy.Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())

    #self.allegati = Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=Join())
    #self.url_allegati = Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=Join())

class PVPPropertyModel(BaseModel):
    basename: str
    filename: str
    id: str
    is_downloaded: bool
    is_relative_href_fixed: bool
    response_status_code: int
    spider_name: str
    url: str
    url_localhost: str
    
    allegati: Optional[List[str]]
    allegati_url: Optional[List[str]]
    bene_descrizione: str
    bene_disponibilita: str
    bene_foglio: int
    bene_particella: int
    bene_piano: int
    bene_sub: int
    bene_tipologia: str
    bene_vani: int
    custode: str
    custode_email: str
    custode_telefono: int
    custode_telefono_mobile: int
    data_pubblicazione_sul_portale: date
    delegato_alla_vendita: str
    descrizione: str
    data_di_vendita: date
    dettaglio: str
    eventi_data: date
    eventi_tipologia: str
    eventi_note: str
    lotto_titolo: str
    lotto_descrizione: str
    esecuzione: str
    giudice: str
    indirizzo: str
    inserzione: str
    luogo_vendita: str
    modalita_di_vendita: str
    numero_lotto: str
    numero_procedura:  int
    offerta_minima: float
    prezzo_base: float
    pubblicato_in: Optional[List[str]]
    pubblicato_in_url: Optional[List[str]]
    rialzo_minimo: float
    termine_presentazione_offerta: str
    tipo_procedura: str
    tipologia: str
    tribunale: str

    @validator('prezzo_base')
    def validate_prezzo_base(cls, value):
        if value <= 0:
            raise ValueError('Prezzo base must be greater than zero.')
        return value

    @validator('custode_email')
    def check_custode_email(cls, value):
        if '@' not in value:
            raise ValueError('This is not an email address! There does not contain an @ character.')
        return value


class PVPPropertyImagesItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    image_urls = Field()
    images = Field()
