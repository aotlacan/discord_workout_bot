import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import json
import atexit
from discord import Embed
from datetime import datetime


DATA_FILE = "gym_data.json"

# Load saved data at startup
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

# Save current data to file
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(gym_minutes, f)

gym_minutes = load_data()
atexit.register(save_data)

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix='!', intents=intents, log_handler=handler, log_level=logging.DEBUG)

def has_gym_role(member):
    return any(role.name.lower() == "gym" for role in member.roles)

@bot.command()
async def leavegym(ctx):
    role = discord.utils.get(ctx.guild.roles, name="gym")
    if not role:
        await ctx.send("No role named 'gym' found.")
        return
    if role in ctx.author.roles:
        await ctx.author.remove_roles(role)
        await ctx.send(f"{ctx.author.mention}, the gym role has been removed.")
    else:
        await ctx.send("You don't have the gym role.")

@bot.command()
async def log(ctx, minutes: int):
    if not has_gym_role(ctx.author):
        await ctx.send("You need the gym role to log minutes.", delete_after=5)
        await ctx.message.delete(delay=3)
        return

    if minutes <= 0 or minutes > 1440:
        await ctx.send("Please enter a valid number of minutes (1–1440).", delete_after=5)
        await ctx.message.delete(delay=3)
        return

    user_id = str(ctx.author.id)
    gym_minutes[user_id] = gym_minutes.get(user_id, 0) + minutes
    save_data()

    await ctx.send(f"{ctx.author.mention} logged {minutes} minutes. Total: {gym_minutes[user_id]}", delete_after=5)
    await ctx.message.delete(delay=3)

@bot.command()
async def total(ctx):
    if not has_gym_role(ctx.author):
        msg = await ctx.send("You need the gym role to view your stats.")
        await ctx.message.delete(delay=5)
        await msg.delete(delay=7)
        return

    user_id = str(ctx.author.id)
    total = gym_minutes.get(user_id, 0)
    msg = await ctx.send(f"{ctx.author.mention}, you have logged {total} total minutes.")
    await ctx.message.delete(delay=5)
    await msg.delete(delay=5)

@bot.command()
async def top(ctx):
    if not has_gym_role(ctx.author):
        msg = await ctx.send("You need the gym role to view the leaderboard.")
        await ctx.message.delete(delay=5)
        await msg.delete(delay=7)
        return

    if not gym_minutes:
        msg = await ctx.send("No one has logged minutes yet.")
        await ctx.message.delete(delay=5)
        await msg.delete(delay=7)
        return

    sorted_data = sorted(gym_minutes.items(), key=lambda x: x[1], reverse=True)[:5]

    embed = Embed(
        title="🏋️ Gym Leaderboard",
        description="Top 5 gym grinders ranked by total minutes logged.",
        color=0xe74c3c  # Red left stripe like your image
    )

    embed.set_author(
        name="GymBot Tracker",
        icon_url="https://cdn-icons-png.flaticon.com/512/2331/2331970.png"  # Replace with your icon if needed
    )

    for i, (user_id, minutes) in enumerate(sorted_data, start=1):
        user = await bot.fetch_user(user_id)
        medal = ["🥇", "🥈", "🥉", "🍎", "💩"][i - 1]  # Emoji per rank
        embed.add_field(
            name=f"#{i} {medal} {user.display_name}",
            value=f"**{minutes}** minutes logged",
            inline=False
        )

    embed.set_footer(text=f"Last updated: {datetime.now().strftime('%d %B %Y at %H:%M:%S')}")

    msg = await ctx.send(embed=embed)
    await ctx.message.delete(delay=5)
    await msg.delete(delay=15)
 
@bot.command()
async def how(ctx):
    message = await ctx.send(
        "**Gym Bot Commands:**\n"
        "`!leavegym` – remove the gym role\n"
        "`!log <minutes>` – log your gym time\n"
        "`!total` – see how many minutes you've logged\n"
        "`!top` – view the top 5 gym users"
    )

@bot.command()
async def gymrolemessage(ctx):
    msg = await ctx.send("React with 🏋️ to get the gym role.")
    bot.gym_role_message_id = msg.id

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return

    if getattr(bot, 'gym_role_message_id', None) != payload.message_id:
        return

    if str(payload.emoji.name) == "🏋️":
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        role = discord.utils.get(guild.roles, name="gym")
        if role and member:
            await member.add_roles(role)

bot.run(token)