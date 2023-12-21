
import logging
from autologging import logged, TRACE, traced

from property_scraper import DEFAULT_HTML_PARSER, IMMOBILIARE_URL_ROOTNAME, add_classes
from property_scraper.immobiliare_property import ImmobiliareProperty
from property_scraper.page import Page


@logged(logging.getLogger("property_scraper"))
class ImmobiliarePage(Page):
    
    URL_ROOTNAME = IMMOBILIARE_URL_ROOTNAME
    URL_ABSOLUTE_FLAG = True
    #SCRAPABLE_TAGS = ['div', 'a', 'span', 'button', 'ul', 'li']
    SCRAPABLE_CLASSES = {}
    #SCRAPABLE_HYPERLINK_CLASSES = [
    #    "in-card__title",
    #]
    SCRAPABLE_USELESS_CLASSES = [
        'in-realEstateListCard__referent', 
        'in-realEstateListCard__referent--image', 
        'in-saveRealEstateButton',
        'nd-ratio--standard',
    ]
    SCRAPABLE_CLASSES_WITH_DEFAULT_VALUE = {
    }
    RENAMED_COLUMNS = {
        'in-card__title_href': 'Hyperlink',
        'in-card__description_text': 'Title',
        'in-card__title_text': 'Address',
        'in-feat__item--main_text': 'Price',
        'in-realEstateListCard__features--main_text': 'Price Comment',
        #'propertyCard-link': 'Hyperlink',
        #'Floorplan',
        #'Pictures',
        #'Property Type',
        #'Number of Bedrooms',
        #'Number of Bathrooms',
        #'Description',
        #'Comment', 
        'in-realEstateCard_href': 'Agent Hyperlink',
        #'Agent Telephone Number',
        #'Agent Email',
        #'Saved'
    }
      
    def __init__(self, name:str=None):
        super(ImmobiliarePage, self).__init__()
        self.property = ImmobiliareProperty()
