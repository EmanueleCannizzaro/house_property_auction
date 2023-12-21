# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy_splash import SplashRequest

from tucasa.items import PropertyItem


class TucasaSpiderSpider(scrapy.Spider):
    name = 'tucasa_spider'

    def __init__(self, page_url='', url_file=None, *args, **kwargs):
        pages = 5
        self.start_urls = ['https://www.tucasa.com/compra-venta/''viviendas/barcelona/?r=&idz=0008&ord=&pgn={}'.format(i + 1) for i in range(pages)]

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
        # https://www.tucasa.com/redirectToPartner.asp?
        property_urls = list(set(response.css('a.menucolor::attr(href)').getall()))
        for property in property_urls:
            if re.search('redirectToPartner.asp?', property, re.I|re.DOTALL):
                continue
            # yield SplashRequest
            yield scrapy.Request(url=property, callback=self.crawl_property)

    def crawl_property(self, response):
        property = PropertyItem()

        # Resource
        property["resource_url"] = "https://www.tucasa.com/"
        property["resource_title"] = 'Tucasa'
        property["resource_country"] = 'ES'

        # Property
        property["active"] = 1
        property["url"] = response.url
        property["title"] = response.xpath('//h1//text()').re_first('\w.+\S')
        property["subtitle"] = self.get_subtitle(response)
        property["location"] = response.xpath('//*[(@id = "mapa-inmueble-tab")]//text()').re_first('piso\s+(.+)')
        property["extra_location"] = ''
        property["body"] = self.get_body(response)

        # Price
        property["current_price"] = response.xpath('//span[(@class = "precio")]/text()').re_first('\w.+\d')
        property["original_price"] = response.xpath('//span[(@class = "precio")]/text()').re_first('\w.+\d')
        property["price_m2"] = self.get_price_m2(response)
        property["area_market_price"] = ''
        property["square_meters"] = self.characteristics_list(response)[0]

        # Details
        property["area"] = response.xpath('//h1').re_first('en (.+) \(')
        property["tags"] = self.get_tags(response)
        property["bedrooms"] = self.characteristics_list(response)[1]
        property["bathrooms"] = self.characteristics_list(response)[2]
        property["last_update"] = response.xpath('//span[@class="actualizado"]/text()').re_first('\d+/\d+/\d+')
        property["certification_status"] = self.get_certification_status(response)
        property["consumption"] = self.get_certification_status(response)
        property["emissions"] = self.get_certification_status(response)

        # Multimedia
        property["main_image_url"] = response.css('.contenedor-img-detalle::attr(style)').re_first("url\(.+(http.+jpg).+\)")
        property["image_urls"] = self.get_img_urls(response)
        property["floor_plan"] = ''
        property["energy_certificate"] = ''
        property["video"] = ''

        # Agents
        property["seller_type"] = response.xpath('//span[(@class = "txt-tipo-vendedor")]/text()').get()
        property["agent"] = response.xpath('//span[(@class = "nombre-vendedor")]/text()').re_first('\w.+\S')
        property["ref_agent"] = ''
        property["source"] = 'tucasa.com'
        property["ref_source"] = self.get_ref_agent(response)
        property["phone_number"] = ''

        # Additional
        property["additional_url"] = ''
        property["published"] = ''
        property["scraped_ts"] = ''

        yield property

    def get_subtitle(self, response):
        subtitle_in_list = response.css('.informacion-detalle-inmueble::text').re('\w.+\S')
        return '2 '.join(subtitle_in_list) if subtitle_in_list else None

    def get_body(self, response):
        body_in_list = response.xpath('//span[(@class = "descripcion")]/text()').re('\w.+\S')
        return ' '.join(body_in_list) if body_in_list else None

    def get_price_m2(self, response):
        m2_xpath = '//li[(((count(preceding-sibling::*) + 1) = 7) and parent::*)]//strong/text()'
        price_m2 = response.xpath(m2_xpath).re_first('\w.+')
        return price_m2 if price_m2 else None

    def get_tags(self, response):
        tags_in_list = response.xpath('//span[(@class = "descripcion")]//text()').getall()
        if tags_in_list:
            return ';'.join(tags_in_list[1:])
        else:
            return None

    def characteristics_list(self, response):
        char_list = response.xpath(
            '//*[contains(concat( " ", @class, " " ), concat( " ", "caracteristicas-ul", " " ))]//li//text()'
        )
        return char_list.re('\n\t+(\S+)') if char_list else None

    def get_certification_status(self, response):
        certification_in_list = response.xpath('//div[@class="txt-certificado"]//text()').re('\w.+\S')
        if certification_in_list:
            return ' '.join(certification_in_list)
        else:
            return None

    def get_main_img(self, response):
        img_style_wrap = response.css('.contenedor-img-detalle::attr(style)').get()

    def get_img_urls(self, response):
        img_url_list = response.css('.visor-imagenes img::attr(src)').getall()
        return ';'.join(img_url_list) if img_url_list else None

    def get_ref_agent(self, response):
        property_data_xpath = '//*[contains(concat( " ", @class, " " ), concat( " ", "informacion-detalle-inmueble", " " ))]//text()'
        property_data_list = response.xpath(property_data_xpath).re('\w.+\S')
        if property_data_list:
            ref_agent_index = property_data_list.index('Referencia:') + 1
            return property_data_list[ref_agent_index]
        else:
            return None





