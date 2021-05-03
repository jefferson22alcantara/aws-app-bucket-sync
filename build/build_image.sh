#!/bin/bash
# docker build -t ifood-docker-tf .

DOCKER_PASSWORD=$MY_DOCKER_PASSWORD
DOCKER_USERNAME=$MY_DOCKER_USERNAME
function build_image_web(){
    docker build -t web-app -f ../web-app/app/Dockerfile ../web-app/app
    echo "$DOCKER_PASSWORD" | docker login --username "$DOCKER_USERNAME" --password-stdin
    docker tag web jefferson22alcantara/challenge-job:web
    docker push jefferson22alcantara/challenge-job:web
}

function build_image_worker1(){
    docker build -t worker1 -f ../worker1/Dockerfile ../worker1/
    echo "$DOCKER_PASSWORD" | docker login --username "$DOCKER_USERNAME" --password-stdin
    docker tag worker1 jefferson22alcantara/challenge-job:worker1
    docker push jefferson22alcantara/challenge-job:worker1
}


function build_image_worker2(){
    docker build -t worker2 -f ../worker1/Dockerfile ../worker2/
    echo "$DOCKER_PASSWORD" | docker login --username "$DOCKER_USERNAME" --password-stdin
    docker tag worker2 jefferson22alcantara/challenge-job:worker2
    docker push jefferson22alcantara/challenge-job:worker2
}


function build_image_worker3(){
    docker build -t worker3 -f ../worker1/Dockerfile ../worker3/
    echo "$DOCKER_PASSWORD" | docker login --username "$DOCKER_USERNAME" --password-stdin
    docker tag worker3 jefferson22alcantara/challenge-job:worker3
    docker push jefferson22alcantara/challenge-job:worker3
}

function build_image_pg(){
    docker build -t pg -f  pg/Dockerfile .
    echo "$DOCKER_PASSWORD" | docker login --username "$DOCKER_USERNAME" --password-stdin
    docker tag pg jefferson22alcantara/challenge-job:pg
    docker push jefferson22alcantara/challenge-job:pg
}

