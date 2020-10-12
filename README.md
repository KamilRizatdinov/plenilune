# Plenilune

## Project description
Plenilune is the distributed file system(DFS), a file system with data stored on a server. The data is accessed and processed as if it was stored on the local client machine. The DFS makes it convenient to share information and files among users on a network. 

## Required installations
[Docker](https://www.docker.com), [Docker hub](https://hub.docker.com/):
```bash
sudo apt-get update
sudo snap install docker
```
Installation of Name Server ([docker image](https://hub.docker.com/r/rizatdinov/name_server))
```bash
docker pull rizatdinov/name_server
docker compose up --build -d
```
Installation of Storage Server ([docker image](https://hub.docker.com/r/rizatdinov/storage_server))
```bash
docker pull rizatdinov/storage_server
docker-compose up --build -d 
```
Installation of Client ([docker image](https://hub.docker.com/r/rizatdinov/client))
```bash
docker pull rizatdinov/client
docker-compose up --build -d 
```

## Usage guide
To start run commands you need to enter client container bash:
```bash
docker exec -it <client-container-name> bash
python client.py <command>
```
Available commands can be find by ```--help``` command:
```bash
python client.py --help
```
![Client Console](images/help.jpg)


## DFS Structure
![DFS structure](images/DFS_structure.png)
On this figure you can see that clients and DFS system are separated.  
DFS nodes are in isolated private subnet for security purpose.   
Naming server is a main node that is responsible for managing incoming requests, processing them and giving all needed information to client. Also it knows all about servers(state, info).  

## Registration of storage servers to DFS system
![Registration of storage servers to DFS system](images/Init_of_DFS.png)
On this figure you can understand how storage servers are registered into DFS system.
We suppose that all nodes(storage servers as well as clients) know the name server's public IP.

* When the storage server is started it immediately sends the request about registration to DFS system to the naming server. It includes into the request its public IP in global network, its private IP and the information about blocks of files it has.
* After getting this information the naming server adds this server to the pool of storage servers of DFS system.

## Client Interaction
![Client interaction](images/Client_communication.png)
When a client wants to do any command from the list described earlier, it:

1. Chooses the command for specific operation
2. Contacts the naming server, then naming server can send 2 variant of response(3 or 4)
3. If client wants to do any operation connected to the file: read, write, create, delete, etc, it sends the information about storage server, where client can get what he wants.
4. If client wants to see the status of DFS, see/change directory structures, it applies all changes and responses to the client.
5. If 3rd point was chosen, then client contact the storage server.
6. This storage server replicates the changes to other storage servers.

## Storage Server Interaction
![Storage server interaction](images/storage_server.jpg)
Here you can see main interactions of storage servers in the DFS system.  

It supports following types of interactions:
1. Replication of file blocks to other servers
2. Accept requests from the naming server
3. Send an info about itself to the naming server
4. Accept requests from clients
5. Response to that requests. 

## Name Server Interaction
![Name server interaction](images/Nameserver_communication.png)

## Description of communication protocols
For communication we use ```requests``` library which simplifies HTTP requests  
All nodes use jsons for communication: ```{'arg[1]':'arg[1]_value', ..., 'arg[n]': 'arg[n]_value'}```   
which are inside reqests functions: ```requests.<command>(<url>, json)```  
For example, file copying:
```bash
requests.get(f'http://{name_server_address}/file/copy', {"filename": filename, "destination": destination})
```
Servers send response messages:  
![Client Console](images/respons.jpg)

### Team members:
* Kamil Rizatdinov
* Rufina Talalaeva
* Alina Paukova
