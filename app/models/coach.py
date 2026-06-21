from typing import List, Optional

from sqlalchemy import String, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Coach(Base):
    """
    Modeled as its own table (per the brief's schema) rather than a
    plain string column on Team, so a coach's history/metadata can
    grow independently — e.g. nationality, past tenures — without
    reshaping the Team table later.
    """

    __tablename__ = "coaches"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    nationality: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    date_of_birth: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)

    teams: Mapped[List["Team"]] = relationship(back_populates="coach")
