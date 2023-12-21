# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field
from itemloaders.processors import TakeFirst, MapCompose
from w3lib.html import remove_tags

#from property_scraper import remove_currency

from property_scraper.pvp.items import PVPSearchItem, PVPSearchModel, PVPSearchPropertyItem, PVPSearchPropertyModel


class AstaGiudiziariaSearchItem(PVPSearchItem):
    pass
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
    '''
class AstaGiudiziariaSearchModel(PVPSearchModel):
    pass

class AstaGiudiziariaSearchPropertyItem(PVPSearchPropertyItem):
    pass

class AstaGiudiziariaSearchPropertyModel(PVPSearchPropertyModel):
    pass