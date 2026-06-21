from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournaments.id"), nullable=False)
    venue_id: Mapped[Optional[int]] = mapped_column(ForeignKey("venues.id"), nullable=True)
    group_id: Mapped[Optional[int]] = mapped_column(ForeignKey("groups.id"), nullable=True)
    home_team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id"), nullable=True)
    away_team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id"), nullable=True)

    match_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # "group" | "round_of_32" | "round_of_16" | "quarter_final" | "semi_final" | "third_place" | "final"
    stage: Mapped[str] = mapped_column(String(20), nullable=False, default="group")

    # "scheduled" | "live" | "halftime" | "completed" | "postponed" | "cancelled"
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="scheduled")

    kickoff_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    minute: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # set only when live

    home_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    away_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    home_penalties: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    away_penalties: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    referee: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)

    # Knockout bracket — slot labels for before teams are determined
    home_slot_label: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    away_slot_label: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)

    tournament: Mapped["Tournament"] = relationship(back_populates="matches")
    venue: Mapped[Optional["Venue"]] = relationship(back_populates="matches")
    group: Mapped[Optional["Group"]] = relationship()
    home_team: Mapped[Optional["Team"]] = relationship(
        back_populates="home_matches", foreign_keys=[home_team_id]
    )
    away_team: Mapped[Optional["Team"]] = relationship(
        back_populates="away_matches", foreign_keys=[away_team_id]
    )
    events: Mapped[List["MatchEvent"]] = relationship(
        back_populates="match", cascade="all, delete-orphan"
    )
