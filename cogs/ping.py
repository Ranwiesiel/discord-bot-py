import discord
from discord.ext import commands
import time


class PingCog(commands.Cog, name="Ping"):
	"""
	Ping command
	"""
	def __init__(self, bot:commands.bot):
		self.bot = bot
        
	@commands.command(name = "ping",
					usage="",
					description = "Display the bot's ping.")
	@commands.cooldown(1, 2, commands.BucketType.member)
	async def ping(self, ctx):
		"""
		Display the bot's ping.
		"""
		before = time.monotonic()
		message = await ctx.send("🏓 Pong !")
		ping = (time.monotonic() - before) * 1000
		await message.edit(content=f"🏓 Pong !  `{int(ping)} ms`")

async def setup(bot:commands.Bot):
	await bot.add_cog(PingCog(bot))