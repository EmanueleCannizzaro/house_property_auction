#!python

from IPython.display import display
import json
import os
import pandas as pd
from playwright.async_api import async_playwright
from tqdm.auto import tqdm


class BorsinoProUtility():
    
    LABEL_FIXED_LENGTH:int = 20
    
    def __init__(self, name:str=None):
        self.name = name
        
    async def init(self):        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.page = await self.browser.new_page()
        
        await self.page.set_viewport_size({"width": 1920, "height": 1080})
        
        url = 'https://borsinopro.it/utility/'
        await self.page.goto(url)
        
        label = 'Accetta e Chiudi'
        await self.page.get_by_text(label).click()
        
    @staticmethod
    def read_configuration(filename:str):
        with open(filename, 'r') as f:
            configuration = json.load(f)
            print(configuration['utility.borsinopro.it'].keys())
            return configuration
    
    async def login(self):
        username = self.configuration['utility.borsinopro.it']['username']
        password = self.configuration['utility.borsinopro.it']['password']
        await self.page.get_by_placeholder('Username').fill(username)
        await self.page.get_by_placeholder('Password').fill(password)
        label = 'Accedi'
        await self.page.get_by_text(label).click()
        await self.page.wait_for_timeout(3000)

    async def get_purchase_tax(self):
        MAP = {
            'Tipologia immobiliare' :'tipo_immobiliare', 
            'Tipo venditore': 'venditore'
        }
        
        url = self.configuration['utility.borsinopro.it']['purchase_tax']['url']
        await self.page.goto(url)
        
        pbar = tqdm(self.configuration['utility.borsinopro.it']['purchase_tax']['addresses'])
        for address in pbar:
            indirizzo_immobile = address['indirizzo_immobile']
            tipo_immobiliare = address['tipo_immobiliare']
            venditore = address['venditore']
            rendita_catastale_abitazione = address['rendita_catastale_abitazione']
            rendita_catastale_cantina = address['rendita_catastale_cantina']
            rendita_catastale_auto = address['rendita_catastale_auto']
            oneri_notarili = address['oneri_notarili']
            spese_agenzia = address['spese_agenzia']
            indirizzo_immobile2 = address['indirizzo_immobile2']

            pbar.set_description(f"{indirizzo_immobile:<{self.LABEL_FIXED_LENGTH}}")
        
            for element in await self.page.locator("//input[@name='indirizzo_immobile']").all():
                await element.fill(indirizzo_immobile)
            await self.page.locator("//select[@name='tipo_immobiliare']").select_option(label=tipo_immobiliare)
            await self.page.wait_for_timeout(3000)
            await self.page.locator("//select[@name='venditore']").select_option(label=venditore)
            await self.page.locator("//input[@name='rendita_catastale_abitazione']").fill(str(rendita_catastale_abitazione))
            await self.page.locator("//input[@name='rendita_catastale_cantina']").fill(str(rendita_catastale_cantina))
            await self.page.locator("//input[@name='rendita_catastale_auto']").fill(str(rendita_catastale_auto))
            await self.page.locator("//input[@name='oneri_notarili']").fill(str(oneri_notarili))
            await self.page.locator("//input[@name='spese_agenzia']").fill(str(spese_agenzia))
            label = 'Calcola imposte e costi acquisto'
            await self.page.get_by_text(label).click()
            
            await self.page.wait_for_timeout(3000)
            result = self.page.locator("//div[@id='esito_calcolo']")
            
            for t in await result.all_inner_texts():
                if t.strip():
                    _bloob = t.split('\n')
                    break
            _bloob = [x.strip() for x in _bloob if x.strip()]
            
            data = {}
            data['inputs'] = {}
            data['results'] = {}
            data['results']['Base imponibile'] = {}
            data['results']['Imposte applicate'] = {}
            for ix in range(len(_bloob)):
                if _bloob[ix] == 'Imposte e Costi acquisto':
                    data['type'] = _bloob[ix]
                elif _bloob[ix] in ['Tipologia immobiliare', 'Tipo venditore']:
                    data['inputs'][_bloob[ix]] = _bloob[ix + 1]
                elif _bloob[ix] in 'Valore catastale':
                    data['results']['Base imponibile'][_bloob[ix]] = _bloob[ix + 1]
                elif _bloob[ix] in ['Imposta Registro', 'Imposta Ipotecaria (fissa)', 'Imposta Catastale (fissa)', 'Imposte acquisto', 'Oneri Notarili', 'Spese Agenzia']:
                    data['results']['Imposte applicate'][_bloob[ix]] = _bloob[ix + 1]
                elif _bloob[ix] in '*Note':
                    k, v = _bloob[ix + 1].split(':')
                    data['results']['Imposte applicate'][_bloob[ix]] = k, v
                elif _bloob[ix] == 'TOTALE':
                    data['results'][_bloob[ix]] = _bloob[ix + 1]
                    
            for key in ['Tipologia immobiliare', 'Tipo venditore']:
                assert(data['inputs'][key] == address[MAP[key]])
                    
            print(json.dumps(data, ensure_ascii=False, indent=4))
                
        return data

    async def get_cadastal_value(self):
        url = self.configuration['utility.borsinopro.it']['cadastal_value']['url']
        await self.page.goto(url)
        
        pbar = tqdm(self.configuration['utility.borsinopro.it']['cadastal_value']['addresses'])
        for address in pbar:
            indirizzo_immobile = address['indirizzo_immobile']
            tipologia_catastale = address['tipologia_catastale']
            rendita_catastale = address['rendita_catastale']
            prima_casa_check = address['prima_casa_check']

            pbar.set_description(f"{indirizzo_immobile:<{self.LABEL_FIXED_LENGTH}}")
            
            for element in await self.page.locator("//input[@name='indirizzo_immobile']").all():
                await element.fill(indirizzo_immobile)
            await self.page.locator("//select[@name='tipologia_catastale']").select_option(label=tipologia_catastale)
            await self.page.wait_for_timeout(3000)
            await self.page.locator("//input[@name='rendita_catastale']").fill(str(rendita_catastale))
            if prima_casa_check:
                await self.page.locator("//input[@name='primacasacheck']").check(force=True)
            else:
                await self.page.locator("//input[@name='primacasacheck']").uncheck(force=True)
            label = 'Calcola Valore Catastale'
            await self.page.get_by_text(label).click()
            
            await self.page.wait_for_timeout(3000)
            result = self.page.locator("//div[@id='esito_calcolo']")
            
            for t in await result.all_inner_texts():
                if t.strip():
                    _bloob = t.split('\n')
                    break
            _bloob = [x.strip() for x in _bloob if x.strip()]
            
            data = {}
            data['results'] = {}
            for ix in range(len(_bloob)):
                if _bloob[ix] in 'Valore catastale':
                    data['type'] = _bloob[ix]                    
                    data['results'][_bloob[ix]] = _bloob[ix + 1]     
                    
            print(json.dumps(data, ensure_ascii=False, indent=4))
                
        return data

    async def get_real_estate_capital_gain(self):
        url = self.configuration['utility.borsinopro.it']['real_estate_capital_gain']['url']
        await self.page.goto(url)

        pbar = tqdm(self.configuration['utility.borsinopro.it']['real_estate_capital_gain']['addresses'])
        for address in pbar:
            indirizzo_immobile = address['indirizzo_immobile']
            spese_acquisto = address['spese_acquisto']
            spese_detraibili = address['spese_detraibili']
            valore_vendita = address['valore_vendita']

            pbar.set_description(f"{indirizzo_immobile:<{self.LABEL_FIXED_LENGTH}}")
            
            for element in await self.page.locator("//input[@name='indirizzo_immobile']").all():
                await element.fill(indirizzo_immobile)
            await self.page.locator("//input[@name='spese_acquisto']").fill(str(spese_acquisto))
            await self.page.locator("//input[@name='spese_detraibili']").fill(str(spese_detraibili))
            await self.page.locator("//input[@name='valore_vendita']").fill(str(valore_vendita))
            label = 'Calcola Plusvalenza'
            await self.page.get_by_text(label).click()
            
            await self.page.wait_for_timeout(3000)
            result = self.page.locator("//div[@id='esito_calcolo']")
            
            for t in await result.all_inner_texts():
                if t.strip():
                    _bloob = t.split('\n')
                    break
            _bloob = [x.strip() for x in _bloob if x.strip()]
            print(_bloob)

            data = {}
            data['results'] = {}
            for ix in range(len(_bloob)):
                if _bloob[ix] == 'Plusvalenza':
                    data['type'] = _bloob[ix]
                elif _bloob[ix] in ['Plusvalenza Ottenuta', 'Imposta sulla Plusvalenza']:
                    data['results'][_bloob[ix]] = _bloob[ix + 1]     
                    
            print(json.dumps(data, ensure_ascii=False, indent=4))
                
        return data

    async def get_dry_coupon(self):
        url = self.configuration['utility.borsinopro.it']['dry_coupon']['url']
        await self.page.goto(url)
        
        pbar = tqdm(self.configuration['utility.borsinopro.it']['dry_coupon']['addresses'])
        for address in pbar:
            indirizzo_immobile = address['indirizzo_immobile']
            canone_mensile = address['canone_mensile']
            tipo_canone = address['tipo_canone']
            
            pbar.set_description(f"{indirizzo_immobile:<{self.LABEL_FIXED_LENGTH}}")
            
            for element in await self.page.locator("//input[@name='indirizzo_immobile']").all():
                await element.fill(indirizzo_immobile)
            await self.page.locator("//input[@name='canone_mensile']").fill(str(canone_mensile))
            await self.page.locator("//select[@name='tipo_canone']").select_option(label=tipo_canone)
            label = 'Calcola Cedolare Secca'
            await self.page.get_by_text(label).click()
            
            await self.page.wait_for_timeout(3000)
            result = self.page.locator("//div[@id='esito_calcolo']")
            
            for t in await result.all_inner_texts():
                if t.strip():
                    _bloob = t.split('\n')
                    break
            _bloob = [x.strip() for x in _bloob if x.strip()]
            
            data = {}
            data['results'] = {}
            for ix in range(len(_bloob)):
                if _bloob[ix] == 'Cedolare secca':
                    data['type'] = _bloob[ix]
                elif _bloob[ix] in ['Imposta annuale', 'Canone mensile netto']:
                    data['results'][_bloob[ix]] = _bloob[ix + 1]     
                    
            print(json.dumps(data, ensure_ascii=False, indent=4))
                
        return data

    async def get_planimetric_surfaces(self):
        url = self.configuration['utility.borsinopro.it']['inheritance_shares']['url']
        await self.page.goto(url)
        
        _dfs = []
        pbar = tqdm(self.configuration['utility.borsinopro.it']['inheritance_shares']['addresses'])
        for address in pbar:
            tipologia_immobile = address['tipologia_immobile']

            pbar.set_description(f"{tipologia_immobile:<{self.LABEL_FIXED_LENGTH}}")
            
            for element in await self.page.locator("//input[@name='indirizzo_immobile']").all():
                await element.fill(indirizzo_immobile)
            await self.page.locator("//input[@name='canone_mensile']").fill(str(canone_mensile))
            await self.page.locator("//select[@name='tipo_canone']").select_option(label=tipo_canone)
            label = 'Calcola Cedolare Secca'
            await self.page.get_by_text(label).click()
            
            await self.page.wait_for_timeout(3000)
            result = self.page.locator("//div[@id='esito_calcolo']")
            
            for t in await result.all_inner_texts():
                if t.strip():
                    _bloob = t.split('\n')
                    break
            _bloob = [x.strip() for x in _bloob if x.strip()]
            
            data = {}
            data['results'] = {}
            for ix in range(len(_bloob)):
                if _bloob[ix] == 'Cedolare secca':
                    data['type'] = _bloob[ix]
                elif _bloob[ix] in ['Imposta annuale', 'Canone mensile netto']:
                    data['results'][_bloob[ix]] = _bloob[ix + 1]     
                    
            print(json.dumps(data, ensure_ascii=False, indent=4))
                
        return data

    async def get_income_capitalization(self):
        url = self.configuration['utility.borsinopro.it']['income_capitalization']['url']
        await self.page.goto(url)
        
        _dfs = []
        pbar = tqdm(self.configuration['utility.borsinopro.it']['income_capitalization']['addresses'])
        for aid, address in enumerate(pbar):
            indirizzo_immobile = address['indirizzo_immobile']
            canone_mensile = address['canone_mensile']
            tasso_capitalizzazione = address['tasso_capitalizzazione']

            pbar.set_description(f"{indirizzo_immobile:<{self.LABEL_FIXED_LENGTH}}")
            
            for element in await self.page.locator("//input[@name='indirizzo_immobile']").all():
                await element.fill(indirizzo_immobile)
            await self.page.locator("//input[@name='canone_mensile']").fill(str(canone_mensile))
            await self.page.locator("//input[@name='tasso_capitalizzazione']").fill(str(tasso_capitalizzazione))
            label = 'Calcola valore'
            await self.page.get_by_text(label).click()
            
            await self.page.wait_for_timeout(3000)
            result = self.page.locator("//div[@id='esito_calcolo']")
            
            for t in await result.all_inner_texts():
                if t.strip():
                    _bloob = t.split('\n')
                    break
            _bloob = [x.strip() for x in _bloob if x.strip()]
            
            data = {}
            data['results'] = {}
            data['results']['Valore'] = []
            for ix in range(len(_bloob)):
                if _bloob[ix] == 'Valore immobile in base alla redditività':
                    data['type'] = _bloob[ix]
                else:
                    data['results']['Valore'].append(_bloob[ix])

            data['results']['Address Id'] = [int(aid + 1)]
            data['results']['Indirizzo immobile'] = [indirizzo_immobile]
            data['results']['Canone_mensile'] = [canone_mensile]
            data['results']['Tasso_capitalizzazione'] = [tasso_capitalizzazione]
                         
            _dfs.append(pd.DataFrame(data['results']))
                
        _df = pd.concat(_dfs).set_index(['Address Id'])[['Indirizzo immobile', 'Canone_mensile', 'Tasso_capitalizzazione', 'Valore']]
        display(_df)
        return _df
    
    async def get_real_estate_profitability(self):
        url = self.configuration['utility.borsinopro.it']['real_estate_profitability']['url']
        await self.page.goto(url)
        
        _dfs = []
        pbar = tqdm(self.configuration['utility.borsinopro.it']['real_estate_profitability']['addresses'])
        for aid, address in enumerate(pbar):
            indirizzo_immobile = address['indirizzo_immobile']
            canone_mensile = address['canone_mensile']
            valore_immobile = address['valore_immobile']

            pbar.set_description(f"{indirizzo_immobile:<{self.LABEL_FIXED_LENGTH}}")
            
            for element in await self.page.locator("//input[@name='indirizzo_immobile']").all():
                await element.fill(indirizzo_immobile)
            await self.page.locator("//input[@name='canone_mensile']").fill(str(canone_mensile))
            await self.page.locator("//input[@name='valore_immobile']").fill(str(valore_immobile))
            label = 'Calcola Redditività'
            await self.page.get_by_text(label).click()
            
            await self.page.wait_for_timeout(3000)
            result = self.page.locator("//div[@id='esito_calcolo']")
            
            for t in await result.all_inner_texts():
                if t.strip():
                    _bloob = t.split('\n')
                    break
            _bloob = [x.strip() for x in _bloob if x.strip()]
            
            data = {}
            data['results'] = {}
            data['results']['Valore'] = []
            for ix in range(len(_bloob)):
                if _bloob[ix] == 'Redditività Immobile':
                    data['type'] = _bloob[ix]
                else:
                    data['results']['Valore'].append(_bloob[ix])

            data['results']['Address Id'] = [int(aid + 1)]
            data['results']['Indirizzo immobile'] = [indirizzo_immobile]
            data['results']['Canone_mensile'] = [canone_mensile]
            data['results']['Valore_immobile'] = [valore_immobile]
                         
            _dfs.append(pd.DataFrame(data['results']))
                
        _df = pd.concat(_dfs).set_index(['Address Id'])[['Indirizzo immobile', 'Canone_mensile', 'Valore_immobile', 'Valore']]
        display(_df)
        return _df
    
    async def get_bare_ownership_value(self):
        url = self.configuration['utility.borsinopro.it']['bare_ownership_value']['url']
        await self.page.goto(url)
        
        _dfs = []
        pbar = tqdm(self.configuration['utility.borsinopro.it']['bare_ownership_value']['addresses'])
        for aid, address in enumerate(pbar):
            indirizzo_immobile = address['indirizzo_immobile']
            valore_immobile = address['valore_immobile']
            eta_usofruttuario = address['eta_usofruttuario']

            pbar.set_description(f"{indirizzo_immobile:<{self.LABEL_FIXED_LENGTH}}")
            
            for element in await self.page.locator("//input[@name='indirizzo_immobile']").all():
                await element.fill(indirizzo_immobile)
            await self.page.locator("//input[@name='valore_immobile']").fill(str(valore_immobile))
            await self.page.locator("//select[@name='eta_usofruttuario']").select_option(label=eta_usofruttuario)
            label = 'Calcola Valore Nuda Proprietà'
            await self.page.get_by_text(label).click()
            
            await self.page.wait_for_timeout(3000)
            result = self.page.locator("//div[@id='esito_calcolo']")
            
            for t in await result.all_inner_texts():
                if t.strip():
                    _bloob = t.split('\n')
                    break
            _bloob = [x.strip() for x in _bloob if x.strip()]
            #print(_bloob)
            
            data = {}
            data['results'] = {}
            data['results']['Valore'] = []
            for ix in range(len(_bloob)):
                if _bloob[ix] == 'Valore nuda proprietà':
                    data['type'] = _bloob[ix]
                else:
                    data['results']['Valore'].append(_bloob[ix])

            data['results']['Address Id'] = [int(aid + 1)]
            data['results']['Indirizzo immobile'] = [indirizzo_immobile]
            data['results']['Valore immobile'] = [valore_immobile]
            data['results']['Eta usofruttuario'] = [eta_usofruttuario]
                         
            _dfs.append(pd.DataFrame(data['results']))
                
        _df = pd.concat(_dfs).set_index(['Address Id'])[['Indirizzo immobile', 'Valore immobile', 'Eta usofruttuario', 'Valore']]
        display(_df)
        return _df

    async def get_commercial_surface_coefficients(self):
        url = self.configuration['utility.borsinopro.it']['commercial_surface_coefficients']['url']
        await self.page.goto(url)
        
        _dfs = []
        pbar = tqdm(self.configuration['utility.borsinopro.it']['commercial_surface_coefficients']['addresses'])
        for address in pbar:
            tipologia_immobile = address['tipologia_immobile']

            pbar.set_description(f"{tipologia_immobile:<{self.LABEL_FIXED_LENGTH}}")
            
            await self.page.locator("//select[@name='tipo_immobile']").select_option(label=tipologia_immobile)
            
            await self.page.wait_for_timeout(3000)
            result = self.page.locator("//div[@id='esito_calcolo']")
            
            for t in await result.all_inner_texts():
                _bloob = t.split('\n')
            
            data = {}
            data['results'] = {}
            HEADERS = ['Tipo superfice', 'Coefficiente', 'Note', 'Dettaglio']
            for cid in range(len(HEADERS)):
                data['results'][HEADERS[cid]] = []
            for ix in range(len(_bloob)):
                idx = _bloob[ix].split('\t')[0].strip()
                if idx == 'Coefficienti Ponderazione':
                    data['type'] = _bloob[ix]
                elif idx == 'Tipo superfice':
                    pass
                elif idx == 'undefined':
                    pass
                elif idx in ['Superfici Coperte', 'Superfici Seminterrate', 'Verande Rifinite', 'Verande Non Rifinite', 
                             'Soppalchi Abitabili', 'Superfici Mansardate', 'Balconi', 'Terrazzi', 'Giardino', 'Loggie Patii', 'Loggie E Patii',
                             'Lastrici Solari', 'Cantina', 'Box', 'Posti Auto Scoperti', 'Altre Superfici Scoperte', 'Posti Auto Coperti',
                             'Locali Tecnici', 'Dependance', 'Terreni Annessi', 'Verande', 'Superfici Esterne', 'Archivi',
                             'Superfici Vendita', 'Sottonegozio Vendita', 'Sottonegozio', 'Retronegozio', 
                             'Mq Principali', 'Mq Principali Al 1° Piano', 'Mq Principali Al 1° Seminterrati',                             
                             'Mq Amministrazione Piano Terra', 'Mq Tettoie', 'Mq Cortilizzi', 
                             'Mq Amministrazione 1 Piano', 'Mq Amministrazione', 'Mq Tettoie', 'Mq Cortilizzi', 'Mq Esterni', 'Mq Soppalchi',
                             'Cantine - Soffitte']:
                    #print(f"{_bloob[ix]}")
                    values = _bloob[ix].split('\t')
                    #print(values)
                    for cid in range(len(HEADERS)):
                        if values[cid] == 'Loggie Patii':
                            values[cid] = 'Loggie E Patii'
                        if len(values) > cid:
                            data['results'][HEADERS[cid]].append(values[cid])
                        else:
                            data['results'][HEADERS[cid]].append(None)
                else:
                    print(f"{_bloob[ix]}")
                    #raise ValueError(f"{_bloob[ix]}")
            
            data['results']['Tipologia Immobile'] = [tipologia_immobile] * len(data['results'][HEADERS[0]])
            
            _dfs.append(pd.DataFrame(data['results']))
                
        _df = pd.concat(_dfs)
        display(_df.head())
        return _df

    async def get_real_estate_trading_business_plan(self):
        url = self.configuration['utility.borsinopro.it']['real_estate_trading_business_plan']['url']
        await self.page.goto(url)
        
        _dfs = []
        pbar = tqdm(self.configuration['utility.borsinopro.it']['real_estate_trading_business_plan']['addresses'])
        for address in pbar:
            indirizzo_immobile = address['indirizzo_immobile']
            spese_acquisto = address['spese_acquisto']
            valore_vendita = address['valore_vendita']
            spese_detraibili = address['spese_detraibili']
            spese_non_detraibili = address['spese_non_detraibili']

            pbar.set_description(f"{indirizzo_immobile:<{self.LABEL_FIXED_LENGTH}}")
            
            for element in await self.page.locator("//input[@name='indirizzo_immobile']").all():
                await element.fill(indirizzo_immobile)
            await self.page.locator("//input[@id='spese_acquisto']").fill(str(spese_acquisto))
            await self.page.locator("//input[@name='valore_vendita']").fill(str(valore_vendita))
            await self.page.locator("//input[@name='spese_detraibili']").fill(str(spese_detraibili))
            await self.page.locator("//input[@name='spese_non_detraibili']").fill(str(spese_non_detraibili))
            label = 'Calcola Conto Economico'
            await self.page.get_by_text(label).click()
            
            await self.page.wait_for_timeout(3000)
            result = self.page.locator("//div[@id='esito_calcolo']")
            
            for t in await result.all_inner_texts():
                if t.strip():
                    _bloob = t.split('\n')
                    break
            _bloob = [x.strip() for x in _bloob if x.strip()]
            
            data = {}
            data['results'] = {}
            for ix in range(len(_bloob)):
                if _bloob[ix] == 'Conto Economico':
                    data['type'] = _bloob[ix]
                elif _bloob[ix] in ['Plusvalenza ottenuta', 'Imposta Plusvalenza', 'Utile Netto', 'Redditività (ROI)']:
                    data['results'][_bloob[ix]] = _bloob[ix + 1]     
                    
            print(json.dumps(data, ensure_ascii=False, indent=4))
                
            return data

    async def get_inheritance_shares(self):
        url = self.configuration['utility.borsinopro.it']['inheritance_shares']['url']
        await self.page.goto(url)
        
        _dfs = []
        pbar = tqdm(self.configuration['utility.borsinopro.it']['inheritance_shares']['addresses'])
        for aid, address in enumerate(pbar):
            indirizzo_immobile = address['indirizzo_immobile']
            importo_successione = address['importo_successione']
            coniuge = address['coniuge']
            figli = address['figli']
            ascendenti = address['ascendenti']
            fratelli = address['fratelli']
            parenti = address['parenti']

            pbar.set_description(f"{indirizzo_immobile:<{self.LABEL_FIXED_LENGTH}}")
            
            for element in await self.page.locator("//input[@name='indirizzo_immobile']").all():
                await element.fill(indirizzo_immobile)
            await self.page.locator("//input[@name='importo_successione']").fill(str(importo_successione))
            await self.page.locator("//select[@name='coniuge']").select_option(label=coniuge)
            await self.page.locator("//input[@name='figli']").fill(str(figli))
            await self.page.locator("//select[@name='ascendenti']").select_option(label=ascendenti)
            await self.page.locator("//input[@name='fratelli']").fill(str(fratelli))
            await self.page.locator("//input[@name='parenti']").fill(str(parenti))
            label = 'Calcola ripartizione quote'
            await self.page.get_by_text(label).click()
            
            await self.page.wait_for_timeout(3000)
            result = self.page.locator("//div[@id='esito_calcolo']")
            
            for t in await result.all_inner_texts():
                _bloob = t.split('\n')
                break
            #print(_bloob)
            
            data = {}
            data['results'] = {}
            HEADERS = ['Aventi Diritto', 'Euro spettanti proquota']
            for cid in range(len(HEADERS)):
                data['results'][HEADERS[cid]] = []
            for ix in range(len(_bloob)):
                idx = _bloob[ix].split('\t')[0].strip()
                if idx == 'figli':
                    idx = 'Figli'                
                if idx == 'Ripartizione Eredità':
                    data['type'] = _bloob[ix]
                elif idx in ['Aventi Diritto', 'Euro spettanti proquota', 'Aventi DirittoEuro spettanti proquota']:
                    pass
                elif not idx:
                    pass
                elif idx.replace('.', '').isnumeric():
                    pass
                elif idx in ['Coniuge', 'Figli', 'Ascendenti', 'Fratelli', 'Parenti']:
                    #print(f"{_bloob[ix]}")
                    #values = _bloob[ix].split('\t')
                    #print(values)
                    #for cid in range(len(HEADERS)):
                        #if len(values) > cid:
                    data['results'][HEADERS[0]].append(_bloob[ix])
                    data['results'][HEADERS[1]].append(_bloob[ix + 1])
                        #else:
                        #    data['results'][HEADERS[cid]].append(None)
                else:
                    print(f"{_bloob[ix]}")
                    #raise ValueError(f"{_bloob[ix]}")

            data['results']['Address Id'] = [int(aid + 1)] * len(data['results'][HEADERS[0]])
            data['results']['Indirizzo immobile'] = [indirizzo_immobile] * len(data['results'][HEADERS[0]])
            
            
            _dfs.append(pd.DataFrame(data['results']))
                
        _df = pd.concat(_dfs).set_index(['Address Id'])
        display(_df)
        return _df
