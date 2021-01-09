# Libraries
import sys
import codecs

import urllib3

urllib3.disable_warnings()
from bs4 import BeautifulSoup
import pandas as pd
import re

# For selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from time import sleep
from datetime import date

from collections import Counter  # Counter counts the number of occurrences of each item
#sys.stdout = codecs.getwriter("iso-8859-1")(sys.stdout, 'xmlcharrefreplace')
sys.stdout.reconfigure(encoding='iso-8859-1')


#
# Parent class: WebCrawler
#
class WebCrawler():

    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
        self.driver = webdriver.Firefox()
        self.driver.wait = WebDriverWait(self.driver, 5)
        self.links = []
        self.data = []

    def safe_click(self, byWhat, buttonLabel):
        self.driver.wait = WebDriverWait(self.driver, 5)
        button = self.driver.wait.until(EC.element_to_be_clickable((byWhat, buttonLabel)))
        button.click()

    def log(self, txt, dt=None):
        ''' Logging function for this strategy txt is the statement and dt can be used to specify a specific datetime'''
        if self.printlog:
            print('%s, %s' % (dt.isoformat(), txt))

    # give webpage to BeautifulSoup for HTML parsing
    def givesoup(self,url):
        http = urllib3.PoolManager()
        MaxRetry = 5
        while (MaxRetry >= 0):
            try:
                page = http.request('GET', url)
                soup = BeautifulSoup(page.data, "lxml", from_encoding='utf8')
                return soup
            except Exception:
                # print('Internet connectivity Error Retrying in 5 seconds :');
                # print(MaxRetry)
                sleep(5)
                MaxRetry = MaxRetry - 1

    # Does nothing: it is overridden in the child classes
    def readhtml(self,url):
        df = []
        return df

    # Loop through the links and concatenate results
    def looplinks(self):
        data = []
        i = 0
        for link in self.links:
            i = i + 1
            df = self.readhtml(link)
            data.append(df)
            # print(str(i) + ': ' + link);
        data = pd.concat(data, axis=0, ignore_index=True)
        return data

    def scrape(self):
        self.lookup()
        self.getlinks()
        self.data = self.looplinks()
        self.driver.quit()
        return self.data

#
# Child class: astalegale
#
class astalegale(WebCrawler):

    # Launch the search given the parameters specified in search_params
    def lookup(self):
        self.driver.get(self.url)
        try:
            self.safe_click(By.ID, "cc-goto-advanced-search")
            WebDriverWait(self.driver, 60).until(EC.url_changes(self.url))
        except TimeoutException:
            pass
            # print("Box or Button not found.") # TODO: Fix error thrown by print

    # Loop through the results of the search query and save the corresponding links
    def getlinks(self):
        pages_remaining = True
        while pages_remaining:
            # DO YOUR THINGS WITHIN THE PAGE
            for a in self.driver.find_elements_by_class_name('cc-item-grid'):
                self.links.append(a.find_element_by_css_selector('a').get_attribute('href'))
            # Checks if there are more pages with links
            try:
                NextPagebutton = self.driver.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".app-btnNextPage")))
                self.driver.execute_script("arguments[0].scrollIntoView();", NextPagebutton)
                NextPagebutton.click()
                sleep(5)
            except TimeoutException:
                # print("End of pages.")
                pages_remaining = False

    # HTML parsing with BeautifulSoup
    def readhtml(self, url):
        titlearr = []
        headerarr = []
        dataarr = []
        soup = self.givesoup(url)  # Tutto ciò che è nella pagina ora è in soup.

        for tag in soup.find_all('div', class_='cc-section-info'):
            thistitle = tag.find('h3', class_='cc-title')
            thistitle = thistitle.getText()
            thistitle = re.sub('\s+', ' ',
                               thistitle).strip()  # substitute all tabs, newlines and other "whitespace-like" characters, eliminate trailing space
            thistitle.encode(encoding='UTF-8', errors='strict')
            titlearr.append(thistitle)
            for elem in tag.find_all('span', class_='cc-field-title'):
                thisheader = elem.getText()
                thisheader = re.sub('\s+', ' ',
                                    thisheader).strip()  # substitute all tabs, newlines and other "whitespace-like" characters, eliminate trailing space
                thisheader.encode(encoding='UTF-8', errors='strict')
                headerarr.append(thisheader)

                thisdata = elem.findNext('span', class_='cc-field-text')
                if thisdata is not None:
                    thisdata = thisdata.getText()
                    thisdata = re.sub('\s+', ' ', thisdata).strip()
                    thisdata.encode(encoding='UTF-8', errors='strict')
                    dataarr.append(thisdata)
                else:
                    dataarr.append("Empty")

        for tag in soup.find_all('div', class_='cc-info-row'):
            for elem in tag.find_all('span', class_='cc-label'):
                thisheader = elem.getText()
                thisheader = re.sub('\s+', ' ',
                                    thisheader).strip()  # substitute all tabs, newlines and other "whitespace-like" characters, eliminate trailing space
                thisheader.encode(encoding='UTF-8', errors='strict')
                headerarr.append(thisheader)

                thisdata = elem.findNext('span', class_='cc-text')
                if thisdata is not None:
                    thisdata = thisdata.getText()
                    thisdata = re.sub('\s+', ' ', thisdata).strip()
                    thisdata.encode(encoding='UTF-8', errors='strict')
                    dataarr.append(thisdata)
                else:
                    dataarr.append("Empty")
        # add the url to the dataframe
        headerarr.append('url')
        dataarr.append(url)

        # rename column headers which are equal
        counts = Counter(headerarr)
        for s, num in counts.items():
            if num > 1:  # ignore strings that only appear once
                for suffix in range(1, num + 1):  # suffix starts at 1 and increases by 1 each time
                    headerarr[headerarr.index(s)] = s + ' ' + str(suffix)  # replace each appearance of s
        headerarr = [re.sub(r'\b 1\b', '', w) for w in headerarr]  # eliminate suffix 1
        df = pd.DataFrame(data=[dataarr], columns=headerarr)
        return df

#
# Child class: astegiudiziarie
#
class astegiudiziarie(WebCrawler):

    # Launch the search given the parameters specified in search_params
    def lookup(self):

        self.driver.get(self.url)
        try:
            boxType = Select(self.driver.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#ctl00_ContentPlaceHolder1_Mascherericerche1_ImmobiliareGenerale1_drpdTipologie"))))
            boxPriceFrom = self.driver.wait.until(EC.presence_of_element_located(
                (By.XPATH,
                 """//*[@id="ctl00_ContentPlaceHolder1_Mascherericerche1_ImmobiliareGenerale1_txtFasciaPrezzoDa"]""")))
            boxPriceTo = self.driver.wait.until(EC.presence_of_element_located(
                (By.XPATH,
                 """//*[@id="ctl00_ContentPlaceHolder1_Mascherericerche1_ImmobiliareGenerale1_txtFasciaPrezzoA"]""")))
            boxProvince = Select(self.driver.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#ctl00_ContentPlaceHolder1_Mascherericerche1_ImmobiliareGenerale1_drpdProvincie"))))
            boxTown = self.driver.wait.until(EC.presence_of_element_located(
                (By.XPATH,
                 """//*[@id="ctl00_ContentPlaceHolder1_Mascherericerche1_ImmobiliareGenerale1_txtComuneImmobile"]""")))

            button = self.driver.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "#ctl00_ContentPlaceHolder1_Mascherericerche1_ImmobiliareGenerale1_btnCerca")))

            boxType.select_by_visible_text(self.filters[0])
            boxPriceFrom.send_keys(self.filters[1])
            boxPriceTo.send_keys(self.filters[2])
            boxProvince.select_by_visible_text(self.filters[3])
            boxTown.send_keys(self.filters[4])

            button.click()
            sleep(10)
        except TimeoutException:
            print("Box or Button not found.")

    # Loop through the results of the search query and save the corresponding links
    def getlinks(self):
        pages_remaining = True
        while pages_remaining:
            # DO YOUR THINGS WITHIN THE PAGE
            for a in self.driver.find_elements_by_class_name('schedadettagliata'):
                self.links.append(a.find_element_by_css_selector('a').get_attribute('href'))
            # Checks if there are more pages with links
            try:
                NextPagebutton = self.driver.wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "#ctl00_ContentPlaceHolder1_Primasel2_1_dlstPrimasel_ctl10_btnSuccessiva")))
                self.driver.execute_script("arguments[0].scrollIntoView();", NextPagebutton)
                NextPagebutton.click()
                sleep(5)
            except TimeoutException:
                print("End of pages.")
                pages_remaining = False

    # HTML parsing with BeautifulSoup
    def readhtml(self, url):
        headerarr = []
        dataarr = []
        soup = self.givesoup(url)  # Tutto ciò che è nella pagina ora è in soup.
        for tag in soup.find_all("tr"):
            for elem in tag.find_all("th"):
                thisheader = elem.getText()
                thisheader = re.sub('\s+', ' ',
                                    thisheader).strip()  # substitute all tabs, newlines and other "whitespace-like" characters, eliminate trailing space
                thisheader.encode(encoding='UTF-8', errors='strict')
                headerarr.append(thisheader)

                thisdata = elem.findNext('td').getText()
                thisdata = re.sub('\s+', ' ', thisdata).strip()
                thisdata.encode(encoding='UTF-8', errors='strict')
                dataarr.append(thisdata)
        # add the url to the dataframe
        headerarr.append('url')
        dataarr.append(url)
        # rename column headers which are equal
        from collections import Counter  # Counter counts the number of occurrences of each item
        counts = Counter(headerarr)
        for s, num in counts.items():
            if num > 1:  # ignore strings that only appear once
                for suffix in range(1, num + 1):  # suffix starts at 1 and increases by 1 each time
                    headerarr[headerarr.index(s)] = s + ' ' + str(suffix)  # replace each appearance of s
        headerarr = [re.sub(r'\b 1\b', '', w) for w in headerarr]  # eliminate suffix 1
        df = pd.DataFrame(data=[dataarr], columns=headerarr)
        return df

#
# Child class: REdiscount
#
class REdiscount(WebCrawler):

    # Launch the search given the parameters specified in search_params
    def lookup(self):
        pass

    # Loop through the results of the search query and save the corresponding links
    def getlinks(self):
        pass

    # HTML parsing with BeautifulSoup
    def readhtml(self, url):
        df = []
        return df

#
# Child class: asteRE
#
class asteRE(WebCrawler):

    # Launch the search given the parameters specified in search_params
    def lookup(self):
        pass

    # Loop through the results of the search query and save the corresponding links
    def getlinks(self):
        pass

    # HTML parsing with BeautifulSoup
    def readhtml(self, url):
        df = []
        return df

#
# Child class: giustizia
#
class giustizia(WebCrawler):

    # Launch the search given the parameters specified in filters
    def lookup(self):
        pass

    # Loop through the results of the search query and save the corresponding links
    def getlinks(self):
        pass

    # HTML parsing with BeautifulSoup
    def readhtml(self, url):
        df = []
        return df