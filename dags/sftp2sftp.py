"""
DAG to transfer files from the source SFTP server to the target SFTP server
ensures the preservation of the original directory structure.
The synchronization process is unidirectional.
"""

import stat

import paramiko
import pendulum
from airflow.models.connection import Connection
from airflow.models.dagrun import DagRun
from airflow.sdk import DAG, task
from airflow.sdk.execution_time.context import ConnectionAccessor

with DAG(
    dag_id="sftp2sftp",
    schedule="*/5 * * * *",
    start_date=pendulum.datetime(2025, 12, 31, tz="Asia/Ho_Chi_Minh"),
):

    @task()
    def list_changed_files(**kwargs) -> list[str]:
        """
        List files in the source SFTP server that has been modified/created
        within time range of current DAG Run.

        :param kwargs: Contains Airflow context variables
        :return: List of absolute file paths
        :rtype: list[str]
        """
        # Get time range for current run
        dagrun: DagRun = kwargs["dag_run"]
        start_dt: pendulum.DateTime = kwargs["data_interval_start"]
        prev_start_dt: pendulum.DateTime = kwargs["prev_data_interval_start_success"]
        start_ts = 0
        if prev_start_dt:
            start_ts = prev_start_dt.timestamp()
        end_ts = start_dt.timestamp()

        print(start_ts, end_ts)
        print(dagrun.data_interval_start)

        # Get SFTP connection
        conn_accessor: ConnectionAccessor = kwargs["conn"]
        conn_sftp_src: Connection = conn_accessor.get(conn_id="sftp-src")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(
            hostname=conn_sftp_src.host,
            username=conn_sftp_src.login,
            password=conn_sftp_src.password,
        )

        # Get changed files
        def _walk(path: str):
            try:
                for item in sftp_client.listdir_attr(path):
                    name = item.filename
                    full = f"{path}/{name}"
                    if stat.S_ISDIR(item.st_mode) and not stat.S_ISLNK(item.st_mode):
                        yield from _walk(full)
                    else:
                        yield full, item
            except IOError:
                pass

        changed_files: list[str] = []
        with client.open_sftp() as sftp_client:
            for full, item in _walk("upload"):
                if start_ts <= int(item.st_mtime) <= end_ts:
                    changed_files.append(full)

        return changed_files

    @task()
    def transfer(files: list[str], **kwargs):
        """
        Transfer files from source SFTP server to destination SFTP server

        :param files: List of absolute file paths
        :type files: list[str]
        """
        # Get SFTP connection
        conn_accessor: ConnectionAccessor = kwargs["conn"]
        conn_sftp_src: Connection = conn_accessor.get(conn_id="sftp-src")
        conn_sftp_dest: Connection = conn_accessor.get(conn_id="sftp-dest")
        client_src = paramiko.SSHClient()
        client_dest = paramiko.SSHClient()
        client_src.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client_dest.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client_src.connect(
            hostname=conn_sftp_src.host,
            username=conn_sftp_src.login,
            password=conn_sftp_src.password,
        )
        client_dest.connect(
            hostname=conn_sftp_dest.host,
            username=conn_sftp_dest.login,
            password=conn_sftp_dest.password,
        )

        # Transfer files from source to destination
        with client_src.open_sftp() as sftp_client_src:
            with client_dest.open_sftp() as sftp_client_dest:
                for file in files:
                    print(f"Transferring: {file} ...")
                    with sftp_client_dest.open(file, "w+") as writer:
                        sftp_client_src.getfo(file, writer)

    transfer(list_changed_files())
