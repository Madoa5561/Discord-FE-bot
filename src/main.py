import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
import sys

sys.path.insert(0, os.path.dirname(__file__))

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_TOKEN が .env に設定されていません")
_raw_channel_id = os.getenv("CHANNEL_ID")
if not _raw_channel_id:
    raise ValueError("CHANNEL_ID が .env に設定されていません")
CHANNEL_ID = int(_raw_channel_id)
DAILY_COUNT = int(os.getenv("DAILY_COUNT", "1"))
if DAILY_COUNT not in (1, 3, 5):
    raise ValueError(f"DAILY_COUNT must be 1, 3, or 5, got {DAILY_COUNT}")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


async def main():
    async with bot:
        from cogs.daily_question import setup
        await setup(bot, CHANNEL_ID, DAILY_COUNT)
        await bot.start(TOKEN)


asyncio.run(main())
