# -*- coding: utf-8 -*-
import scrapy
import time

from property_scraper.habitaclia.items import HabitacliaItem
from property_scraper.habitaclia.utils import clean_text, clean_tags, get_floor_plan, get_certificado_energetico, clean_img, clean_location


class HabitacliaSpider(scrapy.Spider):
    name = 'habitaclia'
    #https://english.habitaclia.com/
    #espanol


    def __init__(self, page_url='', url_file=None, *args, **kwargs):

        if not page_url and url_file is None:
            TypeError('No page URL or URL file passed.')

        if url_file is not None:
            with open(url_file, 'r') as f:
                self.start_urls = f.readlines()
        if page_url:
            self.start_urls = [page_url]

    def parse(self, response):
        if len(response.body) < 1000:
            item = HabitacliaItem()
            item['status'] = response.status
            yield item
            return
        for href in response.xpath(".//section[@class='list-items']//h3/a/@href").extract():
            url = response.urljoin(href)
            yield scrapy.Request(url=url, callback=self.parse_details)

        pg_href = response.xpath(".//li[@class='next']/a/@href").extract_first()
        if pg_href:
            pg_url = response.urljoin(pg_href)
            yield scrapy.Request(url=pg_url, callback=self.parse)

    def parse_details(self, response):
        item = HabitacliaItem()
        item['url'] = response.url
        item['title'] = clean_text(response.xpath("//h1/text()").extract_first())
        item['subtitle'] = clean_text(response.xpath("//h3[@id='js-detail-description-title']/text()").extract_first())
        item['location'] = clean_location(" ".join(response.xpath("//*[@class='address']/text()").extract()))
        item['extra_location'] = clean_text(response.xpath("normalize-space(//a[@id='js-ver-mapa-zona']/parent::h4)").extract_first())
        item['body'] = clean_text(";".join(response.xpath("//*[@class='detail-description']/text()").extract()))

        item['current_price'] = clean_text(response.xpath("translate(//div[@class='price']/span, ' €|.', '')").extract_first())
        item['original_price'] = item['current_price'] + clean_text(response.xpath("translate(//div[@class='price-down']/strong, '.|€', '')").extract_first())
        item['price_m2'] = clean_text(response.xpath("translate(//span[contains(., 'del anuncio')][not(contains(., 'Precio'))]/parent::div, ' €/m2€/m2 del anuncio|.', '')").extract_first())
        item['area_market_price'] = clean_text(response.xpath("translate(//span[contains(., 'distrito')]/parent::div, ' €/m2€/m2 distrito|.', '')").extract_first())
        item['square_meters'] = clean_text(response.xpath("normalize-space(//*[@id='js-feature-container']/ul/li[contains(.,' m')])").extract_first())

        item['area'] = clean_text(response.xpath("normalize-space(//*[@id='js-ver-mapa-zona'])").extract_first())
        item['tags'] = clean_tags("; ".join(response.xpath("//article[@class='has-aside']//li/text()").extract()))
        item['bedrooms'] = clean_text(response.xpath("normalize-space(//*[@id='js-feature-container']/ul/li[contains(.,' hab')])").extract_first())
        item['bathrooms'] = clean_text(response.xpath("normalize-space(//*[@id='js-feature-container']/ul/li[contains(.,' baños')])").extract_first())
        item['last_update'] = clean_text(response.xpath("//*[@id='js-translate']/p[2]/time/text()").extract_first())
        consumption = clean_text(response.xpath("normalize-space(//article[@class='has-aside']//div[@class='rating-box'][1])").extract_first())
        emissions = clean_text(response.xpath("normalize-space(//article[@class='has-aside']//div[@class='rating-box'][2])").extract_first())
        item['certification_status'] = True if consumption and emissions else False
        item['consumption'] = consumption
        item['emissions'] = emissions

        item['main_image_url'] = clean_text(response.xpath("//*[@id='js-gallery']/div[2]/div[1]/a/img/@src").extract_first())
        item['image_urls'] = clean_img("; ".join(response.xpath("//*[@id='js-gallery']/div[2]/div/a/img/@src").extract()))
        item['floor_plan'] = get_floor_plan(response.xpath("//*[@id='js-gallery']/div[2]/div/a/img/@src").extract())
        item['energy_certificate'] = get_certificado_energetico(response.xpath("//*[@id='js-gallery']/div[2]/div/a/img/@src").extract())
        item['video'] = clean_text(response.xpath("//*[@id='video-gallery-0']/iframe/@src").extract_first())

        item['seller_type'] = clean_text(response.xpath("//*[@id='js-contact-top']//span/text()").extract_first())
        item['agent'] = clean_text(response.xpath("//*[@id='js-contact-top']//span/text()").extract_first())
        item['ref_agent'] = ""
        item['source'] = ""
        item['ref_source'] = clean_text(response.xpath("translate(//h4[@class='subtitle'], 'Referencia del anuncio habitaclia/|:', '')").extract_first())
        item['phone_number'] = ""

        item['additional_url'] = ""
        item['published'] = ""
        item['scraped_ts'] = time.time()

        yield item
