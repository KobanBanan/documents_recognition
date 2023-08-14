# Use an official Python runtime as a parent image
FROM python:3.8-buster

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    wget \
    software-properties-common \
    git \
    libzbar0 \
    poppler-utils \
    pkg-config\
    python-dev\
    cmake \
    libfreetype6-dev \
    libfontconfig-dev \
    libjpeg-dev \
    libopenjp2-7-dev \
    libboost-system-dev \
    libboost-thread-dev \
    libboost-program-options-dev \
    libboost-test-dev \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://poppler.freedesktop.org/poppler-data-0.4.12.tar.gz \
    && tar -xf poppler-data-0.4.12.tar.gz \
    && cd poppler-data-0.4.12 \
    && make install \
    && cd .. \
    && wget https://poppler.freedesktop.org/poppler-22.08.0.tar.xz \
    && tar -xf poppler-22.08.0.tar.xz \
    && cd poppler-22.08.0 \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make \
    && make install \
    && ldconfig
CMD tail -f /dev/null


WORKDIR usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
