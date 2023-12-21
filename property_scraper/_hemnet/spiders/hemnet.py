# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 21:45:50 2020

@author: Gwenn
"""

import scrapy

from property_scraper.io import get_worksheet


class HemnetSpider(scrapy.Spider):
    name="hemnet"
        
    start_urls=['https://www.hemnet.se/salda/bostader?item_types%5B%5D=bostadsratt&page='+ str(i) + '&sold_age=all' for i in range(1,51)]
    worksheet = get_worksheet('hemnet')
    worksheet.clear()
    HEADERS = [
        'address',
        'typ',
        'kommun',
        'staden',
        'rum',
        'avgift',
        'slutpris',
        'Pris Variation',
        'datum',
        'pris per sqm',
        'maklare'
    ]
    worksheet.append_row(HEADERS)

             
    def parse(self,response):        
        for annons in response.css('li.sold-results__normal-hit'):
            data = {
                'address': annons.css('.sold-property-listing__location span::text')[2].get(),
                'typ': annons.css('.sold-property-listing__location span::text')[3].get().strip(),
                'kommun': annons.css('.sold-property-listing__location span::text')[4].get().strip(),
                'staden': annons.css('.sold-property-listing__location div::text')[2].get().strip(),
                'rum': annons.css('.sold-property-listing__size div::text')[1].get().strip(),
                'avgift': annons.css('.sold-property-listing__size div::text')[3].get().strip(),
                'slutpris': annons.css('.sold-property-listing__price span::text').get().strip(),
                'Pris Variation': annons.css('.sold-property-listing__price-change::text').get(),
                'datum': annons.css('.sold-property-listing__price div::text')[3].get().strip(),
                'pris per sqm': annons.css('.sold-property-listing__price div::text')[5].get().strip(),
                'maklare': annons.css('.sold-property-listing__broker a::text').get()
            }
            self.worksheet.append_row([str(data[key]).replace('“', '').replace('”', '') for key in data.keys()])

            yield data
        
        