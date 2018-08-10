from os.path import dirname
from .info_uploader import info_uploader
import platform

DEBUG = False
EMULATE_MICROCONTROLLER = DEBUG

# In minutes
if DEBUG:
    WAKEUP_PERIOD_MIN = 0.05
    WAKEUP_PERIOD_MAX = 0.10
else:
    WAKEUP_PERIOD_MIN = 20
    WAKEUP_PERIOD_MAX = 30

PROJECT_PATH = dirname(dirname(__file__))
MAIN_FILENAME = 'start.py'

VERSION = '1.0.0.5'

STATION_INFO_FILENAME = 'station_info.cfg'
STATION_INFO_FILEPATH = PROJECT_PATH + '/' + STATION_INFO_FILENAME

# hh:mm format
NIGHT_START = '19:00'
NIGHT_END = '06:30'

# Preserve the following station specific files after update
PRESERVE_FILES = [ STATION_INFO_FILENAME, 'info_uploader/' + info_uploader.QUEUE_FILENAME ]

if DEBUG:
    SERVER_URL = 'http://0.0.0.0:8000'
else:
    if platform.node() == 'pmg-001':
        SERVER_URL = 'https://10.51.0.54'
    else:
        SERVER_URL = 'https://meteori.petnica.rs:1143'
URL_REGISTER = SERVER_URL + '/station_register'
URL_INFO     = SERVER_URL + '/station_info'
URL_ERROR    = SERVER_URL + '/station_error'
URL_VERSION  = SERVER_URL + '/station_version'
URL_UPDATE   = SERVER_URL + '/station_update'
