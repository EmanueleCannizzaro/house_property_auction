

from bs4 import BeautifulSoup
from joblib import Parallel, delayed
import pandas as pd
import pprint
import re
import requests
from selenium import webdriver
from tqdm import tqdm 

class House:
    def __init__(self, search_url:str=''):
        self.search_url = search_url
        self.pp = pprint.PrettyPrinter(indent=4)
        
    @property
    def page(self):
        """
        Returns house object from house_URL
        """
        options = webdriver.ChromeOptions();
        options.add_argument('--headless');
        browser = webdriver.Chrome(options=options)
        browser.get(self.url)
        html = browser.page_source
        house = BeautifulSoup(html, 'lxml')
        return house
    
    @property
    def urls(self):
        """
        Returns list of house URLs from a search URL
        """
        pages = 20
        house_URLs = []
        pbar = tqdm(range(pages))
        for x in pbar:
            page = self.search_url + "&index=" + str(int(x * 24))
            page = requests.get(page)
            soup = BeautifulSoup(page.content, 'html.parser')
            house_search_results = soup.findAll(class_="propertyCard-link")
            for house_URL in house_search_results:
                house_URLs.append(house_URL["href"])
        house_URLs = list(set(house_URLs))
        house_URLs = [x for x in house_URLs if len(x)>2]
        house_URLs = ["https://www.rightmove.co.uk" + url for url in house_URLs]
        return house_URLs

    @property
    def street_address(self):
        try:
            streetAddress = list(self.page.findAll("h1", itemprop="streetAddress")[0])[0]
            return streetAddress
        except:
            return "NA"

    @property
    def property_type(self):
        try:
            return list(list(self.page.find(text='PROPERTY TYPE').parent.parent())[-1])[0]
        except:
            return "NA"

    @property
    def bedrooms(self):
        try:
            return int(list(list(self.page.find(text='BEDROOMS').parent.parent())[-1])[0][-1])
        except:
            return "NA"

    @property
    def bathrooms(self):
        try:
            return int(list(list(self.page.find(text='BATHROOMS').parent.parent())[-1])[0][-1])
        except:
            return "NA"
        
    @property
    def sqft(self):
        try:
            sqft = list(list(self.page.find(text='SIZE').parent.parent())[-2])[0]
            sqft = [int(s) for s in sqft.split() if s.isdigit()][0]
            return sqft
        except:
            return "NA"
    
    @property
    def guide_price(self):
        try:
            guidePrice = self.page.find(text='Guide Price').parent.parent()[1]
            guidePrice = guidePrice.find(text=re.compile("£"))
            guidePrice = [int(s) for s in guidePrice.split()[0] if s.isdigit()]
            guidePrice = int("".join(map(str, guidePrice)))
            return guidePrice
        except:
            guidePrice = self.page.find(text='Offers in Region of').parent.parent()[1]
            guidePrice = guidePrice.find(text=re.compile("£"))
            guidePrice = [int(s) for s in guidePrice.split()[0] if s.isdigit()]
            guidePrice = int("".join(map(str, guidePrice)))
            return guidePrice
        finally:
            guidePrice = self.page.find(text=re.compile("£"))
            guidePrice = [int(s) for s in guidePrice.split()[0] if s.isdigit()]
            guidePrice = int("".join(map(str, guidePrice)))
            return guidePrice
        
    @property
    def info(self):
        infodict = {
            "URL": self.url,
            "Street Address": self.street_address,
            "Property Type": self.property_type,
            "Bedrooms": self.bedrooms,
            "Bathrooms": self.bathrooms,
            "Size (sq ft)": self.sqft,
            "Guide Price": self.guide_price
        }
        return infodict
