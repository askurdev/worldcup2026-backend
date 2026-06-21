from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class UserFavorite(Base):
    """
    Tracks a user's favorited teams and players. Currently anonymous
    (identified by a session_id cookie), so the user doesn't need to
    log in to save favorites. If proper user accounts are added later,
    session_id can be replaced with user_id FK without structural change.

    Uses a polymorphic entity_type+entity_id pair ("team"/123,
    "player"/456) rather than separate favorite_teams / favorite_players
    tables — fewer tables, same query efficiency for the typical
    "get all favorites for session X" use case.
    """

    __tablename__ = "user_favorites"
    __table_args__ = (
        UniqueConstraint("session_id", "entity_type", "entity_id", name="uq_favorite_session_entity"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(20), nullable=False)  # "team" | "player"
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

    # Convenience relationship to Team (only valid when entity_type == "team")
    team: Mapped["Team"] = relationship(
        back_populates="favorited_by",
        primaryjoin="and_(UserFavorite.entity_type == 'team', foreign(UserFavorite.entity_id) == Team.id)",
        viewonly=True,
    )
