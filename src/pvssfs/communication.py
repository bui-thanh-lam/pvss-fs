import os
import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from server import ServerHandler
from pydantic import BaseModel
import json

app = FastAPI()
server = ServerHandler()
phase = 1
"""
1. register phase
2. key sharing phase
3. key reconstruction phase
"""


class AES_key(BaseModel):
    client_id: str
    key: str
    cipher_file_path: str
    plain_file_path: str


@app.get("/get_client_id/")
def get_cient_id():
    # Server generate client_id for new client
    resp = {}
    global phase
    if phase == 1:
        client_id = server.distribute_client_id()
        resp["client_id"] = client_id
    else:
        print("cannot register into file sharing system")
        resp["client_id"] = None
    return resp


@app.post("/send_key/")
def send_key(key: AES_key):
    # Server receive the AES_key:{"client_id":"", "key":"", "plain_file_name":"", "cipher_file_name":""}
    resp = {}
    global phase
    if (phase == 1):
        key = json.loads(key.json())
        if(server.compute_shares(key)):
            phase = 2
            resp["message"] = "key sharing successful"
            print(resp)
            return resp
        else:
            resp["message"] = "client_id is not exist"
            print(resp)
            return resp

    else:
        resp["message"] = "cannot share file"
        print(resp)
        return resp
    
    
@app.get("/get_share/")
def get_share(client_id):
    # Server generate shares, then distribute each share to each shareholder
    resp = {}
    global phase
    if phase != 2:
        print("cannot get share")
        return None
    else:
        # client_info = json.loads(client_info.json())
        resp = server.distribute_share(client_id)
        return resp


@app.get("/request_open/")
def request_open(client_id):
    # Server check if the requester is the owner or not
    # If True, receive his share and start collecting other shares
    """return code:
            100. client_id is not exist
            200. client_id is not owner
            300. still have share is not distributed
            400. request open is accepted
            """

    resp = {}
    global phase
    if phase != 2:
        resp["message"] = "cannot request open"
    else:
        res = server.check_request_open(client_id)
        if res == 100:
            resp["message"] = "client id is not exist"
        elif res == 200:
            resp["message"] = "client id is not owner"
        elif res == 300:
            resp["message"] = "still have share is not distributed"
        else:
            resp["message"] = "request open is accepted"
            phase = 3
    return resp


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
def send_file(client_id: str, file: UploadFile = File(...)):
    # if client_id == 0:          # If sender is the owner
    server.receive_file(file)
    return {
        'filename': server.filename
    }

@app.get("/download_file/")
def download_file(client_id: str):
    if client_id in server.client_ids:
        return FileResponse(server.filename)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8001)