#!/usr/bin/env python

import ctypes
import random
import time
import sys


user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


keystrokes = 0
mouse_clicks = 0
double_clicks = 0


class LASTINPUTINFO(ctypes.Structure):

    __fields__ = [
        ('cbSize', ctypes.c_uint),
        ('dwTime', ctypes.c_ulong)
    ]


def get_last_input():

    struct_lastinputinfo = LASTINPUTINFO()
    struct_lastinputinfo.cbSize = ctypes.sizeof(LASTINPUTINFO)

    user32.GetLastInputInfo(ctypes.byref(struct_lastinputinfo))

    run_time = kernel32.GetTickCount()

    elapsed = run_time - struct_lastinputinfo.dwTime

    print('[*] %d ms since last modification' % elapsed)

    return elapsed


while True:
    get_last_input()
    time.sleep(1)