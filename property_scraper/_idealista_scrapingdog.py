
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import time

APIKEY = '63d9455c1c60c847bf30e13f'

l=list()
o={}

target_url = "https://www.idealista.com/venta-viviendas/torrelavega/inmobiliaria-barreda/"


driver=webdriver.Chrome()

driver.get(target_url)


time.sleep(7)
resp = driver.page_source
#resp = requests.get("https://api.scrapingdog.com/scrape?api_key=APIKEY&url={}&dynamic=false".format(target_url))

driver.close()

soup = BeautifulSoup(resp, 'html.parser')
totalProperties = int(soup.find("div",{"class":"listing-title"}).text.split(" ")[0])
totalPages = round(totalProperties/30)
allProperties = soup.find_all("div",{"class":"item-info-container"})

for i in range(0,len(allProperties)):
    o["title"]=allProperties[i].find("a",{"class":"item-link"}).text.strip("\n")
    o["price"]=allProperties[i].find("span",{"class":"item-price"}).text.strip("\n")
    o["area-size"]=allProperties[i].find("div",{"class":"item-detail-char"}).text.strip("\n")
    o["description"]=allProperties[i].find("div",{"class":"item-description"}).text.strip("\n")
    o["property-link"]="https://www.idealista.com"+allProperties[i].find("a",{"class":"item-link"}).get('href')
    l.append(o)
    o={}

print(totalPages)

for x in range(2,totalPages+1):
    target_url = "https://www.idealista.com/venta-viviendas/torrelavega/inmobiliaria-barreda/pagina-{}.htm".format(x)
    driver=webdriver.Chrome(PATH)

    driver.get(target_url)


    time.sleep(7)
    resp = driver.page_source
    #resp = requests.get("https://api.scrapingdog.com/scrape?api_key=APIKEY&url={}&dynamic=false".format(target_url))
    driver.close()

    soup = BeautifulSoup(resp, 'html.parser')
    allProperties = soup.find_all("div",{"class":"item-info-container"})
    for i in range(0,len(allProperties)):
        o["title"]=allProperties[i].find("a",{"class":"item-link"}).text.strip("\n")
        o["price"]=allProperties[i].find("span",{"class":"item-price"}).text.strip("\n")
        o["area-size"]=allProperties[i].find("div",{"class":"item-detail-char"}).text.strip("\n")
        o["description"]=allProperties[i].find("div",{"class":"item-description"}).text.strip("\n")
        o["property-link"]="https://www.idealista.com"+allProperties[i].find("a",{"class":"item-link"}).get('href')
        l.append(o)
        o={}

print(l)
