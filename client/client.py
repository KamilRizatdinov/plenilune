import http.client
import fire

name_server_ip = "127.0.0.1"  # we should change it
name_server_port = 80


def get_data_server_address(url: str):
    print("Connecting to Name Server...")
    connection = http.client.HTTPConnection(name_server_ip, name_server_port)
    connection.request("GET", url)
    response = connection.getresponse()
    print("Name server connection:", response.status, response.reason)
    data_server = response.read()
    connection.close()
    return data_server


def read(url: str):
    print("Read", url, "command received!")
    data_server = get_data_server_address(url)
    print("You got data server's address")
    # secondly, we connect to the data server and read the file
    print("Connecting to Data Server...")
    connection2 = http.client.HTTPConnection(data_server)  # i am not sure that it is right
    connection2.request("GET", url)
    response = connection2.getresponse()
    print("Data server connection:", response.status, response.reason)
    data = response.read()
    print(data)
    connection2.close()


def write(url: str):
    print("Write", url, "command received!")
    # firstly, we should get data server's ip and port
    data_server = get_data_server_address(url)
    print("You got data server's address")
    # secondly, we connect to the data server and read the file
    print("Connecting to Data Server...")
    connection2 = http.client.HTTPConnection(data_server)  # i am not sure that it is right
    connection2.request("POST", url)
    response = connection2.getresponse()
    print("Data server connection:", response.status, response.reason)
    connection2.close()


if __name__ == "__main__":

    fire.Fire({
        "File read": read()
    })
