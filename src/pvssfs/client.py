import os
import config
import requests
import ctypes
import json


class ClientHandler:
    """ Handling all clients' behavior.

    Methods:
        encrypt_file(plain_file_path, cipher_file_path): encrypt a plain file
        encrypt_file(cipher_file_path, plain_file_path, key): decrypt a cipher file

    """

    def __init__(self):
        self.client_id = requests.get(config.API_ENDPOINT + "get_client_id/").json()["client_id"]

        # load lib
        _path = os.path.join(config.CLIENT_LIB_PATH)
        _mod = ctypes.cdll.LoadLibrary(_path)

        # char *Encrypt_File(char *input, char *output)
        self.encryptor = _mod.Encrypt_File
        self.encryptor.argtypes = (ctypes.c_char_p, ctypes.c_char_p)
        self.encryptor.restype = ctypes.c_char_p

        # void Decrypt_File(char* input, char* output, char* key_c)
        self.decryptor = _mod.Decrypt_File
        self.decryptor.argtypes = (ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p)
        self.decryptor.restype = ctypes.c_void_p

    def encrypt_file(self, plain_file_path, cipher_file_path):
        """Encrypt file by AES in CTR mode

            Args:
                plain_file_path (str): the path to the plain file to encrypt
                cipher_file_path (str): the path to store cipher file after encryption

            Return:
                key (str): the aes key in hex code
        """
        plain_file_path = ctypes.c_char_p(plain_file_path.encode("utf-8"))
        cipher_file_path = ctypes.c_char_p(cipher_file_path.encode("utf-8"))
        key = self.encryptor(plain_file_path, cipher_file_path).decode("utf-8")
        self.send_key(key, plain_file_path.value.decode("utf-8"), cipher_file_path.value.decode("utf-8"))

    def decrypt_file(self, cipher_file_path, plain_file_path, key):
        """Decrypt file by AES in CTR mode

            Args:
                cipher_file_path (str): the path to the stored cipher file to decrypt
                plain_file_path (str): the path to desired plain file after decryption
                key (str): the a AES key in hex code
        """

        cipher_file_path = ctypes.c_char_p(cipher_file_path.encode("utf-8"))
        plain_file_path = ctypes.c_char_p(plain_file_path.encode("utf-8"))
        key = ctypes.c_char_p(key.encode("utf-8"))
        return self.decryptor(cipher_file_path, plain_file_path, key)

    def send_key(self, key, plain_file_path, cipher_file_path):
        AES_key = {}
        AES_key["key"] = key
        AES_key["client_id"] = self.client_id
        AES_key["plain_file_path"] = plain_file_path
        AES_key["cipher_file_path"] = cipher_file_path
        AES_key = json.dumps(AES_key)
        print(AES_key)
        r = requests.post(config.API_ENDPOINT+"send_key/", data = AES_key)

    def send_share(self, share):
        pass

    def get_key(self):
        pass

    def get_share(self):
        pass
    
    def request_open(self):
        pass

    def send_file(self, file_path=config.TEST_DOCUMENT_PATH):
        f = open(file_path, 'rb')
        requests.post(
            config.API_ENDPOINT + "send_file/",
            params={
                'client_id': 0
            },
            files={
                'file': ('test.txt', f, 'multipart/form-data'),
            }
        )
    
    def download_file(self):
        pass

