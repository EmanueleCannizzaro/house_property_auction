# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose
from w3lib.html import remove_tags 

from property_scraper import remove_currency


class TestScraperItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
