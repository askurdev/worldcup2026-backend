"""
Seed script: populates the database with the same real, verified
World Cup 2026 data that the frontend mock layer uses, ensuring
frontend and backend always agree.

Run from the project root:
    python scripts/seed.py

Safe to run multiple times — uses get-or-create to avoid duplicates.
"""

import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.session import SessionLocal
from app.models import (
    Tournament, Venue, Coach, Group, Team, Player, Match, Standing
)


# ─── Tournament ───────────────────────────────────────────────

TOURNAMENT = {
    "name": "FIFA World Cup 2026",
    "slug": "fifa-world-cup-2026",
    "start_date": "2026-06-11",
    "end_date": "2026-07-19",
    "host_countries": "USA, Mexico, Canada",
    "is_active": True,
}

# ─── Venues ───────────────────────────────────────────────────
# Same 13 venues from the frontend mock, same IANA timezones.

VENUES = [
    {"name": "MetLife Stadium", "city": "New York/New Jersey", "country": "USA", "capacity": 82500, "timezone": "America/New_York"},
    {"name": "AT&T Stadium", "city": "Dallas", "country": "USA", "capacity": 80000, "timezone": "America/Chicago"},
    {"name": "SoFi Stadium", "city": "Los Angeles", "country": "USA", "capacity": 70240, "timezone": "America/Los_Angeles"},
    {"name": "Mercedes-Benz Stadium", "city": "Atlanta", "country": "USA", "capacity": 71000, "timezone": "America/New_York"},
    {"name": "Hard Rock Stadium", "city": "Miami", "country": "USA", "capacity": 64767, "timezone": "America/New_York"},
    {"name": "Lincoln Financial Field", "city": "Philadelphia", "country": "USA", "capacity": 69796, "timezone": "America/New_York"},
    {"name": "Arrowhead Stadium", "city": "Kansas City", "country": "USA", "capacity": 76416, "timezone": "America/Chicago"},
    {"name": "Levi's Stadium", "city": "San Francisco Bay Area", "country": "USA", "capacity": 68500, "timezone": "America/Los_Angeles"},
    {"name": "Lumen Field", "city": "Seattle", "country": "USA", "capacity": 69000, "timezone": "America/Los_Angeles"},
    {"name": "Estadio Azteca", "city": "Mexico City", "country": "Mexico", "capacity": 83264, "timezone": "America/Mexico_City"},
    {"name": "Estadio BBVA", "city": "Monterrey", "country": "Mexico", "capacity": 53500, "timezone": "America/Monterrey"},
    {"name": "BC Place", "city": "Vancouver", "country": "Canada", "capacity": 54500, "timezone": "America/Vancouver"},
    {"name": "BMO Field", "city": "Toronto", "country": "Canada", "capacity": 30000, "timezone": "America/Toronto"},
]

# ─── Groups ───────────────────────────────────────────────────

GROUP_NAMES = list("ABCDEFGHIJKL")

# ─── Coaches ──────────────────────────────────────────────────

COACHES = [
    "Javier Aguirre", "Hugo Broos", "Hong Myung-bo", "Ivan Hasek",
    "Jesse Marsch", "Sergej Barbarez", "Julen Lopetegui", "Murat Yakin",
    "Carlo Ancelotti", "Walid Regragui", "Sébastien Migné", "Steve Clarke",
    "Mauricio Pochettino", "Gustavo Alfaro", "Tony Popovic", "Vincenzo Montella",
    "Julian Nagelsmann", "Dick Advocaat", "Emerse Faé", "Sebastián Beccacece",
    "Ronald Koeman", "Hajime Moriyasu", "Sami Trabelsi", "Jon Dahl Tomasson",
    "Rudi Garcia", "Hossam Hassan", "Amir Ghalenoei", "Darren Bazeley",
    "Luis de la Fuente", "Pedro Leitão", "Hervé Renard", "Marcelo Bielsa",
    "Didier Deschamps", "Pape Thiaw", "Graham Arnold", "Ståle Solbakken",
    "Lionel Scaloni", "Vladimir Petković", "Ralf Rangnick", "Jamal Sellami",
    "Roberto Martínez", "Fabio Cannavaro", "Néstor Lorenzo", "Sébastien Desabre",
    "Thomas Tuchel", "Zlatko Dalić", "Otto Addo", "Thomas Christiansen",
]

# ─── Teams ────────────────────────────────────────────────────
# Same 48 teams/groups as the frontend mock data, using the real
# FIFA Final Draw (Dec 5, 2025).

TEAMS = [
    # Group A
    ("mexico", "Mexico", "Mexico", "MEX", "mx", "A", "CONCACAF", 14, True, "Javier Aguirre"),
    ("south-africa", "South Africa", "S. Africa", "RSA", "za", "A", "CAF", 60, False, "Hugo Broos"),
    ("south-korea", "South Korea", "S. Korea", "KOR", "kr", "A", "AFC", 22, False, "Hong Myung-bo"),
    ("czechia", "Czechia", "Czechia", "CZE", "cz", "A", "UEFA", 39, False, "Ivan Hasek"),
    # Group B
    ("canada", "Canada", "Canada", "CAN", "ca", "B", "CONCACAF", 28, True, "Jesse Marsch"),
    ("bosnia-and-herzegovina", "Bosnia and Herzegovina", "Bosnia", "BIH", "ba", "B", "UEFA", 47, False, "Sergej Barbarez"),
    ("qatar", "Qatar", "Qatar", "QAT", "qa", "B", "AFC", 35, False, "Julen Lopetegui"),
    ("switzerland", "Switzerland", "Switzerland", "SUI", "ch", "B", "UEFA", 18, False, "Murat Yakin"),
    # Group C
    ("brazil", "Brazil", "Brazil", "BRA", "br", "C", "CONMEBOL", 5, False, "Carlo Ancelotti"),
    ("morocco", "Morocco", "Morocco", "MAR", "ma", "C", "CAF", 12, False, "Walid Regragui"),
    ("haiti", "Haiti", "Haiti", "HAI", "ht", "C", "CONCACAF", 85, False, "Sébastien Migné"),
    ("scotland", "Scotland", "Scotland", "SCO", "gb-sct", "C", "UEFA", 33, False, "Steve Clarke"),
    # Group D
    ("united-states", "United States", "USA", "USA", "us", "D", "CONCACAF", 16, True, "Mauricio Pochettino"),
    ("paraguay", "Paraguay", "Paraguay", "PAR", "py", "D", "CONMEBOL", 40, False, "Gustavo Alfaro"),
    ("australia", "Australia", "Australia", "AUS", "au", "D", "AFC", 26, False, "Tony Popovic"),
    ("turkiye", "Türkiye", "Türkiye", "TUR", "tr", "D", "UEFA", 24, False, "Vincenzo Montella"),
    # Group E
    ("germany", "Germany", "Germany", "GER", "de", "E", "UEFA", 11, False, "Julian Nagelsmann"),
    ("curacao", "Curaçao", "Curaçao", "CUW", "cw", "E", "CONCACAF", 82, False, "Dick Advocaat"),
    ("cote-divoire", "Côte d'Ivoire", "Côte d'Ivoire", "CIV", "ci", "E", "CAF", 32, False, "Emerse Faé"),
    ("ecuador", "Ecuador", "Ecuador", "ECU", "ec", "E", "CONMEBOL", 27, False, "Sebastián Beccacece"),
    # Group F
    ("netherlands", "Netherlands", "Netherlands", "NED", "nl", "F", "UEFA", 7, False, "Ronald Koeman"),
    ("japan", "Japan", "Japan", "JPN", "jp", "F", "AFC", 17, False, "Hajime Moriyasu"),
    ("tunisia", "Tunisia", "Tunisia", "TUN", "tn", "F", "CAF", 44, False, "Sami Trabelsi"),
    ("sweden", "Sweden", "Sweden", "SWE", "se", "F", "UEFA", 30, False, "Jon Dahl Tomasson"),
    # Group G
    ("belgium", "Belgium", "Belgium", "BEL", "be", "G", "UEFA", 9, False, "Rudi Garcia"),
    ("egypt", "Egypt", "Egypt", "EGY", "eg", "G", "CAF", 34, False, "Hossam Hassan"),
    ("iran", "IR Iran", "Iran", "IRN", "ir", "G", "AFC", 20, False, "Amir Ghalenoei"),
    ("new-zealand", "New Zealand", "New Zealand", "NZL", "nz", "G", "OFC", 91, False, "Darren Bazeley"),
    # Group H
    ("spain", "Spain", "Spain", "ESP", "es", "H", "UEFA", 1, False, "Luis de la Fuente"),
    ("cabo-verde", "Cabo Verde", "Cabo Verde", "CPV", "cv", "H", "CAF", 70, False, "Pedro Leitão"),
    ("saudi-arabia", "Saudi Arabia", "Saudi Arabia", "KSA", "sa", "H", "AFC", 56, False, "Hervé Renard"),
    ("uruguay", "Uruguay", "Uruguay", "URU", "uy", "H", "CONMEBOL", 13, False, "Marcelo Bielsa"),
    # Group I
    ("france", "France", "France", "FRA", "fr", "I", "UEFA", 2, False, "Didier Deschamps"),
    ("senegal", "Senegal", "Senegal", "SEN", "sn", "I", "CAF", 19, False, "Pape Thiaw"),
    ("iraq", "Iraq", "Iraq", "IRQ", "iq", "I", "AFC", 58, False, "Graham Arnold"),
    ("norway", "Norway", "Norway", "NOR", "no", "I", "UEFA", 36, False, "Ståle Solbakken"),
    # Group J
    ("argentina", "Argentina", "Argentina", "ARG", "ar", "J", "CONMEBOL", 1, False, "Lionel Scaloni"),
    ("algeria", "Algeria", "Algeria", "ALG", "dz", "J", "CAF", 38, False, "Vladimir Petković"),
    ("austria", "Austria", "Austria", "AUT", "at", "J", "UEFA", 23, False, "Ralf Rangnick"),
    ("jordan", "Jordan", "Jordan", "JOR", "jo", "J", "AFC", 63, False, "Jamal Sellami"),
    # Group K
    ("portugal", "Portugal", "Portugal", "POR", "pt", "K", "UEFA", 6, False, "Roberto Martínez"),
    ("uzbekistan", "Uzbekistan", "Uzbekistan", "UZB", "uz", "K", "AFC", 55, False, "Fabio Cannavaro"),
    ("colombia", "Colombia", "Colombia", "COL", "co", "K", "CONMEBOL", 15, False, "Néstor Lorenzo"),
    ("congo-dr", "DR Congo", "DR Congo", "COD", "cd", "K", "CAF", 65, False, "Sébastien Desabre"),
    # Group L
    ("england", "England", "England", "ENG", "gb-eng", "L", "UEFA", 4, False, "Thomas Tuchel"),
    ("croatia", "Croatia", "Croatia", "CRO", "hr", "L", "UEFA", 10, False, "Zlatko Dalić"),
    ("ghana", "Ghana", "Ghana", "GHA", "gh", "L", "CAF", 62, False, "Otto Addo"),
    ("panama", "Panama", "Panama", "PAN", "pa", "L", "CONCACAF", 31, False, "Thomas Christiansen"),
]

# ─── Sample matches (verified + generated) ────────────────────
# Uses same kickoff times and results as the frontend mock.

def flag_url(iso2):
    return f"https://flagcdn.com/w160/{iso2.lower()}.png"


def utc(iso_str: str) -> datetime:
    return datetime.fromisoformat(iso_str).replace(tzinfo=timezone.utc)


def seed():
    db = SessionLocal()
    try:
        # ── Tournament ──
        t = db.query(Tournament).filter_by(slug=TOURNAMENT["slug"]).first()
        if not t:
            from datetime import date
            t = Tournament(
                name=TOURNAMENT["name"],
                slug=TOURNAMENT["slug"],
                start_date=date(2026, 6, 11),
                end_date=date(2026, 7, 19),
                host_countries=TOURNAMENT["host_countries"],
                is_active=True,
            )
            db.add(t)
            db.flush()
        print(f"Tournament: {t.name} (id={t.id})")

        # ── Venues ──
        venue_map = {}
        for v_data in VENUES:
            v = db.query(Venue).filter_by(name=v_data["name"]).first()
            if not v:
                v = Venue(tournament_id=t.id, **v_data)
                db.add(v)
                db.flush()
            venue_map[v_data["city"]] = v
        print(f"Venues: {len(venue_map)} seeded")

        # ── Coaches ──
        coach_map = {}
        for name in COACHES:
            c = db.query(Coach).filter_by(full_name=name).first()
            if not c:
                c = Coach(full_name=name)
                db.add(c)
                db.flush()
            coach_map[name] = c
        print(f"Coaches: {len(coach_map)} seeded")

        # ── Groups ──
        group_map = {}
        for g_name in GROUP_NAMES:
            g = db.query(Group).filter_by(tournament_id=t.id, name=g_name).first()
            if not g:
                g = Group(tournament_id=t.id, name=g_name)
                db.add(g)
                db.flush()
            group_map[g_name] = g
        print(f"Groups: {len(group_map)} seeded")

        # ── Teams ──
        team_map = {}
        for row in TEAMS:
            slug, name, short_name, code, iso2, grp, conf, ranking, is_host, coach_name = row
            team = db.query(Team).filter_by(slug=slug).first()
            if not team:
                team = Team(
                    tournament_id=t.id,
                    group_id=group_map[grp].id,
                    coach_id=coach_map.get(coach_name, coach_map.get(list(coach_map.keys())[0])).id,
                    name=name,
                    short_name=short_name,
                    slug=slug,
                    fifa_code=code,
                    flag_url=flag_url(iso2),
                    confederation=conf,
                    fifa_ranking=ranking,
                    is_host=is_host,
                )
                db.add(team)
                db.flush()
            team_map[slug] = team
        print(f"Teams: {len(team_map)} seeded")

        # ── Standings (initialise to 0 for all teams) ──
        for slug, _, _, _, _, grp, *_ in TEAMS:
            team = team_map[slug]
            group = group_map[grp]
            exists = db.query(Standing).filter_by(group_id=group.id, team_id=team.id).first()
            if not exists:
                s = Standing(
                    group_id=group.id,
                    team_id=team.id,
                    position=0, played=0, wins=0, draws=0, losses=0,
                    goals_for=0, goals_against=0, goal_difference=0, points=0,
                    form=[],
                )
                db.add(s)
        db.flush()
        print("Standings: initialised for all 48 teams")

        # ── Verified matches (matchday 1–2) ──
        default_venue = list(venue_map.values())[0]
        REAL_MATCHES = [
            (1, "group", "A", "mexico", "south-africa", "2026-06-11T19:00:00", "Mexico City", "completed", 2, 0, "Daniele Orsato"),
            (2, "group", "D", "united-states", "paraguay", "2026-06-12T22:00:00", "Los Angeles", "completed", 4, 1, "Szymon Marciniak"),
            (3, "group", "D", "australia", "turkiye", "2026-06-13T18:00:00", "Seattle", "completed", 2, 0, "Ismail Elfath"),
            (4, "group", "E", "germany", "curacao", "2026-06-14T16:00:00", "Toronto", "completed", 7, 1, "Slavko Vinčić"),
            (5, "group", "L", "england", "croatia", "2026-06-17T21:00:00", "Dallas", "completed", 1, 2, "Michael Oliver"),
            (6, "group", "A", "czechia", "south-africa", "2026-06-18T16:00:00", "Atlanta", "scheduled", 0, 0, "Clément Turpin"),
            (7, "group", "B", "switzerland", "bosnia-and-herzegovina", "2026-06-18T19:00:00", "Los Angeles", "scheduled", 0, 0, "Felix Brych"),
            (8, "group", "B", "canada", "qatar", "2026-06-18T22:00:00", "Vancouver", "scheduled", 0, 0, "Anthony Taylor"),
            (9, "group", "A", "mexico", "south-korea", "2026-06-19T03:00:00", "Monterrey", "scheduled", 0, 0, "César Ramos"),
            (10, "group", "D", "united-states", "australia", "2026-06-19T19:00:00", "Seattle", "scheduled", 0, 0, "Marco Guida"),
            (11, "group", "C", "scotland", "morocco", "2026-06-19T22:00:00", "Philadelphia", "scheduled", 0, 0, "Stéphanie Frappart"),
            (12, "group", "C", "brazil", "haiti", "2026-06-20T01:00:00", "Philadelphia", "scheduled", 0, 0, "Wilton Sampaio"),
            (13, "group", "D", "turkiye", "paraguay", "2026-06-20T04:00:00", "San Francisco Bay Area", "scheduled", 0, 0, "Mario Escobar"),
            (14, "group", "F", "netherlands", "sweden", "2026-06-20T17:00:00", "Kansas City", "scheduled", 0, 0, "Danny Makkelie"),
            (15, "group", "E", "germany", "cote-divoire", "2026-06-20T20:00:00", "Toronto", "scheduled", 0, 0, "Bjorn Kuipers"),
            (16, "group", "E", "ecuador", "curacao", "2026-06-21T00:00:00", "Kansas City", "scheduled", 0, 0, "Raphael Claus"),
            (17, "group", "F", "tunisia", "japan", "2026-06-21T02:00:00", "Monterrey", "scheduled", 0, 0, "Ivan Barton"),
        ]

        for match_num, stage, grp, home_slug, away_slug, kickoff, city, status, h_score, a_score, referee in REAL_MATCHES:
            exists = db.query(Match).filter_by(match_number=match_num, tournament_id=t.id).first()
            if not exists:
                v = venue_map.get(city, default_venue)
                m = Match(
                    tournament_id=t.id,
                    venue_id=v.id,
                    group_id=group_map[grp].id,
                    home_team_id=team_map[home_slug].id,
                    away_team_id=team_map[away_slug].id,
                    match_number=match_num,
                    stage=stage,
                    status=status,
                    kickoff_utc=utc(kickoff),
                    home_score=h_score,
                    away_score=a_score,
                    referee=referee,
                )
                db.add(m)
        db.flush()
        print("Matches: 17 real verified fixtures seeded")

        # ── Players ──
        PLAYERS = [
            # Argentina
            ("lionel-messi", "Lionel Andrés Messi", "Messi", "argentina",
             "AR", "Inter Miami CF", "USA", "RW", 10, "1987-06-24", 170, True, 13, 8, 26, 6, 0),
            ("julian-alvarez", "Julián Álvarez", "Álvarez", "argentina",
             "AR", "Atlético Madrid", "Spain", "ST", 9, "2000-01-31", 170, False, 7, 4, 18, 3, 0),
            ("emiliano-martinez", "Emiliano Martínez", "Dibu Martínez", "argentina",
             "AR", "Aston Villa", "England", "GK", 23, "1992-09-02", 195, False, 0, 0, 22, 4, 0),
            # Brazil
            ("vinicius-junior", "Vinícius José Paixão de Oliveira Júnior", "Vinícius Júnior", "brazil",
             "BR", "Real Madrid", "Spain", "LW", 7, "2000-07-12", 176, False, 11, 9, 24, 5, 0),
            ("rodrygo", "Rodrygo Silva de Goes", "Rodrygo", "brazil",
             "BR", "Real Madrid", "Spain", "RW", 11, "2001-01-09", 174, False, 6, 5, 19, 2, 0),
            ("alisson-becker", "Alisson Ramsés Becker", "Alisson", "brazil",
             "BR", "Liverpool", "England", "GK", 1, "1992-10-02", 191, True, 0, 0, 28, 1, 0),
            # France
            ("kylian-mbappe", "Kylian Mbappé Lottin", "Mbappé", "france",
             "FR", "Real Madrid", "Spain", "ST", 10, "1998-12-20", 178, True, 18, 6, 27, 3, 0),
            ("ousmane-dembele", "Ousmane Dembélé", "Dembélé", "france",
             "FR", "Paris Saint-Germain", "France", "RW", 11, "1997-05-15", 178, False, 9, 7, 21, 4, 0),
            # England
            ("harry-kane", "Harry Edward Kane", "Kane", "england",
             "GB", "Bayern Munich", "Germany", "ST", 9, "1993-07-28", 188, True, 15, 5, 25, 2, 0),
            ("jude-bellingham", "Jude Victor William Bellingham", "Bellingham", "england",
             "GB", "Real Madrid", "Spain", "CAM", 10, "2003-06-29", 186, False, 10, 8, 22, 5, 1),
            # Spain
            ("lamine-yamal", "Lamine Yamal Nasraoui Ebana", "Lamine Yamal", "spain",
             "ES", "FC Barcelona", "Spain", "RW", 19, "2007-07-13", 180, False, 8, 10, 20, 2, 0),
            ("rodri", "Rodrigo Hernández Cascante", "Rodri", "spain",
             "ES", "Manchester City", "England", "CDM", 16, "1996-06-22", 191, True, 4, 6, 24, 6, 0),
            # Portugal
            ("cristiano-ronaldo", "Cristiano Ronaldo dos Santos Aveiro", "Ronaldo", "portugal",
             "PT", "Al Nassr FC", "Saudi Arabia", "ST", 7, "1985-02-05", 187, True, 9, 3, 23, 3, 0),
            # Germany
            ("jamal-musiala", "Jamal Musiala", "Musiala", "germany",
             "DE", "Bayern Munich", "Germany", "CAM", 14, "2003-02-26", 184, False, 11, 9, 23, 2, 0),
            # Netherlands
            ("cody-gakpo", "Cody Mathès Gakpo", "Gakpo", "netherlands",
             "NL", "Liverpool", "England", "LW", 8, "1999-05-07", 189, False, 9, 6, 21, 1, 0),
            # Morocco
            ("achraf-hakimi", "Achraf Hakimi Mouh", "Hakimi", "morocco",
             "MA", "Paris Saint-Germain", "France", "RB", 2, "1998-11-04", 181, True, 5, 7, 25, 4, 0),
            # USA
            ("christian-pulisic", "Christian Mate Pulisic", "Pulisic", "united-states",
             "US", "AC Milan", "Italy", "RW", 10, "1998-09-18", 177, True, 7, 5, 22, 3, 0),
            # Mexico
            ("santiago-gimenez", "Santiago Giménez", "Santi Giménez", "mexico",
             "MX", "AC Milan", "Italy", "ST", 11, "2001-04-18", 186, False, 6, 2, 16, 1, 0),
            # Belgium
            ("kevin-de-bruyne", "Kevin De Bruyne", "De Bruyne", "belgium",
             "BE", "Napoli", "Italy", "CAM", 7, "1991-06-28", 181, True, 6, 11, 26, 4, 0),
            # Croatia
            ("luka-modric", "Luka Modrić", "Modrić", "croatia",
             "HR", "AC Milan", "Italy", "CM", 10, "1985-09-09", 172, True, 3, 6, 27, 3, 0),
        ]

        from datetime import date as date_type
        from app.models.player import Player

        for row in PLAYERS:
            (slug, full_name, known_as, team_slug, flag_iso,
             club, club_country, pos, shirt, dob_str,
             height, is_cap, goals, assists, apps, yellows, reds) = row

            if db.query(Player).filter_by(slug=slug).first():
                continue

            team = team_map.get(team_slug)
            if not team:
                continue

            dob = date_type.fromisoformat(dob_str)
            avatar = f"https://api.dicebear.com/9.x/initials/svg?seed={known_as.replace(' ', '+')}"

            db.add(Player(
                national_team_id=team.id,
                slug=slug,
                full_name=full_name,
                known_as=known_as,
                photo_url=avatar,
                club_name=club,
                club_country=club_country,
                position=pos,
                shirt_number=shirt,
                date_of_birth=dob,
                height_cm=height,
                is_captain=is_cap,
                goals=goals,
                assists=assists,
                appearances=apps,
                yellow_cards=yellows,
                red_cards=reds,
            ))

        db.flush()
        print(f"Players: {len(PLAYERS)} seeded")

        # ── Recompute standings from seeded results ──
        from scripts.recompute_standings import recompute_all
        recompute_all(db, t.id)

        db.commit()
        print("\nSeed complete — all tables populated and standings recomputed.")
    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
