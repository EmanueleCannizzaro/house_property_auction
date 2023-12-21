import scrapy


class Pvp2Spider(scrapy.Spider):
    name = 'pvp2'
    allowed_domains = ['www.immobiliallasta.it']
    start_urls = ['https://www.immobiliallasta.it/']

    def parse(self, response):
        pass
