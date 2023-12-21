# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst
from w3lib.html import remove_tags 


from property_scraper import remove_currency


class RightmoveItem(scrapy.Item):
    # define the fields for your item here like:
    address = scrapy.Field()
    postcode = scrapy.Field()
    city = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()
    features = scrapy.Field()