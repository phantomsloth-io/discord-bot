import json
from math import floor, log10
from urllib import request
from datetime import date, timedelta
import http.client, xmltodict, os, time, re, urllib.parse

def encode_string(string):
    return urllib.parse.quote(string)

def nasa_neo(nasa_key):
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

def nasa_apod(nasa_key):
    webUrl = request.urlopen("https://api.nasa.gov/planetary/apod?&api_key=" + str(nasa_key))
    theJSON = json.loads(webUrl.read())
    return theJSON

def plex_search(search_query, library, plex_token):
    api_url = http.client.HTTPSConnection("plex.phantomsloth.io")
    api_url.request("GET", f"/hubs/search/?X-Plex-Token={plex_token}&query={encode_string(search_query)}")
    lib_data = api_url.getresponse().read()
    lib_data_dict = xmltodict.parse(lib_data)
    try:
        lib_item_1 = lib_data_dict['MediaContainer']['Hub'][library]['Video'][0]
    except:
        lib_item_1 = lib_data_dict['MediaContainer']['Hub'][library]['Video']
    poster = f"https://plex.phantomsloth.io{lib_item_1['@thumb']}?X-Plex-Token={plex_token}"
    title = f"{lib_item_1['@title']}"
    rating = f"{lib_item_1['@rating']}"
    tagline = f"{lib_item_1['@tagline']}"
    summary = f"{lib_item_1['@summary']}"
    content_rating = f"{lib_item_1['@contentRating']}"

    return title, poster, tagline, rating, summary, content_rating
