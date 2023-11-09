from math import floor, log10
from urllib import request
from datetime import date, timedelta
from ddtrace import tracer
import json, http.client, xmltodict, os, time, re, urllib.parse, logging, requests

import utilities

@tracer.wrap(service="discord-bot", resource="plex-library-search")
def plex_search(search_query, library, plex_token):
    span = tracer.current_span()
    # title, year, poster, tagline, rating, summary, content_rating = ''
    logging.info(f"Calling Plex server for media info from query: {search_query} in library: {library}")
    api_url = http.client.HTTPSConnection("plex.phantomsloth.io")
    api_url.request("GET", f"/hubs/search/?X-Plex-Token={plex_token}&query={utilities.encode_string(search_query)}")
    lib_data = api_url.getresponse().read()
    lib_data_dict = xmltodict.parse(lib_data)
    if library == 'tv':
        for i in lib_data_dict['MediaContainer']['Hub']:
            if i['@title'] == "Shows":
                library_index = i["Directory"]
                try:
                    lib_item_1 = library_index[0]
                except:
                    lib_item_1 = library_index

    elif library == "movies": 
        for i in lib_data_dict['MediaContainer']['Hub']:
            if i['@title'] == "Movies":
                library_index = i
                try:
                    lib_item_1 = library_index['Video'][0]
                except:
                    lib_item_1 = library_index['Video']
    span.set_tag('media.library', i['@title'])
    poster = f"https://plex.phantomsloth.io{lib_item_1['@thumb']}?X-Plex-Token={plex_token}"
    title = f"{lib_item_1['@title']}"
    year = f"{lib_item_1['@year']}"
    span.set_tag('media.title', title)
    if library == 'tv':
        rating = f"{lib_item_1['@audienceRating']}"
    elif library == "movies": 
        rating = f"{lib_item_1['@rating']}"

    try:
        tagline = f"{lib_item_1['@tagline']}"
    except:
        tagline = " "
        
    summary = f"{lib_item_1['@summary']}"
    try:
        content_rating = f"{lib_item_1['@contentRating']}"
    except:
        content_rating = "N/A"
    return title, year, poster, tagline, rating, summary, content_rating
