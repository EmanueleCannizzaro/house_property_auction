# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from datetime import datetime, date
import re
#import scrapy
from pydantic import BaseModel, validator
from scrapy.item import Item, Field
#from scrapy.loader.processors import  MapCompose, TakeFirst
from itemloaders.processors import Join, MapCompose, TakeFirst
from typing import List, Optional
from urllib.parse import urljoin
from w3lib.html import remove_tags

from property_scraper import INFOENCHERES_URL_ROOTNAME


def create_url(url):
    return urljoin(INFOENCHERES_URL_ROOTNAME, url)
    
def strip(text):
    s = text.strip()
    s = s.replace('\n', '').replace('\r', '')
    s = re.sub("\s\s+", " ", s)
    return s


class InfoEncheresSearchPropertyItem(Item):
    items = {
        'css': {
        },
        'xpath': {
            'ref': './td[1]/a/text()',
            'url': './td[1]/a/@href',
            'town': './td[2]/a/text()',
            'county': './td[3]/text()',
            'property_type': './td[4]/a/text()',
            'price': './td[5]/text()',
            'date_of_sale': './td[6]/text()',
            'lawyer': './td[7]/text()'
        }
    }
    ref = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    url = Field(input_processor=MapCompose(remove_tags, strip), output_processor=MapCompose(create_url))
    town = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    county = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    property_type = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    price = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    date_of_sale = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    lawyer = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())


class InfoEncheresSearchPropertyModel(BaseModel):
    ref: str
    url: str
    town: str
    county: str
    property_type: str
    price: str
    date_of_sale: str
    lawyer: str


class InfoEncheresPropertyItem(Item):
    items = {
        'css': {
        },
        'xpath': {
            'lawyer': '//div[@class="avocat"]/div[@class="nom"]/b/text()', #SELARL DESARNAUTS-HORNY-ROBERT-DESPIERRES
            'lawyer_phone_number': '//div[@class="avocat"]/div[@class="nom"]/div[@class="tel"]/text()', # 05.32.09.49.45
            'lawyer_card': '//div[@class="fiche"]/a/href',
            'lawyer_website': '//div[@class="site"]/a/href',
            #1048-vente-encheres-immobilieres-partenaires-annonceurs-selarl-desarnauts-horny-robert-despierres-.html
            #'ref': '//div[@class="gauche"]/table/tbody/tr/td/b[contains(text(), "Référence :")]/parent::td/following-sibling::td/text()',
            'ref': '//tr/td/b[contains(text(), "Référence :")]/parent::td/following-sibling::td/text()',
            # 5097
            'property_type': '//tr/td/b[contains(text(), "Nature du bien :")]/parent::td/following-sibling::td/text()',
            # Appartement T5, cellier et deux parkings    
            'address': '//tr/td/b[contains(text(), "Adresse :")]/parent::td/following-sibling::td/text()',
            # 21 impasse Negreneys<br>31200  TOULOUSE
            'size': '//tr/td/b[contains(text(), "Superficie :")]/parent::td/following-sibling::td/text()',
            # 92.92 m²
            'price': '//tr/td/b[contains(text(), "Mise à prix")]/parent::td/following-sibling::td/text()',
            # 165 000 €
            'date_of_sale': '//tr/td/b[contains(text(), "Vente le :")]/parent::td/following-sibling::td/text()',
            # 29/06/2023
            'court': '//tr/td/b[contains(text(), "Au TGI de :")]/parent::td/following-sibling::td/text()',
            # Toulouse<br>2, Allées Jules Guesde - 31000 Toulouse</td>
            'date_of_visit': '//tr/td/b[contains(text(), "Date de visite :")]/parent::td/following-sibling::td/text()',
            # Sur les lieux, le 19 juin 2023 de 10h30 à 11h30
            #'address': '//div[@class="droite"]/a::title',
            'actual_sale_price': '//div[@class="droite"]/b[contains(text(), "Résultat")]/parent::div/text()',            
            'geo': '//div[@class="droite"]/a/div[@class="button_detail num1"][contains(text(), "Géolocalisation")]/text()',
			#'images': '//div[@class="droite"]/a/div[@class="button_detail num2"][contains(text(), "Photos")]/parent::a/following-sibling::a/text()',
            'image_urls': '//div[@class="button_detail num2"]/a[contains(@href, "/upload/")]/@href',
            #'files': [
            #],
            'file_urls': [
                '//div[@class="droite"]/a/div[@class="button_detail num3"]/parent::a[contains(@href, "/upload/")]/@href',
                '//div[@class="button_detail num4"]/a[contains(@href, "/upload/")]/@href',
            ],
            #'additional_files': 
            #'additional_file_urls': 
            'description': '//div[@class="cadre"]/div[@class="int2"]/descendant-or-self::*/text()',
        }
    }
    lawyer = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    lawyer_phone_number = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    lawyer_card = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    lawyer_website = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    ref = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    #town = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    #county = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    property_type = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    address = Field(input_processor=MapCompose(remove_tags, strip), output_processor=Join())
    size = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    price = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    date_of_sale = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    court = Field(input_processor=MapCompose(remove_tags, strip), output_processor=Join())
    date_of_visit = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    actual_sale_price = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    geo = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    images = Field(input_processor=MapCompose(remove_tags, strip))
    image_urls = Field(input_processor=MapCompose(remove_tags, strip))
    files = Field(input_processor=MapCompose(remove_tags, strip))
    file_urls = Field(input_processor=MapCompose(remove_tags, strip))
    #additional_file_titles = Field(input_processor=MapCompose(remove_tags, strip))
    #additional_file_urls = Field(input_processor=MapCompose(remove_tags, strip))    
    description = Field(input_processor=MapCompose(remove_tags, strip), output_processor=Join())


class InfoEncheresPropertyModel(BaseModel):
    lawyer: str
    lawyer_phone_number: int
    lawyer_card: str
    lawyer_website: str
    ref: int
    property_type: str
    address: str
    size: float
    price: float
    date_of_sale: datetime
    court: str
    date_of_visit: datetime
    actual_sale_price: float
    geo: str
    images: Optional[List[str]]
    image_urls: Optional[List[str]]
    files: Optional[List[str]]
    file_urls: Optional[List[str]]
    #additional_file_titles: Optional[List[str]]
    #additional_file_urls: Optional[List[str]]
    description: str
    

class InfoEncheresColumns():
    NAMES = {
        'ref': 'Référence',
        'url': 'Hyperlink',
        'town': 'Ville',
        'county': 'Département',
        'lawyer': 'Avocat',
        'lawyer_phone_number': "Numéro de Téléphone de l'Avocat",
        'lawyer_card': "Carte d'Avocat",
        'lawyer_website': "Site d'Avocat",
        'property_type': 'Nature du Bien',
        'address': 'Adresse',
        'size': 'Superficie',
        'price': 'Mise à Prix',
        'date_of_sale': 'Vente le',
        'court': 'Au TGI de',
        'date_of_visit': 'Date de Visite',
        'actual_sale_price': 'Résultat',
        'geo': 'Géolocalisation',
        'images': 'Images',
        'image_urls': 'URL des Images',
        'files': 'Dossiers',
        'file_urls': 'URL des Dossiers',
        #additional_file_titles: Optional[List[str]],
        #additional_file_urls: Optional[List[str]],
        'description': 'Description',
        #'': 'Délais pour formuler une surenchère'
    }