from os.path import dirname
from .info_uploader import info_uploader

DEBUG = True

# In minutes
if DEBUG:
    WAKEUP_PERIOD_MIN = 0.05
    WAKEUP_PERIOD_MAX = 0.10
else:
    WAKEUP_PERIOD_MIN = 30
    WAKEUP_PERIOD_MAX = 60

PROJECT_PATH = dirname(dirname(__file__))
MAIN_FILENAME = 'start.py'

VERSION = '1.0.0.1'

STATION_INFO_FILENAME = 'station_info.cfg'
STATION_INFO_FILEPATH = PROJECT_PATH + '/' + STATION_INFO_FILENAME

NIGHT_START = '19:00'
NIGHT_END = '06:30'

PRESERVE_FILES = [ STATION_INFO_FILENAME, 'info_uploader/' + info_uploader.QUEUE_FILENAME ]

if DEBUG:
    SERVER_URL = "http://0.0.0.0:8000"
else:
    SERVER_URL = "https://meteori.petnica.rs:1143"
URL_REGISTER = SERVER_URL + "/station_register"
URL_INFO     = SERVER_URL + "/station_info"
URL_ERROR    = SERVER_URL + "/station_error"
URL_VERSION  = SERVER_URL + "/station_version"
URL_UPDATE   = SERVER_URL + "/station_update"
