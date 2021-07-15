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
        if (self.client_id != None):
            print("get client id successful")
        else:
            print('cannot get client id')
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

        self.share = None

        self.decrypt_key = None
        self.encrypt_key = None

    def encrypt_file(self, plain_file_path, cipher_file_path):
        """Encrypt file by AES in CTR mode

            Args:
                plain_file_path (str): the path to the plain file to encrypt
                cipher_file_path (str): the path to store cipher file after encryption

            Return:
                key (str): the aes key in hex code
        """
        print("encrypting . . .")
        plain_file_path = ctypes.c_char_p(plain_file_path.encode("utf-8"))
        cipher_file_path = ctypes.c_char_p(cipher_file_path.encode("utf-8"))
        key = self.encryptor(plain_file_path, cipher_file_path).decode("utf-8")
        print("encrypt successful")
        self.encrypt_key = {}
        self.encrypt_key["key"] = key
        self.encrypt_key["plain_file_path"] = plain_file_path.value.decode("utf-8")
        self.encrypt_key["cipher_file_path"] = cipher_file_path.value.decode("utf-8")
        os.remove(self.encrypt_key["plain_file_path"])

    def decrypt_file(self, cipher_file_path, plain_file_path, key):
        """Decrypt file by AES in CTR mode

            Args:
                cipher_file_path (str): the path to the stored cipher file to decrypt
                plain_file_path (str): the path to desired plain file after decryption
                key (str): the a AES key in hex code
        """
        if self.key == None:
            print("You do not have key")
        else:
            print("decrypting file . . . ")
            cipher_file_path = ctypes.c_char_p(self.decrypt_key["cipher_file_path"].encode("utf-8"))
            plain_file_path = ctypes.c_char_p(self.decrypt_key["plain_file_path"].encode("utf-8"))
            key = ctypes.c_char_p(self.decrypt_key["key"].encode("utf-8"))
            self.decryptor(cipher_file_path, plain_file_path, key)
            print("decrypt successful")

    def send_key(self):
        if self.encrypt_key == None:
            print("You do not have key to send")
        else:
            AES_key = {}
            AES_key["key"] = self.encrypt_key["key"]
            AES_key["client_id"] = str(self.client_id)
            AES_key["plain_file_path"] = self.encrypt_key["plain_file_path"]
            AES_key["cipher_file_path"] = self.encrypt_key["cipher_file_path"]
            self.encrypt_key = None
            AES_key = json.dumps(AES_key)
            r = requests.post(config.API_ENDPOINT + "send_key/", data=AES_key)
            print(r.json())

    def get_share(self):
        r = requests.get(config.API_ENDPOINT + "get_share/", params={'client_id': self.client_id})
        if r.json() != None:
            self.share = r.json()
            print("get share successful")
        else:
            print("cannot get share")

    def send_share(self):
        if self.share == None:
            print("You have not received the share")
        else:
            self.share["client_id"] = self.client_id
            share = json.dumps(self.share)
            r = requests.post(config.API_ENDPOINT + "send_share/", data=share)
            print(r.json())

    def request_open(self):
        r = requests.get(config.API_ENDPOINT + "request_open/", params={'client_id': self.client_id})
        print(r.json())

    def send_file(self, file_path=config.TEST_DOCUMENT_PATH):
        f = open(file_path, 'rb')
        requests.post(
            config.API_ENDPOINT + "send_file/",
            params={
                'client_id': self.client_id
            },
            files={
                'file': ('test.txt', f, 'multipart/form-data'),
            }
        )

    def download_file(self):
        response = requests.get(
            config.API_ENDPOINT + "download_file/",
            params={
                'client_id': self.client_id
            }
        )
        print(response.content.decode("utf-8"))

    def get_key(self):
        r = requests.get(config.API_ENDPOINT + "get_key/", params={'client_id': self.client_id})
        resp = r.json()
        if resp["status_code"] == 100:
            print("client id is not exist")
        elif resp["status_code"] == 200:
            print("client id is not owner")
        elif resp["status_code"] == 300:
            print("do not collect enough share")
        else:
            print("get key successful")
            self.decrypt_key = resp
