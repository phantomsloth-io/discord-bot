FROM python:3.10.13

RUN apt update && apt upgrade
RUN pip3 install py-cord requests xmltodict python-slugify ddtrace

WORKDIR /app
COPY . .

CMD python3 main.py
