import discord
from discord.ext import commands
import random
import logging
from database import get_database
from random import randrange
from pymongo import MongoClient
import subprocess

bot = commands.Bot(command_prefix='$')
logging.basicConfig(level=logging.INFO)
file = open("token", "r")
token = file.read()
file.close()
dbname = get_database()
users_collection = dbname["User"]
clickbait_prefix_collection = dbname['Prefix']
clickbait_subject_collection = dbname['Subject']
clickbait_activity_collection = dbname['Activity']

users = list(users_collection.find())
admins = list(filter(lambda x: x['isAdmin'] is True, users))

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


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    with open('channel', 'r') as f:
        await bot.get_channel(int(f.readline())).send("I'm back online!")


@commands.is_owner()
@bot.command()
async def shutdown(ctx):
    await ctx.send("I'm leaving, take care!")
    with open('channel', 'w') as f:
        f.write(ctx.channel.id)
    await ctx.bot.logout()


@commands.is_owner()
@bot.command()
async def restart(ctx):
    await ctx.send("Restarting...")
    await ctx.bot.logout()
    with open('channel', 'w') as f:
        f.write(ctx.channel.id)
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


bot.run(token)

