
import gspread
import os


def get_worksheet(sheetname:str=''):
    filename = os.path.abspath(os.path.join(os.path.expanduser('~'), 'gspreadscraper.json'))
    print(filename)

    if os.path.exists(filename):
        gc = gspread.service_account(filename=filename)
    else:
        raise FileNotFoundError(f"{filename} does NOT exist!")

    workbook = gc.open_by_key('1BRloTbcVOFAL9up2wIsvaAjFuJep9f3TWQwp_f02ntw')
    
    print(workbook.worksheets())
    worksheet = workbook.worksheet(sheetname)
    
    return worksheet