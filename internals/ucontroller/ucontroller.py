from os.path import dirname, realpath, exists
import ctypes
import sys
import os

ucontroller = None

class UControllerError(Exception):
    pass

def check_errors(output):
    output = output.decode('utf-8')
    if "ERROR" in output: raise UControllerError(output.replace("ERROR: ", ""))
    return output

def init():
    global ucontroller

    lib_path = dirname(realpath(__file__)) + "/ucontroller"

    # Check if 32 or 64 bit
    if sys.maxsize <= 2**32:
        lib_path += "32"
    else:
        lib_path += "64"

    # Check OS
    if os.name == 'posix':
        lib_path += '.so'
    elif os.name == 'nt':
        lib_path += '.dll'

    if exists(lib_path):
        ucontroller = ctypes.cdll.LoadLibrary(lib_path)

    if ucontroller == None:
        raise UControllerError("ERROR: Unsupported platform.")

    ucontroller.init.restype = ctypes.c_char_p
    ucontroller.end.restype = ctypes.c_char_p
    ucontroller.send_cmd.argtypes = (ctypes.c_int,)
    ucontroller.send_cmd.restype = ctypes.c_char_p

    if ucontroller == None:
        raise UControllerError("ERROR: Could not initialize microcontroller.")

    print(check_errors(ucontroller.init()))

def end():
    global ucontroller
    print(check_errors(ucontroller.end()))

def get_dht_info():
    global ucontroller

    output = check_errors(ucontroller.send_cmd(4))

    output = output.split('\n')[1].split(' ')
    humidity = output[0]
    temperature = output[1]
    humidity = '30'
    temperature = '20'

    print("INFO: Humidity = {}, Temperature = {}".format(humidity, temperature))

    return humidity, temperature

def camera_switch(turn_on):
    global ucontroller

    if turn_on:
        check_errors(ucontroller.send_cmd(0))
        check_errors(ucontroller.send_cmd(2))
        print("INFO: Camera turned on")
    else:
        check_errors(ucontroller.send_cmd(1))
        check_errors(ucontroller.send_cmd(3))
        print("INFO: Camera turned off")
