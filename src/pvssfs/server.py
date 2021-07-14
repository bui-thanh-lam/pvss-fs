import os
import ctypes
import config


class KeyComponent(ctypes.Structure):
    _fields_ = [('k', ctypes.c_char_p), ('x', ctypes.c_int)]


class KeySharing(ctypes.Structure):
    _fields_ = [('N', ctypes.c_int), ('T', ctypes.c_int), ('p', ctypes.c_char_p), ('key_component', ctypes.POINTER(KeyComponent))]


class ServerHandler:

    def __init__(self):
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
        return self.key_sharing_phase(S, N, T)

    def reconstruct_key(self, shares):
        """Reconstruct the secret key from collected shares

        Args:
            shares (): collected shares

        Return:
            key (str): recontructed key
        """
        return self.key_reconstruction_phase(shares)
    
    def collect_shares(self):
        pass
    
    def distribute_share(self, share, shareholder_id):
        pass


server = ServerHandler()
S = "3CE7C3C862457688D415D34753A446D0"
N = 10
T = 5
shares = server.compute_shares(S, N, T)
print(shares)
reconstructed_key = server.reconstruct_key(shares)
print(reconstructed_key)

