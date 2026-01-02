# Interview test - Cake by VPBank

## [Requirements](./requirements.pdf)
```
Problem Statement
The task involves two SFTP destinations, referred to as <source> and <target>.
Your objective is to develop an Apache Airflow DAG that facilitates the transfer of files from the SFTP server at <source> to the SFTP server at <target> and ensures the preservation of the original directory structure.
The synchronization process should be unidirectional; hence, any modification made on <target> must not impact the <source>.
Deleted files on SFTP server at <source> must remain intact on <target> server.
Examples:

    On March 1st, 2024, when a file named sftp://<source>/a/b/c/file_1.txt is detected on the source server, it should be replicated to sftp://<target>/a/b/c/file_1.txt on the destination server.
    On March 2nd, 2024, a file named sftp://<source>/a/b/c/file_2.txt appears on the source server and subsequently should be transferred to sftp://<target>/a/b/c/file_2.txt on the destination server.
    On March 3rd, 2024, a file named sftp://<source>/a/b/c/file_3.txt appears on the source server and should then be transferred to sftp://<target>/a/b/c/file_3.txt on the destination server.

Expected Outcome
Candidates are expected to provide a GitHub public repository as following:

    Use separated commits that reflect your incremental development and refactoring. Pure atomic commits are not expected, and don’t squash them.
    A docker-compose.yml file for deploying latest Airflow version, with each service (Scheduler, Worker, Web Server) running in a separate container. Utilizing SQLite as the backend is permissible. The use of Celery executor is advised.
    A README.md file that includes:
        Detailed instructions for setting up and running the project.
        Any additional initial setup requirements.
        An explanation of assumptions made, decisions taken, and any trade-offs considered.
        One or more DAG file(s).
        Any additional plugins required for the project.

What We Don’t Expect
A comprehensive, production-ready ETL/ELT solution that is agnostic to data sources and destinations
What We Assess

    The functionality of a runnable Airflow DAG that accurately achieves the specified result.
    The candidate‘s adherence to a consistent and clean coding style.
    The level of abstraction in your API(s). Given that business requirements are subject to change, evaluate how adaptable your solution is if the data source transitions from SFTP to Object Storage.
    The extensibility of your API(s). Assess whether it is feasible to incorporate additional transformations before loading files into the target system without significant effort.
    Your strategy for handling anomalies. For instance, if file sizes increase dramatically from kilobytes to gigabytes, how does your solution accommodate this change in scale?
```

## How-to Guides

**NOTE:** For easy setup, some sensitive informations are included in the source code.

### 1. Setup and Run
This project contains Airflow services and SFTP services defined in [Docker Compose file](./docker-compose.yaml).

The [start.sh](./start.sh) script will help to prepare the environment and start all services.

To start the project, execute the `start.sh` script:
```bash
bash start.sh
```

After all docker containers sucessfuly started, you can access Airflow UI at [http://localhost:8080](http://localhost:8080) with `Username: airflow` and `Password: airflow`.

### 2. Test the `sftp2sftp` DAG
The `sftp2sftp` DAG is designed to run every 5 mins and transfers all the changed files within last 5 mins from SFTP source server to SFTP target server.

The files on source and target SFTP servers are mounted to the docker host at `sftp_src/upload` and `sftp_dest/upload` respectively.

After enable the DAG via Airflow UI, we can test it by updating files in `sftp_src/upload` folder and observe the changes in `sftp_dest/upload`.

### 3. Assumptions made and decisions taken
- On the first of the DAG, it will transfer all files on source server to target server.
- On the sub-sequence runs, it will only transfer files added or modified since last successful run upto the start interval of the current run.
- The `transfer` task perform file transfer directly from source to target SFTP server, eliminate the need of download file to local storage and upload it to target.
This approach greatly reduce the latency and cost of running this DAG.
- For the requirement of adapting the source server from SFTP to Object Storage, I would rather implement another DAG for the benefit of optimazation and simplicity.
- For the requirement of additional transformations before loading files into the target system, I need more details before implementing it:
    - what kind of data we are handling (CSV, Parquet, JSON, etc.)
    - how data need to be processed (aggregate, add new fields, normalize fields, etc.)
