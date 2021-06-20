# tempchans.py is a temporary channel function for my bot, the beholder bot.
import sys
import os
import discord
import asyncio
import random
import json
import time
import datetime as dt
from pathlib import Path
#import sqlite3
#------------------------------------------
from math import ceil
from datetime import datetime
from random import randint
from discord.ext import tasks, commands
from discord.utils import get
#from collections import Counter
#------------------------------------------
class tempchans(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # --
    # Dicts
    # --
    global _tempchannels
    _tempchannels = {}

    global default_config
    default_config = {
        "temp_category": 0
    }


    # -- 
    # Basic Functions
    # --

    def do_create_voice_channel(self, ownerid, channelid, name, maxlimit, private):
        global _tempchannels
        default_channel = {
            "name": name,
            "ownerid": ownerid,
            "maxlimit": maxlimit,
            "private": private,
            "queue": [], # List of IDs
        }
        _tempchannels[str(channelid)] = default_channel

    # --
    # Discord Functions and Commands
    # --
    @commands.Cog.listener()
    async def on_ready(self):
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        configpath = f"{ROOT_DIR}/configs/tempchannels.json"
        configfolder = Path(f"{ROOT_DIR}/configs/")
        configpath = Path(configpath)
        if os.path.exists(configfolder) != True:
            os.mkdir(configfolder)
        if os.path.exists(configpath) != True:
            print(f"You NEED to setup the configuration with the file created at, {configpath}")
            print(f"YOU MUST GET A CATEGORY ID, AND REPLACE THE 0 IN THE CONFIG THAT WAS CREATED!")
            with open(configpath, 'w+') as datafile:
                json.dump(default_config, datafile, indent=4)
        else:
            print("TempChannel Configuration Loaded.")
            with open(configpath, 'r') as datafile:
                global settings
                settings = json.load(datafile)


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel:
            if before.channel.category.id == settings['temp_category']:
                if len(before.channel.members) == 0:
                    await before.channel.delete()

    # Creating Voice Channel Command
    @commands.command(aliases=["vccreate"])
    async def createvc(self, ctx, name, max_limit=0, private=False): # Default means it's a public channel
        global settings
        global _tempchannels
        if ctx.author.voice:
            if bool(private) == False:
                channel_connect = True
            else:
                channel_connect = False
            guild = ctx.guild
            member = ctx.author
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=True, connect=channel_connect),
            }
            category = discord.utils.get(ctx.guild.categories, id=settings['temp_category'])
            channel = await guild.create_voice_channel(str(name), overwrites=overwrites, category=category)
            await channel.edit(user_limit = max_limit)
            await ctx.author.move_to(channel)
            self.do_create_voice_channel(ctx.author.id, channel.id, name, max_limit, private) 
        else:
            await ctx.send("You must be in a voice channel to do this command!")

    # Edit Channel Command   
    @commands.command(aliases=["channeledit", "edit", 'ce', 'ec'])
    async def editchannel(self, ctx, mode, value=''):
        global _tempchannels
        if ctx.author.voice:
            channel = self.bot.get_channel(int(ctx.author.voice.channel.id))
            if str(_tempchannels[str(channel.id)]['ownerid']) == str(ctx.author.id):
                max_users_aliases = ["maxusers", "max_users", "max", "user_limit", "userlimit"]
                name_aliases = ["name", "title", "header", "nametag"]

                if str(mode).lower() in max_users_aliases:
                    await channel.edit(user_limit = int(value))
                if str(mode).lower() in name_aliases:
                    await channel.edit(name=str(value))

                if str(mode).lower() == 'unlock':
                    overwrites = {
                        ctx.guild.default_role: discord.PermissionOverwrite(view_channel=True, connect=True),
                    }
                    await channel.edit(overwrites = overwrites)
                elif str(mode).lower() == 'lock':
                    overwrites = {
                        ctx.guild.default_role: discord.PermissionOverwrite(view_channel=True, connect=False),
                    }
                    await channel.edit(overwrites = overwrites)

            else:
                await ctx.send("You don't own this channel, you must be in the channel you own to edit it.")

def setup(bot):
    bot.add_cog(tempchans(bot))