# Configuration for coldbot.py
import random
from random import randint


settings = {
    "token": "",
    "prefix": "!",
    "administrators": [], # This is pretty much useless.  
    "custom_status": "", # Leaving this empty will result in the default "Analyzing Stats of {x} Players"
    "refresh_time": 10, # this is in minutes
    "leaderboard_aliases": [ 
        "leaderboard",
        "top"
    ],
    "search_aliases": [
        "search",
        "find"
    ],
}


def randColor():
    color = (randint(0, 255), randint(0, 255), randint(0, 255))
    return color






