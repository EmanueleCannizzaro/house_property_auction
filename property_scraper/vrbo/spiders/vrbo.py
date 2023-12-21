from bs4 import BeautifulSoup
import json
import scrapy

from property_scraper.io import get_worksheet
from property_scraper.vrbo.items import VrbodataItem


class VrbospyderSpider(scrapy.Spider):
    name = 'vrbo'

    start_urls = [
        'https://www.vrbo.com/vacation-rentals/beach/usa/florida'
    ]
    worksheet = get_worksheet('vrbo')
    worksheet.clear()
    HEADERS = ['Text', 'Author', 'Tags']
    worksheet.append_row(HEADERS)

    def parse(self, response):
        # script = response.xpath('//script[2]').re_first('\((\[.*\])\)')
        property_items = VrbodataItem()
        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find_all('script')[25].text.strip()[29:-1] # remove 1st 29 char
        data = json.loads(script)

        #  data['abacus']['ha_gdpr_banner']['bucket']
        destinations = data['destination']['listings']
        for destination in destinations:
            name = destination['propertyName']
            price = str(destination['price']['value'])
            thumb = destination['thumbnailUrl']
            details = destination['toplineDescription']

            #print("Pipeline Details :" + details + "\nName:" + name +"\nThumb: "+ thumb)
            #print("\nPrice :" + price)

            property_items['property_name'] = name
            property_items['property_price'] = price
            property_items['property_thumb'] = thumb
            property_items['property_details'] = details

            self.worksheet.append_row([str(property_items[key]).replace('“', '').replace('”', '') for key in property_items.keys()])

            yield property_items
