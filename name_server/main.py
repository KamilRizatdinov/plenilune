from fastapi import FastAPI

app = FastAPI()

# Data stored in runtime
fsimage = {
    ".": {
        "dirs": [],
        "files": {}
    }
}
storage_servers = {}
client_cursros = "."

# Client side API
@app.get("/api/client/init")
async def client_init():
    return {"message": "Initialize request recieved!"}


@app.get("/api/client/read")
async def client_read():
    return {"message": "Read request recieved!"}


@app.get("/api/client/write")
async def client_write():
    return {"message": "Write request recieved!"}


@app.get("/api/client/fetch")
async def client_write():
    return {"message": "Fetch request recieved!"}

# Storage side API
@app.get("/api/storage/update")
async def storage_update():
    return {"message": "Update request recieved!"}
