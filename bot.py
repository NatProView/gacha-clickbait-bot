import discord
from discord.ext import commands
import random
import logging
from database import get_database
from random import randrange
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import subprocess
import scraper
import time
import re
load_dotenv()

bot = commands.Bot(command_prefix='$')
logging.basicConfig(level=logging.INFO)
dbname = get_database()
users_collection = dbname["User"]
clickbait_prefix_collection = dbname['Prefix']
clickbait_subject_collection = dbname['Subject']
clickbait_activity_collection = dbname['Activity']

users = list(users_collection.find())
admins = list(filter(lambda x: x['isAdmin'] is True, users))
starttime = time.time()
limit = 50

clickbait_prefix = list(clickbait_prefix_collection.find())
clickbait_activity = list(clickbait_activity_collection.find())
clickbait_subject = list(clickbait_subject_collection.find())
prefix = []
activity = []
subject = []
for p in clickbait_prefix:
    prefix.append(p['text'])

for a in clickbait_activity:
    activity.append(a['text'])

for s in clickbait_subject:
    subject.append(s['text'])


# TODO change int casting
# TODO remake whole clickbait functionality :)


class NotAnAdmin(commands.CheckFailure):
    pass


def admin_only():
    async def predicate(ctx):
        if users_collection.find_one({"discordId": int(ctx.author.id), "isAdmin": True}) is None:
            raise NotAnAdmin("Hey, you're not an admin!")
        return True

    return commands.check(predicate)


def is_trusted(userid):
    if users_collection.find_one({"discordId": int(userid), "isAdmin": True}) is None:
        return False
    else:
        return True


# async def check_temp():
#     while True:
#         temp = float(subprocess.getoutput('vcgencmd measure_temp | egrep -o \'[0-9]*\.[0-9]*\''))
#         if temp > limit:
#             dif = temp - limit
#             user = await bot.fetch_user(178094529008762880)
#             await user.send(f"The temperature is {dif:.{3}} above limit [{temp}/{limit}]")
#         time.sleep(300.0 - ((time.time() - starttime) % 300.0))


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    with open('channel', 'r') as f:
        await bot.get_channel(int(f.readline())).send("I'm back online!")
    # await check_temp()


@commands.is_owner()
@bot.command()
async def shutdown(ctx):
    await ctx.send("I'm leaving, take care!")
    with open('channel', 'w') as f:
        f.write(str(ctx.channel.id))
    await ctx.bot.logout()


@commands.is_owner()
@bot.command(name="temp")
async def temperature(ctx):
    temp = subprocess.getoutput('vcgencmd measure_temp | egrep -o \'[0-9]*\.[0-9]*\'')
    await ctx.send(f"Machine temperature: **{temp}**")


# TODO dodac error handling z dekoratorami
@bot.command(name="roll")
async def dice_roll(ctx, arg):
    matched = re.match(r"(?P<number_of_times>\d+)d(?P<dice_number>\d+)", arg)
    if matched == None:
        await ctx.send("It's not a correct dice  :<")
        return
    matched = matched.groupdict()
    matched['number_of_times'] = int(matched['number_of_times'])
    matched['dice_number'] = int(matched['dice_number'])
    if matched['number_of_times'] < 1 or matched['dice_number'] < 1:
        await ctx.send("It's not a correct dice :<")
        return
    rolls = []
    for x in range(matched['number_of_times']):
        random_throw = randrange(matched['dice_number']) + 1
        rolls.append(random_throw)
    rolls_list = ', '.join(str(roll) for roll in rolls)
    message = "Rolled: {} | **Sum: {}**".format(rolls_list, sum(rolls))
    await ctx.send(message)


@bot.command()
async def weather(ctx):
    weather_dict = scraper.get_weather()
    msg = "**Currently in Gdańsk:**\n" + \
          "**Temperature:** " + weather_dict.get("temperature") + " °C | " + \
          "**Humidity:** " + weather_dict.get('humidity') + " % | " + \
          "**Pressure:** " + weather_dict.get("pressure") + " hPa"
    await ctx.send(msg)


@commands.is_owner()
@bot.command()
async def restart(ctx):
    await ctx.send("Restarting...")
    with open('channel', 'w') as f:
        f.write(str(ctx.channel.id))
    await ctx.bot.logout()
    subprocess.call("./start.sh")


@shutdown.error
async def shutdown_error(ctx, error):
    await ctx.send(error)


@bot.command()
@admin_only()
async def check(ctx):
    await ctx.send("Yup, you can use this command!")


@check.error
async def check_error(ctx, error):
    if isinstance(error, NotAnAdmin):
        await ctx.send(error)


@bot.command()
async def repeat(ctx, *arg):
    await ctx.send(arg)


@bot.command()
async def clickbait(ctx):
    clickbait = "**" + \
                random.choice(prefix) + "** " + \
                random.choice(subject) + " " + \
                random.choice(activity)
    await ctx.send(clickbait.upper())


@admin_only()
@bot.command(name="trusted_add")
async def add_trusted(ctx, user: discord.User):
    global users
    users = list(users_collection.find())
    if is_trusted(user.id) is True:
        await ctx.send("This user is already an admin! :)")
        return
    users_collection.insert_one({"name": user.name, "discordId": user.id, "isAdmin": True})
    users = list(users_collection.find())
    global admins
    admins = list(filter(lambda x: x['isAdmin'] is True, users))
    await ctx.send(f"Hooray! <@{user.id}> has become an admin!")


@admin_only()
@bot.command(name="trusted_remove")
async def remove_trusted(ctx, user: discord.User):
    x = users_collection.delete_many({"discordId": int(user.id)})
    if x.deleted_count > 0:
        global users
        global admins
        users = list(users_collection.find())
        admins = list(filter(lambda x: x['isAdmin'] is True, users))
        await ctx.send("User successfully deleted from admin list")
    else:
        await ctx.send("Could not delete this user from admin list. Perhaps he wasn't there to begin with?")


@admin_only()
@bot.command(name="trusted_list")
async def trusted_list(ctx):
    msg = "**Admins:** "
    for admin in admins:
        msg += admin['name'] + " | "
    await ctx.send(msg)


@bot.command(name="trusted_check")
async def trusted_check(ctx):
    await ctx.send(list(users_collection.find({"discordId": int(ctx.author.id), "isAdmin": True})))


@add_trusted.error
@remove_trusted.error
@trusted_list.error
async def not_an_admin_error(ctx, error):
    if isinstance(error, NotAnAdmin):
        await ctx.send(error)


@bot.command(name="myid")
async def my_id(ctx):
    await ctx.send(ctx.author.id)


bot.run(os.environ.get('DISCORD_TOKEN'))
