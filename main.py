#!/usr/bin/env python3

from os import path
from shutil import disk_usage
from time import sleep
from random import randint
import ctypes

UCONTROLLER_LIB_PATHS = [ "ucontroller/ucontroller.so", "ucontroller/ucontroller.dll" ]

TELEMETRY_PERIOD_MIN = 2
TELEMETRY_PERIOD_MAX = 5

def get_ucontroller():
    ucontroller = None
    for i in range(0, len(UCONTROLLER_LIB_PATHS)):
        if path.exists(UCONTROLLER_LIB_PATHS[i]):
            ucontroller = ctypes.cdll.LoadLibrary(UCONTROLLER_LIB_PATHS[i])
            break

    ucontroller.init.restype = ctypes.c_char_p
    ucontroller.end.restype = ctypes.c_char_p
    ucontroller.send_cmd.argtypes = (ctypes.c_int,)
    ucontroller.send_cmd.restype = ctypes.c_char_p

    return ucontroller

def telemetry():
    ucontroller = get_ucontroller()
    print(ucontroller.init().decode('utf-8'), end='')

    for i in range(0, 5):
        print(ucontroller.send_cmd(i).decode('utf-8'), end='')
        sleep(3)

    '''
    try:
        while True:
            total_bytes, used_bytes, free_bytes = disk_usage(path.realpath('/'))

            disk_used = used_bytes / (10 ** 9)
            disk_cap = total_bytes / (10 ** 9)

            print(str(disk_used) + "/" + str(disk_cap))

            sleep(randint(TELEMETRY_PERIOD_MIN, TELEMETRY_PERIOD_MAX))
    except KeyboardInterrupt:
        pass
    '''

    print(ucontroller.end().decode('utf-8'), end='')
    print("Ending telemetry.")

if __name__ == "__main__":
    telemetry()
