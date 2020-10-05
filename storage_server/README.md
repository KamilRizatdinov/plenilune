:information_source: This file can be deleted or reformated after the work is done

### How to launch storage server:
#### Prerequisites:
* docker engine (follow instructions from [here](https://docs.docker.com/get-docker/))
#### Instruction:
* This command creates an image for storage server:
```
docker build -t storage .
```
* This command runs 3 applications logically dividing port 8000 of the machine to 8001, 8002, 8003(really questionable)
```
docker run -p 8001:8000 storage
docker run -p 8002:8000 storage
docker run -p 8003:8000 storage
```

All the information you read here is found in this article: https://www.edureka.co/blog/apache-hadoop-hdfs-architecture/

**Here you can find the HDFS Data Node definition:**
DataNodes are the slave nodes in HDFS. Unlike NameNode, DataNode is a commodity hardware, that is, a non-expensive system which is not of high quality or high-availability. The DataNode is a block server that stores the data in the local file ext3 or ext4.

**Functions of Data Node:**
* Stores the data in their local FS
* Sends the updates of local FS to Name Node in order to update the DFS