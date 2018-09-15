FROM ubuntu:18.04

RUN apt-get update && apt-get install -y python3-pip
RUN pip3 install \
  psycopg2-binary \
  numpy \
  dash==0.26.4 \
  dash-core-components==0.29.0 \
  dash-html-components==0.12.0
