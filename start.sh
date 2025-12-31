#!/bin/sh
set -e

if [ ! -f ".env" ]; then
    # Create folders
    mkdir -p ./dags ./logs ./plugins ./config
    mkdir -p ./sftp_dest/upload ./sftp_src/upload

    # Create env file
    cp .example.env .env
    echo -e "AIRFLOW_UID=$(id -u)" > .env

    # Initialize the database
    docker compose up airflow-init
fi

docker compose up -d
