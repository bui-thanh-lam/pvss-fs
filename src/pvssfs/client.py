import os
import pvssfs.config as config
import requests
import ctypes
import json


class ClientHandler:

    def __init__(self):
        self._get_client_id()
        
        # load lib
        _path = os.path.join(config.CONFIG["CLIENT_LIB_PATH"])
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

        self.__decrypt_key = None
        self.__encrypt_key = None

    def _get_client_id(self):
        r = requests.get(config.CONFIG["API_ENDPOINT"] + "get_client_id/")
        self._log(r)
        self.client_id = r.json()["client_id"]
        
    def _log(self, r):
        print(f"Response from server: {r.status_code}")


    def encrypt_file(
        self,
        plain_file_path=config.CONFIG["TEST_DOCUMENT_PATH"], 
        cipher_file_path=config.CONFIG["TEST_DECRYPTED_DOC_PATH"]
    ):
        """Encrypt file by AES in CTR mode

            Args:
                plain_file_path (str): the path to the plain file to encrypt
                cipher_file_path (str): the path to store cipher file after encryption

            Return:
                key (str): the aes key in hex code
        """
        print("Encrypting . . .")
        plain_file_path = ctypes.c_char_p(plain_file_path.encode("utf-8"))
        cipher_file_path = ctypes.c_char_p(cipher_file_path.encode("utf-8"))
        key = self.encryptor(plain_file_path, cipher_file_path).decode("utf-8")
        print("Finish encryption")
        self.__encrypt_key = {}
        self.__encrypt_key["key"] = key
        self.__encrypt_key["plain_file_path"] = plain_file_path.value.decode("utf-8")
        self.__encrypt_key["cipher_file_path"] = cipher_file_path.value.decode("utf-8")
        os.remove(self.__encrypt_key["plain_file_path"])

    def decrypt_file(self):
        """Decrypt file by AES in CTR mode

            Args:
                cipher_file_path (str): the path to the stored cipher file to decrypt
                plain_file_path (str): the path to desired plain file after decryption
                key (str): the a AES key in hex code
        """
        if self.__decrypt_key == None:
            print("You do not have the key to decrypt. Please send a open request to server to get the key.")
        else:
            print("Decrypting file . . . ")
            cipher_file_path = ctypes.c_char_p(self.__decrypt_key["cipher_file_path"].encode("utf-8"))
            plain_file_path = ctypes.c_char_p(self.__decrypt_key["plain_file_path"].encode("utf-8"))
            key = ctypes.c_char_p(self.__decrypt_key["key"].encode("utf-8"))
            self.decryptor(cipher_file_path, plain_file_path, key)
            print("Finish decryption")
            os.remove(self.__decrypt_key["cipher_file_path"])

    def send_key(self):
        if self.__encrypt_key == None:
            print("You do not have a key to send. Please encrypt your file first.")
        else:
            AES_key = {}
            AES_key["key"] = self.__encrypt_key["key"]
            AES_key["client_id"] = str(self.client_id)
            AES_key["plain_file_path"] = self.__encrypt_key["plain_file_path"]
            AES_key["cipher_file_path"] = self.__encrypt_key["cipher_file_path"]
            self.__encrypt_key = None
            AES_key = json.dumps(AES_key)
            r = requests.post(config.CONFIG["API_ENDPOINT"] + "send_key/", data=AES_key)
            self._log(r)

    def get_share(self):
        r = requests.get(config.CONFIG["API_ENDPOINT"] + "get_share/", params={'client_id': self.client_id})
        self._log(r) 
        try:
            self.share = r.json()
        except json.decoder.JSONDecodeError as e:
            raise e
            
    def send_share(self):
        if self.share == None:
            print("You have not received your share yet. Please get your share from server first.")
        else:
            share = self.share
            share["client_id"] = self.client_id
            share = json.dumps(self.share)
            r = requests.post(config.CONFIG["API_ENDPOINT"] + "send_share/", data=share)
            self._log(r) 

    def request_open(self):
        if self.share is None:
            print("You or other shareholders have not received your/their share yet. Please wait util all shareholders have received their share.")
        else:
            r = requests.post(
                config.CONFIG["API_ENDPOINT"] + "request_open/", 
                params={
                    'client_id': self.client_id
                }
            )
            self._log(r)

    def send_file(self):
        if(self.__decrypt_key == None):
            print("You cannot send file")
        else:
            file_name = os.path.basename(self.__decrypt_key["plain_file_path"])
            f = open(self.__decrypt_key["plain_file_path"], 'rb')
            r = requests.post(
                config.CONFIG["API_ENDPOINT"] + "send_file/",
                params={
                    'client_id': self.client_id
                },
                files={
                    'file': (file_name, f, 'multipart/form-data'),
                }
            )
            self._log(r)

    def download_file(self, path):
        r = requests.get(
            config.CONFIG["API_ENDPOINT"] + "download_file/",
            params={
                'client_id': self.client_id
            }
        )
        path = path + self.client_id[0:10] + "_" + self.share["file_name"]
        with open(path, 'wb+') as f:
            f.write(r.content)
            f.close()
        # print(r.content.decode('utf8'))

    def get_key(self):
        r = requests.get(config.CONFIG["API_ENDPOINT"] + "get_key/", params={'client_id': self.client_id})
        self._log(r)      
        try:
            self.__decrypt_key = r.json()
        except json.decoder.JSONDecodeError as e:
            raise e
