import os

import requests
import fire

name_server_address = "http://0.0.0.0"  # we should change it
name_server_port = 80


def write(filename: str):
    print("Write", filename, "command received!")
    filesize = os.path.getsize(filename)
    params = {"filename": filename, "filesize": filesize}
    url = name_server_address + "/file/write"
    print("Connecting to Name Server...")
    response = requests.get(url, params)

    data = response.json()
    if response.status_code != 200:
        print(response.json()["detail"])
        return
    blocks = data["blocks"]
    size = data['block_size']

    file = open(filename, 'rb')
    print("Connecting to Data Servers...")
    for block in blocks:
        block_name = block["block_name"]
        storage_server_addresses = block["addresses"]
        response = requests.post(
            f'http://{storage_server_addresses[0]}/file/put',
            data={'servers': storage_server_addresses},
            files={'file': (block_name, file.read(size))}
        )
        if response.status_code != 200:
            print("Something went wrong:", response.status_code, response.reason)
            return
        print(response.json())
    print("You had successfully upload the file!")


def info(filename):
    print("Get", filename, "information command received!")
    filesize = os.path.getsize(filename)
    params = {"filename": filename, "filesize": filesize}
    url = name_server_address + "/file/info"
    print("Connecting to Name Server...")
    response = requests.get(url, params)
    data = response.json()
    if response.status_code != 200:
        print(response.json()["detail"])
        return
    print("Success! There is information about the file:")
    print(data)


def delete(filename):
    print("Delete", filename, "command received!")
    filesize = os.path.getsize(filename)
    params = {"filename": filename, "filesize": filesize}
    url = name_server_address + "/file/delete"
    response = requests.get(url, params)
    if response.status_code != 200:
        print(response.json()["detail"])
        return
    print("You have successfully deleted the file!")


def initialize():
    print("Initialize command received!")
    print("Connecting to Name Server...")
    url = name_server_address + "/init"
    response = requests.get(url)
    if response.status_code == 200:
        print("You have successfully connect to the name server!")
    else:
        print("Something went wrong:", response.status_code, response.reason)


def read(filename):
    print("Read", filename, "command received!")
    filesize = os.path.getsize(filename)
    params = {"filename": filename, "filesize": filesize}
    url = name_server_address + "/file/read"
    response = requests.get(url, params)
    data = response.json()
    if response.status_code != 200:
        print(response.json()["detail"])
        return
    file = open(filename, "w+")
    blocks = data["blocks"]
    block_size = data["block_size"]
    print("Connecting to Data Servers...")
    for block in blocks:
        block_name = block["block_name"]
        storage_server_addresses = block["addresses"]
        response = requests.get(f'http://{storage_server_addresses[0]}/file/get')
        if response.status_code == 200:
            file.write(response.json())
        else:
            print("Something went wrong:", response.json()["detail"])
    print("You had successfully upload the file!")


if __name__ == "__main__":
    fire.Fire({
        "get": read,
        "put": write,
        "rm": delete,
        "init": initialize,
        "info": info
    })
