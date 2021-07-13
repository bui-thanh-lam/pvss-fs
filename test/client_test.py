from ctypes import *
import os

# load lib
_file = 'Client_Lib.so'
_path = os.path.join("/home/lam-bui/Documents/Projects/ATTT/BTL/pvss-fs/test/client.so")
_mod = cdll.LoadLibrary(_path)

# char *Encrypt_File(char *input, char *output)
Encrypt_File = _mod.Encrypt_File
Encrypt_File.argtypes = (c_char_p, c_char_p)
Encrypt_File.restype = c_char_p

# void Decrypt_File(char* input, char* output, char* key_c)
Decrypt_File = _mod.Decrypt_File
Decrypt_File.argtypes = (c_char_p, c_char_p, c_char_p)
Decrypt_File.restype = c_void_p

def AES_Encrypt(input, output):
    input = c_char_p(input.encode("utf-8"))
    output = c_char_p(output.encode("utf-8"))
    return Encrypt_File(input, output).decode("utf-8")

def AES_Decrypt(input, output, key):
    input = c_char_p(input.encode("utf-8"))
    output = c_char_p(output.encode("utf-8"))
    key = c_char_p(key.encode("utf-8"))
    Decrypt_File(input, output, key)


input = "test4.txt"
encrypted = "encrypted.txt"
recovered = "recovered.txt"
key = "7AF781D3377048287B1C1C69C846A8DF"

# print(AES_Encrypt(input, encrypted))
AES_Decrypt(encrypted, recovered, key)