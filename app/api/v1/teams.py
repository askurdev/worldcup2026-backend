from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import PaginationParams
from app.db.session import get_db
from app.schemas.schemas import Team, TeamListResponse
from app.services import team_service

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("", response_model=TeamListResponse, summary="List all teams")
def list_teams(
    pagination: PaginationParams = Depends(),
    group: Optional[str] = Query(None, description="Filter by group letter"),
    confederation: Optional[str] = Query(None, description="Filter by confederation"),
    db: Session = Depends(get_db),
):
    return team_service.get_teams(
        db=db,
        page=pagination.page,
        page_size=pagination.page_size,
        group=group,
        confederation=confederation,
    )


@router.get("/{slug}", response_model=Team, summary="Get team by slug")
def get_team(slug: str, db: Session = Depends(get_db)):
    team = team_service.get_team_by_slug(db, slug)
    if not team:
        raise HTTPException(status_code=404, detail=f"Team '{slug}' not found")
    return team
