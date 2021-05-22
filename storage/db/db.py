import sqlite3
import os
from sqlite3.dbapi2 import connect


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Database(metaclass=Singleton):
    conn, cursor = None, None

    def __init__(self, onmemory=False):
        self.conn = sqlite3.connect(self.__buildpath(onmemory))
        self.conn.row_factory = dict_factory
        self.cursor = self.conn.cursor()

    def execute(self, query):
        try:
            return self.__execute(query)
        except sqlite3.Error:
            print('Sqlite3 error!!!')
            self.__rollback()     
    
    def fetchall(self):
        return self.cursor.fetchall()   
    
    def __execute(self, query):
        self.cursor.execute(query)
        self.conn.commit()

    def __rollback(self):
        self.conn.rollback()

    def __buildpath(self, onmemory):
        if onmemory:
            return "file::memory:?cache=shared"
        return "{}/{}".format(os.getenv('DB_PATH'), "storage.db")

