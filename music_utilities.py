# This file is used to clean up some of the functions in the main file.
from re import A
import interactions
import datetime
from interactions.ext.wait_for import wait_for_component
import uuid
import random
import asyncio
import lavalink
import database_manager as db_manager
import lyricsgenius
import os
import custom_source

from interactions.ext.lavalink import Lavalink

bot : interactions.Client

def setup_(self):
    global bot
    global genius
    
    bot = self
    genius = lyricsgenius.Genius(os.getenv('GENIUS'))

