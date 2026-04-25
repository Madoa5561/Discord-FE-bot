import discord
from discord.ext import commands, tasks
from discord import ui
from datetime import time, timezone, timedelta
from utils.question_manager import get_today_question

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
            custom_id=f"answer_{label}"
        )
        self.choice = label
        self.question = question
        self.answer_view = view

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user

        if user.id in self.answer_view.answered_users:
            await interaction.response.send_message(
                "すでに回答済みです。", ephemeral=True
            )
            return

        self.answer_view.answered_users.add(user.id)
        correct = self.choice == self.question["answer"]

        if correct and self.answer_view.fastest_user is None:
            self.answer_view.fastest_user = user
            original = self.answer_view.message
            original_content = original.content
            new_content = f"{original_content}\n\n🏆 **最速正答者: {user.mention}**"
            await original.edit(content=new_content)

        result_text = "✅ 正解です！" if correct else f"❌ 不正解です。正解は **{self.question['answer']}** です。"
        await interaction.response.send_message(result_text, ephemeral=True)


class ShowAnswerButton(ui.Button):
    def __init__(self, question: dict, view: AnswerView):
        super().__init__(
            label="答えを見る",
            style=discord.ButtonStyle.secondary,
            custom_id="show_answer"
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


class DailyQuestion(commands.Cog):
    def __init__(self, bot: commands.Bot, channel_id: int, daily_count: int):
        self.bot = bot
        self.channel_id = channel_id
        times = SCHEDULE_MAP.get(daily_count, SCHEDULE_MAP[1])
        self.daily_task = tasks.loop(time=times)(self._task_body)
        self.daily_task.before_loop(self._before_loop)
        self.daily_task.start()

    def cog_unload(self):
        self.daily_task.cancel()

    async def _task_body(self):
        await self.post_question()

    async def _before_loop(self):
        await self.bot.wait_until_ready()

    async def post_question(self):
        channel = self.bot.get_channel(self.channel_id)
        if channel is None:
            print(f"チャンネルID {self.channel_id} が見つかりません。")
            return

        question = get_today_question()
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
        view.message = message


async def setup(bot: commands.Bot, channel_id: int, daily_count: int):
    await bot.add_cog(DailyQuestion(bot, channel_id, daily_count))
