from sqlalchemy import or_, func
from sqlalchemy.orm import Session, joinedload

from app.models import Team, Player, Match
from app.schemas.schemas import SearchResult, TeamBase, PlayerBase, Match as MatchSchema


def search(db: Session, query: str) -> SearchResult:
    q = query.strip().lower()
    if not q or len(q) < 2:
        return SearchResult(teams=[], players=[], matches=[])

    teams = (
        db.query(Team)
        .filter(
            or_(
                func.lower(Team.name).contains(q),
                func.lower(Team.short_name).contains(q),
                func.lower(Team.fifa_code).contains(q),
            )
        )
        .limit(10)
        .all()
    )

    players = (
        db.query(Player)
        .options(joinedload(Player.national_team))
        .filter(
            or_(
                func.lower(Player.known_as).contains(q),
                func.lower(Player.full_name).contains(q),
            )
        )
        .limit(10)
        .all()
    )

    matches = (
        db.query(Match)
        .options(
            joinedload(Match.home_team),
            joinedload(Match.away_team),
            joinedload(Match.venue),
        )
        .join(Team, or_(Match.home_team_id == Team.id, Match.away_team_id == Team.id))
        .filter(
            or_(
                func.lower(Team.name).contains(q),
                func.lower(Team.short_name).contains(q),
            )
        )
        .distinct()
        .limit(10)
        .all()
    )

    return SearchResult(
        teams=[TeamBase.model_validate(t) for t in teams],
        players=[PlayerBase.model_validate(p) for p in players],
        matches=[MatchSchema.model_validate(m) for m in matches],
    )
