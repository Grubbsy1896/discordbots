import os
import configparser
import requests

from twitchAPI.twitch import Twitch

from data import client_id, client_secret


twitch = Twitch(client_id, client_secret)
twitch.authenticate_app([])
TWITCH_STREAM_API_ENDPOINT_V5 = "https://api.twitch.tv/kraken/streams/{}"
API_HEADERS = {
    'Client-ID' : client_id,
    'Accept' : 'application/vnd.twitchtv.v5+json',
}

# --
# > Functions
# --

def check_user(user): #returns true if online, false if not
    userdata = get_stream_data(user)
    if 'stream' in userdata:
        if userdata['stream'] is not None:
            return True
        else:
            return False
    else:
        return False

def get_stream_data(user):
    userid = twitch.get_users(logins=[user])['data'][0]['id']
    url = TWITCH_STREAM_API_ENDPOINT_V5.format(userid)
    try:
        req = requests.Session().get(url, headers=API_HEADERS)
        jsondata = req.json()
        return jsondata
    except Exception as e:
        print("Error checking user: ", e)
        return False
