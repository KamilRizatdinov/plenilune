# Plenilune

## Team members
* Kamil Rizatdinov
* Rufina Talalaeva
* Alina Paukova

## Contribution of each team member
* Kamil: Name Server implementation, deployment
* Rufina: Storage Server implementation, servers configuration on AWS, report
* Alina: Client implementation, report

## Project description
Plenilune is the distributed file system(DFS), a file system with data stored on a server. The data is accessed and processed as if it was stored on the local client machine. The DFS makes it convenient to share information and files among users on a network. 

## AWS deployment
As VPS for storage and name servers we have chosen [AWS](https://aws.amazon.com).  
For configuration we used [9 lab of DS Course in Innopolis University](https://docs.google.com/document/d/1hAmDzrEOwTIx_eWcwqXWy6OnYhCoulr7meR_6rua5Pw/edit) as a reference.

### Prerequisites
* 4 Ubuntu 18.04 Servers
* 10.0.15.10 - name server
* 10.0.15.11 - ss01
* 10.0.15.12 - ss02
* 10.0.15.13 - ss03

### VPC configuration
1. Created a VPC with the IPv4 CIDR block 10.0.0.0/16 & with the name tag DFS Network.
2. Created a subnet for the DFS Network. Chose any availability zone, assigned the IPv4 CIDR block 10.0.15.0/24 and the name tag DFS subnet.
3. For enablin Internet access for our instances, we created a default route pointing to the Internet gateway: 
    1. Created Internet NetworkGateway(VPC dashboard) with name tag DFS internet gateway.
    2. Attached by actions our VPC `DFS Network`
    3. In the route table for DFS Network(VPC dashboard) we edited the routes tab by adding the route where destination(0.0.0.0/0.), target(he identifier of the DFS internet gateway).
4. Created a new Security group for connecting to our servers using ssh:
    1. Clicked create security group
    2. Specified the security group name as dfs-security-group and the description as security group for DFS network.
    3. Selected our VPC `DFS Network`.
    4. Clicked create.
    5. Edited inbound rules for security group by adding:
        * rule(Type:SSH, Source:Anywhere).
        * rule(Type:All traffic, Source:Custom, network’s IP address: 10.0.15.0/24).

### Servers launch
1. In EC2 Dashboard, clicked to launch a new instance and selected an `Ubuntu Server 18.04 LTS` and instance type `t2.micro`.
2. On the Configure Instance page chose VPC `DFS Network`, enabled `Auto-assign Public IP` and assigned primary IP `<server-ip-from-prerequisites>` in Network interfaces tab.
3. On the Add Tags page added the key: Name, value: `<name-of-server-from-prerequisits>`.
4. On the Configure Security Group page, selected an existing security group `dfs-security-group`.
5. Launch the instance.
6. For all instances we have generated the same key pair.
7. Connected to our instances by ssh.

## Required installations
[Docker](https://www.docker.com), [Docker Compose](https://docs.docker.com/compose/install/) are required for installation of DFS.  
Installation base commands for each instance(for client on local machine also):  
```bash
sudo su # root privileges
apt-get update
snap install docker # installs docker & docker-compose
git clone https://github.com/KamilRizatdinov/plenilune.git # clones repository
```
Installation of Name Server ([docker image](https://hub.docker.com/r/rizatdinov/name_server)):
```bash
cd plenilune/name_server
docker pull rizatdinov/name_server
docker compose up --build -d
```
Installation of Storage Server ([docker image](https://hub.docker.com/r/rizatdinov/storage_server)):
```bash
cd plenilune/storage_server
docker pull rizatdinov/storage_server
docker-compose up --build -d 
```
Installation of Client ([docker image](https://hub.docker.com/r/rizatdinov/client)):
```bash
cd plenilune/client
docker pull rizatdinov/client
docker-compose up --build -d 
```

## Usage guide
To start run commands you need to enter client container bash:
```bash
docker exec -it <client-container-name> bash
python client.py <command>
```
Available commands can be found by ```--help``` command:
```bash
python client.py --help
```
![Client Console](https://raw.githubusercontent.com/KamilRizatdinov/plenilune/master/images/help.jpg)<br>


## Architectural diagrams
### DFS Structure
![DFS structure](https://raw.githubusercontent.com/KamilRizatdinov/plenilune/master/images/DFS_structure.png)<br>
Structure of our DFS is inspired by HDFS, we gained the knowledge from [this article](https://hadoop.apache.org/docs/r1.2.1/hdfs_design.html)<br>
Just like in HDFS structure, our name server has the **fsimage** and **storage servers** data records which make possible to name server to mimic the behaiviour of a centralized FS<br>
But our implementation has some differences with the one proposed by HDFS:
* Instead of pushing the HeartBeats from storage to name server we poll the storage servers by the name server
* We decided to make the "full" level of replication, which will simplify our work and make sure each server has the exact same blocks stored on it

On this figure, you can see that clients and the DFS system are separated.  
DFS nodes are in the isolated private subnet for security purposes.   
The naming server is the main node that is responsible for managing incoming requests, processing them, and giving all needed information to client. Also, it knows all about servers(state, info).  

### Name Server internal structure
![Name server structure](https://raw.githubusercontent.com/KamilRizatdinov/plenilune/master/images/NameServerInternal.png)<br>
As you can see on the picture above and as was said previously on the DFS structure section, name server is repponsible for the distribution transparency, because it is the only node who has the file system image. All the storage servers have no idea of what they are storing (data blocks with UUID instead of filenames). 
Name server needs to mimic the FS being centralized and we doing it using the next data on name server:
* Name server makes use of **fsimage** which structure was inspired by python [os library walk function](https://docs.python.org/3/library/os.html#os.walk) structure of output. 
* Name server also stores the information about all the storage servers of the DFS in **storage servers**.
* **Client cursor** is used to determine which directory of the FS is currently open.
* **Block size** is used to split the data into blocks/chuncks which will later delivered to the storage servers.

### Registration of storage servers to the DFS system
![Registration of storage servers to DFS system](https://raw.githubusercontent.com/KamilRizatdinov/plenilune/master/images/Init_of_DFS.png)<br>
On this figure, you can understand how storage servers are registered into the DFS system.
We suppose that all nodes(storage servers as well as clients) know the name server's public IP.

* When the storage server is started it immediately sends the request about registration to the DFS system to the naming server. It includes into the request its public IP in the global network, its private IP, and the information about blocks of files it has.
* After getting this information the naming server adds this server to the pool of storage servers of the DFS system.

### Client Interaction
![Client interaction](https://raw.githubusercontent.com/KamilRizatdinov/plenilune/master/images/Client_communication.png)<br>
When a client wants to do any command from the list described earlier, it:

1. Chooses the command for the specific operation
2. Contacts the naming server, then naming server can send 2 variant of response(3 or 4)
3. If the client wants to do any operation connected to the file: read, write, create, delete, etc, it sends the information about the storage server, where the client can get what he wants.
4. If the client wants to see the status of DFS, see/change directory structures, it applies all changes and responses to the client.
5. If the 3rd point was chosen, then the client contacts the storage server.
6. This storage server replicates the changes to other storage servers.

### Storage Server Interaction
![Storage server interaction](https://raw.githubusercontent.com/KamilRizatdinov/plenilune/master/images/storage_server1.jpg)<br>
Here you can see the main interactions of storage servers in the DFS system.  

It supports the following types of interactions:
1. Replication of file blocks to other servers
2. Accept requests from the naming server
3. Send info about itself to the naming server
4. Accept requests from clients
5. Response to those requests. 

### Name Server Interaction
![Name server interaction](https://raw.githubusercontent.com/KamilRizatdinov/plenilune/master/images/Nameserver_communication.png)<br>
On this figure, you can see the main interactions of the name server in the DFS system.  

It supports the following types of interactions:
1. Accepts the requests from clients
2. If the client wants to do any operation connected to the file: read, write, create, delete, etc, it sends the information about the storage server, where the client can get what he wants.
3. If the client wants to see the status of DFS, see/change directory structures, it applies all changes and responses to the client.
4. Sends the info about any changes in the file system to the Redis database.
5. Accepts responses from the Redis database, handles of smth went wrong.
6. Checks the state of each storage server by sending request. If some server does not respond, deletes it from the pool of available servers and updates the list of the available servers associated with each file block.
7. Accepts responses from the storage server.
8. In the case of a new storage server appear in the DFS system, says to that server to take info and blocks from other servers.

## Description of communication protocols
For communication we use ```requests``` library which simplifies HTTP requests  
All nodes use jsons for communication: ```{'arg[1]':'arg[1]_value', ..., 'arg[n]': 'arg[n]_value'}```   
which are inside reqests functions: ```requests.<command>(<url>, json)```  
For example, file copying:
```bash
requests.get(f'http://{name_server_address}/file/copy', {"filename": filename, "destination": destination})
```
Servers send response messages:  
![Client Console](https://raw.githubusercontent.com/KamilRizatdinov/plenilune/master/images/respons.jpg)<br>

## Difficulties we faced and solutions found
* **Define and assign tasks to each team member** - solved on the second day of group work, when we gained some knowledge about task and decided to conduct a zoom meeting
* **Find ways of interaction between Client, Name Server, and Storage Server** - read the HDFS [article](https://hadoop.apache.org/docs/r1.2.1/hdfs_design.html), whick explains communications between this three
* **Realisation of Fault Tolerance** - make "full replication" (each storage server has all the data blocks), which will assure data availability
* **Realisation of Replications** - make "full replication" (each storage server has all the data blocks), which makes the data replication problem easier
* **Realisation of Storage Server restoration** - introduction of storage server registration, which runs the procedure of getting the differences between current FS and stored on the registering storage server
