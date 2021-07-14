import os
import ctypes
from config import SERVER_LIB_PATH


class KeyComponent(ctypes.Structure):
    _fields_ = [('k', ctypes.c_char_p), ('x', ctypes.c_int)]


class KeySharing(ctypes.Structure):
    _fields_ = [('N', ctypes.c_int), ('T', ctypes.c_int), ('p', ctypes.c_char_p), ('key_component', ctypes.POINTER(KeyComponent))]


class ServerHandler:

    def __init__(self):
        # load lib
        _path = os.path.join(SERVER_LIB_PATH)
        _mod = ctypes.cdll.LoadLibrary(_path)

        # KeySharing key_sharing_phase(char* S, int N, int T)
        self.key_sharing_phase = _mod.key_sharing_phase
        self.key_sharing_phase.argtypes = (ctypes.c_char_p, ctypes.c_int, ctypes.c_int)
        self.key_sharing_phase.restype = (KeySharing)

        # char* key_reconstruction_phase(KeySharing keySharing)
        self.key_reconstruction_phase = _mod.key_reconstruction_phase
        self.key_reconstruction_phase.argtypes = [ctypes.POINTER(KeySharing)]
        self.key_reconstruction_phase.restype = (ctypes.c_char_p)

    def share_key(self, S, N, T):
        S = ctypes.c_char_p(S.encode("utf-8"))
        N = ctypes.c_int(N)
        T = ctypes.c_int(T)
        return self.key_sharing_phase(S, N, T)

    def reconstruct_key(self, keySharing):
        return self.key_reconstruction_phase(keySharing)


server = ServerHandler()
S = "3CE7C3C862457688D415D34753A446D0"
N = 10
T = 5
key_sharing = server.share_key(S, N, T)
reconstructed_key = server.reconstruct_key(key_sharing)
print(reconstructed_key)

