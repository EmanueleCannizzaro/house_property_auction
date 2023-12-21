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
#from property_scraper.io import get_worksheet
from property_scraper.selenium.spiders.selenium import SeleniumSearchSpider
from property_scraper.astalegale.items import AstaLegaleItem


@traced
@logged
class ImmobiliallastaSearchSpider(SeleniumSearchSpider):
    name = 'immobiliallasta'
    allowed_domains = ['www.immobiliallasta.it']
    start_urls = ['https://www.immobiliallasta.it/immobili/ravenna?typology=1&pastAuctions=true']

    URL = 'https://www.immobiliallasta.it/immobili/ravenna?typology=1&pastAuctions=true'
    LOGIN_URL = ''
    WEBSITE = 'immobiliallasta'
    LOGIN_XPATH = {
        #'advertisement': '//button[@class="remodal-close"]',
        #'cookie' : '//a[@class="cc-btn cc-dismiss"][contains(text(), "Accetto")]',
        #'email' : '//input[@name="Email"]',
        #'password' : '//input[@name="Password"]',
        #'remember' : '//input[@name="RememberMe"]',
        #'remember' : '//label[@for="RememberMe"]',
        #'login' : '//button[@class="cc-button cc-standard-button"][@id="btnModalLogin"][contains(text(), "Accedi")]'
    }
    LOGIN_ID = {
        #'email' : 'login-email',
        #'password' : 'login-password',        
        #<input name="RememberMe" type="hidden" value="false">
    }
    SEARCH_XPATH = {
        #'url' : '//button[@class="cc-button-search cc-button-search-primary we"][@id="btnSimpleSearchImmobili"][contains(text(), "Cerca")]',
        #'cookie' : '//a[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinDeclineAll"][contains(text(), "Use necessary cookies only")]',
        #'popup_window' : '//button[@class="btn btn-default closeDialogOk"][contains(text(), "OK")]',
        'number_of_results' : '//b[@class="text-color"][@data-test="auction-total"]',
        'number_of_results_per_page' : '//div[@class="property property-hp row g-0 fp2 clearfix"]',
        'scroll' : '//a[@class="page-link"]/i[@class="fa fa-chevron-right"]',
    }
    SEARCH_SELECT = {
        #<input type="text" class="select-dropdown" readonly="true" data-activates="select-options-85c49809-90e7-a2b5-5014-915bb3882fa7" value="12">
        #'number_of_results_per_page' : '//span[contains(text(), "120")]', #'//input[@value="12"][@class="select-dropdown"]',
        #wait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, ))).click()
        #<input type="text" class="select-dropdown" readonly="true" data-activates="select-options-eee91957-f2b4-fe30-232c-45277998a1e0" value="">
        #'sorting_criteria' : '//input[@value="Pubblicazione: più recente"][@class="select-dropdown"]',
    }
    
    @staticmethod
    def get_number_of_results(element):
        return element.text.replace('Visualizzati 1 - 10 su ', '').strip().split(' ')[0]

    def parse(self, response):
        pass