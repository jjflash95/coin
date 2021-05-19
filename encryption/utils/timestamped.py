import datetime

class TimeStamped:
    __timestamp__ = None

    def __init__(self):
        self.__timestamp__ = datetime.datetime.now().timestamp()

    def timestamp(self):
        return self.__timestamp__