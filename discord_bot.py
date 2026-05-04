import os
import discord
import asyncio
import flights
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
SERVER_ID = int(os.getenv("SERVER_ID"))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

tracking = False

@bot.tree.command(name="flight_checker", description="show flights in air around chosen location")
@app_commands.describe(coords="input coordinates")
async def flight_checker(interaction: discord.Interaction, coords: str):
    await interaction.response.defer(thinking=False)

    embed = build_flight_embed(coords)
    if embed is not None:
        await interaction.followup.send(interaction.user.mention, embed=embed)


@bot.tree.command(name="start_tracker", description="starts tracking flights and pings user whenever a flight is about to come overhead")
async def start_tracker(interaction: discord.Interaction, coords: str):
    global tracking
    tracking = True
    await interaction.response.send_message(f"Tracking started for following coordinates: {coords}")
    bot.loop.create_task(track_flights(interaction.channel, coords, interaction.user.mention))

@bot.tree.command(name="ends_tracker", description="ends flight tracking")
async def end_tracker(interaction: discord.Interaction):
    global tracking
    tracking = False
    await interaction.response.send_message("Tracking ended")

def build_flight_embed(coords: str):
    parts = coords.split(",")
    coords_x = float(parts[0])
    coords_y = float(parts[1])
    radius = float(parts[2])
    flights_info = flights.check_flights(coords_x, coords_y, radius)

    if not flights_info:
        return None

    embed = discord.Embed(title=f"{len(flights_info)} flight(s) nearby")

    for flight in flights_info[:10]:
        embed.add_field(
            name=flight["callsign"],
            value=(
                f"Aircraft: {flight['type']} / {flight['registration']}\n"
                f"Altitude: {flight['altitude']} ft\n"
                f"Speed: {flight['knots']} knots"
            ),
            inline=False,
        )
    return embed


async def track_flights(channel: discord.abc.Messageable, coords: str, user_mention: str):
    while tracking:
        embed = build_flight_embed(coords)
        if embed is not None:
            await channel.send(user_mention, embed=embed)
        await asyncio.sleep(180)



@bot.event
async def setup_hook():
    bot.tree.copy_global_to(guild=discord.Object(id=SERVER_ID))
    await bot.tree.sync(guild=discord.Object(id=SERVER_ID))

@bot.event
async def on_ready():
    print(f"logged in as {bot.user}")
    print("Syncing to:", SERVER_ID)
    print([cmd.name for cmd in await bot.tree.fetch_commands(guild=discord.Object(id=SERVER_ID))])



bot.run(TOKEN)
