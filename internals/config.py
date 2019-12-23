import os
from os.path import dirname, basename, join, abspath, relpath
import platform
from datetime import date, datetime

from .json_uploader import json_uploader

DEBUG = os.environ['DEBUG'] == 'True' if 'DEBUG' in os.environ else False
EMULATE_UCONTROLLERS = DEBUG

VERSION = '1.0.3.5'

PROJECT_PATH = dirname(dirname(abspath(__file__)))
CONFIG_RELPATH = relpath(abspath(__file__), PROJECT_PATH)
MAIN_RELPATH = 'start.py'
STATION_INFO_RELPATH = 'station_info.cfg'
SECURITY_TOKEN_RELPATH = join(dirname(CONFIG_RELPATH), 'security_token.cfg')

# In minutes
if DEBUG:
    WAKEUP_PERIOD_MIN = 0.05
    WAKEUP_PERIOD_MAX = 0.10
else:
    WAKEUP_PERIOD_MIN = 20
    WAKEUP_PERIOD_MAX = 30

# hh:mm format
def GET_NIGHT_INTERVAL(when):
    Y = 2000 # dummy leap year to allow input X-02-29 (leap day)
    SEASONS = [('winter', (date(Y,  1,  1),  date(Y,  3, 20)), ('16:00', '08:00')),
               ('spring', (date(Y,  3, 21),  date(Y,  6, 20)), ('18:00', '07:00')),
               ('summer', (date(Y,  6, 21),  date(Y,  9, 22)), ('19:00', '06:00')),
               ('autumn', (date(Y,  9, 23),  date(Y, 12, 20)), ('17:00', '07:00')),
               ('winter', (date(Y, 12, 21),  date(Y, 12, 31)), ('16:00', '08:00'))]

    if isinstance(when, datetime):
        when = when.date()
    when = when.replace(year=Y)
    return next(nighttime for season, (start, end), nighttime in SEASONS if start <= when <= end)

# Preserve the following station specific files after update
PRESERVE_FILES = [
    STATION_INFO_RELPATH,
    join(CONFIG_RELPATH, 'json_uploader', json_uploader.JsonUploader.DB_FILENAME),
    SECURITY_TOKEN_RELPATH
]

if DEBUG:
    SERVER_URL = 'http://0.0.0.0:8000'
else:
    if platform.node() == 'pmg-001':
        SERVER_URL = 'https://10.51.0.54'
    else:
        SERVER_URL = 'https://meteori.petnica.rs:1143'
URL_REGISTER        = SERVER_URL + '/station_register'
URL_DATA            = SERVER_URL + '/station_data'
URL_VERSION         = SERVER_URL + '/station_version'
URL_CODE_DOWNLOAD   = SERVER_URL + '/station_code_download'

WELCOME_MESSAGE = """
          * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
          *                  ______ ___  ___ _____                  *
          *                  | ___ \|  \/  ||  __ \                 *
          *                  | |_/ /| .  . || |  \/                 *
          *                  |  __/ | |\/| || | __                  *
          *                  | |    | |  | || |_\ \                 *
          *                  \_|    \_|  |_/ \____/                 *
          *                  Meteor network station                 *
          *                                                         *
          *                        v{}                         *
          *                                                         *
          * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
""".format(VERSION)
