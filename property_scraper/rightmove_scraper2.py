
import logging
from autologging import logged, TRACE, traced

from property_scraper import DEFAULT_GEOCODE_ENGINE, DEFAULT_HTML_PARSER, RIGHTMOVE_URL_ROOTNAME
from property_scraper.rightmove_page import RightmovePage
from property_scraper.rightmove_property import RightmoveProperty
from property_scraper.scraper import Scraper

@logged(logging.getLogger("property_scraper"))
class RightmoveScraper(Scraper):
    
    URL_ROOTNAME = RIGHTMOVE_URL_ROOTNAME

    KEYS = [
        #'propertyType', 
        #'protocol', 
        'location', 
        'country', 
        'locationIdentifier', 
        'searchType', 'insId', 'radius', 'minPrice', 'maxPrice', 'minBedrooms', 'maxBedrooms', 'maxDaysSinceAdded', 
        'displayPropertyType', 
        '_includeSSTC', 'sortByPriceDescending', 'primaryDisplayPropertyType', 'secondaryDisplayPropertyType', 'oldDisplayPropertyType', 
        'oldPrimaryDisplayPropertyType', 'newHome', 'auction', 'index'
    ]
    
    # There are 24 results per page.
    NUMBER_OF_RESULTS_PER_PAGE = 24
    # Rightmove will return a maximum of 42 results pages
    MAXIMUM_NUMBER_OF_PAGES = 42
    #PROTOCOLS = ["http", "https"]
    PROPERTY_TYPES = ["property-to-rent", "property-for-sale", "new-homes-for-sale"]

    NUMBER_OF_RESULTS = {
        'tag' : 'span', 
        'attribute': 'class',
        'value': 'searchHeader-resultCount'
    }

    REGIONS = {
        'Bristol': '5E219'
    }
    
    '''

    yes_pls = [
        'underfloor',
        'stunning',
        'wooden floor',
        'balcony',
        'terrace',
        'loft'
    ]
    no_thx = [
        'groundfloor'
    ]
    STOP_PHRASES = [
        "views over the garden",
        "views over the rear garden", "views over the front garden",
        "views over rear garden", "views over front garden",
        "views across the gardens", "views onto the garden",
        "in need of updating", "in need of modernisation",
        "views over rear aspect", "views over front aspect",
        "views over the rear aspect", "views over the front aspect",
        "views over side aspect", "views over the side aspect",
        "1970s",  "bungalow", "bunaglow",
        "views to the front garden", "views to the rear garden"
    ]
    # "semi detached", "semi-detached", "semidetached",

    # Original scraper: stations found by looking at maps
    # Can include changes etc
    # Up to approximately 2h15
    # Parameters for the scraper: stations, radius etc.
    STATIONS = [
        {'Nantwich':6473}, 
        {'Chester':2024},
        {'Acton Bridge':68},
        {'Hartford':4295},
        {'Winsford':10172},
        {'Macclesfield':5930},
        {'Prestbury':7421},
        {'Holmes Chapel':4673},
        {'Sandbach':7946},
        {'Crewe':2423},
        {'Congleton':2288},
        {'Alsager':185},
        {'Nantwich':6473},{'Wrenbury':10331},
        {'Whitchurch (Salop)':10004},{'Kidsgrove':5114},
        {'Stoke-on-Trent':8771},{'Stone':8777},
        {'Ambergate':209},{'Willington':10112},
        {'Burton-on-Trent':1613},{'Stafford':8660},
        {'Rugeley Trent Valley':7856},{'Codsall':2231},
        {'Albrighton':125},{'Cosford':2357},
        {'Stroud':8858},{'Stonehouse':8795},
        {'Pershore':7184},{'Kingham':5156},
        {'Moreton-in-Marsh':6371}, {'Westbury':9920},
        {'Frome':3641}, {'Taunton':9056},
        {'Tiverton':9218}, {'Hamworthy':4211},
        {'Brockenhurst':1418}, {'Ashurst New Forest':389},
        {'Worcester': 10298}, {'Pershore': 7184},
        {'Hagley': 4109}, {'Evesham': 3323},
        {'Honeybourne': 4697}, {'Shipton': 8207},
        {'Ascott-under-Wychwood Station': 350}, {'Charlbury': 1952},
        {'Finstock': 3521},{'Combe': 2282},
        {'Bradford-on-avon': 1265}, {'Bedwyn': 788},
        {'Pewsey': 7211}, {'Westbury': 9920},
        {'Frome': 3641}, 
        {'Castle Cary': 1853},
        {'Tisbury': 9215}, {'Gillingham': 3755},
        {'Templecombe': 9080}, {'Salisbury': 7922},
        {'Warminster': 9620}, {'Dilton Marsh Rail': 2771},
        {'Avoncliff': 449}, {'Freshford': 3623},
        {'Melksham': 6140}, {'Yate': 10373},
        {'Cam & Dursley': 1691}, {'Kemble': 5009},
        {'Market Harborough': 6050}, {'Kettering': 5087},
        {'Corby': 15013}, {'Wellingborough': 9743},
        {'Banbury': 545}, {'Bicester North': 929},
        {'Princes Risborough': 7454}, {'Bicester Town': 932},
        {'Aylesbury': 458}, {'Amersham': 215},
        {'Long Buckby': 5816}, {'Theale': 9125},
        {'Aldermaston': 131}, {'Midgham': 6209},
        {'Thatcham': 9095}, {'Newbury': 6599},
        {'Kintbury': 5222}, {'Leamington Spa': 5444},
        {'Newbury Racecourse':  6596}, {'Newington': 6623}, 
        {'Hollingbourne': 4661}, {'Chilham': 2048}, 
        {'Wye': 10346}, {'Ham street': 4157}, 
        {'Appledore': 266}, {'Estchingham': 3305},
        {'Chippenham': 2069}
    ]
    '''


    def __init__(self, name:str=None):
        super(RightmoveScraper, self).__init__()
        self.page = RightmovePage()
        self.property = RightmoveProperty()

    def set_url(self, parameters:dict):        
        _url = f"{self.URL_ROOTNAME}/{parameters['propertyType']}/find.html?"
        count = 0
        for ix in range(len(self.KEYS)):
            key = self.KEYS[ix]
            if key in parameters.keys():
                if parameters[key]:
                    if count > 0:
                        _url += f"&{key}={parameters[key]}"
                    else:
                        _url += f"{key}={parameters[key]}"
                    count += 1
        return _url
    
    def read_parameters(self, filename:str):
        _parameters = super(ImmobiliareScraper, self).read_parameters(filename)
        self.location = _parameters["location"]
        self.country = _parameters["country"]
        self.property_type = _parameters["propertyType"]

        if hasattr(self, 'REGIONS'):
            self.region = self.REGIONS[_parameters['location']]
        return _parameters
    
    def get_next_search_page(self, ix):
        return f"{str(self.url)}&index={ix * self.NUMBER_OF_RESULTS_PER_PAGE}"
    
