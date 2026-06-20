"""
FIFA 2026 AI ORACLE — Database Access Layer
Thin helper functions for reading Teams/Players and writing simulated
Matches into the SQLite database.
"""

import os
import sqlite3
import pandas as pd

HERE = os.path.dirname(__file__)
ROOT = os.path.dirname(HERE)
DB_PATH = os.path.join(ROOT, "database", "fifa_oracle.db")


def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def get_all_teams() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM teams ORDER BY fifa_rank ASC", conn)
    conn.close()
    return df


def get_team(team_name: str) -> dict:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM teams WHERE team_name = ?", (team_name,))
    row = cur.fetchone()
    cols = [c[0] for c in cur.description]
    conn.close()
    if row is None:
        return None
    return dict(zip(cols, row))


def get_players_by_team(team_name: str) -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM players WHERE team = ? ORDER BY rating DESC", conn, params=(team_name,))
    conn.close()
    return df


def get_team_names() -> list:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT team_name FROM teams ORDER BY team_name ASC")
    names = [r[0] for r in cur.fetchall()]
    conn.close()
    return names


def save_match_prediction(team1, team2, predicted_score, win_prob1, draw_prob, win_prob2,
                            xg1, xg2, possession1, man_of_the_match=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO matches (team1, team2, predicted_score, win_prob_team1, draw_prob,
            win_prob_team2, xg_team1, xg_team2, possession_team1, man_of_the_match)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (team1, team2, predicted_score, win_prob1, draw_prob, win_prob2, xg1, xg2,
          possession1, man_of_the_match))
    conn.commit()
    conn.close()


def get_recent_matches(limit=10) -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM matches ORDER BY id DESC LIMIT ?", conn, params=(limit,)
    )
    conn.close()
    return df
