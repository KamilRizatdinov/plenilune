# Plenilune team

### Team members:
* Kamil Rizatdinov
* Rufina Talalaeva
* Alina Paukova

## Project description
Plenilune is the distributed file system(DFS), a file system with data stored on a server. The data is accessed and processed as if it was stored on the local client machine. The DFS makes it convenient to share information and files among users on a network. 

## Required instalations
[Docker](https://www.docker.com), [Docker hub](https://hub.docker.com/):
```bash
sudo apt-get update
sudo snap install docker
```
Installation of [Name Server](https://hub.docker.com/r/rizatdinov/name_server):
```bash
docker pull rizatdinov/name_server
docker compose up --build -d
```
Installation of [Storage Server](https://hub.docker.com/r/rizatdinov/storage_server)
```bash
docker pull rizatdinov/storage_server
docker-compose up --build -d 
```
Installation of [Client](https://hub.docker.com/r/rizatdinov/client)
```bash
docker pull rizatdinov/storage_server
docker exec -it <container_name> bash
python client.py <comand>
```

## Usage guide
Available commands can be find by ```--help``` command:
![Client Console](images/help.jpg)


## Description of communication protocols
For communication we use ```requests``` library
All nodes use such are messages for communicating:
```bash

```
