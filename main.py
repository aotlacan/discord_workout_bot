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

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"minutes": {}, "gym_role_message_id": None, "leaderboard_message_id": None}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({
            "minutes": gym_minutes,
            "gym_role_message_id": bot.gym_role_message_id,
            "leaderboard_message_id": bot.leaderboard_message_id
        }, f)

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    log_handler=handler,
    log_level=logging.DEBUG,
    help_command=None
)

data = load_data()
gym_minutes = data.get("minutes", {})
bot.gym_role_message_id = data.get("gym_role_message_id")
bot.leaderboard_message_id = data.get("leaderboard_message_id")

atexit.register(save_data)

def has_gym_role(member):
    return any(role.name.lower() == "gym" for role in member.roles)

async def update_leaderboard(channel, delete_message=True):
    sorted_data = sorted(gym_minutes.items(), key=lambda x: x[1], reverse=True)[:5]
    embed = Embed(
        title="🏋️ Gym Leaderboard",
        description="Top 5 gym grinders ranked by total minutes logged.",
        color=0xe74c3c
    )
    embed.set_author(
        name="GymBot Tracker",
        icon_url="https://cdn-icons-png.flaticon.com/512/2331/2331970.png"
    )
    for i, (user_id, minutes) in enumerate(sorted_data, start=1):
        user = await bot.fetch_user(user_id)
        medal = ["🥇", "🥈", "🥉", "🍎", "💩"][i - 1]
        embed.add_field(
            name=f"#{i} {medal} {user.display_name}",
            value=f"**{minutes}** minutes logged",
            inline=False
        )
    embed.set_footer(text=f"Updated: {datetime.now().strftime('%H:%M:%S')}")

    if bot.leaderboard_message_id:
        try:
            message = await channel.fetch_message(bot.leaderboard_message_id)
            await message.edit(embed=embed)
            return
        except discord.NotFound:
            pass
    message = await channel.send(embed=embed)
    bot.leaderboard_message_id = message.id
    save_data()
    if delete_message:
        await message.delete(delay=5)

@bot.command()
async def leaderboardmessage(ctx):
    await update_leaderboard(ctx.channel, delete_message=False)
    await ctx.message.delete(delay=5)

@bot.command()
async def gymrolemessage(ctx):
    embed = Embed(
        title="🏋️ Join the Gym Role",
        description="React with 🏋️ to this message to receive the **gym** role and start logging your workouts!",
        color=0x2ecc71
    )
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🏋️")
    bot.gym_role_message_id = msg.id
    save_data()
    await ctx.message.delete(delay=5)

@bot.command()
async def alert(ctx):
    embed = Embed(
        title="⚠️ Important",
        description="Only run commands when the bot is **ONLINE**.",
        color=0xf1c40f
    )
    msg = await ctx.send(embed=embed)
    await ctx.message.delete(delay=5)

@bot.command()
async def setup(ctx):
    await alert(ctx)
    await gymrolemessage(ctx)
    await help_command(ctx)
    await leaderboardmessage(ctx)
    await ctx.message.delete(delay=5)

@bot.command()
async def joingym(ctx):
    role = discord.utils.get(ctx.guild.roles, name="gym")
    if not role:
        msg = await ctx.send("No role named 'gym' found.")
        await ctx.message.delete(delay=5)
        await msg.delete(delay=5)
        return

    if role in ctx.author.roles:
        msg = await ctx.send("You already have the gym role.")
        await ctx.message.delete(delay=5)
        await msg.delete(delay=5)
        return

    await ctx.author.add_roles(role)
    msg = await ctx.send(f"{ctx.author.mention} has been added to the gym role.")
    await ctx.message.delete(delay=5)
    await msg.delete(delay=5)

@bot.command()
async def leavegym(ctx):
    role = discord.utils.get(ctx.guild.roles, name="gym")
    if not role:
        msg = await ctx.send("No role named 'gym' found.")
        await ctx.message.delete(delay=5)
        await msg.delete(delay=5)
        return
    if role in ctx.author.roles:
        await ctx.author.remove_roles(role)
        msg = await ctx.send(f"{ctx.author.mention}, the gym role has been removed.")
        await ctx.message.delete(delay=5)
        await msg.delete(delay=5)
    else:
        msg = await ctx.send("You don't have the gym role.")
        await ctx.message.delete(delay=5)
        await msg.delete(delay=5)

@bot.command()
async def log(ctx, minutes: int):
    if not has_gym_role(ctx.author):
        msg = await ctx.send("You need the gym role to log minutes.")
        await ctx.message.delete(delay=5)
        await msg.delete(delay=5)
        return

    if minutes <= 0 or minutes > 1440:
        msg = await ctx.send("Please enter a valid number of minutes (1–1440).")
        await ctx.message.delete(delay=5)
        await msg.delete(delay=5)
        return

    user_id = str(ctx.author.id)
    gym_minutes[user_id] = gym_minutes.get(user_id, 0) + minutes
    save_data()
    await update_leaderboard(ctx.channel)

    msg = await ctx.send(f"{ctx.author.mention} logged {minutes} minutes. Total: {gym_minutes[user_id]}")
    await ctx.message.delete(delay=5)
    await msg.delete(delay=5)

@bot.command()
async def total(ctx):
    if not has_gym_role(ctx.author):
        msg = await ctx.send("You need the gym role to view your stats.")
        await ctx.message.delete(delay=5)
        await msg.delete(delay=5)
        return

    user_id = str(ctx.author.id)
    total = gym_minutes.get(user_id, 0)
    msg = await ctx.send(f"{ctx.author.mention}, you have logged {total} total minutes.")
    await ctx.message.delete(delay=5)
    await msg.delete(delay=5)

@bot.command(name="help")
async def help_command(ctx):
    embed = Embed(
        title="📋 GymBot Help Menu",
        description="Here are the available commands:",
        color=0xe74c3c
    )
    embed.add_field(name="`!joingym`", value="Join the gym and get access to logging.", inline=False)
    embed.add_field(name="`!log <minutes>`", value="Log your gym time.", inline=False)
    embed.add_field(name="`!remove <minutes>`", value="Remove previously logged time.", inline=False)
    embed.add_field(name="`!total`", value="View how many total minutes you've logged.", inline=False)
    embed.add_field(name="`!top`", value="See the top 5 users with the most minutes.", inline=False)
    embed.add_field(name="`!leavegym`", value="Remove the gym role from yourself.", inline=False)
    embed.set_footer(text="All commands require the gym role except !joingym.")
    await ctx.message.delete(delay=5)
    msg = await ctx.send(embed=embed)

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

@bot.command()
async def remove(ctx, minutes: int):
    if not has_gym_role(ctx.author):
        msg = await ctx.send("You need the gym role to remove minutes.")
        await ctx.message.delete(delay=5)
        await msg.delete(delay=5)
        return

    if minutes <= 0:
        msg = await ctx.send("Please enter a positive number of minutes to remove.")
        await ctx.message.delete(delay=5)
        await msg.delete(delay=5)
        return

    user_id = str(ctx.author.id)
    current = gym_minutes.get(user_id, 0)
    if current == 0:
        msg = await ctx.send("You haven't logged any minutes yet.")
        await ctx.message.delete(delay=5)
        await msg.delete(delay=5)
        return

    new_total = max(0, current - minutes)
    gym_minutes[user_id] = new_total
    save_data()
    await update_leaderboard(ctx.channel)
    msg = await ctx.send(f"{ctx.author.mention}, removed {minutes} minutes. New total: {new_total}")
    await ctx.message.delete(delay=5)
    await msg.delete(delay=5)

bot.run(token)
