import requests
import fire

name_server_ip = "127.0.0.1"  # we should change it
name_server_port = 80


def get_data_server_address(params):
    print("Connecting to Name Server...")
    response = requests.get(name_server_ip, params)
    print("Name server connection:", response.status_code, response.reason)
    data_server = response.json()
    return data_server


def read(params):
    print("Read", params["filename"], "command received!")
    data_server = get_data_server_address(params)
    print("You got data server's address")
    # secondly, we connect to the data server and read the file
    print("Connecting to Data Server...")
    response = requests.get(data_server["address"], params)
    print("Data server connection:", response.status_code, response.reason)
    data = response.json()
    print(data)


def write(params):
    print("Write", params["filename"], "command received!")
    # firstly, we should get data server's ip and port
    data_server = get_data_server_address(params)
    print("You got data server's address")
    # secondly, we connect to the data server and write the file
    print("Connecting to Data Server...")
    response = requests.post(data_server["address"], params)
    print("Data server connection:", response.status_code, response.reason)


if __name__ == "__main__":

    fire.Fire({
        "File read": read(),
        "File write": write()
    })
