import os
import json
import sys
import configparser

# --
# > Variables
# --

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
data_path = f"{ROOT_DIR}/data"

# --
# Loading From Config.ini
# --
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
config = configparser.ConfigParser()
config.read(f"{data_path}/config.ini")

# Twitch Config Variables
client_id     = config['TWITCH']['client_id']
client_secret = config['TWITCH']['client_secret']

# Discord Config Settings
token         = config['DISCORD']['bot_token']
prefix        = config['DISCORD']['command_prefix']

# Bot Setting Variables
# THESE WILL SOON BE IN THE configration.json !!

announcement_channels = str(config['BOT_SETTINGS']['announcement_channels']).split(", ")

twitch_channels = str(config['BOT_SETTINGS']['twitch_channels']).split(", ")

refresh_rate = int(config['BOT_SETTINGS']['refresh_rate'])


