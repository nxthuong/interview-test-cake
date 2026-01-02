#!/bin/sh
set -e

if [ ! -f ".env" ]; then
    # Create env file
    cp .example.env .env
    echo -e "AIRFLOW_UID=$(id -u)" >> .env

    # Cleanup previous run if any
    docker compose down

    # Remove old postgres-db-volume
    if docker volume rm interview-test-cake_postgres-db-volume; then
        echo "Old volume removed."
    fi

    # Create folders
    mkdir -p ./dags ./logs ./plugins ./config
    mkdir -p ./sftp_dest/upload ./sftp_src/upload

    # Initialize the database
    docker compose up airflow-init
fi

docker compose up -d
