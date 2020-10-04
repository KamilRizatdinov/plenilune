import uuid

from fastapi import FastAPI, Depends

from dataworker import *
import schemas

app = FastAPI()

# Data dependency
def dependency():
    data = get_data()
    return data

def allocate_blocks(data):
    storage_servers = data['storage_servers']

# Client side API
@app.get("/init")
async def client_init():
    dump_data()
    return {"message": "Initialize request recieved!", "data": get_data()}


@app.get("/file/create")
async def client_file_create(
    filename: str, 
    filesize: int = 1024, 
    data: dict = Depends(dependency)
):
    return create_file(filename, filesize)


@app.get("/file/write")
async def client_file_write(
    filename: str, 
    filesize: int = 1024, 
    data: dict = Depends(dependency)
):
    return create_file(filename, filesize)


@app.get("/write")
async def client_write(operation_type: str):
    return {"message": "Write request recieved!"}


@app.get("/fetch")
async def client_write():
    return {"message": "Fetch request recieved!"}

# Storage side API
@app.get("/update")
async def storage_update():
    return {"message": "Update request recieved!"}
