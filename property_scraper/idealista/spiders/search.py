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
class IdealistaSearchSpider(SeleniumSearchSpider):
    name = 'idealista'
    allowed_domains = [
        'www.idealista.com',
		'www.idealista.it',
        'idealista.com'
    ]
    start_urls = [
        'https://www.idealista.it/vendita-case/ravenna-ravenna/con-aste_giudiziarie/',
        #'https://www.idealista.com/venta-viviendas/leganes/el-carrascal/',
        #'https://www.idealista.com/alquiler-viviendas/madrid/zona-norte/',
        #'https://www.idealista.com/venta-viviendas/madrid/carabanchel/',
		#'https://www.idealista.com/venta-viviendas/madrid/carabanchel/'
    ]

    rules = (
        # Filter all the flats paginated by the website following the pattern indicated
        Rule(LinkExtractor(restrict_xpaths=("//a[@class='icon-arrow-right-after']")),
             callback='parse_flats',
			 follow=True)
    )
    
    '''
    worksheet = get_worksheet('immobiliare')
    worksheet.clear()
    HEADERS = ['Text', 'Author', 'Tags']
    worksheet.append_row(HEADERS)
    '''
    # Necessary in order to create the whole link towards the website
    URL_ROOTNAME = 'http://idealista.it'
    URL = 'https://www.idealista.it/vendita-case/ravenna-ravenna/con-aste_giudiziarie/'
    LOGIN_URL = ''
    NEXT_PAGE_URL = 'https://www.idealista.it/vendita-case/ravenna-ravenna/con-aste_giudiziarie/lista-{}.htm'
    WEBSITE = 'idealista'
    LOGIN_XPATH = {
        #'advertisement': '//button[@class="remodal-close"]',
        'cookie' : '//button[@class="didomi-components-button didomi-button didomi-disagree-button didomi-components-button--color didomi-button-highlight highlight-button"]/span[contains(text(), "Accetta solo necessari")]',
        #'email' : '//input[@name="username"]',
        #'password' : '//input[@name="password"]',
        #'login' : '//button[@class="form-btn submit-button"][contains(text(), "Login")]'
    }
    SEARCH_XPATH = {
        #'url' : '//div[@class="gx-motore-ricerca-submit"][contains(text(), "Cerca")]',
        'number_of_results' : '//div[@class="listing-title h1-simulated"]/h1[@id="h1-container"][contains(text(), " aste giudiziarie: ")]',
        'number_of_results_per_page' : '//article[@class="item  item_contains_branding extended-item item-multimedia-container"]',
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


    def parse_flats(self, response):
        info_flats_xpath = response.xpath("//*[@class='item-info-container']")
        prices_flats_xpath = response.xpath("//*[@class='row price-row clearfix']/span[@class='item-price h2-simulated']/text()")
        discounts_xpath = response.xpath("//*[@class='row price-row clearfix']")

        links = [str(''.join(self.URL_ROOTNAME + link.xpath('a/@href').extract().pop()))
                 for link in info_flats_xpath]

        prices = [float(flat.extract().replace('.','').strip())
                 for flat in prices_flats_xpath]
                 
        discounts = [0 if len(discount.xpath("./*[@class='item-price-down icon-pricedown']/text()").extract()) < 1
                     else discount.xpath("./*[@class='item-price-down icon-pricedown']/text()").extract().pop().replace('.','').strip().split(' ').pop(0) 
                     for discount in discounts_xpath]
        
        addresses = [address.xpath('a/@title').extract().pop().encode('iso-8859-1')
		     for address in info_flats_xpath]
                     
        rooms = [int(flat.xpath('span[@class="item-detail"]/small[contains(text(),"hab.")]/../text()').extract().pop().strip()) 
                 if len(flat.xpath('span[@class="item-detail"]/small[contains(text(),"hab.")]')) == 1 
                 else None 
                 for flat in info_flats_xpath]
                 
        sqfts_m2 = [float(flat.xpath('span[@class="item-detail"]/small[starts-with(text(),"m")]/../text()').extract().pop().replace('.','').strip())
                    if len(flat.xpath('span[@class="item-detail"]/small[starts-with(text(),"m")]')) == 1 
                    else None 
                    for flat in info_flats_xpath]
                    
        floors_elevator = [flat.xpath('string(span[@class="item-detail"][last()])').extract().pop().strip()
                           for flat in info_flats_xpath]
                           
        for flat in zip(links, prices, addresses, discounts, sqfts_m2, rooms, floors_elevator):
            item = IdealistaItem(date=datetime.now().strftime('%Y-%m-%d'),
				 link=flat[0], price=flat[1], address=flat[2], discount=flat[3], 
                                 sqft_m2=flat[4], rooms=flat[5], floor_elevator = flat[6])
            yield item

    #Overriding parse_start_url to get the first page
    parse_start_url = parse_flats


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess

    process = CrawlerProcess()
    process.crawl(PVPSearchSpider)
    process.start()
