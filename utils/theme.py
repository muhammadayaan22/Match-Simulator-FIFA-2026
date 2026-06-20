"""
FIFA 2026 AI ORACLE — Shared Theme
Injects the dark, glassmorphism, neon-blue broadcast aesthetic used across
every page. Import and call `inject_theme()` once at the top of each page.
"""

import streamlit as st

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap');

:root {
    --pitch-black: #0a0e14;
    --panel-dark: #11161f;
    --neon-blue: #00d4ff;
    --neon-blue-dim: #0a8cb3;
    --gold: #ffd166;
    --win-green: #2ee6a6;
    --loss-red: #ff5d6c;
    --text-primary: #eef3fa;
    --text-muted: #8a96a8;
}

.stApp {
    background: radial-gradient(circle at 20% 0%, #0d1521 0%, var(--pitch-black) 55%);
    color: var(--text-primary);
}

h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-family: 'Rajdhani', sans-serif;
    letter-spacing: 0.02em;
    color: var(--text-primary);
}

p, span, div, label {
    font-family: 'Inter', sans-serif;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d131d 0%, #090d14 100%);
    border-right: 1px solid rgba(0, 212, 255, 0.12);
}

.oracle-hero {
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.10) 0%, rgba(10, 14, 20, 0.4) 60%);
    border: 1px solid rgba(0, 212, 255, 0.25);
    border-radius: 18px;
    padding: 2.2rem 2.4rem;
    backdrop-filter: blur(12px);
    margin-bottom: 1.5rem;
}

.glass-card {
    background: rgba(17, 22, 31, 0.65);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    backdrop-filter: blur(10px);
    transition: border-color 0.25s ease, transform 0.25s ease;
}

.glass-card:hover {
    border-color: rgba(0, 212, 255, 0.4);
    transform: translateY(-2px);
}

.stat-eyebrow {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.72rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--neon-blue);
    font-weight: 600;
}

.big-number {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.6rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.1;
}

.team-flag-large {
    font-size: 3.4rem;
    line-height: 1;
}

.nickname-tag {
    color: var(--text-muted);
    font-size: 0.85rem;
    font-style: italic;
}

.rank-badge {
    display: inline-block;
    background: rgba(0, 212, 255, 0.12);
    border: 1px solid rgba(0, 212, 255, 0.35);
    color: var(--neon-blue);
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    font-size: 0.8rem;
    padding: 0.15rem 0.6rem;
    border-radius: 100px;
}

.divider-glow {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.5), transparent);
    margin: 1.4rem 0;
    border: none;
}

.event-row {
    display: flex;
    gap: 0.9rem;
    padding: 0.55rem 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    align-items: flex-start;
}

.event-minute {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    color: var(--neon-blue);
    min-width: 2.6rem;
    font-size: 0.95rem;
}

.event-goal {
    color: var(--win-green);
    font-weight: 600;
}

.vs-pill {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    color: var(--gold);
    font-size: 1.1rem;
    text-align: center;
}

[data-testid="stMetricValue"] {
    font-family: 'Rajdhani', sans-serif;
    color: var(--neon-blue);
}

.stButton button {
    background: linear-gradient(135deg, var(--neon-blue-dim), var(--neon-blue));
    color: #051018;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    letter-spacing: 0.03em;
    border: none;
    border-radius: 10px;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.stButton button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(0, 212, 255, 0.35);
}

[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, var(--neon-blue-dim), var(--neon-blue));
}
</style>
"""


def inject_theme():
    st.markdown(THEME_CSS, unsafe_allow_html=True)


def glass_card_open():
    return '<div class="glass-card">'


def glass_card_close():
    return '</div>'
