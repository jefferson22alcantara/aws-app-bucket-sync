FROM python:3.7-slim-buster
WORKDIR /app
ENV MONGO_DB_HOST=""
ENV POSTGRESS_DB_HOST=""
ENV AWS_SECRET_ACCESS_KEY=""
ENV AWS_ACCESS_KEY_ID=""
COPY . /app
RUN pip install -r /app/requirements.txt && \
    chmod 775 /app/worker-1.py
EXPOSE 80
ENTRYPOINT ["./worker-1.py"]



