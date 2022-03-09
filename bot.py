import discord

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))

client = MyClient()
client.run('MzQxNTM3ODczNDAyNTI3NzQ1.WX8P7g.Mc4hRJ7v8zu_3_BDL8IPkbg8OgY')
