FROM python:3.9.1-slim-buster

RUN mkdir -p /app

COPY . /app
WORKDIR /app

RUN pip3 install -r ./requirements.txt
