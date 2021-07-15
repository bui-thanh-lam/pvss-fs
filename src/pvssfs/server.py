import os
import ctypes
import config
import hashlib
import time

class KeyComponent(ctypes.Structure):
    _fields_ = [('k', ctypes.c_char_p), ('x', ctypes.c_int)]


class KeySharing(ctypes.Structure):
    _fields_ = [('N', ctypes.c_int), ('T', ctypes.c_int), ('p', ctypes.c_char_p),
                ('key_component', ctypes.POINTER(KeyComponent))]


class ServerHandler:

    def __init__(self):
        # init client_id
        self.n_clients = 0

        # load lib
        _mod = ctypes.cdll.LoadLibrary(config.SERVER_LIB_PATH)

        # KeySharing key_sharing_phase(char* S, int N, int T)
        self.key_sharing_phase = _mod.key_sharing_phase
        self.key_sharing_phase.argtypes = (ctypes.c_char_p, ctypes.c_int, ctypes.c_int)
        self.key_sharing_phase.restype = (KeySharing)

        # char* key_reconstruction_phase(KeySharing keySharing)
        self.key_reconstruction_phase = _mod.key_reconstruction_phase
        self.key_reconstruction_phase.argtypes = [ctypes.POINTER(KeySharing)]
        self.key_reconstruction_phase.restype = (ctypes.c_char_p)

        self.file_detail = {}
        self.shares = []
        self.client_ids = []
        self.list_client_received_share = []

    def check_client_id(self, client_id):
        return client_id in self.client_ids

    def check_client_id_not_received_share(self, client_id):
        return client_id not in self.list_client_received_share

    def compute_shares(self, AES_key):
        """Compute shares given a key

        Args:
            S (str): a given key
            N (int): number of shareholders
            T (int): threshold of shareholders to reconstruct the key from their shares

        Return:
            shares (json form): {"N":"", "T":"", "p":"","key_components":[{"x":"","k":""},..]}
        """
        client_id = AES_key["client_id"]
        if(self.check_client_id(client_id)):
            S = AES_key["key"]
            S = ctypes.c_char_p(S.encode("utf-8"))
            N = ctypes.c_int(self.n_clients)
            T = int(self.n_clients/ 2)
            T = ctypes.c_int(T)

            key_sharing = self.key_sharing_phase(S, N, T)

            file_detail = {}
            file_detail["plain_file_path"] = AES_key["plain_file_path"]
            file_detail["cipher_file_path"] = AES_key["cipher_file_path"]
            file_detail["owner_id"] = AES_key["client_id"]
            file_detail["N"] = key_sharing.N
            file_detail["T"] = key_sharing.T
            file_detail["p"] = key_sharing.p.decode("utf-8")
            key_components = []
            for i in range(0, key_sharing.N):
                key_component = {}
                key_component["x"] = key_sharing.key_component[i].x
                key_component["k"] = key_sharing.key_component[i].k.decode("utf-8")
                key_components.append(key_component)
            self.shares = key_components
            self.file_detail = file_detail
            print(self.file_detail)
            print(self.shares)
            return True
        return False

    def convert_shares_to_key_sharing(self, shares):
        """Convert the shares (json form) to struct KeySharing

                Args:
                    shares(json form): {"N":"", "T":"", "p":"","key_components":[{"x":"","k":""},..]}

                Return:
                    key_sharing: KeySharing
            """
        key_sharing = KeySharing()
        key_sharing.N = ctypes.c_int(shares["N"])
        key_sharing.T = ctypes.c_int(shares["T"])
        key_sharing.p = ctypes.c_char_p(shares["p"].encode("utf-8"))
        key_component_array_type = KeyComponent * key_sharing.T
        key_component_array = key_component_array_type()

        key_components = shares["key_components"]
        for i in range(0,key_sharing.T):
            key_component = KeyComponent(ctypes.c_char_p(key_components[i]["k"].encode("utf-8")), ctypes.c_int(key_components[i]["x"]))
            key_component_array[i] = key_component
        key_sharing.key_component = ctypes.cast(key_component_array, ctypes.POINTER(KeyComponent))
        return key_sharing

    def reconstruct_key(self, shares):
        """Reconstruct the secret key from collected shares

        Args:
            shares (): collected shares

        Return:
            key (str): recontructed key
        """
        return self.key_reconstruction_phase(self.convert_shares_to_key_sharing(shares)).decode("utf-8")

    def collect_shares(self):
        pass

    def distribute_share(self, client_id):
        if self.check_client_id(client_id):
            if(self.check_client_id_not_received_share(client_id)):
                share = self.shares.pop(1)
                self.list_client_received_share.append(client_id)
                return share
        return None

    def distribute_client_id(self):
        self.n_clients += 1
        client_id = hashlib.sha256( (str(self.n_clients) + str(time.time())).encode("utf-8")).hexdigest()
        self.client_ids.append(client_id)
        return client_id

    def receive_file(self, file):
        server_filename = config.STORAGE_PATH+"/"+file.filename.replace(" ", "_")
        with open(server_filename,'wb+') as f:
            f.write(file.file.read())
            f.close()
        setattr(self, 'filename', server_filename)

# server = ServerHandler()
# S = "3CE7C3C862457688D415D34753A446D0"
# N = 10
# T = 5
# shares = server.compute_shares(S, N, T)
# pprint.pprint(shares)
# reconstructed_key = server.reconstruct_key(shares)
# print(reconstructed_key)
