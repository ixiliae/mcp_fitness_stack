import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import Tool
import stravalib
import os
from dotenv import load_dotenv

load_dotenv()
app = Server("strava-mcp")


def _strava_client():
    return stravalib.Client(access_token=os.getenv("STRAVA_ACCESS_TOKEN"))


@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="get_strava_activities",
            description="List recent Strava activities",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 10},
                },
            },
        ),
        Tool(
            name="get_strava_activity",
            description="Get full detail of a specific Strava activity by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "activity_id": {"type": "integer"},
                },
                "required": ["activity_id"],
            },
        ),
        Tool(
            name="get_strava_athlete_stats",
            description="Get athlete cumulative stats: recent, year-to-date, and all-time totals per sport",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_strava_streams",
            description="Get time-series streams for an activity (heartrate, watts, velocity, cadence, altitude)",
            inputSchema={
                "type": "object",
                "properties": {
                    "activity_id": {"type": "integer"},
                    "types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["heartrate", "velocity_smooth", "cadence", "altitude", "watts"],
                    },
                },
                "required": ["activity_id"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name, arguments):
    if name == "get_strava_activities":
        client = _strava_client()
        activities = client.get_activities(limit=arguments.get("limit", 10))
        result = []
        for a in activities:
            result.append({
                "id": a.id,
                "name": a.name,
                "type": str(a.sport_type),
                "date": str(a.start_date_local),
                "distance_km": round(float(a.distance) / 1000, 2) if a.distance else None,
                "duration_min": round(int(a.moving_time) / 60) if a.moving_time else None,
                "elevation_gain_m": round(float(a.total_elevation_gain)) if a.total_elevation_gain else None,
                "avg_hr": a.average_heartrate,
                "max_hr": a.max_heartrate,
                "avg_watts": a.average_watts,
                "avg_cadence": a.average_cadence,
                "calories": getattr(a, "calories", None),
            })
        return [{"type": "text", "text": str(result)}]

    elif name == "get_strava_activity":
        client = _strava_client()
        a = client.get_activity(arguments["activity_id"])
        detail = {
            "id": a.id,
            "name": a.name,
            "type": str(a.sport_type),
            "date": str(a.start_date_local),
            "distance_km": round(float(a.distance) / 1000, 2) if a.distance else None,
            "moving_time_min": round(int(a.moving_time) / 60) if a.moving_time else None,
            "elapsed_time_min": round(int(a.elapsed_time) / 60) if a.elapsed_time else None,
            "elevation_gain_m": round(float(a.total_elevation_gain)) if a.total_elevation_gain else None,
            "avg_speed_kmh": round(float(a.average_speed) * 3.6, 2) if a.average_speed else None,
            "max_speed_kmh": round(float(a.max_speed) * 3.6, 2) if a.max_speed else None,
            "avg_hr": a.average_heartrate,
            "max_hr": a.max_heartrate,
            "avg_watts": a.average_watts,
            "max_watts": a.max_watts,
            "avg_cadence": a.average_cadence,
            "calories": a.calories,
            "description": a.description,
            "kudos": a.kudos_count,
            "suffer_score": a.suffer_score,
        }
        if a.laps:
            detail["laps"] = [
                {
                    "lap": i + 1,
                    "distance_km": round(float(lap.distance) / 1000, 2) if lap.distance else None,
                    "duration_min": round(int(lap.moving_time) / 60) if lap.moving_time else None,
                    "avg_hr": lap.average_heartrate,
                    "avg_watts": lap.average_watts,
                }
                for i, lap in enumerate(a.laps)
            ]
        return [{"type": "text", "text": str(detail)}]

    elif name == "get_strava_athlete_stats":
        client = _strava_client()
        athlete = client.get_athlete()
        stats = client.get_athlete_stats(athlete.id)

        def totals(t):
            if t is None:
                return None
            return {
                "count": t.count,
                "distance_km": round(float(t.distance) / 1000, 1) if t.distance else None,
                "moving_time_h": round(int(t.moving_time) / 3600, 1) if t.moving_time else None,
                "elevation_gain_m": round(float(t.elevation_gain)) if t.elevation_gain else None,
            }

        result = {
            "recent_run": totals(stats.recent_run_totals),
            "recent_ride": totals(stats.recent_ride_totals),
            "recent_swim": totals(stats.recent_swim_totals),
            "ytd_run": totals(stats.ytd_run_totals),
            "ytd_ride": totals(stats.ytd_ride_totals),
            "ytd_swim": totals(stats.ytd_swim_totals),
            "all_run": totals(stats.all_run_totals),
            "all_ride": totals(stats.all_ride_totals),
            "all_swim": totals(stats.all_swim_totals),
        }
        return [{"type": "text", "text": str(result)}]

    elif name == "get_strava_streams":
        client = _strava_client()
        types = arguments.get("types", ["heartrate", "velocity_smooth", "cadence", "altitude", "watts"])
        streams = client.get_activity_streams(
            arguments["activity_id"],
            types=types,
            resolution="medium",
        )
        result = {key: stream.data for key, stream in streams.items()}
        return [{"type": "text", "text": str(result)}]


if __name__ == "__main__":
    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())

    asyncio.run(main())
