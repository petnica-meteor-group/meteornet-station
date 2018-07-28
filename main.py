#!/usr/bin/env python3

from time import sleep
from random import randint
import time

try:
    import requests
except ImportError:
    try:
        from pip._internal import main
    except ImportError:
        from pip import main
    main(['install', 'requests'])

from internals import station_control

# In minutes
TELEMETRY_PERIOD_MIN = 30
TELEMETRY_PERIOD_MAX = 60

def is_night():
    hours = float(time.strftime("%H"))
    return (19 <= hours <= 24) or (0 <= hours <= 7)

def delay():
    sleep(randint(int(TELEMETRY_PERIOD_MIN * 60), int(TELEMETRY_PERIOD_MAX * 60)))

def run():
    initialized = False
    registered = False
    camera_on = not is_night()

    print("INFO: Starting control & telemetry.")

    try:
        while True:
            if initialized:
                if is_night() and not camera_on:
                    camera_on = station_control.camera_switch(True)
                    if not camera_on:
                        print("ERROR: Could not turn camera on (it's night). Will retry later automatically.")
                elif not is_night() and camera_on:
                    camera_on = not station_control.camera_switch(False)
                    if camera_on:
                        print("ERROR: Could not turn camera off (it's day). Will retry later automatically.")

                if registered:
                    station_control.server_send_info()
                else:
                    if station_control.server_register():
                        registered = True
                    else:
                        print("WARNING: Could not register station. Will retry later automatically.")
            else:
                if station_control.init():
                    initialized = True
                    continue
                else:
                    print("ERROR: Could not initialize station. Will retry later automatically.")

            delay()

    except KeyboardInterrupt:
        print("INFO: Ending control & telemetry.")

    station_control.end()

if __name__ == "__main__":
    run()
