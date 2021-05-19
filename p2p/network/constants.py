import threading
import socket
import struct
import traceback
import time


GOOGLE = ('www.google.com', 80)


class ThreadDebugging:

    def debugmsg(self, msg):
        print('[{}] {}'.format(str(threading.currentThread().getName()), msg))