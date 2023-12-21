#!python

from IPython.display import display
import json
import locale
import os
import pandas as pd
from playwright.async_api import async_playwright
from tqdm.auto import tqdm


class RecrowdScraper():
    
    LABEL_FIXED_LENGTH:int = 20
    
    def __init__(self, name:str=None):
        self.name = name
        
    async def init(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.page = await self.browser.new_page()
        
        await self.page.set_viewport_size({"width": 1920, "height": 1080})
        
        url = 'https://www.recrowd.com/login'
        await self.page.goto(url)
        
    async def close(self):
        await self.browser.close()

    @staticmethod
    def read_configuration(filename:str):
        with open(filename, 'r') as f:
            configuration = json.load(f)
            print(configuration['recrowd'].keys())
            return configuration
    
    async def login(self):
        username = self.configuration['recrowd']['email']
        password = self.configuration['recrowd']['password']
        await self.page.locator("//input[@name='email']").fill(username)
        await self.page.locator("//input[@name='password']").fill(password)
        label = 'accedi'
        await self.page.get_by_text(label).click()
        await self.page.wait_for_timeout(3000)
    
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
