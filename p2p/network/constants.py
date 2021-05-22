import threading
import socket
import struct
import traceback
import time


GOOGLE = ('www.google.com', 80)


def cthreadname():
    return str(threading.currentThread().getName())

def debug(msg):
    print('[{}] {}'.format(cthreadname(), msg))