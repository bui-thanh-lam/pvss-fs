import os
import uvicorn
from fastapi import FastAPI, File, UploadFile
from server import ServerHandler


app = FastAPI()
server = ServerHandler()

@app.get("/get_client_id/")
def get_cient_id():
    # Server generate client_id for new client
    client_id = server.distribute_client_id()
    return client_id

@app.post("/send_key/")
def send_key(msg):
    # Server receive the msg:{"client_id":"", "key":"", "plain_file_name":"", "cipher_file_name":""}
    pass
    
    
@app.get("/get_share/")
def get_key():
    # Server generate shares, then distribute each share to each shareholder
    pass    


@app.post("/request_open/")
def request_open(share: str):
    # Server check if the requester is the owner or not
    # If True, receive his share and start collecting other shares
    pass


@app.post("/send_share/")
def send_share(share: str):
    # Server receive a share and append it to collection
    pass

    
@app.get("/get_key/")
def get_key():
    # Check whether this client is the owner
    # If True, server recontruct and return the key
    # Otherwise, server refuse reconstructing
    pass


@app.post("/send_file/")
def send_file(client_id: int, file: UploadFile = File(...)):
    if client_id == 0:          # If sender is the owner
        server.receive_file(file)
        return {
            'filename': server.filename
        }

@app.get("/download_file/")
def download_file():
    # Server provide clients with the reconstructed file when they request to download it
    pass


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8001)