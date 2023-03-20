import os
import json
import sqlite3
import time
import discord
from discord.ext import commands
import hercules.helper.log as log

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents, help_command=None)

os.environ['TZ'] = 'UTC'

@bot.event
async def on_ready():
    bot_start_load_time = time.time()
    log.in_log("INFO", "on_ready", f"Logged in as {bot.user}")

    for file in os.listdir("hercules/commands"):
        if "pycache" in file:
            continue
        await bot.load_extension("hercules.commands." + file[0:-3])

    for file in os.listdir("hercules/systems"):
        if "pycache" in file:
            continue
        await bot.load_extension("hercules.systems." + file[0:-3])

    bot_finish_load_time = time.time()

    log.in_log("INFO", "benchmark", f"Finished loading in {bot_finish_load_time - bot_start_load_time:.3f} seconds")

    db_connection = sqlite3.connect("data.db")
    db_cursor = db_connection.cursor()

    res = db_cursor.execute("SELECT name FROM sqlite_master WHERE name='servers'")

    if res.fetchone() is None:
        db_cursor.execute("""
        CREATE TABLE
        servers(
            guild_id,
            traffic_channel,
            verification_channel,
            general_channel,
            logs_channel,
            join_message,
            leave_message,
            verification_message,
            join_leave_system,
            invite_nuker_system,
            verification_system,
            logs_system
        )
        """)
        db_connection.commit()

    guilds = bot.guilds

    for guild in guilds:
        guild_id = guild.id
        res = db_cursor.execute("SELECT guild_id FROM servers WHERE guild_id=?", (guild_id,))
        if res.fetchone() is None:
            log.in_log("INFO", "guild_db_init", f"a guild is not in DB; initialising...")
            db_cursor.execute("INSERT INTO servers VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (guild_id, None, None, None, None, None, None, None, None, None, None, None,))
            db_connection.commit()

        general_channel_in_server = discord.utils.find(lambda c: c.name == "general", guild.channels)

        if general_channel_in_server:
            res = db_cursor.execute(f"UPDATE servers SET general_channel = ? WHERE guild_id=?", (general_channel_in_server.id, guild_id))
            db_connection.commit()

    db_connection.close()

@bot.event
async def on_command_error(ctx, error):
    guild = ctx.guild
    guild_name = guild.name
    guild_id = guild.id
    channel = ctx.channel
    channel_name = channel.name
    channel_id = channel.id
    user = ctx.author
    user_id = user.id
    user_name = f"{user.name}#{user.discriminator}"

    log.in_log("ERROR", "on_command_error", f"guild_id={guild_id} guild_name='{guild_name}' channel_id={channel_id} channel_name='{channel_name}' user_id={user_id} user_tag={user_name} {error}")

    if ctx.message.content.startswith("._"):
        return

    embed_content = {
        "title": ":x: There was an error",
        "description": f"```{error}```"
    }

    embed = discord.Embed().from_dict(embed_content)

    await ctx.reply(embed=embed)

@bot.event
async def on_command_completion(ctx):
    guild = ctx.guild
    guild_name = guild.name
    guild_id = guild.id
    channel = ctx.channel
    channel_name = channel.name
    channel_id = channel.id
    user = ctx.author
    user_id = user.id
    user_name = f"{user.name}#{user.discriminator}"
    command_name = ctx.command.name
    command_arguments = ctx.message.content

    log.in_log("INFO", "on_command", f"guild_id={guild_id} guild_name='{guild_name}' channel_id={channel_id} channel_name='{channel_name}' user_id={user_id} user_tag={user_name} command_name='{command_name}' command_arguments='{command_arguments}'")

with open("config.json", "r", encoding="utf-8") as config:
    config = json.load(config)

real_bot = int(os.getenv("REAL"))

if not real_bot == 0:
    bot.run(config["dev_token"])

bot.run(config["token"])
