# -*- coding: utf-8 -*-
from collections import defaultdict

import scrapy
from scrapy_splash import SplashRequest

from ..items import PropertyItem


class PisosSpiderSpider(scrapy.Spider):
    name = 'pisos_spider'

    def __init__(self, page_url='', url_file=None, *args, **kwargs):
        pages = 1
        self.start_urls = ['https://www.pisos.com/venta/pisos-barcelona/{}/'.format(i + 1) for i in range(pages)]

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
        script = """
                function main(splash)
                    local num_scrolls = 10
                    local scroll_delay = 1

                    local scroll_to = splash:jsfunc("window.scrollTo")
                    local get_body_height = splash:jsfunc(
                        "function() {return document.body.scrollHeight;}"
                    )
                    assert(splash:go(splash.args.url))
                    splash:wait(splash.args.wait)

                    for _ = 1, num_scrolls do
                        local height = get_body_height()
                        for i = 1, 10 do
                            scroll_to(0, height * i/10)
                            splash:wait(scroll_delay/10)
                        end
                    end        
                    return splash:html()
                end
            """
        property_urls = self.get_property_urls(response)
        for property in property_urls:
            yield SplashRequest(
                        url=property,
                        callback=self.crawl_property,
                        endpoint='execute',
                        args={'wait': 0.5, 'lua_source': script},  # 'timeout': 1800
                    )

    def crawl_property(self, response):
        property = PropertyItem()

        # Resource
        property["resource_url"] = "https://www.pisos.com/"
        property["resource_title"] = 'Pisos'
        property["resource_country"] = 'ES'

        # Property
        property["active"] = 1
        property["url"] = response.url
        property["title"] = response.xpath('//h1/text()').get()
        property["subtitle"] = response.xpath('//h3[@class="title"]/text()').re_first('\w.+\S')
        property["location"] = response.css('.subtitle::text').re_first('\w.+\S')
        property["extra_location"] = ''
        property["body"] = self.get_body(response)

        # Price
        property["current_price"] = response.xpath('//*[(@class = "h1 jsPrecioH1")]//text()').re_first('(.+) €')
        property["original_price"] = response.xpath('//*[(@class = "h1 jsPrecioH1")]//text()').re_first('(.+) €')
        property["price_m2"] = response.xpath('//*[(@class="basicdata-item")]//text()').re_first('(.+)  €')
        property["area_market_price"] = ''
        property["square_meters"] = response.xpath('//*[(@class="basicdata-item")]//text()').re_first('(.+) m²')

        # Details
        property["area"] = self.get_area(response)
        property["tags"] = self.get_tags(response)
        property["bedrooms"] = response.xpath('//*[(@class="basicdata-item")]//text()').re_first('(\w+) habs')
        property["bathrooms"] = response.xpath('//*[(@class="basicdata-item")]//text()').re_first('(\w+) baño')
        property["last_update"] = response.xpath('//*[(@class="updated-date")]//text()').re_first('\d+/\d+/\d+')
        property["certification_status"] = ''
        property["consumption"] = ''
        property["emissions"] = response.css('.sel::text').re_first('\w+')

        # Multimedia
        property["main_image_url"] = response.xpath('//*[@id="mainPhotoPrint"]//@src').get()
        property["image_urls"] = self.get_img_urls(response)
        property["floor_plan"] = ''
        property["energy_certificate"] = ''
        property["video"] = ''

        # Agents
        property["seller_type"] = response.css('.owner-data-info a::attr(title)').get()
        property["agent"] = response.css('.owner-data-info a::text').get()
        property["ref_agent"] = ''
        property["source"] = 'pisos.com'
        property["ref_source"] = response.css('script::text').re_first('var referencia = \'(.+)\';')
        property["phone_number"] = response.css('.number.one::text').get()

        # Additional
        property["additional_url"] = ''
        property["published"] = ''
        property["scraped_ts"] = ''

        yield property

    def get_property_urls(self, response):
        relative_url_list = response.css('.information a.anuncioLink::attr(href)').getall()
        base_url = 'https://www.pisos.com'
        url_join = lambda rel_url: base_url + rel_url
        return list(map(url_join, relative_url_list))

    def get_area(self, response):
        area = response.xpath('//h2[(@class="position")]//text()').re_first('(.+) \(')
        if not area:
            area = response.xpath('//h2[(@class="position")]//text()').get()
        return area

    def get_img_urls(self, response):
        img_url_list = response.css('.gallery-carousel-item img::attr(src)').getall()
        return ';'.join(img_url_list) if img_url_list else None

    def get_body(self, response):
        body_in_list = response.xpath('//*[(@id = "descriptionBody")]//text()').re('\w.+\S')
        return '\n'.join(body_in_list) if body_in_list else None

    def get_property_details(self, response):
        property_detail_list = response.xpath('//*[(@class="basicdata-item")]//text()').getall()
        return property_detail_list

    def get_tags(self, response):
        tags_list = []
        basic_data_container = response.css('.more-padding span::text').getall()
        outdoor_container = response.css('.charblock-list .element-with-bullet span::text').getall()
        for index, item in enumerate(basic_data_container):
            # append combined consecutive item in the list.
            if index % 2 == 0:
                continue

            tag = basic_data_container[index - 1] + item
            tags_list.append(tag)

        for tag in outdoor_container:
            tags_list.append(tag)

        return ';'.join(tags_list)



