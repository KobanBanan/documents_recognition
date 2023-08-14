# Use an official Python runtime as a parent image
FROM python:3.8-buster

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    libzbar0 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*


WORKDIR usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install pillow python-poppler

COPY . .
