from pathlib import Path
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Response, Body
from typing import List
import os
import shutil
import requests
import logging

from custom_logging import CustomizeLogger

app = FastAPI()

logger = logging.getLogger(__name__)
config_path=Path(__file__).with_name("logging_config.json")


def create_app() -> FastAPI:
    app = FastAPI(title='CustomLogger', debug=False)
    logger = CustomizeLogger.make_logger(config_path)
    app.logger = logger

    return app


app = create_app()

DATA_DIR = '/data/'


@app.post('/file/create')
async def create(servers: List[str] = Body(...), filename: str = Body(...)):
    '''
    servers: list of ip addresses with corresponding port where to create the file
    filename: name of file that client wants to create
    '''
    app.logger.debug(f'Storage server recieved servers list: {servers}.')
    app.logger.debug(f'Storage server has started creating file: {filename}.')

    file_address = DATA_DIR + filename

    with open(file_address, 'w'):
        pass
    if not os.path.isfile(file_address):

        logger.error(f'Storage server didn\'t create the file: {filename}.')
        app.logger.debug('Storage server sent response with status code 404.')
        raise HTTPException(status_code=404, detail=f'File "{file.filename}" is not found in directory!')
        # return Response(status_code=404)
    
    app.logger.debug(f'Storage server created file: {filename}.')
    app.logger.debug('Storage server is ready to forward request to other servers.')

    if len(servers) > 1:
        await forward_create(servers, filename)
    
    app.logger.debug('Storage server finished with creation of the file.')
    app.logger.debug('Storage server sent response with status code 200.')

    # return Response(status_code=200)
    return {'message': 'File is created!'}


async def forward_create(servers: List[str], filename: str):
    '''
    servers: list of ip addresses with corresponding port where to create the file
    filename: name of file that client wants to create
    '''
    server = servers[1]
    servers = servers[1:]

    app.logger.debug(f'Storage server {server} is forwarding request to other servers {servers}.')

    response = requests.get('http://' + server + '/file/create', json={'servers': servers, 'filename': filename})

    if response.status_code != 200:
        logger.error(f'Something went wrong: {response.json()["detail"]}')
    
    app.logger.debug(f'Storage server {server} forwarded request to other servers {servers}.')


@app.post('/file/put')
async def put(servers: list, file: UploadFile = File(...)):
    '''
    servers: list of ip addresses with corresponding port where to replicate the file
    file: file itself to upload, it's name I suppose in format of str
    '''
    app.logger.debug(f'Storage server recieved servers list: {servers}.')
    app.logger.debug(f'Storage server has started writing file: {file.filename}.')

    file_address = DATA_DIR + file.filename

    with open(file_address, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    if not os.path.isfile(file_address):
        logger.error(f'Storage server didn\'t write the file: {file.filename}.')
        logger.error('Storage server raised an error with status code 400.')
        raise HTTPException(status_code=400, detail=f'File "{file.filename}" is not found in directory!')
        
    app.logger.debug(f'Storage server wrote file: {file.filename}.')
    app.logger.debug('Storage server is ready to forward request to other servers.')

    if len(servers) > 1:
        await forward_put(servers, file)

    app.logger.debug('Storage server finished with writing the file.')
    app.logger.debug('Storage server sent response with status code 200.')

    return {'filename': file.filename, 'message': 'Data is recieved!'}


async def forward_put(servers: list, file: UploadFile = File(...)):
    '''
    servers: list of ip addresses with corresponding port where to replicate the file
    file: file itself to upload, it's name I suppose in format of str
    '''
    server = servers[1]
    servers = servers[1:]

    app.logger.debug(f'Storage server {server} is forwarding request to other servers {servers}.')

    files = {
        'file': (file.filename, file.file),
    }

    response = requests.post('http://' + server + '/file/put', data={'servers': servers}, files=files)

    if response.status_code != 200:
        logger.error(f'Something went wrong: {response.json()["detail"]}')
    
    app.logger.debug(f'Storage server {server} forwarded request to other servers {servers}.')


# block_uuid was replaced by filename because of 
# using this notation in function put
@app.get('/file/get')
async def get(filename: str):
    '''
    filename: name of file that client wants to get
    '''
    app.logger.debug(f'Storage server recieved filename: {filename}.')
    app.logger.debug(f'Storage server is searching for a file: {filename}.')

    file_address = DATA_DIR + filename

    if not os.path.isfile(file_address):
        logger.error(f'Storage server didn\'t find the file: {filename}.')
        logger.error('Storage server raised an error with status code 400.')
        raise HTTPException(status_code=400, detail=f'File "{filename}" does not exist in directory!')
    with open(file_address) as f:
        app.logger.debug(f'Storage server has found the file: {filename}.')
        app.logger.debug(f'Storage server sending the file in response')
        return f.read() 


@app.get('/file/copy',
    summary='Copy block',
    response_class=Response,
    responses={
        200: {'message': 'Copy is successfully created'},
        400: {'message': 'Copy is not created'},
    },
)
async def copy(servers: list, filename: str, newfilename: str):
    '''
    servers: list of ip addresses with corresponding port where file need to be copied
    filename: name of file that client wants to copy
    newfilename: name of file copy
    '''
    app.logger.debug(f'Storage server recieved servers list: {servers}.')
    app.logger.debug(f'Storage server is copying file named {filename} to file with name {newfilename}.')

    file_address = DATA_DIR + filename
    new_file_address = DATA_DIR + newfilename

    with open(file_address, 'rb') as f, open(new_file_address, 'wb') as copyfile:
        shutil.copyfileobj(f, copyfile)

    if not os.path.isfile(new_file_address):
        logger.error(f'Storage server didn\'t copied the file :(')
        logger.error('Storage server raised an error with status code 400.')
        return Response(status_code=400)
    
    app.logger.debug(f'Storage server copied the file {filename} into {newfilename}.')
    app.logger.debug('Storage server is ready to forward request to other servers.')

    if len(servers) > 1:
        await forward_copy(servers, filename, newfilename)

    app.logger.debug('Storage server finished with copying the file.')
    app.logger.debug('Storage server sent response with status code 200.')

    return Response(status_code=200)


async def forward_copy(servers: list, filename: str, newfilename: str):
    '''
    servers: list of ip addresses with corresponding port where file need to be copied
    filename: name of file that client wants to copy
    newfilename: name of file copy
    '''
    server = servers[1]
    servers = servers[1:]

    app.logger.debug(f'Storage server {server} is forwarding request to other servers {servers}.')

    response = requests.get('http://' + server + '/file/copy', {'servers': servers, 'filename': filename, 'newfilename': newfilename})

    if response.status_code != 200:
        logger.error(f'Something went wrong: {response.json()["detail"]}')
    
    app.logger.debug(f'Storage server {server} forwarded request to other servers {servers}.')


@app.post('/file/delete')
async def delete(servers: List[str] = Body(...), filename: str = Body(...)):
    '''
    servers: list of ip addresses with corresponding port where to delete the file
    filename: name of file that client wants to delete
    '''
    file_address = DATA_DIR + filename

    if not os.path.isfile(file_address):
        logger.error(f'Storage server didn\'t find the file :(')
        logger.error('Storage server raised an error with status code 404.')
        return Response(status_code=404)
    else:
        app.logger.debug('Storage server is deleting the file.')
        os.remove(file_address)
    
    if os.path.isfile(file_address):
        logger.error('Storage server didn\'t delete the file.')

    app.logger.debug(f'Storage server deleted the file {filename}.')
    app.logger.debug('Storage server is ready to forward request to other servers.')

    if len(servers) > 1:
        await forward_delete(servers, filename)
    
    app.logger.debug('Storage server finished with deleting the file.')
    app.logger.debug('Storage server sent response with status code 200.')

    return Response(status_code=200)


async def forward_delete(servers: list, filename: str):
    '''
    servers: list of ip addresses with corresponding port where to delete the file
    filename: name of file that client wants to delete
    '''
    server = servers[1]
    servers = servers[1:]

    app.logger.debug(f'Storage server {server} is forwarding request to other servers {servers}.')

    response = requests.post('http://' + server + '/file/delete', json={'servers': servers, 'filename': filename})

    if response.status_code != 200:
        logger.error(f'Something went wrong: {response.json()["detail"]}')
    
    app.logger.debug(f'Storage server {server} forwarded request to other servers {servers}.')


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)

