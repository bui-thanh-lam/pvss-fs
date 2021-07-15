import os
import config
import requests
import ctypes


class ClientHandler:
    """ Handling all clients' behavior.

    Methods:
        encrypt_file(plain_file_path, cipher_file_path): encrypt a plain file
        encrypt_file(cipher_file_path, plain_file_path, key): decrypt a cipher file

    """

    def __init__(self):

        self.client_id = 0
        # self.client_id = requests.get("http://localhost:8001/get_client_id").content.decode("utf-8")

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
        plain_file_name = os.path.basename(plain_file_path)
        cipher_file_name = os.path.basename(cipher_file_path)
        plain_file_path = ctypes.c_char_p(plain_file_path.encode("utf-8"))
        cipher_file_path = ctypes.c_char_p(cipher_file_path.encode("utf-8"))
        key = self.encryptor(plain_file_path, cipher_file_path).decode("utf-8")
        self.send_key(key, plain_file_name, cipher_file_name)

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

    def send_key(self, key, plain_file_name, cipher_file_name):
        msg = {}
        msg["key"] = key
        msg["client_id"] = self.client_id
        msg["plain_file_name"] = plain_file_name
        msg["cipher_file_name"] = cipher_file_name
        print(msg)

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