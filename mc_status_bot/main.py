# Monday June 7th 2021
#
# https://github.com/Dinnerbone/mcstatus

import asyncio
import json
import os
import random
import sys
from random import randint

import discord
from discord.ext import commands, tasks
from discord.utils import get
from mcstatus import MinecraftServer

from configuration import mc_address, prefix, token, cogs

from datetime import *

# -----------------
# Setting Variables
# -----------------

client = commands.Bot(command_prefix=prefix)


#print("Time = %s:%s" % (time.hour, time.minute))

global messagelist 
global messageno
messagelist = ["version", "ip", "motd", "players", "randomplayer", "time"]
messageno = 0



# -- 
# Code examples/notes
# --

#query = server.query()

## Stuff I want to save
# Player list | status.players.sample | f"Players Online: {status.players.online}/{status.players.max}"
# Server MOTD | f"MOTD: {status.description['extra'][0]['text']}"
# Server Version | 
# 


# print(f"Players Online: {status.players.online}/{status.players.max}")
# print(namelist)
# print(f"MOTD: {status.description['extra'][0]['text']}")
# print(f"Version: {status.version.name}")

# print(f"IP: {mc_address}")
# print(f"Ping: {status.latency}")
#print(f"Map: {status.map}")
#print(f"Players: {query.players.names}")

# --
# Discord Events
# --

@client.event
async def on_ready(): # When the bot connects to discord it prints the following message.
    print(f"{client.user} has connected to discord.")

    # Starting Loops
    message_loop.start()

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send('cumming is on a %.2fs cooldown' % error.retry_after)
        return
    raise error  # re-raise the error so all the errors will still show up in console

initial_extensions = cogs
# Here we load our extensions(cogs) listed above in [initial_extensions].
if __name__ == '__main__':
    for extension in initial_extensions:
        client.load_extension(extension)
        print(f"{extension} was loaded.")

# --
# Loops
# --

@tasks.loop(seconds = 20)
async def message_loop():
    global time
    time = datetime.now()

    global server
    global status
    try:
        server = MinecraftServer.lookup(mc_address)
        status = server.status()
        await client.change_presence(status=discord.Status.online, activity=discord.Game(get_next_message()), afk=False)
    except:
        await client.change_presence(status=discord.Status.online, activity=discord.Game("Waiting on the minecraft server..."), afk=True)



# --
# Commands
# --

@client.command()
async def players(ctx):
    if  status.players.online >= 1:
        players = return_player_name_list()
        sentence = ", ".join(players)
    else:
        sentence = "No one is online."
        
    embed = discord.Embed(title=f"Players Online | {status.players.online}/{status.players.max}", description = sentence, colour=discord.Color.from_rgb(randint(0, 255),randint(0, 255),randint(0, 255)))
    await ctx.send(embed=embed)

@client.command()
async def info(ctx):
    sentence = f"Join at {mc_address}"
    embed = discord.Embed(title=f"{status.description['text']}", description = sentence, colour=discord.Color.from_rgb(randint(0, 255),randint(0, 255),randint(0, 255)))
    if status.players.online >= 1:
        players = return_player_name_list()
        string = ", ".join(players)
        embed.add_field(name=f"Players {status.players.online}/{status.players.max}", value=string)
    embed.add_field(name="Latency", value=f"{status.latency}")
    embed.add_field(name="Version", value=f"{status.version.name}")

    await ctx.send(embed=embed)


@client.command()
async def randomaction(ctx):
    actions = [
        "PLAYER is mining.",
        "PLAYER is building.",
        "PLAYER is fighting mobs.",
        "PLAYER is tending to their farms.",
        "A skeleton is attacking PLAYER.",
        "A creeper is hissing at PLAYER!",
        "Phantoms are attacking PLAYER!",
        "Nobody but PLAYER is sleeping..",
        "PLAYER is digging straight down!",
        "PLAYER is summoning Herobrine!",
        "PLAYER is playing Terraria instead.",
        "You find PLAYER crafting a diamond hoe..",
        "PLAYER is trading with villagers.",
        "PLAYER accidentally crafted all of their diamonds into boots",
        "PLAYER forgot to bring torches.",
        "PLAYER turned off auto-jump",
        "OOPS! PLAYER turned ON auto-jump!",
        "PLAYER found diamonds!",
        "PLAYER died to [Intentional Game Design]",
        "You told PLAYER to sleep in the nether.",
        "PLAYER is chopping wood!"
    ]
    if status.players.online >= 1:
        # do
        player = random.choice(return_player_name_list())
        action = str(random.choice(actions)).replace("PLAYER", player)

        emb = discord.Embed(description=f"{action}", colour=discord.Color.from_rgb(randint(0, 255),randint(0, 255),randint(0, 255)))
        await ctx.send(embed = emb)

    else:
        await ctx.send("No one is online.")


# --
# Functions
# --
 
def get_next_message():
    global messagelist
    global messageno
    global server
    global status

    messageno += 1

    if messageno <= len(messagelist)-1:
        messagemode = messagelist[messageno]
    else:
        messageno = 0
        messagemode = messagelist[messageno]
    
    if messagemode == "version":
        return f"{status.version.name}"
    elif messagemode == "ip":
        return f"{mc_address}"
    elif messagemode == "players":
        return f"Players Online: {status.players.online}/{status.players.max}"
    elif messagemode == "randomplayer":
        if status.players.online >= 1:
            return f"Minecraft with {random.choice(return_player_name_list())}!"
        else:
            return f"Minecraft with no one... :("
    elif messagemode == "time":
        t = time.strftime("%I:%M %p")
        return f"{status.players.online} online | {t} CST"
    elif messagemode == "motd":
        return f"{status.description['text']}"

def return_player_name_list():
    players = status.players.sample
    namelist = []
    for player in players:
        namelist.append(player.name)
    return namelist

client.run(token)
