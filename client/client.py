import os

import requests
import fire

name_server_address = "http://0.0.0.0"  # we should change it
name_server_port = 80


def get_data_server_address(params):
    print("Connecting to Name Server...")
    response = requests.get(name_server_address, params)
    if response.status_code == 200:
        print("You have successfully obtained the address of the data server!")
    else:
        print("Something went wrong:", response.status_code, response.reason)
    data_server = response.json()
    return data_server["address"]


def read(filename):
    params = {"filename": filename}
    print("Read", filename, "command received!")
    data_server = get_data_server_address(params)
    url = data_server + "/file/read"
    print("Connecting to Data Server...")
    response = requests.get(url, params)
    if response.status_code == 200:
        print("Success!")
        data = response.json()
        print(data)
    else:
        print("Something went wrong:", response.status_code, response.reason)


def write(filename: str):
    filesize = os.path.getsize(filename)
    name_server_response = requests.get(f"{name_server_address}/file/write", params={"filename": filename, "filesize": filesize})
    
    if name_server_response.status_code != 200:
        print(name_server_response.json()["detail"])
        return
    
    data = name_server_response.json()
    blocks = data["blocks"]
    block_size = data["block_size"]

    for block in blocks:
        block_name = block["block_name"]
        storage_server_addresses = block["addresses"]

        storage_server_response = requests.post(
            f'http://{storage_server_addresses[0]}/file/put', 
            data={'servers': storage_server_addresses},
            files={'file': (filename, open(filename, 'rb'))}
        )
        print(storage_server_response.json())


def delete(filename):
    params = {"filename": filename}
    print("Delete", filename, "command received!")
    data_server = get_data_server_address(params)
    url = data_server + "/file/delete"
    print("Connecting to Data Server...")
    response = requests.delete(url, data=params)
    if response.status_code == 200:
        print("You have successfully delete the file!")
    else:
        print("Something went wrong:", response.status_code, response.reason)


def create(filename):
    params = {"filename": filename}
    print("Create", filename, "command received!")
    open("filename", "w+")
    data_server = get_data_server_address(params)
    url = data_server + "/file/create"
    print("Connecting to Data Server...")
    response = requests.post(url, params)
    if response.status_code == 200:
        print("You have successfully create a new file!")
    else:
        print("Something went wrong:", response.status_code, response.reason)


def initialize():
    print("Initialize command received!")
    print("Connecting to Name Server...")
    url = name_server_address + "/init"
    response = requests.get(url)
    if response.status_code == 200:
        print("You have successfully connect to the name server!")
    else:
        print("Something went wrong:", response.status_code, response.reason)


if __name__ == "__main__":
    fire.Fire({
        "get": read,
        "put": write,
        "rm": delete,
        "touch": create,
        "init": initialize
    })
