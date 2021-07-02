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

global configpath 
configpath = f"{ROOT_DIR}/config.json"
global data
data = open_json(configpath)

#
# // Events
#

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

@client.command(aliases=["rolemenu", "rolelist"])
async def roles(ctx):
    global configpath 
    data = open_json(configpath)

    if str(ctx.guild.id) in data:
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

        msg = await ctx.send(
            "Choose your role from the list.",
            components=[
                SelectMenu(
                    custom_id=f"ROLE_MENU_{ctx.author.id}",
                    placeholder="Choose Role",
                    max_values=1,
                    options= optlist
                )
            ]
        )

        inter = await msg.wait_for_dropdown()
        labels = [option.value for option in inter.select_menu.selected_options]
        if inter.author.id == ctx.author.id:
            role = get(ctx.guild.roles, id=int(labels[0]))
            await ctx.author.add_roles(role)
            await inter.reply(f"{ctx.author} was given the {role.name} role.")
        else:
            await inter.reply(f"Action Failed due to interference.")

    else:
        data[str(ctx.guild.id)] = []
        save_json(configpath, data)
        await ctx.send("This server isn't configured.")

@client.command(aliases=["removeroles", "removerolemenu", "subrole"])
async def removerole(ctx):
    global configpath
    global configpath 
    data = open_json(configpath)

    if str(ctx.guild.id) in data:
        role_list = data[str(ctx.guild.id)]
        user_roles = ctx.author.roles
        print(user_roles)
        applicable_roles = []

        for role in role_list:
            for r in user_roles:
                if int(r.id) == int(role):
                    if int(r.id) in applicable_roles:
                        pass
                    else:
                        applicable_roles.append(int(r.id))

        # Breaks before here
        print("Applicable Roles ", applicable_roles)
        optlist = []
        for roleid in applicable_roles:
            role = get(ctx.guild.roles, id=int(roleid))
            applicable_roles.remove(roleid)
            optlist.append(SelectOption(f"{role.name}", roleid))

        print(optlist)
        # Important Break, to catch errors.
        if len(optlist) <= 0:
            await ctx.send("You don't have any roles that can be removed.")
            return 


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

@client.command()
@has_permissions(administrator=True)
async def rolesettings(ctx, mode, role):
    global configpath
    data = open_json(configpath)
    add_modes = ["add", "append", "include"]
    sub_modes = ["sub", "subtract", "remove"]
    print(mode, role)
    role = str(role)[3:len(str(role))-1]
    if str(mode).lower() in add_modes or str(mode).lower() in sub_modes:
        # Do
        if str(mode).lower() in add_modes:
            if str(ctx.guild.id) in data:
                data[str(ctx.guild.id)].append(role)
            else:
                data[str(ctx.guild.id)] = []
                data[str(ctx.guild.id)].append(role)
            pass
        elif str(mode).lower() in sub_modes:
            if role in data[str(ctx.guild.id)]:
                data[str(ctx.guild.id)].remove(role)
            else:
                await ctx.send("That role isn't even in the list!")

        save_json(configpath, data)

    else:
        await ctx.send(f"{mode} is not a valid mode.")


@rolesettings.error
async def rolemenu_error(error, ctx):
    print(error)
    if isinstance(error, MissingPermissions):
        await ctx.send("You cannot perform this action")
    await ctx.send(f"ERROR: You can't do this!")

# @client.command()
# async def spam(ctx, arg1, arg2):

#     optlist = []
#     if int(arg2) >= 25:
#         arg2 = 24
#     for i in range(0, int(arg2)):
#         optlist.append(SelectOption(f"{str(i)}", f"{str(i)}"))

#     msg = await ctx.send(
#         "I'm prime to spam, just tell me how many times I should do it!",
#         components=[
#             SelectMenu(
#                 custom_id="test",
#                 placeholder="Choose Amount to spam",
#                 max_values=1,
#                 options= optlist
#             )
#         ]
#     )

#     inter = await msg.wait_for_dropdown()
#     labels = [option.label for option in inter.select_menu.selected_options]
#     print(inter.__dict__)
#     if inter.author.id == ctx.author.id:
#         await inter.reply(f"Spam Amount: {', '.join(labels)}")

#         for i in range(0, int(labels[0])):
#             await ctx.send(f"{ctx.author.name}: {arg1}")
#     else:
#         await ctx.send(f"Only {ctx.author} can spam using this menu, try doing `!spam <'message in quotes'> <number>` on your own.")


slash = SlashClient(client)
client.run(token)
