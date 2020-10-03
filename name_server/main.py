from fastapi import FastAPI

app = FastAPI()

# Data stored in runtime
fsimage = {}
storage_servers = []
storage_fsimages = []
storage_status = []

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

# Storage side API
@app.get("/api/storage/update")
async def storage_update():
    return {"message": "Update request recieved!"}
