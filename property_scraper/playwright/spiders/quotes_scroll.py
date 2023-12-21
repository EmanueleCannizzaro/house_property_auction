#import asyncio
#import scrapy
from scrapy import Request, Spider
#from scrapy.utils.response import open_in_browser
from scrapy_playwright.page import PageMethod
from scrapy.selector import Selector

from property_scraper.playwright.items import QuoteItem


class QuotesScrollSpider(Spider):
    name = 'quotes_scroll'

    def start_requests(self):
        url="http://quotes.toscrape.com/scroll"
        self.metadata = {
            'playwright': True,
            'playwright_include_page': True, 
            'playwright_page_methods': [
                PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
                PageMethod("wait_for_selector", "div.quote:nth-child(11)"),
            ],
            'errback': self.errback,
        }
        yield Request(url, meta=self.metadata)

    async def parse(self, response):
        page = response.meta['playwright_page']
        selector  = Selector(text=await page.content())
        screenshot = await page.screenshot(path="example.png", full_page=True)
        # screenshot contains the image's bytes
        
        '''
        for i in range(2, 11):  # 2 to 10
            await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            quotes_count = 10*i
            await page.wait_for_selector(f'.quote:nth-child({quotes_count})')
            # sleep for 1 second
            await asyncio.sleep(5)
        '''
        await page.close()
        
        for quote in response.css('div.quote'):
            quote_item = QuoteItem()
            quote_item['text'] = quote.css('span.text::text').get()
            quote_item['author'] = quote.css('small.author::text').get()
            quote_item['tags'] = quote.css('div.tags a.tag::text').getall()
            yield quote_item

        '''
        for q in selector.css('.quote'):
            yield {
                'author': q.css('.author ::text').get(),
                'quote': q.css('.text ::text').get()
            }
        '''

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()


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
    process.crawl(QuotesScrollSpider)

    # Start the crawler process    
    process.start()
