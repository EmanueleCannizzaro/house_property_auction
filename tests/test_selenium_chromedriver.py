from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
#from webdriver_manager.chrome import ChromeDriverManager


DRIVER_PATH = '/home/emanuele/bin/chromedriver'
URL ='https://www.google.com'


#def test_selenium3():
#    driver = webdriver.Chrome(executable_path=DRIVER_PATH)  # Optional argument, if not specified will search path.
#    driver.get(URL)
#    time.sleep(5) # Let the user actually see something!
#    search_box = driver.find_element(By.NAME, 'q')
#    search_box.send_keys('Italy')
#    search_box.submit()
#    time.sleep(5) # Let the user actually see something!
#    print(driver.page_source)
#    driver.quit()

#def test_selenium3_headless():
#    options = Options()
#    options.headless = True
#    options.add_argument("--window-size=1920,1200")
#
#    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
#    driver.get(URL)
#    time.sleep(5) # Let the user actually see something!
#    driver.find_element(By.NAME, 'q').send_keys('Italy')
#    print(driver.page_source)
#    driver.quit()

def test_selenium3_service():
    service = Service(DRIVER_PATH)
    service.start()
    driver = webdriver.Remote(service.service_url)
    driver.get(URL)
    time.sleep(5) # Let the user actually see something!
    driver.quit()

def test_selenium():
    #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver = webdriver.Chrome(service=Service(DRIVER_PATH))
    driver.maximize_window()
    driver.get(URL)
    time.sleep(5) # Let the user actually see something!
    driver.find_element(By.NAME, 'q').send_keys('Italy')
    print(driver.page_source)
    driver.quit()

def test_selenium_headless():
    options = Options()
    options.add_argument("start-maximized")
    #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver = webdriver.Chrome(service=Service(DRIVER_PATH), options=options)    
    driver.get(URL)
    time.sleep(5) # Let the user actually see something!
    driver.find_element(By.NAME, 'q').send_keys('Italy')
    print(driver.page_source)
    driver.quit()
