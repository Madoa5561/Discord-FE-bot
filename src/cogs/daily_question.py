import discord
from discord.ext import commands, tasks
from discord import ui
from datetime import time, timezone, timedelta
from utils.question_manager import (
    get_today_question,
    get_question_by_id,
    get_view_state,
    save_view_state,
)

JST = timezone(timedelta(hours=9))

# 1回: 0:00
# 3回: 0:00, 12:00, 16:00
# 5回: 0:00, 6:00, 12:00, 16:00, 18:00
SCHEDULE_MAP = {
    1: [time(0, 0, tzinfo=JST)],
    3: [time(0, 0, tzinfo=JST), time(12, 0, tzinfo=JST), time(16, 0, tzinfo=JST)],
    5: [time(0, 0, tzinfo=JST), time(6, 0, tzinfo=JST), time(12, 0, tzinfo=JST), time(16, 0, tzinfo=JST), time(18, 0, tzinfo=JST)],
}


class AnswerView(ui.View):
    def __init__(self, question: dict = None):
        super().__init__(timeout=None)
        for label in ["A", "B", "C", "D"]:
            choice_text = question["choices"][label] if question else ""
            self.add_item(AnswerButton(label, choice_text))
        self.add_item(ShowAnswerButton())


class AnswerButton(ui.Button):
    def __init__(self, label: str, choice_text: str = ""):
        super().__init__(
            label=f"{label}: {choice_text}" if choice_text else label,
            style=discord.ButtonStyle.primary,
            custom_id=f"answer_{label}"
        )
        self.choice = label

    async def callback(self, interaction: discord.Interaction):
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
            await interaction.response.send_message(
                "すでに回答済みです。", ephemeral=True
            )
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


class ShowAnswerButton(ui.Button):
    def __init__(self):
        super().__init__(
            label="答えを見る",
            style=discord.ButtonStyle.secondary,
            custom_id="show_answer"
        )

    async def callback(self, interaction: discord.Interaction):
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


class DailyQuestion(commands.Cog):
    def __init__(self, bot: commands.Bot, channel_id: int, daily_count: int):
        self.bot = bot
        self.channel_id = channel_id
        times = SCHEDULE_MAP.get(daily_count, SCHEDULE_MAP[1])
        self.daily_task = tasks.loop(time=times)(self.post_question)
        self.daily_task.before_loop(self._before_loop)
        self.daily_task.start()

    def cog_unload(self):
        self.daily_task.cancel()

    async def _before_loop(self):
        await self.bot.wait_until_ready()

    async def post_question(self):
        try:
            channel = self.bot.get_channel(self.channel_id)
            if channel is None:
                print(f"[ERROR] チャンネルID {self.channel_id} が見つかりません。")
                return

            question = await get_today_question()
            choices_text = "\n".join(
                [f"　**{k}**: {v}" for k, v in question["choices"].items()]
            )
            content = (
                f"**今日の基本情報一問一答**\n\n"
                f"**Q. {question['question']}**\n\n"
                f"{choices_text}"
            )

            view = AnswerView(question)
            message = await channel.send(content=content, view=view)
            await save_view_state(message.id, question["id"], [], [])
        except Exception as e:
            print(f"[ERROR] post_question で例外が発生しました: {e}")


async def setup(bot: commands.Bot, channel_id: int, daily_count: int):
    # 再起動後もボタンを有効にするためパーシステントビューを登録
    bot.add_view(AnswerView())
    await bot.add_cog(DailyQuestion(bot, channel_id, daily_count))
