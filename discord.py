import discord
from discord.ext import commands
from discord.ui import View, Select
import json
import config

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

# JSON'dan veri yükleme
with open("careers.json", "r", encoding="utf-8") as f:
    career_data = json.load(f)

user_answers = {}

@bot.event
async def on_ready():
    print(f"Bot hazır: {bot.user}")

@bot.command()
async def kariyer(ctx):
    user_answers[ctx.author.id] = {}
    await ctx.send("🎯 İlgi alanını seç:")
    await show_select(ctx, "interest", list(career_data.keys()))

async def show_select(ctx, step, options):
    class CustomSelect(discord.ui.Select):
        def __init__(self):
            select_options = [discord.SelectOption(label=opt) for opt in options]
            super().__init__(placeholder="Seçimini yap...", options=select_options)

        async def callback(self, interaction: discord.Interaction):
            user_id = interaction.user.id
            user_answers[user_id][step] = self.values[0]

            if step == "interest":
                await interaction.response.send_message("🧠 Kişiliğini seç:")
                next_options = list(career_data[self.values[0]].keys())
                await show_select(ctx, "personality", next_options)

            elif step == "personality":
                interest = user_answers[user_id]["interest"]
                await interaction.response.send_message("🎓 Eğitim seviyeni seç:")
                next_options = list(career_data[interest][self.values[0]].keys())
                await show_select(ctx, "education", next_options)

            elif step == "education":
                interest = user_answers[user_id]["interest"]
                personality = user_answers[user_id]["personality"]
                await interaction.response.send_message("👥 Çalışma tarzını seç:")
                next_options = list(career_data[interest][personality][self.values[0]].keys())
                await show_select(ctx, "workstyle", next_options)

            elif step == "workstyle":
                await show_recommendation(ctx)

    view = View()
    view.add_item(CustomSelect())
    await ctx.send("Seçimini yap:", view=view)

async def show_recommendation(ctx):
    data = user_answers[ctx.author.id]
    try:
        careers = career_data[data["interest"]][data["personality"]][data["education"]][data["workstyle"]]
        message = "🎉 Sana uygun meslekler:\n" + "\n".join(f"• {c}" for c in careers)
    except KeyError:
        message = "⚠️ Üzgünüm, bu kombinasyona uygun öneri bulunamadı."
    await ctx.send(message)

bot.run(config.TOKEN)
