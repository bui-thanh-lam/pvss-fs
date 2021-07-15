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
def get_cient_id():
    # Server generate client_id for new client
    resp = {}
    global phase
    if phase != 1:
        print("cannot register into file sharing system")
        resp["client_id"] = None
    else:
        client_id = server.distribute_client_id()
        resp["client_id"] = client_id
    return resp


@app.post("/send_key/")
def send_key(key: AES_key):
    # Server receive the AES_key:{"client_id":"", "key":"", "plain_file_name":"", "cipher_file_name":""}
    resp = {}
    global phase
    if (phase == 1):
        key = json.loads(key.json())
        if (server.compute_shares(key)):
            phase = 2
            resp["message"] = "key sharing successful"
        else:
            resp["message"] = "client_id is not exist"
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
        if(resp == None):
            print("cannot get share")
        else:
            print("get share successful")
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
    print(resp)
    return resp


@app.post("/send_share/")
def send_share(share: Share):
    # Server receive a share and append it to collection
    """return code:
                   100. client_id is not exist
                   200. client id sent share
                   300. send share successful
                   """
    resp = {}
    global phase
    if phase != 3:
        resp["message"] = "cannot send share"
    else:
        share = json.loads(share.json())
        res = server.collect_shares(share)
        if res == 100:
            resp["message"] = " client id is not exist"
        elif res == 200:
            resp["message"] = "client sent share"
        else:
            resp["message"] = "send share successful"
    print(resp)
    return resp


@app.get("/get_key/")
def get_key(client_id):
    # Check whether this client is the owner
    # If True, server recontruct and return the key
    # Otherwise, server refuse reconstructing
    """return code:
                           100. client_id is not exist
                           200. client id is not owner
                           300. do not collect enough share
                           400. get key successful
                           500. not the time to reconstruct key
                           """
    resp = {}
    global phase
    if phase != 3:
        resp["status_code"] = 500
        resp["message"] = "not the time to reconstruct key"
    else:
        resp = server.get_key(client_id)
        if resp["status_code"] == 100:
            resp["message"] = "client id is not exist"
        elif resp["status_code"] ==  200:
            resp["message"] = "client id is not owner"
        elif resp["status_code"] == 300:
            resp["message"] = "do not collect enough share"
        else:
            resp["message"] ="get key successful"
            phase = 4
    print(resp["message"])
    return resp


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
