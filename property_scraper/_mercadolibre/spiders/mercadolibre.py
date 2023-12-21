import scrapy

class MercadoLibrePropertiesSpider(scrapy.Spider):
    name = "properties"

    start_urls = ["https://inmuebles.mercadolibre.com.ar/venta/capital-federal/almagro/"]

    def parse(self, response):
        for property_page in response.css("a.item__info-link ::attr(href)").extract():
            yield response.follow(property_page, callback=self.parse_property)
        page_next = response.css(".pagination__next > a::attr(href)").extract_first()
        if page_next is not None:
            yield response.follow(page_next, callback=self.parse)
            
    def parse_property(self, response):
        attr_keys = response.css("span.attribute-key::text").extract()
        attr_values = response.css("span.attribute-value::text").extract()
        data = {
            "price": response.css(".vip-price strong::text").extract_first(),
            "address": response.css("h2.map-location::text").extract_first(),
            "url": response.url
        }
        for i in range(0, len(attr_keys)):
            data[attr_keys[i].replace(":","")] = attr_values[i]
        yield data