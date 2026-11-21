import json
import os
import time
from collections import defaultdict, deque
from pathlib import Path
from datetime import timedelta
import discord
from discord.ext import commands

DATA_DIR = Path(__file__).resolve().parents[1] / 'data'


def guild_settings(guild_id):
    defaults = {'anti_spam': True, 'mass_mention': True, 'invite_filter': True}
    path = DATA_DIR / f'guild_{guild_id}.json'
    try:
        if path.exists():
            defaults.update(json.loads(path.read_text(encoding='utf-8')))
    except (OSError, ValueError):
        pass
    return defaults


class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.recent = defaultdict(lambda: deque(maxlen=8))

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild or message.author.bot:
            return
        member = message.author
        settings = guild_settings(message.guild.id)
        if member.guild_permissions.manage_messages:
            return

        if settings.get('anti_spam', True):
            q = self.recent[(message.guild.id, member.id)]
            q.append(time.monotonic())
            if len(q) >= 6 and q[-1] - q[0] <= 7:
                try:
                    await message.channel.purge(limit=6, check=lambda m: m.author.id == member.id)
                    await member.timeout(discord.utils.utcnow() + timedelta(minutes=2), reason='OG Core anti-spam')
                    await message.channel.send(f'{member.mention} was timed out for spam.', delete_after=8)
                except discord.Forbidden:
                    pass
                q.clear()

        if settings.get('mass_mention', True) and (message.mention_everyone or len(message.mentions) >= 6):
            try:
                await message.delete()
                await member.timeout(discord.utils.utcnow() + timedelta(minutes=5), reason='OG Core mass-mention protection')
            except discord.Forbidden:
                pass

        content = message.content.lower()
        if settings.get('invite_filter', True) and ('discord.gg/' in content or 'discord.com/invite/' in content):
            if not member.guild_permissions.manage_guild:
                try:
                    await message.delete()
                    await message.channel.send(f'{member.mention}, Discord invites are not allowed here.', delete_after=6)
                except discord.Forbidden:
                    pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        age = discord.utils.utcnow() - member.created_at
        if age.days < 3:
            channel_id = int(os.getenv('SECURITY_LOG_CHANNEL_ID', '0'))
            channel = member.guild.get_channel(channel_id)
            if channel:
                await channel.send(f'New-account alert: {member.mention} — account is {age.days} day(s) old. Please review.')


async def setup(bot):
    await bot.add_cog(Security(bot))
