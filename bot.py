import discord
from discord.ext import commands
import random
import logging
from pymongo_test_insert import get_database

logging.basicConfig(level=logging.INFO)
file = open("token", "r")
token = file.read()
file.close()
class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        if message.author == client.user:
            return
        
        if message.content.lower().startsWith("$cadence"):
            await message.channel.send("Yes, it is me~")
        
        if message.content.lower().startswith('$ping'):
            await message.channel.send('pong')

        if message.content.lower().startswith('$pong'):
            await message.channel.send('ping')

        #if message.content.lower().startswith("$trusted add "):

        print('Message from {0.author}: {0.content}'.format(message))

client = MyClient()
client.run(token)
