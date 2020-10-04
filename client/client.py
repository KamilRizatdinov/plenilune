import requests
import fire

name_server_ip = "127.0.0.1"  # we should change it
name_server_port = 80


def get_data_server_address(url: str):
    print("Connecting to Name Server...")
    response = requests.get(url)
    print("Name server connection:", response.status_code, response.reason)
    data_server = response.json()
    return data_server


def read(url: str):
    print("Read", url, "command received!")
    data_server = get_data_server_address(url)
    print("You got data server's address")
    # secondly, we connect to the data server and read the file
    print("Connecting to Data Server...")
    response = requests.get(url)
    print("Data server connection:", response.status_code, response.reason)
    data = response.json()
    print(data)


def write(url: str):
    print("Write", url, "command received!")
    # firstly, we should get data server's ip and port
    data_server = get_data_server_address(url)
    print("You got data server's address")
    # secondly, we connect to the data server and read the file
    print("Connecting to Data Server...")
    response = requests.post(url)
    print("Data server connection:", response.status_code, response.reason)


if __name__ == "__main__":

    fire.Fire({
        "File read": read()
    })
