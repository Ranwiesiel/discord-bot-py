import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio

# youtube player
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

class YTDLSource(discord.PCMVolumeTransformer):
    ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: cls.ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else cls.ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class YtStream(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # bot join and leave voice channel
    @commands.command(name='join', help='Tells the bot to join the voice channel')
    async def join(self, ctx: commands.Context):
        if not ctx.message.author.voice:
            await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
            return
        else:
            channel = ctx.message.author.voice.channel
        await channel.connect()

    @commands.command(name='leave', help='To make the bot leave the voice channel')
    async def leave(self, ctx: commands.Context):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()
        else:
            await ctx.send("The bot is not connected to a voice channel.")
            
    # bot play, pause, resume, stop song
    @commands.command(name='play', help='To play song')
    async def play(self, ctx: commands.Context, url):
        try:
            server = ctx.message.guild
            voice_channel = server.voice_client

            async with ctx.typing():
                try:
                    player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
                    voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
                except Exception as e:
                    await ctx.send('An error occurred while processing this request: {}'.format(str(e)))
                    return
            await ctx.send('**Now playing:** {}'.format(player.title))
        except Exception as e:
            await ctx.send("The bot is not connected to a voice channel: {}".format(str(e)))


    @commands.command(name='pause', help='This command pauses the song')
    async def pause(self, ctx: commands.Context):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.pause()
        else:
            await ctx.send("The bot is not playing anything at the moment.")
        
    @commands.command(name='resume', help='Resumes the song')
    async def resume(self, ctx: commands.Context):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            voice_client.resume()
        else:
            await ctx.send("The bot was not playing anything before this. Use play_song command")

    @commands.command(name='stop', help='Stops the song')
    async def stop(self, ctx: commands.Context):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
        else:
            await ctx.send("The bot is not playing anything at the moment.")

async def setup(bot):
    await bot.add_cog(YtStream(bot))
