from datetime import datetime
import json
from math import floor 
import os
import scrapy
from scrapy import Spider
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from selenium.webdriver import Chrome, ChromeOptions #, Firefox, FirefoxOptions
from selenium.webdriver.chrome.service import Service
#from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
#from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from tqdm.auto import tqdm

from property_scraper import DRIVER_PATH


class SeleniumSpider(Spider):
    DRIVER_PATH = DRIVER_PATH
    #DRIVER_PATH = os.path.join(os.path.expanduser('~'), 'bin', 'chromedriver', '114.0.5735.90', 'chromedriver')
    MAXIMUM_WAITING_TIME = 20
    GENERAL_PAUSE_TIME = 2

    def init_driver(self):
        options = ChromeOptions()
        self.driver = Chrome(service=Service(self.DRIVER_PATH), options=options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, self.MAXIMUM_WAITING_TIME).until
    
    def sleep(self, factor:float=1.0):
        self.driver.implicitly_wait(factor * self.GENERAL_PAUSE_TIME)
        sleep(factor * self.GENERAL_PAUSE_TIME)

    #def start_requests(self):
    #    self.init_driver()
    #    # Start scraping with the initial URL
    #    yield scrapy.Request(url='https://example.com', meta={'driver': self.driver}, callback=self.parse)

    def parse(self, response):
        self.driver.get(response.url)
        self.sleep()
        # Use Selenium to interact with the webpage
        # Extract data using Selenium
        # ...

        # Create a new Scrapy response using the source code obtained from Selenium
        body = self.driver.page_source
        _response = HtmlResponse(self.driver.current_url, body=body, encoding='utf-8')
        # Process the response using Scrapy
        # ...        

    def __init__(self, name:str='selenium_spider'):
        self.name = name        
        self.init_driver()
        

    def closed(self, reason):
        self.driver.quit()


class SeleniumSearchSpider(SeleniumSpider):

    NUMBER_OF_SCROLLS_PER_TEST = 3
    SCROLL_PAUSE_TIME = 2
    MAX_NUMBER_OF_SCROLLS = 1000

    RC_FILENAME = os.path.join(os.path.expanduser('~'), 'property_scraper.json')
    ROOT_FOLDER = '/home/data/property_scraper/demos/downloads'
    URL = ''
    PERIOD = {}
    WEBSITE = ''
    LOGIN_URL = ''
    LOGIN_XPATH = {}
    LOGIN_ID = {}
    SEARCH_TYPE = 'multiple pages'
    SEARCH_XPATH = {}
    SEARCH_ID = {}
    SEARCH_SELECT = {}

    def read_credentials(self):
        with open(self.RC_FILENAME, 'r') as f:
            self.credentials = json.load(f)[self.WEBSITE]
                
    def login(self):
        self.driver.get(self.LOGIN_URL)
        self.sleep()
        
        if 'advertisement' in self.LOGIN_XPATH.keys():
            button = self.wait(EC.element_to_be_clickable((By.XPATH, self.LOGIN_XPATH['advertisement'])))
            button.click()
            self.sleep()
        
        if 'cookie' in self.LOGIN_XPATH.keys():
            button = self.wait(EC.element_to_be_clickable((By.XPATH, self.LOGIN_XPATH['cookie'])))
            button.click()
            self.sleep()
        
        self.read_credentials()
        if 'email' in self.LOGIN_XPATH.keys():
            element_email = self.wait(EC.element_to_be_clickable((By.XPATH, self.LOGIN_XPATH['email'])))
        elif 'email' in self.LOGIN_ID.keys():
            element_email = self.wait(EC.element_to_be_clickable((By.ID, self.LOGIN_ID['email'])))
        element_email.send_keys(self.credentials['email'])
                    
        if 'password' in self.LOGIN_XPATH.keys():
            element_password = self.wait(EC.element_to_be_clickable((By.XPATH, self.LOGIN_XPATH['password'])))
        elif 'password' in self.LOGIN_ID.keys():
            element_password = self.wait(EC.element_to_be_clickable((By.ID, self.LOGIN_ID['password'])))
        element_password.send_keys(self.credentials['password'])
        
        if 'remember' in self.LOGIN_XPATH.keys() or 'remember' in self.LOGIN_ID.keys():
            if 'remember' in self.LOGIN_XPATH.keys():
                button = self.wait(EC.element_to_be_clickable((By.XPATH, self.LOGIN_XPATH['remember'])))
            elif 'remember' in self.LOGIN_ID.keys():
                button = self.wait(EC.element_to_be_clickable((By.ID, self.LOGIN_ID['remember'])))
            button.click()

        '''
        <ul id="select-options-36d8e8ae-dd03-09e0-34bd-c8d59e174c52" class="dropdown-content select-dropdown" style="width: 80px; position: absolute; top: 0px; left: 0px; opacity: 1; display: none;"><li class=""><span>12</span></li><li class=""><span>60</span></li><li class=""><span>120</span></li></ul>
        '''

        if 'login' in self.LOGIN_XPATH.keys():
            button =  self.wait(EC.element_to_be_clickable((By.XPATH, self.LOGIN_XPATH['login'])))
        elif 'login' in self.LOGIN_ID.keys():
            button =  self.wait(EC.element_to_be_clickable((By.ID, self.LOGIN_ID['login'])))
        button = self.wait(EC.element_to_be_clickable((By.XPATH, self.LOGIN_XPATH['login'])))            
        button.click()
        self.sleep()

    @staticmethod
    def format_date(date):
        # Get the current date and format it to 'YYYY/MM/DD'
        today = date.strftime('%Y/%m/%d')
        return today
    
    def set_date(self, date, period:str='future'):
        # Get the current date and format it to 'YYYY/MM/DD'
        today = self.format_date(date)
        print(today)
        
        if period == 'future':
            #<input type="text" class="ico-01 datepicker hasDatepicker" placeholder="Data vendita dal" name="dataVenditaDa" id="venditaDal_1" value="" readonly="readonly">
            element_data_vendita = self.wait(EC.presence_of_element_located((By.ID, self.SEARCH_ID['date_from'])))
            #driver.find_element(By.ID, "venditaDal_1")
        elif period == 'past':
            #<input type="text" class="ico-01 datepicker hasDatepicker" placeholder="Data vendita al" name="dataVenditaA" id="venditaAl_1" value="" readonly="readonly">
            element_data_vendita = self.wait(EC.presence_of_element_located((By.ID, self.SEARCH_ID['date_to'])))
            #driver.find_element(By.ID, "venditaAl_1")
        else:
            raise ValueError(f"The defined value for period '{period} is not valid! Please specify a valid value.")
            
        print(element_data_vendita.get_attribute("value"))
        self.driver.execute_script("arguments[0].setAttribute('value',arguments[1])", element_data_vendita, today)
        #driver.implicitly_wait(GENERAL_PAUSE_TIME)
        self.sleep()
    
    def set_number_of_results_per_page(self, number_of_results_per_page:int=120):
        element = self.wait(EC.presence_of_element_located((By.XPATH, self.SEARCH_SELECT['number_of_results_per_page'])))
        if self.SEARCH_SELECT['number_of_results_per_page'].lower().startswith('//select'):
            self.driver.execute_script("arguments[0].setAttribute('value',arguments[1])", element, str(number_of_results_per_page))
            self.driver.execute_script("var select = arguments[0]; for(var i = 0; i < select.options.length; i++){ if(select.options[i].text == arguments[1]){ select.options[i].selected = true; } }", element, str(number_of_results_per_page))
        elif self.SEARCH_SELECT['number_of_results_per_page'].lower().startswith('//ul') or self.SEARCH_SELECT['number_of_results_per_page'].lower().startswith('//span'):
            self.driver.execute_script("arguments[0].click();", element)
        self.sleep() 
        '''
        Today I cannot change the number of results per page!!!
        '''
        #self.alert()
    
    def set_contract_type(self, contract_type:str='Vendita'):
        element = self.wait(EC.presence_of_element_located((By.XPATH, self.SELECT_XPATH['contract_type'])))
        if self.SEARCH_SELECT['contract_type'].lower().startswith('//select'):
            self.driver.execute_script("arguments[0].setAttribute('value',arguments[1])", element, 'V')
        self.sleep()        

    def set_sorting_criteria(self, sorting_criteria:str='Latest Acquisitions'):
        button = self.driver.find_element(By.XPATH, self.SEARCH_SELECT['sorting_criteria'])
        if self.SEARCH_SELECT['sorting_criteria'].lower().startswith('//select'):
            self.driver.execute_script("arguments[0].setAttribute('value',arguments[1])", button, sorting_criteria)
        elif self.SEARCH_SELECT['sorting_criteria'].lower().startswith('//ul'):
            self.driver.execute_script("arguments[0].click();", button)
        self.sleep()
    
    @staticmethod
    def get_number_of_results(element):
        return element.text
    
    @staticmethod
    def get_number_of_results_per_page(text:str):
        return text
            
    def scroll_down(self, search_date, search_period, test_only):        
        if 'number_of_results' in self.SEARCH_XPATH.keys():
            number_of_results = self.get_number_of_results(self.driver.find_element(By.XPATH, self.SEARCH_XPATH['number_of_results']))
            number_of_results = int(number_of_results)
            print(f"Number of results is {number_of_results}.")
        
        if 'number_of_results_per_page' in self.SEARCH_XPATH.keys():
            number_of_results_per_page = len(self.driver.find_elements(By.XPATH, self.SEARCH_XPATH['number_of_results_per_page']))
            print(f"Number of results per page is {number_of_results_per_page}.")
        
        number_of_pages = floor(number_of_results / number_of_results_per_page)
        if number_of_results % number_of_results_per_page > 0:
            number_of_pages += 1
        print(f"Number of pages is {number_of_pages}.")
        
        if self.SEARCH_TYPE == 'multiple pages':
            pbar = tqdm(range(number_of_pages))
            for page_id in pbar:
                filename = f'/home/data/property_scraper/demos/downloads/{self.WEBSITE}/{self.WEBSITE}_search_{search_date.strftime("%Y%m%d%H%M%S")}_{search_period}_{page_id + 1}.html'
                pbar.set_description(f"{os.path.basename(filename)}")
                with open(filename, 'w') as f:
                    f.write(self.driver.page_source)

                if 'scroll' in self.SEARCH_XPATH.keys():
                    #url = f'https://resales.intrum.it/risultati-annunci/index.html?fromSearch=true&Contratto=&Categoria=&Provincia=&Comune=&Quartiere=&PrezzoMin=&PrezzoMax=&SuperficieMin=&SuperficieMax=&Locali=#start-{page_id * number_of_results_per_page}'
                    #driver.get(url)
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    #<button data-v-43528388="" title="next" class="focus:vue-ads-outline-none vue-ads-ml-1 vue-ads-leading-normal vue-ads-w-6 hover:vue-ads-bg-gray-100"><span><i class="fa fa-angle-right"></i></span></button>
                    if page_id < number_of_pages - 1:
                        self.wait(EC.element_to_be_clickable((By.XPATH, self.SEARCH_XPATH['scroll']))).click()
                        self.sleep()
                else:
                    url = self.NEXT_PAGE_URL.format(page_id + 2)
                    self.driver.get(url)
                    self.sleep()
                if test_only and (page_id > self.NUMBER_OF_SCROLLS_PER_TEST):
                    break
            #pbar.update(1)
        elif self.SEARCH_TYPE == 'single page':
            container = self.SCROLL_CONTAINER
            last_height = 0
            last_number_of_results_per_page = 0
            counter = 0
            while True and counter <= number_of_pages:
                # Load more results function is triggered by scroll event on element.
                self.driver.execute_script(f'var divElement = $(".{container}"); divElement.scrollTop(divElement[0].scrollHeight); divElement.trigger("scroll");')
                self.sleep(5)
                new_height = self.driver.execute_script("return document.getElementsByClassName('listings-container-block')[0].scrollHeight;")
                self.sleep(5)
                new_number_of_results_per_page = len(self.driver.find_elements(By.XPATH, self.SEARCH_XPATH['number_of_results_per_page']))
                self.sleep(5)
                pbar.set_description(f"{container} : {new_number_of_results_per_page} out of {number_of_results} ...")
                if (last_height != new_height) or (last_number_of_results_per_page != new_number_of_results_per_page):
                    last_height = new_height
                    last_number_of_results_per_page = new_number_of_results_per_page
                else:
                    print(f"The loop was terminated with last height = {last_number_of_results_per_page} and new_height = {new_number_of_results_per_page}.")
                    break # we have reached the end of the page        

                counter += 1
                pbar.update(1)
                if test_only and (counter > self.NUMBER_OF_SCROLLS_PER_TEST):
                    break

            print(f'The page was scrolled down {counter} times!')
            filename = f'{self.ROOT_FOLDER}/{self.WEBSITE}/{self.WEBSITE}_search_{search_date.strftime("%Y%m%d%H%M%S")}_{search_period}.html'
            pbar.set_description(f"{os.path.basename(filename)}")
            with open(filename, 'w') as f:
                f.write(self.driver.page_source)

    '''
    def alert(self):
        # Open a new window with a custom message
        message = "Please set the number of results per page to the mximum value allowed by the select element!"
        self.driver.execute_script(f"alert('{message}');")

        # Switch to the alert pop-up window
        alert = self.driver.switch_to.alert

        # Get the text from the alert pop-up
        alert_text = alert.text
        print("Alert Text:", alert_text)

        # Accept the alert (close the pop-up)
        alert.accept()
    '''

    def search(self, 
               date, 
               period:str='future', 
               contract_type:str='Vendita', 
               number_of_results_per_page:int=120, 
               sorting_criteria:int='', 
               test_only:bool=False):
        if self.URL:
            if ('{}' in self.URL) and (period in self.PERIOD.keys()):
                self.URL = self.URL.replace('{}', f"{self.PERIOD[period]}")
            self.driver.get(self.URL)
            self.sleep()
        
        if ('date_from' in self.SEARCH_ID.keys()) or ('date_to' in self.SEARCH_ID.keys()):
            self.set_date(date=date, period=period)
        
        #<div class="gx-col-5 gx-motore-ricerca-div-submit"><div class="gx-pd"><div class="gx-motore-ricerca-submit" onclick="gxMotoreRicercaSubmit('risultati-annunci/index.html')">Cerca</div></div></div>
        
        if 'cookie' in self.SEARCH_XPATH.keys():
            button = self.wait(EC.element_to_be_clickable((By.XPATH, self.SEARCH_XPATH['cookie'])))
            button.click()
            self.sleep()

        if 'popup_window' in self.SEARCH_XPATH.keys():
            button = self.wait(EC.element_to_be_clickable((By.XPATH, self.SEARCH_XPATH['popup_window'])))
            button.click()
            self.sleep()
    
        if 'url' in self.SEARCH_XPATH.keys():
            #<li data-tab="my-asta-tab-3" class="tab-link-myasta current"><span class="fas fa-list"></span>&nbsp;&nbsp;I tuoi risultati</li>
            #<li data-tab="my-asta-tab-3" class="tab-link-myasta"><span class="fas fa-list"></span>&nbsp;&nbsp;I tuoi risultati</li>
            button = self.driver.find_element(By.XPATH, self.SEARCH_XPATH['url'])
            button.click()
            self.sleep()
            
        if 'number_of_results_per_page' in self.SEARCH_SELECT.keys():
            self.set_number_of_results_per_page(number_of_results_per_page=number_of_results_per_page)
            
        if 'contract_type' in self.SEARCH_SELECT.keys():
            self.set_contract_type(contract_type=contract_type)
            
        if 'sorting_criteria' in self.SEARCH_SELECT.keys():
            self.set_sorting_criteria(sorting_criteria=sorting_criteria)
        
        self.scroll_down(search_date=date, search_period=period, test_only=test_only)

    def __init__(self, 
                 date=datetime.now(), 
                 period:str='future', 
                 contract_type:str='Vendita', 
                 number_of_results_per_page:int=120, 
                 sorting_criteria:int='',
                 test_only:bool=False):
        
        #self.name = name
        
        self.init_driver()
        
        if self.LOGIN_URL and self.LOGIN_XPATH:
            self.login()
        else:
            self.driver.get(self.URL)
            self.sleep()
        self.search(date=date, 
                    period=period, 
                    contract_type=contract_type, 
                    number_of_results_per_page=number_of_results_per_page, 
                    sorting_criteria=sorting_criteria,
                    test_only=test_only)
