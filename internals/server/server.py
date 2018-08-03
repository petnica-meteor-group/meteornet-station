import requests
import datetime

SERVER_URL = "https://meteori.petnica.rs:1143"
URL_REGISTER = SERVER_URL + "/station_register"
URL_UPDATE   = SERVER_URL + "/station_update"
URL_ERROR    = SERVER_URL + "/station_error"

id = None
errors = []

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def flush_errors():
    global id
    global errors

    if len(errors) > 0:
        print("INFO: Sending error(s) to the server...")
        errors_sent = []

        for error in errors:
            if id != None:
                error_data = { 'id' : id, 'error' : error }
            else:
                error_data = {            'error' : error }
                requests.post(URL_ERROR, data=error_data, verify=False)
                errors_sent.append(error)

            print("INFO: Error(s) sent successfully.")

        errors = [error for error in errors if error not in errors_sent]

def register(info):
    global id

    try:
        print("INFO: Registering station... ({})".format(datetime.datetime.now().replace(microsecond=0)))

        data = { 'data' : info }
        request = requests.post(URL_REGISTER, data=data, verify=False)
        id = request.text

        print("INFO: Station registration successful.")
    except requests.ConnectionError:
        print("WARNING: Could not connect to the server.")

def send_info(info):
    global id

    try:
        flush_errors()

        print("INFO: Sending station information... ({})".format(datetime.datetime.now().replace(microsecond=0)))
        if id == None:
            print("ERROR: Station not registered.")
            return

        data = { 'id' : id, 'data' : info }
        request = requests.post(URL_UPDATE, data=data, verify=False)

        print("INFO: Station information sent successfully.")
    except requests.ConnectionError:
        print("WARNING: Could not connect to the server.")

def send_error(error):
    global errors

    try:
        errors.append(error)
        flush_errors()
    except requests.ConnectionError:
        print("WARNING: Could not connect to the server.")
