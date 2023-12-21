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


@traced
@logged
class AsteTelematicheSearchSpider(SeleniumSearchSpider):
    name = 'astetelematiche'
    allowed_domains = ['www.astetelematiche.it']
    start_urls = ['https://www.astetelematiche.it/aste-telematiche-beni-immobili']

    URL = 'https://www.astetelematiche.it/aste-telematiche-beni-immobili'
    LOGIN_URL = ''
    NEXT_PAGE_URL = 'https://www.asteavvisi.it/aste/cerca?tipologia_lotto=immobiliare&limit=36&orderby=datavdesc&tipologia=A&proc_old=true&page={}'
    WEBSITE = 'astetelematiche'
    LOGIN_XPATH = {
        #'advertisement': '//button[@class="remodal-close"]',
        #'cookie' : '//button[@class="iubenda-cs-accept-btn iubenda-cs-btn-primary"][contains(text(), "Accetta")]',
        #'popup_window' : '//div[@class="modal-dialog modal-md modal-dialog-centered"]/div[@id="search-modal___BV_modal_content_"][@class="modal-content"]/header[@id="search-modal___BV_modal_header_"][@class="modal-header bg-primary text-light"]/button[@class="close text-light"]',
        #'email' : '//input[@name="username"]',
        #'password' : '//input[@name="password"]',
        #'login' : '//button[@class="form-btn submit-button"][contains(text(), "Login")]'
    }
    SEARCH_XPATH = {
        #'url' : '//div[@class="gx-motore-ricerca-submit"][contains(text(), "Cerca")]',
        #'cookie' : '//div[@class="cc-compliance"]/a[class="cc-btn cc-dismiss"][contains(text(), "Acconsento")]',
        'number_of_results' : '//span[@class="numeroRisultati"][contains(text(), " risultati")]',
        'number_of_results_per_page' : '//div[@class="cbp-vm-switcher cbp-vm-view-list"]/div/ul/li',
        'scroll' : '//ul[@class="pagination pull-right pagination-top"]/li/a[contains(text(), ">")]',
        #'contract_type' : '//select[@class="gx-motore-ricerca-select-contratto"]'
    }
    
    SEARCH_SELECT = {
        #'number_of_results_per_page' : '//select[@id="ddlResultsPerPage"][@name="SearchResultPage.ResultPerPage"]',        
        #'sorting_criteria' : '//ul[@class="dropdown-menu fullwidth"]/li[@class="ng-star-inserted"]/a[@class="dropdown-option"][contains(text(), "Latest Acquisitions")]',
    }

    @staticmethod
    def get_number_of_results(element):
        return element.text.split(' ')[0]

    def parse(self, response):
        location = None #self.scraper.get_location(response.url)
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
        basename = os.path.basename(filename)
        self.to_html(filename, response)        
        #self.to_db(filename, response)
        basename = os.path.basename(filename)
                
        for url in response.xpath("//div[@class='pure-u1']/a"):
            l = ItemLoader(item=PVPItem(), selector=urls)
            l.add_xpath('hyperlink', "//a[@class='cardlink']::attrib('href')")
            yield l.load_item()
        
        next_page = None
        current_page_id = int(response.css('div.pagination').css('a.active::text').get())
        next_page_id = current_page_id + 1
        for url in response.css('div.pagination').css('a'):
            if url.css('a::text').get() == str(next_page_id):
                print(str(next_page_id))
                next_page = url
                break
        if next_page is not None:            
            yield response.follow(next_page, callback=self.parse)

    def parse_properties(self, response, number_of_results_per_page):
        pass

    def parse_property(self, response):
        keys = ['contentId']
        root = f'{ROOT_FOLDER}/{self.name}/{self.name}'
        filename = get_filename_from_identifier(response.url, keys, root)        
        self.to_html(filename, response)        
        self.to_db(filename, response)
