CLIENT_LIB_PATH = "/home/lam-bui/Documents/Projects/ATTT/BTL/pvss-fs/src/cpp_libs/Client_Lib.so"
SERVER_LIB_PATH = "/home/lam-bui/Documents/Projects/ATTT/BTL/pvss-fs/src/cpp_libs/Server_Lib.so"
TEST_DOCUMENT_PATH = "/home/lam-bui/Documents/Projects/ATTT/BTL/pvss-fs/test/test.txt"
TEST_DECRYPTED_DOC_PATH = "/home/lam-bui/Documents/Projects/ATTT/BTL/pvss-fs/test/test.bin"
TEST_RECOVERED_DOC_PATH = "/home/lam-bui/Documents/Projects/ATTT/BTL/pvss-fs/test/reconstructed_test.txt"
STORAGE_PATH = "/home/lam-bui/Documents/Projects/ATTT/BTL/storage"
API_ENDPOINT = "http://localhost:8001/"

import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--clib', dest='clib', help="path to client's .so library")
parser.add_argument('--slib', dest='slib', help="path to server's .so library")
parser.add_argument('--file', dest='file', help="path to the file that needs secret sharing")
parser.add_argument('--dfile', dest='dfile', help="path to store the decrypted file")
parser.add_argument('--rfile', dest='rfile', help="path to store the recovered file")
parser.add_argument('--storage', dest='storage', help="path to server's storage")
parser.add_argument('--endpoint', dest='endpoint', help="API endpoints")

# Execute parse_args()
args = parser.parse_args()
