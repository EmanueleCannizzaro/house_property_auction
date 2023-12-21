# -*- coding: utf-8 -*-
import scrapy
import logging

from scrapy_splash import SplashRequest

from ..items import PropertyItem


class PisocasasSpiderSpider(scrapy.Spider):
    name = 'pisocasas_spider'

    def __init__(self, page_url='', url_file=None, *args, **kwargs):
        pages = 5
        self.start_urls = ['http://www.pisocasas.com/busca.php?pagina={}&o=Venta&t=%&pr=&po=%&md=0&mh=100000&pd=0&ph'
                           '=100000000&do=0&ba=0&pi=&tr=&ga=&as=&ai=&te=&ja=&or=&bz='.format(i + 1) for i in range(pages)]

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
            yield SplashRequest(
                url=page,
                callback=self.crawl_page,
                endpoint='render.html',
                args={'wait': 0.5, 'viewport': '1024x2480', 'timeout': 90, 'images': 0, 'resource_timeout': 90},
            )

    def crawl_page(self, response):
        # logging.info("Getting property urls from {}".format(response.url))
        property_urls = list(set(response.css('a.menucolor::attr(href)').getall()))
        for property in property_urls:
            yield scrapy.Request(url=property, callback=self.crawl_property)

    def crawl_property(self, response):
        logging.info("Crawling page: {}".format(response.url))
        property = PropertyItem()

        # Resource
        property["resource_url"] = "https://www.pisocasas.com/"
        property["resource_title"] = 'Pisocasas'
        property["resource_country"] = 'ES'

        # Property
        property["active"] = 1
        property["url"] = response.url
        property["title"] = response.xpath('//h1/text()').get()
        property["subtitle"] = ''
        property["location"] = response.xpath('//h1/text()').re_first('en (.+,.+) Id')
        property["extra_location"] = ''
        property["body"] = "\n".join(response.xpath('//*[@id="caracteristica_datos_adicionales"]//text()').re('\w.+'))

        # Price
        property["current_price"] = response.xpath('//*[@class="fuente_grande"]//text()').get()[:-1]
        property["original_price"] = ''
        property["price_m2"] = ''
        property["area_market_price"] = ''
        property["square_meters"] = response.xpath('//*[@class="datos_destacados_p"]//text()').getall()[1]

        # Details
        property["area"] = self.get_area(response)
        property["tags"] = ''
        property["bedrooms"] = response.xpath('//*[@class="caracteristica"]/span/text()').getall()[0]
        property["bathrooms"] = response.xpath('//*[@class="caracteristica"]/span/text()').getall()[1]
        property["last_update"] = ''
        property["certification_status"] = self.get_certification_status(response)
        property["consumption"] = ''
        property["emissions"] = ''

        # Multimedia
        property["main_image_url"] = response.css('#contenedor_imagen_principal a::attr(href)').get()
        property["image_urls"] = self.get_img_urls(response)
        property["floor_plan"] = ''
        property["energy_certificate"] = ''
        property["video"] = ''

        # Agents
        property["seller_type"] = ''
        property["agent"] = response.xpath('//*[@id="datos_anunciante"]/p[@style="font-size: 18px;"]/text()').get()
        property["ref_agent"] = response.xpath('//*[@id="datos_anunciante"]/p/text()').re_first('Referencia : (.+)')
        property["source"] = 'pisocasas.com'
        property["ref_source"] = ''
        property["phone_number"] = ''

        # Additional
        property["additional_url"] = ''
        property["published"] = ''
        property["scraped_ts"] = ''

        yield property

    def get_img_urls(self, response):
        img_url_list = response.css('#contenedor_imagen_principal a::attr(href)').getall()
        return ';'.join(img_url_list[1:]) if img_url_list else None

    def get_area(self, response):
        raw_area = response.xpath('//*[@class="texto_zona"]//text()').re_first('\w.+')
        return raw_area.strip() if raw_area else None

    def get_certification_status(self, response):
        characteristics_container = response.xpath('//*[@class="caracteristica"]/span/text()').getall()
        raw_cert_status = characteristics_container[2]
        return raw_cert_status.strip() if raw_cert_status else None

