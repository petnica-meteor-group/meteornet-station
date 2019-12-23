import logging
import time
import random
import time
import json
from os.path import join

from . import dependencies
import urllib3
import requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from .json_uploader.json_uploader import JsonUploader
from .station_info.station_info import StationInfo
from .ucontrollers.ucontrollers import UControllers, UControllersError
from .updater.updater import Updater, UpdateFailed
from .utils import is_night, sleep, get_trace, station_get_json, station_register, get_security_token, set_security_token
from . import config

def run():
    print(config.WELCOME_MESSAGE)
    errors = []

    format = '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'
    datefmt = '%Y/%m/%d %H:%M:%S'
    if config.DEBUG:
        level=logging.DEBUG
    else:
        level=logging.INFO
    logging.basicConfig(level=level, format=format, datefmt=datefmt)

    logger = logging.getLogger("StationControl")
    logger.info("Starting control & telemetry")

    while True:
        try:
            with Updater(config) as updater:
                if updater.update_required():
                    updater.update()
                else:
                    needs_update = False
                    with StationInfo(join(config.PROJECT_PATH, config.STATION_INFO_RELPATH)) as station_info, \
                         JsonUploader(config.URL_DATA) as json_uploader:
                        for error in errors: json_uploader.queue(json.dumps(error))
                        errors = []

                        security_token = get_security_token()
                        cameras_on = not is_night()
                        while not needs_update:
                            try:
                                with UControllers(config.EMULATE_UCONTROLLERS) as ucontrollers:
                                    while not needs_update:
                                        if security_token == None:
                                            security_token = station_register(station_get_json(security_token, station_info, ucontrollers))
                                            if security_token == None:
                                                logger.warning("Failed to register. Will retry later.")
                                            else:
                                                set_security_token(security_token)

                                        if security_token != None:
                                            if is_night() and not cameras_on:
                                                ucontrollers.daynight_inform(True)
                                                cameras_on = True
                                            elif not is_night() and cameras_on:
                                                ucontrollers.daynight_inform(False)
                                                cameras_on = False
                                            json_uploader.queue(station_get_json(security_token, station_info, ucontrollers))

                                        sleep()
                                        if updater.update_required():
                                            needs_update = True
                            except UControllersError as e:
                                trace = get_trace(e)
                                if e.ucontroller_name != "": trace = e.ucontroller_name + ":\n" + trace
                                logger.error("Microcontrollers threw an error:\n" + trace)
                                error = { "error" : trace, "component" : "Computer", "timestamp" : int(time.time()) }
                                if security_token != None: error['security_token'] = security_token
                                json_uploader.queue(json.dumps(error))
                                logger.info("Will try to reinitialize microcontrollers later.")
                                sleep()
                                logger.info("Reinitializing...")

                    updater.update()
        except KeyboardInterrupt:
            logger.info("Ending control & telemetry.")
            break
        except UpdateFailed:
            update_failed = True
            logger.warning("Update failed. Waiting before retrying...")
            try:
                sleep()
            except KeyboardInterrupt:
                logger.info("Ending control & telemetry.")
                break
            logger.info("Retrying...")
        except Exception as e:
            trace = get_trace(e)
            logger.error("Unhandled exception occured:\n" + trace)
            error = { "error" : trace, "component" : "Computer", "timestamp" : int(time.time()) }
            if security_token != None: error['security_token'] = security_token
            errors.append(error)
            logger.info("Waiting before restart...")
            try:
                sleep()
            except KeyboardInterrupt:
                logger.info("Ending control & telemetry.")
                break
            logger.info("Restarting...")
