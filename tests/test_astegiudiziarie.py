from json import dump, load
from selenium import webdriver
#from selenium.webdriver.chrome.options import Options
#from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep, time
#from webdriver_manager.chrome import ChromeDriverManager
#from webdriver_manager.firefox import FirefoxDriverManager


URL ='https://www.astegiudiziarie.it/User/RicercheSalvate#'
SCROLL_PAUSE_TIME = 2


def test_astegiudiziarie():

    filename = '/home/emanuele/Documents/astegiudiziarie.json'
    with open(filename, 'r') as f:
        account = load(f)
    #options.add_argument("start-maximized")
    #options.add_argument("user-data-dir=/home/emanuele/.config/google-chrome")
    #options.add_argument('profile-directory=Default')
    #options.add_argument('profile-directory=Emanuele')
    #options.add_argument('profile-directory=Selenium')
    #options.add_argument('profile-directory=Person 1')
    #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    if 1 == 1:
        options = webdriver.chrome.options.Options()
        #options.add_argument("user-data-dir=/home/emanuele/.config/google-chrome")
        #options.add_argument('profile-directory=Default')
        DRIVER_PATH = '/home/emanuele/bin/chromedriver'
        driver = webdriver.Chrome(service=webdriver.chrome.service.Service(DRIVER_PATH), options=options)
    else:
        options = webdriver.firefox.options.Options()
        #options.add_argument("--disable-web-security")
        #options.add_argument("--allow-running-insecure-content")
        #options.add_argument("user-data-dir=/home/emanuele/.mozilla/firefox/bxnbv04s.default")
        #options.add_argument('profile-directory=default')
        DRIVER_PATH = '/home/emanuele/bin/geckodriver'
        driver = webdriver.Firefox(service=webdriver.firefox.service.Service(DRIVER_PATH), options=options)
    driver.maximize_window()
    driver.get(URL)
    print(driver.current_url)
    driver.find_element(By.NAME, 'txtUsername').send_keys(account['username'])
    driver.find_element(By.NAME, 'txtPassword').send_keys(account['password'])
    driver.find_element(By.NAME, 'btnLogin').click()
    sleep(2)
    driver.switch_to.window(driver.window_handles[0])
    print(driver.current_url)
    #print(driver.page_source)
    sleep(4)
    driver.find_element(By.CLASS_NAME, 'avvia').click()#'Italy')
    sleep(10)
    driver.switch_to.window(driver.window_handles[0])
    print(driver.current_url)
    filename = 'astegiudiziarie.html'
    with open(filename, 'w') as f:
        f.write(driver.page_source)
    #driver.find_element(By.CLASS_NAME, 'fa-map-o').click()
    #sleep(2)
    #driver.find_element(By.CLASS_NAME, 'fa-th-list').click()
    #sleep(2)

    while True:
        try:
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='button-load-more-results']"))).click()
            print("MORE button clicked")
        except TimeoutException:
            break

    #while True:
    #    try:
    #        element = driver.find_element(By.CLASS_NAME, 'button-load-more-results')
    #        element.click()
    #        print("MORE button clicked")
    #    except TimeoutException:
    #        break

    # Get scroll height
    #fs-results-container fs-inner-container
    containers = [
        #'fs-results-container',
        'fs-content',
        #'listings-container-block',
        #'listings-container',
        #'row',
        #'fs-listings',
        ##'list-layout',
        #'load-more-results'
    ]
    for container in containers:
        scroll_down(driver, container)

    '''containers = [
        #'fs-results-container',
        'fs-content',
        #'listings-container-block',
        #'listings-container',
        #'row',
        #'fs-listings',
        #'list-layout',
        #'load-more-results'
    ]
    for container in containers:
        print(container)
        listings_container = driver.find_element(By.CLASS_NAME, container)
        listings_container.send_keys(Keys.PAGE_DOWN)
    '''

    #WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME,'button-load-more-results'))).click()
    #element = driver.find_element(By.CLASS_NAME,'button-load-more-results')
    #driver.execute_script("arguments[0].scrollIntoView(true);")
    #element.click()

    _elements = driver.find_elements(By.CLASS_NAME, 'goto-detail')
    #listing-item')
    elements = {k: v.get_attribute('href') for k, v in enumerate(_elements)}
    for key in elements.keys():
        print(f"{key} -> {elements[key]}")
    filename = 'astegiudiziarie.json'
    with open(filename, 'w') as f:
        dump(elements, f, indent=4)
    sleep(60)
    driver.quit()

def scroll_down(driver, container):
    """A method for scrolling the page."""
    _element = driver.find_element(By.CLASS_NAME, container)
    element = driver.find_element(By.CLASS_NAME, 'button-load-more-results')
    # Get scroll height.
    last_height = driver.execute_script(f"return document.getElementsByClassName('{container}')[0].scrollHeight")
    while True:
        # Scroll down to the bottom.
        driver.execute_script("arguments[0].scrollIntoView(true);", _element)
        #driver.execute_script("document.querySelector('button-load-more-results');")
        driver.execute_script("arguments[0].click();", element)
        sleep(5)
        driver.execute_script(f"arguments[0].scrollTo(0, document.getElementsByClassName('{container}')[0].scrollHeight);", _element)
        # Wait to load the page.
        sleep(SCROLL_PAUSE_TIME)
        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script(f"return document.getElementsByClassName('{container}')[0].scrollHeight")
        print(container, last_height, new_height)
        if new_height == last_height:
            break
        else:
            last_height = new_height

if __name__ == "__main__":
    test_astegiudiziarie()
