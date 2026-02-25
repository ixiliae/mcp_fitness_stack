# MCP Fitness Stack

A collection of [Model Context Protocol](https://modelcontextprotocol.io) servers that connect Claude Desktop to fitness tracking platforms.
Fully AI Slop

## Servers

| Server | Source | Description |
|--------|--------|-------------|
| `fitness-coach` | `stravamcpserver/` | Strava activities and stats |
| `garmin` | External (uvx) | Full Garmin Connect integration |
| `hevy` | External (npx) | Hevy strength training log |

---

## Setup

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (for the `garmin` server)
- Node.js + npx (for the `hevy` server)
- Claude Desktop

---

### 1. fitness-coach (stravamcpserver)

Pulls Strava activities, athlete stats, and time-series streams via the Strava API.

```bash
cd stravamcpserver
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Copy the env template and fill in your credentials:

```bash
cp .env.example .env
```

**Getting a Strava access token:**

Set `STRAVA_CLIENT_ID` and `STRAVA_CLIENT_SECRET` in `.env` (from [Strava API settings](https://www.strava.com/settings/api)), then run:

```bash
python strava_auth.py
```

This will open a browser, handle the OAuth flow, and print your `STRAVA_ACCESS_TOKEN`. Copy it into `.env`.

---

### 2. garmin (external, via uvx)

Installed on-demand from GitHub — no local setup required. The server authenticates via a Garmin MFA flow on first run and caches tokens locally.

The `uvx` binary is typically at `~/.local/bin/uvx`. Find it with:

```bash
which uvx
```

---

### 3. hevy (external, via npx)

Installed on-demand from npm — no local setup required. Requires a [Hevy PRO](https://hevy.com) subscription and an API key from the Hevy app settings.

---

## Claude Desktop Configuration

Copy the example config and fill in your values:

```bash
cp claude_desktop_config.json.example claude_desktop_config.json.local
```

Then adapt it and place the final config at:

- **Linux:** `~/.config/Claude/claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Replace all `<placeholders>` in the example:

| Placeholder | Value |
|-------------|-------|
| `<REPO_PATH>` | Absolute path to this repo (e.g. `/home/user/mcp-fitness-stack`) |
| `<path-to-uvx>` | Output of `which uvx` |
| `<your-strava-access-token>` | From `strava_auth.py` |
| `<your-hevy-api-key>` | From Hevy app settings |

---

## Security

- `.env` files are git-ignored. **Never commit them.**
- The `claude_desktop_config.json` also contains secrets — keep it local.
- `claude_desktop_config.json.example` and `.env.example` files are the only safe-to-commit credential references.
