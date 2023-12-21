import csv
import random
#import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from alltownri.spiders.alltown import AlltownSpider
from immospider.spiders.immoscout import ImmoscoutSpider
from openrent.spiders.openrent import OpenRentSpider
from openrent_scraper.spiders.openrent_scraper import OpenRentScraperSpider

# We are using .csv for data storage for the sake for simplicity and universal.

# Establishing handle with our csv file
def get_csv_rw_handle(fileName):
    with open(fileName + ".csv", 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
    return csv_reader


def get_todo_list_length():
    records = sh.get_all_records()
    todo_list = []

    for i in range(2, len(records)):
        if records[i]['let-agreed'] == '':
            todo_list.append(records[i])

    print(len(todo_list))
    # def get_update_list(self):
    #     records = sh.get_all_records()
    #     # get not rent out list
    #     for i in range(2, len(records)):
    #         if records[i]['let-agreed'] == '':
    #             self.to_update_list.append(records[i])
    #
    # def update_record(self, response):
    #     if len(self.to_update_list) == 0:
    #         return
    #
    #     next_todo_url = self.to_update_list.pop()
    #     yield scrapy.Request(next_todo_url, callback=self.update_record, dont_filter=True)


def updateRecord():
    records = sh.get_all_records()
    todo_list = []

    for i in range(2, len(records)):
        if records[i]['let-agreed'] == '':
            todo_list.append(records[i])

    print(len(todo_list))

    todo_list = random.sample(todo_list, int(len(todo_list)/4))
    print(len(todo_list))

    for i in range(0, len(todo_list)):
        todo_list[i]

def main():
    setting = get_project_settings()
    process = CrawlerProcess(setting)
    process.crawl(AlltownSpider)
    process.crawl(ImmoscoutSpider, url="https://www.immobilienscout24.de/Suche/S-T/Wohnung-Miete/Berlin/Berlin/-/2,50-/60,00-/EURO--1000,00")
    #process.crawl(ImmoscoutSpider, url="https://www.immobilienscout24.de/Suche/S-T/Wohnung-Kauf/Nordrhein-Westfalen/Dortmund/-/-/-/EURO-50000,00-150000,00?enteredFrom=result_list")
    process.crawl(OpenRentSpider)
    process.crawl(OpenRentScraperSpider)
    process.start()
    #updateRecord()
    

if __name__ == '__main__':
    main()

