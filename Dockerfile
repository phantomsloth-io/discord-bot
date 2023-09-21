FROM python:3.10.7-alpine3.15

RUN apk update && apk upgrade
RUN pip3 install py-cord requests xmltodict python-slugify

WORKDIR /app
COPY . .

CMD python3 main.py
