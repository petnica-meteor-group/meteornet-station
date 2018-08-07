import configparser
from os.path import dirname, basename, realpath, exists
import sys
import logging

class StationConfig:

    def __init__(self, config_path):
        config_name = basename(config_path)

        self.logger = logging.getLogger(self.__class__.__name__)

        self.config = configparser.ConfigParser()
        if not exists(config_path):
            # Ask params from user
            try:
                print()
                print("Please input station information.")
                print("--------------------------")
                self.config['station'] = {}
                self.config['station']['name'] = input("Station name: ")
                self.config['station']['latitude'] = self._input_float("Station latitude (degrees): ")
                self.config['station']['longitude'] = self._input_float("Station longitude (degrees): ")
                self.config['station']['height'] = self._input_float("Station height (meters): ")
                print()
                print("Please input host information.")
                print("--------------------------")
                self.config['host'] = {}
                self.config['host']['name'] = input("Host name: ")
                self.config['host']['phone'] = input("Host phone (optional): ")
                self.config['host']['email'] = input("Host email (optional): ")
                self.config['host']['comment'] = input("A comment about station (optional): ")
                print()
                print("Configuration done. Thank you.")
                print("You may delete " + config_name + " to reconfigure the information.")
                print()

                # Save config to file
                with open(config_ath, 'w') as config_file:
                    self.config.write(config_file)
            except KeyboardInterrupt:
                print()
                print("Canceling input.")
                print()
                raise KeyboardInterrupt
        else:
            self.logger.debug("Using " + config_name + " for configuration.")
            self.config.read(config_path)

    def get(self, section, param):
        return self.config[section][param]

    def _input_float(self, prompt):
        while True:
            try:
                input_data = input(prompt)
                float(input_data)
                return input_data
            except ValueError:
                print("Invalid input, try again.")

    @staticmethod
    def get_temp_filelist():
        return []

    def end(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end()
