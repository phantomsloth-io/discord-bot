from math import floor, log10
from urllib import request
from datetime import date, timedelta
from ddtrace import tracer
import json, http.client, xmltodict, os, time, re, urllib.parse, logging, requests

import utilities

@tracer.wrap(service="discord-bot", resource="nasa-neo-function")
def nasa_neo(nasa_key):
    logging.info("calling NASA API for Near Earth Objects")
    today = date.today()
    yesterday = today - timedelta(days = 1)
    superscript = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")

    webUrl = request.urlopen("https://api.nasa.gov/neo/rest/v1/feed?start_date=" + str(yesterday)
                            + "&end_date=" + str(today) + "&api_key=" + str(nasa_key))
    theJSON = json.loads(webUrl.read())
    data = []
    for i in theJSON['near_earth_objects'][str(today)]:
        distance = int(float(i['close_approach_data'][0]['miss_distance']['kilometers']))
        name = i['name']
        size = round(i['estimated_diameter']['meters']['estimated_diameter_max'], 3)
        power = floor(log10(distance))
        distance = (round(float(distance/(10**power)), 1))
        data.append("🌎" + ("-"  * int(distance*10)) + "☄️" + "(each - equals 1" + ("0"* (power - 1)) + "km)\n ↳Today, an asteroid named " + name + ", with a diamater of " + str(size) + " meters, passed " + str(distance) + "x10" + str(power).translate(superscript) + " kilometers from Earth." )
    return data

@tracer.wrap(service="discord-bot", resource="nasa-apod-function")
def nasa_apod(nasa_key):
    logging.info("calling NASA API for Astronomy Picture of the Day")
    webUrl = request.urlopen("https://api.nasa.gov/planetary/apod?&api_key=" + str(nasa_key))
    theJSON = json.loads(webUrl.read())
    return theJSON