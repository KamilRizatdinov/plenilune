import os

import requests
import fire

name_server_address = "http://0.0.0.0"  # we should change it
name_server_port = 80


def get_blocks(url, params):
    print("Connecting to Name Server...")
    response = requests.get(url, params)
    if response.status_code == 200:
        print("Success!")
        return response.json()
    else:
        print("Something went wrong:", response.json()["detail"])
        return


def write(filename: str):
    print("Write", filename, "command received!")
    filesize = os.path.getsize(filename)
    params = {"filename": filename, "filesize": filesize}
    url = name_server_address + "/file/write"
    data = get_blocks(url, params)
    blocks = data["blocks"]
    block_size = data["block_size"]
    file = open(filename, 'rb')
    print("Connecting to Data Servers...")
    for block in blocks:
        block_name = block["block_name"]
        storage_server_addresses = block["addresses"]
        response = requests.post(
            f'http://{storage_server_addresses[0]}/file/put',
            data={'servers': storage_server_addresses},
            files={'file': (block_name, file.read(block_size))}
        )
        if response.status_code == 200:
            print("You had successfully upload the file!")
            print(response.json())
        else:
            print("Something went wrong:", response.status_code, response.reason)


def info(filename):
    print("Get", filename, "information command received!")
    filesize = os.path.getsize(filename)
    params = {"filename": filename, "filesize": filesize}
    url = name_server_address + "/file/info"
    data = get_blocks(url, params)
    print(data)


def read(filename):
    print("Read", filename, "command received!")
    filesize = os.path.getsize(filename)
    params = {"filename": filename, "filesize": filesize}
    url = name_server_address + "/file/read"
    data = get_blocks(url, params)

    blocks = data["blocks"]
    print("Connecting to Data Servers...")
    for block in blocks:
        storage_server_addresses = block["addresses"]
        response = requests.get(f'http://{storage_server_addresses[0]}/file/get')
        if response.status_code == 200:
            print("You had successfully upload the file!")
            print(response.json())
        else:
            print("Something went wrong:", response.json()["detail"])


def delete(filename):
    print("Delete", filename, "command received!")
    filesize = os.path.getsize(filename)
    params = {"filename": filename, "filesize": filesize}
    url = name_server_address + "/file/delete"
    data = get_blocks(url, params)
    print("You have successfully deleted the file!")


def create(filename):
    params = {"filename": filename}
    print("Create", filename, "command received!")
    open("filename", "w+")
    url = name_server_address + "/file/create"
    data_server = get_blocks(url, params)
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
