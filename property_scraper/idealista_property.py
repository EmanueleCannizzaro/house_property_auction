
import logging
from autologging import logged, TRACE, traced

from bs4 import BeautifulSoup
from datetime import datetime
from lxml import etree, html
import pandas as pd
import re
from tqdm import tqdm 

from property_scraper import DEFAULT_HTML_PARSER, RIGHTMOVE_URL_ROOTNAME
from property_scraper.property import Property


class IdealistaProperty(Property):
  
    def __init__(self, name:str=None):
        super(IdealistaProperty, self).__init__()
