import uuid

from fastapi import FastAPI, HTTPException

from dataworker import *

app = FastAPI()


# Client side API
@app.get("/status")
async def client_status():
    return get_data()


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
async def client_file_copy(filename: str, destination: str):
    if not check_file_existance(filename):
        raise HTTPException(status_code=400, detail=f"File '{filename}' does not exist in that directory!")
    if check_file_existance(destination):
        raise HTTPException(status_code=400, detail=f"File '{destination}' already exists in that directory!")
    return file_copy(filename, destination)


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


@app.get("/dir/create")
async def client_directory_create(dirname: str):
    if check_directory_existance(dirname):
        raise HTTPException(status_code=400, detail=f"Directory '{dirname}' already exists in that directory!")
    return directory_create(dirname)


@app.get("/dir/open")
async def client_directory_open(dirname: str):
    if not check_directory_existance(dirname):
        raise HTTPException(status_code=400, detail=f"Directory '{dirname}' does not exist in that directory!")
    return directory_open(dirname)


# Storage side API
@app.get("/update")
async def storage_update():
    return {"message": "Update request recieved!"}
