#!python

from IPython.display import display
from datetime import date
import json
import locale
import os
import pandas as pd
from playwright.async_api import async_playwright
from tqdm.auto import tqdm


class MiglioriAsteScraper():
    
    WAIT_FOR_TIMEOUT:int=3000
    LABEL_FIXED_LENGTH:int = 20
    
    COUNTIES = [
        "AG", "AL", "AN", "AO", "AR", "AP", "AT", "AV", "BA", "BT", "BL", "BN", "BG", "BI", "BO", "BZ", "BS", "BR", "CA", "CL", "CB", "CI", "CE", "CT", "CZ", "CH",
        "CO", "CS", "CR", "KR", "CN", "EN", "FM", "FE", "FI", "FG", "FC", "FR", "GE", "GO", "GR", "IM", "IS", "AQ", "SP", "LT", "LE", "LC", "LI", "LO", "LU", "MC",
        "MN", "MS", "MT", "VS", "ME", "MI", "MO", "MB", "NA", "NO", "NU", "OG", "OT", "OR", "PD", "PA", "PR", "PV", "PG", "PU", "PE", "PC", "PI", "PT", "PN", "PZ",
        "PO", "RG", "RA", "RC", "RE", "RI", "RN", "RM", "RO", "SA", "SS", "SV", "SI", "SR", "SO", "TA", "TE", "TR", "TO", "TP", "TN", "TV", "TS", "UD", "VA", "VE", 
        "VB", "VC", "VR", "VV", "VI", "VT"
    ]

    
    def __init__(self, name:str=None):
        self.name = name
        
    async def init(self):        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.page = await self.browser.new_page()
        
        await self.page.set_viewport_size({"width": 1920, "height": 1080})
        
        url = 'https://miglioriaste.it/'
        await self.page.goto(url)
            
    async def close(self):
        await self.browser.close()
        await self.playwright.stop()

    @staticmethod
    def read_configuration(filename:str):
        with open(filename, 'r') as f:
            configuration = json.load(f)
            print(configuration['miglioriaste'].keys())
            return configuration
    
    async def login(self):
        url = self.configuration['miglioriaste']['url']
        await self.page.goto(url)
        username = self.configuration['miglioriaste']['email']
        password = self.configuration['miglioriaste']['password']
        await self.page.locator("//input[@name='email']").fill(username)
        await self.page.locator("//input[@name='password']").fill(password)
        label = 'accedi'
        await self.page.get_by_text(label).click()
        await self.page.wait_for_timeout(self.WAIT_FOR_TIMEOUT)
        
    async def get_url(self, county:str='PA'):
        url = self.configuration['miglioriaste']['url']
        await self.page.goto(url)
        await self.page.locator("//select[@name='provincia']").highlight()
        await self.page.locator("//select[@name='provincia']").select_option(county)
        await self.page.wait_for_timeout(self.WAIT_FOR_TIMEOUT)
        return self.page.url
    
    async def get_previous_auctions_url(self, county:str='PA'):
        await self.get_url(county)
        
        label = 'Visualizza le aste scadute negli ultimi 45 giorni con dettagli'
        url = await self.page.get_by_text(label, exact=True).get_attribute('href')
        return url

    '''
    async def browse_counties(self):
        pbar = tqdm(self.COUNTIES)
        for county in pbar:
            await self.page.locator("//select[@name='provincia']").select_option(county)
            await self.page.wait_for_timeout(self.WAIT_FOR_TIMEOUT)
    '''
        
    async def get_data_per_county(self, url:str, rootname:str='snapshot.PA'):
        if url != self.page.url:
            await self.page.goto(url)
            await self.page.wait_for_timeout(self.WAIT_FOR_TIMEOUT)
        
        number_of_tables = int((await self.page.locator("//td[@class='pag']/a>>nth=-1").all_inner_texts())[0])
        #print(number_of_tables)
        
        pbar = tqdm(range(number_of_tables), position=1)
        _dfs = []
        today = date.today().isoformat()
        for ix in pbar:
            await self.page.locator("//td[@class='pag']").get_by_text(f"{ix+1}", exact=True).click()
            await self.page.wait_for_timeout(self.WAIT_FOR_TIMEOUT)
            
            filename = os.path.join(self.configuration['miglioriaste']['snapshot_path'], f"{rootname}.{ix}.png")
            await self.page.screenshot(path=filename)
        
            source = await self.page.content()
            _dfs.append(pd.read_html(source)[0][:-1])
        
        df = pd.concat(_dfs)
        df['Data'] = today
        #print(df.shape)
        #display(df.tail())
        return df

    async def get_data(self, past_values_flag:bool=False):
        dfs = {}
        pbar = tqdm(self.COUNTIES, position=0)
        for county in pbar:
            pbar.set_description(f"{county}")
            if past_values_flag:
                url = await self.get_previous_auctions_url(county)
            else:
                url = await self.get_url(county)
            #print(url)

            rootname = f'snapshot.{county}'
            dfs[county] = await self.get_data_per_county(url, rootname)
            dfs[county]['Provincia'] = county
            
        _dfs = list(dfs.values())
        df = pd.concat(_dfs)
        return df
    
'''
    async def get_data_from_result(result):
        text = await result.all_inner_texts()
        data = {}
        for cid in ['Data', 'Tipologia', 'Importo']:
            data[cid] = []    
        for t in text:
            values = t.split('\n')
            data['Data'].append(values[0])
            if len(values) == 3:
                data['Tipologia'].append(values[1])
                data['Importo'].append(self.str2float(values[2]))
            elif len(values) == 2:
                data['Tipologia'].append(None)
                data['Importo'].append(self.str2float(values[1]))
            else:
                data['Tipologia'].append(None)
                data['Importo'].append(None)
        _df = pd.DataFrame(data)
        return _df

    async def extract_data(self):
        old_locale = locale.getlocale()
        locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')

        result = self.page.locator("//ul[@class='MuiPagination-ul css-nhb8h9']")
        for t in await result.all_inner_texts():
            pass
            #print(t)
            break
        last_page = int(t.split('\n')[-1])
        print(last_page)
        
        dfs = []
        pbar = tqdm(range(0, last_page))
        for ix in pbar:
            for element in await self.page.locator("//ul[@class='MuiPagination-ul css-nhb8h9']").get_by_text(f'{ix + 1}').all():
                await element.click()
                await self.page.wait_for_timeout(3000)
                break
        
            result = self.page.locator("//div[@class='MuiBox-root css-i9gxme']//div[@class='MuiBox-root css-1dkhoh2']")
            df = await self.get_data_from_result(result)
            if not df.empty:
                df['Azione'] = 'Refill'
                dfs.append(df)
                #display(dfs[-1])
            
            result = self.page.locator("//div[@class='MuiBox-root css-i9gxme']//div[@class='MuiBox-root css-qemm8r']")
            df = await self.get_data_from_result(result)
            if not df.empty:
                df['Azione'] = 'Investment'
                dfs.append(df)
                #display(dfs[-1])
        
        df = pd.concat(dfs)
        df = df[['Data', 'Tipologia', 'Azione', 'Importo']].sort_values(['Data'])
        
        df['Data'] = pd.to_datetime(df['Data'], format="%d %b %y")
        locale.setlocale(locale.LC_ALL, f'{old_locale[0]}.{old_locale[1]}')
        
        display(df.head())
        return df
    
    def to_excel(self, filename:str):
        self.data.to_excel(filename, index=False)

    @staticmethod
    def str2float(s:str):
        return float(s.replace('€', '').replace('.', '').replace(',', '.').replace('+', '').replace(' ', ''))
'''