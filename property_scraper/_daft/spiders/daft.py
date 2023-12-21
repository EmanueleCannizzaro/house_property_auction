# -*- coding: utf-8 -*-
import scrapy
from scrapy.shell import inspect_response
from scrapy_splash import SplashRequest

from property_scraper.io import get_worksheet


class DaftSpider(scrapy.Spider):
    name = 'daft'
    #allowed_domains = ['daft.ie']
    start_urls = [
        'https://www.daft.ie/ireland/commercial-property/?ad_type=commercial&advanced=1&searchSource=commercial'
	]
    worksheet = get_worksheet('daft')
    worksheet.clear()
    worksheet.append_row(['rent_price', 'location','size', 'how_many_times_views'])

    def start_requests(self):
        yield SplashRequest(
            self.start_urls[0],
            callback=self.scrap_search_result_page,
            args={
                'wait': 1})

    def scrap_search_result_page(self, response):
        links = response.xpath("//div[@class='box']//span[@class='sr_counter']/following-sibling::a/@href").extract()
        print(len(links))
        for link in links:
            yield SplashRequest(
                'https://www.daft.ie' + link,  # It is a relative url so we will concat them
                callback=self.parse,  # Set the callback to parse as this will parse the specific commerial let
                args={
                    'wait': 0.5}) # give splash time to render can be lowered

    def parse(self, response):
        print(response.url)
        rent_price = response.xpath('//div[@id="smi-price-string"]//text()').get()
        #location = response.xpath('//div[@id="address_box"]//h1/text()').get()
        location = response.xpath('//div[@id="search_result_title_box"]//h2/a/text()').get() #does not work
        size = response.xpath('//div[@id="address_box"]//span[contains(text(),"feet")]//text()').get()
        how_many_times_views = response.xpath(
            '//div[@class="description_extras"]//h3[contains(text(),"Property Views:")]/following-sibling::text()[1]').get()

        data = {
            'rent_price': rent_price,
            'location': location,
            'size': size,
            'how_many_times_views': how_many_times_views
        }
        #self.worksheet.append_row([str(data[key]).replace('“', '').replace('”', '') for key in data.keys()])
        
        yield l.load_item()

        '''
        paste link to start url
        override the default start_request method
        create a method to extract the links
        return a splashRequest with a 5 seco wait to allow the js to render and point to parse this
        '''