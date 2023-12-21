
import logging
from autologging import logged, TRACE, traced

from bs4 import BeautifulSoup
from datetime import datetime
from lxml import etree, html
import pandas as pd
import re
from tqdm import tqdm 

from property_scraper import DEFAULT_HTML_PARSER, RIGHTMOVE_URL_ROOTNAME


class Property():
    def scrape(house_url, town):
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO.StringIO(house_html), house_parser)
        data['Description'] = house_tree.xpath('string(//div[@class="propertyDetailDescription"])')
        # Only look at houses with the word 'views' in the ad text. 
        if 'views' in house_text.lower() or 'elevated position' in house_text.lower():
            house = {}
            stopped_phrase = None
            # Check for stop phrases
            title = house_tree.xpath('string(//h1[@id="propertytype"])')
            for sp in stop_phrases:
                if (sp in house_text.lower()):
                    #print 'Ignoring %s because of stop phrase: %s' % (HOUSE_URL, sp)
                    stopped_phrase = sp
                if (sp in title.lower()):
                    stopped_phrase = sp
            #if not any(d.get('link') == HOUSE_URL for d in house_items):
            image_url = tostring(house_tree.xpath('//img[@id="mainphoto"]')[0])
            price = house_tree.xpath('string(//div[@id="amount"])')
            nearby_stations = house_tree.xpath('string(//div[@id="nearbystations"]/div)')
            ns = nearby_stations.split("(")
            distance = ns[-1].replace(")","")
            distance = ' '.join(distance.split()).strip()
            if float(distance.replace(" miles",""))>1.5:
                return False
            map_img = house_tree.xpath('//a[@id="minimapwrapper"]/img')
            if map_img:
                map_img = tostring(house_tree.xpath('//a[@id="minimapwrapper"]/img')[0])
            else:
                map_img = ''
            house['title'] = "%s - %s, %s, %s from station" % (title, town, price, distance)
            #print 'HOUSE FOUND! %s, %s ' % (house['title'], HOUSE_URL)
            item_text = '<a href="' + HOUSE_URL + '">' + image_url + '</a>'
            #item_text += '<div style="position:relative;">'
            item_text += '<a href="' + HOUSE_URL + '">' + map_img + '</a>'
            #item_text += '<img id="googlemapicon" src="http://www.rightmove.co.uk/ps/images11074/maps/icons/rmpin.png"'
            #item_text += ' style="position:absolute;top:100px;left:100px;alt="Property location" /></div>'
            item_text += house_text
            item_text = item_text.replace("views","<span style='font-weight:bold;color:red;'>views</span>")
            house['description'] = item_text.replace("fireplace","<span style='font-weight:bold;color:red;'>fireplace</span>")
            if stopped_phrase:
                house['stop'] = stopped_phrase
            else:
                house['stop'] = ''
            house['link'] = HOUSE_URL
            house['pubDate'] = datetime.now()
    
    def get_page(self, content:str, rent_or_sale:str, engine:str=DEFAULT_HTML_PARSER): #, request_content: str, get_floorplans: bool = False):
        """Method to scrape data from a single page of search results. Used
        iteratively by the `get_results` method to scrape data from every page
        returned by the search."""
        
        data = {}
        soup = BeautifulSoup(content, 'html.parser')
                    
        """
        try:
            streetAddress = list(soup.findAll("h1", itemprop="streetAddress")[0])[0]
        except:
            pass

        try:
            propertyType = list(list(soup.find(text='PROPERTY TYPE').parent.parent())[-1])[0]
        except:
            pass

        try:
            bedrooms = int(list(list(soup.find(text='BEDROOMS').parent.parent())[-1])[0][-1])
        except:
            pass

        try:
            bathrooms = int(list(list(oup.find(text='BATHROOMS').parent.parent())[-1])[0][-1])
        except:
            pass
    
        try:
            sqft = list(list(oup.find(text='SIZE').parent.parent())[-2])[0]
            sqft = [int(s) for s in sqft.split() if s.isdigit()][0]
        except:
            pass
        
        try:
            guidePrice = soup.find(text='Guide Price').parent.parent()[1]
            guidePrice = guidePrice.find(text=re.compile("£"))
            guidePrice = [int(s) for s in guidePrice.split()[0] if s.isdigit()]
            guidePrice = int("".join(map(str, guidePrice)))
        except:
            guidePrice = soup.find(text='Offers in Region of').parent.parent()[1]
            guidePrice = guidePrice.find(text=re.compile("£"))
            guidePrice = [int(s) for s in guidePrice.split()[0] if s.isdigit()]
            guidePrice = int("".join(map(str, guidePrice)))
        finally:
            guidePrice = soup.find(text=re.compile("£"))
            guidePrice = [int(s) for s in guidePrice.split()[0] if s.isdigit()]
            guidePrice = int("".join(map(str, guidePrice)))
        """            
