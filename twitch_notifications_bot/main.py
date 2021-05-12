# Monday April 26th 2021
#
#

import sys
import os
import asyncio
import random
import datetime
import json
import time
import configparser

from random import randint
from pathlib import Path
from twitch_requests import get_stream_data, check_user

# Discord Related Imports
import discord

from discord.ext import commands
from discord.ext import tasks, commands
from discord.utils import get

# Importing Variables From Data 
from data import token, prefix, refresh_rate, twitch_channels, announcement_channels

# --
# 1. > Variables
# --


# Setting Prefix
client = commands.Bot(command_prefix=prefix)

# setting global var for streamer list
global streamers

# --
# 2. Functions
# --

def make_stream_dict(users):
    userdict = {}
    for user in users:
        userdict[str(user)] = False
    return userdict

def update_stream_dict(users):
    userdict = {}
    for user in users:
        userdict[str(user)] = check_user(user)
    return userdict 

# --
# > 3. Discord Functions 
# --

@client.event
async def on_ready(): # When the bot connects to discord it prints the following message.
    print(f"{client.user} has connected to discord.")
    post_live.start()

@tasks.loop(minutes = refresh_rate)
async def post_live(): # I still need to do basic functions
    global streamers
    global twitch_channels
    global announcement_channels
    old_dict = streamers
    new_dict = update_stream_dict(list(twitch_channels))
    
    for user in twitch_channels:
        if (old_dict[str(user)] == False) and (new_dict[str(user)] == True):
            for channel in announcement_channels:
                channel = client.get_channel(int(channel))
                data = get_stream_data(user)
                titlemessage = f"{data['stream']['channel']['status']}"
                descriptionmsg = f"{data['stream']['channel']['display_name']} is live with, {data['stream']['game']}!" + f"\nViewers: {data['stream']['viewers']}"
                url = f"{data['stream']['channel']['url']}"
                livebed = discord.Embed(title=titlemessage, description=descriptionmsg, url=url)
                livebed.set_thumbnail(url=f"{data['stream']['preview']['medium']}")
                #livebed.set_footer(text=f"Viewers: {data['stream']['viewers']}")    #<- I plan to reimplement the footer maybe who knows, but for now the viewers was put in the desc to make it look nicer

                await channel.send(embed=livebed)

        elif (old_dict[str(user)] == True) and (new_dict[str(user)] == False):
            print(f"Channel {user} went offline.")
        else:
            print(f"no change for {user}")
    
    streamers = new_dict
    print("Done checking!")


streamers = make_stream_dict(twitch_channels)
client.run(token)