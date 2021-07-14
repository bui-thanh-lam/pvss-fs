from communication import ServerCommunicator
import ctypes
from config import SERVER_LIB_PATH
import os


class KeyComponent(ctypes.Structure):
    _fields_ = [('k', ctypes.c_char_p), ('x', ctypes.c_int)]


class KeySharing(ctypes.Structure):
    _fields_ = [('N', ctypes.c_int), ('T', ctypes.c_int), ('p', ctypes.c_char_p), ('key_component', KeyComponent)]


class ServerHandler:

    def __init__(self):
        # load lib
        _path = os.path.join(SERVER_LIB_PATH)
        _mod = ctypes.cdll.LoadLibrary(_path)

        #

