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
import traceback

# In minutes
TELEMETRY_PERIOD_MIN = 60
TELEMETRY_PERIOD_MAX = 120

STATION_INFO_FILEPATH= path.dirname(path.realpath(__file__)) + '/station-info.cfg'

SERVER_URL = "http://localhost:8000"
TELEMETRY_URL_REGISTER = SERVER_URL + "/station_register"
TELEMETRY_URL_UPDATE   = SERVER_URL + "/station_update"
ERROR_URL              = SERVER_URL + "/station_error"

def night():
    hours = float(time.strftime("%H"))
    return (19 <= hours <= 24) or (0 <= hours <= 7)

def get_station_data(config):
    name = config['station']['name']

    total_bytes, used_bytes, free_bytes = disk_usage(path.realpath('/'))

    disk_used = str(used_bytes / (10 ** 9))
    disk_cap = str(total_bytes / (10 ** 9))

    station_data = '''
              "name"        : "{}",
              "disk_used"   : "{}",
              "disk_cap"    : "{}"
              '''.format(name, disk_used, disk_cap)

    humidity, temperature = ucontroller.get_dht_info()

    if not math.isnan(float(humidity)):
        station_data += ', "humidity" : "' + humidity + '"'

    if not math.isnan(float(temperature)):
        station_data += ', "temperature" : "' + temperature + '"'

    return station_data

def get_host_data(config):
    host_name = config['host']['name']
    host_phone = config['host']['phone']
    host_email = config['host']['email']
    host_comment = config['host']['comment']

    host_data = '"name" : "' + host_name + '"'
    if len(host_phone) > 0: host_data += ', "phone" : "' + host_phone + '"'
    if len(host_email) > 0: host_data += ', "email" : "' + host_email + '"'
    if len(host_comment) > 0: host_data += ', "comment" : "' + host_comment + '"'

    return host_data

def telemetry():
    if not ucontroller.init():
        return

    if night():
        shutter_open, camera_on = ucontroller.camera_switch(True)
    else:
        shutter_open, camera_on = ucontroller.camera_switch(False)

    id = None
    errors = []
    try:
        print("Starting telemetry")
        while True:
            try:
                if night() and not camera_on:
                    shutter_open, camera_on = ucontroller.camera_switch(True)
                elif not night() and camera_on:
                    shutter_open, camera_on = ucontroller.camera_switch(False)

                config = configparser.ConfigParser()
                config.read(STATION_INFO_FILEPATH)

                station_data = get_station_data(config)
                host_data = get_host_data(config)

                data = '{ ' + station_data + ', "host": {' + host_data + '} }'

                if id == None:
                    print("Registering station...")

                    data = { 'data' : data }
                    request = requests.post(TELEMETRY_URL_REGISTER, data=data)
                    id = request.text

                    print("Station registration successful.")
                else:
                    print("Sending telemetry data...")

                    data = { 'id' : id, 'data' : data }
                    request = requests.post(TELEMETRY_URL_UPDATE, data=data)

                    print("Telemetry data sent successfully.")

            except requests.ConnectionError:
                print("Could not connect to the server.")
            except Exception as e:
                print("\nERROR:")
                trace = ''.join(traceback.format_tb(e.__traceback__)) + str(e)
                print(trace + "\n")
                errors.append(trace)

            if len(errors) > 0:
                print("Sending error(s) to the server...")
                errors_sent = []

                try:
                    for e in errors:
                        if id != None:
                            error_data = { 'id' : id, 'error' : str(e) }
                        else:
                            error_data = {            'error' : str(e) }

                        requests.post(ERROR_URL, data=error_data)
                        errors_sent.append(e)

                    print("Error(s) sent successfully.")
                except requests.ConnectionError:
                    print("Could not connect to the server.")

                errors = [e for e in errors if e not in errors_sent]

            sleep(randint(int(TELEMETRY_PERIOD_MIN * 60), int(TELEMETRY_PERIOD_MAX * 60)))
    except KeyboardInterrupt:
        print("Ending telemetry.")

    ucontroller.end()

if __name__ == "__main__":
    telemetry()
