from encryption.utils.truncate import truncate
import datetime

class TimeStamped:
    def __init__(self):
        self.__timestamp__ = truncate(datetime.datetime.now().timestamp())

    @property
    def timestamp(self):
        return self.__timestamp__
    
    @timestamp.setter
    def timestamp(self, ts):
        self.__timestamp__ = ts