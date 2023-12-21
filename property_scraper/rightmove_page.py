
import logging
from autologging import logged, TRACE, traced

from property_scraper import DEFAULT_HTML_PARSER, RIGHTMOVE_URL_ROOTNAME, add_classes
from property_scraper.page import Page
from property_scraper.rightmove_property import RightmoveProperty


@logged(logging.getLogger("property_scraper"))
class RightmovePage(Page):
    
    URL_ROOTNAME = RIGHTMOVE_URL_ROOTNAME
    URL_ABSOLUTE_FLAG = False
    #SCRAPABLE_TAGS = ["h2", "div", "address", "span"]
    SCRAPABLE_CLASSES = {}
    #SCRAPABLE_HYPERLINK_CLASSES = [
    #    "propertyCard-details", 
    #    #"propertyCard-contactsItem"
    #]
    SCRAPABLE_USELESS_CLASSES = [
        'aspect-3x2', 
        'propertyCard-additionalImg', 
        'propertyCard-additionalImg--gridLayout', 
        'propertyCard-contactButton', 
        'propertyCard-cutout', 
        'propertyCard-fadeOut',
        'propertyCard--featured', 
        'propertyCard-images', 
        'propertyCard-keywordTag', 
        'propertyCard-main-img-mask', 
        'propertyCard-priceContacts', 
        #'propertyCard-contactsItem', 
        'info-lozenge', 'is-hidden', 'ksc_info-lozenge',
        'property-hide-button-square', 
        'propertyCard-branchLogo', 
        'propertyCard-img', 
        'propertyCard--premium',
        'propertyCard-headerLabel', 
        'propertyCard-moreInfoFeaturedTitle', 
        'propertyCard-contactsItem--save', 
        'propertyCard-keywordTags', 
        'propertyCard-main-img', 
        'property-hide-button', 
        'no-svg-heart-unsaved', 
        'no-svg-envelope', 
        'no-svg-heart-saved', 
        'no-svg-virtualtour', 
        'propertyCard-save--unsaved', 
        'no-svg-camera', 
        'propertyCard-contactButtonIcon', 
        'propertyCard-contactsAddedOrReduced', 
        'camera', 
        'no-svg-close', 
        'propertyCard-awaitingImage', 
        'propertyCard-tagLink-chevron', 
        'keyword', 
        'propertyCard-carousel', 
        'propertyCard-branchSummary-addedOrReduced', 
        'propertyCard-save--saved', 
        'propertyCard-save', 
        'no-svg-phone', 
        'property-hide-button-x', 
        'propertyCard-tagTitle--display-status', 
        'no-svg-awaiting-image', 
        'propertyCard-contactButtonIcon--phone', 
        'propertyCard-contactButtonIcon--envelope', 
        'no-svg-floorplan', 
        'propertyCard-moreInfoIcon', 
        'propertyCard-priceQualifier'
    ]
    SCRAPABLE_CLASSES_WITH_DEFAULT_VALUE = {
        'propertyCard-title': 'Property', 
        'propertyCard-details': URL_ROOTNAME, 
        #"propertyCard-details": 'Property',
        'propertyCard-keywords': '', 
        'propertyCard-wrapper': '', 
        'propertyCard-keywordsContainer': '', 
        'propertyCard-detailsFooter': '', 
        'propertyCard': '', 
        'propertyCard-contacts': '', 
        'propertyCard-section': '', 
        'propertyCard-content': '', 
        'propertyCard-keywordsFeaturedProperty': '', 
        'propertyCard-tag': '', 
        'propertyCard-tagTitle': '', 
        'propertyCard-contactsItemDetails': '', 
        'propertyCard-contactsItemDetails--email': '', 
        'propertyCard-tagLink': URL_ROOTNAME, 
        'propertyCard-contactsPhoneRates': '',
        "propertyCard-link": URL_ROOTNAME,
        "propertyCard-contactsItem": URL_ROOTNAME
    }
    RENAMED_COLUMNS = {
        'propertyCard-details_href': 'Hyperlink',
        'propertyCard-title_text': 'Title',
        'propertyCard-address_text': 'Address',
        'propertyCard-price_text': 'Price',
        'propertyCard-priceValue_text': 'Price Comment',
        'propertyCard-link_href': 'Hyperlink',
        #'Floorplan',
        #'Pictures',
        #'Property Type',
        #'Number of Bedrooms',
        #'Number of Bathrooms',
        #'Description',
        #'Comment', 
        'propertyCard-contactsItem_href': 'Agent Hyperlink',
        #'Agent Telephone Number',
        #'Agent Email',
        #'Saved'
    }

    def __init__(self, name:str=None):
        super(RightmovePage, self).__init__()
