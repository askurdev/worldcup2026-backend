from datetime import date
from typing import List, Optional

from sqlalchemy import String, Date, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Tournament(Base):
    """
    A single tournament edition (e.g. 'FIFA World Cup 2026'). Modeled
    as its own table — rather than hardcoding "2026" everywhere — so
    this schema can hold future tournaments without a redesign.
    """

    __tablename__ = "tournaments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(60), unique=True, nullable=False, index=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    host_countries: Mapped[str] = mapped_column(String(200), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    venues: Mapped[List["Venue"]] = relationship(back_populates="tournament")
    teams: Mapped[List["Team"]] = relationship(back_populates="tournament")
    matches: Mapped[List["Match"]] = relationship(back_populates="tournament")
    groups: Mapped[List["Group"]] = relationship(back_populates="tournament")


class Venue(Base):
    """A host stadium. Timezone is stored as an IANA tz string so
    backend-side time math (and the frontend's dual-clock UI) stays
    correct across DST without hardcoding offsets."""

    __tablename__ = "venues"

    id: Mapped[int] = mapped_column(primary_key=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournaments.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    city: Mapped[str] = mapped_column(String(80), nullable=False)
    country: Mapped[str] = mapped_column(String(60), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    timezone: Mapped[str] = mapped_column(String(60), nullable=False)

    tournament: Mapped["Tournament"] = relationship(back_populates="venues")
    matches: Mapped[List["Match"]] = relationship(back_populates="venue")
