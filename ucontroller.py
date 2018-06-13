from os import path
import ctypes
import sys
import os

ucontroller = None

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

    print(ucontroller.init().decode('utf-8'), end='')
    return True

def end():
    global ucontroller
    print(ucontroller.end().decode('utf-8'), end='')

def get_dht_info():
    global ucontroller
    output = ucontroller.send_cmd(4).decode('utf-8').split('\n')[1].split(' ')
    humidity = output[0]
    temperature = output[1]

    print("DHT returned humidity = {}, and temperature = {}".format(humidity, temperature))

    return humidity, temperature

def camera_switch(turn_on):
    global ucontroller
    if turn_on:
        ucontroller.send_cmd(0)
        ucontroller.send_cmd(2)
    else:
        ucontroller.send_cmd(1)
        ucontroller.send_cmd(3)

    print("Camera switched on")

    return turn_on, turn_on
