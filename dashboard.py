import json
import os
import secrets
from pathlib import Path

import requests
from flask import Flask, abort, redirect, render_template_string, request, session, url_for
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('DASHBOARD_SECRET', 'change-this-long-random-secret')
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax')

CLIENT_ID = os.getenv('DISCORD_CLIENT_ID', '')
CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET', '')
REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI', 'http://localhost:8080/callback')
API = 'https://discord.com/api/v10'
DATA_DIR = Path(__file__).parent / 'data'
DATA_DIR.mkdir(exist_ok=True)

PAGE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OG Core | Control Center</title>
<style>
:root{--bg:#09090d;--panel:#121219;--panel2:#181820;--line:#292934;--text:#f4f4f7;--muted:#9292a2;--red:#d93655;--red2:#ff526c;--green:#43c58a}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 75% -15%,#491323 0,transparent 42%),var(--bg);color:var(--text);font:14px Inter,ui-sans-serif,system-ui,Segoe UI,sans-serif;min-height:100vh}
a{color:inherit;text-decoration:none}.shell{display:grid;grid-template-columns:250px 1fr;min-height:100vh}.side{background:#0d0d13;border-right:1px solid var(--line);padding:26px 18px;display:flex;flex-direction:column;gap:30px}.brand{display:flex;align-items:center;gap:12px;padding:4px 8px}.mark{width:38px;height:38px;border-radius:12px;background:linear-gradient(145deg,#ff6477,#8c1834);box-shadow:0 8px 28px #d9365540;display:grid;place-items:center;font-weight:900;letter-spacing:-2px}.brand strong{font-size:17px;letter-spacing:1.5px}.brand small{display:block;color:var(--muted);font-size:10px;letter-spacing:2px;margin-top:2px}.navlabel{color:#666675;font-size:10px;font-weight:800;letter-spacing:1.8px;padding:0 10px}.nav a{display:flex;align-items:center;gap:12px;padding:12px 11px;border-radius:10px;color:#aaaab7;margin-top:4px}.nav a.active,.nav a:hover{background:#29131c;color:white}.nav a.active{box-shadow:inset 3px 0 var(--red2)}.ico{width:18px;text-align:center;color:#e45a73;font-size:15px}.sidefoot{margin-top:auto;color:#666675;font-size:11px;line-height:1.6;padding:8px}.main{padding:30px clamp(18px,4vw,52px);max-width:1500px;width:100%;margin:auto}.top{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:28px}.eyebrow{color:var(--red2);font-size:10px;font-weight:800;letter-spacing:2px;text-transform:uppercase}.top h1{font-size:28px;margin:6px 0 0;letter-spacing:-.8px}.user{display:flex;align-items:center;gap:10px;background:var(--panel);border:1px solid var(--line);padding:8px 12px;border-radius:12px;color:#ddd}.avatar{width:30px;height:30px;border-radius:50%;background:#292934;object-fit:cover}.hero{background:linear-gradient(110deg,#29111b,#17141d 65%,#21121c);border:1px solid #49202d;border-radius:18px;padding:25px;display:flex;justify-content:space-between;align-items:center;gap:20px;margin-bottom:20px;overflow:hidden}.hero h2{font-size:21px;margin:0 0 8px}.hero p{color:#b6aeb7;margin:0;line-height:1.6}.status{white-space:nowrap;border:1px solid #315d4b;color:#79e0ad;background:#10251d;padding:8px 12px;border-radius:999px;font-size:11px;font-weight:700}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:16px 0 22px}.card{background:var(--panel);border:1px solid var(--line);border-radius:15px;padding:18px}.metric{font-size:25px;font-weight:800;margin-top:10px}.muted{color:var(--muted)}.section{display:flex;justify-content:space-between;align-items:end;margin:28px 0 12px}.section h3{font-size:16px;margin:0}.section p{margin:5px 0 0;color:var(--muted);font-size:12px}.settings{display:grid;grid-template-columns:1fr 1fr;gap:12px}.setting{display:flex;justify-content:space-between;align-items:center;gap:18px;background:var(--panel);border:1px solid var(--line);border-radius:13px;padding:16px}.setting strong{display:block;font-size:13px}.setting small{display:block;color:var(--muted);margin-top:5px;line-height:1.4}.switch{position:relative;width:42px;height:24px;flex:none}.switch input{opacity:0;width:0;height:0}.slider{position:absolute;inset:0;border-radius:30px;background:#393944;cursor:pointer;transition:.2s}.slider:before{content:'';position:absolute;width:18px;height:18px;left:3px;top:3px;background:white;border-radius:50%;transition:.2s}.switch input:checked+.slider{background:var(--red)}.switch input:checked+.slider:before{transform:translateX(18px)}.btn{border:0;border-radius:10px;background:linear-gradient(100deg,var(--red),#a51f43);color:white;padding:11px 17px;font-weight:750;cursor:pointer}.btn:hover{filter:brightness(1.12)}.guilds{display:flex;flex-wrap:wrap;gap:9px}.guild{background:var(--panel);border:1px solid var(--line);padding:10px 13px;border-radius:10px;color:#ccc}.guild.selected{border-color:var(--red);background:#28131d;color:#fff}.notice{background:#201c12;border:1px solid #5a4824;color:#e8d5a3;padding:12px 14px;border-radius:10px;margin:16px 0;font-size:12px}.footer{color:#656575;font-size:11px;margin-top:32px;padding-top:16px;border-top:1px solid var(--line)}.login{max-width:460px;margin:12vh auto;padding:36px;background:var(--panel);border:1px solid var(--line);border-radius:20px;text-align:center}.login h1{letter-spacing:3px}.login p{color:var(--muted);line-height:1.6}.login .mark{margin:auto;width:58px;height:58px;font-size:22px}
@media(max-width:850px){.shell{grid-template-columns:1fr}.side{padding:14px 18px;border-right:0;border-bottom:1px solid var(--line);gap:12px}.nav{display:flex;overflow:auto}.navlabel,.sidefoot{display:none}.nav a{white-space:nowrap;padding:9px}.main{padding:22px 16px}.grid{grid-template-columns:1fr 1fr}.settings{grid-template-columns:1fr}.hero{align-items:flex-start;flex-direction:column}}
@media(max-width:480px){.grid{grid-template-columns:1fr}.top{align-items:flex-start;flex-direction:column}.top h1{font-size:24px}}
</style></head><body>
{% if not user %}<div class="login"><div class="mark">OG</div><h1>OG CORE</h1><p>SERVER CONTROL CENTER<br>Sign in with Discord to manage security settings for servers where you have administrator access.</p><a class="btn" href="{{ url_for('login') }}">Continue with Discord</a></div>
{% else %}<div class="shell"><aside class="side"><div class="brand"><div class="mark">OG</div><div><strong>OG CORE</strong><small>CONTROL CENTER</small></div></div><div class="navlabel">MANAGEMENT</div><nav class="nav"><a class="active" href="{{ url_for('home', guild_id=selected.id if selected else '') }}"><span class="ico">▦</span>Overview</a><a href="#security"><span class="ico">◈</span>Security</a><a href="#moderation"><span class="ico">⌁</span>Moderation</a><a href="#server"><span class="ico">▤</span>Server</a></nav><div class="sidefoot">OG CORE<br>Secure server management<br>Version 1.1</div></aside>
<main class="main"><header class="top"><div><div class="eyebrow">OG CORE / DASHBOARD</div><h1>Control Center</h1></div><div class="user">{% if user.avatar %}<img class="avatar" src="https://cdn.discordapp.com/avatars/{{ user.id }}/{{ user.avatar }}.png">{% else %}<div class="avatar"></div>{% endif %}<span>{{ user.username }}</span><a class="muted" href="{{ url_for('logout') }}">Log out</a></div></header>
{% if selected %}<section class="hero"><div><div class="eyebrow">SERVER WORKSPACE</div><h2>{{ selected.name }}</h2><p>Manage protection settings and keep your community under control.</p></div><span class="status">● Dashboard connected</span></section>
<div class="grid"><div class="card"><div class="muted">Selected server</div><div class="metric" style="font-size:19px">{{ selected.name }}</div><div class="muted" style="font-size:11px;margin-top:7px">ID: {{ selected.id }}</div></div><div class="card"><div class="muted">Security modules</div><div class="metric">{{ enabled_count }} / 3</div><div class="muted" style="font-size:11px;margin-top:7px">Protection modules enabled</div></div><div class="card"><div class="muted">Access level</div><div class="metric" style="font-size:19px">Administrator</div><div class="muted" style="font-size:11px;margin-top:7px">Verified through Discord OAuth2</div></div></div>
<div class="section" id="server"><div><h3>Your manageable servers</h3><p>Only servers where your Discord account has administrator access appear here.</p></div></div><div class="guilds">{% for g in guilds %}<a class="guild {{ 'selected' if g.id == selected.id else '' }}" href="{{ url_for('home', guild_id=g.id) }}">{{ g.name }}</a>{% endfor %}</div>
<form method="post" action="{{ url_for('save_settings', guild_id=selected.id) }}"><div class="section" id="security"><div><h3>Security configuration</h3><p>Changes are saved to the bot's shared configuration file.</p></div><button class="btn" type="submit">Save changes</button></div><div class="settings">
{% for key,title,desc in [('anti_spam','Anti-spam protection','Detect rapid message bursts and apply a temporary timeout.'),('mass_mention','Mass-mention protection','Remove excessive mentions and apply a temporary timeout.'),('invite_filter','Discord invite filter','Remove invite links from members without server management permission.')] %}<label class="setting"><span><strong>{{ title }}</strong><small>{{ desc }}</small></span><span class="switch"><input type="checkbox" name="{{ key }}" {{ 'checked' if settings.get(key, True) else '' }}><span class="slider"></span></span></label>{% endfor %}
</div><div class="section" id="moderation"><div><h3>Moderation tools</h3><p>Available as Discord slash commands. Permissions are checked by Discord.</p></div></div><div class="settings"><div class="setting"><span><strong>Member moderation</strong><small>/ban, /kick, /timeout</small></span><span class="muted">Enabled</span></div><div class="setting"><span><strong>Channel management</strong><small>/purge, /slowmode</small></span><span class="muted">Enabled</span></div></div></form>
{% else %}<div class="notice">No administrator-access servers were found for this Discord account.</div>{% endif %}
<div class="footer">OG CORE CONTROL CENTER · Use a strong DASHBOARD_SECRET and HTTPS in production. Never share your bot token.</div></main></div>{% endif %}
</body></html>'''


def get_json(guild_id):
    path = DATA_DIR / f'guild_{guild_id}.json'
    defaults = {'anti_spam': True, 'mass_mention': True, 'invite_filter': True}
    if path.exists():
        try:
            defaults.update(json.loads(path.read_text(encoding='utf-8')))
        except (ValueError, OSError):
            pass
    return defaults


def save_json(guild_id, data):
    path = DATA_DIR / f'guild_{guild_id}.json'
    path.write_text(json.dumps(data, indent=2), encoding='utf-8')


def discord_request(path, token=None, data=None):
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    return requests.get(API + path, headers=headers, timeout=15) if data is None else requests.post(API + path, headers=headers, data=data, timeout=15)


def current_guilds():
    token = session.get('access_token')
    if not token:
        return []
    response = discord_request('/users/@me/guilds', token)
    if response.status_code != 200:
        session.clear()
        return []
    # ADMINISTRATOR permission bit is 0x8. Server owner is also authorized.
    return [g for g in response.json() if (int(g.get('permissions', '0')) & 8) or g.get('owner')]


@app.get('/')
def home():
    user = session.get('user')
    if not user:
        return render_template_string(PAGE, user=None)
    guilds = current_guilds()
    requested = request.args.get('guild_id')
    selected = next((g for g in guilds if g['id'] == requested), guilds[0] if guilds else None)
    settings = get_json(selected['id']) if selected else {}
    enabled_count = sum(bool(settings.get(k)) for k in ('anti_spam', 'mass_mention', 'invite_filter'))
    return render_template_string(PAGE, user=user, guilds=guilds, selected=selected, settings=settings, enabled_count=enabled_count)


@app.get('/login')
def login():
    if not CLIENT_ID or not CLIENT_SECRET:
        abort(500, 'Set DISCORD_CLIENT_ID and DISCORD_CLIENT_SECRET in .env')
    state = secrets.token_urlsafe(24)
    session['oauth_state'] = state
    params = {'client_id': CLIENT_ID, 'redirect_uri': REDIRECT_URI, 'response_type': 'code', 'scope': 'identify guilds', 'state': state}
    from urllib.parse import urlencode
    return redirect('https://discord.com/oauth2/authorize?' + urlencode(params))


@app.get('/callback')
def callback():
    if request.args.get('state') != session.get('oauth_state') or not request.args.get('code'):
        abort(400, 'Invalid OAuth state')
    token_response = requests.post(API + '/oauth2/token', data={
        'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET, 'grant_type': 'authorization_code',
        'code': request.args['code'], 'redirect_uri': REDIRECT_URI
    }, headers={'Content-Type': 'application/x-www-form-urlencoded'}, timeout=15)
    if token_response.status_code != 200:
        abort(502, 'Discord OAuth token exchange failed')
    token = token_response.json()['access_token']
    me = discord_request('/users/@me', token)
    if me.status_code != 200:
        abort(502, 'Could not retrieve Discord profile')
    session.clear()
    session['access_token'] = token
    session['user'] = me.json()
    return redirect(url_for('home'))


@app.post('/settings/<guild_id>')
def save_settings(guild_id):
    if not session.get('user'):
        return redirect(url_for('login'))
    guilds = current_guilds()
    if not any(g['id'] == guild_id for g in guilds):
        abort(403)
    settings = {k: (k in request.form) for k in ('anti_spam', 'mass_mention', 'invite_filter')}
    save_json(guild_id, settings)
    return redirect(url_for('home', guild_id=guild_id))


@app.get('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('DASHBOARD_PORT', '8080')), debug=False)
