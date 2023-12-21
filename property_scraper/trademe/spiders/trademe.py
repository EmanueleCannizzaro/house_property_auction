from datetime import datetime
import json
import pandas as pd
from pprint import pprint
import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.http import FormRequest
from tqdm import tqdm

from property_scraper.io import get_worksheet


LISTING_TYPE = "CommercialSale" # One of CommercialSale, CommercialLease, Residential, Rental, NewHomes, Rural, Lifestyle, Retirement. Not case sensitive
# See https://developer.trademe.co.nz/api-reference/search-methods/commercial-sale-search for API documentation

class TrademeSpider(scrapy.Spider):
    name = "trademe"
    allowed_domains = ["trademe.co.nz"]
    base_url = f"https://api.trademe.co.nz/v1/search/property/{LISTING_TYPE}.json"
    worksheet = get_worksheet('trademe')
    worksheet.clear()
    HEADERS = ['Text', 'Author', 'Tags']
    worksheet.append_row(HEADERS)

    def start_requests(self):
        for page in range(1, 100):
            yield FormRequest(
                self.base_url,
                formdata = {
                    "page": str(page),
                    "rows": "500",
                },
                method = "GET",
                headers = {
                    "x-trademe-uniqueclientid": "f7e6fb2a-5629-aaee-34e2-9e17d7b2cfaa",
                    "Referer": "https://www.trademe.co.nz/",
                }
            )

    def parse_unix_timestamp(self, s):
        s = "".join(c for c in s if c.isnumeric())
        return datetime.fromtimestamp(int(s) / 1000)

    def parse(self, response):
        r = json.loads(response.text)
        if r["PageSize"] == 0:
            raise CloseSpider("finished")
        for listing in r["List"]:
            for k in ["StartDate", "EndDate", "AsAt", "NoteDate"]:
                listing[k] = self.parse_unix_timestamp(listing[k])
            self.worksheet.append_row([str(listing[key]).replace('“', '').replace('”', '') for key in listing.keys()])

            yield listing