# -*- coding: utf-8 -*-

import logging
import sys

from autologging import logged, TRACE, traced
from datetime import datetime
import json
import os
import pandas as pd
import re
import scrapy
from scrapy.loader import ItemLoader
#from urllib.parse import urljoin

from property_scraper import LOCALHOST_URL_ROOTNAME, ROOT_FOLDER, get_unique_filename
from property_scraper.io import get_worksheet
from property_scraper.atico.items import PropertyItem
from property_scraper.pvp_scraper import PVPScraper


class AticoSpider(scrapy.Spider):
    name = 'atico'
    scraper = PVPScraper()

    def __init__(self, page_url='', url_file=None, *args, **kwargs):
        pages = 5
        self.start_urls = ['https://www.atico.es/resultados-de-la-busqueda/page/{}/'.format(i + 1) for i in
                           range(pages)]

        if not page_url and url_file is None:
            TypeError('No page URL or URL file passed.')

        if url_file is not None:
            with open(url_file, 'r') as f:
                self.start_urls = f.readlines()
        if page_url:
            # Replaces the list of URLs if url_file is also provided
            self.start_urls = [page_url]

        super().__init__(*args, **kwargs)

    def start_requests(self):        
        for page in self.start_urls:
            logging.info("Scraping page: {}".format(page))
            yield scrapy.Request(url=page, callback=self.crawl_page)

    def crawl_page(self, response):
        location = response.url.split('/')[3]# None #self.scraper.get_location(response.url)
        number_of_results = int(response.xpath('//p[contains(text(), " Results - Guardar esta búsqueda?")]/text()').extract_first().replace(' Results - Guardar esta búsqueda?', ''))
        page_id = self.scraper.get_page_id(response.url)
        maximum_number_of_results_per_page = self.scraper.get_maximum_number_of_results_per_page(response.url)
        number_of_pages = self.scraper.get_number_of_pages(number_of_results, maximum_number_of_results_per_page)
        number_of_results_per_page = self.scraper.get_number_of_results_per_page(number_of_results, number_of_pages, maximum_number_of_results_per_page)

        if location:
            template = f'{ROOT_FOLDER}/{self.name}/{self.name}_{location}.html'
        else:
            template = f'{ROOT_FOLDER}/{self.name}/{self.name}.html'
        filename = get_unique_filename(template)
        basename = os.path.basename(filename)
        self.to_html(filename, response)        
        #self.to_db(filename, response)
        basename = os.path.basename(filename)

        property_urls = response.css('.property-item a.hover-effect::attr(href)').getall()
        for property in property_urls:
            logging.info("Scraping property: {}".format(property))
            yield scrapy.Request(url=property, callback=self.crawl_property)
            
        next_page = None
        current_page_id = int(response.css('div.pagination-main').xpath("//li[@class='active']//a").attrib['data-houzepagi'])
        next_page_id = current_page_id + 1
        next_page = response.css('div.pagination-main').xpath(f"//li//a[@data-houzepagi={next_page_id}]")[0].attrib['href']
        if next_page is not None:            
            yield response.follow(next_page, callback=self.parse)

        

    def crawl_property(self, response):
        pid = response.xpath('//div[contains(@id, "ID-")]').attrib['id'].replace('ID-', '')
        filename = f'{ROOT_FOLDER}/{self.name}/{self.name}_{pid}.html'
        self.to_html(filename, response)        
        self.to_db(filename, response)        
        
        property = PropertyItem()

        # Resource
        property["resource_url"] = "https://www.atico.es/"
        property["resource_title"] = 'Atico'
        property["resource_country"] = 'ES'

        # Property
        property["active"] = 1
        property["url"] = response.url
        property["title"] = response.xpath('.//*[@class="table-cell"]/h1/text()').get()
        property["subtitle"] = response.xpath('.//*[@class="descrip-corta"]/text()').get()
        property["location"] = self.get_location(response)
        property["extra_location"] = ''
        property["body"] = ';'.join(response.xpath('.//*[@id="description"]/p//text()').extract())

        # Price
        property["current_price"] = response.xpath('.//*[@class="header-right"]/span/text()').get()[:-1]
        property["original_price"] = response.xpath('.//*[@class="header-right"]/span/text()').get()[:-1]
        property["price_m2"] = ''
        property["area_market_price"] = ''
        property["square_meters"] = response.xpath('.//*[@class="ico-detail"]/span/text()').get()[:-3]

        # Details
        property["area"] = ''
        property["tags"] = self.get_tags(response)
        property["bedrooms"] = response.xpath('.//*[@class="ico-txt"]//text()').extract()[1][:1]
        property["bathrooms"] = response.xpath('.//*[@class="ico-txt"]//text()').extract()[2][:1]
        property["last_update"] = ''
        property["certification_status"] = response.xpath('.//*[@class="txt-certif"]/text()').get()
        property["consumption"] = ''
        property["emissions"] = response.xpath('.//*[@class="txt-certif"]/text()').get()

        # Multimedia
        property["main_image_url"] = self.get_main_img_url(response)
        property["image_urls"] = self.get_img_urls(response)
        property["floor_plan"] = ''
        property["energy_certificate"] = ''
        property["video"] = ''

        # Agents
        property["seller_type"] = ''
        property["agent"] = "ATICO Especialistas en Aticos"
        property["ref_agent"] = "ATICO Especialistas en Aticos"
        property["source"] = "ATICO Especialistas en Aticos"
        property["ref_source"] = self.get_reference(response)
        property["phone_number"] = ''

        # Additional
        property["additional_url"] = ''
        property["published"] = ''
        property["scraped_ts"] = ''

        yield property

    def get_img_url_list(self, response):
        img_url_wraps = response.xpath('//*[@id="gallery"]//@style').extract()
        extract_url = lambda url_wrap: re.search('url\((.*?)\)', url_wrap).group(1)
        return list(map(extract_url, img_url_wraps))

    def get_main_img_url(self, response):
        return self.get_img_url_list(response)[0]

    def get_img_urls(self, response):
        return ';'.join(self.get_img_url_list(response)[1:])

    def get_tags(self, response):
        property_type = ' '.join(response.xpath('//*[@id="detail"]/div[2]/ul/li[8]//text()').extract())
        garaje = ' '.join(response.xpath('//*[@id="detail"]/div[2]/ul/li[7]//text()').extract())
        characteristics = response.xpath('//*[@id="features"]//text()').extract()
        characteristics = list(filter(lambda x: '\n' not in x, characteristics))[1:-1]

        return ';'.join([property_type, garaje] + characteristics)

    def get_location(self, response):
        ciudad = ' '.join(response.xpath('.//*[@class="detail-city"]//text()').extract())
        barrio = ' '.join(response.xpath('.//*[@class="detail-area"]//text()').extract())

        return ';'.join([ciudad, barrio])

    def get_reference(self, response):
        full_reference = response.xpath("//*[@class='referencia']/text()").get()
        extract_ref_number = lambda reference: re.search('Ref. (\d+)', reference).group(1)
        return extract_ref_number(full_reference)


    def to_html(self, filename:str, response):
        with open(filename, 'wb') as f:
            f.write(response.body)
        
    def to_db(self, filename:str, response):
        pass

    def to_gsheet(self):
        pass

