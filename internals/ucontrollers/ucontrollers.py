from os.path import dirname, realpath, exists
import ctypes
import sys
import os
import math
import logging
import pprint
import random

class UControllersError(Exception):

    def __init__(self, message, ucontroller_name=""):
        super().__init__(message)
        self.ucontroller_name = ucontroller_name

class UControllers:

    def __init__(self, emulate=False):
        self.ucontrollers_lib = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.emulate = emulate

        lib_path = dirname(realpath(__file__)) + '/ucontrollers'

        # Check if 32 or 64 bit
        if sys.maxsize <= 2**32:
            lib_path += '32'
        else:
            lib_path += '64'

        # Check OS
        if os.name == 'posix':
            lib_path += '.so'
        elif os.name == 'nt':
            lib_path += '.dll'

        if exists(lib_path):
            self.ucontrollers_lib = ctypes.cdll.LoadLibrary(lib_path)
        else:
            error = "Unsupported platform."
            self.logger.error(error)
            raise UControllersError(error)

        if self.ucontrollers_lib == None:
            error = "Could not load the microcontrollers lib."
            self.logger.error(error)
            raise UControllersError(error)

        self.ucontrollers_lib.init.restype = ctypes.c_char_p
        self.ucontrollers_lib.end.restype = ctypes.c_char_p
        self.ucontrollers_lib.get_ucontroller_count.restype = ctypes.c_int
        self.ucontrollers_lib.send_cmd.argtypes = (ctypes.c_uint, ctypes.c_int)
        self.ucontrollers_lib.send_cmd.restype = ctypes.c_char_p

        if self.emulate:
            self.logger.debug("Emulated microcontrollers connected.")
        else:
            self.logger.info("Searching for microcontrollers...")
            self._process_output(self.ucontrollers_lib.init())
            count = self.ucontrollers_lib.get_ucontroller_count()
            self.logger.info("Found {} microcontroller(s).".format(count))

    def daynight_inform(self, is_night):
        if is_night:
            if not self.emulate:
                for i in range(self.ucontrollers_lib.get_ucontroller_count()):
                    self._process_output(self.ucontrollers_lib.send_cmd(i, 0))
            self.logger.info("Microcontrollers informed of night approaching.")
        else:
            if not self.emulate:
                for i in range(self.ucontrollers_lib.get_ucontroller_count()):
                    self._process_output(self.ucontrollers_lib.send_cmd(i, 1))
            self.logger.info("Microcontrollers informed of day approaching.")

    def get_measurements_list(self):
        measurements_list = []

        if self.emulate:
            for i in range(1, 3):
                measurements = { 'name' : 'Emulated ' + str(i), 'data' : {
                        'Temperature' : str(random.uniform(20, 40)) + 'C',
                        'Humidity' : str(random.uniform(30, 90)) + '%',
                        'Camera voltage' : str(random.uniform(11, 13)) + 'V',
                        'PSU' : 'on' if random.random() < 0.5 else 'off'
                    }
                }
                measurements_list.append(measurements)
        else:
            for i in range(self.ucontrollers_lib.get_ucontroller_count()):
                measurements = {}

                output = self._process_output(self.ucontrollers_lib.send_cmd(i, 2))
                measurements['name'] = output.split('\n')[1]

                output = self._process_output(self.ucontrollers_lib.send_cmd(i, 3), measurements['name'])
                measurements['data'] = {}
                for line in output.split('\n')[1:]:
                    if line.strip() == "": continue
                    key, value = line.split(':')
                    measurements['data'][key] = value

                measurements_list.append(measurements)

        self.logger.info("Measurements received:\n" + pprint.pformat(measurements_list))

        return measurements_list

    def _process_output(self, output, ucontroller_name=""):
        output = output.decode('utf-8')
        if "ERROR: " in output:
            error = output.replace("ERROR: ", "")
            self.logger.error(error)
            raise UControllersError(error, ucontroller_name)
        elif "INFO: " in output:
            self.logger.info(output.replace("INFO: ", ""))
        elif "DEBUG: " in output:
            self.logger.debug(output.replace("DEBUG: ", ""))
        return output

    def end(self):
        if self.emulate:
            self.logger.debug("Emulated microcontrollers disconnected.")
        else:
            self._process_output(self.ucontrollers_lib.end())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end()
