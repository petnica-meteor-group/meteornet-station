#!/usr/bin/env python3

from os import path
from shutil import disk_usage
from time import sleep
from random import randint
import ctypes
import requests

UCONTROLLER_LIB_PATHS = [ "./ucontroller.so", "./ucontroller.dll" ]

# In minutes
TELEMETRY_PERIOD_MIN = 60
TELEMETRY_PERIOD_MAX = 120

TELEMETRY_URL_REGISTER = "http://localhost/station_register"
TELEMETRY_URL_UPDATE = "http://localhost/staton_update"

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

    #
    # name = "Station1"
    #
    # data = { 'data' : '{ "name" : "' + name +'" }' }
    #
    # request = requests.post(TELEMETRY_URL_REGISTER, data=data)
    # id = request.text
    #
    # try:
    #     while True:
    #         total_bytes, used_bytes, free_bytes = disk_usage(path.realpath('/'))
    #
    #         disk_used = str(used_bytes / (10 ** 9))
    #         disk_cap = str(total_bytes / (10 ** 9))
    #
    #         output = ucontroller.send_cmd(i).decode('utf-8')split('\n')[1].split(' ')
    #         humidity = output[0]
    #         temperature = output[1]
    #
    #         data = {
    #                  'id'   : id,
    #                  'data' : '{ "humidity"    : "' + humidity    + '",' \
    #                           '  "temperature" : "' + temperature + '",' \
    #                           '  "disk_used"   : "' + disk_used   + '",' \
    #                           '  "disk_cap"    : "' + disk_cap    + '"'
    #                 }
    #
    #         request = requests.post(TELEMETRY_URL_UPDATE, data=data)
    #
    #         sleep(randint(TELEMETRY_PERIOD_MIN * 60, TELEMETRY_PERIOD_MAX * 60))
    # except KeyboardInterrupt:
    #     pass


    print(ucontroller.end().decode('utf-8'), end='')
    print("Ending telemetry.")

if __name__ == "__main__":
    telemetry()
