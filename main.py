import discord
from discord.ext import commands, tasks
import json
import os
import settings
from dotenv import load_dotenv
import asyncio
from itertools import cycle

logger = settings.logging.getLogger("bot")

load_dotenv()

# Load the environment variables
token = os.getenv("TOKEN")
prefix = os.getenv("PREFIX")
owner_id = os.getenv("OWNER_ID")

# Intents
intents = discord.Intents.all()
# The bot
client = discord.Client(intents=intents)
bot = commands.Bot(prefix, intents = intents, owner_id = owner_id)

bot_status = cycle(["$help", "Proses Maintenance", "RonggoW Jemlek", "Server Macam Apa Ini?!", "Aduhaii"])

@tasks.loop(seconds=5)
async def change_status():
    await bot.change_presence(activity=discord.Game(next(bot_status)))

# Load cogs
async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

    for filename in os.listdir('./cmds'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cmds.{filename[:-3]}')
            
    for filename in os.listdir('./slashcmds'):
        if filename.endswith('.py'):
            await bot.load_extension(f'slashcmds.{filename[:-3]}')

# Events
@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    change_status.start()
    print(discord.__version__)
    # await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name =f"{bot.command_prefix}help"))
    try:
        synced_commands = await bot.tree.sync()
        print(f"Synced {len(synced_commands)} commands")
    except Exception as e:
        print(f"Failed to sync commands: {e}")


@bot.tree.command(name="hello", description="Say hello to the bot")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello! {interaction.user.mention}") #, ephemeral=True
    

# shutdown command
@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    exit()

# check server info
@bot.command(help = "Prints details of Server")
async def where_am_i(ctx):
    owner=str(ctx.guild.owner)
    guild_id = str(ctx.guild.id)
    memberCount = str(ctx.guild.member_count)
    # icon = str(ctx.guild.icon_url)
    desc=ctx.guild.description
    
    embed = discord.Embed(
        title=ctx.guild.name + " Server Information",
        description=desc,
        color=discord.Color.blue()
    )
    # embed.set_author(name=ctx.guild.name, icon_url=ctx.author.avatar)
    # embed.set_thumbnail(url=icon)
    # embed.set_image(url=ctx.guild.icon_url)
    embed.add_field(name="Owner", value=owner, inline=True)
    embed.add_field(name="Server ID", value=guild_id, inline=True)
    embed.add_field(name="Member Count", value=memberCount, inline=True)
    embed.set_footer(text="Server created at" + str(ctx.guild.created_at))

    await ctx.send(embed=embed)

# check user latency
# @bot.command()
# async def ping(ctx):
#     ping_embed = discord.Embed(
#         title = "Pong!",
#         description = f'Latency in ms',
#         color = discord.Color.blue()
#     )
#     ping_embed.add_field(f'Pong! {round(bot.latency * 1000)}ms')
#     ping_embed.set_footer(text=f'Requested by {ctx.author}')
#     await ctx.send(embed=ping_embed)
    
# check user info
@bot.command()
async def tell_me_about_yourself(ctx):
    text = "I am a bot created by a human named " + str(ctx.message.author.mention) + " and I am here to help you."
    await ctx.send(text)

# Run the bot
async def main():
    async with bot:
        await load_extensions()
        await bot.start(token)

asyncio.run(main())