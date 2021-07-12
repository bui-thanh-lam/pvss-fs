from communication import ClientCommunicator
from ctypes import *
import os

conn = ClientCommunicator(server_ip='LamBui-ThinkPad-T440s')
conn.receive()


class ClientHandle:
    """ Initiate a link to the *.so file

    Methods:
        Encrypt_File(input_file_path, output_file_path): encrypt file and return a AES key and delete input file
        Decrypt_File(input_file_path, output_file_path, key): decrypt file with a AES key and delete input file
        """

    def __init__(self):
        # load lib
        _file = 'Client_Lib.so'
        _path = os.path.join("/home/lam-bui/Documents/Projects/ATTT/BTL/pvss-fs/test/Client_Lib.so")
        _mod = cdll.LoadLibrary(_path)

        # char *Encrypt_File(char *input, char *output)
        Encrypt_File = _mod.Encrypt_File
        Encrypt_File.argtypes = (c_char_p, c_char_p)
        Encrypt_File.restype = c_char_p

        # void Decrypt_File(char* input, char* output, char* key_c)
        Decrypt_File = _mod.Decrypt_File
        Decrypt_File.argtypes = (c_char_p, c_char_p, c_char_p)
        Decrypt_File.restype = c_void_p
        pass

    def Encryt_File(self, input_file_path, output_file_path):
        """Encrypt file by AES with CTR mode

            Args:
                input_file_path (str): the path of the file need to be encrypted
                output_file_path (str): the path of output file after encrypt
            Return:
                key (str): hex code of aes key used to encrypt file
            """
        pass

    def Decrypt_file(self, input_file_path, output_file_path, key):
        """Decrypt file by AES with CTR mode

            Args:
                input_file_path (str): the path of the file need to be decrypted
                output_file_path (str): the path of output file after decrypt
                key: hex code of aes key to decrypt input file
            """
        pass


