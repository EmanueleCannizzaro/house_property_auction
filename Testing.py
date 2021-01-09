# -*- coding: utf-8 -*-

# Author : Federico Garzarelli
# Date : 16/05/2017
# Description : web crawler for www.astegiudiziarie.it
#
# Requirements:
# - selenium (run "pip install selenium" from cmd)
# - Google Chrome
# - chromedriver.exe, to be placed in PATH (e.g. C:\Users\feder\Anaconda3)
#
# To Launch:
# - start python from cmd
# - change search parameters in this script as required
# - when opening the output text file in Excel, select the encoding utf-8 and change the regional settings to Italian


# global vars
#                   Type, Price Min, Price Max, Province, Town
search_params = ["Appartamento", 100000, 120000, "Roma", "Roma"]
links = []

# Libraries
import sys
import codecs

sys.stdout = codecs.getwriter("iso-8859-1")(sys.stdout, 'xmlcharrefreplace')
import urllib3
import urllib

urllib3.disable_warnings()
from bs4 import BeautifulSoup
import string
import random
import numpy as np
import pandas as pd
import time
import os
import re
# For selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from time import sleep


# debugger
# import pdb
# from pdb import set_trace as bp

# Initialise the Firefox driver
def init_driver():
    driver = webdriver.Firefox()
    driver.wait = WebDriverWait(driver, 5)
    return driver


# Launch the search given the parameters specified in search_params
def lookup(driver, search_params):
    driver.get("https://www.astalegale.net/")
    try:
        boxType = Select(driver.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#ctl00_ContentPlaceHolder1_Mascherericerche1_ImmobiliareGenerale1_drpdTipologie"))))
        boxPriceFrom = driver.wait.until(EC.presence_of_element_located(
            (By.XPATH,
             """//*[@id="ctl00_ContentPlaceHolder1_Mascherericerche1_ImmobiliareGenerale1_txtFasciaPrezzoDa"]""")))
        boxPriceTo = driver.wait.until(EC.presence_of_element_located(
            (By.XPATH,
             """//*[@id="ctl00_ContentPlaceHolder1_Mascherericerche1_ImmobiliareGenerale1_txtFasciaPrezzoA"]""")))
        boxProvince = Select(driver.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#ctl00_ContentPlaceHolder1_Mascherericerche1_ImmobiliareGenerale1_drpdProvincie"))))
        boxTown = driver.wait.until(EC.presence_of_element_located(
            (By.XPATH,
             """//*[@id="ctl00_ContentPlaceHolder1_Mascherericerche1_ImmobiliareGenerale1_txtComuneImmobile"]""")))

        button = driver.wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "#ctl00_ContentPlaceHolder1_Mascherericerche1_ImmobiliareGenerale1_btnCerca")))

        boxType.select_by_visible_text(search_params[0])
        boxPriceFrom.send_keys(search_params[1])
        boxPriceTo.send_keys(search_params[2])
        boxProvince.select_by_visible_text(search_params[3])
        boxTown.send_keys(search_params[4])

        button.click()
        sleep(10)
    except TimeoutException:
        print("Box or Button not found.")


# Loop through the results of the search query and save the corresponding links
def getlinks(driver):
    pages_remaining = True
    while pages_remaining:
        # DO YOUR THINGS WITHIN THE PAGE
        for a in driver.find_elements_by_class_name('app-detail-open cc-link we-guaglio we-dark'):
            links.append(a.find_element_by_css_selector('a').get_attribute('href'))
        # Checks if there are more pages with links
        try:
            NextPagebutton = driver.wait.until(EC.element_to_be_clickable(
                (By.CLASS_NAME, "app-btnNextPage cc-arrow cc-arrow-right")))
            driver.execute_script("arguments[0].scrollIntoView();", NextPagebutton)
            NextPagebutton.click()
            sleep(5)
        except TimeoutException:
            print("End of pages.")
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
            print('Internet connectivity Error Retrying in 5 seconds :');
            print(MaxRetry)
            sleep(5)
            MaxRetry = MaxRetry - 1


# HTML parsing with BeautifulSoup
def readhtml(url):
    headerarr = []
    dataarr = []
    soup = givesoup(url)  # Tutto ciò che è nella pagina ora è in soup.
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


# Loop through the links and concatenate results
def looplinks(driver):
    data = []
    i = 0
    for link in links:
        i = i + 1
        df = readhtml(link)
        data.append(df)
        print(str(i) + ': ' + link);
    data = pd.concat(data, axis=0, ignore_index=True)
    return data


# Main
if __name__ == "__main__":
    driver = init_driver()
    lookup(driver, search_params)
    getlinks(driver)
    data = looplinks(driver)
    driver.quit()
    outfileName = "astegiudiziarie_" + search_params[4] + "_da" + str(search_params[1]) + "_a" + str(
        search_params[2]) + ".txt"
    data.to_csv(outfileName, index=False, encoding='utf-8')
