# Coldbot.py is a discord bot implementation of the hiscores by github.com/coderezzo 
# This bot works by using the json dumped online by rezzo's website to grab the data.

# Import Everything From Discord
import discord

from discord.ext import commands
from discord.ext import tasks, commands
from discord.utils import get

from collections import OrderedDict 
from operator import getitem 

# General Imports 
import sys
import os
import asyncio
import random
import datetime
import json
import requests

from random import randint

# Importing the config
from coldconfig import settings
from coldconfig import randColor
# Loading the Config Values 
client = commands.Bot(command_prefix=settings['prefix'])
token = settings['token']

# ---
# EVENTS
# ---

@client.event
async def on_ready():
    global data
    print(f"{client.user} has connected to Discord! \nCurrent prefix is {settings['prefix']}")
    refresh_data.start()
    refresh_status.start()


    
@client.event
async def on_message(message): # This function is useless right now
    await client.process_commands(message) # This is so that it will still process commands


# ---
# COMMANDS
# ---

# THIS IS THE LEADERBOARD COMMAND
@client.command(aliases=settings["leaderboard_aliases"])
async def topten(ctx, mode='bank', limit=10):
    global data
    valid_mode_list = ['bank', 'income', 'playtime', 'experience', 'respect']
    if str(mode).lower() in valid_mode_list:
        if int(limit) < 26 and int(limit) > 0:
            print(f"{ctx.author}, requested top {limit} {mode}, ID: {ctx.author.id}")
            top = getTop(int(limit), str(mode).lower())

            top10string = ''
            counter = 0
            for player in top:
                counter += 1
                top10string = top10string + f"{counter}. {data[player]['name']}, {str(mode).lower()}: {data[player][str(mode).lower()]} \n"

            sortembed = discord.Embed(title=f"Top {str(limit)} {str(mode).lower()}", description=f"```{top10string}```", colour=discord.Color.from_rgb(randColor()[0],randColor()[1],randColor()[2]))
            await ctx.send(embed=sortembed)

        else:
            await ctx.send(f"{limit} Isn't a valid amount. It's either too big or too small.")
    else:
        await ctx.send(f"{mode} isn't a valid sorting mode!")

# THIS IS THE search COMMAND
@client.command(aliases=settings["search_aliases"]) 
async def findplayer(ctx, player):
    global data
    matches = search(str(player))
    counter = 0
    searchembed = discord.Embed(title=f"Search Results for '{str(player)}'", description=f"*{len(matches)} matches*", colour=discord.Color.from_rgb(randColor()[0],randColor()[1],randColor()[2]))
    print(f"{ctx.author} searched for {player}, ID: {ctx.author.id}")
    if len(matches) > 10:
        await ctx.send(f"There are too many matches to your search!")
    else:
        for match in matches:
            counter += 1
            searchembed.add_field(name=f"Match {counter}", 
            value= f"```{data[match]['name']}: \n" +
            f"SteamID64: {data[match]['steamid']} \n" +
            f"Bank: {data[match]['bank']} \n" +
            f"Income: {data[match]['income']} \n" +
            f"Playtime: {data[match]['playtime']} \n" +
            f"Experience: {data[match]['experience']} \n" +
            f"Respect: {data[match]['respect']}```")
        await ctx.send(embed=searchembed)


# ---
# FUNCTIONS
# ---

def getTop(limit=10, key='bank'): # Key must be ['bank', 'income', 'playtime', 'experience', 'respect']
    global data
    dick = OrderedDict(sorted(data.items(), 
       key = lambda x: getitem(x[1], key), reverse=True))
    top_limit_list = []
    for p in dick:
        if len(top_limit_list) < limit:
            top_limit_list.append(p)
        
    return top_limit_list

def search(string): # Simply Returns a list of IDs in the data dictionary related to the given string of player name or steamid
    global data 
    returnlist = []
    for player in data: 
        if str(string) in data[player]['steamid'] or str(string) in data[player]['name']:
            returnlist.append(player)

    return returnlist 

def do_data():  # THIS FUNCTION IS RESPONSIBLE FOR CONVERTING RETRIEVED DATA INTO SOMETHING USABLE
    data1 = getData() # THIS ALSO DOES EVERYTHING WE NEED.
    data = data1['Information']
    for p in data:
        if data[p]['name'] == "None ASCII Name - Deleted":
            data[p]['name'] = "<invalid_username>"
    return data

def getData():  # THIS FUNCTION IS RESPONSIBLE FOR RETRIEVING DATA
    url = "http://rezzo.dev/visualscores/print.php"
    response = requests.get(url) 
    s = response.text
    json_acceptable_string = s.replace("'", "\"")
    return json.loads(json_acceptable_string)


# --
# DATA
# --

# Declaring The Data
global data
data = {}

# --
# Loops
# --

@tasks.loop(minutes=settings["refresh_time"])
async def refresh_data():
    global data 
    data = do_data()
    print("[Data Refreshed]")

@tasks.loop(minutes=1)
async def refresh_status():
    global data
    if settings['custom_status'] == "":
        status = f"Analyzing Data of {len(data)} Players"
    else:
        status = settings['custom_status']
    await client.change_presence(status=discord.Status.online, activity=discord.Game(status), afk=False)

client.run(token)