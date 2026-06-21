"""
Recomputes group standings from actual match results.

Called by the seed script and by the match-result update endpoint
so standings and results always stay in sync. Same logic as the
frontend's computeGroupStandings(), expressed in Python.

Usage from within the app:
    from scripts.recompute_standings import recompute_all, recompute_group
    recompute_all(db, tournament_id)

Standalone:
    python scripts/recompute_standings.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models import Group, Match, Standing, Team, Tournament


def recompute_group(db: Session, group: Group) -> None:
    """Recompute standings for a single group."""
    completed = (
        db.query(Match)
        .filter(
            Match.group_id == group.id,
            Match.status == "completed",
        )
        .order_by(Match.kickoff_utc)
        .all()
    )

    # Initialise accumulators for each team in this group
    teams = {t.id: t for t in db.query(Team).filter(Team.group_id == group.id).all()}
    stats: dict[int, dict] = {
        tid: {"played": 0, "wins": 0, "draws": 0, "losses": 0,
              "goals_for": 0, "goals_against": 0, "form": []}
        for tid in teams
    }

    for match in completed:
        h, a = match.home_team_id, match.away_team_id
        if h not in stats or a not in stats:
            continue

        hs, as_ = match.home_score, match.away_score

        stats[h]["played"] += 1
        stats[a]["played"] += 1
        stats[h]["goals_for"] += hs
        stats[h]["goals_against"] += as_
        stats[a]["goals_for"] += as_
        stats[a]["goals_against"] += hs

        if hs > as_:
            stats[h]["wins"] += 1; stats[h]["form"].append("W")
            stats[a]["losses"] += 1; stats[a]["form"].append("L")
        elif hs < as_:
            stats[a]["wins"] += 1; stats[a]["form"].append("W")
            stats[h]["losses"] += 1; stats[h]["form"].append("L")
        else:
            stats[h]["draws"] += 1; stats[h]["form"].append("D")
            stats[a]["draws"] += 1; stats[a]["form"].append("D")

    # Sort by points, goal difference, goals scored (FIFA tiebreak order)
    def sort_key(tid):
        s = stats[tid]
        pts = s["wins"] * 3 + s["draws"]
        gd = s["goals_for"] - s["goals_against"]
        return (-pts, -gd, -s["goals_for"])

    ranked = sorted(teams.keys(), key=sort_key)

    for position, tid in enumerate(ranked, start=1):
        s = stats[tid]
        gd = s["goals_for"] - s["goals_against"]
        pts = s["wins"] * 3 + s["draws"]

        standing = (
            db.query(Standing)
            .filter(Standing.group_id == group.id, Standing.team_id == tid)
            .first()
        )
        if not standing:
            standing = Standing(group_id=group.id, team_id=tid)
            db.add(standing)

        standing.position = position
        standing.played = s["played"]
        standing.wins = s["wins"]
        standing.draws = s["draws"]
        standing.losses = s["losses"]
        standing.goals_for = s["goals_for"]
        standing.goals_against = s["goals_against"]
        standing.goal_difference = gd
        standing.points = pts
        standing.form = s["form"][-5:]  # last 5 results


def recompute_all(db: Session, tournament_id: int) -> None:
    """Recompute standings for every group in the tournament."""
    groups = db.query(Group).filter(Group.tournament_id == tournament_id).all()
    for group in groups:
        recompute_group(db, group)
    db.flush()
    print(f"Standings recomputed for {len(groups)} groups")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        t = db.query(Tournament).filter_by(slug="fifa-world-cup-2026").first()
        if not t:
            print("Tournament not found — run seed.py first")
            sys.exit(1)
        recompute_all(db, t.id)
        db.commit()
        print("Done")
    finally:
        db.close()
