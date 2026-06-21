import math
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.db.cache import cache_get, cache_set
from app.models import Player, Team
from app.schemas.schemas import PlayerListResponse, Player as PlayerSchema


def get_players(
    db: Session,
    page: int = 1,
    page_size: int = settings.DEFAULT_PAGE_SIZE,
    team_id: Optional[int] = None,
    position: Optional[str] = None,
) -> PlayerListResponse:
    cache_key = f"players:{page}:{page_size}:{team_id}:{position}"
    cached = cache_get(cache_key)
    if cached:
        return PlayerListResponse(**cached)

    query = db.query(Player).options(joinedload(Player.national_team))

    if team_id:
        query = query.filter(Player.national_team_id == team_id)
    if position:
        query = query.filter(Player.position == position.upper())

    query = query.order_by(Player.goals.desc(), Player.known_as)

    total_items = query.count()
    total_pages = max(1, math.ceil(total_items / page_size))
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    result = PlayerListResponse(
        data=[PlayerSchema.model_validate(p) for p in items],
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
    )
    cache_set(cache_key, result.model_dump())
    return result


def get_player_by_slug(db: Session, slug: str) -> Optional[Player]:
    cache_key = f"player:{slug}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    player = (
        db.query(Player)
        .options(joinedload(Player.national_team))
        .filter(Player.slug == slug)
        .first()
    )
    if player:
        schema = PlayerSchema.model_validate(player)
        cache_set(cache_key, schema.model_dump())
    return player
