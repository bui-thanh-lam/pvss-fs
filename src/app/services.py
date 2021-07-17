import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from pvssfs.server import ServerHandler
from pydantic import BaseModel

app = FastAPI()
# Add singleton later
server = ServerHandler()
# Add observer later
phase = 1
"""
1. register phase
2. key sharing phase
3. key reconstruction phase
4. download phase
"""

class AES_key(BaseModel):
    client_id: str
    key: str
    cipher_file_path: str
    plain_file_path: str


class Share(BaseModel):
    x: int
    k: str
    client_id: str


@app.get("/get_client_id/")
def get_client_id():
    # Server generate client_id for new client
    global phase
    if phase == 1:
        client_id = server.distribute_client_id()
        return {
            'client_id': client_id
        }
    else:
        raise Exception("Too late to register a new client")


@app.post("/send_key/")
def send_key(key: AES_key):
    global phase
    if phase == 1:
        is_computed = server.compute_shares(key)
        if is_computed:
            phase = 2
            print("Receive key successfully! All shares are ready to be distributed")
        else:
            raise Exception("Failed to compute shares")
    else:
        raise Exception("Cannot receive key at this time")


@app.get("/get_share/")
def get_share(client_id: str):
    # Server distribute each share to each shareholder
    global phase
    if phase == 2:
        share = server.distribute_share(client_id)
        # share: dict {'k', 'x'}
        print(f"Distribute share to client {client_id} successfully!")
        return share
    else:
        raise Exception("Cannot distribute shares at this time")


@app.post("/request_open/")
def request_open(client_id: str):
    # Server check if the requester is the owner or not
    # If True, receive his share and start collecting other shares for rescontruction phase
    global phase
    if phase == 2:
        is_owner = server.check_request_open(client_id)
        if is_owner:
            phase = 3
    else:
        raise Exception("Cannot open requested file at this time")


@app.post("/send_share/")
def send_share(share: Share):
    global phase
    if phase == 3:
        has_collected = server.collect_shares(share)
        if has_collected:
            print(f"Receive share from client {share.client_id} succesfully!")
    else:
        raise Exception("Cannot receive shares at this time")


@app.get("/get_key/")
def get_key(client_id: str):
    # Check whether this client is the owner
    # If True, server recontruct and return the key
    # Otherwise, server refuse to reconstruct

    global phase
    if phase != 3:
        raise Exception("Cannot send key at this time")
    else:
        key = server.reconstruct_key(client_id)
        if key:
            print("Distribute key back to owner successfully")
            phase = 4
    return {
        'key': key,
        'plain_file_path': server.file_detail.plain_file_path,
        'cipher_file_path': server.file_detail.cipher_file_path
    }


@app.post("/send_file/")
def send_file(client_id: str, file: UploadFile = File(...)):
    global phase
    if phase == 4:
        if server.file_detail.owner_id == client_id:
            server.receive_file(file)
            return {
                'filename': server.filename
            }
        else:
            raise Exception("Only owner can send file")
    else:
        raise Exception("Cannot receive file at this time")


@app.get("/download_file/")
def download_file(client_id: str):
    global phase
    if phase == 4:
        if server._is_valid_client_id(client_id):
            return FileResponse(server.filename)
        else:
            raise Exception("Invalid client id")
    else:
        raise Exception("Cannot provide file at this time")


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8001)
