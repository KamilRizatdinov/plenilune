import uuid

from fastapi import FastAPI, HTTPException

from dataworker import *

app = FastAPI()


# Client side API
@app.get("/init")
async def client_init():
    dump_data()
    return {"message": "Initialize request recieved!", "data": get_data()}


@app.get("/file/create")
async def client_file_create(filename: str, filesize: int = 1024):
    if check_file_existance(filename):
        raise HTTPException(status_code=400, detail=f"File '{filename}' already exists in that directory!")
    return file_create(filename, filesize)


@app.get("/file/write")
async def client_file_write(filename: str, filesize: int = 1024):
    if check_file_existance(filename):
        raise HTTPException(status_code=400, detail=f"File '{filename}' already exists in that directory!")
    return file_create(filename, filesize)


@app.get("/file/read")
async def client_file_read(filename: str):
    if not check_file_existance(filename):
        raise HTTPException(status_code=400, detail=f"File '{filename}' does not exist in that directory!")
    return file_read(filename)


@app.get("/file/copy")
async def client_file_copy(filename: str, copy: str):
    if not check_file_existance(filename):
        raise HTTPException(status_code=400, detail=f"File '{filename}' does not exist in that directory!")
    if check_file_existance(copy):
        raise HTTPException(status_code=400, detail=f"File '{copy}' already exists in that directory!")
    return file_copy(filename, copy)


@app.get("/file/delete")
async def client_file_delete(filename: str):
    if not check_file_existance(filename):
        raise HTTPException(status_code=400, detail=f"File '{filename}' does not exist in that directory!")
    return file_delete(filename)


@app.get("/file/info")
async def client_file_info(filename: str):
    if not check_file_existance(filename):
        raise HTTPException(status_code=400, detail=f"File '{filename}' does not exist in that directory!")
    return file_info(filename)

# Storage side API
@app.get("/update")
async def storage_update():
    return {"message": "Update request recieved!"}
