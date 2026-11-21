# OG Core Discord Bot

Python Discord bot starter with:
- Welcome embed
- Support ticket dropdown and private ticket channels
- Staff/Media application dropdown + modal
- Moderation slash commands: `/ban`, `/kick`, `/timeout`, `/purge`, `/slowmode`
- Basic anti-spam, mass-mention, invite filter and new-account alerts

## 1. Create Discord application
1. Open https://discord.com/developers/applications
2. New Application → name it **OG Core**
3. Bot → Add Bot → Reset Token → copy token privately.
4. Enable **Server Members Intent** and **Message Content Intent** under Privileged Gateway Intents.
5. OAuth2 → URL Generator: scopes `bot` and `applications.commands`.
6. Bot permissions: Manage Roles (only if you add role features), Manage Channels, View Channels, Send Messages, Embed Links, Read Message History, Manage Messages, Moderate Members, Kick Members, Ban Members. Invite the bot.

Never share your bot token or upload `.env` to GitHub.

## 2. Configure
- Rename `.env.example` to `.env`
- Add `DISCORD_TOKEN`
- Add your test server ID to `GUILD_ID` for fast slash-command sync.
- Add channel/role IDs as needed. Keep 0 for features you have not configured.

## 3. Run locally
```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# Linux/macOS:
source .venv/bin/activate
pip install -r requirements.txt
python bot.py
```

Then use `/setup_support` and `/setup_applications` in the channels where you want panels.

## 4. Hosting
A Discord Gateway bot needs a continuously running worker. Render's free web service sleeps and is not suitable for reliable 24/7 Gateway uptime. Oracle Cloud Always Free VM is a possible free VPS route, but capacity, account approval and idle reclamation policies apply. If you use a VPS, install Python, upload this folder, configure `.env`, and run it under `systemd` or `tmux`.

## Important safety notes
This is a starter build, not a finished production anti-raid suite. Set bot role below owner/admin roles. Test in a private server first. Anti-spam thresholds are conservative defaults; tune them to your community. Add a dedicated staff role and log channels before public use.


## 5. OG Core web dashboard
The project now includes a dark red/black responsive dashboard (`dashboard.py`). It uses Discord OAuth2 login and only lists servers where the signed-in user has Administrator permission or owns the server. The dashboard can toggle anti-spam, mass-mention protection and invite filtering. Settings are stored in `data/guild_<server_id>.json` and read by the bot's security module.

### Configure Discord OAuth2
1. In the same Discord Developer Portal application, open **OAuth2 → General**.
2. Add the exact redirect URL, for example `http://localhost:8080/callback` (for production, use your HTTPS domain ending in `/callback`).
3. Copy the Application ID and Client Secret into `DISCORD_CLIENT_ID` and `DISCORD_CLIENT_SECRET` in `.env`.
4. Set `DISCORD_REDIRECT_URI` to the exact same redirect URL.
5. Set `DASHBOARD_SECRET` to a long random secret. Do not use the example value in production.
6. Install dependencies with `pip install -r requirements.txt`.
7. Start the bot with `python bot.py` and the dashboard separately with `python dashboard.py`.
8. Open `http://localhost:8080`, sign in with Discord, choose your server and save security settings.

For a public deployment, put the dashboard behind HTTPS (for example, Nginx + Let's Encrypt) and configure the HTTPS callback URL in both `.env` and the Discord Developer Portal. Do not expose Flask's development server directly to the public internet. Run it with Gunicorn. Keep the bot and dashboard on the same machine or shared persistent storage so both can access the `data/` directory.

The dashboard currently controls the three security toggles listed above; moderation actions remain Discord slash commands. It is a starter dashboard and does not yet include live analytics, ticket transcripts, role editor or a full audit-log browser.
