#!/usr/bin/env python3

import os
from os import path
from shutil import disk_usage
from time import sleep
from random import randint
import time
import configparser
import requests
import ucontroller

# In minutes
TELEMETRY_PERIOD_MIN = 60
TELEMETRY_PERIOD_MAX = 120

STATION_INFO_FILEPATH= './station-info.cfg'

TELEMETRY_URL_REGISTER = "http://localhost/station_register"
TELEMETRY_URL_UPDATE = "http://localhost/staton_update"

def night():
    hours = float(time.strftime("%H"))
    return (19 <= hours <= 24) or (0 <= hours <= 7)

def telemetry():
    if not ucontroller.init():
        return

    if night():
        shutter_open, camera_on = ucontroller.camera_switch(True)
    else:
        shutter_open, camera_on = ucontroller.camera_switch(False)

    id = None
    try:
        while True:
            if night() and not camera_on:
                shutter_open, camera_on = ucontroller.camera_switch(True)
            elif not night() and camera_on:
                shutter_open, camera_on = ucontroller.camera_switch(False)

            total_bytes, used_bytes, free_bytes = disk_usage(path.realpath('/'))

            disk_used = str(used_bytes / (10 ** 9))
            disk_cap = str(total_bytes / (10 ** 9))

            humidity, temperature = ucontroller.get_dht_info()

            config = configparser.ConfigParser()
            config.read(STATION_INFO_FILEPATH)

            name = config['station']['name']
            host_name = config['host']['name']
            host_phone = config['host']['phone']
            host_email = config['host']['email']
            host_comment = config['host']['comment']

            station = '''
                      "name"        : "{}",
                      "humidity"    : "{}",
                      "temperature" : "{}",
                      "disk_used"   : "{}",
                      "disk_cap"    : "{}"
                      '''.format(name, humidity, temperature, disk_used, disk_cap)
            host =  '''
                    "name"    : "{}",
                    "phone"   : "{}",
                    "email"   : "{}",
                    "comment" : "{}"
                    '''.format(host_name, host_phone, host_email, host_comment)

            data = '{ ' + station + ', "host": {' + host + '} }'

            if id == None:
                print("Registering")

                data = { 'data' : data }
                request = requests.post(TELEMETRY_URL_REGISTER, data=data)
                id = request.text
            else:
                print("Updating")

                data = { 'id' : id, 'data' : data }
                request = requests.post(TELEMETRY_URL_UPDATE, data=data)

            sleep(randint(int(TELEMETRY_PERIOD_MIN * 60), int(TELEMETRY_PERIOD_MAX * 60)))
    except KeyboardInterrupt:
        pass

    ucontroller.end()
    print("Ending telemetry.")

if __name__ == "__main__":
    telemetry()
