import uvicorn
from fastapi import FastAPI, UploadFile, File
import os
import shutil
import requests
from pydantic import BaseModel

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
    #     forward(servers, file)
    return {'filename': file.filename, 'message': 'Data is recieved!'}


# @app.post('/server/client/put/')
# async def put(block: Block):
#     with open(DATA_DIR + str(block.block_uuid), 'w') as f:
#         f.write(block.data)
#     return {'message': 'Data is recieved!'}


# block_uuid was replaced by filename because of 
# using this notation in function put
@app.get('/file/get/{filename}')
async def get(filename: str):
    '''
    filename: name of file that client wants to get
    '''
    block_address = DATA_DIR + filename
    if not os.path.isfile(block_address):
        return {'message': 'No such file on the server'}
    with open(block_address) as f:
        return f.read() 


async def forward(servers: list, file: UploadFile = File(...)):
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


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)