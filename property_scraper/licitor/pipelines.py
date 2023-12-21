# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from property_scraper.infoencheres.pipelines import InfoEncheresFilesPipeline, InfoEncheresImagesPipeline


class LicitorFilesPipeline(InfoEncheresFilesPipeline):
    pass


class LicitorImagesPipeline(InfoEncheresImagesPipeline):
    pass
