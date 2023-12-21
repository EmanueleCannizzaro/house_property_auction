import logging
import sys
 
from autologging import logged, TRACE, traced
 

from babel.numbers import format_currency
from bs4 import BeautifulSoup
from bs4.element import Tag
from datetime import datetime
import functools
from langchain.callbacks import get_openai_callback
import os
from random import randint
import re
import requests
import sentry_sdk
from time import sleep
from urllib.parse import parse_qs, urlparse


logging.basicConfig(filename='property_scraper.log', encoding='utf-8', level=logging.DEBUG)
logging.debug('This message should go to the log file')
logging.info('So should this')
logging.warning('And this, too')
logging.error('And non-ASCII stuff, too, like Øresund and Malmö')

MIN_WAITING_TIME = 1
MAX_WAITING_TIME = 5
MAX_TIMEOUT = 20

DEFAULT_HTML_PARSER = 'bs4'

DEFAULT_GEOCODE_ENGINE = 'googlemaps'

DRIVER_PATH = os.path.join(os.path.expanduser('~'), 'bin', 'chromedriver', '117.0.5938.92', 'chromedriver')
# 114.0.5735.90
GENERAL_PAUSE_TIME = 2
SCROLL_PAUSE_TIME = 2

SCRAPENINJA_URL_ROOTNAME = 'https://scrapeninja.p.rapidapi.com/scrape'
# 'https://scrapeninja.p.rapidapi.com/scrape-js'

ASTAGIUDIZIARIA_URL_ROOTNAME = "https://www.astagiudiziaria.com"
ASTEGIUDIZIARIE_URL_ROOTNAME = "https://www.astegiudiziarie.it"
#IDEALISTA_URL_ROOTNAME = "https://www.idealista.it"
#IMMOBILIARE_URL_ROOTNAME = "https://www.immobiliare.it"
INFOENCHERES_URL_ROOTNAME = "https://www.info-encheres.com"
LICITOR_URL_ROOTNAME = "https://www.licitor.com"
PVP_URL_ROOTNAME = "https://pvp.giustizia.it"
RECROWD_URL_ROOTNAME = "https://www.recrowd.com"
RIGHTMOVE_URL_ROOTNAME = "https://www.rightmove.co.uk"

LOCALHOST_URL_ROOTNAME = "http://localhost"
ROOT_FOLDER = '/home/git/property_scraper/demos/downloads'

PLUGINS = dict()

def register(func):
    """Register a function as a plug-in"""
    PLUGINS[func.__name__] = func
    return func

#@register


def accountant(func):
    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        # Do something before
        with get_openai_callback() as cb:
            value = func(*args, **kwargs)
            # Do something after
            print(f"Finished {func.__name__!r}")
            print(cb)
            return value
    return wrapper_decorator

#@accountant

def timer(func):
    """Print the runtime of the decorated function"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()    # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()      # 2
        run_time = end_time - start_time    # 3
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value
    return wrapper_timer

@timer
def waste_some_time(num_times):
    for _ in range(num_times):
        sum([i**2 for i in range(10000)])

def sleep_randomly(a:int=MIN_WAITING_TIME, b:int=MAX_WAITING_TIME):
    waiting_time = randint(a, b)
    sleep(waiting_time)

def add_classes(s:set, tag, exclude:list):
    if hasattr(tag, 'attrs'):
        key = 'class'
        if key in tag.attrs.keys():
            t = tag.attrs[key]
            for x in t:
                if x and (x not in exclude):    
                    s.add(x)

def remove_currency(value:str):
    return value.replace('€', '').strip()

def remove_whitespace(value):
    return value.strip()
                    
def remove_duplicated_whitespaces(s:str):
    if isinstance(s, str): 
        _s_wo_duplicated_spaces = re.sub("\s\s+", " ", s.strip())
        return _s_wo_duplicated_spaces
    elif isinstance(s, list): 
        _s_wo_duplicated_spaces = [re.sub("\s\s+", " ", x.strip()) for x in s]
        return _s_wo_duplicated_spaces
    else:
        return s

def get_unique_filename(basename:str, now=None):
    if now is None:
        now = datetime.now().strftime("%Y%m%d%H%M%S")
    rootname, extension = os.path.splitext(basename)
    ix = 0
    while True:
        filename = f'{rootname}_{now}_{ix:06}{extension}'
        if not os.path.exists(filename):
            break
        ix += 1
    return filename

def get_parameters(url:str):
    parsed_url = urlparse(url)
    _parameters = parse_qs(parsed_url.query)
    return _parameters

def get_filename_from_identifier(url:str, keys:list, root:str):
    parameters = get_parameters(url)
    #print(parameters)
    filename = root
    for key in keys:
        if key in parameters.keys():
            filename += f'_{parameters[key][0]}'
    filename += '.html'
    return filename

def get_basename(url:str, keys:list, root:str):
    filename = os.path.join(root, os.path.basename(url))
    return filename

def to_currency(s, currency="EUR", locale="it_IT"):
    # To be fixed as it generate an error: decimal.InvalidOperation: [<class 'decimal.ConversionSyntax'>]    
    if isinstance(s, str): 
        _s_to_currency = s.replace('€', '') #format_currency(s, currency=currency, locale=locale)
        return _s_to_currency
    elif isinstance(s, list): 
        _s_to_currency = [x.replace('€', '') for x in s] #[format_currency(x, currency=currency, locale=locale) for x in s]
        return _s_to_currency
    else:
        return s
    
def convert_hyperlink_rel2global(body:str, root:str):
    if root.endswith('/'):
        root = root[:-1]
    soup = BeautifulSoup(body, 'html.parser')
    for link in soup.findAll('link', {"href": True}):
        link['href'] = link['href'].strip()
        if link['href'].startswith('/'):
            link['href'] = f"{root}{link['href']}"
    for a in soup.findAll('a', {"href": True}):
        a['href'] = a['href'].strip()
        if a['href'].startswith('/'):
            print(a['href'])
            a['href'] = f"{root}{a['href']}"
            print(a['href'])
    for img in soup.findAll('img', {"src": True}):
        img['src'] = img['src'].strip()
        if img['src'].startswith('/'):
            img['src'] = f"{root}{img['src']}"
    for script in soup.find_all('script', {"src": True}):
        script['src'] = script['src'].strip()
        if script['src'].startswith('/'):
            script['src'] = f"{root}{script['src']}"
    for option in soup.findAll('option', {"value": True}):
        option['value'] = option['value'].strip()
        if option['value'].startswith('/'):
            option['value'] = f"{root}{option['value']}"
    return soup

def replace_broken_hyperlink(body:str, old:str, new:str, prefix_only:bool=False):
    soup = BeautifulSoup(body, 'html.parser')
    elements = {
        'link': "href",
        'a': "href",
        'img': "src",
        'script': "src",
        'option': "value"
    }
    for key in elements.keys():
        for link in soup.findAll(key, {elements[key]: True}):
            url = link[elements[key]].strip()
            if prefix_only and url.startswith(old):
                link[elements[key]] = url[:len(old)].replace(old, new) + url[len(old):]
                #print(url, link['href'])
            elif not prefix_only and url.contains(old):
                link[elements[key]] = url.replace(old, new)
                #print(url, link['href'])
    '''
    for a in soup.findAll('a', {"href": True}):
        url = a['href'].strip()
        if prefix_only and url.startswith(old):
            a['href'] = url[:len(old)].replace(old, new) + url[len(old):]
            #print(url, a['href'])
        elif not prefix_only and url.contains(old):
            a['href'] = url.replace(old, new)
            #print(url, a['href'])
    for img in soup.findAll('img', {"src": True}):
        img['src'] = img['src'].strip()
        if prefix_only and img['src'].startswith(old):
            img['src'] = img['src'][:len(old)].replace(old, new) + img['src'][len(old):]
        elif not prefix_only and a['href'].contains(old):
            img['src'] = img['src'].replace(old, new)
    for script in soup.find_all('script', {"src": True}):
        script['src'] = script['src'].strip()
        if prefix_only and script['src'].startswith(old):
            script['src'] = script['src'][:len(old)].replace(old, new) + script['src'][len(old):]
        elif not prefix_only and script['src'].contains(old):
            script['src'] = script['src'].replace(old, new)
    for option in soup.findAll('option', {"value": True}):
        option['value'] = option['value'].strip()
        if prefix_only and option['value'].startswith(old):
            option['value'] = option['value'][:len(old)].replace(old, new) + option['value'][len(old):]
        elif not prefix_only and option['value'].contains(old):
            option['value'] = option['value'].replace(old, new)
    '''
    return soup

@traced
@logged
def replace_href_global2localhost(body:str, filters:dict, keys:list, root:str):
    soup = BeautifulSoup(body, 'html.parser')
    for a in soup.findAll('a', {"href":True}):
        isparameterfound = False
        for filter in filters.keys():
            a['href'] = a['href'].strip()
            if a['href'].startswith(filter):
                parameters = get_parameters(a['href'])
                for key in keys:
                    if (key in parameters.keys()) or (key is None):
                        #print(f'{key} -> {parameters.keys()}')
                        isparameterfound = True
                        break
                if isparameterfound:
                    hyperlink_old = a['href']
                    hyperlink_new = filters[filter](a['href'], keys, root)
                    # get_filename_from_identifier(url:str, keys:list, root:str)                    
                    #r = requests.get(hyperlink_new)
                    #print(r.status_code)
                    # Requests to scrape lots of pages eventually get status 400, so:
                    #if r.status_code == 200:
                    a['href'] = hyperlink_new
                    #print(f"{hyperlink_old} -> {a['href']}")
                    replace_href_global2localhost._log.info(f"{hyperlink_old} -> {a['href']}")
                    #else:
                    #    replace_href_global2localhost._log.info(f"Skipping {hyperlink_new} because it is not available yet!")
    return soup

@traced
@logged
def fix_hyperlinks(filename:str, filters:dict, keys:list, root:str, url_rootname:str, prefixes:dict, overwrite:bool=True, subfolder:str='99_backup'):
    if not overwrite:
        rootname, extension = os.path.splitext(filename)
        dirname = os.path.join(os.path.dirname(filename), subfolder)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        ofilename = os.path.join(dirname, f'{os.path.basename(rootname)}{extension}')
    else:
        ofilename = filename
        
    fix_hyperlinks._log.info(filename)
    with open(filename, 'r') as f:
        content = f.read()
    soup = convert_hyperlink_rel2global(content, url_rootname)

    for key in prefixes.keys():
        soup = replace_broken_hyperlink(soup.prettify(), key, prefixes[key], prefix_only=True)
    
    soup = replace_href_global2localhost(soup.prettify(), filters, keys, root)
    with open(ofilename, 'wb') as f:
        f.write(soup.prettify("utf-8"))
   
@traced
@logged
def get_latest_file_mtime(filenames:list):
    mtime = 0
    ctime = 0
    for filename in filenames:
        _mtime = os.path.getmtime(filename)
        _ctime = os.path.getctime(filename)
        if _mtime > mtime:
            mtime = _mtime
        if _ctime > ctime:
            ctime = _ctime
    print(f"last modified: \t{ctime}")
    print(f"created: \t{mtime}")
    return mtime #, ofilename_ctime

