"""
testRun.py - 起動時に即座に問題を投稿するテスト用スクリプト
通常の main.py と違い、スケジューラを待たずに on_ready で即投稿します。
本番の used_ids.json を消費しないよう固定問題ID(TEST_QUESTION_ID)を使用します。
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
if not TOKEN:
    raise ValueError("DISCORD_TOKEN が .env に設定されていません")
_raw_channel_id = os.getenv("CHANNEL_ID")
if not _raw_channel_id:
    raise ValueError("CHANNEL_ID が .env に設定されていません")
CHANNEL_ID = int(_raw_channel_id)

TEST_QUESTION_ID = 1  # 固定テスト問題ID（used_ids.json を消費しない）

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ─── View / Button ─────────────────────────────────────────────────────────────

class TestAnswerView(ui.View):
    def __init__(self, question: dict = None):
        super().__init__(timeout=None)
        for label in ["A", "B", "C", "D"]:
            choice_text = question["choices"][label] if question else ""
            self.add_item(TestAnswerButton(label, choice_text))
        self.add_item(TestShowAnswerButton())


class TestAnswerButton(ui.Button):
    def __init__(self, label: str, choice_text: str = ""):
        super().__init__(
            label=f"{label}: {choice_text}" if choice_text else label,
            style=discord.ButtonStyle.primary,
            custom_id=f"test_answer_{label}",
        )
        self.choice = label

    async def callback(self, interaction: discord.Interaction):
        from utils.question_manager import get_question_by_id, get_view_state, save_view_state

        message_id = interaction.message.id
        state = await get_view_state(message_id)
        if state is None:
            await interaction.response.send_message(
                "この質問の情報が見つかりません。", ephemeral=True
            )
            return

        user = interaction.user
        answered_users = state["answered_users"]
        if user.id in answered_users:
            await interaction.response.send_message("すでに回答済みです。", ephemeral=True)
            return

        question = get_question_by_id(state["question_id"])
        answered_users.append(user.id)
        correct = self.choice == question["answer"]

        top_user_ids = state["top_user_ids"]
        if correct and len(top_user_ids) < 3:
            top_user_ids.append(user.id)
            medals = ["🥇", "🥈", "🥉"]
            ranking_lines = "\n".join(
                f"{medals[i]} <@{uid}>"
                for i, uid in enumerate(top_user_ids)
            )
            base_content = interaction.message.content.split("\n\n🏆")[0]
            new_content = f"{base_content}\n\n🏆 **正答ランキング**\n{ranking_lines}"
            await interaction.message.edit(content=new_content)

        await save_view_state(message_id, state["question_id"], answered_users, top_user_ids)

        result_text = "✅ 正解です！" if correct else f"❌ 不正解です。正解は **{question['answer']}** です。"
        await interaction.response.send_message(result_text, ephemeral=True)


class TestShowAnswerButton(ui.Button):
    def __init__(self):
        super().__init__(
            label="答えを見る",
            style=discord.ButtonStyle.secondary,
            custom_id="test_show_answer",
        )

    async def callback(self, interaction: discord.Interaction):
        from utils.question_manager import get_question_by_id, get_view_state

        message_id = interaction.message.id
        state = await get_view_state(message_id)
        if state is None:
            await interaction.response.send_message(
                "この質問の情報が見つかりません。", ephemeral=True
            )
            return

        q = get_question_by_id(state["question_id"])
        answer_text = (
            f"**正解: {q['answer']}**\n"
            f"{q['choices'][q['answer']]}\n\n"
            f"**解説:**\n{q['explanation']}"
        )
        await interaction.response.send_message(answer_text, ephemeral=True)


# ─── 起動時に即投稿 ─────────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    print(f"[TEST] Logged in as {bot.user}")
    await post_test_question()


async def post_test_question():
    from utils.question_manager import get_question_by_id, save_view_state

    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print(f"[TEST] チャンネルID {CHANNEL_ID} が見つかりません。CHANNEL_ID を確認してください。")
        return

    try:
        question = get_question_by_id(TEST_QUESTION_ID)
    except ValueError as e:
        print(f"[TEST] 問題の取得に失敗しました: {e}")
        return

    choices_text = "\n".join([f"　**{k}**: {v}" for k, v in question["choices"].items()])
    content = (
        f"**[TEST] 今日の基本情報一問一答**\n\n"
        f"**Q. {question['question']}**\n\n"
        f"{choices_text}"
    )

    view = TestAnswerView(question)
    message = await channel.send(content=content, view=view)
    await save_view_state(message.id, question["id"], [], [])
    print(f"[TEST] 問題を投稿しました: ID={question['id']} Q={question['question'][:30]}...")


# ─── 起動 ───────────────────────────────────────────────────────────────────────

async def main():
    bot.add_view(TestAnswerView())
    async with bot:
        await bot.start(TOKEN)


asyncio.run(main())

