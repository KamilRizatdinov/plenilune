import uuid

from fastapi import FastAPI

from dataworker import *

app = FastAPI()


# Client side API
@app.get("/init")
async def client_init():
    dump_data()
    return {"message": "Initialize request recieved!", "data": get_data()}


@app.get("/file/create")
async def client_file_create(filename: str, filesize: int = 1024):
    return file_create(filename, filesize)


@app.get("/file/write")
async def client_file_write(filename: str, filesize: int = 1024):
    return file_create(filename, filesize)


@app.get("/file/read")
async def client_file_read(filename: str):
    return file_read(filename)


@app.get("/file/delete")
async def client_file_delete(filename: str):
    return file_delete(filename)


@app.get("/file/info")
async def client_file_delete(filename: str):
    return file_info(filename)


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
