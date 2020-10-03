:info: This file can be deleted or reformated after the work is done

All the information you read here is found in this article: https://www.edureka.co/blog/apache-hadoop-hdfs-architecture/

**Here you can find the HDFS Name Node definition:**
NameNode is the master node in the Apache Hadoop HDFS Architecture that maintains and manages the blocks present on the DataNodes (slave nodes). NameNode is a very highly available server that manages the File System Namespace and controls access to files by clients. I will be discussing this High Availability feature of Apache Hadoop HDFS in my next blog. The HDFS architecture is built in such a way that the user data never resides on the NameNode. The data resides on DataNodes only.

**Functions of Name Node:**
* It stores file system image
* It stores file system change log
* It stores the status of each data node
* It manages the data replications if needed
* Recieves updates from the Data Nodes