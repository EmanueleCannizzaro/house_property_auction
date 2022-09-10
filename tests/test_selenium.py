from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


DRIVER_PATH = '/data/git/chromedriver'
URL ='https://www.google.com'


def test_selenium3():
    driver = webdriver.Chrome(executable_path=DRIVER_PATH)
    driver.get(URL)
    driver.find_element(By.NAME, 'q').send_keys('Italy')
    print(driver.page_source)
    driver.quit()

def test_selenium3_headless():
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")

    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
    driver.get(URL)
    driver.find_element(By.NAME, 'q').send_keys('Italy')
    print(driver.page_source)
    driver.quit()

def test_selenium():
    #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver = webdriver.Chrome(service=Service(DRIVER_PATH))
    driver.maximize_window()
    driver.get(URL)
    driver.find_element(By.NAME, 'q').send_keys('Italy')
    print(driver.page_source)
    driver.quit()

def test_selenium_headless():
    options = Options()
    options.add_argument("start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(URL)
    driver.find_element(By.NAME, 'q').send_keys('Italy')
    print(driver.page_source)
    driver.quit()
