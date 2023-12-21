import scrapy
from scrapy.loader import ItemLoader
f#from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from property_scraper import DRIVER_PATH, LOCALHOST_URL_ROOTNAME, ROOT_FOLDER, get_filename_from_identifier, get_unique_filename


class RightmoveSpider(scrapy.Spider):
    name = "rightmove_search"
    allowed_domains = ["rightmove.co.uk"]
    start_urls = ["https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E94617"]
    login_url = "https://www.rightmove.co.uk/login"

    def __init__(self):
        self.driver = webdriver.Chrome("/path/to/chromedriver")
        options = ChromeOptions()
        driver = Chrome(service=webdriver.chrome.service.Service(DRIVER_PATH), options=options)
                

    def parse(self, response):
        self.driver.get(self.login_url)

        # wait for the login page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "loginEmailAddress"))
        )

        # enter login credentials and submit
        email_input = self.driver.find_element_by_id("loginEmailAddress")
        password_input = self.driver.find_element_by_id("loginPassword")
        email_input.send_keys("your_email@example.com")
        password_input.send_keys("your_password")
        password_input.send_keys(Keys.RETURN)

        # wait for the login to complete and the dashboard page to load
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("dashboard")
        )
        

        # visit the property listing page
        self.driver.get(response.url)
        sel = HtmlResponse(url=response.url, body=self.driver.page_source, encoding='utf-8')
        # Scrape the page using Scrapy selectors
        #listings = sel.xpath('//div[@id="l-searchResults"]//div[@class="l-searchResult is-list"]')
        #for listing in listings:
        l = ItemLoader(item=RightmoveItem(), response=sel)
        l.default_output_processor = TakeFirst()

        l.add_xpath('address', '//div[@itemprop="address"]//span[@itemprop="streetAddress"]/text()')
        l.add_xpath('postcode', '//div[@itemprop="address"]//span[@itemprop="postalCode"]/text()')
        l.add_xpath('city', '//div[@itemprop="address"]//span[@itemprop="addressLocality"]/text()')
        l.add_xpath('price', '//div[@class="property-header__price"]//strong/text()')
        l.add_xpath('description', '//div[@itemprop="description"]/p/text()', MapCompose(str.strip))
        l.add_xpath('features', '//ul[@class="property-details__features"]/li/text()', MapCompose(str.strip))

        yield l.load_item()

    def closed(self, reason):
        self.driver.quit() # close the webdriver instance when the spider is finished
