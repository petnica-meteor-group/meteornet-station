from shutil import disk_usage
import traceback
import time
import random
import logging
import requests
import json
import math
from os.path import realpath
from . import constants

def sleep():
    delay = random.randint(int(constants.WAKEUP_PERIOD_MIN * 60), int(constants.WAKEUP_PERIOD_MAX * 60))
    logging.getLogger("Utils").debug("Sleeping for {}.".format(delay))
    time.sleep(delay)

def is_night():
    hours = float(time.strftime("%H"))
    return (constants.NIGHT_START <= hours <= 24) or (0 <= hours <= constants.NIGHT_END)

def get_trace(exception):
    return str(''.join(traceback.format_tb(exception.__traceback__))) + str(exception)

def get_info(station_config, ucontroller):
    name = station_config.get('station', 'name')
    latitude = station_config.get('station', 'latitude')
    longitude = station_config.get('station', 'longitude')
    height = station_config.get('station', 'height')

    total_bytes, used_bytes, free_bytes = disk_usage(realpath('/'))

    disk_used = str(used_bytes / (1024 ** 3))
    disk_cap = str(total_bytes / (1024 ** 3))

    station_info = { 'name' : name, 'disk_used' : disk_used, 'disk_cap' : disk_cap }

    if len(latitude) > 0: station_info['latitude'] = latitude
    if len(longitude) > 0: station_info['longitude'] = longitude
    if len(height) > 0: station_info['height'] = height

    humidity, temperature = ucontroller.get_dht_info()
    humidity = str(humidity)
    temperature = str(temperature)

    try:
        if not math.isnan(float(humidity)):
            station_info['humidity'] = humidity
    except ValueError:
        pass

    try:
        if not math.isnan(float(temperature)):
            station_info['temperature'] = temperature
    except ValueError:
        pass

    host_name = station_config.get('host', 'name')
    host_phone = station_config.get('host', 'phone')
    host_email = station_config.get('host', 'email')
    host_comment = station_config.get('host', 'comment')

    host_info = { 'name' : host_name }
    if len(host_phone) > 0: host_info['phone'] = host_phone
    if len(host_email) > 0: host_info['email'] = host_email
    if len(host_comment) > 0: host_info['comment'] = host_comment

    station_info['host'] = host_info

    return station_info

def register(station_config, ucontroller):
    logger = logging.getLogger("Utils")

    try:
        logger.info("Registering station...")

        data = { 'data' : json.dumps(get_info(station_config, ucontroller)) }
        response = requests.post(constants.URL_REGISTER, data=data, verify=False)
        response.raise_for_status()

        logger.info("Station registered successfully.")
        return response.text
    except requests.exceptions.ConnectionError:
        logger.warning("Could not connect to the registration server.")
    except requests.exceptions.RequestException:
        logger.warning("The registration server returned an error.")

    return None
