FROM python:3.10-alpine

MAINTAINER Laetitia BUGUELLOU <laetitiabug@gmail.com>

WORKDIR /var/www/map.streamlit

RUN apk add --no-cache gcc musl-dev linux-headers

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

EXPOSE 80

COPY . .

ENTRYPOINT ["streamlit", "run", "map.py", "--server.port=80", "--client.toolbarMode=minimal"]