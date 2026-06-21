from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.schemas import Bracket, Match, SearchResult
from app.services import standings_service, match_service, search_service

# ── Bracket ──────────────────────────────────────────────────
brackets_router = APIRouter(prefix="/brackets", tags=["bracket"])


@brackets_router.get("", response_model=Bracket, summary="Full knockout bracket")
def get_bracket(db: Session = Depends(get_db)):
    return standings_service.get_bracket(db)


# ── Live ─────────────────────────────────────────────────────
live_router = APIRouter(prefix="/live", tags=["live"])


@live_router.get("", response_model=list[Match], summary="Currently live matches")
def get_live(db: Session = Depends(get_db)):
    return match_service.get_live_matches(db)


@live_router.get("/today", response_model=list[Match], summary="Today's matches (UTC date)")
def get_today(db: Session = Depends(get_db)):
    return match_service.get_today_matches(db)


# ── Search ───────────────────────────────────────────────────
search_router = APIRouter(prefix="/search", tags=["search"])


@search_router.get("", response_model=SearchResult, summary="Search teams, players, and matches")
def search(
    q: str = Query(..., min_length=2, description="Search query (min 2 chars)"),
    db: Session = Depends(get_db),
):
    return search_service.search(db, q)
