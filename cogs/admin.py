import discord
from discord.ext import commands
import os

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

class Admin(commands.Cog):
    """
    Admin commands only for the bot owner
    """
    def __init__(self, bot):
        self.bot = bot
    
    def is_owner():
        async def predicate(ctx):
            return ctx.author.id == 592585000663121930
        return commands.check(predicate)

    @commands.hybrid_command(name='cog', description='Load, Unload, and Reloads a module.', usage='[action] [path]')
    @is_owner()
    async def cog(self, ctx, action, path: str=None):
        folders = [filename for filename in os.listdir('cogs') if os.path.isdir(f'cogs/{filename}')]
        """Load, Unload, and Reloads a module."""

        if path:
            if path.endswith('.py'):
                path = path[:-3]
            path = path.split('/')

            if path[0] in folders:
                cog_names = []
                for filename in os.listdir(f'cogs/{path[0]}'):
                    if filename.endswith('.py'):
                        cog_names.append(filename[:-3])

                if path[1] in cog_names:
                    cog_file = f"cogs.{path[0]}.{path[1]}"
                    if action == 'reload':
                        await self.bot.unload_extension(cog_file)
                        await self.bot.load_extension(cog_file)
                        await ctx.send(f"Reloaded {cog_file}")
                    elif action == 'load':
                        await self.bot.load_extension(cog_file)
                        await ctx.send(f"Loaded {cog_file}")
                    elif action == 'unload':
                        await self.bot.unload_extension(cog_file)
                        await ctx.send(f"Unloaded {cog_file}")
                    else:
                        await ctx.send("Invalid action")
                else:
                    await ctx.send("Invalid cog name ", path[1])
            else:
                await ctx.send("Invalid folder name ", path[0])
        else:
            if action == 'reload':
                counter = 0
                for ext in extensions:
                # for filename in os.listdir('cogs'):
                #     if filename.endswith('.py'):
                        counter += 1
                        # cog_file = f"cogs.{filename[:-3]}"
                        await self.bot.unload_extension(ext)
                        await self.bot.load_extension(ext)
                await ctx.send(f"Reloaded {counter} cogs")
            elif action == 'load' or action == 'unload':
                await ctx.send("Please provide a path")
            else:
                await ctx.send("use folder/cog_name or cog_name")


async def setup(bot):
    await bot.add_cog(Admin(bot))