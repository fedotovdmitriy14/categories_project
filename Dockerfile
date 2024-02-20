FROM python:3.9.1-slim-buster AS builder

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
