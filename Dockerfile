FROM ubuntu:latest as rle-development
COPY dpkg-requirements.txt .
COPY requirements.txt .

RUN apt-get update \
    && apt-get install -y --force-yes software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get install -y --force-yes \
        $(cat dpkg-requirements.txt | tr '\n' ' ') \
    && apt-get clean \
    && python3.9 -m pip install -r requirements.txt \
    && mkdir /workarea \
    && rm -rf dpkg-requirements.txt \
    && rm -rf requirements.txt

WORKDIR /workarea
VOLUME ["/workarea"]