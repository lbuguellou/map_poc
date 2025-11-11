FROM python:3.10-alpine

MAINTAINER Laetitia BUGUELLOU <laetitiabug@gmail.com>

WORKDIR /var/www/map.fastapi

RUN apk add --no-cache gcc musl-dev linux-headers

COPY requirements.txt requirements.txt

RUN pip install "fastapi[standard]"
RUN pip install -r requirements.txt

EXPOSE 81

COPY . .

ENTRYPOINT ["fastapi", "run", "main.py", "--port=81"]