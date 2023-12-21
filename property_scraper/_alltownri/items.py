# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose
from w3lib.html import remove_tags

from property_scraper import remove_currency


class AlltownriItem(scrapy.Item):
    # define the fields for your item here like:
    id = scrapy.Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())
    #item['home_listing_id'] = mls_number
    name = scrapy.Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())
    availability = scrapy.Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())
    address = scrapy.Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())
    #item['address.addr1'] = address
    city = scrapy.Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())
    #item['address.city'] = city
    region = scrapy.Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())
    #item['address.region'] = region
    country = scrapy.Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())
    #item['address.country'] = country
    postal_code = scrapy.Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())
    #item['address.postal_code'] = postal_code
    image = scrapy.Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())
    #item['image[0].url'] = image
    price = scrapy.Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())
    url = scrapy.Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())
    description = scrapy.Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())
    #bed = scrapy.Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())
    no_of_bedrooms = scrapy.Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())
    #item['num_beds'] = bedrooms
    #bath = scrapy.Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())
    no_of_bathrooms = scrapy.Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())
    #item['num_baths'] = bathrooms
    status = scrapy.Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())
    mls_num = scrapy.Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())
    #item['mls_num'] = mls_number
    property_type = scrapy.Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())
    #item['property_type'] = type1
    listing_type = scrapy.Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())
    build_year = scrapy.Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())
    #item['year_built'] = year
    size = scrapy.Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())
