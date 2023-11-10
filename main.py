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
import utilities, run_local, nasa, plex, dungeons

run_local.setEnvars()

bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

nasa = discord.SlashCommandGroup("nasa", "Cool NASA Things")

### Nasa Slash Command
@bot.slash_command(name="nasa")
@tracer.wrap(service="discord-bot", resource="nasa-slash-command")
async def nasa_command(
  ctx: discord.ApplicationContext,
  nasa_function: discord.Option(str, choices=["Near Earth Objects", "Astronomy Picture of the Day"]),
):
  span = tracer.current_span()
  await ctx.defer()
  logging.info("Received NASA slash command")
  span.set_tag('function', nasa_function)
  try:
    if nasa_function == "Near Earth Objects":
      neo_data = nasa.nasa_neo(os.environ["NASA_KEY"])
      await ctx.respond(f"Here's a near Earth object recorded today: \n {neo_data[random.randint(0, len(neo_data))]}")
      logging.info("Reply sent!")
    elif nasa_function == "Astronomy Picture of the Day":
      apod_data = nasa.nasa_apod(os.environ["NASA_KEY"])
      await ctx.respond(f"Astronomy Picture of the Day:\n {apod_data['title']} - {apod_data['date']}\n{apod_data['explanation']}\n{apod_data['hdurl']}")
      logging.info("Reply sent!")
    else: 
      pass
  except:
    await ctx.respond("We were unable to complete your request, please try again...")


### Plex Slash Command
@bot.slash_command(name="plex")
@tracer.wrap(service="discord-bot", resource="plex-slash-command")
async def plex_command(
  ctx: discord.ApplicationContext,
  library: discord.Option(str, choices=["Movies", "TV Shows"]),
  search_query: discord.Option(str)
):
  span = tracer.current_span()
  await ctx.defer()
  
  try:
    logging.info("Received Plex slash command")
    if library == "Movies":
      library_choice = "movies"
    elif library == "TV Shows":
      library_choice = "tv"
    else: 
      pass
    span.set_tag('library', library_choice)

    title, year, poster, tagline, rating, summary, content_rating = plex.plex_search(search_query, library_choice ,os.environ["PLEX_TOKEN"])

    span.set_tag('title', title)

    if content_rating in ['R', 'NC-17', 'TV-MA']:
      bubbleColor = discord.Colour.orange()
    elif content_rating in ['PG-13', 'TV-14']:
      bubbleColor = discord.Colour.yellow()
    elif content_rating in ['PG', 'TV-PG', 'G', 'TV-G']:
      bubbleColor = discord.Colour.green()
    else:
      bubbleColor = discord.Colour.gold()
      
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

    utilities.save_image(poster, imageName)

    file = discord.File(imageName, filename=imageName)
    embed.set_image(url=f"attachment://{imageName}")
    await ctx.respond(embed=embed, file=file)
    logging.info("Reply sent!")

    utilities.delete_saved_image(imageName)
  except:
    await ctx.respond("We were unable to complete your request, please try again...")

### DnD slack Commands
dnd = discord.SlashCommandGroup("dnd", "Roll Initiate!")

## dice roll
@dnd.command(name="roll_dice") # Create a slash command
async def roll_dice(
  ctx: discord.ApplicationContext,
  sides: discord.Option(str, "What kind of dice?", choices=["D4", "D6", "D8", "D10", "D12", "D20"]),
  dice_count: discord.Option(int, "How many dice?"),
  bonus: discord.Option(int, "Any Bonus to add?", min_value=0, max_value = 20, default=0)
):
  roll = dungeons.roll_dice(int(dice_count), sides, bonus)
  await ctx.respond(roll)

## saving throw
@dnd.command(name="saving_throw") # Create a slash command
async def saving_throw(
  ctx: discord.ApplicationContext,
  advantage: discord.Option(str, "Any Advantage or Disadvantage", choices=["Advantage", "Disadvantage", "None"]),
  bonus: discord.Option(int, "Any Bonus to add?", min_value=0, max_value = 20, default=0)
):
  roll = dungeons.saving_throw(bonus, advantage)
  await ctx.respond(roll)

## dnd lookup
top_level_choices = ["ability-scores", "alignments", "classes", "conditions", "damage-types", "equipment", "equipment-categories", "feats", "features", "languages", "magic-items", "magic-schools", "monsters", "proficiencies", "races", "rule-sections", "rules", "skills", "spells", "subclasses", "subraces", "traits", "weapon-properties"]

async def get_sub_category(ctx: discord.AutocompleteContext):
  category = ctx.options['category']
  values = dungeons.dnd_lookup(category)
  options = []
  for i in values["results"]:
    options.append(i['index'])
  return options


@dnd.command(name="lookup")
@tracer.wrap(service="discord-bot", resource="dnd-lookup-slash-command")
async def dnd_lookup(
  ctx: discord.ApplicationContext,
  category: discord.Option(str, choices=top_level_choices),
  sub_category: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_sub_category))
):
  span = tracer.current_span()
  await ctx.defer()
  endpoint = category + "/" + sub_category
  values = dungeons.dnd_lookup(endpoint)

  await ctx.respond(values)

class MyView(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
    @discord.ui.button(label="Click me!", style=discord.ButtonStyle.primary, emoji="😎") # Create a button with the label "😎 Click me!" with color Blurple
    async def button_callback(self, button, interaction):
        await interaction.response.send_message("You clicked the button!") # Send a message when the button is clicked

@dnd.command(name="button") # Create a slash command
async def button(ctx):
    await ctx.respond("This is a button!", view=MyView()) # Send a message with our View class that contains the button

bot.add_application_command(dnd)

# testing = discord.SlashCommandGroup("testing", "testing things here")

# @testing.command(description="Sends the bot's latency.") # this decorator makes a slash command
# async def ping(ctx): # a slash command will be created with the name "ping"
#     await ctx.respond(f"Pong! Latency is {bot.latency}")


# class MyView(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
#     @discord.ui.button(label="Click me!", style=discord.ButtonStyle.primary, emoji="😎") # Create a button with the label "😎 Click me!" with color Blurple
#     async def button_callback(self, button, interaction):
#         await interaction.response.send_message("You clicked the button!") # Send a message when the button is clicked

# @testing.command(name="button") # Create a slash command
# async def button(ctx):
#     await ctx.respond("This is a button!", view=MyView()) # Send a message with our View class that contains the button

# bot.add_application_command(testing)

bot.run(os.environ["DISCORD_TOKEN"])
