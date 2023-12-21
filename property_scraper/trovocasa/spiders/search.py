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
from property_scraper.selenium.spiders.selenium import SeleniumSearchSpider
from property_scraper.io import get_worksheet
from property_scraper.immobiliare.items import ImmobiliareItem
#from property_scraper.pvp_page import PVPPage
#from property_scraper.pvp_property import PVPProperty
#from property_scraper.pvp_scraper import PVPScraper


@traced
@logged
class TrovocasaSearchSpider(SeleniumSearchSpider):
    name = 'trovocasa'
    allowed_domains = ['trovocasa.corriere.it']
    start_urls = [
        'https://trovocasa.corriere.it/annunci/search.html?&categoriaImmobile=10&version=1.1&localiMin=all&localiMax=all'
    ]
    '''
    worksheet = get_worksheet('immobiliare')
    worksheet.clear()
    HEADERS = ['Text', 'Author', 'Tags']
    worksheet.append_row(HEADERS)
    '''

    URL = 'https://trovocasa.corriere.it/annunci/search.html?&categoriaImmobile=10&version=1.1&localiMin=all&localiMax=all'
    LOGIN_URL = ''
    NEXT_PAGE_URL = ''
    WEBSITE = 'trovocasa'
    LOGIN_XPATH = {
        #'advertisement': '//button[@class="remodal-close"]',
        #'cookie' : '//button[@class="btn-default"][contains(text(), "Accetta tutti")]',
        #'email' : '//input[@name="username"]',
        #'password' : '//input[@name="password"]',
        #'login' : '//button[@class="form-btn submit-button"][contains(text(), "Login")]'
    }
    SEARCH_XPATH = {
        #'url' : '//div[@class="gx-motore-ricerca-submit"][contains(text(), "Cerca")]',
        'number_of_results' : '//span[@class="property-search-sorting__number"]',
        'number_of_results_per_page' : '//li[@class="property-card__container"]',
        'scroll' : '//button[@class="load-more"]',
        #'contract_type' : '//select[@class="gx-motore-ricerca-select-contratto"]'
    }
    SEARCH_TYPE = 'single page'

    @staticmethod
    def get_number_of_results(element):
        return element.text.split(' ')[0]    

    def parse(self, response):    
        for href in response.xpath('//a[@rel="listingName"]/@href').extract():
            url = response.urljoin(href)
            print(url)
            yield scrapy.Request(url, callback=self.parse_listing_contents)    
    
        location = response.url.split('/')[4]
        #location = self.scraper.get_location(response.url)
        #number_of_results = int(response.xpath('//span[@class="font-green"]/text()').extract_first().replace(' Annunci', '')) 
        #page_id = self.scraper.get_page_id(response.url)
        #maximum_number_of_results_per_page = self.scraper.get_maximum_number_of_results_per_page(response.url)
        #number_of_pages = self.scraper.get_number_of_pages(number_of_results, maximum_number_of_results_per_page)
        #number_of_results_per_page = self.scraper.get_number_of_results_per_page(number_of_results, number_of_pages, maximum_number_of_results_per_page)

        if location:
            template = f'{ROOT_FOLDER}/{self.name}/{self.name}_{location}.html'
        else:
            template = f'{ROOT_FOLDER}/{self.name}/{self.name}.html'
        filename = get_unique_filename(template)
        basename = os.path.basename(filename)
        with open(filename, 'wb') as f:
            f.write(response.body)
                
        for url in response.xpath("//div[@class='pure-u1']/a"):
            l = ItemLoader(item=PVPItem(), selector=urls)
            l.add_xpath('hyperlink', "//a[@class='cardlink']::attrib('href')")
            yield l.load_item()
        
        next_page = None
        current_page_id = int(response.css('div.in-pagination__item--current::text').get())
        next_page_id = current_page_id + 1
        for url in response.css('a.in-pagination__item'):
            if url.css('a::text').get() == str(next_page_id):
                print(str(next_page_id))
                next_page = url
                break
        if next_page is not None:            
            yield response.follow(next_page, callback=self.parse)
        
        '''
        for quote in response.css("div.quote"):            
            data = {
                'text': quote.css("span.text::text").extract_first(),
                'author': quote.css("small.author::text").extract_first(),
                'tags': quote.css("div.tags > a.tag::text").extract()
            }
            self.worksheet.append_row([str(data[key]).replace('“', '').replace('”', '') for key in data.keys()])
            
            yield data

        next_page_url = response.css("li.next > a::attr(href)").extract_first()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))
        '''

    def parse_listing_contents(self, response):
        item = ImmobiliareitItem()
        item['listingID'] = response.xpath('//p[@class="agencyId"]/text()').extract() 
        item['area'] = response.xpath('//li[@class="property_info"]//li[@class="first"]/span/text()').extract()
        item['bathrooms'] = response.xpath('//div[@class="featureList"]//li[contains(text(),"Bagni")]/span/text()').extract()
        item['gardenQ'] = response.xpath('//div[@class="featureList"]//li[contains(text(),"Giardino")]/span/text()').extract() 
        item['description'] = response.xpath('//meta[@itemprop="description"]/@content').extract() 
        item['address'] = response.xpath('//li[@class="address"]/h1/text()').extract() 
        item['price'] = response.xpath('//li[@class="price"]/span[@class="hidden"]/text()').extract() 
        item['url'] = response.url
        item['rooms'] = response.xpath('//div[@class="featureList"]//li[contains(text(),"Locali")]/span/text()').extract()
        item['condition'] =response.xpath('//div[@class="featureList"]//li[contains(text(),"Condizioni")]/span/text()').extract() 
        item['constructionYear'] = response.xpath('//div[@class="featureList"]//li[contains(text(),"Anno di costruzione")]/span/text()').extract()
        item['agency'] = response.xpath('//div[@class="emailAgentInfo"]/a/img[@class="logo"]/@alt').extract()
        item['propertyType'] = response.xpath('//li[@class="property_info"]//li[@class="type"]//text()').extract()
        yield item
