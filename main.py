from ddtrace import patch; patch(logging=True)
import logging
from ddtrace import tracer

FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
          '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
          '- %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger(__name__)
log.level = logging.INFO

import discord, os, time, random, requests, slugify
import extra_functions, run_local

# run_local.setEnvars()

bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")


## Nasa Slash Command
@bot.slash_command(name="nasa")
@tracer.wrap(service="discord-bot", resource="nasa-slash-command")
async def nasa_command(
  ctx: discord.ApplicationContext,
  nasa_function: discord.Option(str, choices=["Near Earth Objects", "Astronomy Picture of the Day"]),
):
  span = tracer.current_span()
  logging.info("Received NASA slash command")
  span.set_tag('function', nasa_function)
  if nasa_function == "Near Earth Objects":
    neo_data = extra_functions.nasa_neo(os.environ["NASA_KEY"])
    await ctx.defer()
    await ctx.respond(f"Here's a near Earth object recorded today: \n {neo_data[random.randint(0, len(neo_data))]}")
    logging.info("Reply sent!")
  elif nasa_function == "Astronomy Picture of the Day":
    apod_data = extra_functions.nasa_apod(os.environ["NASA_KEY"])
    await ctx.respond(f"Astronomy Picture of the Day:\n {apod_data['title']} - {apod_data['date']}\n{apod_data['explanation']}\n{apod_data['hdurl']}")
    logging.info("Reply sent!")
  else: 
    pass


## Plex Slash Command
@bot.slash_command(name="plex")
@tracer.wrap(service="discord-bot", resource="plex-slash-command")
async def plex_command(
  ctx: discord.ApplicationContext,
  library: discord.Option(str, choices=["Movies", "TV Shows"]),
  search_query: discord.Option(str)
):
  span = tracer.current_span()
  logging.info("Received Plex slash command")
  if library == "Movies":
    library_choice = "movies"
  elif library == "TV Shows":
    library_choice = "tv"
  else: 
    pass
  span.set_tag('library', library_choice)

  title, year, poster, tagline, rating, summary, content_rating = extra_functions.plex_search(search_query, library_choice ,os.environ["PLEX_TOKEN"])

  span.set_tag('title', title)

  if content_rating in ['R', 'NC-17', 'TV-MA']:
    bubbleColor = discord.Colour.orange()
  elif content_rating in ['PG-13', 'TV-14']:
    bubbleColor = discord.Colour.yellow()
  elif content_rating in ['PG', 'TV-PG', 'G', 'TV-G']:
    bubbleColor = discord.Colour.green()
  else:
    bubbleColor = discord.Colour.gold()
    
  await ctx.defer()
  embed = discord.Embed(
        title = f'{title}' ,
        description = f'{tagline}',
        color=bubbleColor, # Pycord provides a class with default colors you can choose from
    )
  embed.add_field(name="Year:", value=year, inline=True)
  embed.add_field(name="Rating:", value=rating, inline=True)
  embed.add_field(name="Content Rating:", value=content_rating, inline=True)
  embed.add_field(name="Summary:", value=summary)

  embed.set_footer(text="plex.phantomsloth.io") # footers can have icons too
  embed.set_author(name="Plex @ Phantomsloth.io", icon_url="https://phantomsloth.io/images/phantomsloth_logo.png")
  embed.set_thumbnail(url="https://static-00.iconduck.com/assets.00/plex-new-icon-512x512-k93c4jua.png")
  imageName = f'{str(slugify.slugify(title))}.png'
  logging.info("Requesting and saving plex poster")

  extra_functions.save_image(poster, imageName)

  file = discord.File(imageName, filename=imageName)
  embed.set_image(url=f"attachment://{imageName}")
  await ctx.respond(embed=embed, file=file)
  logging.info("Reply sent!")

  extra_functions.delete_saved_image(imageName)


bot.run(os.environ["DISCORD_TOKEN"])
