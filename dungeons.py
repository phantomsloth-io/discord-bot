from math import floor, log10
from urllib import request
from datetime import date, timedelta
from ddtrace import tracer
import json, http.client, xmltodict, os, time, re, urllib.parse, logging, requests, random

import utilities

@tracer.wrap(service="discord-bot", resource="roll-dice")
def roll_dice(dice_count, sides, bonus):
    result = ""
    total = bonus
    sides = int(str(sides).replace("D",""))
    if dice_count > 1:
        for i in range(1, dice_count + 1):
            critical_success = False
            critical_failure = False
            current_roll = random.randint(1, sides)
            if current_roll == 20:
                critical_success = True
            elif current_roll == 1:
                critical_failure = True

            if i == 1:
                result = str(current_roll) + (' Crit!' if critical_success else '') + (' Crit Fail!' if critical_failure else '')
                total = total + current_roll
            else:
                result = result + ", " + str(current_roll) + (' Crit!' if critical_success else '') + (' Crit Fail!' if critical_failure else '')

                total = total + current_roll
    else:
        result = random.randint(1, sides)
        total = result
    result = f"Rolled {dice_count} D{str(sides) + ('s' if int(dice_count) > 1 else '')}: Results: {result}{', plus ' + str(bonus) if bonus != 0 else ''}, Total: {total}"
    return result

@tracer.wrap(service="discord-bot", resource="roll-dice")
def saving_throw(bonus, advantage):
    roll1 = 0
    roll2 = 0
    if advantage == "None":
        roll1 = random.randint(1, 20)
        result = bonus + roll1
        final_roll = f"Rolled saving throw... Result: {result}. Your roll was a {str(roll1) + (' Crit!' if roll1 == 20 else '') + (' Crit Fail!' if roll1 == 1 else '')}, and your bonus was {bonus}"
        return final_roll
    else:
        roll1 = random.randint(1, 20)
        roll2 = random.randint(1, 20)
        
        rolls = [roll1, roll2]
        sorted_roll = sorted(rolls)
        print(sorted_roll[0], sorted_roll[1])
        if advantage == 'Advantage':
            picked_die = sorted_roll[1]
            result = sorted_roll[1] + bonus
        elif advantage == 'Disadvantage':
            picked_die = sorted_roll[0]
            result = sorted_roll[0] + bonus
        else:
            pass
        final_roll = f"Rolled saving throw with {advantage}... Result: {result}. Your {advantage} die was {str(picked_die) + (' Crit!' if picked_die == 20 else '') + (' Crit Fail!' if picked_die == 1 else '')}. Your roll was a {roll1} and a {roll2}, and your bonus was {bonus}"
        return final_roll
   

@tracer.wrap(service="discord-bot", resource="DnD-lookup")
def dnd_lookup(topic, query):
    conn = http.client.HTTPSConnection("https://www.dnd5eapi.co/api/")
    payload = ''
    headers = {}
    conn.request("GET", f"{topic}/{query}", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))


    
            