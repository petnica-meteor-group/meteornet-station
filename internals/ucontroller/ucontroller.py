from os.path import dirname, realpath, exists
import ctypes
import sys
import os
import math
import logging

class UControllerError(Exception):
    pass

class UController:

    def __init__(self, emulate=False):
        self.ucontroller = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.emulate = emulate

        lib_path = dirname(realpath(__file__)) + '/ucontroller'

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
            self.ucontroller = ctypes.cdll.LoadLibrary(lib_path)
        else:
            error = "Unsupported platform."
            self.logger.error(error)
            raise UControllerError(error)

        if self.ucontroller == None:
            error = "Could not initialize microcontroller."
            self.logger.error(error)
            raise UControllerError(error)

        self.ucontroller.init.restype = ctypes.c_char_p
        self.ucontroller.end.restype = ctypes.c_char_p
        self.ucontroller.send_cmd.argtypes = (ctypes.c_int,)
        self.ucontroller.send_cmd.restype = ctypes.c_char_p

        if self.emulate:
            self.logger.debug("Emulated microcontrolled connected.")
        else:
            self._process_output(self.ucontroller.init())

    def get_dht_info(self):
        if self.emulate:
            output = "Command sent.\n50 30"
        else:
            output = self._process_output(self.ucontroller.send_cmd(4))

        output = output.split('\n')
        if len(output) > 1: output = output[1].split(' ')
        if len(output) > 1:
            humidity = output[0]
            temperature = output[1]
        else:
            humidity = math.nan
            temperature = math.nan

        self.logger.info("Humidity = {}, Temperature = {}".format(humidity, temperature))

        return humidity, temperature

    def check_power_supply(self):
        if self.emulate:
            output = "Command sent.\n1"
        else:
            output = self._process_output(self.ucontroller.send_cmd(5))

        on = False
        output = output.split('\n')
        if len(output) > 1:
            on = int(output[1]) > 0

        if on:
            self.logger.info("Power supply on.")
        else:
            self.logger.info("Power supply off.")

        return on

    def camera_switch(self, turn_on):
        if turn_on:
            if not self.emulate:
                self._process_output(self.ucontroller.send_cmd(0))
                self._process_output(self.ucontroller.send_cmd(2))
            self.logger.info("Camera turned on.")
        else:
            if not self.emulate:
                self._process_output(self.ucontroller.send_cmd(1))
                self._process_output(self.ucontroller.send_cmd(3))
            self.logger.info("Camera turned off.")

    def _process_output(self, output):
        output = output.decode('utf-8')
        if "ERROR: " in output:
            error = output.replace("ERROR: ", "")
            self.logger.error(error)
            raise UControllerError(error)
        elif "INFO: " in output:
            self.logger.info(output.replace("INFO: ", ""))
        elif "DEBUG: " in output:
            self.logger.debug(output.replace("DEBUG: ", ""))
        return output

    def end(self):
        if self.emulate:
            self.logger.debug("Emulated microcontroller disconnected.")
        else:
            self._process_output(self.ucontroller.end())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end()
