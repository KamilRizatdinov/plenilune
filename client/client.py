import os
import pprint
import requests
import fire

name_server_address = "3.22.44.23:80"


def write(filename: str):
    """
    Uploads a file to the DFS
    :param filename: a name of file to upload
    """
    filesize = os.path.getsize(filename)
    response = requests.get(f'http://{name_server_address}/file/write',
                            {"filename": filename, "filesize": filesize})
    data = response.json()

    if response.status_code != 200:
        print(response.json()["detail"])
        return
    
    blocks = data["blocks"]
    storage_server_addresses = data["addresses"]
    size = data['block_size']
    file = open(filename, 'rb')

    for block in blocks:
        block_name = block["block_name"]

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
    """
    Provides information about the file
    :param filename: a name of file to get information about
    """
    response = requests.get(f'http://{name_server_address}/file/info',
                            {"filename": filename})

    if response.status_code != 200:
        print(response.json()["detail"])
        return

    data = response.json()
    pprint.pprint(data)


def delete(filename):
    """
    Deletes a file from DFS
    :param filename: a name of file to delete
    """
    response = requests.get(f'http://{name_server_address}/file/delete',
                            {"filename": filename})

    if response.status_code != 200:
        print(response.json()["detail"])
        return

    data = response.json()
    blocks = data["blocks"]
    storage_server_addresses = data["addresses"]

    for block in blocks:
        block_name = block["block_name"]
        response = requests.post(
            f'http://{storage_server_addresses[0]}/file/delete',
            json={'servers': storage_server_addresses, 'filename': block_name}
        )
        print(storage_server_addresses, block_name)

        if response.status_code != 200:
            print("Something went wrong:", response.status_code, response.reason)
            return
        
    print(f'File deleted: {filename}')


def initialize(block_size=1024):
    '''
    Initializes the client storage on a new system, removes any existing file in the dfs root directory
    :param block_size: a size of data blocks in storage servers, by default is 1024
    '''
    response = requests.get(f'http://{name_server_address}/init',
                            {"blocksize": block_size})

    data = response.json()
    storage_server_addresses = data["servers"]

    if storage_server_addresses:
        requests.post(
                f'http://{storage_server_addresses[0]}/init',
                json=storage_server_addresses
        )
    
    print('System initialized')


def read(filename):
    '''
    Downloads a file from the DFS
    :param filename: a name of file to download
    '''
    response = requests.get(f'http://{name_server_address}/file/read',
                            {"filename": filename})
    data = response.json()

    if response.status_code != 200:
        print(response.json()["detail"])
        return
    
    file = open(filename, "w+")
    blocks = data["blocks"]
    storage_server_addresses = data["addresses"]
    
    for block in blocks:
        block_name = block["block_name"]
        response = requests.get(f'http://{storage_server_addresses[0]}/file/get',
                                {"filename": block_name})

        if response.status_code == 200:
            file.write(response.json())
        else:
            print(response.json()["detail"])

    print(f'File downloaded: {filename}')


def create(filename):
    '''
    Creates a new empty file
    :param filename: a name of file to create
    '''
    response = requests.get(f'http://{name_server_address}/file/create',
                            {"filename": filename})
    data = response.json()

    if response.status_code != 200:
        print(response.json()["detail"])
        return
    
    blocks = data["blocks"]
    storage_server_addresses = data["addresses"]

    for block in blocks:
        response = requests.post(f'http://{storage_server_addresses[0]}/file/create',
                                json={"servers": storage_server_addresses, "filename": block["block_name"]})
        if response.status_code != 200:
            print("Something went wrong:", response.status_code)

    print(f'File created: {filename}')


def copy(filename, destination):
    """
    Creates a copy of file in the destination directory
    :param filename: a name of file to copy
    :param destination: directory to allocate copy of file
    """
    response = requests.get(f'http://{name_server_address}/file/copy',
                            {"filename": filename, "destination": destination})
    data = response.json()

    if response.status_code != 200:
        print(response.json()["detail"])
        return

    blocks = data["blocks"]
    storage_server_addresses = data["addresses"]

    for block in blocks:
        response = requests.post(f'http://{storage_server_addresses[0]}/file/copy',
                                json={"servers": storage_server_addresses, "filename": block["block_name"], "newfilename": block["copy_name"]})

        if response.status_code != 200:
            print("Something went wrong:", response.status_code)

    print(f'File copied: {destination}')


def move(filename, destination):
    """
    Moves a file to the destination path
    :param filename: a name of file to move
    :param destination: a directory where allocate the file
    """
    response = requests.get(f'http://{name_server_address}/file/move',
                            {"filename": filename, "destination": destination})

    if response.status_code != 200:
        print(response.json()["detail"])
        return
    
    print(response.json()["detail"])


def create_dir(dirname):
    """
    Creates a new directory
    :param dirname: a name of directory to create
    """
    response = requests.get(f'http://{name_server_address}/dir/create',
                            {"dirname": dirname})

    if response.status_code != 200:
        print(response.json()["detail"])
        return
    
    print(response.json()["detail"])


def open_dir(dirname):
    """
    Opens a directory
    :param dirname: a name of directory to open
    """
    response = requests.get(f'http://{name_server_address}/dir/open',
                            {"dirname": dirname})

    if response.status_code != 200:
        print(response.json()["detail"])
        return

    print(response.json()["detail"])


def delete_dir(dirname, flag=None):
    """
    Deletes a directory
    :param dirname: a name or directory to delete
    :param flag: y if you want to delete directory with data inside it
    """
    response = requests.get(f'http://{name_server_address}/dir/delete',
                            {"dirname": dirname, "flag": flag})

    if response.status_code != 200:
        print(response.json()["detail"])
        return
    
    print(response.json()["detail"])


def read_dir():
    """
    Returns list of files, which are stored in the current directory
    """
    response = requests.get(f'http://{name_server_address}/dir/read')

    if response.status_code != 200:
        print(response.json()["detail"])
        return
    
    print(response.json())


def status():
    """
    Returns client status
    """
    response = requests.get(f'http://{name_server_address}/status')

    if response.status_code != 200:
        print(response.json()["detail"])
        return
    
    pprint.pprint(response.json())


if __name__ == "__main__":
    fire.Fire({
        "init": initialize,
        "create": create,
        "get": read,
        "put": write,
        "rm": delete,
        "info": info,
        "copy": copy,
        "move": move,
        "cd": open_dir,
        "ls": read_dir,
        "mkdir": create_dir,
        "rmdir": delete_dir,
        "status": status
    })
