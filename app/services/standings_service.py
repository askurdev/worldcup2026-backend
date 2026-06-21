from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.db.cache import cache_get, cache_set
from app.models import Group, Standing, Match, Team
from app.schemas.schemas import GroupWithStandings, Standing as StandingSchema, Bracket, BracketSlot


def get_all_groups(db: Session) -> list[GroupWithStandings]:
    cache_key = "standings:all"
    cached = cache_get(cache_key)
    if cached:
        return [GroupWithStandings(**g) for g in cached]

    groups = (
        db.query(Group)
        .options(
            joinedload(Group.standings).joinedload(Standing.team)
        )
        .order_by(Group.name)
        .all()
    )

    result = []
    for g in groups:
        sorted_standings = sorted(g.standings, key=lambda s: s.position)
        result.append(GroupWithStandings(
            id=g.id,
            name=g.name,
            standings=[StandingSchema.model_validate(s) for s in sorted_standings],
        ))

    cache_set("standings:all", [r.model_dump() for r in result])
    return result


def get_group_by_name(db: Session, name: str) -> Optional[GroupWithStandings]:
    cache_key = f"standings:group:{name}"
    cached = cache_get(cache_key)
    if cached:
        return GroupWithStandings(**cached)

    group = (
        db.query(Group)
        .options(joinedload(Group.standings).joinedload(Standing.team))
        .filter(Group.name == name.upper())
        .first()
    )
    if not group:
        return None

    sorted_standings = sorted(group.standings, key=lambda s: s.position)
    result = GroupWithStandings(
        id=group.id,
        name=group.name,
        standings=[StandingSchema.model_validate(s) for s in sorted_standings],
    )
    cache_set(cache_key, result.model_dump())
    return result


def get_bracket(db: Session) -> Bracket:
    """
    Builds the knockout bracket from matches with stage != 'group'.
    When teams are not yet determined, slots show the label text
    (e.g. 'Winner Group A vs Runner-up Group B').
    """
    cache_key = "bracket:current"
    cached = cache_get(cache_key)
    if cached:
        return Bracket(**cached)

    def make_slot(match: Match) -> BracketSlot:
        home_team = None
        away_team = None
        if match.home_team:
            from app.schemas.schemas import TeamBase
            home_team = TeamBase.model_validate(match.home_team)
        if match.away_team:
            from app.schemas.schemas import TeamBase
            away_team = TeamBase.model_validate(match.away_team)

        label = ""
        if match.home_slot_label and match.away_slot_label:
            label = f"{match.home_slot_label} vs {match.away_slot_label}"
        elif match.home_slot_label:
            label = match.home_slot_label
        elif home_team and away_team:
            label = f"{home_team.short_name} vs {away_team.short_name}"

        return BracketSlot(
            match_id=match.id,
            round=match.stage,
            slot_label=label,
            home_team=home_team,
            away_team=away_team,
            home_score=match.home_score if match.status != "scheduled" else None,
            away_score=match.away_score if match.status != "scheduled" else None,
        )

    knockout_matches = (
        db.query(Match)
        .options(joinedload(Match.home_team), joinedload(Match.away_team))
        .filter(Match.stage != "group")
        .order_by(Match.match_number)
        .all()
    )

    by_stage: dict[str, list[Match]] = {}
    for m in knockout_matches:
        by_stage.setdefault(m.stage, []).append(m)

    bracket = Bracket(
        round_of_32=[make_slot(m) for m in by_stage.get("round_of_32", [])],
        round_of_16=[make_slot(m) for m in by_stage.get("round_of_16", [])],
        quarter_finals=[make_slot(m) for m in by_stage.get("quarter_final", [])],
        semi_finals=[make_slot(m) for m in by_stage.get("semi_final", [])],
        third_place=make_slot(by_stage["third_place"][0]) if by_stage.get("third_place") else None,
        final=make_slot(by_stage["final"][0]) if by_stage.get("final") else None,
    )

    cache_set(cache_key, bracket.model_dump())
    return bracket
