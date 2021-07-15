import os
import ctypes
import config
import pprint


class KeyComponent(ctypes.Structure):
    _fields_ = [('k', ctypes.c_char_p), ('x', ctypes.c_int)]


class KeySharing(ctypes.Structure):
    _fields_ = [('N', ctypes.c_int), ('T', ctypes.c_int), ('p', ctypes.c_char_p),
                ('key_component', ctypes.POINTER(KeyComponent))]


class ServerHandler:

    def __init__(self):
        # init client_id
        self.current_client_id = -1

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

    def compute_shares(self, S, N=3, T=2):
        """Compute shares given a key

        Args:
            S (str): a given key
            N (int): number of shareholders
            T (int): threshold of shareholders to reconstruct the key from their shares
            
        Return:

        """
        S = ctypes.c_char_p(S.encode("utf-8"))
        N = ctypes.c_int(N)
        T = ctypes.c_int(T)
        shares = self.convert_key_sharing_to_json_form(self.key_sharing_phase(S, N, T))
        return shares

    def convert_key_sharing_to_json_form(self, key_sharing):
        """Convert the key_sharing (struct KeySharing) to json form

               Args:
                   key_sharing: KeySharing

               Return:
                   shares(json form): {"N":"", "T":"", "p":"","key_components":[{"x":"","k":""},..]}
               """
        shares = {}
        shares["N"] = key_sharing.N
        shares["T"] = key_sharing.T
        shares["p"] = key_sharing.p.decode("utf-8")
        key_components = []
        for i in range(0,key_sharing.N):
            key_component = {}
            key_component["x"] = key_sharing.key_component[i].x
            key_component["k"] = key_sharing.key_component[i].k.decode("utf-8")
            key_components.append(key_component)
        shares["key_components"] = key_components
        return shares


    def convert_shares_to_key_sharing(self, shares):
        #fixing
        """Convert the shares (json form) to struct KeySharing

                       Args:
                           shares(json form): {"N":"", "T":"", "p":"","key_components":[{"x":"","k":""},..]}

                       Return:
                           key_sharing: KeySharing
            """
        N = shares["N"]
        T = shares["T"]
        p = shares["p"]
        key_component_array = ctypes.POINTER(KeyComponent)
        key_components = shares["key_components"]
        for i in range(0,T):
            key_component = KeyComponent(ctypes.c_char_p(key_components[i]["k"].encode("utf-8")), ctypes.c_int(key_components[i]["x"]))
            key_component_array(key_component)
        print(key_component_array)
        for i in range(0,T):
            print(key_component_array[i].x)
        # key_sharing = KeySharing(ctypes.c_int(N),ctypes.c_int(T),ctypes.c_char_p(p.encode("utf-8")),key_component_array
        key_sharing = ""
        return key_sharing

    def reconstruct_key(self, shares):
        #fixing
        """Reconstruct the secret key from collected shares

        Args:
            shares (): collected shares

        Return:
            key (str): recontructed key
        """
        return self.key_reconstruction_phase(self.convert_shares_to_key_sharing(shares))

    def collect_shares(self):
        pass

    def distribute_share(self, share, shareholder_id):
        pass

    def distribute_client_id(self):
        self.current_client_id += 1
        print(self.current_client_id)
        return self.current_client_id

server = ServerHandler()
S = "3CE7C3C862457688D415D34753A446D0"
N = 10
T = 5
shares = server.compute_shares(S, N, T)
pprint.pprint(shares)
# reconstructed_key = server.reconstruct_key(shares)
# print(reconstructed_key)
