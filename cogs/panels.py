import discord
from discord import app_commands
from discord.ext import commands

PINK = discord.Color.from_rgb(180, 65, 145)

SUPPORT_OPTIONS = [
  (" General Help", "Gameplay, commands, rules or server systems"),
  (" Account Help", "Login, password or account-linking issues"),
  (" Other Problems", "Anything not covered by the categories above"),
  (" Player Report", "Report rule breakers, hackers or exploiters"),
  (" Staff Report", "Report staff abuse or unfair actions"),
  (" Bug Report", "Report bugs, dupes, errors or glitches"),
  (" Appeals", "Appeal a punishment, ban, mute or warning"),
  (" Store Purchase Claim", "Missing ranks, crates, keys or rewards"),
  (" Payment Issue", "Failed or pending payments"),
  (" Reward Claims", "Missing store rewards or bundles"),
]

class TicketSelect(discord.ui.Select):
  def __init__(self):
    super().__init__(placeholder="Select a support category...", min_values=1, max_values=1, custom_id="ogcore:support_select",
             options=[discord.SelectOption(label=a, description=b[:100]) for a,b in SUPPORT_OPTIONS])

  async def callback(self, interaction: discord.Interaction):
    guild = interaction.guild
    category = discord.utils.get(guild.categories, name="OG Core Tickets")
    if category is None:
      category = await guild.create_category("OG Core Tickets")
    existing = discord.utils.get(category.text_channels, topic=f"ticket-owner:{interaction.user.id}")
    if existing:
      return await interaction.response.send_message(f"You already have a ticket: {existing.mention}", ephemeral=True)
    overwrites = {
      guild.default_role: discord.PermissionOverwrite(view_channel=False),
      interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
      guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
    }
    staff_role_id = int(__import__("os").getenv("STAFF_ROLE_ID", "0"))
    staff_role = guild.get_role(staff_role_id) if staff_role_id else None
    if staff_role:
      overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
    channel = await guild.create_text_channel(
      f"ticket-{interaction.user.name}".lower().replace(" ", "-")[:90],
      category=category, overwrites=overwrites, topic=f"ticket-owner:{interaction.user.id}"
    )
    embed = discord.Embed(title=" OG Core Support", description=f"**Category:** {self.values[0]}\nPlease explain your issue. A staff member will assist you shortly.", color=PINK)
    await channel.send(content=interaction.user.mention, embed=embed, view=CloseTicket())
    await interaction.response.send_message(f"Your ticket is ready: {channel.mention}", ephemeral=True)

class SupportView(discord.ui.View):
  def __init__(self):
    super().__init__(timeout=None)
    self.add_item(TicketSelect())

class CloseTicket(discord.ui.View):
  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.button(label="Close Ticket", emoji="", style=discord.ButtonStyle.danger, custom_id="ogcore:close")
  async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
    if not interaction.user.guild_permissions.manage_channels:
      topic = interaction.channel.topic or ""
      if f"ticket-owner:{interaction.user.id}" not in topic:
        return await interaction.response.send_message("Only the ticket owner or staff can close this.", ephemeral=True)
    await interaction.response.send_message(" Ticket closing in 5 seconds.")
    await __import__("asyncio").sleep(5)
    await interaction.channel.delete(reason="Ticket closed")

class ApplicationSelect(discord.ui.Select):
  def __init__(self):
    options = [
      discord.SelectOption(label="Staff Application", description="Apply to help moderate the community", emoji=""),
      discord.SelectOption(label="Media Application", description="Apply to create content and get promoted", emoji="")
    ]
    super().__init__(placeholder="Make a selection...", options=options, custom_id="ogcore:application_select")

  async def callback(self, interaction: discord.Interaction):
    await interaction.response.send_modal(ApplicationModal(self.values[0]))

class ApplicationModal(discord.ui.Modal):
  def __init__(self, kind):
    super().__init__(title=kind)
    self.kind = kind
    self.age = discord.ui.TextInput(label="Age", max_length=3)
    self.time = discord.ui.TextInput(label="How active are you?", max_length=300)
    self.reason = discord.ui.TextInput(label="Why should we choose you?", style=discord.TextStyle.paragraph, max_length=1000)
    self.add_item(self.age); self.add_item(self.time); self.add_item(self.reason)

  async def on_submit(self, interaction: discord.Interaction):
    embed = discord.Embed(title=f" {self.kind}", color=PINK)
    embed.add_field(name="Applicant", value=f"{interaction.user.mention} (`{interaction.user.id}`)", inline=False)
    embed.add_field(name="Age", value=self.age.value)
    embed.add_field(name="Activity", value=self.time.value, inline=False)
    embed.add_field(name="Reason", value=self.reason.value, inline=False)
    channel_id = int(__import__("os").getenv("APPLICATION_LOG_CHANNEL_ID", "0"))
    channel = interaction.guild.get_channel(channel_id)
    if channel:
      await channel.send(embed=embed)
    await interaction.response.send_message(" Your application has been submitted!", ephemeral=True)

class ApplicationView(discord.ui.View):
  def __init__(self):
    super().__init__(timeout=None)
    self.add_item(ApplicationSelect())

class Panels(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    bot.add_view(SupportView())
    bot.add_view(ApplicationView())
    bot.add_view(CloseTicket())

  @app_commands.command(name="setup_support", description="Post the OG Core support ticket panel")
  @app_commands.checks.has_permissions(administrator=True)
  async def setup_support(self, interaction: discord.Interaction):
    embed = discord.Embed(title=" OG Core Support Center", description="Need help? Select a category below to open a private support ticket.\n\n" + "\n".join(f"**{a}**\n{b}" for a,b in SUPPORT_OPTIONS), color=PINK)
    embed.set_footer(text="OG Core • Support System")
    await interaction.channel.send(embed=embed, view=SupportView())
    await interaction.response.send_message("Support panel posted.", ephemeral=True)

  @app_commands.command(name="setup_applications", description="Post staff and media application panel")
  @app_commands.checks.has_permissions(administrator=True)
  async def setup_applications(self, interaction: discord.Interaction):
    embed = discord.Embed(title=" OhoSMP Applications ", description="Welcome! Select the rank you wish to apply for from the dropdown menu below.\n\n **Staff:** Keep the community safe and assist players\n **Media:** Showcase your gameplay and get promoted\n\n Please read all requirements before submitting.", color=PINK)
    await interaction.channel.send(embed=embed, view=ApplicationView())
    await interaction.response.send_message("Application panel posted.", ephemeral=True)

async def setup(bot):
  await bot.add_cog(Panels(bot))
