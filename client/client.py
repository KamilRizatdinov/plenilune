import os
import pprint
import requests
import fire

name_server_address = "3.22.44.23:80"


def write(filename: str):
    filesize = os.path.getsize(filename)
    response = requests.get(f'http://{name_server_address}/file/write',
                            {"filename": filename, "filesize": filesize})
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
            {'servers': storage_server_addresses},
            files={'file': (block_name, file.read(size))},
        )

        if response.status_code != 200:
            print(response.json()["detail"])
            return
        
        print(response.json())
    print(f'File uploaded: {filename}')


def info(filename):
    response = requests.get(f'http://{name_server_address}/file/info',
                            {"filename": filename})

    if response.status_code != 200:
        print(response.json()["detail"])
        return

    data = response.json()
    pprint.pprint(data)


def delete(filename):
    response = requests.get(f'http://{name_server_address}/file/delete',
                            {"filename": filename})

    if response.status_code != 200:
        print(response.json()["detail"])
        return

    data = response.json()
    blocks = data["blocks"]

    for block in blocks:
        block_name = block["block_name"]
        storage_server_addresses = block["addresses"]
        response = requests.post(
            f'http://{storage_server_addresses[0]}/file/delete',
            json={'servers': storage_server_addresses, 'filename': block_name}
        )
        print(storage_server_addresses, block_name)

        if response.status_code != 200:
            print("Something went wrong:", response.status_code, response.reason)
            return
        
    print(f'File deleted: {filename}')


def initialize():
    response = requests.get(f'http://{name_server_address}/init')

    if response.status_code == 200:
        print("File system initialized")
    else:
        print("Something went wrong:", response.status_code, response.reason)


def read(filename):
    response = requests.get(f'http://{name_server_address}/file/read',
                            {"filename": filename})
    data = response.json()

    if response.status_code != 200:
        print(response.json()["detail"])
        return
    
    file = open(filename, "w+")
    blocks = data["blocks"]
    
    for block in blocks:
        block_name = block["block_name"]
        storage_server_addresses = block["addresses"]
        response = requests.get(f'http://{storage_server_addresses[0]}/file/get',
                                {"filename": block_name})

        if response.status_code == 200:
            file.write(response.json())
        else:
            print(response.json()["detail"])

    print(f'File downloaded: {filename}')


def create(filename):
    response = requests.get(f'http://{name_server_address}/file/create',
                            {"filename": filename})
    data = response.json()

    if response.status_code != 200:
        print(response.json()["detail"])
        return
    
    blocks = data["blocks"]
    for block in blocks:
        storage_server_addresses = block["addresses"]
        response = requests.post(f'http://{storage_server_addresses[0]}/file/create',
                                json={"servers": storage_server_addresses, "filename": block["block_name"]})
        if response.status_code != 200:
            print("Something went wrong:", response.status_code)

    print(f'File created: {filename}')


def copy(filename, destination):
    response = requests.get(f'http://{name_server_address}/file/copy',
                            {"filename": filename, "destination": destination})
    data = response.json()

    if response.status_code != 200:
        print(response.json()["detail"])
        return

    blocks = data["blocks"]
    for block in blocks:
        storage_server_addresses = block["addresses"]
        response = requests.get(f'http://{storage_server_addresses[0]}/file/copy',
                                json={"servers": storage_server_addresses, "filename": block["block_name"], "newfilename": block["copy_name"]})

        if response.status_code != 200:
            print("Something went wrong:", response.status_code)

    print(f'File copied: {destination}')


def move(filename, destination):
    response = requests.get(f'http://{name_server_address}/file/move',
                            {"filename": filename, "destination": destination})

    if response.status_code != 200:
        print(response.json()["detail"])
        return
    
    print(response.json()["detail"])


def create_dir(dirname):
    response = requests.get(f'http://{name_server_address}/dir/create',
                            {"dirname": dirname})

    if response.status_code != 200:
        print(response.json()["detail"])
        return
    
    print(response.json()["detail"])


def open_dir(dirname):
    response = requests.get(f'http://{name_server_address}/dir/open',
                            {"dirname": dirname})

    if response.status_code != 200:
        print(response.json()["detail"])
        return

    print(response.json()["detail"])


def delete_dir(dirname, flag=None):
    response = requests.get(f'http://{name_server_address}/dir/delete',
                            {"dirname": dirname, "flag": flag})

    if response.status_code != 200:
        print(response.json()["detail"])
        return
    
    print(response.json()["detail"])


def read_dir():
    response = requests.get(f'http://{name_server_address}/dir/read')

    if response.status_code != 200:
        print(response.json()["detail"])
        return
    
    print(response.json())


def status():
    response = requests.get(f'http://{name_server_address}/status')

    if response.status_code != 200:
        print(response.json()["detail"])
        return
    
    pprint.pprint(response.json())


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
