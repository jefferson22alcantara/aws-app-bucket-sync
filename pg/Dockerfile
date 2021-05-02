# syntax=docker/dockerfile:1
FROM postgres


ADD init-user-db.sh /docker-entrypoint-initdb.d/init-user-db.sh 
# Expose the PostgreSQL port
EXPOSE 5432
