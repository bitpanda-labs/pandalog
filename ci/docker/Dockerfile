# base-image
FROM python:3.7-slim
# set labels
LABEL maintainer="Yuri Neves" \
      email="<yuri.neves@bitpanda.com>" \
      description="pandalog - bitpanda graylog python wrapper" \
      version="0.5.0"
# set current directory
WORKDIR /app
# copy root directory
COPY . /app
# upgrade PIP, install PIP requirements, clear APT lists
RUN apt update -y && apt install -y wget && \
    python3 -m pip install --upgrade pip && \
    python3 setup.py install && \
    rm -rf /var/lib/apt/lists/*
# initialize environment variables
ENV GRAYLOG_HOST ""
ENV GRAYLOG_TOKEN ""
ENV PYTHONWARNINGS="ignore:Unverified HTTPS request,ignore:Extraction path is writable"
ENV PYTHON_EGG_CACHE="/tmp"
# set unprivileged user
USER nobody:nogroup
