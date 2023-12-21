import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver import Chrome, ChromeOptions
from time import sleep

from property_scraper import DRIVER_PATH

class AstegiudiziarieSpider(scrapy.Spider):
    name = "astegiudiziarie"
    allowed_domains = ["www.astegiudiziarie.it"]
    start_urls = ["https://www.astegiudiziarie.it/aste-giudiziarie/immobili/"]

    def __init__(self):
        options = ChromeOptions()
        self.driver = Chrome(service=webdriver.chrome.service.Service(DRIVER_PATH), options=options)
         

    def parse(self, response):
        self.driver.get(response.url)
        sleep(10)
        
        sel = HtmlResponse(url=response.url, body=self.driver.page_source, encoding='utf-8')

        listings = sel.xpath('//div[@class="single_box_asta"]')
        for listing in listings:
            l = ItemLoader(item=AstegiudiziarieItem(), selector=listing)
            l.default_output_processor = TakeFirst()

            l.add_xpath('title', './/h4[@class="box_title"]/text()')
            l.add_xpath('location', './/div[@class="box_dettagli"]/p[1]/span/text()')
            l.add_xpath('price', './/div[@class="box_dettagli"]/p[2]/span/text()')
            l.add_xpath('description', './/div[@class="box_dettagli"]/p[3]/text()')

            yield l.load_item()

    def closed(self, reason):
        self.driver.quit()

class AstegiudiziarieItem(scrapy.Item):
    title = scrapy.Field()
    location = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()

def main():
    process = CrawlerProcess()
    process.crawl(AstegiudiziarieSpider)
    process.start()

if __name__ == "__main__":
    main()
