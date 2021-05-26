import threading
import socket
import struct
import traceback
import time
import sys


GOOGLE = ('www.google.com', 80)

def cthreadname():
    return str(threading.currentThread().getName())


def debug(handler, msg):
    if not handler:
        return

    handler.write('[{}] {}\n'.format(cthreadname(), msg[:90]))
    if getattr(handler, "flush", None):
        handler.flush()

