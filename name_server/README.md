:information_source: This file can be deleted or reformated after the work is done

### How to launch naming server:
#### Prerequisites:
* docker engine (follow instructions from [here](https://docs.docker.com/get-docker/))
* docker compose (follow instructions from [here](https://docs.docker.com/compose/install/))
#### Instruction:
* Run nessesary containers in daemon mode with the following command:
```
docker-compose up --build -d 
```
* Go [here](http://127.0.0.1/docs) in order to view the naming server API documentation

### TODO:
* [x] **/init** Initialize the client storage on a new system, should remove any existing file in the dfs root directory and return available size.
* [x] **/file/create.** Should allow to create a new empty file.
* [x] **/file/read.** Should allow to read any file from DFS (download a file from the DFS to the Client side).
* [x] **/file/write.** Should allow to put any file to DFS (upload a file from the Client side to the DFS)
* [x] **/file/delete.** Should allow to delete any file from DFS
* [x] **/file/info.** Should provide information about the file (any useful information - size, node id, etc.)
* [x] **/file/copy.** Should allow to create a copy of file.
* [ ] **/file/move.** Should allow to move a file to the specified path.
* [x] **/dir/open.** Should allow to change directory
* [ ] **/dir/read.** Should return list of files, which are stored in the directory.
* [x] **/dir/create** Should allow to create a new directory.
* [ ] **/dir/delete.** Should allow to delete directory.  If the directory contains files the system should ask for confirmation from the user before deletion.
* [ ] **/storage/info** Should allow storage servers to send heartbeats
* [ ] **/storage/blocks** Should allow storage servers to send stored block information