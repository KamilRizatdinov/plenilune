from pathlib import Path
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Response, Body
from typing import List
import os
import shutil
import requests
import logging
import socket
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
PORT = 8000
NAME_SERVER_IP = '3.22.44.23:80'
IP = ''

@app.on_event("startup")
async def startup_event():
    app.logger.debug('Storage server is extracting an ip of host machine.')
    response = requests.get('https://api.ipify.org')
    if response.status_code != 200:
        logger.error(f'Something went wrong: {response.json()["detail"]}')
    
    global IP
    IP = f'{response.content.decode("utf-8")}:{PORT}'

    initial_info = await info()
    app.logger.debug(f'Storage server sends info about itself on start up to: {NAME_SERVER_IP}.')
    
    response = requests.post(
            f'http://{NAME_SERVER_IP}/storage/register',
            json=initial_info
        )
    
    if response.status_code != 200:
        logger.error(f'Something went wrong: {response.json()["detail"]}')


    data = response.json()
    app.logger.debug('Storage server sends info to replication function.')
    await replicate(data['address'], data['blocks_to_delete'], data['blocks_to_replicate'])


async def replicate(address: str, blocks_to_delete: List[str], blocks_to_replicate: List[str]):
    '''
    Function that replicates the data
    Params:
    - **address**: address of another storage server to get the blocks for replication
    - **blocks_to_delete**: names of blocks for deletion on the current storage server
    - **blocks_to_replicate**: names of blocks to get from **address** and put on the current storage server
    '''
    app.logger.debug('Storage server starts replication function.')
    app.logger.debug('Storage server is deleting blocks.')
    for block in blocks_to_delete:
        await delete(servers=[], filename=block)
    
    app.logger.debug('Storage server is getting and writing blocks.')
    for block in blocks_to_replicate:
        response = requests.get(f'http://{address}/file/get', {"filename": block})
        if response.status_code == 200:
            file_address = DATA_DIR + block

            with open(file_address, 'wb') as buffer:
                shutil.copyfileobj(response.json(), buffer)

        else:
            raise HTTPException(status_code=404, detail=str(response.json()["detail"]))
    
    app.logger.debug('Storage server is done with replication.')
    

@app.post('/init', summary='Initialize the server')
async def init(servers: List[str] = Body(...)):
    '''
    - **servers**: list of ip addresses with corresponding port where to create the file
    '''

    app.logger.debug(f'Storage server recieved servers list: {servers}.')
    app.logger.debug('Storage server has started init process.')

    for filename in os.listdir(DATA_DIR):
        file_path = os.path.join(DATA_DIR, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logger.error(f'Storage server didn\'t failed to delete the file: {file_path}.')
            app.logger.debug('Storage server sent response with status code 400.')
            raise HTTPException(status_code=400, detail=f'{file_path} is failed to be deleted. Error: {e}')
    
    app.logger.debug('Storage server is ready to forward request to other servers.')

    if len(servers) > 1:
        await forward_init(servers)

    app.logger.debug('Storage server finished with initialising.')
    app.logger.debug('Storage server sent response with status code 200.')

    return {'message': 'The server is initialised.'}


async def forward_init(servers: List[str]):
    '''
    - **servers**: list of ip addresses with corresponding port where to create the file
    - **filename**: name of file that client wants to create
    '''
    server = servers[1]
    servers = servers[1:]

    app.logger.debug(f'Storage server {server} is forwarding request to other servers {servers}.')

    response = requests.post(f'http://{server}/init', json=servers)

    if response.status_code != 200:
        logger.error(f'Something went wrong: {response.json()["detail"]}')
    
    app.logger.debug(f'Storage server {server} forwarded request to other servers {servers}.')


@app.get('/storage/info', summary='Information about storage server')
async def info():
    app.logger.debug('Storage server is prepairing the info.')
    app.logger.debug('Storage server is extracting an ip of docker.')
    try: 
        docker_name = socket.gethostname() 
        docker_ip = socket.gethostbyname(docker_name)
        docker_ip = f'{docker_ip}:{PORT}'
    except: 
        raise HTTPException(status_code=400, detail='Unable to get IP of docker')

    app.logger.debug('Storage server is prepairing the info about block names.')
    blocks = [str(f) for f in os.listdir(DATA_DIR)]
    app.logger.debug('Storage server is sending the info.')
    return {'hostname': IP, 'dockername' : docker_ip, 'blocks': blocks}


@app.post('/file/create', summary='Create file')
async def create(servers: List[str] = Body(...), filename: str = Body(...)):
    '''
    - **servers**: list of ip addresses with corresponding port where to create the file
    - **filename**: name of file that client wants to create
    '''
    app.logger.debug(f'Storage server recieved servers list: {servers}.')
    app.logger.debug(f'Storage server has started creating file: {filename}.')

    file_address = DATA_DIR + filename

    with open(file_address, 'w'):
        pass
    if not os.path.isfile(file_address):

        logger.error(f'Storage server didn\'t create the file: {filename}.')
        app.logger.debug('Storage server sent response with status code 404.')
        raise HTTPException(status_code=404, detail=f'File {filename} is not found in directory!')
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
    - **servers**: list of ip addresses with corresponding port where to create the file
    - **filename**: name of file that client wants to create
    '''
    server = servers[1]
    servers = servers[1:]

    app.logger.debug(f'Storage server {server} is forwarding request to other servers {servers}.')

    response = requests.post(f'http://{server}/file/create', json={'servers': servers, 'filename': filename})

    if response.status_code != 200:
        logger.error(f'Something went wrong: {response.json()["detail"]}')
    
    app.logger.debug(f'Storage server {server} forwarded request to other servers {servers}.')


@app.post('/file/put', summary='Write a file')
async def put(servers: list, file: UploadFile = File(...)):
    '''
    - **servers**: list of ip addresses with corresponding port where to replicate the file
    - **file**: file itself to upload, it's name I suppose in format of str
    '''
    app.logger.debug(f'Storage server recieved servers list: {servers}.')
    app.logger.debug(f'Storage server has started writing file: {file.filename}.')

    file_address = DATA_DIR + file.filename

    with open(file_address, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    if not os.path.isfile(file_address):
        logger.error(f'Storage server didn\'t write the file: {file.filename}.')
        logger.error('Storage server raised an error with status code 400.')
        raise HTTPException(status_code=400, detail=f'File {file.filename} is not found in directory!')
        
    app.logger.debug(f'Storage server wrote file: {file.filename}.')
    app.logger.debug('Storage server is ready to forward request to other servers.')

    if len(servers) > 1:
        await forward_put(servers, file)

    app.logger.debug('Storage server finished with writing the file.')
    app.logger.debug('Storage server sent response with status code 200.')

    return {'filename': file.filename, 'message': 'Data is recieved!'}


async def forward_put(servers: list, file: UploadFile = File(...)):
    '''
    - **servers**: list of ip addresses with corresponding port where to replicate the file
    - **file**: file itself to upload, it's name I suppose in format of str
    '''
    server = servers[1]
    servers = servers[1:]

    app.logger.debug(f'Storage server {server} is forwarding request to other servers {servers}.')

    
    with open(DATA_DIR + file.filename, 'rb') as f:
        files = {
            'file': (file.filename, f),
        }
        response = requests.post(f'http://{server}/file/put', data={'servers': servers}, files=files)

        if response.status_code != 200:
            logger.error(f'Something went wrong: {response.json()["detail"]}')
    
    app.logger.debug(f'Storage server {server} forwarded request to other servers {servers}.')


# block_uuid was replaced by filename because of 
# using this notation in function put
@app.get('/file/get', summary='Read a file')
async def get(filename: str):
    '''
    - **filename**: name of file that client wants to get
    '''
    app.logger.debug(f'Storage server recieved filename: {filename}.')
    app.logger.debug(f'Storage server is searching for a file: {filename}.')

    file_address = DATA_DIR + filename

    if not os.path.isfile(file_address):
        logger.error(f'Storage server didn\'t find the file: {filename}.')
        logger.error('Storage server raised an error with status code 400.')
        raise HTTPException(status_code=400, detail=f'File {filename} does not exist in directory!')
    with open(file_address) as f:
        app.logger.debug(f'Storage server has found the file: {filename}.')
        app.logger.debug(f'Storage server sending the file in response')
        return f.read() 


@app.post('/file/copy', summary='Copy a file')
async def copy(servers: List[str] = Body(...), filename: str = Body(...), newfilename: str = Body(...)):
    '''
    - **servers**: list of ip addresses with corresponding port where file need to be copied
    - **filename**: name of file that client wants to copy
    - **newfilename**: name of file copy
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


async def forward_copy(servers: List[str], filename: str, newfilename: str):
    '''
    - **servers**: list of ip addresses with corresponding port where file need to be copied
    - **filename**: name of file that client wants to copy
    - **newfilename**: name of file copy
    '''
    server = servers[1]
    servers = servers[1:]

    app.logger.debug(f'Storage server {server} is forwarding request to other servers {servers}.')

    response = requests.post(f'http://{server}/file/copy', json={'servers': servers, 'filename': filename, 'newfilename': newfilename})

    if response.status_code != 200:
        logger.error(f'Something went wrong: {response.json()["detail"]}')
    
    app.logger.debug(f'Storage server {server} forwarded request to other servers {servers}.')


@app.post('/file/delete', summary='Delete a file')
async def delete(servers: List[str] = Body(...), filename: str = Body(...)):
    '''
    - **servers**: list of ip addresses with corresponding port where to delete the file
    - **filename**: name of file that client wants to delete
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


async def forward_delete(servers: List[str], filename: str):
    '''
    - **servers**: list of ip addresses with corresponding port where to delete the file
    - **filename**: name of file that client wants to delete
    '''
    server = servers[1]
    servers = servers[1:]

    app.logger.debug(f'Storage server {server} is forwarding request to other servers {servers}.')

    response = requests.post(f'http://{server}/file/delete', json={'servers': servers, 'filename': filename})

    if response.status_code != 200:
        logger.error(f'Something went wrong: {response.status_code}')
    
    app.logger.debug(f'Storage server {server} forwarded request to other servers {servers}.')


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=PORT)

