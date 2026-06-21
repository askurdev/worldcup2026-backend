from typing import Optional

from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class MatchEvent(Base):
    """
    A single event within a match: goal, yellow card, red card,
    substitution. Kept in one table with an event_type discriminator
    rather than separate tables per event type — simpler queries for
    the timeline view, and events are rarely queried independently of
    their match anyway.
    """

    __tablename__ = "match_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), nullable=False, index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    player_id: Mapped[Optional[int]] = mapped_column(ForeignKey("players.id"), nullable=True)

    # "goal" | "own_goal" | "penalty" | "yellow_card" | "red_card" | "second_yellow" | "substitution"
    event_type: Mapped[str] = mapped_column(String(20), nullable=False)

    minute: Mapped[int] = mapped_column(Integer, nullable=False)
    extra_time_minute: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Goal-specific
    is_penalty: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_own_goal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    assist_player_id: Mapped[Optional[int]] = mapped_column(ForeignKey("players.id"), nullable=True)

    # Substitution-specific
    player_out_id: Mapped[Optional[int]] = mapped_column(ForeignKey("players.id"), nullable=True)

    # Card-specific
    card_reason: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    match: Mapped["Match"] = relationship(back_populates="events")
    player: Mapped[Optional["Player"]] = relationship(
        back_populates="match_events", foreign_keys=[player_id]
    )
    team: Mapped["Team"] = relationship(foreign_keys=[team_id])
