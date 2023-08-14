# Use an official Python runtime as a parent image
FROM python:3.8-buster

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    cmake \
    libfreetype6-dev \
    libfontconfig-dev \
    libjpeg-dev \
    libopenjp2-7-dev \
    libcairo2-dev \
    libtiff5-dev -y \
    software-properties-common \
    git \
    libzbar0 \
    poppler-utils \
    libpoppler-cpp-dev\
    pkg-config \
    python-dev \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://poppler.freedesktop.org/poppler-data-0.4.10.tar.gz \
    && tar -xf poppler-data-0.4.10.tar.gz \
    && cd poppler-data-0.4.10 \
    && make install \
    && cd .. \
    && wget https://poppler.freedesktop.org/poppler-21.03.0.tar.xz \
    && tar -xf poppler-21.03.0.tar.xz \
    && cd poppler-21.03.0 \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make \
    && make install \
    && cd ../.. \
    && ldconfig \
    && rm poppler-data-0.4.10.tar.gz \
    && rm -rf poppler-data-0.4.10 \
    && rm poppler-21.03.0.tar.xz \
    && rm -rf poppler-21.03.0
CMD tail -f /dev/null


WORKDIR usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install pillow python-poppler

COPY . .
