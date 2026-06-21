from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.schemas import GroupWithStandings
from app.services import standings_service

router = APIRouter(prefix="/standings", tags=["standings"])


@router.get("", response_model=list[GroupWithStandings], summary="All groups with standings")
def get_all_standings(db: Session = Depends(get_db)):
    return standings_service.get_all_groups(db)


@router.get("/{group}", response_model=GroupWithStandings, summary="Standings for a single group")
def get_group_standings(group: str, db: Session = Depends(get_db)):
    result = standings_service.get_group_by_name(db, group)
    if not result:
        raise HTTPException(status_code=404, detail=f"Group '{group}' not found")
    return result
