
import discord
from discord import interactions
from discord.ext import commands
from discord import app_commands
import os
import random
from keep_alive import keep_alive
import settings
from cogs.greetings import Greetings
import typing
import enum

logger = settings.logging.getLogger("bot")  #membuat log


class NotOwner(commands.CheckFailure):
  ...

def is_owner():
  def predicate(interaction : discord.Interaction):
    if interaction.user.id == settings.owner_id:
      return True
  return app_commands.check(predicate)

#hanya owner yang bisa
def is_owner():

  async def predicate(ctx):
    if ctx.author.id != ctx.guild.owner_id:
      raise NotOwner("Hanya owner yang bisa")
    return True

  return commands.check(predicate)


intents = discord.Intents.default()  #perizinan discord
intents.message_content = True  #perizinan pesan
intents.members = True

bot = commands.Bot(command_prefix="$",
                   intents=intents)  #deklarasi bot dengan commandnya

class Food(enum.Enum):
  apple = 1
  banana = 2
  cherry = 3



class Tampar(commands.Converter):  #custom converter user input

  def __init__(self, *, use_nicknames):
    self.use_nicknames = use_nicknames

  async def convert(self, ctx, argument):
    seseorang = random.choice(ctx.guild.members)
    nickname = ctx.author
    if self.use_nicknames:
      nickname = ctx.author.nick
    return f"{ctx.author} menampar {seseorang} dengan {argument}"


@bot.event  #ketika bot dijalankan
async def on_ready():
  logger.info(f"We have logged in as {bot.user} (ID {bot.user.id})")
  print("=" * 50)

  
  # mygroup = MyGroup(name="greetings", description="Welcomes users")
  # bot.tree.add_command(mygroup)
  await bot.load_extension("slashcmds.welcome")
  
  bot.tree.copy_global_to(guild=settings.GUILDS_ID)
  await bot.tree.sync(guild=settings.GUILDS_ID)

  #load semua file yang dituju dalam file settings
  for cog_file in settings.COGS_DIR.glob("*.py"):
    if cog_file != "__init__.py":
      await bot.load_extension(f"cogs.{cog_file.name[:-3]}")

  for cmd_file in settings.CMDS_DIR.glob("*.py"):
    if cmd_file.name != "__init__.py":
      await bot.load_extension(f"cmds.{cmd_file.name[:-3]}")

  #load, unload, dan reload cog commands
  @commands.command()
  async def load(ctx, cog: str):
    await bot.load_extension(f"cogs.{cog.lower()}")

  @commands.command()
  async def unload(ctx, cog: str):
    await bot.unload_extension(f"cogs.{cog.lower()}")

  @commands.command()
  async def reload(ctx, cog: str):
    await bot.reload_extension(f"cogs.{cog.lower()}")


#sintaks apps atau plas klik kanan
@bot.tree.context_menu(name="Show join date")
async def get_joined_date(interaction: discord.Interaction, member: discord.Member):
  await interaction.response.send_message(f"Member bergabung: {discord.utils.format_dt(member.joined_at)} ", ephemeral=True)

@bot.tree.context_menu(name="Report Messsage")
async def report_message(interaction: discord.Interaction, message: discord.Message):
  await interaction.response.send_message(f"Message reported ", ephemeral=True)

# @bot.tree.context_menu(name="Report Messsage")
# async def report_message(interaction: discord.Interaction, channel: discord.VoiceChannel):
#   await interaction.response.send_message(f"Message reported ", ephemeral=True)

@bot.tree.command()
@is_owner()
async def katakan2(interaction: discord.Interaction, text_to_send : str):
  """ hehe """
  await interaction.response.send_message(f"{text_to_send}", ephemeral=True)

# @say.error
# async def say_error(interaction: discord.Interaction, error):
#   await interaction.response.send_message("Not allowed", empheral=True)

@bot.tree.command()
@app_commands.describe(text_to_send="Tulul..")
@app_commands.rename(text_to_send="pesan")
async def katakan(interaction: discord.Interaction, text_to_send : str):
  await interaction.response.send_message(f"{text_to_send}", ephemeral=True)

#auto completion dekorasi
async def minum_autocompletion(
  interaction: discord.Interaction,
  current: str,
) -> typing.List[app_commands.Choice[str]]:
  data = []
  for minum_choice in ['beer', 'susu', 'teh', 'kopi']:
    if current.lower() in minum_choice.lower():
      data.append(app_commands.Choice(name-minum_choice, value=minum_choice))
  return data


@bot.tree.command()
@app_commands.autocomplete(choice=minum_autocompletion)
async def minum(interaction: discord.Interaction, choice: str):
  await interaction.response.send_message(f"{choice}", ephemeral=True)
  

@bot.tree.command()
async def makan(interaction: discord.Interaction, choice:Food):
  await interaction.response.send_message(f"{choice}", ephemeral=True)

#dekorasi command
@bot.tree.command()
@app_commands.choices(choice=[
  app_commands.Choice(name="red", value="1"),
  app_commands.Choice(name="blue", value="2"),
  app_commands.Choice(name="green", value="3"),
])
async def warna(interaction: discord.Interaction, choice:app_commands.Choice[str]):
  await interaction.response.send_message(f"{choice}", ephemeral=True)


@bot.event
#kirim pesan error jika argument kurang
async def on_command_error(ctx, error):
  if isinstance(error, commands.MissingRequiredArgument):
    await ctx.send("Terjadi error")


#perintah bot
@bot.hybrid_command(aliases=['p'],
                    help="this is help",
                    description="Deskripsi tentang",
                    brief="this is brief",
                    enabled=True,
                    hidden=True)
async def ping(ctx):
  """ Menjawab dengan pong """
  await ctx.send("pong")


@bot.tree.command(description="Welcome user", name="greetings4")
async def hallo2(interaction: discord.Interaction):
  """ Merespon """
  await interaction.response.send_message(
      f"Hallo juga {interaction.user.mention}", ephemeral=True)


@bot.command()
@is_owner()
async def say(ctx, user="Haa?"):
  """ Kosong """
  await ctx.send(user)


@say.error
async def say_error(ctx, error):
  if isinstance(error, NotOwner):
    await ctx.send("Permission denied")


@bot.command()
async def say2(ctx, *user):
  """ Kosong """
  await ctx.send(" ".join(user))


@bot.command()
async def say3(ctx, user="Haa?", kenapa="Whut??"):
  """ Kosong """
  await ctx.send(user, kenapa)


@bot.command()
async def dmsaya(ctx):
  await ctx.message.author.send("Haluuu")


#   user = discord.utils.get(bot.guilds[0].members, nick="Ranwiesiel")
#   if user:
#     await user.send("holla")


@bot.command()
async def Choices(ctx, *user):
  """ Kosong """
  await ctx.send(random.choice(user))


@bot.command()
async def joined(ctx, siapa: discord.Member):
  """ Kosong """
  await ctx.send(siapa.joined_at)


@bot.command()
async def tampar(ctx, alasan: Tampar(use_nicknames=True)):
  """ Kosong """
  await ctx.send(alasan)


# @joined.error kirim pesan error jika argument kurang
# async def add_error(ctx, error):
#   if isinstance(error, commands.MissingRequiredArgument):
#     await ctx.send("Terjadi error")

keep_alive()
bot.run(os.environ['TOKEN'], root_logger=True)
