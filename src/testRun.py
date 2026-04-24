"""
testRun.py - 起動時に即座に問題を投稿するテスト用スクリプト
通常の main.py と違い、0時のスケジューラを待たずに on_ready で即投稿します。
"""
import discord
from discord.ext import commands
from discord import ui
from dotenv import load_dotenv
import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(__file__))

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ─── View / Button (daily_question.py と同じロジックをここに直書き) ──────────

class AnswerView(ui.View):
    def __init__(self, question: dict):
        super().__init__(timeout=None)
        self.question = question
        self.answered_users: set = set()
        self.fastest_user = None
        self.message: discord.Message = None

        for label in ["A", "B", "C", "D"]:
            self.add_item(AnswerButton(label, question, self))

        self.add_item(ShowAnswerButton(question, self))


class AnswerButton(ui.Button):
    def __init__(self, label: str, question: dict, view: AnswerView):
        choice_text = question["choices"][label]
        super().__init__(
            label=f"{label}: {choice_text}",
            style=discord.ButtonStyle.primary,
            custom_id=f"test_answer_{label}",
        )
        self.choice = label
        self.question = question
        self.answer_view = view

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user

        if user.id in self.answer_view.answered_users:
            await interaction.response.send_message("すでに回答済みです。", ephemeral=True)
            return

        self.answer_view.answered_users.add(user.id)
        correct = self.choice == self.question["answer"]

        if correct and self.answer_view.fastest_user is None:
            self.answer_view.fastest_user = user
            original = self.answer_view.message
            new_content = f"{original.content}\n\n🏆 **最速正答者: {user.mention}**"
            await original.edit(content=new_content)

        result_text = "✅ 正解です！" if correct else f"❌ 不正解です。正解は **{self.question['answer']}** です。"
        await interaction.response.send_message(result_text, ephemeral=True)


class ShowAnswerButton(ui.Button):
    def __init__(self, question: dict, view: AnswerView):
        super().__init__(
            label="答えを見る",
            style=discord.ButtonStyle.secondary,
            custom_id="test_show_answer",
        )
        self.question = question
        self.answer_view = view

    async def callback(self, interaction: discord.Interaction):
        q = self.question
        answer_text = (
            f"**正解: {q['answer']}**\n"
            f"{q['choices'][q['answer']]}\n\n"
            f"**解説:**\n{q['explanation']}"
        )
        await interaction.response.send_message(answer_text, ephemeral=True)


# ─── 起動時に即投稿 ──────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    print(f"[TEST] Logged in as {bot.user}")
    await post_test_question()


async def post_test_question():
    from utils.question_manager import get_today_question

    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print(f"[TEST] チャンネルID {CHANNEL_ID} が見つかりません。CHANNEL_ID を確認してください。")
        return

    question = get_today_question()
    choices_text = "\n".join([f"　**{k}**: {v}" for k, v in question["choices"].items()])
    content = (
        f"**[TEST] 今日の基本情報一問一答**\n\n"
        f"**Q. {question['question']}**\n\n"
        f"{choices_text}"
    )

    view = AnswerView(question)
    message = await channel.send(content=content, view=view)
    view.message = message
    print(f"[TEST] 問題を投稿しました: ID={question['id']} Q={question['question'][:30]}...")


# ─── 起動 ────────────────────────────────────────────────────────────────────

async def main():
    async with bot:
        await bot.start(TOKEN)


asyncio.run(main())
