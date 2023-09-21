import discord, os, time, random, requests
import extra_functions, main_tests


# main_tests.setEnvars()

bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.slash_command(name="nasa")
async def nasa_command(
  ctx: discord.ApplicationContext,
  nasa_function: discord.Option(str, choices=["Near Earth Objects", "Astronomy Picture of the Day"]),
  # nasa_results: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_nasa_function))
):
  if nasa_function == "Near Earth Objects":
    neo_data = extra_functions.nasa_neo(os.environ["NASA_KEY"])
    await ctx.defer()
    await ctx.respond(f"Here's a near Earth object recorded today: \n {neo_data[random.randint(0, len(neo_data))]}")
  elif nasa_function == "Astronomy Picture of the Day":
    apod_data = extra_functions.nasa_apod(os.environ["NASA_KEY"])
    await ctx.respond(f"Astronomy Picture of the Day:\n {apod_data['title']} - {apod_data['date']}\n{apod_data['explanation']}\n{apod_data['hdurl']}")
  else: 
    pass

@bot.slash_command(name="plex")
async def plex_command(
  ctx: discord.ApplicationContext,
  library: discord.Option(str, choices=["Movies", "TV Shows"]),
  search_query: discord.Option(str)
):
  if library == "Movies":
    library_choice = 0
  elif library == "TV Shows":
    library_choice = 1
  else: 
    pass
  title, poster, tagline, rating, summary, content_rating = extra_functions.plex_search(search_query, library_choice ,os.environ["PLEX_TOKEN"])

  
  await ctx.defer()
  embed = discord.Embed(
        title = title,
        description = tagline,
        color=discord.Colour.blurple(), # Pycord provides a class with default colors you can choose from
    )
  embed.add_field(name="Summary:", value=summary)
  embed.add_field(name="Rating:", value=rating)
  embed.add_field(name="Content Rating:", value=content_rating)
  embed.set_footer(text="Plex, Courtesy of Phantomsloth.io") # footers can have icons too
  embed.set_author(name="Plex @ Phantomsloth.io", icon_url="https://phantomsloth.io/images/phantomsloth_logo.png")
  embed.set_thumbnail(url="https://static-00.iconduck.com/assets.00/plex-new-icon-512x512-k93c4jua.png")
  url = poster
  imageName = f"{title.lower().replace(' ', '_')}.png"
  response = requests.get(url)
  with open('tmp.png', 'wb') as f:
    f.write(response.content)
  file = discord.File("tmp.png", filename=imageName)
  embed.set_image(url=f"attachment://{imageName}")
  await ctx.respond(embed=embed, file=file)
  
  os.remove('tmp.png')



bot.run(os.environ["DISCORD_TOKEN"])
