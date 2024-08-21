import discord
from discord import app_commands
from discord.ext import commands


class MyGroup(app_commands.Group):
  @app_commands.command(description="Welcome user", name="greetings2")
  async def hallo(self,interaction: discord.Interaction):
    """ Merespon """
    await interaction.response.send_message(
      f"Hallo juga {interaction.user.mention}", ephemeral=True)


  @app_commands.command(description="Welcome user", name="greetingss")
  async def cuy(self,interaction: discord.Interaction):
    """ Merespon """
    await interaction.response.send_message(
      f"Hallo juga {interaction.user.mention}", ephemeral=True)

async def setup(bot):
  bot.tree.add_command(MyGroup(name="greetings3", description="Says hello"))