#! /bin/bash

# create docker file for python application

# pull image
docker pull python:3.7.4-slim-buster

# create my image
cd ./python
docker build ./ -t python:aiohttp

# create container
docker run \
    --name python \
    --env EXTERNAL_ADDRESS=XXX.XXX.XXX.XXX \
    --env EXTERNAL_PORT=8443 \
    --env TOKEN=TOKEN_FROM_TELEGRAM_HERE \
    --publish 8443:8443 \
    --volume /telegram-bot/backend:/usr/src/app \
    --detach \
    python:aiohttp

