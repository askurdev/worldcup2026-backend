
"""
Match service — provider-aware.
FOOTBALL_DATA_PROVIDER=api_football → real API-Football data
FOOTBALL_DATA_PROVIDER=mock         → database seeded data (default)
"""

import math
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.db.cache import cache_get, cache_set, cache_delete_pattern
from app.models import Match, Group
from app.schemas.schemas import MatchListResponse, Match as MatchSchema


def get_live_matches(db: Session) -> list:
    if settings.FOOTBALL_DATA_PROVIDER == "api_football":
        return _live_from_api()
    return _live_from_db(db)


def get_today_matches(db: Session) -> list:
    if settings.FOOTBALL_DATA_PROVIDER == "api_football":
        return _today_from_api()
    return _today_from_db(db)


def get_matches(
    db: Session,
    page: int = 1,
    page_size: int = settings.DEFAULT_PAGE_SIZE,
    status: Optional[str] = None,
    stage: Optional[str] = None,
    group: Optional[str] = None,
    team_id: Optional[int] = None,
    sort_by: str = "kickoff_utc",
    sort_order: str = "asc",
) -> MatchListResponse:
    if settings.FOOTBALL_DATA_PROVIDER == "api_football":
        return _matches_from_api(page, page_size, status, group)
    return _matches_from_db(db, page, page_size, status, stage, group, team_id,sort_by, sort_order)


def get_match_by_id(db: Session, match_id: int) -> Optional[Match]:
    return _match_detail_from_db(db, match_id)


def update_match_result(db, match_id, status=None, minute=None,
                        home_score=None, away_score=None,
                        home_penalties=None, away_penalties=None):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        return None
    if status is not None: match.status = status
    if minute is not None: match.minute = minute
    if home_score is not None: match.home_score = home_score
    if away_score is not None: match.away_score = away_score
    if home_penalties is not None: match.home_penalties = home_penalties
    if away_penalties is not None: match.away_penalties = away_penalties
    db.commit()
    db.refresh(match)
    cache_delete_pattern("matches:*")
    cache_delete_pattern(f"match:{match_id}")
    cache_delete_pattern("standings:*")
    cache_delete_pattern("apif:*")
    if status == "completed":
        from scripts.recompute_standings import recompute_all
        recompute_all(db, match.tournament_id)
        db.commit()
    return match


# ── API-Football ──────────────────────────────────────────────

def _live_from_api():
    from app.providers.api_football import fetch_live_fixtures, convert_fixture_to_match
    return [convert_fixture_to_match(f) for f in fetch_live_fixtures()]


def _today_from_api():
    from app.providers.api_football import fetch_fixtures, convert_fixture_to_match
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    fixtures = [
        f for f in fetch_fixtures()
        if f.get("fixture", {}).get("date", "").startswith(today)
    ]
    return [convert_fixture_to_match(f) for f in fixtures]


def _matches_from_api(page, page_size, status, group):
    from app.providers.api_football import fetch_fixtures, convert_fixture_to_match
    status_map = {"scheduled": "NS", "live": "1H", "completed": "FT", "halftime": "HT"}
    api_status = status_map.get(status) if status else None
    fixtures = fetch_fixtures(status=api_status)
    if group:
        fixtures = [f for f in fixtures if group.upper() in f.get("league", {}).get("round", "")]
    converted = [convert_fixture_to_match(f) for f in fixtures]
    total_items = len(converted)
    total_pages = max(1, math.ceil(total_items / page_size))
    start = (page - 1) * page_size
    return MatchListResponse(
        data=converted[start: start + page_size],
        page=page, page_size=page_size,
        total_items=total_items, total_pages=total_pages,
    )


# ── Database (mock/seed data) ─────────────────────────────────

def _load_opts():
    return [joinedload(Match.home_team), joinedload(Match.away_team),
            joinedload(Match.venue), joinedload(Match.group)]


def _live_from_db(db):
    cache_key = "matches:live"
    cached = cache_get(cache_key)
    if cached: return cached
    matches = (db.query(Match).options(*_load_opts())
               .filter(Match.status.in_(["live", "halftime"]))
               .order_by(Match.kickoff_utc).all())
    cache_set(cache_key, [MatchSchema.model_validate(m).model_dump() for m in matches],
              ttl=settings.LIVE_CACHE_TTL_SECONDS)
    return matches


def _today_from_db(db):
    now = datetime.now(timezone.utc)
    cache_key = f"matches:today:{now.strftime('%Y-%m-%d')}"
    cached = cache_get(cache_key)
    if cached: return cached
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = now.replace(hour=23, minute=59, second=59, microsecond=0)
    matches = (db.query(Match).options(*_load_opts())
               .filter(and_(Match.kickoff_utc >= day_start, Match.kickoff_utc <= day_end))
               .order_by(Match.kickoff_utc).all())
    cache_set(cache_key, [MatchSchema.model_validate(m).model_dump() for m in matches], ttl=60)
    return matches


def _matches_from_db(db, page, page_size, status, stage, group, team_id, date_utc, sort_by, sort_order):
    cache_key = f"matches:{page}:{page_size}:{status}:{stage}:{group}:{team_id}:{date_utc}:{sort_by}:{sort_order}"
    cached = cache_get(cache_key)
    if cached: return MatchListResponse(**cached)
    


    

    query = db.query(Match).options(*_load_opts())
    if status: query = query.filter(Match.status == status)
    if stage: query = query.filter(Match.stage == stage)
    if group:
        query = query.join(Group, Match.group_id == Group.id).filter(Group.name == group)
    if team_id:
        query = query.filter(or_(Match.home_team_id == team_id, Match.away_team_id == team_id))
    sort_col = Match.kickoff_utc if sort_by == "kickoff_utc" else Match.match_number
    query = query.order_by(sort_col.asc() if sort_order == "asc" else sort_col.desc())

    total_items = query.count()
    

    


    total_pages = max(1, math.ceil(total_items / page_size))
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    result = MatchListResponse(
        data=[MatchSchema.model_validate(m) for m in items],
        page=page, page_size=page_size,
        total_items=total_items, total_pages=total_pages,
    )
    ttl = settings.LIVE_CACHE_TTL_SECONDS if status == "live" else settings.CACHE_TTL_SECONDS
    cache_set(cache_key, result.model_dump(), ttl=ttl)
    return result


def _match_detail_from_db(db, match_id):
    return (db.query(Match).options(*_load_opts(), joinedload(Match.events))
            .filter(Match.id == match_id).first())
