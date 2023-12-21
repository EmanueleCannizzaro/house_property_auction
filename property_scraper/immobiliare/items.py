# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose
from w3lib.html import remove_tags

from property_scraper import remove_currency


class ImmobiliareItem(scrapy.Item):
    # define the fields for your item here like:
    #name = scrapy.Field()
	listingID = scrapy.Field()
	listingDate = scrapy.Field()
	contract = scrapy.Field()
	area = scrapy.Field()
	bathrooms = scrapy.Field() 
	gardenQ = scrapy.Field()  
	energyClass = scrapy.Field()
	description = scrapy.Field()
	address = scrapy.Field() 
	price = scrapy.Field() 
	url = scrapy.Field()
	rooms = scrapy.Field()
	condition = scrapy.Field()
	constructionYear = scrapy.Field()
	agency = scrapy.Field()
	propertyType = scrapy.Field()