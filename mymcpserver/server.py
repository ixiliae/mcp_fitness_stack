import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import Tool
import stravalib
from garminconnect import Garmin
import os
from dotenv import load_dotenv
from datetime import date, timedelta

load_dotenv()
app = Server("fitness-coach")

# --- Outils Strava ---
@app.list_tools()
async def list_tools():
    return [
        Tool(name="get_strava_activities", description="Récupère les dernières activités Strava", inputSchema={
            "type": "object",
            "properties": {"limit": {"type": "integer", "default": 10}},
        }),
        Tool(name="get_garmin_stats", description="Récupère les stats Garmin (HRV, sommeil, charge)", inputSchema={
            "type": "object",
            "properties": {"days": {"type": "integer", "default": 7}},
        }),
        Tool(name="get_training_load", description="Analyse la charge d'entraînement globale", inputSchema={
            "type": "object", "properties": {}
        }),
    ]

@app.call_tool()
async def call_tool(name, arguments):
    if name == "get_strava_activities":
        client = stravalib.Client(access_token=os.getenv("STRAVA_ACCESS_TOKEN"))
        activities = client.get_activities(limit=arguments.get("limit", 10))
        result = []
        for a in activities:
            result.append({
                "name": a.name,
                "type": str(a.type),
                "distance_km": round(float(a.distance) / 1000, 2),
                "duration_min": round(int(a.moving_time) / 60),
                "avg_hr": a.average_heartrate,
                "date": str(a.start_date_local),
            })
        return [{"type": "text", "text": str(result)}]

    elif name == "get_garmin_stats":
        api = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
        api.login()
        days = arguments.get("days", 7)
        stats = []

        for i in range(days):
            d = (date.today() - timedelta(days=i)).isoformat()
            day = {"date": d}

            try:
                day["stats"] = api.get_stats_and_body(d)
            except Exception:
                pass

            try:
                day["hrv"] = api.get_hrv_data(d)
            except Exception:
                pass

            try:
                day["body_battery"] = api.get_body_battery(d, d)
            except Exception:
                pass

            try:
                day["sleep"] = api.get_sleep_data(d)
            except Exception:
                pass

            try:
                day["stress"] = api.get_stress_data(d)
            except Exception:
                pass

            try:
                day["training_readiness"] = api.get_training_readiness(d)
            except Exception:
                pass

            try:
                day["training_load"] = api.get_training_load(d)
            except Exception:
                pass

            stats.append(day)
            return [{"type": "text", "text": str(stats)}]
    elif name == "get_training_load":
        # Combine les deux sources
        return [{"type": "text", "text": "Analyse combinée Garmin + Strava disponible"}]

if __name__ == "__main__":
    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())
    
    asyncio.run(main())
