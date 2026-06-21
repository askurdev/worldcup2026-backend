"""
Pydantic v2 schemas for the World Cup 2026 API.

Naming convention:
  <Model>Base      — shared fields used in both create and read
  <Model>Create    — request body for POST (subset of fields, no id/timestamps)
  <Model>          — full response schema (includes id, computed fields)
  <Model>WithX     — extended schema that includes a nested relationship

All response schemas inherit from model_config = ConfigDict(from_attributes=True)
so they can be constructed from SQLAlchemy ORM instances directly.
"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator


# ─────────────────────────────────────────────
# Shared config
# ─────────────────────────────────────────────

class ORMBase(BaseModel):
    """Base for all response schemas — enables ORM-mode."""
    model_config = ConfigDict(from_attributes=True)


# ─────────────────────────────────────────────
# Pagination envelope
# ─────────────────────────────────────────────

class PaginatedResponse(BaseModel):
    """Generic pagination wrapper. FastAPI can't easily make this
    generic over T in a way that shows cleanly in OpenAPI, so each
    endpoint defines its own typed version."""
    page: int
    page_size: int
    total_items: int
    total_pages: int


# ─────────────────────────────────────────────
# Tournament
# ─────────────────────────────────────────────

class TournamentBase(ORMBase):
    name: str
    slug: str
    start_date: date
    end_date: date
    host_countries: str
    is_active: bool = True


class TournamentCreate(BaseModel):
    name: str
    slug: str
    start_date: date
    end_date: date
    host_countries: str


class Tournament(TournamentBase):
    id: int


# ─────────────────────────────────────────────
# Venue
# ─────────────────────────────────────────────

class VenueBase(ORMBase):
    name: str
    city: str
    country: str
    capacity: int
    timezone: str


class VenueCreate(BaseModel):
    tournament_id: int
    name: str
    city: str
    country: str
    capacity: int
    timezone: str


class Venue(VenueBase):
    id: int
    tournament_id: int


# ─────────────────────────────────────────────
# Coach
# ─────────────────────────────────────────────

class CoachBase(ORMBase):
    full_name: str
    nationality: Optional[str] = None


class Coach(CoachBase):
    id: int


# ─────────────────────────────────────────────
# Team
# ─────────────────────────────────────────────

class TeamBase(ORMBase):
    name: str
    short_name: str
    slug: str
    fifa_code: str
    flag_url: str
    confederation: str
    fifa_ranking: int
    is_host: bool


class TeamCreate(BaseModel):
    tournament_id: int
    group_id: Optional[int] = None
    coach_id: Optional[int] = None
    name: str
    short_name: str
    slug: str
    fifa_code: str
    flag_url: str
    confederation: str
    fifa_ranking: int = 0
    is_host: bool = False


class Team(TeamBase):
    id: int
    tournament_id: int
    group_id: Optional[int] = None
    coach_id: Optional[int] = None
    coach: Optional[Coach] = None


class TeamWithGroup(Team):
    group_name: Optional[str] = None


# ─────────────────────────────────────────────
# Player
# ─────────────────────────────────────────────

class PlayerBase(ORMBase):
    slug: str
    full_name: str
    known_as: str
    photo_url: str
    club_name: str
    club_country: str
    position: str
    shirt_number: int
    date_of_birth: Optional[date] = None
    height_cm: Optional[int] = None
    is_captain: bool = False
    goals: int = 0
    assists: int = 0
    appearances: int = 0
    yellow_cards: int = 0
    red_cards: int = 0


class PlayerCreate(BaseModel):
    national_team_id: int
    slug: str
    full_name: str
    known_as: str
    photo_url: str
    club_name: str
    club_country: str
    position: str
    shirt_number: int
    date_of_birth: Optional[date] = None
    height_cm: Optional[int] = None
    is_captain: bool = False
    goals: int = 0
    assists: int = 0
    appearances: int = 0
    yellow_cards: int = 0
    red_cards: int = 0


class Player(PlayerBase):
    id: int
    national_team_id: int
    national_team: Optional[TeamBase] = None


# ─────────────────────────────────────────────
# Match
# ─────────────────────────────────────────────

class MatchBase(ORMBase):
    match_number: int
    stage: str
    status: str
    kickoff_utc: datetime
    minute: Optional[int] = None
    home_score: int = 0
    away_score: int = 0
    home_penalties: Optional[int] = None
    away_penalties: Optional[int] = None
    referee: Optional[str] = None
    home_slot_label: Optional[str] = None
    away_slot_label: Optional[str] = None


class MatchCreate(BaseModel):
    tournament_id: int
    venue_id: Optional[int] = None
    group_id: Optional[int] = None
    home_team_id: Optional[int] = None
    away_team_id: Optional[int] = None
    match_number: int
    stage: str = "group"
    status: str = "scheduled"
    kickoff_utc: datetime
    referee: Optional[str] = None
    home_slot_label: Optional[str] = None
    away_slot_label: Optional[str] = None


class MatchUpdate(BaseModel):
    status: Optional[str] = None
    minute: Optional[int] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    home_penalties: Optional[int] = None
    away_penalties: Optional[int] = None


class Match(MatchBase):
    id: int
    tournament_id: int
    venue_id: Optional[int] = None
    group_id: Optional[int] = None
    home_team_id: Optional[int] = None
    away_team_id: Optional[int] = None
    venue: Optional[Venue] = None
    home_team: Optional[TeamBase] = None
    away_team: Optional[TeamBase] = None


# ─────────────────────────────────────────────
# MatchEvent
# ─────────────────────────────────────────────

class MatchEventCreate(BaseModel):
    match_id: int
    team_id: int
    player_id: Optional[int] = None
    event_type: str
    minute: int
    extra_time_minute: Optional[int] = None
    is_penalty: bool = False
    is_own_goal: bool = False
    assist_player_id: Optional[int] = None
    player_out_id: Optional[int] = None
    card_reason: Optional[str] = None


class MatchEvent(ORMBase):
    id: int
    match_id: int
    team_id: int
    player_id: Optional[int] = None
    event_type: str
    minute: int
    extra_time_minute: Optional[int] = None
    is_penalty: bool
    is_own_goal: bool
    assist_player_id: Optional[int] = None
    player_out_id: Optional[int] = None
    card_reason: Optional[str] = None


# ─────────────────────────────────────────────
# Standing
# ─────────────────────────────────────────────

class Standing(ORMBase):
    id: int
    group_id: int
    team_id: int
    position: int
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int
    form: List[str]
    team: Optional[TeamBase] = None


class GroupWithStandings(ORMBase):
    id: int
    name: str
    standings: List[Standing] = []


# ─────────────────────────────────────────────
# Bracket slot (computed, not a DB table)
# ─────────────────────────────────────────────

class BracketSlot(BaseModel):
    match_id: Optional[int] = None
    round: str
    slot_label: str
    home_team: Optional[TeamBase] = None
    away_team: Optional[TeamBase] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None


class Bracket(BaseModel):
    round_of_32: List[BracketSlot]
    round_of_16: List[BracketSlot]
    quarter_finals: List[BracketSlot]
    semi_finals: List[BracketSlot]
    third_place: Optional[BracketSlot] = None
    final: Optional[BracketSlot] = None


# ─────────────────────────────────────────────
# Search
# ─────────────────────────────────────────────

class SearchResult(BaseModel):
    teams: List[TeamBase]
    players: List[PlayerBase]
    matches: List[Match]


# ─────────────────────────────────────────────
# Paginated typed responses
# ─────────────────────────────────────────────

class MatchListResponse(PaginatedResponse):
    data: List[Match]


class TeamListResponse(PaginatedResponse):
    data: List[Team]


class PlayerListResponse(PaginatedResponse):
    data: List[Player]
