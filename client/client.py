import requests
import fire

name_server_address = "127.0.0.1"  # we should change it
name_server_port = 80


def get_data_server_address(params):
    print("Connecting to Name Server...")
    response = requests.get(name_server_address, params)
    print("Name server connection:", response.status_code, response.reason)
    data_server = response.json()
    return data_server


def read(filename):
    params = {"filename": filename}
    print("Read", filename, "command received!")
    data_server = get_data_server_address(params)
    print("You got data server's address")
    url = data_server["address"] + "/read"
    # secondly, we connect to the data server and read the file
    print("Connecting to Data Server...")
    response = requests.get(url, params)
    print("Data server connection:", response.status_code, response.reason)
    data = response.json()
    print(data)


def write(filename):
    params = {"filename": filename}
    print("Write", filename, "command received!")
    # firstly, we should get data server's ip and port
    data_server = get_data_server_address(params)
    print("You got data server's address")
    url = data_server["address"] + "/write"
    # secondly, we connect to the data server and write the file
    print("Connecting to Data Server...")
    response = requests.post(url, params)
    print("Data server connection:", response.status_code, response.reason)


def delete(filename):
    params = {"filename": filename}
    print("Delete", filename, "command received!")
    # firstly, we should get data server's ip and port
    data_server = get_data_server_address(params)
    print("You got data server's address")
    url = data_server["address"] + "/delete"
    # secondly, we connect to the data server and write the file
    print("Connecting to Data Server...")
    response = requests.delete(url, data=params)
    print(response.status_code, response.reason)


def create(filename):
    print("Create", filename, "command received!")
    file = open("filename", "w+")
    write(filename)


if __name__ == "__main__":

    fire.Fire({
        "File read": read(),
        "File write": write(),
        "File delete": delete(),
        "File create": create()
    })
