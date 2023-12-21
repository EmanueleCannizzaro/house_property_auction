
#
# https://www.avvocatoandreani.it/servizi/calcolo-ammortamento-mutuo.php

# https://www.avvocatoandreani.it/servizi/calcolo-surroga-mutuo.php
# 
    # https://www.avvocatoandreani.it/servizi/risultato-calcolo-ammortamento-mutuo.php




#!python

from IPython.display import display
import json
import os
import pandas as pd
from playwright.async_api import async_playwright
from tqdm.auto import tqdm


class AvvocatoAndreaniUtility():
    
    LABEL_FIXED_LENGTH:int = 20
    
    METODI = {
        "F" : "Rata Costante (metodo francese)",
        "I" : "Capitale Costante (metodo italiano)"
    }
    PERIODICITA = {
        12 : "Mensile = 12&nbsp;rate all'anno",
        6 : "Bimestrale = 6rate all'anno",
        4 : "Trimestrale = 4 rate all'anno",
        3 : "Quadrimestrale = 3 rate all'anno",
        2 : "Semestrale = 2 rate all'anno",
        1 : "Annuale = 1 rata"
    }
    DURATE = {
        "Anni" : range(1, 40),
        "Rate" : range(2, 360)        
    }    
    TIPI_DURATA = {
        "Anni" : 1,
        "Rate" : 2
    }
    
    def __init__(self, name:str=None):
        self.name = name
        
    async def init(self):        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.page = await self.browser.new_page()
        
        await self.page.set_viewport_size({"width": 1920, "height": 1080})
        
        url = 'https://www.avvocatoandreani.it/servizi/'
        await self.page.goto(url)
        
        label = 'Accetta e Chiudi'
        await self.page.get_by_text(label).click()

    async def close(self):
        await self.browser.close()
        await self.playwright.stop()

    @staticmethod
    def read_configuration(filename:str):
        with open(filename, 'r') as f:
            configuration = json.load(f)
            print(configuration['servizi.avvocatoandreani.it'].keys())
            return configuration
    
    '''
    async def login(self):
        username = self.configuration['utility.borsinopro.it']['username']
        password = self.configuration['utility.borsinopro.it']['password']
        await self.page.get_by_placeholder('Username').fill(username)
        await self.page.get_by_placeholder('Password').fill(password)
        label = 'Accedi'
        await self.page.get_by_text(label).click()
        await self.page.wait_for_timeout(3000)
    '''
    
    async def get_amortization_schedule(self):
        
        _dfs = []
        pbar = tqdm(self.configuration['servizi.avvocatoandreani.it']['amortization_schedule']['mortgages'])
        for ix, mortgage in enumerate(pbar):
            url = self.configuration['servizi.avvocatoandreani.it']['amortization_schedule']['url']
            await self.page.goto(url)
            await self.page.wait_for_timeout(3000)
            
            metodo = mortgage['metodo']
            if metodo not in self.METODI.keys():
                raise ValueError(f"The variable metodo is set to {metodo}. It should be one of the following values: {self.METODI.keys()}.")
            capitale = mortgage['capitale']
            tasso = mortgage['tasso']
            periodicita = mortgage['periodicita']            
            if periodicita not in self.PERIODICITA.keys():
                raise ValueError(f"The variable periodicita is set to {periodicita}. It should be one of the following values: {self.PERIODICITA.keys()}.")
            tipo_durata = mortgage['tipo_durata']
            if tipo_durata not in self.TIPI_DURATA.keys():
                raise ValueError(f"The variable tipo_durata is set to {tipo_durata}. It should be one of the following values: {self.TIPI_DURATA.keys()}.")            
            durata = mortgage['durata']
            if durata not in self.DURATE[tipo_durata]:
                raise ValueError(f"The variable durata is set to {durata}. It should be one of the following values: {self.DURATE[tipo_durata]}.")
            dettagli_rate = mortgage['dettagli_rate']
            riepilogo_annuale = mortgage['riepilogo_annuale']

            pbar.set_description(f"{metodo:<{self.LABEL_FIXED_LENGTH}}")
            await self.page.locator("//select[@name='Metodo']").select_option(value=metodo)
            await self.page.locator("//input[@name='Capitale']").fill(str(capitale))
            await self.page.locator("//input[@name='Tasso']").fill(str(tasso))
            await self.page.locator("//select[@name='Periodicita']").select_option(value=str(periodicita))
            if tipo_durata == 'Anni':
                #await self.page.locator("//input[@name='TipoDurata']").fill(str(self.TIPI_DURATA[tipo_durata]))
                await self.page.locator("//input[@title='Clicca qui se conosci la durata in anni']").check(force=True)
                await self.page.locator("//select[@name='DurataAnni']").select_option(value=str(durata))
            elif tipo_durata == 'Rate':
                #await self.page.locator("//input[@name='TipoDurata']").fill(str(self.TIPI_DURATA[tipo_durata]))
                await self.page.locator("//input[@title='Clicca qui se conosci già il numero complessivo delle rate']").check(force=True)
                await self.page.locator("//select[@name='NumeroRate']").select_option(value=str(durata))
            if dettagli_rate:
                await self.page.locator("//input[@name='DettaglioRate']").check(force=True)
            else:
                await self.page.locator("//input[@name='DettaglioRate']").uncheck(force=True)
            if riepilogo_annuale:
                await self.page.locator("//input[@name='RiepilogoAnnuale']").check(force=True)
            else:
                await self.page.locator("//input[@name='RiepilogoAnnuale']").uncheck(force=True)
            label = 'Calcola'
            await self.page.get_by_text(label, exact=True).click()            
            await self.page.wait_for_timeout(3000)
            #result = self.page.locator("//div[@id='esito_calcolo']")
            '''
            Risultato
            <span class="SvcButton" title="Versione adatta per la stampa">Anteprima</span>
            <span class="SvcButton" title="Stampa la pagina">Stampa</span>
            <span class="SvcButton" title="Salva la pagina in formato PDF">PDF</span>
            '''
            rootname = f'snapshot'
            _df = await self.get_data(self.page.url, rootname)
            _dfs.append(_df)
        
        return _dfs            

    async def get_data(self, url:str, rootname:str='snapshot'):
        if url != self.page.url:
            await self.page.goto(url)
            await self.page.wait_for_timeout(self.WAIT_FOR_TIMEOUT)
        
        filename = os.path.join(self.configuration['servizi.avvocatoandreani.it']['snapshot_path'], f"{rootname}.png")
        await self.page.screenshot(path=filename)
    
        source = await self.page.content()
        _data = {}
        _dfs = pd.read_html(source)
        _df = pd.concat([_dfs[0], _dfs[-1]])
        _df = _df.drop_duplicates(keep='first', ignore_index=True)
        _df = _df[0].str.split(': ', expand=True)
        _df.columns = ['Parameter', 'Value'] 
        _df = _df.set_index(['Parameter'])
        _data['Summary'] = _df
        #print(_data['Summary'].shape)
        #display(_data['Summary'])

        _df = _dfs[1]
        _columns = ['Numero della Rata']
        _columns.extend(_df.iloc[0].values.tolist()[1:])
        _df.columns = _columns
        _df = _df.dropna(how='all')

        _df1 = _df[_df['Numero della Rata'].str.startswith('rata n. ')].copy()
        _df1['Indice'] = _df1['Numero della Rata'].apply(lambda x: x.replace('rata n. ', '')).astype(int)
        _df1 = _df1.dropna(how='all').dropna(how='all', axis=1)
        _df1 = _df1.set_index(['Indice'])
        _df1 = _df1.drop(['Numero della Rata'], axis=1)
        _data['Schedule'] = _df1
        _df2 = _df[(~_df['Numero della Rata'].str.startswith('rata n. ')) & (_df['Importo Rata'] != 'Importo Rata')].copy()
        _df2 = _df2.dropna(how='all').dropna(how='all', axis=1)        
        _df3 = _df2[_df2['Numero della Rata'].str.startswith('Tot. ')].copy()
        _df3['Indice'] = _df3['Numero della Rata'].apply(lambda x: x.replace('Tot. ', '').replace('° anno:', '')).astype(int)        
        _df3 = _df3.set_index(['Indice'])
        _df3 = _df3.drop(['Numero della Rata'], axis=1)
        _data['Yearly Payment'] = _df3
        _df4 = _df2[_df2['Numero della Rata'] == 'Rimanente:'].copy()
        _df4['Indice'] = list(range(1, len(_df4) + 1))
        _df4 = _df4.set_index(['Indice'])
        _df4 = _df4.drop(['Numero della Rata'], axis=1)
        _data['Yearly Outstanding Amount'] = _df4
        _df5 = _df2[_df2['Numero della Rata'] == "Dall'inizio:"].copy()
        _df5['Indice'] = list(range(2, len(_df5) + 2))
        _df5 = _df5.set_index(['Indice'])
        _df5 = _df5.drop(['Numero della Rata'], axis=1)
        _data['Yearly Repaid Amount'] = _df5
        #print(_data['Yearly Schedule'].shape)
        #display(_data['Yearly Schedule'].tail())
        return _data
            
    '''
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
        '''