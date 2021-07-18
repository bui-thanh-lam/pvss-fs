import ctypes
import pvssfs.config as config
import hashlib
import time

class KeyComponent(ctypes.Structure):
    _fields_ = [('k', ctypes.c_char_p), ('x', ctypes.c_int)]


class KeySharing(ctypes.Structure):
    _fields_ = [('N', ctypes.c_int), ('T', ctypes.c_int), ('p', ctypes.c_char_p),
                ('key_component', ctypes.POINTER(KeyComponent))]


class FileDetail():
    
    def __init__(
        self, 
        plain_file_path,
        cipher_file_path,
        owner_id,
        N, T, p
    ):
        self.plain_file_path = plain_file_path
        self.cipher_file_path = cipher_file_path
        self.owner_id = owner_id
        self.N = N
        self.T = T
        self.p = p


class ServerHandler:

    def __init__(self):
        # init client_id
        self.n_clients = 0

        # load lib
        _mod = ctypes.cdll.LoadLibrary(config.CONFIG["SERVER_LIB_PATH"])

        # KeySharing key_sharing_phase(char* S, int N, int T)
        self.key_sharing_phase = _mod.key_sharing_phase
        self.key_sharing_phase.argtypes = (ctypes.c_char_p, ctypes.c_int, ctypes.c_int)
        self.key_sharing_phase.restype = (KeySharing)

        # char* key_reconstruction_phase(KeySharing keySharing)
        self.key_reconstruction_phase = _mod.key_reconstruction_phase
        self.key_reconstruction_phase.argtypes = [ctypes.POINTER(KeySharing)]
        self.key_reconstruction_phase.restype = (ctypes.c_char_p)

        self.file_detail = None

        self.shares = []
        self.collected_shares = []

        self.client_ids = []
        self.client_received_shares = []
        self.client_sent_shares = []

    def _is_valid_client_id(self, client_id):
        return client_id in self.client_ids

    def _has_received_share(self, client_id):
        return client_id in self.client_received_shares

    def _has_sent_share(self,client_id):
        return client_id in self.client_sent_shares

    def _has_enough_shares(self):
        return len(self.collected_shares) >= self.file_detail.T

    def reconstruct_key(self, client_id):  
        """
        Args:
            client_id (str): client id, expected owner's id
            
        Return:
            key (str): key for owner to decrypt desired file
        """                   
        if self._is_valid_client_id(client_id):
            if self.file_detail.owner_id == client_id:
                if self._has_enough_shares():
                    key_sharing = KeySharing()
                    key_sharing.N = ctypes.c_int(self.file_detail.N)
                    key_sharing.T = ctypes.c_int(self.file_detail.T)
                    key_sharing.p = ctypes.c_char_p(self.file_detail.p.encode("utf-8"))
                    key_component_array_type = KeyComponent * key_sharing.T
                    key_component_array = key_component_array_type()
                    for i in range(0, key_sharing.T):
                        key_component = KeyComponent(ctypes.c_char_p(self.collected_shares[i].k.encode("utf-8")),
                                                     ctypes.c_int(self.collected_shares[i].x))
                        key_component_array[i] = key_component
                    key_sharing.key_component = ctypes.cast(key_component_array, ctypes.POINTER(KeyComponent))
                    # key = {}
                    key = self._reconstruct_key(key_sharing)
                    # key["plain_file_path"] = self.file_detail.plain_file_path
                    # key["cipher_file_path"] = self.file_detail.cipher_file_path
                    return key
                else:
                    raise Exception("Insufficient shares to reconstruct")
            else:
                raise Exception("This client is not the owner")
        else:
            raise Exception("Invalid client id")

    def compute_shares(self, AES_key, threshold=0.5):
        """Compute shares given a key, store in object's attributes

        Args:
            AES_key (AES_key): body of "send_key" request
                class AES_key(BaseModel):
                    client_id: str
                    key: str
                    cipher_file_path: str
                    plain_file_path: str
            threshold (float): T / N ratio

        Return:
            (bool): True if compute shares successfully
        """
        client_id = AES_key.client_id
        if self._is_valid_client_id(client_id):
            S = AES_key.key
            S = ctypes.c_char_p(S.encode("utf-8"))
            N = ctypes.c_int(self.n_clients)
            T = int((self.n_clients+1)*threshold)
            T = ctypes.c_int(T)

            key_sharing = self.key_sharing_phase(S, N, T)

            self.file_detail = FileDetail(
                AES_key.plain_file_path,
                AES_key.cipher_file_path,
                AES_key.client_id,
                key_sharing.N,
                key_sharing.T,
                key_sharing.p.decode("utf-8")
            )
            key_components = []
            for i in range(0, key_sharing.N):
                key_component = {}
                key_component["x"] = key_sharing.key_component[i].x
                key_component["k"] = key_sharing.key_component[i].k.decode("utf-8")
                key_components.append(key_component)
            self.shares = key_components
            return True
        return False

    def _reconstruct_key(self, key_sharing):
        """Reconstruct the secret key from collected shares

        Args:
            key_sharing (KeySharing): collected shares

        Return:
            key (str): recontructed key
        """
        return self.key_reconstruction_phase(key_sharing).decode("utf-8")

    def collect_shares(self, share):
        """
    
        Args:
            share (Share): a client's share
                class Share(BaseModel):
                    x: int
                    k: str
                    client_id: str
                    
        Return:
            (bool): True if receive a share successfully
        """

        client_id = share.client_id
        if self._is_valid_client_id(client_id):
            if self._has_sent_share(client_id):
                raise Exception("This client has already sent his share")
            else:
                self.collected_shares.append(share)
                self.client_sent_shares.append(client_id)
                return True
        else:
            raise Exception("Invalid client id")

    def distribute_share(self, client_id):
        """Distribute a share to a client given his id

        Args:
            client_id (str): expected a valid client_id

        Raise:
            Exception: "Invalid client id" if the given client_id is invalid
            Exception: "This client has already received his share" if the given client_id request his share more than once

        Return:
            share (dict): {'k', 'x'}
        """
        if self._is_valid_client_id(client_id):
            if self._has_received_share(client_id):
                raise Exception("This client has already received his share")
            else:
                share = self.shares.pop(0)
                self.client_received_shares.append(client_id)
                return share
        else:
            raise Exception("Invalid client id")

    def check_request_open(self, client_id):
        if self._is_valid_client_id(client_id):
            if self.file_detail.owner_id == client_id:
                if len(self.shares) == 0:
                    return True
                else:
                    raise Exception("Shares have not been distributed yet")
            else:
                raise Exception("This client is not the owner")
        else:
            raise Exception("Invalid client id")

    def distribute_client_id(self):
        self.n_clients += 1
        client_id = hashlib.sha256( (str(self.n_clients) + str(time.time())).encode("utf-8")).hexdigest()
        self.client_ids.append(client_id)
        return client_id

    def receive_file(self, file):
        server_filename = config.CONFIG["STORAGE_PATH"]+"/"+file.filename.replace(" ", "_")
        with open(server_filename,'wb+') as f:
            f.write(file.file.read())
            f.close()
        setattr(self, 'filename', server_filename)
