from ctypes import *
import os


_file = 'Client_Lib.so'
_path = os.path.join(*(os.path.split(__file__)[:-1] + (_file, )))
_mod = cdll.LoadLibrary(_path)


# char *Encrypt_File(char *input, char *output)
Encrypt_File = _mod.Encrypt_File
Encrypt_File.argtypes = (c_char_p, c_char_p)
Encrypt_File.restype = c_char_p

def AES_Encrypt(input, output):
    input = c_char_p(input.encode("utf-8"))
    output = c_char_p(output.encode("utf-8"))
    key = Encrypt_File(input, output)
    return key


input = "text.txt"
output = "decrypt.txt"
key = AES_Encrypt(input, output)
print(key)