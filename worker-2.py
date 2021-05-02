#!/usr/bin/env python


"""
WORKER TO READ DATA FROM PG AND INSERT ON mongo 
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
from pymongo import MongoClient
from bson import ObjectId

warnings.filterwarnings("ignore", category=UserWarning, module="psycopg2")
import psycopg2

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

POSTGRESS_DB_HOST = os.environ.get("POSTGRESS_DB_HOST", "")
MONGO_DB_HOST = os.environ.get("MONGO_DB_HOST", "")


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


def mg_conn():
    try:
        client = MongoClient("mongodb://%s:%s@%s" % ("admin", "admin", MONGO_DB_HOST))
        return client
    except Exception as e:
        logger.warning(str(e))


def get_all_from_pg():
    conn = pg_conn()
    cur = conn.cursor()
    cur.execute("select * from objects")
    db_result = cur.fetchall()
    return db_result


def updage_mongo_infos_from_pg():
    mongo_conn = mg_conn()
    if check_db_exist(mongo_conn):
        print("Database Already exist")
        pg_infos = get_all_from_pg()
        for info in pg_infos:
            object_name = info[1]
            bucket_dest_synced = info[2]
            sync_status = info[3]
            sync_request = info[4]
            bucket_name = info[5]
            object_infos = {
                "bucket_name": bucket_name,
                "object_name": object_name,
                "sync_status": sync_status,
                "bucket_sync": bucket_dest_synced,
            }

            check_id = check_object_exist(object_infos)
            if check_id is None:
                insert_mongo_objects(object_infos)
            else:
                print("Object Alread Exist start update infos from %s " % check_id)
                result = update_mongo_objects(object_infos, check_id)
                if result is not None:
                    if result.raw_result.get("nModified") != 0:
                        print("Object Updated")
                        print(result.raw_result.get("nModified"))
                    else:
                        print("Object not updated")
    else:
        print("Db not exist Start create new db and collections")
        mongo_create_collection(mongo_conn)
        updage_mongo_infos_from_pg()


def check_object_exist(object_infos):
    mongo_conn = mg_conn()
    db = mongo_conn.get_database("objects")
    find_object = db.objects.find_one(
        {
            "bucket_name": object_infos.get("bucket_name"),
            "object_name": object_infos.get("object_name"),
        }
    )
    if find_object is not None:
        collection_id = find_object.get("_id")
        return collection_id
    else:
        print("object not found")


def update_mongo_objects(object_infos, obj_id):
    try:
        mongo_conn = mg_conn()
        db = mongo_conn.get_database("objects")
        collections = db.get_collection("objects")
        result = collections.update_one(
            {"_id": ObjectId(obj_id)}, {"$set": object_infos}
        )
        return result
    except Exception as e:
        print(str(e))


def insert_mongo_objects(object_infos):
    try:
        mongo_conn = mg_conn()
        db = mongo_conn.get_database("objects")
        collections = db.get_collection("objects")
        result = collections.insert_one(object_infos)
        print(
            "Created Object infos from Postgress on Collection objects %s"
            % object_infos
        )
    except Exception as e:
        print(str(e))


def mongo_create_collection(mg_conn):
    try:

        mongo_client = mg_conn
        db_names = mongo_client.list_database_names()
        if "objects" not in db_names:
            db = mongo_client.objects  # access "objects"
            col = db.create_collection("objects")
            if col is not None:
                print("Collection objects and Database Create Success ")
                return col
        else:
            print("collection objects already exists")
            db = mongo_client.get_database("objects")
            col = db.get_collection("objects")
            return col
    except Exception as e:
        print(str(e))


def check_db_exist(mg_conn):
    mongo_client = mg_conn
    db_names = mongo_client.list_database_names()
    if "objects" in db_names:
        return True
    else:
        return False


def check_collections_exist(mg_conn):
    mongo_client = mg_conn
    db = mongo_client.get_database("objects")
    collections_names = db.list_collection_names()
    if "objects" in collections_names:
        return True
    else:
        return False


def worker2():
    updage_mongo_infos_from_pg()


if __name__ == "__main__":
    while True:
        try:
            worker2()
            sleep(30)
        except Exception as e:
            logger.warning(
                "Connections db or Aws is not possible , Please check connections !!!"
            )
