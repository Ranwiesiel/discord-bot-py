from discord.ext import commands

@commands.group() #Sub grup command dari math
async def math(ctx):
  """ Kosong """
  if ctx.invoked_subcommand is None:
    await ctx.send(f"Tidak, {ctx.subcommand_passed} tidak ada dalam simple")
    
@math.command()
async def add(ctx, satu : int, dua : int):
  """ Kosong """
  await ctx.send(satu + dua)

# @bot.group() #Grup command
# async def math(ctx):
#   """ Kosong """
#   if ctx.invoked_subcommand is None:
#     await ctx.send(f"Tidak, {ctx.subcommand_passed} tidak ada dalam math")

# @math.group() #Sub grup command dari math
# async def simple(ctx):
#   """ Kosong """
#   if ctx.invoked_subcommand is None:
#     await ctx.send(f"Tidak, {ctx.subcommand_passed} tidak ada dalam simple")
    
# @simple.command()
# async def add(ctx, satu : int, dua : int):
#   """ Kosong """
#   await ctx.send(satu + dua)

async def setup(bot):
  bot.add_command(math)