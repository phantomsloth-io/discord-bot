from math import floor, log10
from urllib import request
from datetime import date, timedelta
from ddtrace import tracer
import json, http.client, xmltodict, os, time, re, urllib.parse, logging, requests

@tracer.wrap(service="discord-bot", resource="string-encoder")
def encode_string(string):
    return urllib.parse.quote(string)

@tracer.wrap(service="discord-bot", resource="save-image")
def save_image(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)
    logging.info(f"Image saved as {filename}")

@tracer.wrap(service="discord-bot", resource="delete-image")
def delete_saved_image(filename):
    logging.info("Scrubbing files")
    os.remove(filename)
    logging.info("Tmp files successfully scrubbed")