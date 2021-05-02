docker build -t eg_postgresql -f pg/Dockerfile .
docker run -d \
-p 5432:5432 \
-e POSTGRES_PASSWORD='admin' \
-e POSTGRES_USER='admin' \
eg_postgresql 



docker run -d --name mongodb \
    -e MONGO_INITDB_ROOT_USERNAME='admin' \
    -e MONGO_INITDB_ROOT_PASSWORD='admin' \
    -p 27017:27017 \
    mongo

docker run -d --name mongodb \
    -e MONGO_INITDB_ROOT_USERNAME='admin' \
    -e MONGO_INITDB_ROOT_PASSWORD='admin' \
    -p 27017:27017 \
    mongo