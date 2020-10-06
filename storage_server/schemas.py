from pydantic import BaseModel

class BlockDelete(BaseModel):
    servers: list
    filename: str