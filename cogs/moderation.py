import discord
from datetime import timedelta
from discord import app_commands
from discord.ext import commands

def mod_only():
  return app_commands.checks.has_permissions(moderate_members=True)

class Moderation(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="purge", description="Delete recent messages")
  @mod_only()
  async def purge(self, interaction: discord.Interaction, amount: app_commands.Range[int, 1, 100]):
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f" Deleted {len(deleted)} messages.", ephemeral=True)

  @app_commands.command(name="timeout", description="Timeout a member")
  @mod_only()
  async def timeout(self, interaction: discord.Interaction, member: discord.Member,
           minutes: app_commands.Range[int, 1, 40320], reason: str = "No reason provided"):
    if member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
      return await interaction.response.send_message("You cannot moderate someone with an equal/higher role.", ephemeral=True)
    await member.timeout(discord.utils.utcnow() + timedelta(minutes=minutes), reason=reason)
    await interaction.response.send_message(f" {member.mention} timed out for {minutes} minute(s).")

  @app_commands.command(name="kick", description="Kick a member")
  @app_commands.checks.has_permissions(kick_members=True)
  async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f" {member} was kicked. Reason: {reason}")

  @app_commands.command(name="ban", description="Ban a member")
  @app_commands.checks.has_permissions(ban_members=True)
  async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f" {member} was banned. Reason: {reason}")

  @app_commands.command(name="slowmode", description="Set channel slowmode")
  @app_commands.checks.has_permissions(manage_channels=True)
  async def slowmode(self, interaction: discord.Interaction, seconds: app_commands.Range[int, 0, 21600]):
    await interaction.channel.edit(slowmode_delay=seconds)
    await interaction.response.send_message(f"⏱ Slowmode set to {seconds} seconds.")

async def setup(bot):
  await bot.add_cog(Moderation(bot))
