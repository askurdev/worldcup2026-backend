from typing import List, Optional

from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournaments.id"), nullable=False)
    group_id: Mapped[Optional[int]] = mapped_column(ForeignKey("groups.id"), nullable=True)
    coach_id: Mapped[Optional[int]] = mapped_column(ForeignKey("coaches.id"), nullable=True)

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    short_name: Mapped[str] = mapped_column(String(60), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    fifa_code: Mapped[str] = mapped_column(String(3), nullable=False)  # e.g. "ARG"
    flag_url: Mapped[str] = mapped_column(String(255), nullable=False)
    confederation: Mapped[str] = mapped_column(String(60), nullable=False)
    fifa_ranking: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_host: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    tournament: Mapped["Tournament"] = relationship(back_populates="teams")
    group: Mapped[Optional["Group"]] = relationship(back_populates="teams")
    coach: Mapped[Optional["Coach"]] = relationship(back_populates="teams")
    players: Mapped[List["Player"]] = relationship(back_populates="national_team")
    home_matches: Mapped[List["Match"]] = relationship(
        back_populates="home_team", foreign_keys="Match.home_team_id"
    )
    away_matches: Mapped[List["Match"]] = relationship(
        back_populates="away_team", foreign_keys="Match.away_team_id"
    )
    standings: Mapped[List["Standing"]] = relationship(back_populates="team")
    favorited_by: Mapped[List["UserFavorite"]] = relationship(
        back_populates="team",
        primaryjoin="and_(UserFavorite.entity_type == 'team', foreign(UserFavorite.entity_id) == Team.id)",
    )
