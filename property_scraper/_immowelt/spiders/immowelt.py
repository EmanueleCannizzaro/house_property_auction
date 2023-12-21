import scrapy


class PropertyScraperSpider(scrapy.Spider):
    name = "property_scraper"
    allowed_domains = ["www.immowelt.at"]
    start_urls = ["http://www.immowelt.at/"]

    def parse(self, response):
        pass
