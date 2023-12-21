from selenium import webdriver
from selenium.webdriver.common.by import By

APIKEY = "1VOKFLW79X7J2T3GX1Q5JFCIJJN4NK4RCKDIXLLF9EKY76D5S6GROHJDO3YJBV8MDLHK8VUNIKNF9Z15"
PASS = "render_js=False&premium_proxy=True"

seleniumwire_options = {
    'proxy': {
        'http': f'http://{APIKEY}:{PASS}@proxy.scrapingbee.com:8886',
    }
}

# https://stackoverflow.com/questions/70485179/runtimeerror-when-using-undetected-chromedriver
#driver = uc.Chrome(use_subprocess=True)
options = webdriver.ChromeOptions();
options.add_argument('--headless');
driver = webdriver.Chrome(
    options=options, 
    #use_subprocess=True, 
    seleniumwire_options=seleniumwire_options
)

results = {}

def extract_provinces():
    driver.get("https://www.idealista.com/")
    #input("press any key to continue...")
    provinces_div = driver.find_element(By.CLASS_NAME, 'locations-list')
    provinces = provinces_div.find_elements(By.XPATH, './/a')
    for province in provinces:
        results[province.text] = {
            "url": province.get_attribute('href'),
            "municipalities": {}
        }

def extract_municipalities(province, url):
    driver.get(url)
    municipalities = driver.find_elements(By.XPATH, '//ul[@id="location_list"]//a')
    results[province]['municipalities'] = {}
    for municipality in municipalities:
        results[province]['municipalities'][municipality.text] = {
            "url": municipality.get_attribute('href'),
            "properties": [],
        }

def extract_properties(url):
    driver.get(url)
    property_divs = driver.find_elements(By.XPATH, "//article[contains(@class, 'item')]")
    properties = []
    for div in property_divs:
        property = {}
        property['title'] = div.find_element(By.XPATH, './/a[@class="item-link"]').text
        property['url'] = div.find_element(By.XPATH, './/a[@class="item-link"]').get_attribute('href')
        property['price'] = div.find_element(By.XPATH, './/div[contains(@class, "price-row")]').text
        property['detail'] = div.find_element(By.XPATH, './/div[@class="item-detail-char"]').text
        property['description'] = div.find_element(By.XPATH, './/div[contains(@class, "item-description")]').text
        properties.append(property)
        
    if driver.find_elements(By.CLASS_NAME, "next"):
        url = driver.find_element(By.XPATH, "//li[@class='next']/a").get_attribute("href")
        properties += extract_properties(url)
    return properties


if __name__ == "__main__":
    extract_provinces()
    for province in results.keys():
        extract_municipalities(province, results[province]['url'])
        for municipality in results[province]['municipalities'].keys():
            municipality_properties = extract_properties(results[province]['municipalities'][municipality]['url'])
            results[province]['municipalities'][municipality]['properties'] = municipality_properties
    print(results)
