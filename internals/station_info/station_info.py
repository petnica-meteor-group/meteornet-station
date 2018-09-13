import configparser
from os.path import dirname, basename, realpath, exists
import sys
import logging

class StationInfo:

    def __init__(self, info_path):
        info_name = basename(info_path)

        self.logger = logging.getLogger(self.__class__.__name__)

        self.config = configparser.ConfigParser()
        if not exists(info_path):
            # Ask params from user
            try:
                print()
                print("Please input station information.")
                print("--------------------------")
                station = {}
                station['name'] = input("Station name: ")
                station['latitude'] = self._input_float("Station latitude (degrees, decimal): ")
                station['longitude'] = self._input_float("Station longitude (degrees, decimal): ")
                station['height'] = self._input_float("Station height (meters): ")
                station['comment'] = input("A comment about station (optional): ")
                self.config['station'] = station
                print()
                print("Please input maintainers' information.")
                print("--------------------------")
                i = 1
                while True:
                    maintainer = {}
                    maintainer['name'] = input("Maintainer name: ")
                    maintainer['phone'] = input("Maintainer phone (optional): ")
                    maintainer['email'] = input("Maintainer email (optional): ")
                    self.config['maintainer' + str(i)] = maintainer
                    i += 1
                    if not self._input_yesno("Add more maintainers? "):
                        break
                print()
                print("Information input done. Thank you.")
                print("You may edit " + info_name + " or delete it to input information again.")
                print()

                # Save config to file
                with open(info_path, 'w') as info_file:
                    self.config.write(info_file)
            except KeyboardInterrupt:
                print()
                print("Canceling input.")
                print()
                raise KeyboardInterrupt
        else:
            self.logger.debug("Using " + info_name + " for station information.")
            self.config.read(info_path)

    def get(self, section, param=None):
        if section in self.config:
            if param == None:
                return self.config[section]
            elif param in self.config[section]:
                return self.config[section][param]
        return None

    def _input_float(self, prompt):
        while True:
            try:
                input_data = input(prompt)
                float(input_data)
                return input_data
            except ValueError:
                print("Invalid input, try again.")

    def _input_yesno(self, prompt):
        yesno = ""
        while yesno != "y" and yesno != "n":
            if yesno != "": print("Invalid input, try again.")
            yesno = input(prompt + "(Y/N) ").lower()
        return yesno == "y"

    def end(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end()
