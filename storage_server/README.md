:information_source: This file can be deleted or reformated after the work is done

### How to launch storage server:
You can easily run the storage server using [this bash script](https://pastebin.com/LydXNbBS), otherwise follow commands below.
#### Prerequisites:
* docker engine (follow instructions from [here](https://docs.docker.com/get-docker/))
* docker compose (follow instructions from [here](https://docs.docker.com/compose/install/))
#### Instruction:
* Run nessesary containers in daemon mode with the following command:
```
docker-compose up --build -d 
```
* Go [here](http://52.14.131.8:8000/docs) in order to view a storage server's API documentation

All the information you read here is found in this article: https://www.edureka.co/blog/apache-hadoop-hdfs-architecture/

**Here you can find the HDFS Data Node definition:**
DataNodes are the slave nodes in HDFS. Unlike NameNode, DataNode is a commodity hardware, that is, a non-expensive system which is not of high quality or high-availability. The DataNode is a block server that stores the data in the local file ext3 or ext4.

**Functions of Data Node:**
* Stores the data in their local FS
* Sends the updates of local FS to Name Node in order to update the DFS