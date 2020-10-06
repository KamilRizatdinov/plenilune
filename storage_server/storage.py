import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Response
import os
import shutil
import requests

app = FastAPI()


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
    with open(filename, 'w'):
        pass
    if not os.path.isfile(filename):
        return Response(status_code=404)
    if len(servers) > 1:
        await forward_create(servers, filename)
    return Response(status_code=200)


async def forward_create(servers: list, filename: str):
    '''
    servers: list of ip addresses with corresponding port where to create the file
    filename: name of file that client wants to create
    '''
    server = servers[1]
    servers = servers[1:]

    requests.post('http://' + server + '/file/create', data={'servers': servers, 'filename': filename})


@app.post('/file/put')
async def put(servers: list, file: UploadFile = File(...)):
    '''
    servers: list of ip addresses with corresponding port where to replicate the file
    file: file itself to upload, it's name I suppose in format of str
    '''
    with open(file.filename, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)
    if len(servers) > 1:
        await forward_put(servers, file)
    return {'filename': file.filename, 'message': 'Data is recieved!'}


async def forward_put(servers: list, file: UploadFile = File(...)):
    '''
    servers: list of ip addresses with corresponding port where to replicate the file
    file: file itself to upload, it's name I suppose in format of str
    '''
    server = servers[1]
    servers = servers[1:]

    files = {
        'file': (file.filename, open(file.filename, 'rb')),
    }

    requests.post('http://' + server + '/file/put', data={'servers': servers}, files=files)


# block_uuid was replaced by filename because of 
# using this notation in function put
@app.get('/file/get')
async def get(filename: str):
    '''
    filename: name of file that client wants to get
    '''
    if not os.path.isfile(filename):
        raise HTTPException(status_code=400, detail=f'File "{filename}" does not exist in directory!')
    with open(filename) as f:
        return f.read() 


@app.post('/file/copy',
    summary='Copy block',
    response_class=Response,
    responses={
        200: {'message': 'Copy is successfully created'},
        404: {'message': 'Copy is not created'},
    },
)
async def copy(servers: list, filename: str, newfilename: str):
    '''
    servers: list of ip addresses with corresponding port where file need to be copied
    filename: name of file that client wants to copy
    newfilename: name of file copy
    '''
    with open(filename, 'rb') as f, open(newfilename) as copyfile:
        shutil.copyfileobj(f, copyfile)
    if not os.path.isfile(newfilename):
        return Response(status_code=404)
    if len(servers) > 1:
        await forward_copy(servers, filename, newfilename)
    return Response(status_code=200)


async def forward_copy(servers: list, filename: str, newfilename: str):
    '''
    servers: list of ip addresses with corresponding port where file need to be copied
    filename: name of file that client wants to copy
    newfilename: name of file copy
    '''
    server = servers[1]
    servers = servers[1:]

    requests.post('http://' + server + '/file/copy', data={'servers': servers, 'filename': filename, 'newfilename': newfilename})


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
        return Response(status_code=404)
    else:
        os.remove(filename)
    if len(servers) > 1:
        await forward_delete(servers, filename)
    return Response(status_code=200)


async def forward_delete(servers: list, filename: str):
    '''
    servers: list of ip addresses with corresponding port where to delete the file
    filename: name of file that client wants to delete
    '''
    server = servers[1]
    servers = servers[1:]

    requests.post('http://' + server + '/file/delete', data={'servers': servers, 'filename': filename})


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)

