# Thursday June 17th 2021
# Dataloader is an addon for the sole use of myself, as I am incredibly lazy with loading data 
# And saving data. This is a more streamlined way of me doing this.
# import dataloader 
# ^ how it would be imported or something idk lolllll lets go


# ------------
# > Imports
# ------------

import json
import os
import sys


# ------------
# > Defined Variables
# ------------

global ROOT_DIR
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


# ------------
# > Functions
# ------------

def open_json(path):
    if os.path.exists(path) != True:
        return False
    with open(path, 'r') as datafile:
        return json.load(datafile)

def save_json(path, data):
    if os.path.exists(path) != True:
        return False
    with open(path, 'w+') as datafile:
        json.dump(data, datafile, indent=4)