from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import PaginationParams
from app.db.session import get_db
from app.schemas.schemas import Player, PlayerListResponse
from app.services import player_service

router = APIRouter(prefix="/players", tags=["players"])


@router.get("", response_model=PlayerListResponse, summary="List players")
def list_players(
    pagination: PaginationParams = Depends(),
    team_id: Optional[int] = Query(None, alias="teamId"),
    position: Optional[str] = Query(None, description="Position code e.g. GK, ST, CM"),
    db: Session = Depends(get_db),
):
    return player_service.get_players(
        db=db,
        page=pagination.page,
        page_size=pagination.page_size,
        team_id=team_id,
        position=position,
    )


@router.get("/{slug}", response_model=Player, summary="Get player by slug")
def get_player(slug: str, db: Session = Depends(get_db)):
    player = player_service.get_player_by_slug(db, slug)
    if not player:
        raise HTTPException(status_code=404, detail=f"Player '{slug}' not found")
    return player
