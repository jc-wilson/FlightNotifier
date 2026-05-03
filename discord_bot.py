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
    if not interaction.response.is_done():
        await interaction.response.send_message("Checking flights...")

    await track_flights(interaction, coords)


@bot.tree.command(name="start_tracker", description="starts tracking flights and pings user whenever a flight is about to come overhead")
async def start_tracker(interaction: discord.Interaction, coords: str):
    global tracking
    tracking = True
    await interaction.response.send_message(f"Tracking started for following coordinates: {coords}")
    await track_flights(interaction, coords)

@bot.tree.command(name="ends_tracker", description="ends flight tracking")
async def end_tracker(interaction: discord.Interaction):
    global tracking
    tracking = False
    await interaction.response.send_message("Tracking ended")

async def track_flights(interaction: discord.Interaction, coords: str):
    while tracking:
        embed = discord.Embed(title="Flight information:")
        comma_pos = coords.find(",")
        coords_x = float(coords[:comma_pos])
        coords_y = float(coords[comma_pos + 2:])
        flights_info = flights.check_flights(coords_x, coords_y)

        if flights_info:
            embed.add_field(name="Flight: ", value=flights_info["callsign"], inline=False)
            embed.add_field(name="Aircraft: ", value=f"{flights_info['type']} / {flights_info['registration']}", inline=False)
            embed.add_field(name="Altitude: ", value=f"{flights_info['altitude']} ft", inline=False)
            embed.add_field(name="Speed: ", value=f"{flights_info['knots']} knots", inline=False)
        else:
            embed.add_field(name="Error", value="No Flights Found", inline=False)

        await interaction.followup.send("@bai13l", embed=embed)
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