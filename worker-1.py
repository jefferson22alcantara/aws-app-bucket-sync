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
buckets_list = ["dev-s3-sensu-assets"]

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


def get_all_objects(bucket):
    conn = client("s3")
    logger.info("Getting all objects from bucket ")
    objects = conn.list_objects(Bucket=bucket)
    return objects


def pg_conn():
    try:
        conn = psycopg2.connect(
            host="localhost", database="bucket_infos", user="docker", password="docker"
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


"""
get object from buckets array and insert ou update infos from object on postgress db 
"""


def worker1():
    for bucket in buckets_list:
        print(bucket)
        objects_list = get_all_objects(bucket).get("Contents")
        for obj in objects_list:
            object_name = obj.get("Key")
            if check_object_exist_db(bucket, object_name, pg_conn()) is not True:
                insert_object_infos_to_pg(bucket, object_name, pg_conn())
            else:
                logger.warning("Object Alread Exist on Postgress Db - nothing To do ")


"""
TO RUN worker-1.py --buckets bucket1,bucket2,bucket3 
"""
if __name__ == "__main__":
    while True:
        try:
            worker1()
            sleep(30)
        except Exception as e:
            logger.warning(
                "Connections db or Aws is not possible , Please check connections !!!"
            )
