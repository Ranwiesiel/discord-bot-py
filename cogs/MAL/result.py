import discord
from discord.ext import commands
from discord.ext.commands import MissingRequiredArgument
from cogs.MAL.getJson import jikanJson
import asyncio

class Precheck(commands.Cog):
	def results(self, data, name, query, type):

		"""To get all the matching results of the requested query."""

		result_list = [f'{str(n + 1)}.   {data[n][name]}' for n in range(0,len(data))]
		pre_message = f'`{len(data)}` {type} found matching `{query}`!'
		post_message = 'Please type the number corresponding to your selection, or type `c` now to cancel.'

		message = '\n '.join(result_list)
		output = f'{pre_message}\n \n```md\n {message}\n```\n {post_message}'
		return output

	def getName(self, name):
		name = name.replace(' ','%20')
		return name

	async def selection(self,ctx,message,data_len,type):

		"""A function that allows users to select the desired name from the matching results."""

		def check(m):
			return m.author == ctx.author and m.channel == ctx.channel

		while True:
			try:
				msg = await self.wait_for('message',check=check,timeout=20)
			except asyncio.TimeoutError:
				await message.delete()
				await ctx.send("Sorry, you didn't reply in time!")
				return None

			if msg.content.isdigit():
				if int(msg.content) in [*range(1,data_len+1)]:
					await message.delete()
					await msg.delete()
					return int(msg.content)
				else:
					continue
			elif msg.content.lower() == 'c':
				await message.delete()
				await msg.delete()
				await ctx.send(f'{ctx.author.name} cancelled the {type} selection.')
				return None
			else:
				continue

class MyAnimeList(commands.Cog):
	"""
	Search for anime and manga via MyAnimeList.
	"""

	COG_EMOJI = "🌸"

	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.command(name='anime')
	async def anime(self,ctx,*,name):
		"""
		Gives information about any anime via [MyAnimeList](https://myanimelist.net/).

		**Usage:**
		`prefix anime Naruto`
		"""
		if ctx.guild:
			pass
		else:
			return
		async with ctx.typing():
			query = Precheck.getName(self, name)
			url = f'https://api.jikan.moe/v4/anime?q={query}&order_by=members&sort=desc&page=1'
			search_result = jikanJson(url)
			data = search_result['data']
			data_len = len(search_result['data'])
		if data_len == 1:
			n = 0
		elif data_len == 0:
			await ctx.send('No results for query.')
			return
		
		else:
			output = Precheck.results(self, data,'title',name,'animes')
			output_message = await ctx.send(output)
			selection_result = await Precheck.selection(self.bot ,ctx, output_message, data_len, 'anime')
			if selection_result:
				n = selection_result - 1
			else:
				return
			
		search = search_result["data"][n]
		embed=discord.Embed(title=search["title"], url=search["url"] , description=search['synopsis'], color=0xf37a12)
		embed.set_thumbnail(url=search["images"]['jpg']['image_url'])
		embed.add_field(name="Score", value=search["score"], inline=True)
		embed.add_field(name="Members", value=search["members"], inline=True)

		if search["aired"]["from"] is None:
			embed.add_field(name="Start Date", value='Unknown', inline=True)
		else:
			embed.add_field(name="Start Date", value=search["aired"]["from"][:-15], inline=True)
		if search["aired"]["to"] is None:
			embed.add_field(name="End Date", value="Unknown", inline=True)
		else:
			embed.add_field(name="End Date", value=search["aired"]["to"][:-15], inline=True)

		embed.add_field(name="Total Episodes", value=search["episodes"], inline=True)
		embed.add_field(name="Type", value=search["type"], inline=True)
		genre = search['genres']
		c = []

		for length in range(0,len(genre)):
			c.append(genre[length]['name'])

		string = ', '.join([str(item) for item in c])
		genres = string
		embed.add_field(name="Genres", value=genres, inline=False)
		print('No selection made.')
		await ctx.send(embed=embed)

	@anime.error
	async def anime_error(self,ctx,error):
		if isinstance(error,(MissingRequiredArgument)):
			if ctx.guild:
				await ctx.send('Please provide a query.')
		else:
			return


	@commands.command(name='manga')
	async def manga(self,ctx,*,name):
		"""
		Gives information about any manga via [MyAnimeList](https://myanimelist.net/).

		**Usage:**
		`prefix manga Naruto`
		"""
		if ctx.guild:
			pass
		else:
			return

		query = Precheck.getName(self, name)
		url = f'https://api.jikan.moe/v4/manga?q={query}&order_by=members&sort=desc&page=1'
		search_result = jikanJson(url)

		data = search_result['data']
		data_len = len(search_result['data'])
		if data_len == 1:
			n = 0
		elif data_len == 0:
			await ctx.send('No results for query.')
			return
		else:
			output = Precheck.results(self, data,'title',name,'mangas')
			output_message = await ctx.send(output)
			selection_result = await Precheck.selection(self.bot ,ctx ,output_message ,data_len, 'manga')
		if selection_result:
			n = selection_result - 1
		else:
			return

		search = search_result["data"][n]
		embed=discord.Embed(title=search["title"], url=search["url"] , description=search['synopsis'], color=0xf37a12)
		embed.set_thumbnail(url=search["images"]['jpg']['image_url'])

		embed.add_field(name="Score", value=search["scored"], inline=True)

		embed.add_field(name="Members", value=search["members"], inline=True)

		if search["published"]["from"] is None:
			embed.add_field(name="Start Date", value='Unknown', inline=True)
		else:
			embed.add_field(name="Start Date", value=search["published"]["from"][:-15], inline=True)

		if search["published"]["to"] is None:
			embed.add_field(name="End Date", value="Unknown", inline=True)
		else:
			embed.add_field(name="End Date", value=search["published"]["to"][:-15], inline=True)

		embed.add_field(name="Total Chapters", value=search["chapters"], inline=True)
		embed.add_field(name="Type", value=search["type"], inline=True)
		genre = search['genres']
		c = []
		for length in range(0,len(genre)):
			c.append(genre[length]['name'])
		string = ', '.join([str(item) for item in c])
		genres = string

		embed.add_field(name="Genres", value=genres, inline=False)

		await ctx.send(embed=embed)

	@manga.error
	async def manga_error(self,ctx,error):
		if isinstance(error,(MissingRequiredArgument)):
			if ctx.guild:
				await ctx.send('Please provide a query.')
		else:
			return


async def setup(bot):
  await bot.add_cog(MyAnimeList(bot))