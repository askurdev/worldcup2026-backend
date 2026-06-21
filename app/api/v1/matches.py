from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import PaginationParams
from app.db.session import get_db
from app.schemas.schemas import Match, MatchListResponse, MatchUpdate
from app.services import match_service

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("", response_model=MatchListResponse, summary="List matches")
def list_matches(
    pagination: PaginationParams = Depends(),
    status: Optional[str] = Query(None, description="Filter: scheduled|live|halftime|completed"),
    stage: Optional[str] = Query(None, description="Filter: group|round_of_32|round_of_16|..."),
    group: Optional[str] = Query(None, description="Filter by group letter e.g. 'A'"),
    team_id: Optional[int] = Query(None, alias="teamId", description="Filter matches by team ID"),
    date_utc: Optional[str] = Query(None, alias="date", description="Filter by UTC date (YYYY-MM-DD)"),
    sort_by: str = Query("kickoff_utc", alias="sortBy", description="Sort field: kickoff_utc|match_number"),
    sort_order: str = Query("asc", alias="sortOrder", description="asc|desc"),
    db: Session = Depends(get_db),
):
    return match_service.get_matches(
        db=db,
        page=pagination.page,
        page_size=pagination.page_size,
        status=status,
        stage=stage,
        group=group,
        team_id=team_id,
        date_utc=date_utc,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/{match_id}", response_model=Match, summary="Get match by ID")
def get_match(match_id: int, db: Session = Depends(get_db)):
    match = match_service.get_match_by_id(db, match_id)
    if not match:
        raise HTTPException(status_code=404, detail=f"Match {match_id} not found")
    return match


@router.patch("/{match_id}", response_model=Match, summary="Update match result (admin)")
def update_match(match_id: int, body: MatchUpdate, db: Session = Depends(get_db)):
    match = match_service.update_match_result(
        db=db,
        match_id=match_id,
        status=body.status,
        minute=body.minute,
        home_score=body.home_score,
        away_score=body.away_score,
        home_penalties=body.home_penalties,
        away_penalties=body.away_penalties,
    )
    if not match:
        raise HTTPException(status_code=404, detail=f"Match {match_id} not found")
    return match
