import discord
from discord.ext import commands
import sqlite3
import hercules.helper.log as log
import hercules.helper.herculesdb as db

class JoinLeave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = member.guild.id

        db_connection, db_cursor = db.connect_to_db("data.db")

        row = db_cursor.execute("SELECT general_channel, join_leave_system, traffic_channel, join_message, verification_system, verification_channel, verification_message FROM servers WHERE guild_id = ?", (guild_id,)).fetchone()

        general_channel = row["general_channel"]
        join_leave_system = row["join_leave_system"]
        traffic_channel = row["traffic_channel"]
        join_message = row["join_message"]
        verification_system = row["verification_system"]
        verification_channel = row["verification_channel"]
        verification_message = row["verification_message"]

        if general_channel is not None:
            general_channel = self.bot.get_channel(int(general_channel))

        if join_leave_system == 1:
            if traffic_channel is not None:
                traffic_channel = self.bot.get_channel(int(traffic_channel))

                if join_message is not None:
                    await traffic_channel.send(f":inbox_tray: {member.mention} {join_message}")
            else:
                await general_channel.send(":warning: **System Message**: The Join/Leave system has been turned on but there is no `traffic_channel` set.")

        if verification_system == 1:
            if verification_channel is not None:
                verification_channel = self.bot.get_channel(int(verification_channel))

                if verification_message is not None:
                    await verification_channel.send(f"{member.mention} {verification_message}")
            else:
                await general_channel.send(":warning: **System Message**: The Verification System has been turned on but there is no `verification_channel` set.")

        db_connection.close()

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild_id = member.guild.id

        db_connection, db_cursor = db.connect_to_db("data.db")

        row = db_cursor.execute("SELECT join_leave_system, traffic_channel, leave_message, general_channel FROM servers WHERE guild_id = ?", (guild_id,)).fetchone()

        general_channel = row["general_channel"]
        join_leave_system = row["join_leave_system"]
        traffic_channel = row["traffic_channel"]
        leave_message = row["leave_message"]

        if general_channel is not None:
            general_channel = self.bot.get_channel(int(general_channel))

        if join_leave_system == 1:
            if traffic_channel is not None:
                traffic_channel = self.bot.get_channel(int(traffic_channel))

                if leave_message is not None:
                    await traffic_channel.send(f":outbox_tray: {member.mention} {leave_message}")
            else:
                await general_channel.send(":warning: **System Message**: The Join/Leave system has been turned on but there is no `traffic_channel` set.")

        db_connection.close()

async def setup(bot):
    log.in_log("INFO", "listener_setup", "Join/Leave System has been loaded")
    await bot.add_cog(JoinLeave(bot))
