import scrapy

from property_scraper.io import get_worksheet


class ZameenSpider(scrapy.Spider):
    name = "zameen"

    start_urls = [
        'https://www.zameen.com/Homes/Karachi-2-1.html',
        'https://www.zameen.com/Homes/Karachi-2-2.html'
    ]
    worksheet = get_worksheet('zameen')
    worksheet.clear()
    HEADERS = ['Text', 'Author', 'Tags']
    worksheet.append_row(HEADERS)

    def parse(self, response):
        prop = response.css("div._1d4d62ed")
        def func(req,ind):
            if len(req)==2:
                return req[ind]
            else:
                return "Not Specified"
        for p in prop:            
            data = {
                'price': p.css('span.f343d9ce::text').get(),
                'location':p.css('div._162e6469::text').get(),
                'bed': func(p.css('span._984949e5::text').getall(),0),
                'bath':func(p.css('span._984949e5::text').getall(),1),
                'size':p.css('span._984949e5 div div div span::text').get(),
            }            
            self.worksheet.append_row([str(data[key]).replace('“', '').replace('”', '') for key in data.keys()])
                        
            yield data
            
        next_page = response.css("a.b7880daf::attr(href)").getall()[-1]
        if next_page is not None:
            next_page = response.urljoin(next_page)
            # yield scrapy.Request(next_page, callback=self.parse)
            # shortcut
            yield response.follow(next_page, callback=self.parse)
            