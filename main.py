#!/usr/bin/env python3

import os
from os import path
from shutil import disk_usage
from time import sleep
from random import randint
import math
import time
import configparser
import requests
import ucontroller

# In minutes
TELEMETRY_PERIOD_MIN = 0.1 #60
TELEMETRY_PERIOD_MAX = 0.1 #120

STATION_INFO_FILEPATH= path.dirname(path.realpath(__file__)) + '/station-info.cfg'

TELEMETRY_URL_REGISTER = "http://localhost:8000/station_register"
TELEMETRY_URL_UPDATE = "http://localhost:8000/station_update"

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
                      "disk_used"   : "{}",
                      "disk_cap"    : "{}"
                      '''.format(name, disk_used, disk_cap)

            if not math.isnan(float(humidity)):
                station += ', "humidity" : "' + humidity + '"'

            if not math.isnan(float(temperature)):
                station += ', "temperature" : "' + temperature + '"'

            host = '"name" : "' + host_name + '"'
            if len(host_phone) > 0: host += ', "phone" : "' + host_phone + '"'
            if len(host_email) > 0: host += ', "email" : "' + host_email + '"'
            if len(host_comment) > 0: host += ', "comment" : "' + host_comment + '"'

            data = '{ ' + station + ', "host": {' + host + '} }'

            try:
                if id == None:
                    print("Registering")

                    data = { 'data' : data }
                    request = requests.post(TELEMETRY_URL_REGISTER, data=data)
                    id = request.text
                else:
                    print("Updating")

                    data = { 'id' : id, 'data' : data }
                    request = requests.post(TELEMETRY_URL_UPDATE, data=data)
            except requests.ConnectionError:
                print("Could not connect to server")

            sleep(randint(int(TELEMETRY_PERIOD_MIN * 60), int(TELEMETRY_PERIOD_MAX * 60)))
    except KeyboardInterrupt:
        pass

    ucontroller.end()
    print("Ending telemetry.")

if __name__ == "__main__":
    telemetry()
