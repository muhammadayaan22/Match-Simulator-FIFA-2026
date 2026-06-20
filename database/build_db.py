"""
FIFA 2026 AI ORACLE — Database Builder
Creates the SQLite database with Teams, Players, and Matches tables and
seeds it from the generated JSON datasets.
"""

import sqlite3
import json
import os

HERE = os.path.dirname(__file__)
ROOT = os.path.dirname(HERE)
DB_PATH = os.path.join(HERE, "fifa_oracle.db")
DATA_DIR = os.path.join(ROOT, "data")


SCHEMA = """
DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS matches;

CREATE TABLE teams (
    id INTEGER PRIMARY KEY,
    team_name TEXT UNIQUE NOT NULL,
    confederation TEXT,
    nickname TEXT,
    flag TEXT,
    fifa_rank INTEGER,
    elo_rating INTEGER,
    attack_score INTEGER,
    midfield_score INTEGER,
    defense_score INTEGER,
    recent_form TEXT,
    form_points INTEGER,
    world_cups_won INTEGER,
    player_quality_index REAL,
    goal_difference_last10 INTEGER
);

CREATE TABLE players (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    team TEXT NOT NULL,
    position TEXT,
    goals INTEGER,
    assists INTEGER,
    appearances INTEGER,
    rating REAL,
    FOREIGN KEY (team) REFERENCES teams(team_name)
);

CREATE TABLE matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team1 TEXT NOT NULL,
    team2 TEXT NOT NULL,
    predicted_score TEXT,
    win_prob_team1 REAL,
    draw_prob REAL,
    win_prob_team2 REAL,
    xg_team1 REAL,
    xg_team2 REAL,
    possession_team1 REAL,
    man_of_the_match TEXT,
    date TEXT DEFAULT (datetime('now'))
);
"""


def build_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript(SCHEMA)

    with open(os.path.join(DATA_DIR, "teams.json")) as f:
        teams = json.load(f)
    with open(os.path.join(DATA_DIR, "players.json")) as f:
        players = json.load(f)

    cur.executemany("""
        INSERT INTO teams (id, team_name, confederation, nickname, flag, fifa_rank,
            elo_rating, attack_score, midfield_score, defense_score, recent_form,
            form_points, world_cups_won, player_quality_index, goal_difference_last10)
        VALUES (:id, :team_name, :confederation, :nickname, :flag, :fifa_rank,
            :elo_rating, :attack_score, :midfield_score, :defense_score, :recent_form,
            :form_points, :world_cups_won, :player_quality_index, :goal_difference_last10)
    """, teams)

    cur.executemany("""
        INSERT INTO players (id, name, team, position, goals, assists, appearances, rating)
        VALUES (:id, :name, :team, :position, :goals, :assists, :appearances, :rating)
    """, players)

    conn.commit()

    cur.execute("SELECT COUNT(*) FROM teams")
    n_teams = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM players")
    n_players = cur.fetchone()[0]

    conn.close()
    print(f"Database built at {DB_PATH}")
    print(f"  Teams: {n_teams}")
    print(f"  Players: {n_players}")
    print(f"  Matches table: ready (populated as simulations are run)")


if __name__ == "__main__":
    build_database()
