from sqlalchemy import Integer, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Standing(Base):
    """
    Computed group-stage standing for one team within one group.
    This is a *cached* denormalization of what could be derived from
    match results alone — kept in the database so the standings
    endpoint stays fast under load without aggregating all match rows
    on every request.

    IMPORTANT: standings must always be recomputed from match results
    via the compute_standings() service whenever a match result is
    updated. Never update standings independently of updating match
    results — the two must always agree.

    Same rule as the frontend: if standings and results can diverge,
    the table is wrong.
    """

    __tablename__ = "standings"
    __table_args__ = (UniqueConstraint("group_id", "team_id", name="uq_standing_group_team"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)

    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    played: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    wins: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    draws: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    losses: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    goals_for: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    goals_against: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    goal_difference: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Last 5 match results stored as a JSON list: ["W","D","L","W","W"]
    # JSON avoids a separate form_results table for a simple ordered list.
    form: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    group: Mapped["Group"] = relationship(back_populates="standings")
    team: Mapped["Team"] = relationship(back_populates="standings")
