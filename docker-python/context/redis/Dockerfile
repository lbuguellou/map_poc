FROM redis:5.0.9

MAINTAINER Laetitia BUGUELLOU <laetitiabug@gmail.com>

WORKDIR /redis

COPY redis.conf /usr/local/etc/redis/redis.conf

COPY init.sh ./
RUN chmod +x init.sh

EXPOSE 6379