# -*- coding: utf-8 -*-

import logging
import sys

from autologging import logged, TRACE, traced
from datetime import datetime
import os
import pandas as pd
import scrapy
from scrapy.loader import ItemLoader

from property_scraper import LOCALHOST_URL_ROOTNAME, ROOT_FOLDER, get_filename_from_identifier, get_unique_filename
from property_scraper.io import get_worksheet
from property_scraper.alltownri.items import AlltownriItem


@traced
@logged
class AlltownSpider(scrapy.Spider):
    name = 'alltownri'
    allowed_domains = ['alltownri.com']
    start_urls = [
        "https://www.alltownri.com/search/results/?state=RI&county=all&city=all&beds_min=all&baths_min=all&list_price_min=175000&list_price_max=325000&type=res"        
    ]

    def parse(self, response):
        location = response.url.split('/')[4]
        number_of_results = int(response.xpath('//span[@class="font-green"]/text()').extract_first().replace(' Annunci', '')) 
        page_id = self.scraper.get_page_id(response.url)
        maximum_number_of_results_per_page = self.scraper.get_maximum_number_of_results_per_page(response.url)
        number_of_pages = self.scraper.get_number_of_pages(number_of_results, maximum_number_of_results_per_page)
        number_of_results_per_page = self.scraper.get_number_of_results_per_page(number_of_results, number_of_pages, maximum_number_of_results_per_page)
        
        if location:
            template = f'{ROOT_FOLDER}/{self.name}/{self.name}_{location}.html'
        else:
            template = f'{ROOT_FOLDER}/{self.name}/{self.name}.html'
        filename = get_unique_filename(template)
        self.to_html(filename, response)        
        #self.to_db(filename, response)
        basename = os.path.basename(filename)


        urls = response.xpath("//div[@class='property-detail-section']/div/div/a/@href") #.extract()
        #print("Total : ", len(items))
        #if items:
        for url in urls:
            #link = "https://www.alltownri.com{0}".format(item)
            #yield scrapy.Request(url=link, callback=self.parse_property)
            # break
        
            l = ItemLoader(item = AlltownriItem(), selector=urls)
            #l.add_xpath('image', "//meta[@property='og:image']/@content")
            l.add_xpath('address', "//div[@class='small-12 columns prop-address']/h1/text()")
            #l.add_xpath('id', "") # response.url.split("RIS-")[-1].split("/")[0].strip()
            #l.add_xpath('name', "")
            #l.add_xpath('address', "")
            #l.add_xpath('city', "")
            #l.add_xpath('postal_code', "")
            #l.add_xpath('region', "")
            #l.add_xpath('availability', "")
            #l.add_xpath('listing_type', "")
            #l.add_xpath('', "") # "for_sale_by_agent"
            l.add_xpath('price', ".//dt[contains(text(), 'List Price')]/following-sibling::dd/text()")
            #l.add_xpath('mls_number', ".//dt[contains(text(), 'MLS#')]/following-sibling::dd/text()")
            l.add_xpath('status', ".//dt[contains(text(), 'Status')]/following-sibling::dd/text()")
            #l.add_xpath('type', ".//dt[contains(text(), 'Type')]/following-sibling::dd/text()")
            l.add_xpath('city', ".//dt[contains(text(), 'City')]/following-sibling::dd/text()")
            l.add_xpath('country', ".//dt[contains(text(), 'Country')]/following-sibling::dd/text()")
            l.add_xpath('no_of_bedrooms', ".//dt[contains(text(), 'Bedrooms')]/following-sibling::dd/text()")
            l.add_xpath('no_of_bathrooms', ".//dt[contains(text(), 'Bathrooms')]/following-sibling::dd/text()")
            l.add_xpath('size', ".//dt[contains(text(), 'Living Area')]/following-sibling::dd/text()")
            l.add_xpath('build_year', ".//dt[contains(text(), 'Year')]/following-sibling::dd/text()")
            l.add_xpath('description', "//div[@class='additional-information-element']/p/text()")
            #l.add_xpath('unit', "//dd[@class='price']/ancestor::dl/dt")[-2].xpath("./text()")
            #l.add_xpath('', "")
            
            yield l.load_item()
        
        #next_page_list = response.xpath("//ul[@class='pagination']/li")[-2].xpath("./a/text()").extract_first()
        #if next_page_list:
        #    pages = int(next_page_list)
        #    for page in range(2, pages):
        #        next_url = "https://www.alltownri.com/search/results/?state=RI&county=all&city=all&beds_min=all&baths_min=all&list_price_min=175000&list_price_max=325000&type=res&page={0}".format(page)
        #        yield scrapy.Request(next_page, callback=self.parse)
        
    def parse_properties(self, response, number_of_results_per_page):
        pass
        '''
        items = response.xpath("//div[@class='property-detail-section']/div/div/a/@href").extract()
        print("Total : ",len(items))
        if items:
            for item in items:
                link = "https://www.alltownri.com{0}".format(item)
                #yield scrapy.Request(url=link, callback=self.parse_property)
        '''

    def parse_property(self, response):
        keys = ['contentId']
        root = f'{ROOT_FOLDER}/{self.name}/{self.name}'
        filename = get_filename_from_identifier(response.url, keys, root)        
        self.to_html(filename, response)        
        self.to_db(filename, response)

        '''
        if address_txt:
            address_txt = address_txt.split(", ")
            name = address_txt[0].strip() + ", " + address_txt[1].strip()
            address = address_txt[0].strip()
            city = address[1].strip()
            postal_code = address_txt[-1].strip().split()[-1].strip()
            region_txt = address_txt[-1].strip().split()[0].strip()
            if region_txt == "RI":
                region = "Rhode Island"
            else:
                region = region_txt
            country = "United States"
            unit = unit.lower()
            description = ""
            if bedrooms and bathrooms and size and unit:
                description = bedrooms + "BR | " + bathrooms + "BA | " + size + " " + unit
            if mls_number:
                mls_number = mls_number.replace("RIS-", "").strip()
        '''
