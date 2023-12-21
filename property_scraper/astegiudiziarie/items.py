# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import re
import scrapy
from scrapy.item import Item, Field
from itemloaders.processors import Join, MapCompose, TakeFirst
from urllib.parse import urljoin
from w3lib.html import remove_tags

from property_scraper import PVP_URL_ROOTNAME


def strip(text):
    s = text.strip()
    s = s.replace('\n', '').replace('\r', '')
    s = re.sub("\s\s+", " ", s)
    return s

def remove_currency(value):
    return float(value.replace(',', '.').replace('.', '').replace('€', '').replace('$', '').replace('£', '').strip())

def fix_relative_hyperlink(url:str):
    if url.startswith('/'):
        return urljoin(PVP_URL_ROOTNAME, url)
    else:
        return url

def description_in(d):
    return d.strip()

def description_out(d):
    labels = d[0:3]
    values = d[3:]
    output = {
        labels[0]: "".join(values[0]),
        labels[1]: " ".join(values[1:-1]),
        labels[2]: "".join(values[-1])
    }
    return output


class AsteGiudiziarieSearchPropertyItem(Item):
    items = {
        'css': {
            #'indirizzo': "div.anagrafica-risultato a::text",
            #'lotto': "span.black::text",
            #'url': "div.anagrafica-risultato a::attr(href)",
        },
        'xpath': {
            'title': './/h4[@class="box_title"]/text()',
            'location': './/div[@class="box_dettagli"]/p[1]/span/text()',
            'price': './/div[@class="box_dettagli"]/p[2]/span/text()',
            'description': './/div[@class="box_dettagli"]/p[3]/text()',
            #'data_di_vendita': '//span[contains(text(), "Data di vendita")]//span[@class="inline margin-left-10 font-green"]/text()',
            #'modalita_consegna': '//span[contains(text(), "Modalità Consegna")]//span[@class="margin-left-10 inline font-black"]/text()',
            #'numero_di_procedura': '//span[contains(text(), "N° Procedura")]//span[@class="margin-left-10 inline font-black"]/text()',
            #'offerta_minima': '//span[contains(text(), "Offerta minima")]//span[@class="margin-left-10 inline font-blue"]/text()',
            #"prezzo_base": '''//span[contains(text(), "Prezzo base d'asta")]//span[@class="font-blue font18 inline margin-left-10"]/text()''',
            #'rialzo_minimo': '//span[contains(text(), "Rialzo minimo")]//span[@class="margin-left-10 inline font-blue"]/text()',
            
            
            #'hyperlink': "/a[@class='listing-img-container']/href()",
            # /vendita-asta-appartamento-genova-via-bolzaneto-31-3-2061900
            
            #'tipo_asta': "/div[@class='listing-badges']/div[@class='auction-list-yellow']/span::text()", # Asta Telematica
            #'prezzo_base': "/div[@class='listing-img-content']/div[@class='listing-price']/span::text()", # € 86.549,75
            #'allegato': "/div[@class='listing-carousel']/div/img::src()", # /Allegato/Foto-GE-EI-124-2021-7.jpg/2061900
            # "ABITAZIONE DI TIPO ECONOMICO"
            
            #'hyperlink': "/div[@class='listing-content']/div[@class='listing-title']/h4/a::text()", # /vendita-asta-appartamento-genova-via-bolzaneto-31-3-2061900
            #'tipo_abitazione': "/div[@class='listing-content']/div[@class='listing-title']/h4/a::href()", # ABITAZIONE DI TIPO ECONOMICO
            
            #'nome': "/div[@class='listing-content']/div[@class='listing-title']/span::text()", # via Bolzaneto 31/3 Genova (GE)
            #'tribunale': "/div[@class='listing-content']/div[@class='listing-title']/h4/a[position=1]::title()", # Tribunale di Genova
            ## tribunale': "/div[@class='listing-content']/div[@class='listing-title']/h4/a[position=1]::text()", # Tribunale di Genova
            #'procedura': "/div[@class='listing-content']/div[@class='listing-title']/h4/a[position=2]::title()", # Esecuzione immobiliare 124 / 2021

            #'riferimento': "/div[@class='listing-content']/div[@class='listing-title']/h4/span[position=1]::text()", # EI-124-2021
            #'tipo_lotto': "/div[@class='listing-content']/div[@class='listing-title']/h4/span[position=2]::text()", # Lotto unico

            #'tribunale2': "/div[@class='listing-content']/div[@class='listing-details second-row']/ul/li[@class='more-details'][position=1]::text()", # Tribunale di Genova
            #'procedura2': "/div[@class='listing-content']/div[@class='listing-details second-row']/ul/li[@class='more-details'][position=2]::text()", # Esecuzione immobiliare
            #'codice': "/div[@class='listing-content']/div[@class='listing-details second-row']/ul/li[@class='more-details'][position=3]::text()", # Ruolo: 124/2021

            #'tipo_vendita': "/div[@class='listing-content']/ul[@class='listing-details']/li[@class='more-details'][position=1]::text()", # Vendita: Senza incanto - Sincrona mista
            #'data_vendita': "/div[@class='listing-content']/ul[@class='listing-details']/li[@class='more-details'][position=2]::text()", # 28/04/2023

            #'tipo_lotto2': "/div[@class='listing-content']/ul[@class='listing-details']/li[@class='more-details lotti']::text()", # Lotto: unico
            #'codice_asta': "/div[@class='listing-content']/ul[@class='listing-details']/li[@class='more-details'][position=4]::text()", # Codice asta: 4268796

            #'descrizione': "/div[@class='listing-content']/div[@class='listing-footer show-more']/span[@class='ellipsis-description']::text()", 
            # proprietà dell'appartamento sito a Genova, via Bolzaneto, n. 31/3. piano 1, composto da corridoio di ingresso e di distribuzione, soggiorno, due camere, cucina, sgabuzzino, servizio igienico,  ripostiglio.

            # tribunale': "/div[@class='listing-content']/div[@class='listing-footer show-more']/a[@class='show-more-button goto-detail']::text()", # Vai al dettaglio
            #'hyperlink3': "/div[@class='listing-content']/div[@class='listing-footer show-more']/a[@class='show-more-button goto-detail']::href()" # /vendita-asta-appartamento-genova-via-bolzaneto-31-3-2061900
            
        }
    }

    basename = Field(output_processor=TakeFirst())
    data_della_ricerca = Field(output_processor=TakeFirst())
    data_di_vendita = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    filename = Field(output_processor=TakeFirst())
    id = Field(output_processor=TakeFirst())
    indirizzo = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    is_downloaded = Field(input_processor=MapCompose(bool), output_processor=TakeFirst())
    is_relative_href_fixed = Field(input_processor=MapCompose(bool), output_processor=TakeFirst())
    lotto = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    modalita_consegna = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    numero_di_procedura = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    offerta_minima = Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())
    prezzo_base = Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())
    response_status_code = Field(input_processor=MapCompose(int), output_processor=TakeFirst())
    rialzo_minimo = Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())
    search_id = Field(output_processor=TakeFirst())
    spider_name = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    url = Field(input_processor=MapCompose(remove_tags, strip, fix_relative_hyperlink), output_processor=TakeFirst())
    url_localhost = Field(output_processor=TakeFirst())

    title = Field()
    location = Field()
    price = Field()
    description = Field()



class AsteGiudiziariePropertyItem(Item):
    items = {
        'css': {
            'dettaglio': 'div.anagrafica-risultato a::text',
        },
        'xpath': {
            'inserzione': "//h1[@class='page-name'][contains(text(), 'Inserzione')]/text()",
            # +).get().replace('Inserzione N.', '').strip()
            'descrizione': "//div[@class='col-xs-12 anagrafica-dato']/text()",
            # + )[0].get().strip()
            'lotto': "//div[@class='col-xs-12 anagrafica-dato']/text()",
            # + )[1].get().strip()
            'siti': "//div[@class='info-box'] a::attr(href)",
        }
    }

    """
    #'inserzione': 'div.anagrafica-risultato a::text',
    'Inserzione N. ': ,
    'Dettaglio': "div.anagrafica-risultato a::text",
    'DETTAGLIO LOTTO': 'div.anagrafica-risultato a::text',
    'LOTTO UNICO': 'div.anagrafica-risultato a::text',
    'PUBBLICATO ANCHE IN': 'div.anagrafica-risultato a::text',
    'Sito pubblicità': 'div.anagrafica-risultato a::text',
    'DETTAGLIO VENDITA': 'div.anagrafica-risultato a::text',
    'Gestore vendita telematica': 'div.anagrafica-risultato a::text',
    'Beni inclusi nel lotto': 'div.anagrafica-risultato a::text',
    'Prenota visita immobile': 'div.anagrafica-risultato a::text',
    'Dettaglio': 'div.anagrafica-risultato a::text',
    'DESCRIZIONE': 'div.anagrafica-risultato a::text',
    'DETTAGLIO PROCEDURA': 'div.anagrafica-risultato a::text',
    'REFERENTI': 'div.anagrafica-risultato a::text',
    'ALLEGATI': 'div.anagrafica-risultato a::text'

    "//div[@class='col-xs-12 anagrafica-dato']"

    "//h1[@class='page-name'][contains(text(), 'Inserzione')]",
    "p[@class='page-name']",
    "a[@class='btn']/href",

    'data_di_vendita': '//span[contains(text(), "Link a gestore vendita telematica")]//span[@class="inline margin-left-10 font-green"]/text()',
    'data_di_vendit': '//span[contains(text(), "Link per prenotazione della visita dell")]//span[@class="inline margin-left-10 font-green"]/text()',

    "a[@class='btn']/href",

    'data_di_vendit': '//span[contains(text(), ""Allegati"
    'data_di_vendit': '//span[contains(text(), "Sito di vendita all"

                      'div', {'class': 'anagrafica-dato'})][2:]
        _values = [x.text.strip() for x in soup.find_all('div', {'class': 'anagrafica-risultato'})

    'Vani', 'Delegato alla vendita', 'Curatore', 'Superficie', 'Giudice'


                      "a[@class='btn']/href",
            'data_di_vendita': '//span[contains(text(), "Data di vendita")]//span[@class="inline margin-left-10 font-green"]/text()',
            'modalita_consegna': '//span[contains(text(), "Modalità Consegna")]//span[@class="margin-left-10 inline font-black"]/text()',
            'numero_di_procedura': '//span[contains(text(), "N° Procedura")]//span[@class="margin-left-10 inline font-black"]/text()',
            'offerta_minima': '//span[contains(text(), "Offerta minima")]//span[@class="margin-left-10 inline font-blue"]/text()',
            "prezzo_base": '''//span[contains(text(), "Prezzo base d'asta")]//span[@class="font-blue font18 inline margin-left-10"]/text()''',
            'rialzo_minimo': '//span[contains(text(), "Rialzo minimo")]//span[@class="margin-left-10 inline font-blue"]/text()',
    """

    dettaglio = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    inserzione = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    descrizione = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    lotto = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    siti = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    # data_di_vendita = Field(input_processor=MapCompose(remove_tags, strip), output_processor=TakeFirst())
    # "title": "h1#page-name::text",
    # "price": "span#ContentPlaceHolder1_DetailsFormView_Shillings::text",
    # "location": "span#ContentPlaceHolder1_DetailsFormView_LocationLabel::text",
    # "bedrooms": "span#ContentPlaceHolder1_DetailsFormView_BedsInWordsLabel::text",
    # "district": "span#ContentPlaceHolder1_DetailsFormView_DistrictLabel::text",
    # "status": "span#ContentPlaceHolder1_DetailsFormView_StatusLabel::text",
    # "bathrooms": "span#ContentPlaceHolder1_DetailsFormView_BathsInWordsLabel::text",
    # "category": "span#ContentPlaceHolder1_DetailsFormView_CategoryLabel::text",
    # "agent": "span#ContentPlaceHolder1_DetailsFormView_AgentLabel::text",
    # "agent_contact": "span#ContentPlaceHolder1_FormView1_TelephoneLabel::text",
    # "agent_email": "span#ContentPlaceHolder1_FormView1_ContactEmailLabel::text",
    # "agent_company": "span#ContentPlaceHolder1_FormView1_CompanyLabel::text",

    # define the fields for your item here like:
    # number_of_results = int(scrapy.Field(.replace(' Annunci', '')))
    # hyperlink = Field(input_processor=MapCompose(remove_tags), output_processor=TakeFirst())
    # price = scrapy.Field(input_processor=MapCompose(remove_tags, remove_currency), output_processor=TakeFirst())
