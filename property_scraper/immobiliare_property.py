
import logging
from autologging import logged, TRACE, traced

from bs4 import BeautifulSoup
from datetime import datetime
from lxml import etree, html
import pandas as pd
import re
from tqdm import tqdm 

from property_scraper import DEFAULT_HTML_PARSER, IMMOBILIARE_URL_ROOTNAME
from property_scraper.property import Property


class ImmobiliareProperty(Property):

    URL_ROOTNAME = IMMOBILIARE_URL_ROOTNAME

    KEYWORDS = [
        "Contatta l'inserzionista",
        'Mi interessa questo immobile, vorrei avere maggiori informazioni',
        'Nome',
        'Email',
        'Telefono',
        'Invia messaggio',
        'Richiedi nuova visita',
        'Mostra Telefono',
        'segnala annuncio',        
        'Troviamo il mutuo ideale per te',
        'Ricevi una stima immediata',
        'Descrizione',
        'PREZZO BASE:',
        'PREZZO MINIMO',
        'Caratteristiche',
        'RIFERIMENTO E DATA ANNUNCIO',
        'CONTRATTO',
        'TIPOLOGIA',
        'SUPERFICIE',
        'LOCALI',
        'PIANO',
        'TOTALE PIANI EDIFICIO',
        'DISPONIBILITÀ',
        'DATI CATASTALI',
        'ALTRI DATI CATASTALI',
        'ALTRE CARATTERISTICHE',
        'Efficienza energetica',
        'ANNO DI COSTRUZIONE',
        'STATO',
        'RISCALDAMENTO',
        'EFFICIENZA ENERGETICA',
        'Dettaglio vendite',
        'TIPO VENDITA',
        'DATA VENDITA',
        'STATO',
        'Per partecipare',
        'OFFERTA MINIMA',
        'VALORE PERIZIA',
        'DEPOSITO CAUZIONALE',
        'DEPOSITO CONTO SPESE',
        'RIALZO MINIMO',
        'RIALZO MINIMO IN CASO DI GARA',
        'MOTIVO ESENZIONE',
        'SPESA PRENOTA DEBITO',
        'CONTRIBUTO NON DOVUTO',
        'LUOGO VENDITA',
        'REFERENTE',
        'LUOGO PRESENTAZIONE',
        'TERMINE PRESENTAZIONE',
        'CAUZIONE E SPESE',
        'NOTE',
        'Modalità deposito',
        #'bonifico bancario',
        'Dettagli lotto',
        'LOTTO NUMERO',
        'NUMERO IMMOBILI',
        'CATEGORIA',
        'Dati procedura',
        'AGGIORNATO IL',
        'REGISTRO',
        'NUMERO PROCEDURA',
        'PROCEDURA',
        'RITO',
        'TRIBUNALE',
        'Planimetria',
        'Mappa',
        'Mutuo,',
        "Prezzo dell'immobile",
        'Importo del mutuo',
        'Tasso del mutuo',
        'Durata del mutuo',
        'Rata da ... al mese'
        'Vuoi sapere che mutuo puoi richiedere?',
        'Scoprilo subito',
        'Opzioni aggiuntive',
        'stampa annuncio',
        'condividi annuncio'
    ]
    
    DICTIONARIES = {
        'li' : {
            'aria-label' : {
                'Accedi' : '',
                'profilo' : 'Profile', 
                "condividi l'annuncio" : 'Shared',
                'locali' : 'Number of Rooms',
                'data vendita' : 'Auction Date',
                'superficie' : 'Size',
                'bagni' : 'Number of Bathrooms',
                'piano' : 'Floor',
                #'' : 'Mortgage Duration'
            }
        }
    }
        
    SCRAPABLE_USELESS_CLASSES = [
        'nd-navbar__item--menuBack', 
        'in-referent__figure', 
        'nd-footerSection--social', 
        'in-referent__image', 
        'nd-ratio--wide', 
        'nd-slideshow__content', 
        'in-landingDetail__simpleGallery', 
        'nd-navbar__userMenu', 
        'in-mosaic__photo', 
        'nd-slideshow', 
        'in-landingDetail__banner', 
        'nd-footerSocial', 
        'nd-ratio--square', 
        'in-photo', 
        'nd-navbar__section--brand', 
        'nd-navbar__logo', 
        're-mortgageLink__icon', 
        'nd-select__arrow', 
        'in-userMenuToggleContent__arrow', 
        'in-agencyPhone__icon', 
        'nd-navbar__arrow', 
        're-mortgageBanner__icon', 
        'in-titleBlock__map', 
        'nd-figure', 
        'in-header__logo', 
        'in-userMenuToggleContent__avatar', 
        'nd-avatar', 
        'nd-slideshow__arrow--prev', 
        'in-userMenuToggleContent', 
        'is-hidden', 
        'nd-slideshow__arrow--next', 
        'in-landingDetail__documents', 
        'nd-navbar__item--menuBack', 
        'in-referent__figure', 
        'nd-footerSection--social', 
        'in-referent__image', 
        'nd-ratio--wide', 
        'nd-slideshow__content', 
        'in-landingDetail__simpleGallery', 
        'nd-navbar__userMenu', 
        'in-mosaic__photo', 
        'nd-slideshow', 
        'in-landingDetail__banner', 
        'nd-footerSocial', 
        'nd-ratio--square', 
        'in-photo', 
        'nd-navbar__section--brand', 
        'nd-navbar__logo', 
        're-mortgageLink__icon', 
        'nd-select__arrow', 
        'in-userMenuToggleContent__arrow', 
        'in-agencyPhone__icon', 
        'nd-navbar__arrow', 
        're-mortgageBanner__icon', 
        'in-titleBlock__map', 
        'nd-figure', 
        'in-header__logo', 
        'in-userMenuToggleContent__avatar', 
        'nd-avatar', 
        'nd-slideshow__arrow--prev', 
        'in-userMenuToggleContent', 
        'is-hidden', 
        'nd-slideshow__arrow--next', 
        'in-landingDetail__documents'
    ]
  
    def __init__(self, name:str=None):
        super(ImmobiliareProperty, self).__init__()
  
    def get_data(self, soup):
        data = {}
    
        #[(x['aria-label'], x.text) for x in soup.find_all(None, {'aria-label': True})]
        
        for tag in self.DICTIONARIES.keys():
            for attr in self.DICTIONARIES[tag].keys():
                for key in self.DICTIONARIES[tag][attr].keys():
                    data[self.DICTIONARIES[tag][attr][key]] = soup.find(tag, {attr: key})

        '''
        index = int(soup.find('h1', {'class': 'page-name'}).text.strip().split(' ')[-1])
        
        data['Title'], data['Description'] = [x.text.strip() for x in soup.find_all('p')][:2]
        
        urls = []
        for x in soup.find_all('a', {'class': 'btn'}):
            href = x['href']
            if not href.startswith('http'):
                href = self.URL_ROOTNAME + href
            if href not in urls:
                urls.append(href)
        data['Link a gestore vendita telematica'] = urls[0]
        data["Link per prenotazione della visita dell'immobile"] = urls[1]
        
        urls = []
        for x in soup.find_all('div', {'class': 'info-box'}):
            for y in x.find_all('a'):
                href = y['href']
                if href.startswith('/'):
                    href = self.URL_ROOTNAME + href
                if href not in urls:
                    urls.append(href)
        data["Sito di vendita all'asta"] = ''
        data['Allegati'] = ''
        for url in urls:
            if url.lower().endswith('.pdf'):
                key = 'Allegati'
            else:
                key = "Sito di vendita all'asta"
            if data[key]:
                data[key] += f', {url}'
            else:
                data[key] += url

        data['Tipologia del lotto'], data['Dettaglio'] = [x.text.strip() for x in soup.find_all('div', {'class': 'anagrafica-dato'})][:2]
        
        _keys = [x.text.strip() for x in soup.find_all('div', {'class': 'anagrafica-dato'})][2:]
        _values = [x.text.strip() for x in soup.find_all('div', {'class': 'anagrafica-risultato'})]    
        kix, vix = 0, 0
        for ix in range(len(_keys)):
            k = _keys[kix]
            if k == 'Tipologia' :
                if 'Tipologia di vendita' in data.keys():
                    k += ' del lotto'
                else:
                    k += ' di vendita'
            if ix == 7:
                vix += 1
            data[k] = _values[vix]
            kix += 1
            vix += 1
            
        _df = pd.DataFrame(data, index=[index])
        _df.index.name = 'Reference'
        
        return _df
        '''
        pass
