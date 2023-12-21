# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
#import mysql.connector
#from pathlib import PurePosixPath
#import psycopg2
#import pymongo
from scrapy.exceptions import DropItem
from scrapy.pipelines.files import FilesPipeline
import sqlite3
#import sqlalchemy
#from urllib.parse import urlparse

from property_scraper import ROOT_FOLDER


def get_location(s:str, prefix:str='localita='):
    location = None
    tokens = s.split('/')[-1].split('?')[-1].split('&')
    for token in tokens:
        if token.startswith(prefix):
            location = token[len(prefix):].lower()
            return location
    return location


class SqlitePipeline:

    def __init__(self, database:str='pvp.db'):
        ## Create/Connect to database
        self.con = sqlite3.connect(databse)

        ## Create cursor, used to execute commands
        self.cur = self.con.cursor()

        ## Create quotes table if none exists
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS quotes(
            text TEXT,
            tags TEXT,
            author TEXT
        )
        """)

    def process_item(self, item, spider):
        ## Define insert statement
        self.cur.execute("""
             INSERT INTO quotes (text, tags, author) VALUES (?, ?, ?)
         """,
                         (
                             item['text'],
                             str(item['tags']),
                             item['author']
                         ))

        ## Execute insert of data into database
        self.con.commit()
        return item


class SqliteNoDuplicatesPipeline(SqlitePipeline):

    def __init__(self, database:str='pvp.db'):
        super().__init__(database)
        #super(SqliteNoDuplicatesPipeline, self).__init__(database)

    def process_item(self, item, spider):
        ## Check to see if text is already in database
        self.cur.execute("select * from quotes where text = ?", (item['text'],))
        result = self.cur.fetchone()

        if result:
            ## If it is in DB, create log message
            spider.logger.warn("Item already in database: %s" % item['text'])
        else:
            ## If text isn't in the DB, insert data

            ## Define insert statement
            self.cur.execute("""
                INSERT INTO quotes (text, tags, author) VALUES (?, ?, ?)
            """,
                             (
                                 item['text'],
                                 str(item['tags']),
                                 item['author']
                             ))

            ## Execute insert of data into database
            self.con.commit()
        return item


class HtmlPipeline(FilesPipeline):

    def __init__(self, filename:str='pvp.html'):
        ## Create/Connect to database
        self.name = 'pvp'

    def file_path(self, request, response=None, info=None, *, item=None):
        url = response.url
        if 'risultati_ricerca.page?' in url:
            location = get_location(url)
            if location:
                template = f'{ROOT_FOLDER}/{self.name}/{self.name}_{location}.html'
            else:
                template = f'{ROOT_FOLDER}/{self.name}/{self.name}.html'
            filename = get_unique_filename(template)
        else:
            keys = ['contentId']
            root = f'{ROOT_FOLDER}/{self.name}/{self.name}'
            filename = get_filename_from_identifier(url, keys, root)
        print(filename)
        return filename

    '''
    def process_item(self, item, spider):
        ## Define insert statement
        with open(filename, 'wb') as f:
            f.write(response.body)
        return item
    '''


class DuplicatesPipeline:

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter['id'] in self.ids_seen:
            raise DropItem(f"Duplicate item found: {item!r}")
        else:
            self.ids_seen.add(adapter['id'])
            return item

'''
class MongoPipeline:

    collection_name = 'scrapy_items'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
        return item


class MysqlPipeline:

    def __init__(self,
                 host:str='localhost',
                 user:str='root',
                 password:str='******',
                 database:str='quotes'):

        self.conn = mysql.connector.connect(host=host, user=user, password=password, database=database)

        ## Create cursor, used to execute commands
        self.cur = self.conn.cursor()

        ## Create quotes table if none exists
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS quotes(
            id int NOT NULL auto_increment, 
            content text,
            tags text,
            author VARCHAR(255),
            PRIMARY KEY (id)
        )
        """)

    def process_item(self, item, spider):
        ## Define insert statement
        self.cur.execute(""" insert into quotes (content, tags, author) values (%s,%s,%s)""", (
            item["text"],
            str(item["tags"]),
            item["author"]
        ))

        ## Execute insert of data into database
        self.conn.commit()

    def close_spider(self, spider):
        ## Close cursor & connection to database
        self.cur.close()
        self.conn.close()


class MysqlNoDuplicatesPipeline(MysqlPipeline):

    def __init__(self,
                 host:str='localhost',
                 user:str='root',
                 password:str='******',
                 database:str='quotes'):
        super().__init__(host=host, user=user, password=password, database=database)
        #super(SqliteNoDuplicatesPipeline, self).__init__()

    def process_item(self, item, spider):

        ## Check to see if text is already in database
        self.cur.execute("select * from quotes where content = %s", (item['text'],))
        result = self.cur.fetchone()

        if result:
            ## If it is in DB, create log message
            spider.logger.warn("Item already in database: %s" % item['text'])
        else:
            ## If text isn't in the DB, insert data
            ## Define insert statement
            self.cur.execute(""" insert into quotes (content, tags, author) values (%s,%s,%s)""", (
                item["text"],
                str(item["tags"]),
                item["author"]
            ))

            ## Execute insert of data into database
            self.connection.commit()
        return item

    def close_spider(self, spider):

        ## Close cursor & connection to database
        self.cur.close()
        self.conn.close()


class PostgresPipeline:

    def __init__(self,
                 hostname:str='localhost',
                 username:str='postgres',
                 password:str='******',  # your password
                 database:str='quotes'
                 ):

        ## Create/Connect to database
        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)

        ## Create cursor, used to execute commands
        self.cur = self.connection.cursor()

        ## Create quotes table if none exists
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS quotes(
            id serial PRIMARY KEY, 
            content text,
            tags text,
            author VARCHAR(255)
        )
        """)

    def process_item(self, item, spider):
        ## Define insert statement
        self.cur.execute(""" insert into quotes (content, tags, author) values (%s,%s,%s)""", (
            item["text"],
            str(item["tags"]),
            item["author"]
        ))

        ## Execute insert of data into database
        self.connection.commit()
        return item

    def close_spider(self, spider):
        ## Close cursor & connection to database
        self.cur.close()
        self.connection.close()


class PostgresNoDuplicatesPipeline:

    def __init__(self):
        def __init__(self,
                     host: str = 'localhost',
                     user: str = 'root',
                     password: str = '******',
                     database: str = 'quotes'):
            super().__init__(host=host, user=user, password=password, database=database)
            # super(SqliteNoDuplicatesPipeline, self).__init__()

    def process_item(self, item, spider):

        ## Check to see if text is already in database
        self.cur.execute("select * from quotes where content = %s", (item['text'],))
        result = self.cur.fetchone()

        ## If it is in DB, create log message
        if result:
            spider.logger.warn("Item already in database: %s" % item['text'])


        ## If text isn't in the DB, insert data
        else:

            ## Define insert statement
            self.cur.execute(""" insert into quotes (content, tags, author) values (%s,%s,%s)""", (
                item["text"],
                str(item["tags"]),
                item["author"]
            ))

            ## Execute insert of data into database
            self.connection.commit()
        return item

    def close_spider(self, spider):

        ## Close cursor & connection to database
        self.cur.close()
        self.connection.close()
'''
