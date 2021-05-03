#!/usr/bin/env python


"""
WORKER TO GET OBJECTS FROM BUCKET AND CATALOG ON POSTGRESS DB 
"""
import boto3
from botocore.config import Config
from multiprocessing.pool import ThreadPool
from multiprocessing import Process, Queue
import time
import sys
import os
import json
import random
import logging
import argparse
import warnings
from time import sleep

warnings.filterwarnings("ignore", category=UserWarning, module="psycopg2")
import psycopg2


# region = "sa-east-1"
# profile = ""
### aws-app-bucket-sync-1 , aws-app-bucket-sync-2, aws-app-bucket-sync-3
# buckets_list = ["dev-s3-sensu-assets"]

POSTGRESS_DB_HOST = os.environ.get("POSTGRESS_DB_HOST", "")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler
handler = logging.StreamHandler(sys.stdout)

handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# formatter = logging.Formatter(LOG_FORMATTER)
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)


def client(resource_type):
    config = Config(retries={"max_attempts": 10, "mode": "standard"},)
    session = boto3.Session()
    return session.client(resource_type, config=config)


def resource(resource_type):
    config = Config(retries={"max_attempts": 10, "mode": "standard"},)
    session = boto3.Session()
    return session.resource(resource_type, config=config)


def get_all_objects(bucket):
    conn = client("s3")
    logger.info("Getting all objects from bucket ")
    objects = conn.list_objects(Bucket=bucket)
    return objects


def pg_conn():
    try:
        conn = psycopg2.connect(
            host=POSTGRESS_DB_HOST,
            database="bucket_infos",
            user="docker",
            password="docker",
        )
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        logger.warning(str(error))


def insert_object_infos_to_pg(bucket, object_name, pg_conn):
    try:
        conn = pg_conn
        cur = conn.cursor()
        print("PostgreSQL connected Database")
        cur.execute(
            """insert into objects ( bucket_name, object_name, bucket_dest_synced, sync_status, sync_request )  
            values( '%s', '%s', '%s', '%s', '%s');
            """
            % (bucket, object_name, None, "Not sync", False)
        )
        conn.commit()
        count = cur.rowcount
        print(count, "Record inserted successfully into objects table")

    except Exception as error:
        print(error)
    finally:
        print("closing database connection")
        # closing database connection.
        if conn:
            cur.close()
            conn.close()
            print("PostgreSQL connection is closed")


def check_object_exist_db(bucket, object_name, pg_conn):
    try:
        conn = pg_conn
        cur = conn.cursor()
        cur.execute(
            "select id  from objects where bucket_name = '%s' and object_name = '%s';"
            % (bucket, object_name)
        )
        db_result = cur.fetchall()
        if len(db_result) > 0:
            return True
        else:
            return False
    except Exception as error:
        print(error)
    finally:
        print("closing database connection")
        # closing database connection.
        if conn:
            cur.close()
            conn.close()
            print("PostgreSQL connection is closed")


def get_object_request_sync_from_db():
    try:
        conn = pg_conn()
        cur = conn.cursor()
        cur.execute(
            "select object_name,bucket_name,bucket_dest_synced from objects where sync_request =  True and sync_status != 'synchronized';"
        )
        db_result = cur.fetchall()
        if len(db_result) > 0:
            return db_result

    except Exception as error:
        print(error)
    finally:
        print("closing database connection")
        # closing database connection.
        if conn:
            cur.close()
            conn.close()
            print("PostgreSQL connection is closed")


def copy_object(bucket_source, bucket_dest, object_name):
    conn = resource("s3")
    logger.info(
        "Start Copy object %s from Bucket source %s to Bucket Dest %s "
        % (object_name, bucket_source, bucket_dest)
    )
    copy_source = {"Bucket": bucket_source, "Key": object_name}
    bucket = conn.Bucket(bucket_dest)
    try:
        result = bucket.copy(copy_source, object_name)
        return True
    except Exception as e:
        logger.info("Not possible copy object %s" % str(e))
        return False


def update_object_sync_status(object_name, bucket_name):
    try:
        conn = pg_conn()
        cur = conn.cursor()
        cur.execute(
            "update objects set sync_status = 'synchronized' where bucket_name = '%s' and object_name = '%s' "
            % (bucket_name, object_name)
        )
        conn.commit()
        result = cur.rowcount
        print(result, "Record Updated successfully ")

    except Exception as error:
        print(error)
    finally:
        print("closing database connection")
        # closing database connection.
        if conn:
            cur.close()
            conn.close()
            print("PostgreSQL connection is closed")


"""
get object from buckets array and insert ou update infos from object on postgress db 
"""


def worker3():
    request_sync = get_object_request_sync_from_db()
    if request_sync is not None:
        for request in request_sync:
            object_name = request[0]
            bucket_source = request[1]
            bucket_dest = request[2]
            result = copy_object(bucket_source, bucket_dest, object_name)
            if result:
                update_object_sync_status(object_name, bucket_source)
            else:
                logger.info("Object not Sync")


def parseArguments():
    from argparse import RawTextHelpFormatter

    parser = argparse.ArgumentParser(description="Worker  3 ")
    parser = argparse.ArgumentParser(
        formatter_class=RawTextHelpFormatter,
        description="""

    {0}  \n

    """.format(
            __file__
        ),
    )

    # parser.add_argument("--buckets", help="bucket_list")
    return parser.parse_args(), parser


"""
TO RUN worker-3.py
"""
if __name__ == "__main__":
    args = parseArguments()[0]
    cli_help = parseArguments()[1]
    while True:
        try:
            worker3()
            sleep(5)
        except Exception as e:
            logger.warning(
                "Connections db or Aws is not possible , Please check connections !!!"
            )
