# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import mysql.connector
from mysql.connector import Error

class VrbodataPipeline:

    connection = None
    count = 0

    def __init__(self):

        self.connection = self.create_server_connection("localhost", "root", "rootadmin")
        self.create_database(self.connection)
        self.connection = self.create_db_connection("localhost", "root", "rootadmin", "vrbo")
        self.create_table(self.connection)

    def create_server_connection(self, host_name, user_name, user_password):
        connection = None
        try:
            connection = mysql.connector.connect(
                host=host_name,
                user=user_name,
                passwd=user_password
            )
            print("MySQL Database connection successful")
        except Error as err:
            print(f"Connection Error: '{err}'")

        return connection

    def create_database(self, connection):
        create_vrbo_database = "CREATE DATABASE IF NOT EXISTS vrbo"
        cursor = connection.cursor()
        try:
            cursor.execute(create_vrbo_database)
            print("Database created successfully")
        except Error as err:
            print(f"Database Error: '{err}'")

    def create_db_connection(self, host_name, user_name, user_password, db_name):
        connection = None
        try:
            connection = mysql.connector.connect(
                host=host_name,
                user=user_name,
                passwd=user_password,
                database=db_name
            )
            print("MySQL Database connection successful")
        except Error as err:
            print(f"Error: '{err}'")

        return connection

    def create_table(self, connection):
        create_property_table = """
        CREATE TABLE IF NOT EXISTS property (
        property_name VARCHAR(100) NOT NULL,
        property_price VARCHAR(10) NOT NULL,
        property_thumb VARCHAR(100) NOT NULL,
        property_details VARCHAR(100) NOT NULL
        );
        """
        cursor = connection.cursor()
        try:
            cursor.execute(create_property_table)
            connection.commit()
            print("create table successful")
        except Error as err:
            print(f"Table Error: '{err}'")

    def execute_query(self, connection, query, data):
        cursor = connection.cursor()
        try:
            cursor.execute(query, data)
            connection.commit()
            print("Query successful")
        except Error as err:
            print(f"Query Error: '{err}'")

    def process_item(self, item, spider):

        self.insert_property(item)
        return item

    def insert_property(self, item):

        insert_stmt = (
            "INSERT INTO property(property_name, property_price, property_thumb, property_details)"
            "VALUES (%s, %s, %s, %s)"
        )
        data = (item['property_name'], item['property_price'], item['property_thumb'], item['property_details'])

        self.execute_query(self.connection, insert_stmt, data)


        # pop_teacher = """
        # INSERT INTO property VALUES
        # ('James', 'Smith', 'ENG', '1985-04-20'),
        # ('Stefanie',  'Martin',  'FRA',  '1970-02-17');
        # """
        # self.execute_query(self.connection, pop_teacher)



