# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose
from w3lib.html import remove_tags 

from property_scraper import remove_currency


class VrbodataItem(scrapy.Item):
    # define the fields for your item here like:
    # Location, Title, Sleep, Bedroom, Price and Image link

    name = scrapy.Field()
    price = scrapy.Field()
    thumb = scrapy.Field()
    details = scrapy.Field()


