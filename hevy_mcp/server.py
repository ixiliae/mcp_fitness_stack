#!/usr/bin/env python3
"""
Hevy MCP Server
A Model Context Protocol server for the Hevy fitness tracking API.
Requires a Hevy PRO subscription and API key from https://hevy.com/settings?developer
"""

import os
import json
from typing import Any, Optional
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("Hevy Fitness Tracker")

# Base URL for Hevy API
BASE_URL = "https://api.hevyapp.com/v1"


def get_client() -> httpx.Client:
    """Create an HTTP client with Hevy API authentication."""
    api_key = os.environ.get("HEVY_API_KEY")
    if not api_key:
        raise ValueError(
            "HEVY_API_KEY environment variable is not set. "
            "Get your key at https://hevy.com/settings?developer"
        )
    return httpx.Client(
        base_url=BASE_URL,
        headers={
            "api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        timeout=30.0,
    )


def api_get(path: str, params: dict = None) -> dict:
    """Perform a GET request to the Hevy API."""
    with get_client() as client:
        response = client.get(path, params=params)
        response.raise_for_status()
        return response.json()


def api_post(path: str, data: dict) -> dict:
    """Perform a POST request to the Hevy API."""
    with get_client() as client:
        response = client.post(path, json=data)
        response.raise_for_status()
        return response.json()


def api_put(path: str, data: dict) -> dict:
    """Perform a PUT request to the Hevy API."""
    with get_client() as client:
        response = client.put(path, json=data)
        response.raise_for_status()
        return response.json()


def api_delete(path: str) -> dict:
    """Perform a DELETE request to the Hevy API."""
    with get_client() as client:
        response = client.delete(path)
        response.raise_for_status()
        if response.content:
            return response.json()
        return {"success": True}


# ─── WORKOUT TOOLS ─────────────────────────────────────────────────────────────

@mcp.tool()
def get_workouts(page: int = 1, page_size: int = 10) -> str:
    """
    Fetch a paginated list of workouts from your Hevy training log.
    
    Args:
        page: Page number (default: 1)
        page_size: Number of workouts per page (max 10, default: 10)
    
    Returns:
        JSON list of workouts with exercises, sets, reps, weight, and timestamps.
    """
    data = api_get("/workouts", params={"page": page, "pageSize": page_size})
    return json.dumps(data, indent=2)


@mcp.tool()
def get_workout_count() -> str:
    """
    Get the total number of workouts logged in your Hevy account.
    
    Returns:
        JSON with the total workout count.
    """
    data = api_get("/workouts/count")
    return json.dumps(data, indent=2)


@mcp.tool()
def get_workout(workout_id: str) -> str:
    """
    Get detailed information about a specific workout by its ID.
    
    Args:
        workout_id: The unique identifier of the workout.
    
    Returns:
        JSON with full workout details including all exercises and sets.
    """
    data = api_get(f"/workouts/{workout_id}")
    return json.dumps(data, indent=2)


@mcp.tool()
def create_workout(
    title: str,
    start_time: str,
    end_time: str,
    exercises: str,
    description: str = ""
) -> str:
    """
    Create a new workout session in Hevy.
    
    Args:
        title: Name of the workout (e.g., "Push Day", "Leg Day").
        start_time: ISO 8601 start datetime (e.g., "2024-01-15T09:00:00+00:00").
        end_time: ISO 8601 end datetime (e.g., "2024-01-15T10:30:00+00:00").
        exercises: JSON string array of exercises. Each exercise object must have:
                   - exercise_template_id (string): ID from get_exercise_templates
                   - superset_id (null or int): null for standalone exercises
                   - notes (string): exercise notes
                   - sets (array): each set has type ("normal","warmup","failure","dropset"),
                     weight_kg (float|null), reps (int|null), distance_meters (float|null),
                     duration_seconds (int|null), rpe (float|null)
                   Example: '[{"exercise_template_id":"abc123","superset_id":null,"notes":"","sets":[{"type":"normal","weight_kg":80,"reps":10,"distance_meters":null,"duration_seconds":null,"rpe":null}]}]'
        description: Optional workout description/notes.
    
    Returns:
        JSON with the created workout data.
    """
    exercises_data = json.loads(exercises)
    payload = {
        "workout": {
            "title": title,
            "description": description,
            "start_time": start_time,
            "end_time": end_time,
            "exercises": exercises_data,
        }
    }
    data = api_post("/workouts", payload)
    return json.dumps(data, indent=2)


@mcp.tool()
def update_workout(
    workout_id: str,
    title: str,
    start_time: str,
    end_time: str,
    exercises: str,
    description: str = ""
) -> str:
    """
    Update an existing workout in Hevy.
    
    Args:
        workout_id: The unique identifier of the workout to update.
        title: Updated name of the workout.
        start_time: ISO 8601 start datetime.
        end_time: ISO 8601 end datetime.
        exercises: JSON string array of exercises (same format as create_workout).
        description: Optional updated description.
    
    Returns:
        JSON with the updated workout data.
    """
    exercises_data = json.loads(exercises)
    payload = {
        "workout": {
            "title": title,
            "description": description,
            "start_time": start_time,
            "end_time": end_time,
            "exercises": exercises_data,
        }
    }
    data = api_put(f"/workouts/{workout_id}", payload)
    return json.dumps(data, indent=2)


# ─── ROUTINE TOOLS ──────────────────────────────────────────────────────────────

@mcp.tool()
def get_routines(page: int = 1, page_size: int = 10) -> str:
    """
    Fetch all workout routines saved in your Hevy account.
    
    Args:
        page: Page number (default: 1)
        page_size: Number of routines per page (default: 10)
    
    Returns:
        JSON list of routines with exercises and sets.
    """
    data = api_get("/routines", params={"page": page, "pageSize": page_size})
    return json.dumps(data, indent=2)


@mcp.tool()
def get_routine(routine_id: str) -> str:
    """
    Get a specific workout routine by its ID.
    
    Args:
        routine_id: The unique identifier of the routine.
    
    Returns:
        JSON with the full routine including all exercises, sets, and notes.
    """
    data = api_get(f"/routines/{routine_id}")
    return json.dumps(data, indent=2)


@mcp.tool()
def create_routine(
    title: str,
    exercises: str,
    folder_id: Optional[int] = None,
    notes: str = ""
) -> str:
    """
    Create a new workout routine in Hevy.
    
    Args:
        title: Name of the routine (e.g., "Push A", "Upper Body").
        exercises: JSON string array of exercises. Each must have:
                   - exercise_template_id (string): from get_exercise_templates
                   - superset_id (null or int)
                   - notes (string)
                   - sets (array): each with type, weight_kg, reps, distance_meters,
                     duration_seconds, rpe
                   Example: '[{"exercise_template_id":"abc123","superset_id":null,"notes":"","sets":[{"type":"normal","weight_kg":100,"reps":5,"distance_meters":null,"duration_seconds":null,"rpe":null}]}]'
        folder_id: Optional ID of the folder to save the routine in.
        notes: Optional routine-level notes.
    
    Returns:
        JSON with the created routine data.
    """
    exercises_data = json.loads(exercises)
    payload = {
        "routine": {
            "title": title,
            "notes": notes,
            "exercises": exercises_data,
        }
    }
    if folder_id is not None:
        payload["routine"]["folder_id"] = folder_id
    data = api_post("/routines", payload)
    return json.dumps(data, indent=2)


@mcp.tool()
def update_routine(
    routine_id: str,
    title: str,
    exercises: str,
    folder_id: Optional[int] = None,
    notes: str = ""
) -> str:
    """
    Update an existing workout routine in Hevy.
    
    Args:
        routine_id: The unique identifier of the routine to update.
        title: Updated routine name.
        exercises: JSON string array of exercises (same format as create_routine).
        folder_id: Optional folder ID to move the routine to.
        notes: Optional updated notes.
    
    Returns:
        JSON with the updated routine data.
    """
    exercises_data = json.loads(exercises)
    payload = {
        "routine": {
            "title": title,
            "notes": notes,
            "exercises": exercises_data,
        }
    }
    if folder_id is not None:
        payload["routine"]["folder_id"] = folder_id
    data = api_put(f"/routines/{routine_id}", payload)
    return json.dumps(data, indent=2)


# ─── EXERCISE TEMPLATE TOOLS ────────────────────────────────────────────────────

@mcp.tool()
def get_exercise_templates(page: int = 1, page_size: int = 20) -> str:
    """
    Fetch available exercise templates from Hevy's library.
    Use the returned template IDs when creating workouts or routines.
    
    Args:
        page: Page number (default: 1)
        page_size: Number of templates per page (default: 20, max 100)
    
    Returns:
        JSON list of exercise templates with IDs, names, muscle groups, and equipment.
    """
    data = api_get("/exercise_templates", params={"page": page, "pageSize": page_size})
    return json.dumps(data, indent=2)


@mcp.tool()
def get_exercise_template(template_id: str) -> str:
    """
    Get details about a specific exercise template by its ID.
    
    Args:
        template_id: The unique identifier of the exercise template.
    
    Returns:
        JSON with exercise details including muscles targeted and equipment.
    """
    data = api_get(f"/exercise_templates/{template_id}")
    return json.dumps(data, indent=2)


# ─── ROUTINE FOLDER TOOLS ───────────────────────────────────────────────────────

@mcp.tool()
def get_routine_folders(page: int = 1, page_size: int = 10) -> str:
    """
    Fetch all routine folders used to organize your workout routines.
    
    Args:
        page: Page number (default: 1)
        page_size: Number of folders per page (default: 10)
    
    Returns:
        JSON list of routine folders with their IDs and names.
    """
    data = api_get("/routine_folders", params={"page": page, "pageSize": page_size})
    return json.dumps(data, indent=2)


@mcp.tool()
def get_routine_folder(folder_id: int) -> str:
    """
    Get a specific routine folder by its ID.
    
    Args:
        folder_id: The unique identifier of the folder.
    
    Returns:
        JSON with the folder details.
    """
    data = api_get(f"/routine_folders/{folder_id}")
    return json.dumps(data, indent=2)


@mcp.tool()
def create_routine_folder(title: str) -> str:
    """
    Create a new folder to organize your workout routines.
    
    Args:
        title: Name of the folder (e.g., "Push Pull Legs", "Strength Program").
    
    Returns:
        JSON with the created folder data including its ID.
    """
    payload = {"routine_folder": {"title": title}}
    data = api_post("/routine_folders", payload)
    return json.dumps(data, indent=2)


@mcp.tool()
def update_routine_folder(folder_id: int, title: str) -> str:
    """
    Update the name of an existing routine folder.
    
    Args:
        folder_id: The unique identifier of the folder to update.
        title: New name for the folder.
    
    Returns:
        JSON with the updated folder data.
    """
    payload = {"routine_folder": {"title": title}}
    data = api_put(f"/routine_folders/{folder_id}", payload)
    return json.dumps(data, indent=2)


@mcp.tool()
def delete_routine_folder(folder_id: int) -> str:
    """
    Delete a routine folder. Note: This may also affect routines in the folder.
    
    Args:
        folder_id: The unique identifier of the folder to delete.
    
    Returns:
        JSON confirming deletion.
    """
    data = api_delete(f"/routine_folders/{folder_id}")
    return json.dumps(data, indent=2)


# ─── ANALYSIS HELPER TOOLS ──────────────────────────────────────────────────────

@mcp.tool()
def analyze_recent_workouts(days: int = 7) -> str:
    """
    Analyze recent workouts by fetching the latest data and computing summary stats.
    Shows total volume, frequency, and exercises performed in the last N days.
    
    Args:
        days: Number of days to analyze (default: 7)
    
    Returns:
        A formatted text summary of recent training activity.
    """
    from datetime import datetime, timedelta, timezone
    
    # Fetch recent workouts (grab more pages to ensure coverage)
    all_workouts = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    for page in range(1, 6):  # up to 50 workouts
        data = api_get("/workouts", params={"page": page, "pageSize": 10})
        workouts = data.get("workouts", [])
        if not workouts:
            break
        
        for w in workouts:
            start = w.get("start_time", "")
            if start:
                try:
                    wdate = datetime.fromisoformat(start.replace("Z", "+00:00"))
                    if wdate >= cutoff:
                        all_workouts.append(w)
                    elif wdate < cutoff:
                        break  # Workouts are newest-first, so stop here
                except Exception:
                    continue
        else:
            continue
        break  # inner break triggered
    
    if not all_workouts:
        return f"No workouts found in the last {days} days."
    
    # Build summary
    lines = [f"📊 **Training Summary — Last {days} days**", ""]
    lines.append(f"Total workouts: {len(all_workouts)}")
    
    total_sets = 0
    total_volume_kg = 0.0
    exercise_counts: dict[str, int] = {}
    
    for w in all_workouts:
        title = w.get("title", "Untitled")
        wdate = w.get("start_time", "")[:10]
        exercises = w.get("exercises", [])
        
        for ex in exercises:
            ex_title = ex.get("title", "Unknown")
            exercise_counts[ex_title] = exercise_counts.get(ex_title, 0) + 1
            for s in ex.get("sets", []):
                total_sets += 1
                kg = s.get("weight_kg") or 0
                reps = s.get("reps") or 0
                total_volume_kg += kg * reps
    
    lines.append(f"Total sets: {total_sets}")
    lines.append(f"Total volume: {total_volume_kg:,.1f} kg")
    lines.append("")
    lines.append("**Workouts:**")
    for w in all_workouts:
        title = w.get("title", "Untitled")
        wdate = w.get("start_time", "")[:10]
        ex_count = len(w.get("exercises", []))
        lines.append(f"  • {wdate} — {title} ({ex_count} exercises)")
    
    if exercise_counts:
        lines.append("")
        lines.append("**Most frequent exercises:**")
        sorted_ex = sorted(exercise_counts.items(), key=lambda x: -x[1])[:10]
        for ex, count in sorted_ex:
            lines.append(f"  • {ex}: {count}x")
    
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
