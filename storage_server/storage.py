import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Response
import os
import shutil
import requests
import logging
import logging.config

app = FastAPI()

"""
Based on http://docs.python.org/howto/logging.html#configuring-logging
"""
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('storage')

@app.post('/file/create',
    summary='Create block',
    response_class=Response,
    responses={
        200: {'message': 'Block is successfully created'},
        404: {'message': 'Block is not created'},
    },
)
async def create(servers: list, filename: str):
    '''
    servers: list of ip addresses with corresponding port where to create the file
    filename: name of file that client wants to create
    '''
    logger.info(f'Storage server recieved servers list: {servers}.')
    logger.info(f'Storage server has started creating file: {filename}.')

    with open(filename, 'w'):
        pass
    if not os.path.isfile(filename):

        logger.error(f'Storage server didn\'t create the file: {filename}.')
        logger.info('Storage server sent response with status code 404.')

        return Response(status_code=404)
    
    logger.info(f'Storage server created file: {filename}.')
    logger.info('Storage server is ready to forward request to other servers.')

    if len(servers) > 1:
        await forward_create(servers, filename)
    
    logger.info('Storage server finished with creation of the file.')
    logger.info('Storage server sent response with status code 200.')

    return Response(status_code=200)


async def forward_create(servers: list, filename: str):
    '''
    servers: list of ip addresses with corresponding port where to create the file
    filename: name of file that client wants to create
    '''
    server = servers[1]
    servers = servers[1:]

    logger.info(f'Storage server {server} is forwarding request to other servers {servers}.')

    response = requests.post('http://' + server + '/file/create', data={'servers': servers, 'filename': filename})

    if response.status_code != 200:
        logger.error(f'Something went wrong: {response.json()["detail"]}')
    
    logger.info(f'Storage server {server} forwarded request to other servers {servers}.')


@app.post('/file/put')
async def put(servers: list, file: UploadFile = File(...)):
    '''
    servers: list of ip addresses with corresponding port where to replicate the file
    file: file itself to upload, it's name I suppose in format of str
    '''
    logger.info(f'Storage server recieved servers list: {servers}.')
    logger.info(f'Storage server has started writing file: {file.filename}.')

    with open(file.filename, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    if not os.path.isfile(file.filename):
        logger.error(f'Storage server didn\'t write the file: {file.filename}.')
        logger.error('Storage server raised an error with status code 400.')
        raise HTTPException(status_code=400, detail=f'File "{file.filename}" is not found in directory!')
        
    logger.info(f'Storage server wrote file: {file.filename}.')
    logger.info('Storage server is ready to forward request to other servers.')

    if len(servers) > 1:
        await forward_put(servers, file)

    logger.info('Storage server finished with writing the file.')
    logger.info('Storage server sent response with status code 200.')

    return {'filename': file.filename, 'message': 'Data is recieved!'}


async def forward_put(servers: list, file: UploadFile = File(...)):
    '''
    servers: list of ip addresses with corresponding port where to replicate the file
    file: file itself to upload, it's name I suppose in format of str
    '''
    server = servers[1]
    servers = servers[1:]

    logger.info(f'Storage server {server} is forwarding request to other servers {servers}.')

    files = {
        'file': (file.filename, open(file.filename, 'rb')),
    }

    response = requests.post('http://' + server + '/file/put', data={'servers': servers}, files=files)

    if response.status_code != 200:
        logger.error(f'Something went wrong: {response.json()["detail"]}')
    
    logger.info(f'Storage server {server} forwarded request to other servers {servers}.')


# block_uuid was replaced by filename because of 
# using this notation in function put
@app.get('/file/get')
async def get(filename: str):
    '''
    filename: name of file that client wants to get
    '''
    logger.info(f'Storage server recieved filename: {filename}.')
    logger.info(f'Storage server is searching for a file: {filename}.')

    if not os.path.isfile(filename):
        logger.error(f'Storage server didn\'t find the file: {filename}.')
        logger.error('Storage server raised an error with status code 400.')
        raise HTTPException(status_code=400, detail=f'File "{filename}" does not exist in directory!')
    with open(filename) as f:
        logger.info(f'Storage server has found the file: {filename}.')
        logger.info(f'Storage server sending the file in response')
        return f.read() 


@app.post('/file/copy',
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
    logger.info(f'Storage server recieved servers list: {servers}.')
    logger.info(f'Storage server is copying file named {filename} to file with name {newfilename}.')

    with open(filename, 'rb') as f, open(newfilename) as copyfile:
        shutil.copyfileobj(f, copyfile)

    if not os.path.isfile(newfilename):
        logger.error(f'Storage server didn\'t copied the file :(')
        logger.error('Storage server raised an error with status code 400.')
        return Response(status_code=400)
    
    logger.info(f'Storage server copied the file {filename} into {newfilename}.')
    logger.info('Storage server is ready to forward request to other servers.')

    if len(servers) > 1:
        await forward_copy(servers, filename, newfilename)

    logger.info('Storage server finished with copying the file.')
    logger.info('Storage server sent response with status code 200.')

    return Response(status_code=200)


async def forward_copy(servers: list, filename: str, newfilename: str):
    '''
    servers: list of ip addresses with corresponding port where file need to be copied
    filename: name of file that client wants to copy
    newfilename: name of file copy
    '''
    server = servers[1]
    servers = servers[1:]

    logger.info(f'Storage server {server} is forwarding request to other servers {servers}.')

    response = requests.post('http://' + server + '/file/copy', data={'servers': servers, 'filename': filename, 'newfilename': newfilename})

    if response.status_code != 200:
        logger.error(f'Something went wrong: {response.json()["detail"]}')
    
    logger.info(f'Storage server {server} forwarded request to other servers {servers}.')


@app.delete('/file/delete',
    summary='Delete block',
    response_class=Response,
    responses={
        200: {'message': 'Block is successfully deleted'},
        404: {'message': 'Block is not found'},
    },
)
async def delete(servers: list, filename: str):
    '''
    servers: list of ip addresses with corresponding port where to delete the file
    filename: name of file that client wants to delete
    '''
    if not os.path.isfile(filename):
        logger.error(f'Storage server didn\'t find the file :(')
        logger.error('Storage server raised an error with status code 404.')
        return Response(status_code=404)
    else:
        logger.info('Storage server is deleting the file.')
        os.remove(filename)
    
    if os.path.isfile(filename):
        logger.error('Storage server didn\'t delete the file.')

    logger.info(f'Storage server deleted the file {filename}.')
    logger.info('Storage server is ready to forward request to other servers.')

    if len(servers) > 1:
        await forward_delete(servers, filename)
    
    logger.info('Storage server finished with deleting the file.')
    logger.info('Storage server sent response with status code 200.')

    return Response(status_code=200)


async def forward_delete(servers: list, filename: str):
    '''
    servers: list of ip addresses with corresponding port where to delete the file
    filename: name of file that client wants to delete
    '''
    server = servers[1]
    servers = servers[1:]

    logger.info(f'Storage server {server} is forwarding request to other servers {servers}.')

    response = requests.post('http://' + server + '/file/delete', data={'servers': servers, 'filename': filename})

    if response.status_code != 200:
        logger.error(f'Something went wrong: {response.json()["detail"]}')
    
    logger.info(f'Storage server {server} forwarded request to other servers {servers}.')


if __name__ == '__main__':
    logger.info('Storage server has started it\'s work!')
    uvicorn.run(app, host='0.0.0.0', port=8000)

