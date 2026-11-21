import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "0")) or None

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.moderation = True

class OGCore(commands.Bot):
  async def setup_hook(self):
    for ext in ("cogs.moderation", "cogs.security", "cogs.panels"):
      await self.load_extension(ext)
    if GUILD_ID:
      guild = discord.Object(id=GUILD_ID)
      self.tree.copy_global_to(guild=guild)
      await self.tree.sync(guild=guild)
    else:
      await self.tree.sync()

bot = OGCore(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
  print(f"OG Core online as {bot.user} | {len(bot.guilds)} server(s)")

@bot.event
async def on_member_join(member):
  channel_id = int(os.getenv("WELCOME_CHANNEL_ID", "0"))
  channel = member.guild.get_channel(channel_id)
  if channel:
    embed = discord.Embed(
      title=" Welcome to OhoSMP!",
      description=f"Hey {member.mention}, welcome to **{member.guild.name}**!\n\n"
            " Read the server rules\n Check the connection guide\n Open a support ticket if you need help.",
      color=discord.Color.from_rgb(190, 45, 85)
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text="OG Core • Server Management")
    await channel.send(embed=embed)

if not TOKEN:
  raise RuntimeError("DISCORD_TOKEN missing. Copy .env.example to .env and add your bot token.")
bot.run(TOKEN)
