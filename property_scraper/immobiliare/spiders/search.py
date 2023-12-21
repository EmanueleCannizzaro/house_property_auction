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
class ImmobiliareSearchSpider(SeleniumSearchSpider):
    
    '''
    You'll need to have Scrapy and Selenium installed in your Python environment. Additionally, make sure to have the Chrome WebDriver (chromedriver) installed and provide the correct path to it in the webdriver.Chrome() constructor.

    Customize the interactions with the web page using Selenium by adding appropriate code in the parse method. Adjust the CSS selectors to extract the desired property details based on the HTML structure of the immobiliare.it website.

    To run the script, save it in a Python file (e.g., immobiliare_spider.py) and execute the file using python immobiliare_spider.py. The extracted property details will be displayed or can be modified to save to a file or perform further processing.

    Remember to review and update the CSS selectors as needed to ensure accurate data extraction based on the website structure.
    
    
    In this improved version, a custom PropertyItem class is defined using Scrapy's Item and Field classes. It allows you to define the fields for each property and easily store the extracted details.

    The search results are processed within the parse method, where the property details are extracted and assigned to the PropertyItem object. Additional fields can be added to the PropertyItem class as needed.

    You can further customize the script by adding pagination logic or performing additional operations on the search results.

    To run the script, save it in a Python file (e.g., immobiliare_spider.py) and execute the file using python immobiliare_spider.py. The extracted property details will be processed as PropertyItem objects, which can be saved to a file or further processed as per your requirements.

    Remember to update the CSS selectors and add the necessary logic to handle pagination or additional operations based on the immobiliare.it website structure and your specific needs.
    
    In this updated version, the ItemLoader is used to process the property details. The PropertyItem class remains the same with the defined fields.

    The search results are processed within the parse method using an ItemLoader object. The property details are added to the loader using add_css or add_xpath methods. Additional fields can be added and processed in a similar manner.

    Remember to update the CSS selectors and add the necessary logic to handle pagination or additional operations based on the immobiliare.it website structure and your specific needs.

    To run the script, save it in a Python file (e.g., immobiliare_spider.py) and execute the file using python immobiliare_spider.py. The extracted property details will be processed as PropertyItem objects, which can be saved to a file or further processed as per your requirements.
    
    '''
    
    name = 'immobiliare'
    allowed_domains = ['www.immobiliare.it']
    start_urls = [
        'https://www.immobiliare.it/vendita-case/ravenna-provincia/?criterio=rilevanza',
        'https://www.immobiliare.it/vendita-case/bologna-provincia/?criterio=rilevanza',
        'https://www.immobiliare.it/vendita-case/palermo-provincia/?criterio=rilevanza',
        'https://www.immobiliare.it/vendita-case/genova-provincia/?criterio=rilevanza'
    ]
    '''
    worksheet = get_worksheet('immobiliare')
    worksheet.clear()
    HEADERS = ['Text', 'Author', 'Tags']
    worksheet.append_row(HEADERS)
    '''

    URL = 'https://www.immobiliare.it/aste-immobiliari/ravenna-provincia/?criterio=rilevanza'
    LOGIN_URL = ''
    NEXT_PAGE_URL = 'https://www.immobiliare.it/aste-immobiliari/ravenna-provincia/?criterio=rilevanza&pag={}'
    WEBSITE = 'immobiliare'
    LOGIN_XPATH = {
        #'advertisement': '//button[@class="remodal-close"]',
        'cookie' : '//button[@class="didomi-components-button didomi-button didomi-dismiss-button didomi-components-button--color didomi-button-highlight highlight-button"]/span[contains(text(), "Agree & Close")]',
        #'cookie' : '//span[@class="didomi-continue-without-agreeing"][contains(text(), "Continue without agreeing")]',        
        #'email' : '//input[@name="username"]',
        #'password' : '//input[@name="password"]',
        #'login' : '//button[@class="form-btn submit-button"][contains(text(), "Login")]'
    }
    SEARCH_XPATH = {
        #'url' : '//div[@class="gx-motore-ricerca-submit"][contains(text(), "Cerca")]',
        'number_of_results' : '//div[@class="in-searchList__title"][contains(text(), " risultati per:")]',
        'number_of_results_per_page' : '//li[@class="nd-list__item in-realEstateResults__item"]',
        #'scroll' : '//div[@class="in-pagination__control"][@data-cy="pagination-next"]/a[@class="in-pagination__item"]',
        #'contract_type' : '//select[@class="gx-motore-ricerca-select-contratto"]'
    }

    @staticmethod
    def get_number_of_results(element):
        return element.text.split(' ')[0]    

    def parse(self, response):
        for href in response.css('div .annuncio_title strong a::attr(href)').extract():
            url = response.urljoin(href)
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
        item['listingID'] = response.xpath('//div[@id="details"]/table//tr/td[contains(text(), "ferimento")]/following::td[1]/text()').extract() 
        item['listingDate'] = response.xpath('//div[@id="details"]/table//tr/td[contains(text(), "Data")]/following::td[1]/text()').extract()
        item['contract'] = response.xpath('//div[@id="details"]/table//tr/td[contains(text(), "Contratto:")]/following::td[1]/text()').extract()
        item['area'] =  response.xpath('//div[@id="details"]/table//tr/td[contains(text(), "Superficie:")]/following::td[1]/text()').extract()
        item['bathrooms'] = response.xpath('//div[@id="details"]/table//tr/td[contains(text(), "Bagni:")]/following::td[1]/text()').extract()
        item['gardenQ'] = response.xpath('//div[@id="details"]/table//tr/td[contains(text(), "Giardino:")]/following::td[1]/text()').extract()
        item['energyClass'] = response.xpath('//img[@class="imgClasseEnergetica"]/@alt').extract()
        item['description'] = response.xpath('//div[@class="descrizione"]/text()').extract()[0].replace("\n","").replace("\t","")
        item['address'] = [x.strip() for x in response.xpath('//div[contains(@class,"indirizzo_")]/text()').extract()]
        item['price'] =  cleanUnicodePrice.match(response.css('div.info_annuncio div.dettaglio_superficie strong::text').extract()[0]).groups()
        item['url'] = response.url
        yield item


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess

    process = CrawlerProcess()
    process.crawl(PVPSearchSpider)
    process.start()
