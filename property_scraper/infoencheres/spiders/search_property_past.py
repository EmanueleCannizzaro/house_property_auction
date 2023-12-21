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

from property_scraper.infoencheres.spiders.search_property import InfoEncheresSearchPropertySpider


@traced
@logged
class InfoEncheresPastSearchPropertySpider(InfoEncheresSearchPropertySpider):
    '''
        Résultats des adjudications
    '''
    name = 'infoencheres_pastsearchproperty'
    start_urls = [
        'https://www.info-encheres.com/recherche.php?1=1&cat=2&snr=0&nbpage=100',
        #'https://www.info-encheres.com/vente-encheres-immobilieres-resultats.html'
    ]


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.settings import Settings
    from scrapy.utils.log import configure_logging
    
    #logging.disable(logging.CRITICAL)
    configure_logging()
    
    # Load the settings file
    settings = Settings()
    settings_module_path = 'property_scraper.infoencheres.settings'
    # Replace with your actual settings module path
    settings.setmodule(settings_module_path)

    # Create a crawler process with the loaded settings
    process = CrawlerProcess(settings)

    # Add your spider(s) to the crawler process
    process.crawl(InfoEncheresPastSearchPropertySpider)

    # Start the crawler process    
    process.start()
