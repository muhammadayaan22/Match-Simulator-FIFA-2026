"""
FIFA 2026 AI ORACLE — Team Dataset Generator
Generates a realistic, internally-consistent dataset for the 48 nations
qualified for the FIFA World Cup 2026, including FIFA ranking, Elo rating,
attack/midfield/defense sub-scores, recent form, and historical World Cup
performance. Numbers are hand-tuned to track real-world football intuition
(e.g. Argentina/France/Brazil near the top) but are NOT live API data.
"""

import json
import random
import os

random.seed(42)

# 48 teams qualified for FIFA World Cup 2026 (host nations + qualifiers,
# confederations approximate real qualification slots).
TEAMS_RAW = [
    # (name, confederation, base_fifa_rank, base_elo, attack, midfield, defense, world_cups_won)
    ("Argentina", "CONMEBOL", 1, 2106, 90, 88, 87, 3),
    ("France", "UEFA", 2, 2008, 91, 86, 84, 2),
    ("Spain", "UEFA", 3, 1996, 89, 90, 85, 1),
    ("England", "UEFA", 4, 1968, 87, 85, 83, 1),
    ("Brazil", "CONMEBOL", 5, 1984, 92, 84, 80, 5),
    ("Portugal", "UEFA", 6, 1960, 86, 85, 82, 0),
    ("Netherlands", "UEFA", 7, 1944, 85, 86, 83, 0),
    ("Belgium", "UEFA", 8, 1900, 83, 84, 80, 0),
    ("Germany", "UEFA", 9, 1916, 84, 85, 81, 4),
    ("Italy", "UEFA", 10, 1888, 82, 83, 84, 4),
    ("Croatia", "UEFA", 11, 1872, 80, 86, 81, 0),
    ("Morocco", "CAF", 12, 1860, 81, 82, 83, 0),
    ("Colombia", "CONMEBOL", 13, 1844, 82, 81, 78, 0),
    ("Uruguay", "CONMEBOL", 14, 1836, 80, 79, 81, 2),
    ("USA", "CONCACAF", 15, 1804, 78, 78, 77, 0),
    ("Mexico", "CONCACAF", 16, 1788, 77, 80, 75, 0),
    ("Switzerland", "UEFA", 17, 1780, 76, 79, 80, 0),
    ("Japan", "AFC", 18, 1772, 78, 81, 76, 0),
    ("Senegal", "CAF", 19, 1764, 80, 76, 78, 0),
    ("Denmark", "UEFA", 20, 1756, 77, 78, 78, 0),
    ("Ecuador", "CONMEBOL", 21, 1740, 75, 74, 79, 0),
    ("Iran", "AFC", 22, 1724, 74, 75, 77, 0),
    ("South Korea", "AFC", 23, 1716, 76, 77, 73, 0),
    ("Austria", "UEFA", 24, 1708, 75, 78, 75, 0),
    ("Australia", "AFC", 25, 1692, 72, 73, 76, 0),
    ("Canada", "CONCACAF", 26, 1684, 74, 73, 74, 0),
    ("Tunisia", "CAF", 27, 1668, 71, 74, 76, 0),
    ("Algeria", "CAF", 28, 1660, 73, 72, 73, 0),
    ("Egypt", "CAF", 29, 1652, 75, 71, 72, 0),
    ("Nigeria", "CAF", 30, 1644, 77, 72, 70, 0),
    ("Ghana", "CAF", 31, 1628, 74, 71, 70, 0),
    ("Saudi Arabia", "AFC", 32, 1612, 70, 70, 72, 0),
    ("Qatar", "AFC", 33, 1580, 68, 70, 70, 0),
    ("Panama", "CONCACAF", 34, 1564, 67, 68, 71, 0),
    ("Costa Rica", "CONCACAF", 35, 1556, 66, 69, 72, 0),
    ("Jamaica", "CONCACAF", 36, 1540, 68, 65, 67, 0),
    ("Paraguay", "CONMEBOL", 37, 1532, 67, 68, 70, 0),
    ("Bolivia", "CONMEBOL", 38, 1480, 64, 63, 62, 0),
    ("Venezuela", "CONMEBOL", 39, 1516, 68, 67, 65, 0),
    ("Ivory Coast", "CAF", 40, 1620, 76, 70, 68, 0),
    ("South Africa", "CAF", 41, 1500, 65, 66, 67, 0),
    ("Cape Verde", "CAF", 42, 1488, 63, 64, 66, 0),
    ("Jordan", "AFC", 43, 1472, 62, 65, 65, 0),
    ("Uzbekistan", "AFC", 44, 1464, 61, 64, 64, 0),
    ("New Zealand", "OFC", 45, 1420, 58, 60, 63, 0),
    ("Haiti", "CONCACAF", 46, 1408, 60, 58, 58, 0),
    ("Curacao", "CONCACAF", 47, 1392, 57, 59, 60, 0),
    ("Suriname", "CONCACAF", 48, 1380, 56, 57, 59, 0),
]

NICKNAMES = {
    "Argentina": "La Albiceleste", "France": "Les Bleus", "Spain": "La Roja",
    "England": "The Three Lions", "Brazil": "Selecao", "Portugal": "A Selecao das Quinas",
    "Netherlands": "Oranje", "Belgium": "Red Devils", "Germany": "Die Mannschaft",
    "Italy": "Gli Azzurri", "Croatia": "Vatreni", "Morocco": "Atlas Lions",
    "Colombia": "Los Cafeteros", "Uruguay": "La Celeste", "USA": "The Stars and Stripes",
    "Mexico": "El Tri", "Switzerland": "Nati", "Japan": "Samurai Blue",
    "Senegal": "Lions of Teranga", "Denmark": "Danish Dynamite", "Ecuador": "La Tri",
    "Iran": "Team Melli", "South Korea": "Taegeuk Warriors", "Austria": "Das Team",
    "Australia": "Socceroos", "Canada": "Les Rouges", "Tunisia": "Eagles of Carthage",
    "Algeria": "Desert Foxes", "Egypt": "The Pharaohs", "Nigeria": "Super Eagles",
    "Ghana": "Black Stars", "Saudi Arabia": "The Green Falcons", "Qatar": "The Maroon",
    "Panama": "Los Canaleros", "Costa Rica": "Los Ticos", "Jamaica": "Reggae Boyz",
    "Paraguay": "La Albirroja", "Bolivia": "La Verde", "Venezuela": "La Vinotinto",
    "Ivory Coast": "Les Elephants", "South Africa": "Bafana Bafana", "Cape Verde": "Blue Sharks",
    "Jordan": "The Chivalrous", "Uzbekistan": "The White Wolves", "New Zealand": "All Whites",
    "Haiti": "Les Grenadiers", "Curacao": "Blue Wave", "Suriname": "Natio",
}

FLAGS = {
    "Argentina": "🇦🇷", "France": "🇫🇷", "Spain": "🇪🇸", "England": "🏴",
    "Brazil": "🇧🇷", "Portugal": "🇵🇹", "Netherlands": "🇳🇱", "Belgium": "🇧🇪",
    "Germany": "🇩🇪", "Italy": "🇮🇹", "Croatia": "🇭🇷", "Morocco": "🇲🇦",
    "Colombia": "🇨🇴", "Uruguay": "🇺🇾", "USA": "🇺🇸", "Mexico": "🇲🇽",
    "Switzerland": "🇨🇭", "Japan": "🇯🇵", "Senegal": "🇸🇳", "Denmark": "🇩🇰",
    "Ecuador": "🇪🇨", "Iran": "🇮🇷", "South Korea": "🇰🇷", "Austria": "🇦🇹",
    "Australia": "🇦🇺", "Canada": "🇨🇦", "Tunisia": "🇹🇳", "Algeria": "🇩🇿",
    "Egypt": "🇪🇬", "Nigeria": "🇳🇬", "Ghana": "🇬🇭", "Saudi Arabia": "🇸🇦",
    "Qatar": "🇶🇦", "Panama": "🇵🇦", "Costa Rica": "🇨🇷", "Jamaica": "🇯🇲",
    "Paraguay": "🇵🇾", "Bolivia": "🇧🇴", "Venezuela": "🇻🇪", "Ivory Coast": "🇨🇮",
    "South Africa": "🇿🇦", "Cape Verde": "🇨🇻", "Jordan": "🇯🇴", "Uzbekistan": "🇺🇿",
    "New Zealand": "🇳🇿", "Haiti": "🇭🇹", "Curacao": "🇨🇼", "Suriname": "🇸🇷",
}


def jitter(value, spread=3):
    return max(1, min(99, value + random.randint(-spread, spread)))


def build_teams():
    teams = []
    for idx, (name, conf, rank, elo, atk, mid, dfn, wc_won) in enumerate(TEAMS_RAW, start=1):
        recent_form = "".join(random.choices(
            ["W", "D", "L"],
            weights=[0.55 if rank <= 15 else 0.4 if rank <= 30 else 0.3,
                     0.25,
                     0.20 if rank <= 15 else 0.35 if rank <= 30 else 0.45],
            k=5
        ))
        form_points = recent_form.count("W") * 3 + recent_form.count("D")
        player_quality_index = round((atk * 0.4 + mid * 0.35 + dfn * 0.25), 1)

        teams.append({
            "id": idx,
            "team_name": name,
            "confederation": conf,
            "nickname": NICKNAMES.get(name, name),
            "flag": FLAGS.get(name, "🏳️"),
            "fifa_rank": rank,
            "elo_rating": elo,
            "attack_score": atk,
            "midfield_score": mid,
            "defense_score": dfn,
            "recent_form": recent_form,
            "form_points": form_points,
            "world_cups_won": wc_won,
            "player_quality_index": player_quality_index,
            "goal_difference_last10": random.randint(-8, 18) if rank <= 20 else random.randint(-12, 8),
        })
    return teams


def build_players(teams):
    """Generate a representative squad sample (5 key players per team) for the Players table."""
    positions = ["GK", "DF", "MF", "FW"]
    first_names = ["Carlos", "Luca", "Kwame", "Hiro", "Mateo", "Liam", "Youssef", "Erik",
                   "Diego", "Noah", "Bilal", "Theo", "Andres", "Felix", "Omar", "Lucas"]
    last_names = ["Silva", "Rossi", "Mensah", "Tanaka", "Garcia", "Smith", "Haddad", "Larsen",
                  "Fernandez", "Müller", "Khan", "Dubois", "Lopez", "Schmidt", "Nasser", "Costa"]

    players = []
    pid = 1
    for team in teams:
        quality = team["player_quality_index"]
        for slot in range(5):
            pos = positions[slot % 4] if slot < 4 else "FW"
            base_skill = quality + random.randint(-6, 6)
            goals = max(0, int((base_skill - 60) * random.uniform(0.15, 0.45))) if pos in ("FW", "MF") else random.randint(0, 3)
            assists = max(0, int((base_skill - 60) * random.uniform(0.1, 0.3)))
            appearances = random.randint(25, 95)
            players.append({
                "id": pid,
                "name": f"{random.choice(first_names)} {random.choice(last_names)}",
                "team": team["team_name"],
                "position": pos,
                "goals": goals,
                "assists": assists,
                "appearances": appearances,
                "rating": round(min(9.4, max(6.0, base_skill / 11.5)), 1),
            })
            pid += 1
    return players


if __name__ == "__main__":
    teams = build_teams()
    players = build_players(teams)

    out_dir = os.path.dirname(__file__)
    with open(os.path.join(out_dir, "teams.json"), "w") as f:
        json.dump(teams, f, indent=2)
    with open(os.path.join(out_dir, "players.json"), "w") as f:
        json.dump(players, f, indent=2)

    print(f"Generated {len(teams)} teams and {len(players)} players.")
