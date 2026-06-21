from typing import List

from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Group(Base):
    """A single group (e.g. 'A') within one tournament edition.
    Scoped per-tournament (not a bare global 'A'/'B'/...) so multiple
    tournaments can coexist in the same database without collision."""

    __tablename__ = "groups"
    __table_args__ = (UniqueConstraint("tournament_id", "name", name="uq_group_tournament_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournaments.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(1), nullable=False)  # "A" through "L"

    tournament: Mapped["Tournament"] = relationship(back_populates="groups")
    teams: Mapped[List["Team"]] = relationship(back_populates="group")
    standings: Mapped[List["Standing"]] = relationship(back_populates="group")
