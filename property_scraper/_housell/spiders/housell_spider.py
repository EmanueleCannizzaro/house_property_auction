# -*- coding: utf-8 -*-
import scrapy

from ..items import PropertyItem


class HousellSpiderSpider(scrapy.Spider):
    name = 'housell_spider'

    def __init__(self, page_url='', url_file=None, *args, **kwargs):
        pages = 5
        self.start_urls = ['https://www.housell.com/pisos-en-venta/?p={}&o=relevance_desc'.format(i) for i in range(pages)]

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
        property_urls = response.css('a.c-item-house__link::attr(href)').getall()
        for property in property_urls:
            yield scrapy.Request(url=property, callback=self.crawl_property)

    def crawl_property(self, response):
        property = PropertyItem()

        # Resource
        property["resource_url"] = "https://www.tucasa.com/"
        property["resource_title"] = 'Housell'
        property["resource_country"] = 'ES'

        # Property
        property["active"] = 1
        property["url"] = response.url
        property["title"] = response.xpath('//h1/text()').get()
        property["subtitle"] = ''
        property["location"] = response.xpath('//h1/text()').re_first('(\d{5} .+) \(')
        property["extra_location"] = response.xpath('//h1/text()').re_first('venta en (.+) \d')
        property["body"] = self.get_body(response)

        # Price
        property["current_price"] = response.xpath('//*[@class="c-mod-property-details__header-price"]/text()').re_first("(.+)€")
        property["original_price"] = ''
        property["price_m2"] = response.xpath('//*[@class="c-mod-property-details__bar-chart-price"]/text()').re_first("(.+) €")
        property["area_market_price"] = ''
        property["square_meters"] = response.xpath('//*[@class="c-mod-property-details__header-features-item"]/text()').re_first("(.+) m2")

        # Details
        property["area"] = response.xpath('//*[@class="c-mod-property-details__details-address"]/text()').re_first("- (.+)\s$")
        property["tags"] = self.get_tags(response)
        property["bedrooms"] = response.xpath('//*[@class="c-mod-property-details__header-features-item"]/text()').re_first("(.+) hab")
        property["bathrooms"] = ''
        property["last_update"] = ''
        property["certification_status"] = '\n'.join(self.get_certification_status(response))
        property["consumption"] = self.get_certification_status(response)[2]
        property["emissions"] = self.get_certification_status(response)[4]

        # Multimedia
        property["main_image_url"] = response.xpath('//*[@class="c-mod-property-details__gallery-big '
                                                    'js-mod-property-details__open-gallery"]//@href').get()
        property["image_urls"] = self.get_image_urls(response)
        property["floor_plan"] = self.get_floor_plan(response)
        property["energy_certificate"] = ''
        property["video"] = ''

        # Agents
        property["seller_type"] = ''
        property["agent"] = ''
        property["ref_agent"] = ''
        property["source"] = 'Housell'
        property["ref_source"] = response.xpath('//span[@class="c-mod-property-details__details-reference"]/text()').get()
        property["phone_number"] = ''

        # Additional
        property["additional_url"] = self.get_additional_data(response)
        property["published"] = ''
        property["scraped_ts"] = ''

        yield property

    def get_body(self, response):
        body_in_list = response.css('.js-mod-property-details__details-text-i::text').getall()
        return '\n'.join(body_in_list) if body_in_list else None

    def get_tags(self, response):
        tags_in_list = response.xpath('//*[@class="c-mod-property-details__details-list-item"]/text()').getall()
        return ';'.join(tags_in_list[:13]) if tags_in_list else None

    def get_certification_status(self, response):
        cert_status_in_list = response.xpath('//*[@class="c-mod-property-details__cee"]//text()').re('\w.+\S')
        return cert_status_in_list if cert_status_in_list else None

    def get_image_urls(self, response):
        image_url_in_list = response.xpath('//*[@class="c-mod-property-details__gallery-small"]//@href').getall()
        return ';'.join(image_url_in_list) if image_url_in_list else None

    def get_floor_plan(self, response):
        floor_plan_in_list = response.xpath('//*[@class="c-mod-property-details__plans-images"]//@data-src').getall()
        return ';'.join(floor_plan_in_list) if floor_plan_in_list else None

    def get_additional_data(self, response):
        additional_data_in_list = response.xpath('//*[@class="c-mod-property-details__zone-price-detail"]//text()').getall()
        return ' '.join(additional_data_in_list) if additional_data_in_list else None
