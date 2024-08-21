import discord
from discord.ext import commands, tasks
import os, random
import settings
from dotenv import load_dotenv
import asyncio
from itertools import cycle
from motor.motor_asyncio import AsyncIOMotorClient as MotorClient

logger = settings.logging.getLogger("bot")
load_dotenv()


extensions = [
    "cogs.admin",
    "cogs.GeminiSimple",
    "cogs.greetings",
    "cogs.help",
    "cogs.leveling",
    "cogs.ping",
    "cogs.reddit",
    # "cogs.simpleMusic",
    "cogs.yt_stream",
    "cogs.MAL.result"
]


# Load the environment variables
token = os.getenv("TOKEN")
owner_id = os.getenv("OWNER_ID")

mongodb = {}
bot_status_types = {
    "playing":discord.ActivityType.playing,
    "listening":discord.ActivityType.listening,
    "watching": discord.ActivityType.watching,
    "streaming": discord.ActivityType.streaming
}

async def connect_database():
    client = MotorClient(os.getenv("MONGO"))
    database = client['Discord-Bot-Database']
    collections = database['General']
    mongodb['client'] = client
    mongodb['collections'] = collections
    mongodb['doc'] = await collections.find_one({"_id":"bot_prefixes"})
    mongodb['status'] = await collections.find_one({"_id":"bot_status"})



def get_prefix(bot,ctx):
    guildId = str(ctx.guild.id)
    if ctx.guild is None or guildId not in mongodb['doc']:
        # DM or guild prefixes not defined
        return commands.when_mentioned_or(*["$"])(bot,ctx)

    guild_prefixes = mongodb['doc'][guildId]
    if guildId in mongodb['doc']:
        return commands.when_mentioned_or(*guild_prefixes)(bot,ctx)

# Intents
intents = discord.Intents.all()
# The bot
bot = commands.Bot(command_prefix=get_prefix, intents = intents, owner_id = owner_id)


@tasks.loop(minutes=1)
async def auto_change_bot_status():
    status_type = random.choice(list(mongodb['status']['ranwbot'].keys()))
    status_message = random.choice(mongodb['status']['ranwbot'][status_type])
    await bot.change_presence(activity=discord.Activity(name=status_message,type=bot_status_types[status_type]))

@auto_change_bot_status.after_loop
async def after_auto_status_loop():
    auto_change_bot_status.change_interval(minutes=random.randint(15,540))

# Load cogs
# async def load_extensions():
#     for filename in os.listdir('./cogs'):
#         if filename.endswith('.py'):
#             await bot.load_extension(f'cogs.{filename[:-3]}')

# Events
@bot.event
async def setup_hook():
    await connect_database()

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    auto_change_bot_status.start()
    print(discord.__version__)
    await load_bot_extensions()
    try:
        synced_commands = await bot.tree.sync()
        print(f"Synced {len(synced_commands)} commands")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_guild_join(guild):
    if str(guild.id) not in mongodb['doc']:
        mongodb['doc'][str(guild.id)] = ["$"]
        await mongodb['collections'].update_one({'_id':'bot_prefixes'},{'$set':{str(guild.id):["$"]}})

@bot.command(name='view-prefixes')
async def view_prefixes(ctx):
    """
    View current prefixes the bot has for the server.
    {command_prefix}{command_name}
    """
    if str(ctx.guild.id) not in mongodb['doc']:
        return await ctx.send("$")
    return await ctx.send("**{}**".format('\n'.join(mongodb['doc'][str(ctx.guild.id)])))

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
    
# check user info
@bot.command()
async def whoareu(ctx):
    text = "I am a bot created by a human named <@592585000663121930> and I am here to help you."
    await ctx.send(text)

async def load_bot_extensions():
    for ext in extensions:
        await bot.load_extension(ext)

# Run the bot

async def main():
    async with bot:
        # await load_extensions()
        await bot.start(token)

asyncio.run(main())