# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import os
from pathlib import PurePosixPath
from scrapy.pipelines.files import FilesPipeline
from scrapy.pipelines.images import ImagesPipeline
from itemadapter import ItemAdapter
from urllib.parse import urlparse

from property_scraper import ROOT_FOLDER


class InfoEncheresFilesPipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        #print(urlparse(request.url).path)
        #print(urlparse(request.url).name)
        #print(os.path.basename(request.url))
        #return os.path.basename(urlparse(request.url))
        return PurePosixPath(urlparse(request.url).path).name


class InfoEncheresImagesPipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        #return os.path.join(ROOT_FOLDER, 'infoencheres', 'documents', os.path.basename(request.url))
        return PurePosixPath(urlparse(request.url).path).name
