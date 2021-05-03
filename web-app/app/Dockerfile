FROM python:3.7-slim-buster
WORKDIR /app
ENV MONGO_DB_HOST=localhost
ENV POSTGRESS_DB_HOST=localhost
COPY . /app
RUN pip install -r /app/requirements.txt && \
    chmod 775 /app/gunicorn.sh
EXPOSE 80
ENTRYPOINT ["./gunicorn.sh"]



