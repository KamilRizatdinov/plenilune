import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Response
import os
import shutil
import requests

app = FastAPI()

DATA_DIR = '/'

@app.post('/file/put')
async def put(servers: list, file: UploadFile = File(...)):
    '''
    servers: list of ip addresses with corresponding port where to replicate the file
    file: file itself to upload, it's name I suppose in format of str
    '''
    with open(DATA_DIR + file.filename, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)
    # if len(servers) > 0:
    #     forward_put(servers, file)
    return {'filename': file.filename, 'message': 'Data is recieved!'}


async def forward_put(servers: list, file: UploadFile = File(...)):
    '''
    servers: list of ip addresses with corresponding port where to replicate the file
    file: file itself to upload, it's name I suppose in format of str
    '''
    server = servers[0]
    servers = servers[1:]

    files = {
        'file': (file.filename, open(DATA_DIR + file.filename, 'rb')),
    }

    requests.post('http://' + server + 'file/put', files=files)


# block_uuid was replaced by filename because of 
# using this notation in function put
@app.get('/file/get/')
async def get(filename: str):
    '''
    filename: name of file that client wants to get
    '''
    block_address = DATA_DIR + filename
    if not os.path.isfile(block_address):
        raise HTTPException(status_code=400, detail=f'File "{filename}" does not exist in directory!')
    with open(block_address) as f:
        return f.read() 


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
    block_address = DATA_DIR + filename
    if not os.path.isfile(block_address):
        return Response(status_code=404)
    else:
        os.remove(block_address)
        forward_delete(servers, filename)
    return Response(status_code=200)


async def forward_delete(servers: list, filename: str):
    '''
    servers: list of ip addresses with corresponding port where to delete the file
    filename: name of file that client wants to delete
    '''
    server = servers[0]
    servers = servers[1:]

    requests.post('http://' + server + 'file/delete', data={'servers': servers, 'filename': filename},)


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)