"""
FIFA 2026 AI ORACLE
Home Page / App Entry Point

Run with: streamlit run app.py
"""

import streamlit as st
import sys
import os
from datetime import datetime
import random

sys.path.insert(0, os.path.dirname(__file__))

from utils.theme import inject_theme
from utils.db import get_all_teams

st.set_page_config(
    page_title="FIFA 2026 AI Oracle",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_theme()

# World Cup 2026 kicks off June 11, 2026 (host: USA/Mexico/Canada)
WORLD_CUP_START = datetime(2026, 6, 11)


def render_countdown():
    now = datetime.now()
    delta = WORLD_CUP_START - now
    if delta.days < 0:
        st.markdown(
            '<div class="oracle-hero"><span class="stat-eyebrow">FIFA WORLD CUP 2026</span>'
            '<h2 style="margin:0.3rem 0 0 0;">🏆 The tournament is underway</h2></div>',
            unsafe_allow_html=True,
        )
        return
    days, hours = delta.days, delta.seconds // 3600
    st.markdown(
        f"""
        <div class="oracle-hero">
            <span class="stat-eyebrow">FIFA WORLD CUP 2026 · USA · MEXICO · CANADA</span>
            <h1 style="margin:0.4rem 0 0.2rem 0;">⚽ FIFA 2026 AI ORACLE</h1>
            <p style="color:var(--text-muted); margin-bottom:1.2rem;">
                AI-powered match intelligence, predictive simulation, and tactical analysis for the 48-team World Cup.
            </p>
            <div style="display:flex; gap:2.4rem; align-items:baseline;">
                <div>
                    <div class="big-number">{days}</div>
                    <div class="stat-eyebrow">DAYS</div>
                </div>
                <div>
                    <div class="big-number">{hours}</div>
                    <div class="stat-eyebrow">HOURS</div>
                </div>
                <div style="font-size:2.4rem;">🏆</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_live_rankings(teams_df):
    st.markdown("### 🌍 Live FIFA Rankings — Top 10")
    top10 = teams_df.head(10)
    cols = st.columns(5)
    for i, (_, team) in enumerate(top10.iterrows()):
        with cols[i % 5]:
            st.markdown(
                f"""
                <div class="glass-card" style="text-align:center; margin-bottom:0.8rem;">
                    <span class="rank-badge">#{team['fifa_rank']}</span>
                    <div class="team-flag-large" style="margin-top:0.4rem;">{team['flag']}</div>
                    <div style="font-weight:600; margin-top:0.2rem;">{team['team_name']}</div>
                    <div class="nickname-tag">{team['nickname']}</div>
                    <div style="margin-top:0.5rem; color:var(--neon-blue); font-family:'Rajdhani',sans-serif; font-weight:700;">
                        Elo {team['elo_rating']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_featured_matches(teams_df):
    st.markdown("### 🔥 Featured Matchups")
    top_teams = teams_df.head(12)
    random.seed(datetime.now().day)
    sample = top_teams.sample(n=6, random_state=datetime.now().day).reset_index(drop=True)

    cols = st.columns(3)
    for i in range(0, len(sample) - 1, 2):
        team_a = sample.iloc[i]
        team_b = sample.iloc[i + 1]
        with cols[(i // 2) % 3]:
            st.markdown(
                f"""
                <div class="glass-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div style="text-align:center; flex:1;">
                            <div style="font-size:2rem;">{team_a['flag']}</div>
                            <div style="font-weight:600; font-size:0.9rem;">{team_a['team_name']}</div>
                            <span class="rank-badge">#{team_a['fifa_rank']}</span>
                        </div>
                        <div class="vs-pill">VS</div>
                        <div style="text-align:center; flex:1;">
                            <div style="font-size:2rem;">{team_b['flag']}</div>
                            <div style="font-weight:600; font-size:0.9rem;">{team_b['team_name']}</div>
                            <span class="rank-badge">#{team_b['fifa_rank']}</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def main():
    render_countdown()

    teams_df = get_all_teams()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Qualified Teams", "48")
    with col2:
        st.metric("Host Nations", "3", help="USA, Mexico, Canada")
    with col3:
        st.metric("Highest Elo", f"{teams_df['elo_rating'].max()}", help=teams_df.loc[teams_df['elo_rating'].idxmax(), 'team_name'])
    with col4:
        st.metric("Past Champions in Field", f"{(teams_df['world_cups_won'] > 0).sum()}")

    st.markdown('<hr class="divider-glow">', unsafe_allow_html=True)
    render_live_rankings(teams_df)
    st.markdown('<hr class="divider-glow">', unsafe_allow_html=True)
    render_featured_matches(teams_df)

    st.markdown('<hr class="divider-glow">', unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align:center; color:var(--text-muted); font-size:0.85rem;">'
        'Use the sidebar to open the Match Simulator, AI Commentary, AI Analyst, or Historical Insights.'
        '</p>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
