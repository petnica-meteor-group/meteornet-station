from os import path
import ctypes
import sys
import os

ucontroller = None

class UControllerError(Exception):
    pass

def check_errors(output):
    output = output.decode('utf-8')
    if "ERROR" in output: raise UControllerError(output)
    return output

def init():
    global ucontroller

    lib_path = path.dirname(path.realpath(__file__)) + "/ucontroller"

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

    if path.exists(lib_path):
        ucontroller = ctypes.cdll.LoadLibrary(lib_path)

    if ucontroller == None:
        print("Unsupported platform.")
        return False

    ucontroller.init.restype = ctypes.c_char_p
    ucontroller.end.restype = ctypes.c_char_p
    ucontroller.send_cmd.argtypes = (ctypes.c_int,)
    ucontroller.send_cmd.restype = ctypes.c_char_p

    if ucontroller == None:
        print("Error initializing microcontroller.")
        return False

    output = ucontroller.init().decode('utf-8')
    print(output, end='')
    if "ERROR" in output:
        return False
    else:
        return True

def end():
    global ucontroller

    print(ucontroller.end().decode('utf-8'), end='')

def get_dht_info():
    global ucontroller

    output = check_errors(ucontroller.send_cmd(4))

    output = output.split('\n')[1].split(' ')
    humidity = output[0]
    temperature = output[1]

    print("DHT returned humidity = {}, and temperature = {}".format(humidity, temperature))

    return humidity, temperature

def camera_switch(turn_on):
    global ucontroller

    if turn_on:
        check_errors(ucontroller.send_cmd(0))
        check_errors(ucontroller.send_cmd(2))
    else:
        check_errors(ucontroller.send_cmd(1))
        check_errors(ucontroller.send_cmd(3))

    print("Camera switched on")

    return turn_on, turn_on
