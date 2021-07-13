from communication import ClientCommunicator
from ctypes import *
import os


class ClientHandler:
    """ Handling all clients' behavior.

    Methods:
        encrypt_file(plain_file_path, cipher_file_path): encrypt a plain file
        eecrypt_file(cipher_file_path, plain_file_path, key): decrypt a cipher file
    
    """

    def __init__(self):
        # load lib
        _file = 'Client_Lib.so'
        _path = os.path.join("../cpp_libs/client.so")
        _mod = cdll.LoadLibrary(_path)

        # char *Encrypt_File(char *input, char *output)
        self.encryptor = _mod.Encrypt_File
        self.encryptor.argtypes = (c_char_p, c_char_p)
        self.encryptor.restype = c_char_p

        # void Decrypt_File(char* input, char* output, char* key_c)
        self.decryptor = _mod.Decrypt_File
        self.decryptor.argtypes = (c_char_p, c_char_p, c_char_p)
        self.decryptor.restype = c_void_p

    def encrypt_file(self, plain_file_path, cipher_file_path):
        """Encrypt file by AES in CTR mode

            Args:
                plain_file_path (str): the path to the plain file to encrypt
                cipher_file_path (str): the path to store cipher file after encryption
            
            Return:
                key (str): the aes key in hex code
        """
        plain_file_path = c_char_p(plain_file_path.encode("utf-8"))
        cipher_file_path = c_char_p(cipher_file_path.encode("utf-8"))
        return self.encryptor(plain_file_path, cipher_file_path).decode("utf-8")

    def decrypt_file(self, cipher_file_path, plain_file_path, key):
        """Decrypt file by AES in CTR mode

            Args:
                cipher_file_path (str): the path to the strored cipher file to decrypt
                plain_file_path (str): the path to desired plain file after decryption
                key (str): the a AES key in hex code
        """
        cipher_file_path = c_char_p(cipher_file_path.encode("utf-8"))
        plain_file_path = c_char_p(plain_file_path.encode("utf-8"))
        key = c_char_p(key.encode("utf-8"))
        return self.decryptor(cipher_file_path, plain_file_path, key)


client = ClientHandler()
client.encrypt_file(
    "../test/test.txt",
    "../test/test.bin"
)