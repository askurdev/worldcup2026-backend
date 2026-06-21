import math
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.db.cache import cache_get, cache_set
from app.models import Team, Group
from app.schemas.schemas import TeamListResponse, Team as TeamSchema


def get_teams(
    db: Session,
    page: int = 1,
    page_size: int = settings.DEFAULT_PAGE_SIZE,
    group: Optional[str] = None,
    confederation: Optional[str] = None,
) -> TeamListResponse:
    cache_key = f"teams:{page}:{page_size}:{group}:{confederation}"
    cached = cache_get(cache_key)
    if cached:
        return TeamListResponse(**cached)

    query = db.query(Team).options(joinedload(Team.coach))

    if group:
        query = query.join(Group, Team.group_id == Group.id).filter(Group.name == group.upper())
    if confederation:
        query = query.filter(Team.confederation == confederation)

    query = query.order_by(Team.fifa_ranking)

    total_items = query.count()
    total_pages = max(1, math.ceil(total_items / page_size))
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    result = TeamListResponse(
        data=[TeamSchema.model_validate(t) for t in items],
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
    )
    cache_set(cache_key, result.model_dump())
    return result


def get_team_by_slug(db: Session, slug: str) -> Optional[Team]:
    cache_key = f"team:{slug}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    team = (
        db.query(Team)
        .options(joinedload(Team.coach), joinedload(Team.players))
        .filter(Team.slug == slug)
        .first()
    )
    if team:
        schema = TeamSchema.model_validate(team)
        cache_set(cache_key, schema.model_dump())
    return team
