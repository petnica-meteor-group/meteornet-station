import traceback
import time
import random
import logging
import requests
import json
import math
import pprint
import datetime
from shutil import disk_usage
from os.path import realpath, exists, join, dirname
from . import config

def sleep():
    delay = random.randint(int(config.WAKEUP_PERIOD_MIN * 60), int(config.WAKEUP_PERIOD_MAX * 60))
    logging.getLogger("Utils").debug("Sleeping for {}.".format(delay))
    time.sleep(delay)

def is_night():
    current_time = time.strftime('%H:%M')
    night_start, night_end = config.GET_NIGHT_INTERVAL(datetime.date.today())
    return (night_start <= current_time <= night_end) or \
           ( \
               ((night_start <= current_time) or (current_time <= night_end)) and \
                 night_end < night_start \
            )

def get_trace(exception):
    return str(''.join(traceback.format_tb(exception.__traceback__))) + str(exception)

def station_get_json(security_token, station_info, ucontrollers):
    logger = logging.getLogger("Utils")
    logger.debug("Gathering station data...")

    station_json = {}

    if security_token != None: station_json['security_token'] = security_token
    station_json['timestamp'] = int(time.time())

    for key in station_info.get('station'):
        station_json[key] = station_info.get('station', key)

    components = []

    computer = {}
    computer['name'] = 'Computer'

    measurements = {}
    total_bytes, used_bytes, free_bytes = disk_usage(realpath('/'))
    measurements['Disk used'] = str(used_bytes / (1024 ** 3)) + "GiB"
    measurements['Disk cap'] = str(total_bytes / (1024 ** 3)) + "GiB"
    computer['measurements'] = measurements

    components.append(computer)

    measurements_list = ucontrollers.get_measurements_list()
    for measurement in measurements_list:
        component = {}
        component['name'] = measurement['name']
        component['measurements'] = measurement['data']
        components.append(component)

    i = 1
    while True:
        camera = station_info.get('camera' + str(i))
        if camera == None:
            break

        camera_data = {}
        if i == 1:
            camera_data['name'] = 'Camera (ϕ: {}, λ: {})'.format(camera['azimuth'], camera['altitude'])
        else:
            camera_data['name'] = 'Camera {} (ϕ: {}, λ: {})'.format(str(i), camera['azimuth'], camera['altitude'])
            if i == 2:
                components[-1]['name'] = components[-1]['name'][0:7] + "1 " + components[-1]['name'][7:]

        components.append(camera_data)
        i += 1

    station_json['components'] = components

    maintainers = []
    i = 1
    while True:
        maintainer = station_info.get('maintainer' + str(i))
        if maintainer == None:
            break

        maintainer_data = {}
        for key in maintainer:
            maintainer_data[key] = maintainer[key]
        maintainers.append(maintainer_data)
        i += 1
    station_json['maintainers'] = maintainers

    logger.debug("Status data gathered.")
    logger.debug("Status:\n" + pprint.pformat(station_json))

    return json.dumps(station_json)

def station_register(station_json):
    logger = logging.getLogger("Utils")

    try:
        logger.info("Registering station...")

        response = requests.post(config.URL_REGISTER, data={ 'json' : station_json }, verify=False)
        response.raise_for_status()

        security_token = response.text
        if response.text == '' or response.text == 'failure':
            security_token = None
            logger.warning("Server refused registration.")
        else:
            logger.info("Station registered successfully.")

        return security_token
    except requests.exceptions.ConnectionError:
        logger.warning("Could not connect to the registration server.")
    except requests.exceptions.RequestException:
        logger.warning("The registration server returned an error.")

    return None

def get_security_token():
    path = join(dirname(__file__), config.SECURITY_TOKEN_FILENAME)
    if exists(path):
        with open(path, 'r') as security_token_file:
            content = security_token_file.readlines()
            if len(content) == 1:
                content = content[0].split('=')
                if len(content) == 2:
                    return content[1]
    return None

def set_security_token(security_token):
    path = join(dirname(__file__), config.SECURITY_TOKEN_FILENAME)
    with open(path, 'w') as security_token_file:
        security_token_file.write('security_token=' + str(security_token))
