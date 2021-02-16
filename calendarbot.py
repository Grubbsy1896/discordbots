# Program: Calendar Bot
# Desc: Calendar Discord Bot for fun
# This is the first time in a year I've used this format lol
# Author: Grubbsy
# Date: 2/15/2021
# ----------------------------

#||Imports||

import os

import discord

from discord.ext import commands

from discord.ext import tasks, commands
from discord.utils import get
from discord.ext.commands import has_permissions, MissingPermissions
#Importing the discord lib for the bot

import asyncio
import random
from random import randint
import json

from config import settings
from config import holidays

import datetime

# ----Connecting To Discord And Setup----
client = commands.Bot(command_prefix=settings['Prefix'])
token = settings['Token']


@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord! \nCurrent prefix is {settings['Prefix']}")
    refresh_holiday.start()

'''Command for seeing the holidays'''
@client.command()
async def holiday(ctx, month=datetime.datetime.now().strftime("%B"), day=datetime.datetime.now().strftime("%d")):
    if str(month).isnumeric():
        await ctx.send("I plan to fix it so you can use numbers for the month.")
    elif str(day).isnumeric() != True:
        await ctx.send("Please Enter a Number for the day!")

    try:
        holiday = holidays[str(month)][str(day)]
    except:
        errorembed = discord.Embed(
            title="Error", 
            description=f"We ran into an error, you probably entered it in wrong or mispelled. \nProper Syntax: \n`{settings['Prefix']}holiday <Month> <Day>` \nExample: \n`{settings['Prefix']}holiday January 1`",
            colour=discord.Color.from_rgb(randint(0, 255),randint(0, 255),randint(0, 255))
            )
        await ctx.send(embed=errorembed)
        return
    
    if holiday == '':
        holiday = "Sorry! No Holidays Today!"
    else:
        holiday = "Happy " + holiday

    hollyembed = discord.Embed(title=f"{month} {day}", description=f"{holiday}", colour=discord.Color.from_rgb(randint(0, 255),randint(0, 255),randint(0, 255)))
    await ctx.send(embed=hollyembed)

@client.command()
@has_permissions(administrator=True)
async def forceannounce(ctx):
    now = datetime.datetime.now()
    month = now.strftime("%B")
    day = now.strftime("%d")

    holiday = holidays[str(month)][str(day)]
    if holiday != '':
        # Setting Status because it's a holiday of sorts
        await client.change_presence(status=discord.Status.online, activity=discord.Game(f"Happy {holiday}"), afk=False)

        # If an announcement channel exists and is defined, this will only happen if it's a holiday
        if str(settings['announcement_channel']) != str(0):
            channel = client.get_channel(int(settings['announcement_channel']))
            announcementbed = discord.Embed(title=f"{month} {day}", description=f"Happy {holiday}", colour=discord.Color.from_rgb(randint(0, 255),randint(0, 255),randint(0, 255)))
            await channel.send(embed=announcementbed)
        else:
            await ctx.send("Cannot announce because there is no channel defined in config.py")
    else:
        # Because there's no holiday :)
        await client.change_presence(status=discord.Status.online, activity=discord.Game(f"Have a nice day!"), afk=False)



# Looping Tasks
@tasks.loop(minutes=60.0)
async def refresh_holiday():
    now = datetime.datetime.now()
    month = now.strftime("%B")
    day = now.strftime("%d")

    holiday = holidays[str(month)][str(day)]

    await client.change_presence(status=discord.Status.online, activity=discord.Game(f"Happy {holiday}"), afk=False)
    if now.hour == 1 and str(settings['announcement_channel']) != str(0):
        if holiday != '':
            channel = client.get_channel(int(settings['announcement_channel']))
            announcementbed = discord.Embed(title=f"{month} {day}", description=f"Happy {holiday}", colour=discord.Color.from_rgb(randint(0, 255),randint(0, 255),randint(0, 255)))
            await channel.send(embed=announcementbed)

client.run(token)
