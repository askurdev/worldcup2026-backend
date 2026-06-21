from typing import Optional
from datetime import date

from sqlalchemy import String, Integer, Boolean, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True)
    national_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)

    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    known_as: Mapped[str] = mapped_column(String(80), nullable=False)
    photo_url: Mapped[str] = mapped_column(String(255), nullable=False)
    club_name: Mapped[str] = mapped_column(String(120), nullable=False)
    club_country: Mapped[str] = mapped_column(String(60), nullable=False)
    position: Mapped[str] = mapped_column(String(10), nullable=False)  # GK, CB, ST, etc.
    shirt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    height_cm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_captain: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Tournament stats — updated as results come in
    goals: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    assists: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    appearances: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    yellow_cards: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    red_cards: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    national_team: Mapped["Team"] = relationship(back_populates="players")
    match_events: Mapped[list["MatchEvent"]] = relationship(
        back_populates="player",
        foreign_keys="MatchEvent.player_id",
    )
