import json
import random
import uuid

import redis


conn = redis.Redis('localhost')


def dump_data():
    set_data({
        "block_size": 1024,
        "replication": 2,
        "fsimage": {
            ".": {
                "dirs": [],
                "files": {}
            }
        },
        "storage_servers": [
            {
                "id": 1,
                "hostname": "localhost1",
                "status": "UP",
            },
            {
                "id": 2,
                "hostname": "localhost2",
                "status": "UP",
            },
            {
                "id": 3,
                "hostname": "localhost3",
                "status": "UP",
            },
        ],
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
    return (result, len(result))


def get_block_num(filesize):
    block_size = get_data()['block_size']
    if filesize % block_size == 0:
        return filesize // block_size
    return filesize // block_size + 1


def allocate_blocks(blocks_num: int):
    replicas = get_data()['replication']
    result = []
    for i in range(blocks_num):
        block_id = str(uuid.uuid1())
        hostnames, hostnames_num = get_active_storage_servers_hostnames()
        addresses = random.sample(hostnames, min(hostnames_num, replicas))
        result.append({"block_index": i, "block_name": block_id, "addresses": addresses})
    return result


def get_file_blocks(filename: str):
    data = get_data()
    client_cursor = data['client_cursor']
    fsimage = data['fsimage']
    
    if filename in fsimage[client_cursor]["files"].keys():
        return fsimage[client_cursor]["files"][filename]
    else:
        return None


def create_file_entry(filename: str, blocks_allocation: list):
    data = get_data()
    client_cursor = data['client_cursor']
    fsimage = data['fsimage']
    fsimage[client_cursor]["files"][filename] = blocks_allocation
    update_data("fsimage", fsimage)


def create_file(filename: str, filesize: int):
    blocks_num = get_block_num(filesize)
    blocks_allocation = allocate_blocks(blocks_num)
    create_file_entry(filename, blocks_allocation)
    return blocks_allocation


def read_file(filename: str):
    blocks = get_file_blocks(filename)
    result = []
    for block in blocks:
        block["address"] = block.pop("addresses")[0]
        result.append(block)
    return {"filename": filename, "blocks": result}


def delete_file(filename: str):
    data = get_data()
    client_cursor = data['client_cursor']
    fsimage = data['fsimage']
    file_allocation = fsimage[client_cursor]["files"].pop(filename)
    update_data("fsimage", fsimage)
    return {"filename": filename, "blocks": file_allocation}
