'''

    Available functions:
        - init()
        - end()
        - camera_switch(true/false)
        - server_register()
        - server_send_info()

    Each returns True/False depending on success.

'''

from .server import server
from .ucontroller import ucontroller
from . import station_info
import traceback

def get_trace(exception):
    return str(''.join(traceback.format_tb(exception.__traceback__))) + str(exception)

def init():
    try:
        station_info.init()
        ucontroller.init()
        return True
    except Exception as e:
        print("ERROR: " + str(e))
        return False

def end():
    try:
        ucontroller.end()
        return True
    except Exception as e:
        print("ERROR: " + str(e))
        return False

def server_register():
    try:
        server.register(station_info.get())
        return True
    except Exception as e:
        print("ERROR: " + str(e))
        return False

def server_send_info():
    try:
        server.send_info(station_info.get())
        return True
    except Exception as e:
        print("ERROR: " + str(e))
        server.send_error(get_trace(e))
        return False

def camera_switch(turn_on):
    try:
        ucontroller.camera_switch(turn_on)
        return True
    except Exception as e:
        print("ERROR: " + str(e))
        server.send_error(get_error(e))
        return False
