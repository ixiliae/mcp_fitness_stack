# Hevy MCP Server 🏋️

A [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) server that connects AI assistants to your **Hevy** fitness tracking account.

> Built on top of the [hevy-api](https://github.com/remuzel/hevy-api) Python client and the official [Hevy API](https://api.hevyapp.com/docs).

---

## Features

| Category | Tools |
|---|---|
| 💪 **Workouts** | Get, create, update workouts + count |
| 📋 **Routines** | Get, create, update routines |
| 🗂️ **Folders** | Create, update, delete routine folders |
| 🔍 **Exercise Templates** | Browse Hevy's 400+ exercise library |
| 📊 **Analysis** | Analyze recent training (volume, frequency) |

---

## Prerequisites

- **Hevy PRO** subscription
- API key from [https://hevy.com/settings?developer](https://hevy.com/settings?developer)
- Python 3.11+

---

## Installation

```bash
# Clone this repo
git clone <this-repo>
cd hevy-mcp

# Install dependencies
pip install mcp httpx

# Set your API key
export HEVY_API_KEY="your_api_key_here"

# Run the server
python src/server.py
```

---

## Claude Desktop Configuration

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "hevy": {
      "command": "python",
      "args": ["/absolute/path/to/hevy-mcp/src/server.py"],
      "env": {
        "HEVY_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**Config file locations:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

---

## Available MCP Tools

### Workout Tools
| Tool | Description |
|---|---|
| `get_workouts` | Paginated list of your workouts |
| `get_workout_count` | Total number of workouts logged |
| `get_workout` | Specific workout by ID |
| `create_workout` | Log a new workout session |
| `update_workout` | Edit an existing workout |

### Routine Tools
| Tool | Description |
|---|---|
| `get_routines` | List all your saved routines |
| `get_routine` | Specific routine by ID |
| `create_routine` | Create a new routine template |
| `update_routine` | Edit an existing routine |

### Exercise Template Tools
| Tool | Description |
|---|---|
| `get_exercise_templates` | Browse Hevy's exercise library (400+) |
| `get_exercise_template` | Specific template by ID |

### Folder Tools
| Tool | Description |
|---|---|
| `get_routine_folders` | List all folders |
| `get_routine_folder` | Specific folder by ID |
| `create_routine_folder` | Create a new folder |
| `update_routine_folder` | Rename a folder |
| `delete_routine_folder` | Delete a folder |

### Analysis Tools
| Tool | Description |
|---|---|
| `analyze_recent_workouts` | Summary stats for last N days |

---

## Example Prompts

Once connected to Claude, you can ask:

- *"Show me my last 5 workouts"*
- *"How many times have I worked out this month?"*
- *"Create a Push/Pull/Legs routine for me"*
- *"Analyze my training from the past 2 weeks"*
- *"Find me exercises that target the chest"*
- *"Log today's workout: 3 sets of bench press at 80kg x 8 reps"*

---

## Exercise JSON Format

When creating or updating workouts/routines, exercises follow this format:

```json
[
  {
    "exercise_template_id": "TEMPLATE_ID_FROM_get_exercise_templates",
    "superset_id": null,
    "notes": "Optional exercise note",
    "sets": [
      {
        "type": "warmup",
        "weight_kg": 60.0,
        "reps": 10,
        "distance_meters": null,
        "duration_seconds": null,
        "rpe": null
      },
      {
        "type": "normal",
        "weight_kg": 80.0,
        "reps": 8,
        "distance_meters": null,
        "duration_seconds": null,
        "rpe": 8.0
      }
    ]
  }
]
```

**Set types:** `"normal"`, `"warmup"`, `"failure"`, `"dropset"`

---

## License

MIT — Based on [hevy-api](https://github.com/remuzel/hevy-api) by [@remuzel](https://github.com/remuzel)
