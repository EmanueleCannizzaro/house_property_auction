# -*- coding: utf-8 -*-

import logging
import sys

from autologging import logged, traced
from datetime import datetime
from glob import glob
#import json
import os
import scrapy
from scrapy import Spider
from scrapy.loader import ItemLoader
#from scrapy.loader.processors import TakeFirst
from scrapy.selector import Selector
#from time import sleep
#from tqdm.auto import tqdm

from property_scraper import ROOT_FOLDER, get_latest_file_mtime
#from property_scraper import LOCALHOST_URL_ROOTNAME, PVP_URL_ROOTNAME, ROOT_FOLDER, get_filename_from_identifier, get_unique_filename
from property_scraper.licitor.items import LicitorPropertyItem, LicitorPropertyModel


@traced
@logged
class LicitorPropertySpider(Spider):
    '''
    In this modified code, after scraping the initial property listings, we follow the link of each property by making a new request using scrapy.Request(). The parse_property_details method is defined as the callback function for handling the property details page.

    Inside the parse_property_details method, we extract the property details using an XPath selector and join the extracted texts into a single string. The property details are then added to the existing loader using loader.add_value().

    Make sure to adjust the XPath selector for the property details based on the HTML structure of the property details page. The scraped property details will be added to the property_details field of the AuctionItem model.

    Feel free to customize the code further to suit your specific scraping needs and adapt it to the target website's HTML structure.
    '''

    name = 'licitor_property'
    WEBSITE = name.split('_')[0]
    
    allowed_domains = ['localhost:8000', 'www.licitor.com']
    
    ## Filter the list of files only to ones more recent than the output file
    ofilenames = glob(f'/home/data/property_scraper/demos/{name}_*.csv')
    ofilename_mtime = get_latest_file_mtime(ofilenames)
    
    filenames = glob(os.path.join(ROOT_FOLDER, WEBSITE, f'{WEBSITE}_property_*.html'))
    print(f"There are {len(filenames)} listed properties.")
    #print(filenames)
    #filenames = ['infoencheres_property_5052.html']
    #start_urls = [f'http://localhost:8000/infoencheres/{os.path.basename(x)}' for x in filenames[:1]]
    #start_urls = [f'http://localhost:8000/infoencheres/{os.path.basename(x)}' for x in filenames if (os.path.getctime(x) > ofilename_mtime)]
    start_urls = []
    for x in filenames :
        if os.path.getctime(x) > ofilename_mtime:
            start_urls.append(f'http://localhost:8000/{WEBSITE}/{os.path.basename(x)}')
    print(f"There are {len(start_urls)} new properties to scrape.")
    
    search_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
    is_first_page = True

    def parse(self, response):
        selector = Selector(response)
        self.property = LicitorPropertyItem()
        property_loader = ItemLoader(item=self.property, selector=selector)
        for key in self.property.items['css'].keys():
            if isinstance(self.property.items['css'][key], list):
                for item in self.property.items['css'][key]:
                    property_loader.add_css(key, item)
            else:
                property_loader.add_css(key, self.property.items['css'][key])
        for key in self.property.items['xpath'].keys():
            if isinstance(self.property.items['xpath'][key], list):
                for item in self.property.items['xpath'][key]:
                    property_loader.add_xpath(key, item)
            else:
                property_loader.add_xpath(key, self.property.items['xpath'][key])
        
        property_data = property_loader.load_item()
        #property_model = InfoEncheresPropertyModel(**property_data)
        yield property_data

'''
    def parse_property_details(self, response):
        loader = response.meta['loader']
        property_details = response.xpath('//div[contains(@class, "property-details")]//text()').getall()
        property_details = ' '.join(property_details).strip()

        loader.add_value('property_details', property_details)

        item = loader.load_item()
        yield item
'''

'''
https://www.info-encheres.com/107230-d-vente-encheres-immobilieres-immeuble-pau-64-ref-5065.html

<div class="avocat">
    
    	<div class="icone"><img src="pix/avocat.png"></div>
    	<div class="nom"><b>Selarl MALTERRE-CHAUVELIER</b><div class="tel">05.59.11.33.33</div></div>
    	<div class="fiche"><a href="30-vente-encheres-immobilieres-partenaires-annonceurs-selarl-malterre-chauvelier.html"><img src="pix/fiche.png">&nbsp;&nbsp;Voir la fiche</a></div>
    	        <div class="clear"></div>
        
    </div>
    
    <div class="gauche">
	<table cellpadding="0" cellspacing="0">
    <tbody><tr>
    	<td valign="top" width="110px"><b>Référence : </b></td>
    	<td valign="top">5065</td>
    </tr>
    <tr>
    	<td valign="top" width="110px"><b>Nature du bien : </b></td>
    	<td valign="top">Immeuble</td>
    </tr>
    <tr>
    	<td valign="top"><b>Adresse : </b></td>
    	<td valign="top">46 rue de Liège<br>64000 PAU</td>
    </tr>
        <tr>
    	<td valign="top"><b>Mise à prix </b></td>
    	<td valign="top">192 000 € Frais en sus.</td>
    </tr>
    <tr>
    	<td valign="top"><b>Vente le : </b></td>
    	<td valign="top">16/06/2023</td>
    </tr>
    <tr>
    	<td valign="top"><b>Au TGI de : </b></td>
    	<td valign="top">Pau<br>Site des Halles - Place Marguerite Laborde - 64000 Pau</td>
    </tr>
    <tr>
    	<td valign="top"><b>Date de visite : </b></td>
    	<td valign="top"></td>
    </tr>
    </tbody></table>
</div>

<div class="droite">

	<a href="#inline1" title="Adresse : 4 Chemin de La Peyrière 31240 SAINT JEAN"><div class="button_detail num1">
    	Géolocalisation
        <div class="icone ico1"><img src="pix/geoloc.png"></div>
    </div></a>

	<a id="fancybox-manual-c" href="javascript:;"><div class="button_detail num2">
    	Photos
        <div class="icone ico2"><img src="pix/photo.png"></div>
    </div></a>
	

	    
		<a href="https://www.info-encheres.com/upload/vRQQCAHIER_DES_CONDITIONS_DE_VENTE.pdf" target="_blank"><div class="button_detail num3">
    	cahier des <br>
		conditions de la vente
        <div class="icone ico3"><img src="pix/telec.png"></div>
    </div></a>
	    
        <div class="button_detail num4">
    	<span>Annexes au cahier des <br>
		conditions de la vente</span>
        <div class="icone ico3"><img src="pix/telec.png"></div>
    
    
            	<a href="https://www.info-encheres.com/upload/7fUIPVD.pdf" target="_blank" style="color:#fff">•  Procès-verbal descriptif</a><br>
                	<a href="https://www.info-encheres.com/upload/ru000.pdf" target="_blank" style="color:#fff">•  Renseignements d'urbanisme</a><br>
                	<a href="https://www.info-encheres.com/upload/MUEwCADASTRE.pdf" target="_blank" style="color:#fff">•  Plan cadastral</a><br>
                	<a href="https://www.info-encheres.com/upload/cgG3RHF.pdf" target="_blank" style="color:#fff">•  Etat hypothécaire</a><br>
        </div>    
        
	    
</div>    
    

<div class="cadre">
	<div class="titre" style="font-size:17px;">Description</div>
    <div class="int2" style="overflow:auto; height:250px;"><p align="LEFT"><strong><span style="color: #000000;"><span style="font-family: Arial, sans-serif;"><span style="font-size: small;"><span>VENTE AUX ENCHERES</span></span></span></span></strong></p>
<p align="LEFT"><span style="color: #000000;">&nbsp;</span></p>
<p align="LEFT"><span style="color: #000000;"><span style="font-family: Arial, sans-serif;"><span style="font-size: small;">A PAU (Pyrénées Atlantiques) 46 rue de Liège un immeuble portant les numéros 46 et 48 rue de Liège, édifié sur sous sol, rez-de-chaussée, et trois étages. <br>Parkings aériens<br><br></span></span></span></p>
<p align="LEFT"><span style="color: #000000;"><span style="font-family: Arial, sans-serif;"><span style="font-size: small;">Terrain en nature de sol et cour. <br>Le tout cadastré section CK N° 87 au 48 rue de Liège pour une contenance de 1 a 50 ca et N° 88 au 46 rue de Liège pour une contenance de 5 a 80 ca d’une contenance totale de 7 a 30 ca</span></span></span></p>
<p align="LEFT"><span style="color: #000000;">&nbsp;</span></p>
<p align="LEFT"><span style="color: #000000;"><span style="font-family: Arial, sans-serif;"><span style="font-size: small;">Le cahier des conditions de la vente peut être consulté au greffe du Juge de l’Exécution du Tribunal Judiciaire de PAU,&nbsp;ou au cabinet de la SELARL MALTERRE CHAUVELIER représentée par Maître MALTERRE, avocat poursuivant&nbsp;sous le numéro 22/00033 .</span></span></span></p>
<p align="LEFT"><span style="color: #000000;">&nbsp;</span></p>
<p align="LEFT"><span style="color: #000000;"><span style="font-family: Arial, sans-serif;"><span style="font-size: small;">Pour participer aux enchères, l’adjudicataire devra remettre à son conseil une consignation de garantie de 19.200 €<br><br></span></span></span></p>
<p align="LEFT"><span style="color: #000000;"><span style="font-family: Arial, sans-serif;"><span style="font-size: small;">Le bien est pour partie loué dans sa partie garage, la partie à usage d’habitation est libre de toute occupation.</span></span></span></p>
<p align="LEFT"><span style="color: #000000;">&nbsp;</span></p>
<p align="LEFT"><strong><span style="color: #000000;"><span style="font-family: Arial, sans-serif;"><span style="font-size: small;"><span>POUR TOUS RENSEIGNEMENTS&nbsp;:</span></span></span></span></strong></p>
<p align="LEFT"><span style="color: #000000;">&nbsp;</span></p>
<p align="LEFT"><span style="color: #000000;"><span style="font-family: Arial, sans-serif;"><span style="font-size: small;">- à la SELARL MALTERRE CHAUVELIER représentée par Maître MALTERRE, Avocat poursuivant<br><br></span></span></span></p>
<p align="LEFT"><span style="color: #000000;"><span style="font-family: Arial, sans-serif;"><span style="font-size: small;">- à PAU – 18 Rue des Cordeliers Tél&nbsp;: 05.59.11.33.33<br><br></span></span></span><span style="font-family: Arial, sans-serif; font-size: small;">- ou aux autres avocats inscrits au barreau de PAU</span></p>
<p align="LEFT"><span style="color: #000000;"><span style="font-family: Arial, sans-serif;"><span style="font-size: small;"><br>Les audiences de vente débutent à 9h30</span></span></span></p>
<p align="LEFT">&nbsp;</p></div>
	<div class="clear"></div>
</div>

	
	

	    
	    
        
        
	    
</div>



'''


'''
https://www.info-encheres.com/30-vente-encheres-immobilieres-partenaires-annonceurs-selarl-malterre-chauvelier.html

<div class="avocat">
    
    	<div class="icone"><img src="pix/avocat.png"></div>
    	<div class="nom"><b>Selarl MALTERRE-CHAUVELIER</b><div class="tel"></div></div>
    	        <div class="clear"></div>
        
    </div>
    
<div class="gauche">
	<table cellpadding="0" cellspacing="0">
    <tbody><tr>
    	<td valign="top" width="220px"><b>Nom de l'avocat praticien des procédures et de l'exécution : </b></td>
    	<td valign="top">Malterre Robert</td>
    </tr>
        <tr>
    	<td valign="top"><b>Adresse cabinet ou SCP... : </b></td>
    	<td valign="top">18 rue des Cordeliers<br>64000 Pau</td>
    </tr>
    <tr>
    	<td valign="top"><b>Email de contact : </b></td>
    	<td valign="top">robert.malterre@wanadoo.fr </td>
    </tr>
       <tr>
    	<td valign="top"><b>Tél. standard : </b></td>
    	<td valign="top">05 59 11 33 33</td>
    </tr>
        <tr>
    	<td valign="top"><b>Fax : </b></td>
    	<td valign="top">05 59 11 33 35</td>
    </tr>
        
    </tbody></table>
</div>

    <div class="droite">


	
	<a href="#inline1" title="Adresse : 18 rue des Cordeliers 64000 Pau"><div class="button_detail num1">
    	Géolocalisation
        <div class="icone ico1"><img src="pix/geoloc.png"></div>
    </div></a>

	<div class="cadre">
	<div class="titre" style="font-size:17px;">Description</div>
    <div class="int2" style="overflow:auto; height:250px;"><span style="text-decoration: underline;"><span style="color: #da249c; text-decoration: underline;">Maître Robert Malterre :</span></span> <br>- Droit Social <br>- Mesures d'Exécution</div>
	<div class="clear"></div>
</div>



	
    
</div>

'''


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.settings import Settings
    from scrapy.utils.log import configure_logging
    
    #logging.disable(logging.CRITICAL)
    configure_logging()
    
    # Load the settings file
    settings = Settings()
    settings_module_path = 'property_scraper.licitor.settings'
    # Replace with your actual settings module path
    settings.setmodule(settings_module_path)

    # Create a crawler process with the loaded settings
    process = CrawlerProcess(settings)

    # Add your spider(s) to the crawler process
    process.crawl(LicitorPropertySpider)

    # Start the crawler process    
    process.start()
