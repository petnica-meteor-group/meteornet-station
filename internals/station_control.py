import logging
import time
import random
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    import requests
except ImportError:
    try:
        from pip._internal import main
    except ImportError:
        from pip import main
    main(['install', 'requests'])

from .info_uploader.info_uploader import InfoUploader
from .station_config.station_config import StationConfig
from .ucontroller.ucontroller import UController
from .updater.updater import Updater
from .updater.updater import UpdateFailed
from .utils import get_info, is_night, sleep, get_trace, register
from . import constants

def do_work(info_uploader, station_config, ucontroller, camera_on, errors_and_timestamps):
    for error, timestamp in errors_and_timestamps:
        info_uploader.queue_error(error, timestamp)
    info_uploader.queue_info(get_info(station_config, ucontroller), int(time.time()))

    if is_night() and not camera_on:
        ucontroller.camera_switch(True)
        camera_on = True
    elif not is_night() and camera_on:
        ucontroller.camera_switch(False)
        camera_on = False

    return camera_on

def run():
    format = '[%(asctime)s] [%(levelname)-7s] %(name)30s: %(message)-80s'
    datefmt = '%Y/%m/%d %H:%M:%S'
    if constants.DEBUG:
        level=logging.DEBUG
    else:
        level=logging.INFO
    logging.basicConfig(level=level, format=format, datefmt=datefmt)

    logger = logging.getLogger("StationControl")
    logger.info("Starting control & telemetry")

    registered = False
    id = None
    update_failed = False
    camera_on = not is_night()
    errors_and_timestamps = []
    while True:
        try:
            with Updater(constants.PROJECT_PATH, constants.MAIN_FILENAME, constants.URL_UPDATE,
                        constants.PRESERVE_FILES, constants.VERSION, constants.URL_VERSION) as updater:
                try:
                    if not update_failed and updater.update_required():
                        updater.update()
                    else:
                        update_failed = False
                        with StationConfig(constants.STATION_INFO_FILEPATH) as station_config, \
                             UController(constants.DEBUG) as ucontroller:
                            while True:
                                if not registered:
                                    id = register(station_config, ucontroller)
                                    if id == None:
                                        logger.warning("Failed to register. Will retry later.")
                                        sleep()
                                    else:
                                        break

                            with InfoUploader(constants.URL_INFO, constants.URL_ERROR, id) as info_uploader:
                                while True:
                                    camera_on = do_work(info_uploader, station_config, ucontroller, camera_on, errors_and_timestamps)
                                    sleep()

                                    if updater.update_required():
                                        break

                        updater.update()
                except UpdateFailed:
                    update_failed = True
                    logger.warning("Update failed. Continuing with old version.")

        except KeyboardInterrupt:
            logger.info("Ending control & telemetry")
            break
        except Exception as e:
            logger.error("Unhandled exception occured:")
            print(get_trace(e))
            errors_and_timestamps.append((get_trace(e), int(time.time())))
            logger.error("Waiting before restart.")
            try:
                sleep()
            except KeyboardInterrupt:
                logger.info("Ending control & telemetry")
                break
            logger.info("Restarting.")
