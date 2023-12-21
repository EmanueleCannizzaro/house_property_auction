# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from datetime import datetime, date
import re
#import scrapy
from pydantic import BaseModel, validator
from scrapy.item import Item, Field
#from scrapy.loader.processors import Join
from itemloaders.processors import  Join, MapCompose, TakeFirst
from typing import List, Optional
from urllib.parse import urljoin
from w3lib.html import remove_tags

from property_scraper import RECROWD_URL_ROOTNAME


def remove_inserzione(text):
    return text.replace('Inserzione N.', '')

def title(text):
    return text.title()

def strip(text):
    s = text.strip()
    s = s.replace('\n', '').replace('\r', '')
    s = re.sub("\s\s+", " ", s)
    return s

def join_sentences(l):
    if isinstance(l, list):
        return '\n'.join([strip(x) for x in l if strip(x)])
    else:
        return l
    
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
        return urljoin(Recrowd_URL_ROOTNAME, url)
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


class RecrowdProjectsItem(Item):
    items = {
        'css': {
        },
        'xpath': {
            'url': './@href',
            'category': './/div[@class="card--category"]/h3/text()',
            'image': './/div[@class="card--image"]/img/@src',
            'target_title': './/div[@class="card-hover-text"]/h4[contains(text(), "OBIETTIVO")]/text()',
            'target': './/div[@class="card-hover-text"]/h4[contains(text(), "OBIETTIVO")]/span/text()',            
            'null': './/div[@class="card--banner"]/h3/text()',            
            'percentage': './/div[@class="card--progress"]/div[@class="card-percentage"]/text()',
            'title': './/div[@class="card--title"]/h2/text()',
            'duration': './/div[@class="card--row card--row-1"]/div[@class="row--data"]/p[contains(text(), "DURATA INVESTIMENTO")]/following-sibling::h2/text()',
            'duration_unit': './/div[@class="card--row card--row-1"]/div[@class="row--data"]/p[contains(text(), "DURATA INVESTIMENTO")]/following-sibling::h2/span/text()',
            'minimum_investement': './/div[@class="row--data"]/p[contains(text(), "INVESTIMENTO MINIMO")]/following-sibling::h2/text()',
            'minimum_investement_unit': './/div[@class="row--data"]/p[contains(text(), "INVESTIMENTO MINIMO")]/following-sibling::h2/span/text()',
            'interest': './/div[@class="card--data"]/div[@class="row-data--label"]/p/text()',
            'interest_minimum': './/div[@class="card--data"]/div[@class="card--row card--row-2"]/div[@class="row--data"]/p[contains(text(), "MINIMO")]/following-sibling::h2/text()',
            'interest_minimum_unit': './/div[@class="card--data"]/div[@class="card--row card--row-2"]/div[@class="row--data"]/p[contains(text(), "MINIMO")]/following-sibling::h2/span/text()',
            'interest_maximum': './/div[@class="card--data"]/div[@class="card--row card--row-2"]/div[@class="row--data"]/p[contains(text(), "MASSIMO TRATTABILE")]/following-sibling::h2/text()',
            'interest_maximum_unit': './/div[@class="card--data"]/div[@class="card--row card--row-2"]/div[@class="row--data"]/p[contains(text(), "MASSIMO TRATTABILE")]/following-sibling::h2/span/text()',
            'interest_title': './/div[@class="row-data--label "]/p/text()',
            'interest_minimum_annual': './/div[@class="card--row card--row-3 "]/div[@class="row--data"]/p[contains(text(), "MINIMO")]/following-sibling::h2/text()',
            'interest_minimum_annual_unit': './/div[@class="card--row card--row-3 "]/div[@class="row--data"]/p[contains(text(), "MINIMO")]/following-sibling::h2/span/text()',
            'interest_maximum_annual': './/div[@class="card--row card--row-3 "]/div[@class="row--data"]/p[contains(text(), "MASSIMO TRATTABILE")]/following-sibling::h2/text()',
            'interest_maximum_annual_unit': './/div[@class="card--row card--row-3 "]/div[@class="row--data"]/p[contains(text(), "MASSIMO TRATTABILE")]/following-sibling::h2/span/text()',
            'status': './/div[@class="card-status"]/h3/text()',
        }
    }

    url = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    category = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    image = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    target_title = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    target = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    null = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    percentage = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    title = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    duration = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    duration_unit = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    minimum_investement = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    minimum_investement_unit = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    interest = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    interest_minimum = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    interest_minimum_unit = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    interest_maximum = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    interest_maximum_unit = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    interest_title = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    interest_minimum_annual = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    interest_minimum_annual_unit = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    interest_maximum_annual = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    interest_maximum_annual_unit = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    status = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())


class RecrowdProjectsModel(BaseModel):
    url : str
    category : str
    image : str
    target_title : str
    target : float
    null : str
    percentage : str
    title : str
    duration : str
    duration_unit : str
    minimum_investement : str
    minimum_investement_unit : str
    interest : str
    interest_minimum : str
    interest_minimum_unit : str
    interest_maximum : str
    interest_maximum_unit : str
    interest_title : str
    interest_minimum_annual : str
    interest_minimum_annual_unit : str
    interest_maximum_annual : str
    interest_maximum_annual_unit : str
    status : str
    
    @validator('target')
    def validate_prezzo_base(cls, value):
        if value <= 0:
            raise ValueError('Prezzo base must be greater than zero.')
        return value


class RecrowdProjectItem(Item):

    '''
    To do:

    1. Aggiungere parser per "Eventi significativi ed esiti", that is http://localhost:8001/pvp/pvp_property_LTT514660.html

    '''

    items = {
        'css': {
        },
        'xpath': {
            'title': '//div[@class="card"]/div[@class="card-body"]/div[@class="card__title"]/text()',
            'city': '//div[@class="card"]/div[@class="card-body"]/div[@class="card__text"]/text()',
            #'booh': '//div[@class="card"]/div[@class="card-body"]/div[@class="card__text"]/text()',            
            #'amount_target': '//div[@class="card"]/div[@class="card-body"]/div[@class="card__text"][position() = 2][contains(text(), "Obiettivo raccolta:")]/strong/text()',
            'amount_target': '//div[@class="card"]/div[@class="card-body"]/div[@class="card__text"][position() = 1]/strong/text()',
            'amount_collected': '//div[@class="card"]/div[@class="card-body"]/div[@class="card__text"][contains(text(), "Investimenti raccolti:")]/strong/text()',
            #'remaining_days': '//div[@class="card"]/div[@class="card-body"]/div[@class="card__text"]/div[@class="col-xs-6"][position() = 2][contains(text(), "giorni mancanti")]/strong/text()',
            'remaining_days': '//div[@class="card"]/div[@class="card-body"]/div[@class="card__text"]/div[@class="col-xs-6"][position() = 1]/strong/text()',
            'number_of_investors': '//div[@class="card"]/div[@class="card-body"]/div[@class="card__text"]/div[@class="col-xs-6"][contains(text(), "Numero di investitori:")]/strong/text()',
            'status': '//div[@class="card__progress"]/div[@class="progress-bar"]/span/text()',
            'interest_annual': '//div[@class="card__projectdate"]/ul[@class="list-unstyled"]/li[contains(text(), "INTERESSE ANNUO")]/span/text()',
            'interest_annual_units': '//div[@class="card__projectdate"]/ul[@class="list-unstyled"]/li[contains(text(), "INTERESSE ANNUO")]/span/small/text()',
            'interest_total': '//div[@class="card__projectdate"]/ul[@class="list-unstyled"]/li[contains(text(), "INTERESSE TOTALE")]/span/text()',
            'interest_total_units': '//div[@class="card__projectdate"]/ul[@class="list-unstyled"]/li[contains(text(), "INTERESSE TOTALE")]/span/small/text()',
            'interestment_duration': '//div[@class="card__projectdate"]/ul[@class="list-unstyled"]/li[contains(text(), "Durata investimento")]/span/text()',
            'interestment_duration_units': '//div[@class="card__projectdate"]/ul[@class="list-unstyled"]/li[contains(text(), "Durata investimento")]/span/small/text()',
            'amount_minimum': '//div[@class="card-footer"]/div[@class="card__text"][contains(text(), "Investimento minimo")]/strong/text()',
            'date_opening': '//div[@class="card-footer"]/div[@class="card__text"][contains(text(), "Data apertura:")]/strong/text()',

            'proponent': '//div[@id="panel-proponent"][@class="section"]/div[@class="container"]/div[@class="row"]/div[@class="col-xs-12"]/h3[contains(text(), "Descrizione della società")]/following-sibling::p',
            
            'project': '//div[@id="panel-project"][@class="section"]/div[@class="container"]/div[@class="row"]/div[@class="col-xs-12"]/h3[contains(text(), "Caratteristiche della campagna")]/following-sibling::p',
            
            #'images': '/div[@id="panel-project"][@class="section"]/div[@class="container"]/div[@class="row"]/div[@class="col-xs-12"]/div[@class="owl-carousel owl-gallery owl-theme owl-loaded owl-drag"]/div[@class="owl-stage-outer"]/div[@class="owl-stage"]/div[@class="owl-item"]/a/@href',
            'images': '//div[contains(@class, "owl-item")]/a/@href',
            'allegati': '//div[@id="panel-documents"][@class="section"]/div[@class="container"]/div[@class="row"]/div[@class="col-xs-12"]/p/a/text()',
            'allegati_url': '//div[@id="panel-documents"][@class="section"]/div[@class="container"]/div[@class="row"]/div[@class="col-xs-12"]/p/a/@href',
        }
    }
    title = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())    
    city = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    amount_target = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    #booh = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    amount_collected = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    remaining_days = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    number_of_investors = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    status = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    interest_annual = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    interest_annual_units = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    interest_total = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    interest_total_units = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    interestment_duration = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    interestment_duration_units = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    amount_minimum = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    date_opening = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    proponent = Field(input_processor=MapCompose(remove_tags, strip), output_processor=Join())
    project = Field(input_processor=MapCompose(remove_tags, strip), output_processor=Join())
    images = Field(input_processor=MapCompose(remove_tags, strip), output_processor=MapCompose())
    allegati = Field(input_processor=MapCompose(remove_tags, strip), output_processor=MapCompose())
    allegati_url = Field(input_processor=MapCompose(remove_tags, strip), output_processor=MapCompose())


class RecrowdProjectModel(BaseModel):
    title: str
    city: str
    amount_target: str
    #booh: str
    amount_collected: float
    remaining_days: int
    number_of_investors: int
    status: str
    interest_annual: float
    interest_annual_units: str
    interest_total: float
    interest_total_units: str
    interestment_duration: int
    interestment_duration_units: str
    amount_minimum: float
    date_opening: str
    proponent: str
    description: str
    images: list
    allegati: list
    allegati_url: list

    #@validator('allegati')
    #def validate_target(cls, value):
    #    if value <= 0:
    #        raise ValueError('Prezzo base must be greater than zero.')
    #    return value


class RecrowdMyDashboardItem(Item):
    items = {
        'css': {
        },
        'xpath': {
            '//div[@class="card-body"]/h5[@class="card-title"][contains(text(), "Conto Virtuale"]/sibling::div[@class="card__amount"]/text()',
            '//div[@class="card-body"]/h5[@class="card-title"][contains(text(), "Conto Virtuale"]/sibling::small/text()',

            #'//h3[contains(text(), "Ultimi Movimenti")]/parent::div/parent::div/sibling::div/div/table/tbody/tr/td[1]',
            '//h3[contains(text(), "Ultimi Movimenti")]/parent::div/parent::div/sibling::div/div/table/tbody/tr/td[2]',
            '//h3[contains(text(), "Ultimi Movimenti")]/parent::div/parent::div/sibling::div/div/table/tbody/tr/td[3]',
            '//h3[contains(text(), "Ultimi Movimenti")]/parent::div/parent::div/sibling::div/div/table/tbody/tr/td[4]',

            '//div[@class="col-xs-12 col-sm-6 col-md-4"]/div[@class="card shadow wow fadeInUp  animated"]/div[@class="card-head"]', 
            '//div[@class="col-xs-12 col-sm-6 col-md-4"]/div[@class="card shadow wow fadeInUp  animated"]/div[@class="card-body"]/div[@class="card__title"]',  # LE CASETTE</div>
            '//div[@class="col-xs-12 col-sm-6 col-md-4"]/div[@class="card shadow wow fadeInUp  animated"]/div[@class="card-body"]/div[@class="card__text"]',  #Lonigo (VI)</div>

            '//div[@class="card__projectdate"]/div[@class="alert alert-success"][contains(text(), "Hai investito")]/strong/text()', #>2.100,00€
            '//div[@class="card-footer"]/div[@class="row"]/div[@class="col-xs-12"]/a[@class="link-block"]/href', # /it/progetti/dettaglio/106-le-casette"
            '//div[@class="card-footer"]/div[@class="row"]/div[@class="col-xs-12"]/a[@class="link-block"]/div[@class="card__link"][contains(text(), "VEDI DETTAGLIO")]', #
            
            '//div[@class="col-xs-12"]/a[@class="link-block"]/href', #/it/area-privata/investimenti/contratto/CFECB9DCCD298C252B7C91BB186A56C6/8D00ED00FADBF924BF2B7E543349E71D
            '//div[@class="col-xs-12"]/a[@class="link-block"]/div[@class="card__link][contains(text(), "VEDI CONTRATTO")]',
            '//div[@class="col-xs-12"]/a[@class="link-block"]/href', #/it/area-privata/progetto/contratto/106-82EE14DCBB4B5BB2016D01C7A1AEAC36" target="blank" 
            '//div[@class="col-xs-12"]/a[@class="link-block"]/div[@class="card__link"][contains(text(), "VEDI CONDIZIONI GENERALI")]',
        }
    }


class RecrowdMyDashboardModel(BaseModel):
    title: str


class RecrowdMyInvestmentItem(Item):
    items = {
        'css': {
        },
        'xpath': {
        }
    }


class RecrowdMyInvestmentModel(BaseModel):
    title: str


class RecrowdMyAccountItem(Item):
    items = {
        'css': {
        },
        'xpath': {
        }
    }


class RecrowdMyAccountModel(BaseModel):
    title: str


class RecrowdPropertyImagesItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    image_urls = Field()
    images = Field()
