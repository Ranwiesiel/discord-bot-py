import discord
from discord.ext import commands,tasks
import json
import os
import settings
from dotenv import load_dotenv
import asyncio
import yt_dlp as youtube_dl

logger = settings.logging.getLogger("bot")

load_dotenv()

# Load the environment variables
token = os.getenv("TOKEN")
prefix = os.getenv("PREFIX")
owner_id = os.getenv("OWNER_ID")

class Greetings(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self._last_member = None

# Intents
intents = discord.Intents.all()
# The bot
client = discord.Client(intents=intents)
bot = commands.Bot(prefix, intents = intents, owner_id = owner_id)

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
	print(discord.__version__)
	await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name =f"{bot.command_prefix}help"))

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
    text = "I am a bot created by a human named " + str(bot.owner_id) + " and I am here to help you."
    await ctx.send(text)

# youtbe player
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

# bot join and leave voice channel
@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")
        
# bot play, pause, resume, stop song
@bot.command(name='play_song', help='To play song')
async def play(ctx,url):
    try :
        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            try:
                filename = await YTDLSource.from_url(url, loop=bot.loop)
                voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))
            except Exception as e:
                await ctx.send('An error occurred while processing this request: {}'.format(str(e)))
                return
        await ctx.send('**Now playing:** {}'.format(filename))
    except:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")
    
@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play_song command")

@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")

# Run the bot
async def main():
    async with bot:
        await load_extensions()
        await bot.start(token)

asyncio.run(main())