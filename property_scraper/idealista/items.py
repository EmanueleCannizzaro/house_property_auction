# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose
from w3lib.html import remove_tags 

from property_scraper import remove_currency


class IdealistaSearchItem(scrapy.Item):
    #Matching variables of every flat to be scrapped
    #id_idealista = scrapy.Field()
    date = scrapy.Field()
    link = scrapy.Field()
    price = scrapy.Field()
    address = scrapy.Field()
    sqft_m2 = scrapy.Field()
    rooms = scrapy.Field()
    discount = scrapy.Field()
    floor_elevator = scrapy.Field()

class IdealistaPropertyItem(scrapy.Item):
    slug = scrapy.Field()
    url = scrapy.Field()
    price = scrapy.Field()
    date = scrapy.Field()

    title = scrapy.Field()
    price_raw = scrapy.Field()
    source = scrapy.Field()
    url = scrapy.Field()
    country = scrapy.Field()
    # TODO: Change string concatenation
    slug = scrapy.Field()
    transaction = scrapy.Field()
        property_item['property_type' = scrapy.Field()
        property_item['address_province' = scrapy.Field()
        property_item['address_path' = scrapy.Field()
        property_item['geocode_raw' = scrapy.Field()
        property_item['geocode' = scrapy.Field()
                      
        # property_item['html'] = response.text
        property_item['desc'] = response.xpath('//div[@class="adCommentsLanguage expandable"]/text()').extract_first()
        property_item['name'] = response.xpath('//div[@class="advertiser-data txt-soft"]/p/text()').extract_first()
        # FIXED: phone sometimes is shown as:
        phones = [response.xpath('//p[@class="txt-big txt-bold _browserPhone"]/text()').extract_first(),
                  response.xpath('//p[@class="txt-bold _browserPhone icon-phone"]/text()').extract_first(),
                  response.xpath('//a[@class="_mobilePhone"]/text()').extract_first(),
                  response.xpath('//div[@class="phone last-phone"]/text()').extract_first()]
        property_item['phones'] = phones
        property_item['address_exact'] = not bool(
            response.xpath('//div[@class="contextual full-width warning icon-feedbk-alert"]/text()').extract_first())
        property_item['address_raw'] = ".".join(response.xpath('//div[@id="addressPromo"]/ul/li/text()').extract())
        # mapConfig={latitude:"42.0064667",longitude:"-5.6714257",
        match = re.search(r"latitude:\"(.*)\",longitude:\"(.*)\",onMapElements", response.text)
        property_item['latitude'] = match.group(1)
        property_item['longitude'] = match.group(2)
        property_item['real_estate_raw'] = response.xpath('//a[@class="about-advertiser-name"]/@href').extract_first()
        # Will continue parsing the child property, with the correct specific child parameters
        # Example: property_item = self.parse_garage(response, property_item)
        property_item = self.parse_property_middleware(response, property_item)

        # If property has a real estate
        if property_item['real_estate_raw']:
            # TODO: Change string concatenation
            real_estate_slug = 'id-' + property_item['real_estate_raw'].split('/')[2]
            real_estate = RealEstate.objects.filter(slug=real_estate_slug)
            # if the real estate is not in de db
            if not real_estate:
                real_estate_page = response.urljoin(property_item['real_estate_raw'])
                yield scrapy.Request(real_estate_page, callback=self.parse_real_estate,
                                     meta={'property_item': property_item})
            else:
                property_item['real_estate'] = real_estate.first()
                yield property_item
        else:
            yield property_item

