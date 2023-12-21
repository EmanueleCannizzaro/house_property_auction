# -*- coding: utf-8 -*-

import logging
import sys

from autologging import logged, traced
from datetime import datetime
import json
import os
import scrapy
from scrapy import Spider
from scrapy.loader import ItemLoader
import yaml

from property_scraper.licitor.spiders.search_property import LicitorSearchPropertySpider


@traced
@logged
class LicitorPastSearchPropertySpider(LicitorSearchPropertySpider):
    '''
        Résultats des adjudications
    '''
    name = 'licitor_pastsearchproperty'
    start_urls = [
        #'https://www.licitor.com/historique-des-adjudications.html
        #'https://www.licitor.com/ventes-aux-encheres-immobilieres/france.html?type=H'
        'https://www.licitor.com/ventes-aux-encheres-immobilieres/bretagne-grand-ouest/historique-des-adjudications.html',
        'https://www.licitor.com/ventes-aux-encheres-immobilieres/regions-du-nord-est/historique-des-adjudications.html',
        'https://www.licitor.com/ventes-aux-encheres-immobilieres/paris-et-ile-de-france/historique-des-adjudications.html',
        'https://www.licitor.com/ventes-aux-encheres-immobilieres/centre-loire-limousin/historique-des-adjudications.html',
        'https://www.licitor.com/ventes-aux-encheres-immobilieres/sud-est-mediterrannee/historique-des-adjudications.html',
        'https://www.licitor.com/ventes-aux-encheres-immobilieres/sud-ouest-pyrenees/historique-des-adjudications.html'        
    ]


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.settings import Settings
    from scrapy.utils.log import configure_logging
    
    #logging.disable(logging.CRITICAL)
    configure_logging()
    
    # Load the settings file
    settings = Settings()
    settings_module_path = 'property_scraper.licitor.settings'
    # Replace with your actual settings module path
    settings.setmodule(settings_module_path)

    # Create a crawler process with the loaded settings
    process = CrawlerProcess(settings)

    # Add your spider(s) to the crawler process
    process.crawl(LicitorPastSearchPropertySpider)

    # Start the crawler process    
    process.start()
