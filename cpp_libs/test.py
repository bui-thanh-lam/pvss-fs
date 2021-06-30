import ctypes
import sys
import os
# os.add_dll_directory(os.path.realpath(__file__))

dir_path = os.path.dirname(os.path.realpath(__file__))
handle = ctypes.CDLL(dir_path + "\libTest.so")

handle.My_Function.argtypes = [ctypes.c_int]


def My_Function(num):
    return handle.My_Function(num)

My_Function(10)