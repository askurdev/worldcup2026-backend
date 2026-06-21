# World Cup 2026 Dashboard — Backend

FastAPI backend with PostgreSQL, Redis caching, Alembic migrations, and all 7 REST API modules from the brief.

This is **Step 2 of 5** (Backend structure). Data comes from the seed script using the same verified World Cup 2026 data as the frontend mock layer.

## Quick start

```bash
# 1. Start dependencies
docker-compose up -d db redis

# 2. Install Python deps
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 3. Copy and configure env
cp .env.example .env

# 4. Run migrations
alembic upgrade head

# 5. Seed real data
python scripts/seed.py

# 6. Start the API
uvicorn app.main:app --reload --port 8000
```

API docs at `http://localhost:8000/docs` (Swagger UI) or `/redoc`.

## Run everything with Docker

```bash
docker-compose up --build
# Then seed inside the container:
docker-compose exec api python scripts/seed.py
```

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/matches | List matches (filter: status, stage, group, teamId, date) |
| GET | /api/v1/matches/{id} | Match detail with events |
| PATCH | /api/v1/matches/{id} | Update result + auto-recompute standings |
| GET | /api/v1/teams | List teams (filter: group, confederation) |
| GET | /api/v1/teams/{slug} | Team detail with squad |
| GET | /api/v1/players | List players (filter: teamId, position) |
| GET | /api/v1/players/{slug} | Player detail |
| GET | /api/v1/standings | All 12 groups with standings |
| GET | /api/v1/standings/{group} | Single group standings |
| GET | /api/v1/brackets | Full knockout bracket |
| GET | /api/v1/live | Currently live matches |
| GET | /api/v1/live/today | Today's matches (UTC date) |
| GET | /api/v1/search?q= | Search teams, players, matches |

## Architecture notes

**Standings are always derived from match results** — update a match result via `PATCH /api/v1/matches/{id}` with `status: "completed"` and standings recompute automatically. Never update standings directly.

**Redis caching** — all list endpoints cache for 30s (configurable). `/live` caches for 10s. Cache is automatically invalidated when match results change.

**Step 3 — connecting a real provider**: set `FOOTBALL_DATA_PROVIDER=api_football` in `.env` and add your key. A new provider class implementing `FootballDataProvider` (see `app/providers/`) needs to be written and registered in `app/core/config.py`.
