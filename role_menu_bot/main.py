# Discord bot to make a rolemenu using discord's new drop down message component
# July 1st 2021
# Import Everything From Discord
import discord

from discord.ext import commands
from discord.ext import tasks, commands
from discord.utils import get
from discord.ext.commands import has_permissions, MissingPermissions
# OO
from dislash import SlashClient, SelectMenu, SelectOption, slash_commands
from dislash.interactions import *

# General Imports 
import sys
import os
import asyncio
import random
import datetime

from random import randint

from dataloader import open_json, save_json, ROOT_DIR

# Importing the config
from configuration import token, prefix


#
# // Loading the Config Values 
#

client = commands.Bot(command_prefix=prefix)

# 
# //  Global Vars
#

# Here I am making use of dataloader.py, and using the functions I made. 
global configpath 
configpath = f"{ROOT_DIR}/config.json"
global data
data = open_json(configpath)

#
# // Events
#

# This function is the on_message function. It is triggered whenever a message is sent in a channel the bot can view.
@client.event
async def on_message(message):
    # just doing this here cause I had it before, and I wanna keep it just incase
    await client.process_commands(message) # This is so that it will still process commands

@client.event
async def on_ready():
    global data
    print(f"{client.user} has connected to discord.")
    if data == False:
        print("data unable to be loaded. exiting...")
        sys.exit()


#
# // Functions
#

# Functions that streamline dataloader.py as I made the main variables global variables 
# due to the fact I would need them pretty much everywhere.
def get_data():
    global configpath
    global data
    data = open_json(configpath)

def save_data():
    global configpath
    global data
    save_json(configpath, data)



#
# // Commands
#

# The roles command is a huge command.
# It takes no parameters and it creates a neat select menu to pick a role that it will then give to the person who activated the command and the dropdwon.
@client.command(aliases=["rolemenu", "rolelist"])
async def roles(ctx):
    global configpath 
    data = open_json(configpath) # Getting the saved configs.
    
    # This checks to make sure the server is in the config and has saved role ids. 
    if str(ctx.guild.id) in data:
        # The following code is an algorithm of sorts to populate a list full of the role ids and names for the select menu.
        # It first grabs the role list from the serverid in the json saved.
        role_list = data[str(ctx.guild.id)]

        optlist = []
        for roleid in role_list:
            role = get(ctx.guild.roles, id=int(roleid))
            if roleid in optlist:
                data[str(ctx.guild.id)].remove(roleid)
                data[str(ctx.guild.id)].append(roleid)
                save_json(configpath, data)
                return
            else:
                role_list.remove(roleid)
                optlist.append(SelectOption(f"{role.name}", roleid))

        msg = await ctx.send(  # Constructing the message to send.
            "Choose your role from the list.",
            components=[
                SelectMenu(
                    custom_id=f"ROLE_MENU_{ctx.author.id}",
                    placeholder="Choose Role",
                    max_values=1,
                    options= optlist # Constructed earlier
                )
            ]
        )

        inter = await msg.wait_for_dropdown() # This waits for the message component to be interacted with, and once it is, it will continue in the code.
        labels = [option.value for option in inter.select_menu.selected_options] # Getting the answer of the dropdown.
        
        # This check is neccessary as the way I am doing this dropdown is a temporary one. it can be touched once and scrapped.
        # It makes sure that only the author of the message can utilize the dropdown menu.
        if inter.author.id == ctx.author.id: 
            role = get(ctx.guild.roles, id=int(labels[0]))
            await ctx.author.add_roles(role)
            await inter.reply(f"{ctx.author} was given the {role.name} role.")
        else:
            await inter.reply(f"Action Failed due to interference.")

    else: 
        # If the server has no saved role ids for it's role list, it will create an entry and send that message.
        data[str(ctx.guild.id)] = []
        save_json(configpath, data)
        await ctx.send("This server isn't configured.")

# The remove role command is simply an opposite of the role list. 
@client.command(aliases=["removeroles", "removerolemenu", "subrole"])
async def removerole(ctx):
    global configpath
    global configpath 
    data = open_json(configpath) # Getting the data

    if str(ctx.guild.id) in data: # Checking if the server has roles to give.
        role_list = data[str(ctx.guild.id)]
        user_roles = ctx.author.roles # We get the user's roles because we don't want it to try and remove roles a user doesn't have.
        
        # This following portion is the algorithm for getting role ids to then put into the list.
        # It works by grabbing the server's role list (discord server), and seeing what roles the user has, and what roles are saved/ allowed on rolemenu.
        applicable_roles = []
        for role in role_list:
            for r in user_roles:
                if int(r.id) == int(role):
                    if int(r.id) in applicable_roles:
                        pass
                    else:
                        applicable_roles.append(int(r.id))

        print("Applicable Roles ", applicable_roles)
        # constructing the Select Menu Options
        optlist = []
        for roleid in applicable_roles:
            role = get(ctx.guild.roles, id=int(roleid))
            applicable_roles.remove(roleid)
            optlist.append(SelectOption(f"{role.name}", roleid))

        # Important Break, to catch errors.
        # If this wasn't here it would break sometimes.
        # because option lists for the select menus cannot have 0 length/ no items
        if len(optlist) <= 0:
            await ctx.send("You don't have any roles that can be removed.")
            return 

        # Constructing the message.
        msg = await ctx.send(
            "Select the role to remove from the list.",
            components=[
                SelectMenu(
                    custom_id=f"ROLE_MENU_{ctx.author.id}",
                    placeholder="Choose Role To Remove",
                    max_values=1,
                    options= optlist
                )
            ]
        )
        
        # Same sort of interaction stuff, waits for interaction, and does what's needed. (see the previous command for the applicable info)
        inter = await msg.wait_for_dropdown()
        labels = [option.value for option in inter.select_menu.selected_options]
        if inter.author.id == ctx.author.id:
            role = get(ctx.guild.roles, id=int(labels[0]))
            await ctx.author.remove_roles(role)
            await inter.reply(f"The {role.name} role was removed from {ctx.author}.")
        else:
            await inter.reply(f"Action failed due to interferance.")


    else:
        await ctx.send(f"This server is not configured.")

# This is the command that only server admins can use currently, that allows them to determine what roles are allowed in rolemenu. 
# it takes a mode, "Add" or "Subtract" or any of the listed modesl. and then the role. 
# an example use would be
# !rolesettings add @AnnounceToggle
@client.command()
@has_permissions(administrator=True)
async def rolesettings(ctx, mode, role):
    global configpath
    data = open_json(configpath) # Data stuff
    
    # The following lists in lowercase depict what to type to add or remove a role from the server's saved list.
    add_modes = ["add", "append", "include"]   # This is a list that means to add to the list of saved roles. 
    sub_modes = ["sub", "subtract", "remove"]  # This is the list that means to subtract from the list of saved roles.
    print(mode, role) # Debug print.
    
    role = str(role)[3:len(str(role))-1] # This strips the string gained from @ing a role, as on discord an @ mention is formated as <@!roleidno000>
    if str(mode).lower() in add_modes or str(mode).lower() in sub_modes: # This checks if the mode input is valid.
        if str(mode).lower() in add_modes: # this then checks if it's adding.
            if str(ctx.guild.id) in data: # This checks for the server's id.
                data[str(ctx.guild.id)].append(role) # this appends the roleid.
            else:
                data[str(ctx.guild.id)] = [] # this else means that it will then create the server's role list now.
                data[str(ctx.guild.id)].append(role) # this appends the server's first role to it's list.
                
        elif str(mode).lower() in sub_modes: # Checking if it's the subtract mode instead of the add mode.
            if role in data[str(ctx.guild.id)]: # chcecks if the role is in there to prevent error.
                data[str(ctx.guild.id)].remove(role) # removes if such.
            else:
                await ctx.send("That role isn't even in the list!") # reply if action was unsuccessful

        save_json(configpath, data) # Saving the changes made to the data.

    else:
        await ctx.send(f"{mode} is not a valid mode.")

# Discord.py Error handling. In case something went wrong.
@rolesettings.error
async def rolemenu_error(error, ctx):
    print(error)
    if isinstance(error, MissingPermissions):
        await ctx.send("You cannot perform this action")
    await ctx.send(f"ERROR: You can't do this!")

slash = SlashClient(client)
client.run(token)
