import http.client
import fire

name_server_ip = "127.0.0.1"  # we should change it
name_server_port = 80


def read(url: str):
    # firstly, we should get data server's ip and port
    connection = http.client.HTTPConnection(name_server_ip, name_server_port)
    connection.request("GET", url)
    response = connection.getresponse()
    print("Name server connection:", response.status, response.reason)
    data_server = response.read()
    data_server = data_server.split()
    data_server_ip = data_server[0]
    data_server_port = data_server[1]
    connection.close()

    # secondly, we connect to the data server and read the file
    connection2 = http.client.HTTPConnection(data_server_ip, data_server_port)  # i am not sure that it is right
    connection.request("GET", url)
    response = connection2.getresponse()
    print(response.status, response.reason)
    data = response.read()
    print(data)
    connection2.close()


if __name__ == "__main__":

    fire.Fire({
        "File read": read()
    })
