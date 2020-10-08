import json
import random
import uuid

import redis
import requests


conn = redis.Redis('redis')


def dump_data():
    storage_servers = get_data()['storage_servers']
    set_data({
        "block_size": 1024,
        "replication": 1000,
        "fsimage": {
            ".": {
                "dirs": [],
                "files": {}
            }
        },
        "storage_servers": storage_servers,
        "client_cursor": "."
        }
    )


def set_data(data):
    conn.set("data", json.dumps(data))


def get_data():
    return json.loads(conn.get("data"))


def update_data(field, value):
    data = get_data()
    data[field] = value
    set_data(data)


def get_active_storage_servers_hostnames():
    storage_servers = get_data()['storage_servers']
    result = [storage_server['hostname'] for storage_server in storage_servers if storage_server["status"] == "UP"]
    random.shuffle(result)
    return result


def get_random_active_storage_server():
    storage_servers = get_data()["storage_servers"]
    active_storage_servers = [storage_server for storage_server in storage_servers if storage_server["status"] == "UP"]
    storage_server = random.choice(active_storage_servers)
    return storage_server


def get_blocks_difference(blocks):
    storage_server = get_random_active_storage_server()
    dest_blocks = storage_server["blocks"]
    blocks_to_delete = [block for block in blocks if block not in dest_blocks]
    blocks_to_replicate = [block for block in dest_blocks if block not in blocks]

    return (blocks_to_delete, blocks_to_replicate)


def register_storage_server(hostname: str, dockername: str, blocks: list):
    storage_servers = get_data()["storage_servers"]
    storage_servers_hostnames = [storage_server["hostname"] for storage_server in storage_servers]

    blocks_to_delete, blocks_to_replicate = get_blocks_difference(blocks)

    for block in blocks_to_delete:
        requests.post(
            f'http://{hostname}/file/delete',
            json={'servers': [hostname], 'filename': block}
        )
    
    for block in blocks_to_replicate:
        requests.post(
            f'http://{hostname}/file/delete',
            json={'server': hostname, 'filename': block}
        )

    if not hostname in storage_servers_hostnames:
        storage_servers.append({"hostname": hostname, "dockername": dockername, "status": "UP", "blocks": blocks})
        update_data("storage_servers", storage_servers)
    
    return {"hostname": hostname, "dockername": dockername, "status": "UP", "blocks": blocks}


def get_block_num(filesize: int):
    block_size = get_data()['block_size']
    if filesize % block_size == 0:
        return filesize // block_size
    return filesize // block_size + 1


def get_file_blocks(filename: str):
    data = get_data()
    client_cursor = data['client_cursor']
    fsimage = data['fsimage']
    
    if filename in fsimage[client_cursor]["files"].keys():
        return fsimage[client_cursor]["files"][filename]
    else:
        return None


def allocate_blocks(blocks_num: int):
    result = []
    for i in range(blocks_num):
        block_name = str(uuid.uuid1())
        result.append({"block_index": i, "block_name": block_name})
    return result


def check_file_existance(filename: str):
    return get_file_blocks(filename) != None


def create_file_entry(filename: str, blocks_allocation: list):
    data = get_data()
    client_cursor = data['client_cursor']
    fsimage = data['fsimage']
    fsimage[client_cursor]["files"][filename] = blocks_allocation
    update_data("fsimage", fsimage)


def init(block_size: int):
    dump_data()
    update_data('block_size', block_size)
    return get_active_storage_servers_hostnames()


def file_create(filename: str, filesize: int):
    blocks_num = get_block_num(filesize)
    blocks_allocation = allocate_blocks(blocks_num)
    create_file_entry(filename, blocks_allocation)
    return {
        "filename": filename, 
        "blocks": blocks_allocation, 
        "addresses": get_active_storage_servers_hostnames(), 
        "block_size": get_data()["block_size"]
    }


def file_read(filename: str):
    blocks = get_file_blocks(filename)
    return {
        "filename": filename, 
        "blocks": blocks, 
        "addresses": get_active_storage_servers_hostnames(),
        "block_size": get_data()["block_size"]
    }


def file_copy(filename: str, destination: str):
    blocks = get_file_blocks(filename)
    result = []
    copy_blocks = []
    for block in blocks:
        block["copy_name"] = str(uuid.uuid1())
        result.append(block)
        copy_block = block.copy()
        copy_block["block_name"] = copy_block.pop("copy_name")
        copy_blocks.append(copy_block)
    
    create_file_entry(destination, copy_blocks)

    return {
        "blocks": result, 
        "addresses": get_active_storage_servers_hostnames()
    }


def file_delete(filename: str):
    data = get_data()
    client_cursor = data['client_cursor']
    fsimage = data['fsimage']
    file_allocation = fsimage[client_cursor]["files"].pop(filename)
    update_data("fsimage", fsimage)
    return {
        "filename": filename, 
        "blocks": file_allocation, 
        "addresses": get_active_storage_servers_hostnames(),
        "block_size": get_data()["block_size"]
    }


def file_move(filename: str, destination: str):
    file_blocks = file_delete(filename)['blocks']
    directory_open(destination)
    create_file_entry(filename, file_blocks)
    directory_open('..')
    return {"detail": f"File '{filename}' moved to directory: {destination}"}


def file_info(filename: str):
    data = get_data()
    client_cursor = data['client_cursor']
    fsimage = data['fsimage']
    file_allocation = fsimage[client_cursor]["files"][filename]
    return {
        "filename": filename, 
        "blocks": file_allocation, 
        "addresses": get_active_storage_servers_hostnames(),
        "block_size": get_data()["block_size"]
    }


def check_directory_existance(dirname: str):
    data = get_data()
    client_cursor = data['client_cursor']
    fsimage = data['fsimage']
    if dirname in fsimage[client_cursor]["dirs"] or dirname == "..":
        return True
    return False


def directory_create(dirname: str):
    data = get_data()
    client_cursor = data['client_cursor']
    fsimage = data['fsimage']
    fsimage[client_cursor]["dirs"].append(dirname)
    fsimage[f'{client_cursor}/{dirname}'] = {"dirs": [], "files": {}}
    update_data("fsimage", fsimage)
    return {"detail": f"Directory {dirname} created"}


def directory_open(dirname: str):
    data = get_data()
    client_cursor = data['client_cursor']
    if dirname != "..":
        client_cursor = f'{client_cursor}/{dirname}'
        update_data("client_cursor", client_cursor)
        return {"detail": f"Your current directory: {client_cursor}"}
    else:
        if client_cursor == '.':
            return {"detail": f"Your current directory: {client_cursor}"}
        else:
            client_cursor = '/'.join(client_cursor.split("/")[:-1])
            update_data("client_cursor", client_cursor)
            return {"detail": f"Your current directory: {client_cursor}"}


def directory_read(client_cursor: str = None):
    data = get_data()
    if client_cursor is None:
        client_cursor = data['client_cursor']
    fsimage = data['fsimage']
    result = {}
    result['dirs'] = fsimage[client_cursor]['dirs']
    result['files'] = list(fsimage[client_cursor]['files'].keys())
    return result


def directory_delete(dirname: str, flag: str):
    data = get_data()
    client_cursor = data['client_cursor']
    fsimage = data['fsimage']

    if flag == "y":
        fsimage[client_cursor]['dirs'].remove(dirname)
        fsimage.pop(f'{client_cursor}/{dirname}')
        update_data('fsimage', fsimage) 
    else:
        if directory_read(f'{client_cursor}/{dirname}')['dirs'] == [] and directory_read(f'{client_cursor}/{dirname}')['files'] == []:
            fsimage[client_cursor]['dirs'].remove(dirname)
            fsimage.pop(f'{client_cursor}/{dirname}')
            update_data('fsimage', fsimage) 
        else:
            return None

    return {"detail": f"Directory deleted: '{dirname}'"}

