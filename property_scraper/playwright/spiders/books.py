
import asyncio
import hashlib
import logging
from pathlib import Path
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_async
from scrapy import FormRequest, Request, Spider
from scrapy.http.response import Response
from scrapy_playwright.page import PageMethod
from typing import Generator, Optional


class PlaywrightSpider(Spider):

    """Extract all items and save screenshots."""

    name = "playwright_spider"
    custom_settings = {
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "DOWNLOAD_HANDLERS": {
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "http" : "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        #"CONCURRENT_REQUESTS": 32,
        "CONCURRENT_REQUESTS": 2,
        "PLAYWRIGHT_MAX_PAGES_PER_CONTEXT": 4,
        "CLOSESPIDER_ITEMCOUNT": 100,
        "FEEDS": {
            "items.json": {
                "format": "json", 
                "encoding": "utf-8", 
                "indent": 4
            },
        },
    }
    start_urls = ["http://books.toscrape.com"]

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        logging.getLogger("scrapy.core.engine").setLevel(logging.WARNING)
        logging.getLogger("scrapy.core.scraper").setLevel(logging.WARNING)

    def start_requests(self):
        async def main():
            with sync_playwright() as p:
                #for browser_type in [p.chromium, p.firefox, p.webkit]:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto('http://whatsmyuseragent.org/')
                page.screenshot(path='chrome_headless_playwright.png', fullPage=True)
                browser.close()


        async def main():
            async with async_playwright() as p:
                #for browser_type in [p.chromium, p.firefox, p.webkit]:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await stealth_async(page)
                await page.goto('http://whatsmyuseragent.org/')
                await page.screenshot(path='chrome_headless_stealth.png', fullPage=True)
                await browser.close()

        asyncio.run(main())

        
        
        # GET request
        yield Request("https://httpbin.org/get", meta={"playwright": True})
        # POST request
        yield FormRequest(
            url="https://httpbin.org/post",
            formdata={"foo": "bar"},
            meta={"playwright": True},
        )

    def parse(self, response:Response, current_page:Optional[int]=None) -> Generator:
        # 'response' contains the page as seen by the browser
        page_count = response.css(".pager .current::text").re_first(r"Page \d+ of (\d+)")
        page_count = int(page_count)
        for page in range(2, page_count + 1):
            yield response.follow(f"/catalogue/page-{page}.html", cb_kwargs={"current_page": page})

        current_page = current_page or 1
        for book in response.css("article.product_pod a"):
            yield response.follow(
                book,
                callback=self.parse_book,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_context": f"page-{current_page}",
                },
            )

    async def parse_book(self, response: Response) -> dict:
        url_sha256 = hashlib.sha256(response.url.encode("utf-8")).hexdigest()
        page = response.meta["playwright_page"]
        await page.screenshot(
            path=Path(__file__).parent / "books" / f"{url_sha256}.png", full_page=True
        )
        await page.close()
        return {
            "url": response.url,
            "title": response.css("h1::text").get(),
            "price": response.css("p.price_color::text").get(),
            "breadcrumbs": response.css(".breadcrumb a::text").getall(),
            "image": f"books/{url_sha256}.png",
        }
    

class ClickAndSavePdfSpider(Spider):
    name = "pdf"

    def start_requests(self):
        yield Request(
            url="https://example.org",
            meta=dict(
                playwright=True,
                playwright_page_methods={
                    "click": PageMethod("click", selector="a"),
                    "pdf": PageMethod("pdf", path="/tmp/file.pdf"),
                },
            ),
        )

    def parse(self, response):
        pdf_bytes = response.meta["playwright_page_methods"]["pdf"].result
        with open("iana.pdf", "wb") as fp:
            fp.write(pdf_bytes)
        yield {"url": response.url}  # response.url is "https://www.iana.org/domains/reserved"


class ScrollSpider(Spider):
    """Scroll down on an infinite-scroll page."""

    name = "scroll"
    custom_settings = {
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "DOWNLOAD_HANDLERS": {
            # "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "LOG_LEVEL": "INFO",
    }

    def start_requests(self):
        yield Request(
            url="http://quotes.toscrape.com/scroll",
            cookies={"foo": "bar", "asdf": "qwerty"},
            meta={
                "playwright": True,
                #"playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "div.quote"),
                    PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
                    PageMethod("wait_for_selector", "div.quote:nth-child(11)"),  # 10 per page
                    PageMethod(
                        "screenshot", path=Path(__file__).parent / "scroll.png", full_page=True
                    ),
                ],
            },
        )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.screenshot(path="quotes.png", full_page=True)
        await page.close()
        return {"url": response.url, "count": len(response.css("div.quote"))}
    