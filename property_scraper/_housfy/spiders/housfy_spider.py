# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import yaml

from housfy.items import PropertyItem


class HousfySpiderSpider(scrapy.Spider):
    name = 'housfy_spider'

    def __init__(self, page_url='', url_file=None, *args, **kwargs):
        pages = 5
        self.start_urls = ['https://housfy.com/venta-inmuebles/barcelona/barcelona/?page={}'.format(i + 1) for i in range(pages)]

        if not page_url and url_file is None:
            TypeError('No page URL or URL file passed.')

        if url_file is not None:
            with open(url_file, 'r') as f:
                self.start_urls = f.readlines()
        if page_url:
            # Replaces the list of URLs if url_file is also provided
            self.start_urls = [page_url]

        super().__init__(*args, **kwargs)

    def start_requests(self):
        for page in self.start_urls:
            yield scrapy.Request(url=page, callback=self.crawl_page)

    def crawl_page(self, response):
        property_urls = list(set(response.css('.property-card a::attr(href)').getall()))
        for property in property_urls:
            yield scrapy.Request(url=property, callback=self.crawl_property)

    def crawl_property(self, response):
        property = PropertyItem()

        # Resource
        property["resource_url"] = 'https://housfy.com/'
        property["resource_title"] = 'Housfy'
        property["resource_country"] = 'ES'

        # Property
        property["active"] = 1
        property["url"] = response.url
        property["title"] = response.css('.propertyDetail__address::text').get()
        property["subtitle"] = ''
        location = response.xpath('.//*[@class="propertyDetail__exactLocationContent"]/p/text()').extract()
        property["location"] = ';'.join(location)
        property["extra_location"] = ''
        body = response.xpath('.//*[@class="collapseText__content propertyDetail__descriptionContent"]/text()').get()
        property["body"] = body.strip().replace('\n', ';').replace('\r', '').replace(';;', ';')

        # Price
        property["current_price"] = response.xpath('.//*[@class="propertyDetail__mainData__price"]/strong/text()').get()
        property["original_price"] = response.xpath('.//*[@class="propertyDetail__mainData__price"]/strong/text()').get()
        property["price_m2"] = response.xpath('.//*[@class="propertyDetail__mainData__price"]/text()').get()
        property["area_market_price"] = ''
        square_meters = response.xpath('.//*[@class="propertyDetail__feature propertyDetail__feature--enabled"]/span/text()').extract_first()
        property["square_meters"] = square_meters.split()[0]

        # Details
        details = response.xpath('.//*[@class="propertyDetail__feature propertyDetail__feature--enabled"]/span/text()').extract()
        area = response.xpath('.//*[@class="propertyDetail__boxedSection propertyDetail__spacedBetween"]/a/text()').get()
        index = area.index('en') + 3
        property["area"] = area[index::]
        property["tags"] = ';'.join(details)
        property["bedrooms"] = details[1].split()[0]
        property["bathrooms"] = details[2].split()[0]
        property["last_update"] = ''
        certification_status = response.xpath('.//*[@class="propertyDetail__specsContainer"]/div[6]/span/text()').extract()
        property["certification_status"] = ';'.join(certification_status)
        property["consumption"] = ''
        property["emissions"] = ''

        # Multimedia
        images_array = self.prepare_images(response)
        property["main_image_url"] = self.get_main_photo(images_array)
        property["image_urls"] = ';'.join(self.get_photos(images_array))
        property["floor_plan"] = ''
        property["energy_certificate"] = ''
        property["video"] = ''

        # Agents
        property["seller_type"] = response.xpath('.//*[@class="propertyDetail__ownerName"]/span/text()').get()
        property["agent"] = ''
        property["ref_agent"] = ''
        property["source"] = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "hide-sticky-mobile", " " ))]/@src').get()
        property["ref_source"] = ''
        property["phone_number"] = ''

        # Additional
        property["additional_url"] = ''
        property["published"] = ''
        property["scraped_ts"] = ''

        yield property

    def prepare_images(self, response):
        images_container = response.css('.propertyDetail > property-images').extract_first()
        property_images = BeautifulSoup(images_container, "xml")
        images_array = property_images.contents[0].attrs[":images-array"]
        return yaml.load(images_array, Loader=yaml.FullLoader)

    def get_main_photo(self, property_images):
        for image in property_images:
            if image["isMain"]:
                return image["url"]

    def get_photos(self, property_images):
        photos = []
        for image in property_images:
            if not image["isMain"]:
                photos.append(image["url"])
        return photos
