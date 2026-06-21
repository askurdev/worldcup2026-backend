"""
API-Football v3 Provider
========================
Real implementation of FootballDataProvider using api-sports.io v3.

World Cup 2026 constants:
  League ID : 1   (FIFA World Cup)
  Season    : 2026

Free tier: 100 requests/day → we cache aggressively and batch
calls so a normal day of browsing stays well under the limit.

Set in .env:
  FOOTBALL_DATA_PROVIDER=api_football
  API_FOOTBALL_KEY=your_key_here
"""

import logging
import urllib.request
import urllib.parse
import json
from datetime import datetime, timezone
from typing import Optional

from app.core.config import settings
from app.db.cache import cache_get, cache_set

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────
WC_LEAGUE_ID = 1
WC_SEASON = 2026
BASE_URL = "https://v3.football.api-sports.io"

# Cache TTLs (seconds) — tuned to stay under 100 req/day free limit
TTL_FIXTURES = 300      # 5 min  — fixtures list
TTL_LIVE = 60           # 1 min  — live scores (most precious requests)
TTL_STANDINGS = 600     # 10 min — standings change slowly
TTL_PLAYERS = 3600      # 1 hr   — player stats rarely change mid-day
TTL_TEAMS = 86400       # 24 hr  — team info never changes


# ── HTTP helper ──────────────────────────────────────────────

def _get(endpoint: str, params: dict) -> dict:
    """
    Make one API-Football request. Returns the parsed JSON dict.
    Raises on HTTP/network error so callers can handle gracefully.
    """
    qs = urllib.parse.urlencode(params)
    url = f"{BASE_URL}/{endpoint}?{qs}"
    req = urllib.request.Request(
        url,
        headers={"x-apisports-key": settings.API_FOOTBALL_KEY},
    )
    logger.debug("API-Football → %s?%s", endpoint, qs)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


def _get_cached(cache_key: str, endpoint: str, params: dict, ttl: int) -> Optional[dict]:
    """Return cached result or fetch and cache it."""
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    try:
        data = _get(endpoint, params)
        cache_set(cache_key, data, ttl=ttl)
        return data
    except Exception as exc:
        logger.error("API-Football error [%s]: %s", endpoint, exc)
        return None


# ── Public fetcher functions (used by services) ──────────────

def fetch_fixtures(status: Optional[str] = None) -> list[dict]:
    """
    Fetch all WC 2026 fixtures, optionally filtered by status.
    status values: "NS" (not started) | "1H","2H","HT" (live) | "FT" (finished)
    """
    params: dict = {"league": WC_LEAGUE_ID, "season": WC_SEASON}
    if status:
        params["status"] = status

    cache_key = f"apif:fixtures:{status or 'all'}"
    data = _get_cached(cache_key, "fixtures", params, TTL_FIXTURES)
    if not data:
        return []
    return data.get("response", [])


def fetch_live_fixtures() -> list[dict]:
    """Fetch currently live WC 2026 fixtures — shortest TTL."""
    cache_key = "apif:fixtures:live"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    try:
        data = _get("fixtures", {"league": WC_LEAGUE_ID, "season": WC_SEASON, "live": "all"})
        result = data.get("response", [])
        cache_set(cache_key, result, ttl=TTL_LIVE)
        return result
    except Exception as exc:
        logger.error("API-Football live error: %s", exc)
        return []


def fetch_fixture_by_id(fixture_id: int) -> Optional[dict]:
    """Fetch full details (events, lineups, stats) for one fixture."""
    cache_key = f"apif:fixture:{fixture_id}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    try:
        data = _get("fixtures", {"id": fixture_id})
        resp = data.get("response", [])
        result = resp[0] if resp else None
        if result:
            cache_set(cache_key, result, ttl=TTL_FIXTURES)
        return result
    except Exception as exc:
        logger.error("API-Football fixture %d error: %s", fixture_id, exc)
        return None


def fetch_standings() -> list[dict]:
    """Fetch group standings for WC 2026."""
    cache_key = "apif:standings"
    data = _get_cached(
        cache_key, "standings",
        {"league": WC_LEAGUE_ID, "season": WC_SEASON},
        TTL_STANDINGS,
    )
    if not data:
        return []
    resp = data.get("response", [])
    if not resp:
        return []
    # standings response: [{ league: { standings: [[...],[...]] } }]
    try:
        return resp[0]["league"]["standings"]
    except (IndexError, KeyError):
        return []


def fetch_teams() -> list[dict]:
    """Fetch all teams participating in WC 2026."""
    cache_key = "apif:teams"
    data = _get_cached(
        cache_key, "teams",
        {"league": WC_LEAGUE_ID, "season": WC_SEASON},
        TTL_TEAMS,
    )
    return data.get("response", []) if data else []


def fetch_top_scorers() -> list[dict]:
    """Fetch top scorers for WC 2026 (used for player stats)."""
    cache_key = "apif:topscorers"
    data = _get_cached(
        cache_key, "players/topscorers",
        {"league": WC_LEAGUE_ID, "season": WC_SEASON},
        TTL_PLAYERS,
    )
    return data.get("response", []) if data else []


# ── Converter helpers ─────────────────────────────────────────
# These map the raw API-Football JSON shapes to our app's schema
# (same field names used by MockFootballDataProvider so the
# frontend never needs to change when we swap providers).

def convert_fixture_to_match(f: dict) -> dict:
    """
    Convert one API-Football fixture object to our Match schema dict.
    """
    fix = f.get("fixture", {})
    teams = f.get("teams", {})
    goals = f.get("goals", {})
    league = f.get("league", {})

    # Map API-Football status codes to our status strings
    status_code = fix.get("status", {}).get("short", "NS")
    status_map = {
        "NS": "scheduled",
        "1H": "live",
        "2H": "live",
        "HT": "halftime",
        "FT": "completed",
        "AET": "completed",
        "PEN": "completed",
        "PST": "postponed",
        "CANC": "cancelled",
        "TBD": "scheduled",
    }
    status = status_map.get(status_code, "scheduled")

    # Kickoff time — API returns Unix timestamp
    kickoff_ts = fix.get("timestamp")
    kickoff_utc = (
        datetime.fromtimestamp(kickoff_ts, tz=timezone.utc).isoformat()
        if kickoff_ts else None
    )

    venue = fix.get("venue", {})

    home = teams.get("home", {})
    away = teams.get("away", {})

    return {
        "id": str(fix.get("id", "")),
        "match_number": fix.get("id", 0),  # use fixture id as match number
        "stage": _map_round_to_stage(league.get("round", "")),
        "group": _extract_group(league.get("round", "")),
        "status": status,
        "kickoff_utc": kickoff_utc,
        "minute": fix.get("status", {}).get("elapsed"),
        "home_team": {
            "id": str(home.get("id", "")),
            "name": home.get("name", ""),
            "short_name": home.get("name", "")[:12],
            "slug": _slugify(home.get("name", "")),
            "fifa_code": home.get("name", "")[:3].upper(),
            "flag_url": home.get("logo", ""),
            "group": _extract_group(league.get("round", "")),
            "confederation": "",
            "coach_name": "",
            "fifa_ranking": 0,
            "is_host": False,
        },
        "away_team": {
            "id": str(away.get("id", "")),
            "name": away.get("name", ""),
            "short_name": away.get("name", "")[:12],
            "slug": _slugify(away.get("name", "")),
            "fifa_code": away.get("name", "")[:3].upper(),
            "flag_url": away.get("logo", ""),
            "group": _extract_group(league.get("round", "")),
            "confederation": "",
            "coach_name": "",
            "fifa_ranking": 0,
            "is_host": False,
        },
        "home_score": goals.get("home") or 0,
        "away_score": goals.get("away") or 0,
        "venue": {
            "id": str(venue.get("id", "")),
            "name": venue.get("name", "Unknown"),
            "city": venue.get("city", ""),
            "country": "USA",
            "capacity": 0,
            "timezone": _city_to_timezone(venue.get("city", "")),
        },
        "referee": fix.get("referee", "TBD"),
    }


def convert_events(f: dict, home_team_id: str) -> dict:
    """Convert fixture events to our MatchEvents schema."""
    events = f.get("events", [])
    goals, cards, subs = [], [], []

    for ev in events:
        team_id = str(ev.get("team", {}).get("id", ""))
        minute = ev.get("time", {}).get("elapsed", 0)
        player = ev.get("player", {})
        assist = ev.get("assist", {})
        ev_type = ev.get("type", "")
        detail = ev.get("detail", "")

        if ev_type == "Goal":
            goals.append({
                "id": f"g-{team_id}-{minute}",
                "minute": minute,
                "player_id": str(player.get("id", "")),
                "player_name": player.get("name", ""),
                "team_id": team_id,
                "is_penalty": detail == "Penalty",
                "is_own_goal": detail == "Own Goal",
                "assist_player_id": str(assist.get("id", "")) if assist.get("id") else None,
                "assist_player_name": assist.get("name"),
            })
        elif ev_type == "Card":
            cards.append({
                "id": f"c-{team_id}-{minute}",
                "minute": minute,
                "player_id": str(player.get("id", "")),
                "player_name": player.get("name", ""),
                "team_id": team_id,
                "card_type": "yellow" if "Yellow" in detail else "red",
            })
        elif ev_type == "subst":
            assist_name = assist.get("name", "")
            subs.append({
                "id": f"s-{team_id}-{minute}",
                "minute": minute,
                "team_id": team_id,
                "player_out_id": str(player.get("id", "")),
                "player_out_name": player.get("name", ""),
                "player_in_id": str(assist.get("id", "")),
                "player_in_name": assist_name,
            })

    return {"goals": goals, "cards": cards, "substitutions": subs}


def convert_stats(f: dict) -> dict:
    """Convert fixture statistics to our MatchStats schema."""
    stats_list = f.get("statistics", [])

    def get_stat(stats: list, name: str) -> int:
        for s in stats:
            if s.get("type") == name:
                val = s.get("value")
                if val is None:
                    return 0
                if isinstance(val, str) and val.endswith("%"):
                    return int(val.replace("%", ""))
                return int(val) if val else 0
        return 0

    home_stats = stats_list[0].get("statistics", []) if len(stats_list) > 0 else []
    away_stats = stats_list[1].get("statistics", []) if len(stats_list) > 1 else []

    return {
        "possession": {
            "home": get_stat(home_stats, "Ball Possession"),
            "away": get_stat(away_stats, "Ball Possession"),
        },
        "shots": {
            "home": get_stat(home_stats, "Total Shots"),
            "away": get_stat(away_stats, "Total Shots"),
        },
        "shots_on_target": {
            "home": get_stat(home_stats, "Shots on Goal"),
            "away": get_stat(away_stats, "Shots on Goal"),
        },
        "corners": {
            "home": get_stat(home_stats, "Corner Kicks"),
            "away": get_stat(away_stats, "Corner Kicks"),
        },
        "fouls": {
            "home": get_stat(home_stats, "Fouls"),
            "away": get_stat(away_stats, "Fouls"),
        },
        "offsides": {
            "home": get_stat(home_stats, "Offsides"),
            "away": get_stat(away_stats, "Offsides"),
        },
        "passes": {
            "home": get_stat(home_stats, "Total passes"),
            "away": get_stat(away_stats, "Total passes"),
        },
        "pass_accuracy": {
            "home": get_stat(home_stats, "Passes %"),
            "away": get_stat(away_stats, "Passes %"),
        },
    }


# ── Internal helpers ──────────────────────────────────────────

def _map_round_to_stage(round_str: str) -> str:
    r = round_str.lower()
    if "group" in r:
        return "group"
    if "32" in r:
        return "round_of_32"
    if "16" in r:
        return "round_of_16"
    if "quarter" in r:
        return "quarter_final"
    if "semi" in r:
        return "semi_final"
    if "3rd" in r or "third" in r:
        return "third_place"
    if "final" in r:
        return "final"
    return "group"


def _extract_group(round_str: str) -> Optional[str]:
    """Extract 'A' from 'Group Stage - A' etc."""
    if "group" in round_str.lower():
        parts = round_str.split(" - ")
        if len(parts) > 1:
            return parts[-1].strip()
        parts = round_str.split("-")
        if len(parts) > 1:
            return parts[-1].strip()
    return None


def _slugify(name: str) -> str:
    return name.lower().replace(" ", "-").replace(".", "").replace("'", "")


def _city_to_timezone(city: str) -> str:
    """Best-effort city → IANA timezone mapping for WC 2026 host cities."""
    mapping = {
        "New York": "America/New_York",
        "New Jersey": "America/New_York",
        "Dallas": "America/Chicago",
        "Los Angeles": "America/Los_Angeles",
        "Atlanta": "America/New_York",
        "Miami": "America/New_York",
        "Philadelphia": "America/New_York",
        "Kansas City": "America/Chicago",
        "San Francisco": "America/Los_Angeles",
        "Seattle": "America/Los_Angeles",
        "Mexico City": "America/Mexico_City",
        "Monterrey": "America/Monterrey",
        "Vancouver": "America/Vancouver",
        "Toronto": "America/Toronto",
    }
    for key, tz in mapping.items():
        if key.lower() in city.lower():
            return tz
    return "America/New_York"  # default
