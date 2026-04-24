import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
import sys

sys.path.insert(0, os.path.dirname(__file__))

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


async def main():
    async with bot:
        from cogs.daily_question import setup
        await setup(bot, CHANNEL_ID)
        await bot.start(TOKEN)


asyncio.run(main())