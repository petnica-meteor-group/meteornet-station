from shutil import disk_usage
from .station_config import station_config
from .ucontroller import ucontroller
from os.path import realpath
import math

def init():
    station_config.init()

def get():
    name = station_config.get('station', 'name')
    latitude = station_config.get('station', 'latitude')
    longitude = station_config.get('station', 'longitude')
    height = station_config.get('station', 'height')

    total_bytes, used_bytes, free_bytes = disk_usage(realpath('/'))

    disk_used = str(used_bytes / (1024 ** 3))
    disk_cap = str(total_bytes / (1024 ** 3))

    station_info = '''
              "name"        : "{}",
              "disk_used"   : "{}",
              "disk_cap"    : "{}"
              '''.format(name, disk_used, disk_cap)

    if len(latitude) > 0: station_info += ', "latitude" : "' + latitude + '"'
    if len(longitude) > 0: station_info += ', "longitude" : "' + longitude + '"'
    if len(height) > 0: station_info += ', "height" : "' + height + '"'

    humidity, temperature = ucontroller.get_dht_info()
    humidity = str(humidity)
    temperature = str(temperature)

    try:
        if not math.isnan(float(humidity)):
            station_info += ', "humidity" : "' + humidity + '"'
    except ValueError:
        pass

    try:
        if not math.isnan(float(temperature)):
            station_info += ', "temperature" : "' + temperature + '"'
    except ValueError:
        pass

    host_name = station_config.get('host', 'name')
    host_phone = station_config.get('host', 'phone')
    host_email = station_config.get('host', 'email')
    host_comment = station_config.get('host', 'comment')

    host_info = '"name" : "' + host_name + '"'
    if len(host_phone) > 0: host_info += ', "phone" : "' + host_phone + '"'
    if len(host_email) > 0: host_info += ', "email" : "' + host_email + '"'
    if len(host_comment) > 0: host_info += ', "comment" : "' + host_comment + '"'

    station_info = '{ ' + station_info + ', "host": {' + host_info + '} }'

    return station_info
