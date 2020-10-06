import os

import requests
import fire

name_server_address = "127.0.0.1:80" #"3.22.44.23:80"


def write(filename: str):
    filesize = os.path.getsize(filename)
    response = requests.get(f'http://{name_server_address}/file/write', {"filename": filename, "filesize": filesize})
    data = response.json()

    if response.status_code != 200:
        print(response.json()["detail"])
        return
    
    blocks = data["blocks"]
    size = data['block_size']
    file = open(filename, 'rb')

    for block in blocks:
        block_name = block["block_name"]
        storage_server_addresses = block["addresses"]

        response = requests.post(
            f'http://{storage_server_addresses[0]}/file/put',
            data={'servers': storage_server_addresses},
            files={'file': (block_name, file.read(size))}
        )

        if response.status_code != 200:
            print(response.json()["detail"])
            return
        
        print(response.json())
    print(f"File uploaded: '{filename}'")


def info(filename):
    response = requests.get(f'http://{name_server_address}/file/info', {"filename": filename})
    data = response.json()

    if response.status_code != 200:
        print(response.json()["detail"])
        return
    
    print(data)


def delete(filename):
    response = requests.get(f'http://{name_server_address}/file/delete', {"filename": filename})

    if response.status_code != 200:
        print(response.json()["detail"])
        return
    data = response.json()
    blocks = data["blocks"]
    print("Connecting to Data Servers...")
    for block in blocks:
        block_name = block["name"]
        storage_server_addresses = block["addresses"]
        response = requests.delete(
            f'http://{storage_server_addresses[0]}/file/delete',
            data={'servers': storage_server_addresses},
            files={'filename': block_name}
        )
        if response.status_code != 200:
            print("Something went wrong:", response.status_code, response.reason)
            return
        print(response.json())
    print("You have successfully deleted the file!")


def initialize():
    response = requests.get(f'http://{name_server_address}/init')

    if response.status_code == 200:
        print("File system initialized")
    else:
        print("Something went wrong:", response.status_code, response.reason)


def read(filename):
    response = requests.get(f'http://{name_server_address}/file/read', {"filename": filename})
    data = response.json()

    if response.status_code != 200:
        print(response.json()["detail"])
        return
    
    file = open(filename, "w+")
    blocks = data["blocks"]
    block_size = data["block_size"]
    
    for block in blocks:
        block_name = block["block_name"]
        storage_server_addresses = block["addresses"]
        response = requests.get(f'http://{storage_server_addresses[0]}/file/get', {"filename": block_name})

        if response.status_code == 200:
            file.write(response.json())
        else:
            print(response.json()["detail"])
    print(f"File downloaded: '{filename}'")


def create(filename):
    print("Create", filename, "command received!")
    params = {"filename": filename}
    url = name_server_address + "/file/create"
    print("Connecting to Name Server...")
    response = requests.get(f'http://{url}', params)
    data = response.json()
    if response.status_code != 200:
        print(response.json()["detail"])
        return
    blocks = data["blocks"]
    for block in blocks:
        storage_server_addresses = block["addresses"]
        response = requests.get(f'http://{storage_server_addresses[0]}/file/create',
                                params={"servers": storage_server_addresses, "filename": filename})
        if response.status_code != 200:
            print("Somethiing went wrong:", response.status_code)

    print("You had successfully created a new file!")


def copy(filename):
    print("Copy", filename, "command received!")
    filesize = os.path.getsize(filename)
    params = {"filename": filename, "filesize": filesize}
    url = name_server_address + "/file/copy"
    print("Connecting to Name Server...")
    response = requests.get(f'http://{url}', params)
    data = response.json()
    if response.status_code != 200:
        print(response.json()["detail"])
        return
    src_blocks = data["src_blocks"]
    dest_blocks = data["dest_blocks"]

    print("You had successfully copied the file!")


def move(filename, destination):
    print("Move", filename, "to", destination, "command received!")
    params = {"filename": filename, "destination": destination}
    url = name_server_address + "/file/move"
    print("Connecting to Name Server...")
    response = requests.get(f'http://{url}', params)
    if response.status_code != 200:
        print(response.json()["detail"])
        return
    print("You had successfully moved the file!")


def create_dir(dirname):
    print("Create directory", dirname, "command received!")
    params = {"dirname": dirname}
    url = name_server_address + "/dir/create"
    print("Connecting to Name Server...")
    response = requests.get(f'http://{url}', params)
    if response.status_code != 200:
        print(response.json()["detail"])
        return
    print("You had successfully created a new directory!")


def open_dir(dirname):
    print("Open directory", dirname, "command received!")
    params = {"dirname": dirname}
    url = name_server_address + "/dir/open"
    print("Connecting to Name Server...")
    response = requests.get(f'http://{url}', params)
    if response.status_code != 200:
        print(response.json()["detail"])
        return
    print("You are in", dirname, "directory!")


def delete_dir(dirname, flag=None):
    print("Delete directory", dirname, "command received!")
    params = {"dirname": dirname, "flag": flag}
    url = name_server_address + "/dir/delete"
    print("Connecting to Name Server...")
    response = requests.get(f'http://{url}', params)
    if response.status_code != 200:
        print(response.json()["detail"])
        return
    print("You had successfully deleted the directory!")


def read_dir():
    print("Read directory command received!")
    url = name_server_address + "/dir/read"
    print("Connecting to Name Server...")
    response = requests.get(f'http://{url}')
    if response.status_code != 200:
        print(response.json()["detail"])
        return
    data = response.json()
    print(data)


def status():
    print("Status command received!")
    url = name_server_address + "/status"
    print("Connecting to Name Server...")
    response = requests.get(f'http://{url}')
    if response.status_code != 200:
        print(response.json()["detail"])
        return
    data = response.json()
    print(data)


if __name__ == "__main__":
    fire.Fire({
        "get": read,
        "put": write,
        "rm": delete,           # works
        "init": initialize,     # works
        "info": info,           # works
        "copy": copy,
        "create": create,
        "move": move,           # works
        "ls": read_dir,         # works
        "rmdir": delete_dir,    # works
        "cd": open_dir,         # works
        "mkdir": create_dir,    # works
        "status": status        # works
    })
