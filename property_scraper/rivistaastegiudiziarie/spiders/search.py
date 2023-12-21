# -*- coding: utf-8 -*-

import logging
import sys

from autologging import logged, TRACE, traced
from datetime import datetime
import json
import os
import pandas as pd
import scrapy
from scrapy.loader import ItemLoader
#from urllib.parse import urljoin

from property_scraper import LOCALHOST_URL_ROOTNAME, ROOT_FOLDER, get_filename_from_identifier, get_unique_filename
from property_scraper.selenium.spiders.selenium import SeleniumSearchSpider
from property_scraper.io import get_worksheet
from property_scraper.astainsieme.items import AstaInsiemeItem


class RivistaAsteGiudiziarieSearchSpider(SeleniumSearchSpider):
    name = 'rivistaastegiudiziarie'
    allowed_domains = ['www.rivistaastegiudiziarie.it']
    start_urls = [
        'https://www.rivistaastegiudiziarie.it/'
    ]

    URL = 'https://www.rivistaastegiudiziarie.it/aste/cerca?tipologia_lotto=immobiliare&limit=36&proc_old=true'
    LOGIN_URL = ''
    NEXT_PAGE_URL = 'https://www.rivistaastegiudiziarie.it/aste/cerca?tipologia_lotto=immobiliare&limit=36&proc_old=true&page={}'
    WEBSITE = 'canaleaste'
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
        'cookie' : '//button[@class="iubenda-cs-accept-btn iubenda-cs-btn-primary"][contains(text(), "Accetta")]',
        'number_of_results' : '//h5[@class="font-weight-bold mb-3 mb-sm-0"][contains(text(), " aste giudiziarie")]',
        'number_of_results_per_page' : '//div[@class="card vertical-card horizontal rounded overflow-hidden mb-4 border-0 drop-shadow"]',
        #'scroll' : '//li[@class="page-item"]/a[class="page-link"][contains(text(), ">")]',
        #'contract_type' : '//select[@class="gx-motore-ricerca-select-contratto"]'
    }
    
    SEARCH_SELECT = {
        'number_of_results_per_page' : '//select[@class="mr-3 d-none d-sm-block custom-select"]',
        #'sorting_criteria' : '//ul[@class="dropdown-menu fullwidth"]/li[@class="ng-star-inserted"]/a[@class="dropdown-option"][contains(text(), "Latest Acquisitions")]',
    }

    @staticmethod
    def get_number_of_results(element):
        return element.text.split(' ')[0]

    def parse(self, response):
        pass
