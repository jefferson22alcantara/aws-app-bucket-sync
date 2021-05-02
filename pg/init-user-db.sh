#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER docker WITH PASSWORD 'docker';
    CREATE DATABASE bucket_infos;
    GRANT ALL PRIVILEGES ON DATABASE bucket_infos TO docker;
EOSQL

psql -v ON_ERROR_STOP=1 --username "docker" --dbname "bucket_infos" <<-EOSQL
    CREATE TABLE objects (
    id SERIAL,
    object_name VARCHAR ( 250 ),
    bucket_dest_synced VARCHAR ( 250 ),
    sync_status  VARCHAR ( 250 ),
    sync_request boolean DEFAULT 'f',
    bucket_name VARCHAR ( 250 ),
    PRIMARY KEY (object_name, bucket_name)
    );
EOSQL

# select * from buckets;
# select * from objects;
# DROP TABLE IF EXISTS buckets;
# DROP TABLE IF EXISTS objects;

# CREATE TABLE buckets (
#     id SERIAL,
#     bucket_name VARCHAR ( 50 ) PRIMARY KEY
#     );

# CREATE TABLE objects (
#    id SERIAL,
#    CONSTRAINT fk_bucket_name
#       FOREIGN KEY(bucket_name)
# 	  REFERENCES buckets(bucket_name),
#     obj_name VARCHAR ( 250 )  PRIMARY KEY,
#     bucket_dest_synced VARCHAR ( 250 ),
#     sync_status  VARCHAR ( 250 ),
#     sync_request boolean DEFAULT 'f'
#     );

###insert into buckets ( bucket, obj, bucket_synced, sync_status, sync_request )  values( 'teste', 'teste', 'teste', 'teste', 't');


