import discord
from discord.ext import commands


class Greetings(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  #setiap kali member masuk server
  @commands.Cog.listener()
  async def on_member_join(self, member):
      channel = member.guild.system_channel
      if channel is not None:
          await channel.send(f'Welcome {member.mention}.')

  #setiap kali user chat akan direact
  # @commands.Cog.listener()
  # async def on_message(self, message: discord.Message):
  #   await message.add_reaction("✅")
  
  @commands.command()
  async def hello(self, ctx, *, member: discord.Member):
    await ctx.send(f"Hello {member.name}")

async def setup(bot):
  await bot.add_cog(Greetings(bot))

#Macam-macam event:
#on_member_join, on_member_remove, on_member_update, on_member_ban