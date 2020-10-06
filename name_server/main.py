from pathlib import Path
import uuid

from fastapi import FastAPI, HTTPException
import logging
import uvicorn

from custom_logging import CustomizeLogger
from dataworker import *

logger = logging.getLogger(__name__)
config_path=Path(__file__).with_name("logging_config.json")


def create_app() -> FastAPI:
    app = FastAPI(title='CustomLogger', debug=False)
    logger = CustomizeLogger.make_logger(config_path)
    app.logger = logger

    return app


app = create_app()


# Client side API
@app.get("/status")
async def client_status():
    return get_data()


@app.get("/init")
async def client_init():
    app.logger.debug("Here Is Your Error Log")
    dump_data()
    return {"detail": "File system initialized"}


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


@app.get("/file/move")
async def client_file_move(filename: str, destination: str):
    if not check_file_existance(filename):
        raise HTTPException(status_code=400, detail=f"File '{filename}' does not exist in that directory!")
    if not check_directory_existance(destination):
        raise HTTPException(status_code=400, detail=f"Directory '{dirname}' does not exist in that directory!")
    return file_move(filename, destination)


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


@app.get("/dir/read")
async def client_directory_read():
    return directory_read()


@app.get("/dir/delete")
async def client_directory_delete(dirname: str, flag: str = None):
    if not check_directory_existance(dirname):
        raise HTTPException(status_code=400, detail=f"Directory '{dirname}' does not exist in that directory!")
    result = directory_delete(dirname, flag)
    if result is None:
        raise HTTPException(status_code=400, detail=f"Directory '{dirname}' has some data inside, use the flag '-y' to delete it")
    return result


# Storage side API
@app.get("/update")
async def storage_update():
    return {"message": "Update request recieved!"}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
