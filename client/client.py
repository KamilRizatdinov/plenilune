import requests
import fire

name_server_address = "127.0.0.1"  # we should change it
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
    url = data_server + "/read"
    print("Connecting to Data Server...")
    response = requests.get(url, params)
    if response.status_code == 200:
        print("Success!")
        data = response.json()
        print(data)
    else:
        print("Something went wrong:", response.status_code, response.reason)


def write(filename, c: bool = False):
    params = {"filename": filename}
    print("Write", filename, "command received!")
    data_server = get_data_server_address(params)
    url = data_server + "/write"
    print("Connecting to Data Server...")
    response = requests.post(url, params)
    if c:
        return response
    if response.status_code == 200:
        print("You have successfully uploaded the file!")
    else:
        print("Something went wrong:", response.status_code, response.reason)


def delete(filename):
    params = {"filename": filename}
    print("Delete", filename, "command received!")
    data_server = get_data_server_address(params)
    url = data_server + "/delete"
    print("Connecting to Data Server...")
    response = requests.delete(url, data=params)
    if response.status_code == 200:
        print("You have successfully delete the file!")
    else:
        print("Something went wrong:", response.status_code, response.reason)


def create(filename):
    print("Create", filename, "command received!")
    open("filename", "w+")
    response = write(filename, c=True)
    if response.status_code == 200:
        print("You have successfully create a new file!")
    else:
        print("Something went wrong:", response.status_code, response.reason)


if __name__ == "__main__":
    fire.Fire({
        "File read": read,
        "File write": write,
        "File delete": delete,
        "File create": create
    })
