from pydantic import BaseModel

class FileCopy(BaseModel):
    servers: list
    filename: str
    newfilename: str
