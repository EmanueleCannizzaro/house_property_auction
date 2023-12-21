
from bs4 import BeautifulSoup
from datetime import date, datetime
from glob import glob
from gspread import service_account
import json
#import linkcheck
from multiprocessing import Pool
import os
import pandas as pd
import subprocess
from subprocess import run
from tqdm.auto import tqdm

#from property_scraper.pvp_scraper import PVPScraper


class SearchStore:
    DEFAULT_CREDENTIALS = os.path.expanduser('~/gspreadscraper.json')
    DEFAULT_WORKBOOK_ID = '1BRloTbcVOFAL9up2wIsvaAjFuJep9f3TWQwp_f02ntw'

    INCOMPLETE = {
        'bologna': ['11/04/2023', '25/04/2023'],
        'busto+arsizio': ['25/04/2023'],
        'gallarate': ['25/04/2023'],
        'lodi': ['25/04/2023'],
        'novara': ['11/04/2023'],
        'palermo': ['25/04/2023'],
        'perugia': ['25/04/2023'],
        'ravenna': ['25/04/2023'],
        'roma': ['25/04/2023'],
        'torino': ['25/04/2023'],
        'venezia': ['11/04/2023', '25/04/2023'],
        'vicenza': ['25/04/2023'],
        'NaN': ['26/04/2023', ]
    }
    
    
    def __init__(self, name:str=None, credentials:str=None, workbook_id:str=None):
        self.name = name
        self.credentials = credentials
        self.workbook_id = workbook_id
        
        if not self.credentials:
           self.credentials = self.DEFAULT_CREDENTIALS
        self.gc = service_account(filename=self.credentials)
        
        if not self.workbook_id:
            self.workbook_id = self.DEFAULT_WORKBOOK_ID

        self.workbook = self.gc.open_by_key(self.workbook_id)

    def fix_results(self):
        #self.results['Data della Ricerca'] = pd.to_datetime(self.results['Data della Ricerca'])
        for cid in ['raggio', 'frame4_item']:
            if cid in self.results.columns:
                self.results[cid] = self.results[cid].fillna(0)
        for cid in ['raggio', 'elementiPerPagina', 'frame4_item']:
            if cid in self.results.columns:
                self.results[cid] = self.results[cid].astype(int)

    def update_results(self, filename:str, pattern:str):
        if os.path.exists(filename):
            is_first_database = False
            search = pd.read_parquet(filename)
            print(search.shape)
            display(search.head(3).T)
        else:
            is_first_database = True

        filenames = glob(pattern) 
        print(pattern)
        if filenames:
            print('\n'.join(sorted(filenames)))
            _searches = []
            pbar = tqdm(filenames)
            for filename in pbar:
                _searches.append(pd.read_csv(filename))
            _search = pd.concat(_searches)
            _search = _search.rename(columns=PVPScraper.SEARCH_NAMES)
            print(_search.shape)
            _search = _search.drop_duplicates(keep='last')
            print(_search.shape)
            display(_search.head(3).T)
            if not _search.empty:
                if is_first_database:
                    search = _search
                else:
                    search = pd.concat([search, _search])
                print(search.shape)
                search = search.drop_duplicates(keep='last')
                print(search.shape)
                display(search.head(3).T)        
                    
                search['Basename'] = search['Basename'].astype(str)
                search['Batch'] = search['Basename'].apply(lambda x: '_'.join(x.split('_')[:-1]))
                display(search.head(3).T)
                
        return search
            
    def backup_results(self, filename:str, bylocation_filename:str):
        rootname, extension = os.path.splitext(filename)
        if os.path.exists(filename):
            today = date.today()
            iso_date = today.strftime('%Y%m%d')
            filename_old = f"{rootname}.{iso_date}{extension}"
            print(f"Renaming file from {filename} to {filename_old}...")
            os.rename(filename, filename_old)

        print(f"Saving file {filename}...")
        if extension == '.parquet':
            #if 'Data della Ricerca' in self.results.columns:
            #    self.results['Data della Ricerca'] = self.results['Data della Ricerca'].astype(str)
            self.results.to_parquet(filename)
        elif extension == '.csv':
            self.results.to_csv(filename)
        elif extension == '.xlsx':
            with pd.ExcelWriter(filename) as f:
                sheetname = 'property'
                self.results.to_excel(f, sheet_name=sheetname)
                                
                if not self.results_bylocation.empty:    
                    sheetname = 'bylocation_property'
                    self.results_bylocation.to_excel(f, sheet_name=sheetname)

        if bylocation_filename:  
            if not self.results_bylocation.empty:
                rootname, extension = os.path.splitext(bylocation_filename)
                if os.path.exists(bylocation_filename):
                    today = date.today()
                    iso_date = today.strftime('%Y%m%d')
                    bylocation_filename_old = f"{rootname}.{iso_date}{extension}"
                    print(f"Renaming file from {filename} to {bylocation_filename_old}...")
                    os.rename(bylocation_filename, bylocation_filename_old)

                print(f"Saving file {bylocation_filename}...")
                if extension == '.parquet':
                    self.results_bylocation.to_parquet(bylocation_filename)
                elif extension == '.csv':
                    self.results_bylocation.to_csv(bylocation_filename)
    
    def to_gsheet(self, sheetname:str, bylocation_sheetname:str=''):
        worksheet = self.workbook.worksheet(sheetname)

        worksheet.clear()
        
        search = self.results.copy().fillna('')
        search = search.reset_index()
        search = search.rename(columns=PVPScraper.SEARCH_NAMES)
        worksheet.update([search.columns.values.tolist()] + search.values.tolist())
        search = search.set_index(['Identificativo'])
        
        if bylocation_sheetname:
            if not self.results_bylocation.empty:
                worksheet = self.workbook.worksheet(bylocation_sheetname)
            
                worksheet.clear()
                
                search_grouped = self.results_bylocation.copy().fillna('')
                search_grouped = search_grouped.reset_index()
                search_grouped["Localita' estratta dal nome del file"] = search_grouped["Localita' estratta dal nome del file"].fillna('Italia')
                worksheet.update([search_grouped.columns.values.tolist()] + search_grouped.values.tolist())
                #search_grouped = search_grouped.set_index(["Localita' estratta dal nome del file", 'Data della Ricerca'])

    def create_results_bylocation_table(self):
        search_completed_only = self.results.copy()
        for key in self.INCOMPLETE.keys():
            for date in self.INCOMPLETE[key]:
                if key != 'NaN':
                    indices = search_completed_only[(search_completed_only["Localita' estratta dal nome del file"] == key) & (search_completed_only['Data della Ricerca'] == date)].index
                else:
                    indices = search_completed_only[pd.isnull(search_completed_only["Localita' estratta dal nome del file"]) & (search_completed_only['Data della Ricerca'] == date)].index
                #display(search_completed_only.loc[indices][["Localita' estratta dal nome del file", 'Data della Ricerca', 'Numero di Pagine']])
                search_completed_only = search_completed_only.drop(indices)

        print(f"{self.results.shape} != {search_completed_only.shape}")
        
        columns = ["Localita' estratta dal nome del file", 'Data della Ricerca']
        _search_grouped = []
        _search_grouped.append(search_completed_only.groupby(by=columns, dropna=False)[['Identificativo della Pagina']].min().rename(columns={'Identificativo della Pagina': 'Prima Pagina'}))
        _search_grouped.append(search_completed_only.groupby(by=columns, dropna=False)[['Identificativo della Pagina', 'Numero di Pagine']].max().rename(
            columns={'Identificativo della Pagina': 'Ultima Pagina'}))
        search_grouped = pd.concat(_search_grouped, axis=1).sort_index()
        
        df = search_grouped.unstack().fillna(0).astype(int)
        df.columns = df.columns.swaplevel(0, 1)
        df = df.sort_index(ascending=[True, False], axis=1)
        #df.columns = df.columns.
        search_grouped = df.stack()
        display(search_grouped)
    
        return search_grouped

    def show(self, n:int):
        for cid in self.results.keys():
            print(f"{cid} -> \n\t" + '\n\t'.join([str(x) for x in self.results[cid].unique()[:n]]))
        
class SearchPropertyStore(SearchStore):
    pass
    
    
class PropertyStore(SearchStore):
    COLUMNS = [
        'Référence', 
        'Hyperlink', 
        'Ville', 
        'Département', 
        'Nature du Bien', 
        'Mise à Prix', 
        'Chiffre de Prix',
        'Superficie', 
        #'Size [m2]', 
        #'Price', 
        'Vente le',
        #'Date de la Vente', 
        'Date de Visite',
        #'Date de la Visite', 
        'Avocat', 
        "Numéro de Téléphone de l'Avocat",
        "Carte d'Avocat",
        "Site d'Avocat",
        'Interesting?', 
        'Property Value per square meter', 
        'Sell Price', 
        'Requested Profit', 
        'Repairment Costs', 
        'Lawyer Fees', 
        'Sale Fees', 
        'Advance Fees', 
        'Registration and Notary Fees', 
        'Transfer Fees', 
        'Sale subject to Property Tax?', 
        'Property Tax', 
        'Last Expenses Provision', 
        'Real Estate Fees', 
        'Purchase Price', 
        'Total Cost', 
        'Actual Profit', 
        'Maximum Purchase Price', 
        'Auction Deposit', 
        'Is the opportunity feasible?', 
        'Minimum Auction Offer', 
        'Final Decision', 
        'ROI', 
        'Purchase Price Increase'
    ]