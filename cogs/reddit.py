import discord
from discord.ext import commands
from random import choice
import asyncpraw as praw
from dotenv import load_dotenv
import os

load_dotenv()

class Reddit(commands.Cog):
    """
    Share memes from Reddit
    """

    COG_EMOJI = "🤡"

    def __init__(self, bot):
        self.bot = bot
        self.reddit = praw.Reddit(client_id=os.getenv('CLIENT_ID_REDDIT'), client_secret=os.getenv('CLIENT_SECRET_REDDIT'), user_agent="script:randomeme:v1.0 (by u/Ranwiesiel)")
        

    @commands.command(name="meme", aliases=["memes"])
    async def meme(self, ctx: commands.Context):

        subreddit = await self.reddit.subreddit("memes")
        post_list = []

        async for post in subreddit.hot(limit=30):
            if not post.over_18 and post.author is not None and any(post.url.endswith(ext) for ext in ["jpg", "jpeg", "png", "gif"]):
                author_name = post.author.name
                caption = post.title
                post_list.append((post.url, author_name, caption))
            elif post.author is None:
                post_list.append((post.url, "Unknown"))

        if post_list:

            random_post = choice(post_list)

            meme_embed = discord.Embed(
                title="Random Meme",
                description=f"{random_post[2]}",
                color=discord.Color.random()
            )
            meme_embed.set_author(name=f"Meme dari {ctx.author.name}", icon_url=ctx.author.avatar)
            meme_embed.set_image(url=random_post[0])
            meme_embed.set_footer(text=f"👤 Post created by {random_post[1]}.", icon_url=None)
            await ctx.send(embed=meme_embed)

        else:
            await ctx.send("Tidak ada meme yang bisa diambil.")

    def cog_unload(self):
        self.bot.loop.create_task(self.reddit.close())

async def setup(bot):
    await bot.add_cog(Reddit(bot))