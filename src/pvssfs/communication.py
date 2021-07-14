import uvicorn
from fastapi import FastAPI
from server import ServerHandler


app = FastAPI()
server = ServerHandler()


@app.post("/send_key")
def send_key(key: str):
    # Server receive the key and remember the owner
    pass
    
    
@app.get("/get_share")
def get_key():
    # Server generate shares, then distribute each share to each shareholer
    pass    


@app.post("/request_open")
def request_open(share: str):
    # Server check if the requester is the owner or not
    # If True, receive his share and start collecting other shares
    pass


@app.post("/send_share")
def send_share(share: str):
    # Server receive a share and append it to collection
    pass

    
@app.get("/get_key")
def get_key():
    # Check whether this client is the owner
    # If True, server recontruct and return the key
    # Otherwise, server refuse reconstructing
    pass


@app.post("/send_file")
def send_file():
    # Server receive reconstructed file from owner
    pass


@app.get("/download_file")
def download_file():
    # Server provide clients with the reconstructed file when they request to download it
    pass