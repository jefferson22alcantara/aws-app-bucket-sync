docker build -t eg_postgresql -f pg/Dockerfile .
docker run -d \
-p 5432:5432 \
-e POSTGRES_PASSWORD='admin' \
-e POSTGRES_USER='admin' \
eg_postgresql 



