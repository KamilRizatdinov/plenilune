:information_source: This file can be deleted or reformated after the work is done

First of all we need to understand what is the client? From this citation from the Project description we can say that the client is some sort of centralized software, we will make simle CLI (command line interface) for the client.

> Responsible for making the distributed nature of the system transparent to the user.

**Client CLI should be able to handle the next commands:**
* **Initialize.** Initialize the client storage on a new system, should remove any existing file in the dfs root directory and return available size.
* **File create.** Should allow to create a new empty file.
* **File read.** Should allow to read any file from DFS (download a file from the DFS to the Client side).
* **File write.** Should allow to put any file to DFS (upload a file from the Client side to the DFS)
* **File delete.** Should allow to delete any file from DFS
* **File info.** Should provide information about the file (any useful information - size, node id, etc.)
* **File copy.** Should allow to create a copy of file.
* **File move.** Should allow to move a file to the specified path.
* **Open directory.** Should allow to change directory
* **Read directory.** Should return list of files, which are stored in the directory.
* **Make directory.** Should allow to create a new directory.
* **Delete directory.** Should allow to delete directory.  If the directory contains files the system should ask for confirmation from the user before deletion.

**Requirements added by our team:**
* **Connect.** Before applying any of the commands above the client should be able to connect to the name server or pool of the name servers.

**What needs to be done:**
* Think about the commands and their usage.
* Think of the API calls needed in order to interact with Name Server.
* Think of the API calls needed in order to interact with Storage Server.
* Simple CLI which is able to handle all of the commands above.

**Useful links:**
* [**Fire**](https://towardsdatascience.com/a-simple-way-to-create-python-cli-app-1a4492c164b6) - library for creating python-based CLI