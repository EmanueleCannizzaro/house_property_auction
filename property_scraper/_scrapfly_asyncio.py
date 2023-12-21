import asyncio

import logging as logger
from sys import stdout

scrapfly_logger = logger.getLogger('scrapfly')
scrapfly_logger.setLevel(logger.DEBUG)
logger.StreamHandler(stdout)

from scrapfly import ScrapeConfig, ScrapflyClient, ScrapeApiResponse

scrapfly = ScrapflyClient(key='scp-live-4458666b83d34af0834b936215c3c168', max_concurrency=2)

async def main():

    targets = [
        ScrapeConfig(url='http://httpbin.org/anything', render_js=True),
        ScrapeConfig(url='http://httpbin.org/anything', render_js=True),
        ScrapeConfig(url='http://httpbin.org/anything', render_js=True),
        ScrapeConfig(url='http://httpbin.org/anything', render_js=True),
        ScrapeConfig(url='http://httpbin.org/anything', render_js=True),
        ScrapeConfig(url='http://httpbin.org/anything', render_js=True),
        ScrapeConfig(url='http://httpbin.org/anything', render_js=True),
        ScrapeConfig(url='http://httpbin.org/anything', render_js=True)
    ]

    async for result in scrapfly.concurrent_scrape(scrape_configs=targets):
        print(result)

asyncio.run(main())
