import sqlite3
import os


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class Database:

    def __init__(self, onmemory=False):
        self.__onmemory__ = onmemory
        self.conn = sqlite3.connect(self.__buildpath(onmemory), check_same_thread=False)
        self.conn.row_factory = dict_factory
        self.cursor = self.conn.cursor()
        self.__clean()
        self.__initdb()


    def execute(self, query):
        try:
            return self.__execute(query)
        except sqlite3.Error as e:
            self.__rollback()     
    
    def fetchall(self):
        return self.cursor.fetchall()   
    
    def loadquery(self, q):
        path = os.path.realpath(__file__) 
        fdir = path[0:len(path)-len(os.path.basename(__file__))]
        f = open('{}/../querys/{}.sql'.format(fdir, q))
        query = f.read()
        f.close()
        return query

    def __execute(self, query):
        self.cursor.execute(query)
        self.conn.commit()

    def __rollback(self):
        self.conn.rollback()

    def __buildpath(self, onmemory):
        if onmemory:
            return ":memory:"
        return "{}/{}".format(os.getenv('DB_PATH'), "storage.db")

    def __initdb(self):
        self.cursor.executescript(self.loadquery('initdb'))
 
    def __clean(self):
        if not self.__onmemory__:
            return
        if not self.conn or not self.cursor:
            return
        self.__execute("DROP TABLE IF EXISTS `Block`;")
        self.__execute("DROP TABLE IF EXISTS `Coinbase`;")
        self.__execute("DROP TABLE IF EXISTS `Transaction`;")

    def __del__(self):
        self.conn.close()