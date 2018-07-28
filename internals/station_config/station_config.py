import configparser
from os.path import dirname, realpath, exists
import sys

STATION_INFO_FILENAME = 'station_info.cfg'
STATION_INFO_FILEPATH = dirname(realpath(sys.argv[0])) + '/' + STATION_INFO_FILENAME

config = configparser.ConfigParser()
config.read(STATION_INFO_FILEPATH)

def input_float(prompt):
    while True:
        try:
            input_data = input(prompt)
            float(input_data)
            return input_data
        except ValueError:
            print("Invalid input, try again.")

def init():
    if not exists(STATION_INFO_FILEPATH):
        # Ask params from user
        try:
            print()
            print("Please input station information.")
            print("--------------------------")
            config['station'] = {}
            config['station']['name'] = input("Station name: ")
            config['station']['latitude'] = input_float("Station latitude (degrees): ")
            config['station']['longitude'] = input_float("Station longitude (degrees): ")
            config['station']['height'] = input_float("Station height (meters): ")
            print()
            print("Please input host information.")
            print("--------------------------")
            config['host'] = {}
            config['host']['name'] = input("Host name: ")
            config['host']['phone'] = input("Host phone (optional): ")
            config['host']['email'] = input("Host email (optional): ")
            config['host']['comment'] = input("A comment about station (optional): ")
            print()
            print("Configuration done. Thank you.")
            print("You may delete " + STATION_INFO_FILENAME + " to reconfigure the information.")
            print()

            # Save config to file
            with open(STATION_INFO_FILEPATH, 'w') as configfile:
                config.write(configfile)
        except KeyboardInterrupt:
            print()
            print("Canceling input.")
            print()
            raise KeyboardInterrupt
    else:
        print("INFO: Using " + STATION_INFO_FILENAME + " for configuration.")

def get(section, param):
    return config[section][param]
