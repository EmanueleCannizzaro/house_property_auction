#import scrapy
from scrapy import Request, Spider
from scrapy_playwright.page import PageMethod

from property_scraper.playwright.items import QuoteItem


class QuotesJavascriptSpider(Spider):
    name = 'quotes_javascript'
    allowed_domains = ['quotes.toscrape.com']

    def start_requests(self):
        url = "https://quotes.toscrape.com/js/"
        self.metadata = {
            'playwright': True,
            'playwright_include_page': True, 
            'playwright_page_methods': [
                PageMethod('wait_for_selector', 'div.quote'),
            ],
            'errback': self.errback,
        }
        yield Request(url, meta=self.metadata)

    async def parse(self, response):
        page = response.meta["playwright_page"]
        screenshot = await page.screenshot(path="example.png", full_page=True)
        # screenshot contains the image's bytes
        await page.close()
        
        for quote in response.css('div.quote'):
            quote_item = QuoteItem()
            quote_item['text'] = quote.css('span.text::text').get()
            quote_item['author'] = quote.css('small.author::text').get()
            quote_item['tags'] = quote.css('div.tags a.tag::text').getall()
            yield quote_item
        
        next_page = response.css('.next>a ::attr(href)').get()

        if next_page is not None:
            next_page_url = 'http://quotes.toscrape.com' + next_page
            yield Request(next_page_url, meta=self.metadata)

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()


class ProxySpider(Spider):
    name = "proxy"
    custom_settings = {
        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "proxy": {
                "server": "http://myproxy.com:3128",
                "username": "user",
                "password": "pass",
            },
        }
    }

    def start_requests(self):
        yield Request("http://httpbin.org/get", meta={"playwright": True})

    def parse(self, response):
        print(response.text)


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.settings import Settings
    from scrapy.utils.log import configure_logging
    
    #logging.disable(logging.CRITICAL)
    configure_logging()
    
    # Load the settings file
    settings = Settings()
    settings_module_path = 'property_scraper.playwright.settings'
    # Replace with your actual settings module path
    settings.setmodule(settings_module_path)

    # Create a crawler process with the loaded settings
    process = CrawlerProcess(settings)

    # Add your spider(s) to the crawler process
    process.crawl(QuotesJavascriptSpider)

    # Start the crawler process    
    process.start()
