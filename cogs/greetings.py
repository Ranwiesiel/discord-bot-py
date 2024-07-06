import discord
from discord.ext import commands
import os
import easy_pil
import random

class Greetings(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #setiap kali member masuk server
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        
        channel = member.guild.system_channel
        images = [image for image in os.listdir("./cogs/welcome_images")]
        random_image = random.choice(images)

        bg = easy_pil.Editor(f"./cogs/welcome_images/{random_image}").resize((1920, 1080))
        avatar_image = await easy_pil.load_image_async(str(member.avatar.url))
        avatar = easy_pil.Editor(avatar_image).resize((250, 250)).circle_image()

        font_big = easy_pil.Font.poppins(size=90, variant="bold")
        font_small = easy_pil.Font.poppins(size=60, variant="bold")

        bg.paste(avatar, (835, 340))
        bg.ellipse((835, 340), 250, 250, outline="white", stroke_width=5)

        bg.text((960, 620), f"Welcome to {member.guild.name}!", font=font_big, color="black", align="center")
        bg.text((960, 720), f"{member.name}#{member.discriminator}", font=font_small, color="black", align="center")

        img_file = discord.File(fp=bg.image_bytes, filename=random_image)

        await channel.send(f"Selamat datang {member.mention}!")
        await channel.send(file=img_file)

        # if channel is not None:
        #     await channel.send(f'Welcome {member.mention}.')

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