# -*- coding: utf-8 -*-

# Author : Federico Garzarelli
# Date : 06/01/2020
# Description : web crawler for www.astalegale.net
#
# Requirements:
# - selenium (run "pip install selenium" from cmd)
# - Mozilla
# - geckodriver.exe, to be placed in PATH (e.g. C:\Users\feder\Anaconda3)
#
# To Launch:
# - start python from cmd
# - launch in python, execfile("astalegale.py")
# - when opening the output text file in Excel, select the encoding utf-8 and change the regional settings to Italian


# global vars
links = []

# Libraries
import sys
import codecs

sys.stdout = codecs.getwriter("iso-8859-1")(sys.stdout, 'xmlcharrefreplace')
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


URL = "https://www.astalegale.net/"

# Initialise the Firefox driver
def init_driver():
    driver = webdriver.Firefox()
    driver.wait = WebDriverWait(driver, 5)
    return driver

def safe_click(byWhat, buttonLabel):
    driver.wait = WebDriverWait(driver, 5)
    button = driver.wait.until(EC.element_to_be_clickable((byWhat, buttonLabel)))
    button.click()

# Launch the search given the parameters specified in search_params
def lookup(driver):
    driver.get(URL)
    try:
        safe_click(By.ID, "cc-goto-advanced-search")
        WebDriverWait(driver, 60).until(EC.url_changes(URL))
    except TimeoutException:
        pass
        # print("Box or Button not found.") # TODO: Fix error thrown by print


# Loop through the results of the search query and save the corresponding links
def getlinks(driver):
    pages_remaining = True
    while pages_remaining:
        # DO YOUR THINGS WITHIN THE PAGE
        for a in driver.find_elements_by_class_name('cc-item-grid'):
            links.append(a.find_element_by_css_selector('a').get_attribute('href'))
        # Checks if there are more pages with links
        try:
            NextPagebutton = driver.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".app-btnNextPage")))
            driver.execute_script("arguments[0].scrollIntoView();", NextPagebutton)
            NextPagebutton.click()
            sleep(5)
        except TimeoutException:
            #print("End of pages.")
            pages_remaining = False

# give webpage to BeautifulSoup for HTML parsing
def givesoup(url):
    http = urllib3.PoolManager()
    MaxRetry = 5
    while (MaxRetry >= 0):
        try:
            page = http.request('GET', url)
            soup = BeautifulSoup(page.data, "lxml", from_encoding='utf8')
            return soup
        except Exception:
            #print('Internet connectivity Error Retrying in 5 seconds :');
            #print(MaxRetry)
            sleep(5)
            MaxRetry = MaxRetry - 1


# HTML parsing with BeautifulSoup
def readhtml(url):
    titlearr = []
    headerarr = []
    dataarr = []
    soup = givesoup(url)  # Tutto ciò che è nella pagina ora è in soup.

    for tag in soup.find_all('div', class_='cc-section-info'):
        thistitle = tag.find('h3', class_='cc-title')
        thistitle = thistitle.getText()
        thistitle = re.sub('\s+', ' ', thistitle).strip()  # substitute all tabs, newlines and other "whitespace-like" characters, eliminate trailing space
        thistitle.encode(encoding='UTF-8', errors='strict')
        titlearr.append(thistitle)
        for elem in tag.find_all('span', class_='cc-field-title'):
            thisheader = elem.getText()
            thisheader = re.sub('\s+', ' ', thisheader).strip()  # substitute all tabs, newlines and other "whitespace-like" characters, eliminate trailing space
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
            thisheader = re.sub('\s+', ' ', thisheader).strip()  # substitute all tabs, newlines and other "whitespace-like" characters, eliminate trailing space
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


# Loop through the links and concatenate results
def looplinks(driver):
    data = []
    i = 0
    for link in links:
        i = i + 1
        df = readhtml(link)
        data.append(df)
        #print(str(i) + ': ' + link);
    data = pd.concat(data, axis=0, ignore_index=True)
    return data


# Main
if __name__ == "__main__":
    driver = init_driver()
    lookup(driver)
    getlinks(driver)
    data = looplinks(driver)
    driver.quit()
    outfileName = "astalegale_" + date.today().strftime("%Y%m%d") + ".txt"
    data.to_csv(outfileName, index=False, encoding='utf-8')

