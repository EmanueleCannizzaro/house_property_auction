# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from datetime import datetime, date
import re
#import scrapy
from pydantic import BaseModel, validator
from scrapy.item import Item, Field
#from scrapy.loader.processors import  MapCompose, TakeFirst
from itemloaders.processors import Join, MapCompose, TakeFirst
from typing import List, Optional
from urllib.parse import urljoin
from w3lib.html import remove_tags

from property_scraper import LICITOR_URL_ROOTNAME


def create_url(url):
    return urljoin(INFOENCHERES_URL_ROOTNAME, url)
    
def strip(text):
    s = text.strip()
    s = s.replace('\n', '').replace('\r', '')
    s = re.sub("\s\s+", " ", s)
    return s


class LicitorSearchPropertyItem(Item):
    items = {
        'css': {
        },
        'xpath': {
            'url_title': '//section[@id="courts"]/div[@class="Column"]/ul/li/a/text()',
            'url': '//section[@id="courts"]/div[@class="Column"]/ul/li/a/@href',
            'url_extra': '//section[@id="courts"]/div[@class="Column"]/ul/li/a/span/text()',

            'url2': '//div[@class="Content ResultContent"]/div[@class="Container"]/article[@class="Traversing"]/div[@id="traversing-hearings"]/ul/li/a/@href',

            '1': '//article[@class="LegalAd"]/div[@class="Container"]/div[@class="AdNavBlock"].text()',

            '2': '//div[@class="AdContent"]/@id',
            'date_published_unformatted': '//div[@class="AdContent"]/p[@class="PublishingDate"]/text()',

            'date_published': '//div[@class="AdContent"]/p[@class="PublishingDate"]/time/@datetime',
            'number': '//div[@class="AdContent"]/p[@class="Number"]/text()',
            'tribunal': '//div[@class="AdContent"]/p[@class="Court"]/text()',
            'type': '//div[@class="AdContent"]/p[@class="Type"]/text()',
            'auction_date': '//div[@class="AdContent"]/p[@class="Date"]/time/text()',
            'auction_date_unformatted': '//div[@class="AdContent"]/p[@class="Date"]/time/@datetime',

            'title': '//section[@class="AddressBlock"]/div[@class="Lot"]/div[@class="FirstSousLot SousLot"]/h2/text()',
            'description': '//section[@class="AddressBlock"]/div[@class="Lot"]/div[@class="FirstSousLot SousLot"]/p/text()',

            'full_titles': '//section[@class="AddressBlock"]/div[@class="Lot"]/div[@class="SousLot"]/h2/text()',
            'full_descriptions': '//section[@class="AddressBlock"]/div[@class="Lot"]/div[@class="SousLot"]/p/text()',

            'outcome': '//section[@class="AddressBlock"]/div[@class="Lot"]/h3/text()',
            'price': '//section[@class="AddressBlock"]/div[@class="Lot"]/h4/text()',
            'city': '//section[@class="AddressBlock"]/div[@class="Location"]/p[class="City"]/text()',
            'street': '//section[@class="AddressBlock"]/div[@class="Location"]/p[class="Street"]/text()',
            'map': '//section[@class="AddressBlock"]/div[@class="Location"]/p[class="Map"]/@href',

            'lawyer': '//div[@class="Trusts"]/div@class="Trust"]/h3/text()',
            'lawyer_address': '//div[@class="Trusts"]/div@class="Trust"]/p/text()',
            'lawyer_website': '//div[@class="Trusts"]/div@class="Trust"]/p/a/@href',

            'next': '//a[@class="NextAd AdNav"]/@href',
            #"/annonce/09/50/53/vente-aux-encheres/une-piece/paris-9eme/paris/095053.html"
        }
    }
    

    #div class="Container"
    #span class="AdNumber">1</span>
    #span class="AdTotal">274</span>
    
    #div class="AdContent"
    #p class="Number">95128
    
    '''
    <div class="Container">
		<ul class="AdResults">
		<li>
		<a class="Ad First Loaded" href="/annonce/09/51/28/vente-aux-encheres/des-combles-amenages-en-appartement/firminy/loire/095128.html" title="Des combles aménagés en appartement, Firminy, Loire">
			<p class="Location">
				<span class="Number">42</span>
				<span class="City">Firminy</span>
			</p>
			<p class="Description">
				<span class="Name">Des combles aménagés en appartement</span>
				<span class="Text">d'une surface de 92,50 m² dont 66,90 m² Loi Carrez, au 4ème étage du bâtiment A, [...]</span>
			</p>
			<div class="Footer">
				<div class="Price">
										<p class="Initial">Mise à prix : <span class="PriceNumber">30 000 €</span></p>
									</div>
			</div>
		</a>
		<p class="PublishingDate"><span>Jeudi 13 avril</span></p>

	</li>
		<li>
		<a class="Ad" href="/annonce/09/51/29/vente-aux-encheres/un-chalet/saint-maurice-en-gourgois/loire/095129.html" title="Un chalet, Saint-Maurice-en-Gourgois, Loire">
			<p class="Location">
				<span class="Number">42</span>
				<span class="City" title="Saint-Maurice-en-Gourgois">Saint-Maurice-en-Gour…</span>
			</p>
			<p class="Description">
				<span class="Name">Un chalet</span>
				<span class="Text">de 57,95 m², comprenant : Au rez-de-chaussée : pièce à usage de séjour, cuisine, wc À l'étage : [...]</span>
			</p>
			<div class="Footer">
				<div class="Price">
										<p class="Initial">Mise à prix : <span class="PriceNumber">60 000 €</span></p>
									</div>
			</div>
		</a>
		<p class="PublishingDate"></p>

	</li>
		<li>
		<a class="Ad" href="/annonce/09/53/18/vente-aux-encheres/un-appartement/saint-etienne/loire/095318.html" title="Un appartement, Saint-Étienne, Loire">
			<p class="Location">
				<span class="Number">42</span>
				<span class="City">Saint-Étienne</span>
			</p>
			<p class="Description">
				<span class="Name">Un appartement</span>
				<span class="Text">de 58,23 m², dans le bâtiment I, au 7ème étage, comprenant : trois pièces, cuisine avec hall, salle [...]</span>
			</p>
			<div class="Footer">
				<div class="Price">
										<p class="Initial">Mise à prix : <span class="PriceNumber">15 000 €</span></p>
									</div>
			</div>
		</a>
		<p class="PublishingDate"><span>Mercredi 26 avril</span></p>

	</li>
		<li>
		<a class="Ad" href="/annonce/09/54/30/vente-aux-encheres/une-maison-d-habitation-contemporaine-en-cours-d-achevement/renaison/loire/095430.html" title="Une maison d'habitation contemporaine en cours d'achèvement, Renaison, Loire">
			<p class="Location">
				<span class="Number">42</span>
				<span class="City">Renaison</span>
			</p>
			<p class="Description">
				<span class="Name">Une maison d'habitation contemporaine en cours d'achèvement</span>
				<span class="Text">sur une parcelle d'une superficie de 2.351 m², [...]</span>
			</p>
			<div class="Footer">
				<div class="Price">
										<p class="Initial">Mise à prix : <span class="PriceNumber">200 000 €</span></p>
									</div>
			</div>
		</a>
		<p class="PublishingDate"><span>Vendredi 5 mai</span></p>

	</li>
		<li>
		<a class="Ad" href="/annonce/09/54/32/vente-aux-encheres/un-appartement/rive-de-gier/loire/095432.html" title="Un appartement, Rive-de-Gier, Loire">
			<p class="Location">
				<span class="Number">42</span>
				<span class="City">Rive-de-Gier</span>
			</p>
			<p class="Description">
				<span class="Name">Un appartement</span>
				<span class="Text">de 45,55 m², au 1er étage, comprenant : séjour/cuisine, deux chambres, dégagement, salle d'eau, wc - [...]</span>
			</p>
			<div class="Footer">
				<div class="Price">
										<p class="Initial">Mise à prix : <span class="PriceNumber">20 058 €</span></p>
									</div>
			</div>
		</a>
		<p class="PublishingDate"></p>

	</li>
	</ul>
	</div>
    '''
    
    
    '''
    <div class="AdContent" id="ad-095128">
					<p class="PublishingDate">Annonce publiée le <time datetime="2023-04-13T00:00:00+02:00">13 avril 2023</time></p>

					<p class="Number">95128</p>

					<p class="Court">Tribunal Judiciaire de Saint Étienne						 (Loire)					</p>
					<p class="Type">Vente aux enchères publiques en un lot</p>
					<p class="Date"><time datetime="2023-06-02T14:00:00">vendredi 2 juin 2023 à 14h</time></p>
										<section class="AddressBlock">
												<div class="Lot">
							
														<div class="FirstSousLot SousLot">
								<h2>Des combles aménagés en appartement</h2>
																<p>d'une surface de 92,50 m² dont 66,90 m² Loi Carrez, au 4ème étage du bâtiment A, de type 3<br>Occupé</p>
															</div>
							
																							<h3>Mise à prix : 30 000 €</h3>
															
													</div>
						
						

						<div class="Location">
														<p class="City">Firminy															</p>
							
														<p class="Street">86, rue Jean Jaurès</p>
							
														<p class="Map">
                                <a href="https://maps.google.fr/maps?q=45.3877258,4.2856054&amp;z=13" class="Button" target="_blank">Afficher le plan</a>
                            </p>
							<div style="margin: 0 0 5px; padding: 0; text-align: center; font-size: 0.7em; color: #21282c;">(exactitude non garantie)</div>
							
														<p class="Visits">Visite sur place mercredi 17 mai 2023 de 9h à 10h</p>
							
													</div>
					</section>
					
					<div class="Trusts">
											<div class="Trust">
						
												<h3>Maître Romain Maymon, Avocat</h3>
						
												<p>4, rue Georges Teissier - 42000 Saint Étienne<br>Tél.: 04 77 25 97 97</p>
						
												<p><a href="mailto:maymon@maymon.fr">maymon@maymon.fr</a></p>
																		</div>
										</div>

															
					
															<p>
						</p><div class="Reference" style="float: left;">
							🔎︎ 13.987&nbsp;&nbsp;&nbsp;&nbsp;❤ 173						</div>
						<div class="Reference" style="float: right;">
															Annonce non-officielle - Contenu non certifié
													</div>
					<p></p>
									</div>
    '''
    
    #//a class="NextAd AdNav" href="/annonce/09/51/29/vente-aux-encheres/un-chalet/saint-maurice-en-gourgois/loire/095129.html" title="Consulter l'annonce suivante" style=""></a>
    #<a class="NextAd PageNav" href="/ventes-aux-encheres-immobilieres/sud-est-mediterrannee/prochaines-ventes.html?p=2" title="Consulter l'annonce suivante" style="display: none;"></a>
     
    

    url = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())


class LicitorSearchPropertyModel(BaseModel):
    title: str = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    description: str = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    price: str = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    location: str = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    end_date: str = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    image_url: str = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    auction_url: str = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    property_details: str = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())

'''
        
        data_elements = response.xpath('//div[contains(@class, "auction-card")]')
        for element in data_elements:
            loader = ItemLoader(item=AuctionItem(), selector=element)
            loader.default_output_processor = TakeFirst()

            loader.add_xpath('title', './/h2/text()')
            loader.add_xpath('description', './/div[contains(@class, "card-body")]/text()')
            loader.add_xpath('price', './/div[contains(@class, "price")]/text()')
            loader.add_xpath('location', './/div[contains(@class, "location")]/text()')
            loader.add_xpath('end_date', './/div[contains(@class, "end-date")]/text()')
            loader.add_xpath('image_url', './/img/@src')
            loader.add_value('auction_url', response.urljoin(element.xpath('.//a/@href').get()))

            property_url = response.urljoin(element.xpath('.//a/@href').get())
            yield scrapy.Request(property_url, callback=self.parse_property_details, meta={'loader': loader})

'''

class LicitorPropertyItem(Item):
    items = {
        'css': {
        },
        'xpath': {
            'lawyer': '//div[@class="avocat"]/div[@class="nom"]/b/text()', #SELARL DESARNAUTS-HORNY-ROBERT-DESPIERRES
            'lawyer_phone_number': '//div[@class="avocat"]/div[@class="nom"]/div[@class="tel"]/text()', # 05.32.09.49.45
            'lawyer_card': '//div[@class="fiche"]/a/href',
            'lawyer_website': '//div[@class="site"]/a/href',
            #1048-vente-encheres-immobilieres-partenaires-annonceurs-selarl-desarnauts-horny-robert-despierres-.html
            #'ref': '//div[@class="gauche"]/table/tbody/tr/td/b[contains(text(), "Référence :")]/parent::td/following-sibling::td/text()',
            'ref': '//tr/td/b[contains(text(), "Référence :")]/parent::td/following-sibling::td/text()',
            # 5097
            'property_type': '//tr/td/b[contains(text(), "Nature du bien :")]/parent::td/following-sibling::td/text()',
            # Appartement T5, cellier et deux parkings    
            'address': '//tr/td/b[contains(text(), "Adresse :")]/parent::td/following-sibling::td/text()',
            # 21 impasse Negreneys<br>31200  TOULOUSE
            'size': '//tr/td/b[contains(text(), "Superficie :")]/parent::td/following-sibling::td/text()',
            # 92.92 m²
            'price': '//tr/td/b[contains(text(), "Mise à prix")]/parent::td/following-sibling::td/text()',
            # 165 000 €
            'date_of_sale': '//tr/td/b[contains(text(), "Vente le :")]/parent::td/following-sibling::td/text()',
            # 29/06/2023
            'court': '//tr/td/b[contains(text(), "Au TGI de :")]/parent::td/following-sibling::td/text()',
            # Toulouse<br>2, Allées Jules Guesde - 31000 Toulouse</td>
            'date_of_visit': '//tr/td/b[contains(text(), "Date de visite :")]/parent::td/following-sibling::td/text()',
            # Sur les lieux, le 19 juin 2023 de 10h30 à 11h30
            #'address': '//div[@class="droite"]/a::title',
            'actual_sale_price': '//div[@class="droite"]/b[contains(text(), "Résultat")]/parent::div/text()',            
            'geo': '//div[@class="droite"]/a/div[@class="button_detail num1"][contains(text(), "Géolocalisation")]/text()',
			#'images': '//div[@class="droite"]/a/div[@class="button_detail num2"][contains(text(), "Photos")]/parent::a/following-sibling::a/text()',
            'image_urls': '//div[@class="button_detail num2"]/a[contains(@href, "/upload/")]/@href',
            #'files': [
            #],
            'file_urls': [
                '//div[@class="droite"]/a/div[@class="button_detail num3"]/parent::a[contains(@href, "/upload/")]/@href',
                '//div[@class="button_detail num4"]/a[contains(@href, "/upload/")]/@href',
            ],
            #'additional_files': 
            #'additional_file_urls': 
            'description': '//div[@class="cadre"]/div[@class="int2"]/descendant-or-self::*/text()',
        }
    }
    lawyer = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    lawyer_phone_number = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    lawyer_card = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    lawyer_website = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    ref = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    #town = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    #county = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    property_type = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    address = Field(input_processor=MapCompose(remove_tags, strip), output_processor=Join())
    size = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    price = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    date_of_sale = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    court = Field(input_processor=MapCompose(remove_tags, strip), output_processor=Join())
    date_of_visit = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    actual_sale_price = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    geo = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    images = Field(input_processor=MapCompose(remove_tags, strip))
    image_urls = Field(input_processor=MapCompose(remove_tags, strip))
    files = Field(input_processor=MapCompose(remove_tags, strip))
    file_urls = Field(input_processor=MapCompose(remove_tags, strip))
    #additional_file_titles = Field(input_processor=MapCompose(remove_tags, strip))
    #additional_file_urls = Field(input_processor=MapCompose(remove_tags, strip))    
    description = Field(input_processor=MapCompose(remove_tags, strip), output_processor=Join())


class LicitorPropertyModel(BaseModel):
    lawyer: str
    lawyer_phone_number: int
    lawyer_card: str
    lawyer_website: str
    ref: int
    property_type: str
    address: str
    size: float
    price: float
    date_of_sale: datetime
    court: str
    date_of_visit: datetime
    actual_sale_price: float
    geo: str
    images: Optional[List[str]]
    image_urls: Optional[List[str]]
    files: Optional[List[str]]
    file_urls: Optional[List[str]]
    #additional_file_titles: Optional[List[str]]
    #additional_file_urls: Optional[List[str]]
    description: str
    

class LicitorColumns():
    NAMES = {
        'ref': 'Référence',
        'url': 'Hyperlink',
        'town': 'Ville',
        'county': 'Département',
        'lawyer': 'Avocat',
        'lawyer_phone_number': "Numéro de Téléphone de l'Avocat",
        'lawyer_card': "Carte d'Avocat",
        'lawyer_website': "Site d'Avocat",
        'property_type': 'Nature du Bien',
        'address': 'Adresse',
        'size': 'Superficie',
        'price': 'Mise à Prix',
        'date_of_sale': 'Vente le',
        'court': 'Au TGI de',
        'date_of_visit': 'Date de Visite',
        'actual_sale_price': 'Résultat',
        'geo': 'Géolocalisation',
        'images': 'Images',
        'image_urls': 'URL des Images',
        'files': 'Dossiers',
        'file_urls': 'URL des Dossiers',
        #additional_file_titles: Optional[List[str]],
        #additional_file_urls: Optional[List[str]],
        'description': 'Description',
        #'': 'Délais pour formuler une surenchère'
    }