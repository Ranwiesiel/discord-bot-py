import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import math
import random
import typing

class Leveling(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._cd = commands.CooldownMapping.from_cooldown(1, 6.0, commands.BucketType.member)

    def get_ratelimit(self, message: discord.Message) -> typing.Optional[int]:
        """Returns the ratelimit left"""
        bucket = self._cd.get_bucket(message)
        return bucket.update_rate_limit()
    

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        ratelimit = self.get_ratelimit(message)
        if ratelimit is None:
            if message.author.bot:
                return
            
            conn = sqlite3.connect("./cogs/levels.db")
            cursor = conn.cursor()
            guild_id = message.guild.id
            user_id = message.author.id

            cursor.execute(f"SELECT * FROM Users WHERE guild_id = {guild_id} AND user_id = {user_id}")
            result = cursor.fetchone()

            if result is None:
                cur_level = 0
                xp = 0
                level_up_xp = 100
                cursor.execute(f"INSERT INTO Users (guild_id, user_id, level, xp, level_up_xp) VALUES ({guild_id}, {user_id}, {xp}, {cur_level}, {level_up_xp})")

            else:
                cur_level = result[2]
                xp = result[3]
                level_up_xp = result[4]

                xp += random.randint(10, 20)

            if xp >= level_up_xp:
                cur_level += 1
                new_level_up_xp = math.ceil(50 * cur_level ** 2 + 100 * cur_level + 50)

                await message.channel.send(f"Selamat {message.author.mention}, kamu telah naik level {cur_level}!")

                cursor.execute(f"UPDATE Users SET level = {cur_level}, xp = {xp}, level_up_xp = {new_level_up_xp} WHERE guild_id = {guild_id} AND user_id = {user_id}")

            cursor.execute(f"UPDATE Users SET xp = {xp} WHERE guild_id = {guild_id} AND user_id = {user_id}")

            conn.commit()
            conn.close()


    """ default level command """
    @commands.command()
    async def level(self, ctx: commands.Context, member: discord.Member = None):

        if member is None:
            member = ctx.author

        member_id = member.id
        guild_id = ctx.guild.id

        conn = sqlite3.connect("./cogs/levels.db")
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM Users WHERE guild_id = {guild_id} AND user_id = {member_id}")
        result = cursor.fetchone()

        if result is None:
            await ctx.send(f"Member {member.mention} belum memiliki level!")
        else:
            level = result[2]
            xp = result[3]
            level_up_xp = result[4]

            await ctx.send(f"Member {member.mention} memiliki level {level} dengan {xp} XP dan butuh {level_up_xp} XP untuk naik level selanjutnya!")
        
        conn.close()


    """ slash command """
    @app_commands.command(name="level", description="Check your level")
    async def level(self, interaction: discord.Interaction, member: discord.Member = None):

        if member is None:
            member = interaction.user

        member_id = member.id
        guild_id = interaction.guild.id

        conn = sqlite3.connect("./cogs/levels.db")
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM Users WHERE guild_id = {guild_id} AND user_id = {member_id}")
        result = cursor.fetchone()

        if result is None:
            await interaction.response.send_message(f"Member {member.mention} belum memiliki level!")
        else:
            level = result[2]
            xp = result[3]
            level_up_xp = result[4]

            await interaction.response.send_message(f"Member {member.mention} memiliki level {level} dengan {xp} XP dan butuh {level_up_xp} XP untuk naik level selanjutnya!")
        
        conn.close()


async def setup(bot):
    await bot.add_cog(Leveling(bot))