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


class CanaleAsteSearchSpider(SeleniumSearchSpider):
    
    ''' Copy of asteavvisi '''
    
    name = 'canaleaste'
    allowed_domains = ['www.canaleaste.it']
    start_urls = [
        'https://www.canaleaste.it/aste/cerca?tipologia_lotto=immobiliare&limit=36&tipologia=A&proc_old=true'
    ]

    URL = 'https://www.canaleaste.it/aste/cerca?tipologia_lotto=immobiliare&limit=36&tipologia=A&proc_old=true'
    LOGIN_URL = ''
    NEXT_PAGE_URL = 'https://www.canaleaste.it/aste/cerca?tipologia_lotto=immobiliare&limit=36&tipologia=A&proc_old=true&page={}'
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
        #'scroll' : '//li[@class="page-item"]/a[class="page-link"]',
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

#https://www.asteavvisi.it/aste/cerca?tipologia_lotto=immobiliare&limit=36&tipologia=A&proc_old=true
#https://www.asteavvisi.it/aste/cerca?tipologia_lotto=immobiliare&limit=36&tipologia=A&page=2
#<a href="/aste/cerca?tipologia_lotto=immobiliare&amp;limit=36&amp;tipologia=A&amp;page=75" aria-label="Go to next page" target="_self" class="page-link nuxt-link-active">›</a>

#<nav aria-hidden="false" aria-label="Pagination" class="mb-0 float-right"><ul aria-disabled="false" class="pagination b-pagination justify-content-end"><li class="page-item"><a href="/aste/cerca?tipologia_lotto=immobiliare&amp;limit=36&amp;tipologia=A&amp;page=1" aria-label="Go to first page" target="_self" class="page-link nuxt-link-active">«</a></li><li class="page-item"><a href="/aste/cerca?tipologia_lotto=immobiliare&amp;limit=36&amp;tipologia=A&amp;page=73" aria-label="Go to previous page" target="_self" class="page-link nuxt-link-active">‹</a></li><!----><li role="separator" class="page-item disabled bv-d-xs-down-none"><span class="page-link">…</span></li><li class="page-item"><a href="/aste/cerca?tipologia_lotto=immobiliare&amp;limit=36&amp;tipologia=A&amp;page=73" aria-label="Go to page 73" target="_self" class="page-link nuxt-link-active">73</a></li><li class="page-item active"><a href="/aste/cerca?tipologia_lotto=immobiliare&amp;limit=36&amp;tipologia=A&amp;page=74" aria-current="page" aria-label="Go to page 74" target="_self" class="page-link nuxt-link-exact-active nuxt-link-active">74</a></li><li class="page-item"><a href="/aste/cerca?tipologia_lotto=immobiliare&amp;limit=36&amp;tipologia=A&amp;page=75" aria-label="Go to page 75" target="_self" class="page-link nuxt-link-active">75</a></li><li role="separator" class="page-item disabled bv-d-xs-down-none"><span class="page-link">…</span></li><!----><li class="page-item"><a href="/aste/cerca?tipologia_lotto=immobiliare&amp;limit=36&amp;tipologia=A&amp;page=75" aria-label="Go to next page" target="_self" class="page-link nuxt-link-active">›</a></li><li class="page-item"><a href="/aste/cerca?tipologia_lotto=immobiliare&amp;limit=36&amp;tipologia=A&amp;page=153" aria-label="Go to last page" target="_self" class="page-link nuxt-link-active">»</a></li></ul></nav>
