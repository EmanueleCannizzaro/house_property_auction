# -*- coding: utf-8 -*-

import logging
import sys

from autologging import logged, TRACE, traced
from datetime import datetime
import json
import os
#import pandas as pd
from scrapy import Spider
from scrapy.loader import ItemLoader
#from urllib.parse import urljoin
import yaml
import scrapy


@traced
@logged
class SubitoSearch(Spider):
    name = 'subito_search'
    allowed_domains = ['www.subito.it']
    start_urls = ['http://www.subito.it/']
    follow_links = False
    download_pages = False
    search_datetime = datetime.now().strftime("%Y%m%d%H%M%S")

    def start_requests(self):
        with open('pvp.json') as f:
            URLS = json.load(f)
            self.follow_links = URLS['follow_links']
            self.download_pages = URLS['download_pages']
            for url in URLS['searches']:
                yield scrapy.Request(URLS['root'] + url)
				

    def parse(self, response):
       url = response.url
        location = self.get_location(response.url)
        number_of_results = int(response.xpath('//span[@class="font-green"]/text()').extract_first().replace(' Annunci', ''))
        page_id = self.get_page_id(response.url)
        maximum_number_of_results_per_page = self.get_maximum_number_of_results_per_page(response.url)
        number_of_pages = self.get_number_of_pages(number_of_results, maximum_number_of_results_per_page)
        number_of_results_per_page = self.get_number_of_results_per_page(number_of_results, number_of_pages, maximum_number_of_results_per_page)

        if location:
            template = f"{ROOT_FOLDER}/{self.name.split('_')[0]}/{self.name.split('_')[0]}_{location}.html"
        else:
            template = f"{ROOT_FOLDER}/{self.name.split('_')[0]}/{self.name.split('_')[0]}.html"
        filename = get_unique_filename(template, self.search_datetime)
        basename = os.path.basename(filename)
        if LOCALHOST_URL_ROOTNAME not in url:
            if self.download_pages:
                self.to_html(filename, response)
            url_localhost = os.path.join(LOCALHOST_URL_ROOTNAME, self.name.split('_')[0], basename)
        else:
            url_localhost = url


        #<div class="items__item item-card item-card--big BigCard-module_card__Exzqv">
        #<nav class="pagination-container pagination_pagination-container___4uTK"

        #<button type="button" class="index-module_sbt-button__hQMUx index-module_text__nhl4i index-module_medium__pYkH6 pagination__btn index-module_icon-only__gkRU8" aria-label="Andare a pagina 171"><span class="index-module_sbt-text-atom__ed5J9 index-module_token-button__eMeQT size-normal index-module_weight-semibold__MWtJJ index-module_button-text__VZcja">171</span></button>


        self.search = PVPSearchItem()
        self.items = self.search.items
        search_loader = ItemLoader(item=self.search) #, response=response)
        search_loader.add_value('filename', filename)
        search_loader.add_value('basename', basename)
        search_loader.add_value('id', os.path.splitext(basename)[0])
        search_loader.add_value('spider_name', self.name)
        search_loader.add_value('location', location)
        search_loader.add_value('page_id', page_id)
        search_loader.add_value('number_of_results', number_of_results)
        search_loader.add_value('number_of_pages', number_of_pages)
        search_loader.add_value('number_of_results_per_page', number_of_results_per_page[page_id-1])
        search_loader.add_value('url', url)
        search_loader.add_value('url_localhost', url_localhost)
        search_loader.add_value('is_downloaded', False)
        search_loader.add_value('is_relative_href_fixed', False)
        search_loader.add_value('response_status_code', 200)
        yield search_loader.load_item()

        if self.follow_links:
            next_page = response.xpath('//li[contains(@class,"pull-right")]/a').attrib['href']
            #next_page = response.css('[rel="next"]::attr(href)').get()
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)

    def to_html(self, filename:str, response):
        with open(filename, 'wb') as f:
            f.write(response.body)

    @staticmethod
    def get_location(s: str, prefix: str = 'localita='):
        location = None
        tokens = s.split('/')[-1].split('?')[-1].split('&')
        for token in tokens:
            if token.startswith(prefix):
                location = token[len(prefix):].lower()
                return location
        return location

    @staticmethod
    def get_page_id(s: str, prefix: str = 'frame4_item='):
        page_id = 1
        tokens = s.split('/')[-1].split('?')[-1].split('&')
        for token in tokens:
            if token.startswith(prefix):
                page_id = int(token[len(prefix):])
                return page_id
        return page_id

    @staticmethod
    def get_maximum_number_of_results_per_page(s: str, prefix: str = 'elementiPerPagina='):
        maximum_number_of_results_per_page = 50
        tokens = s.split('/')[-1].split('?')[-1].split('&')
        for token in tokens:
            if token.startswith(prefix):
                maximum_number_of_results_per_page = int(token[len(prefix):])
                return maximum_number_of_results_per_page
        return maximum_number_of_results_per_page

    @staticmethod
    def get_number_of_pages(number_of_results: int, maximum_number_of_results_per_page: int):
        number_of_pages = number_of_results // maximum_number_of_results_per_page
        if number_of_results % maximum_number_of_results_per_page > 0:
            number_of_pages += 1
        # Rightmove will return a maximum of 42 results pages, hence:
        return number_of_pages

    @staticmethod
    def get_number_of_results_per_page(number_of_results: int, number_of_pages: int,
                                       maximum_number_of_results_per_page: int):
        if number_of_results == number_of_pages * maximum_number_of_results_per_page:
            number_of_results_per_page = [maximum_number_of_results_per_page] * number_of_pages
        else:
            number_of_results_per_page = [maximum_number_of_results_per_page] * (number_of_pages - 1) + [
                number_of_results % maximum_number_of_results_per_page]
        return number_of_results_per_page
