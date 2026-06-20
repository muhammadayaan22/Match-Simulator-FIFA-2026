"""
FIFA 2026 AI ORACLE — AI Match Commentary Page
Generates a minute-by-minute commentary timeline, tactical summary, and
crowd reaction for the most recently simulated match (or a freshly chosen one).
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.theme import inject_theme
from utils.db import get_team, get_team_names
from utils.predictor import predict_match
from utils.ai_commentary import generate_match_commentary

st.set_page_config(page_title="AI Commentary — FIFA 2026 AI Oracle", page_icon="🎙️", layout="wide")
inject_theme()

st.markdown(
    '<div class="oracle-hero"><span class="stat-eyebrow">AI MATCH COMMENTARY</span>'
    '<h1 style="margin:0.3rem 0;">🎙️ Live AI Commentary Feed</h1>'
    '<p style="color:var(--text-muted);">Broadcast-style minute-by-minute commentary, generated and grounded in the match prediction.</p></div>',
    unsafe_allow_html=True,
)

team_names = get_team_names()

if "last_teams" in st.session_state:
    default_a, default_b = st.session_state["last_teams"]
else:
    default_a, default_b = "Brazil", "Germany"

col1, col_vs, col2 = st.columns([5, 1, 5])
with col1:
    team_a_name = st.selectbox("Team 1", team_names, index=team_names.index(default_a) if default_a in team_names else 0)
with col_vs:
    st.markdown('<div style="text-align:center; padding-top:1.8rem;" class="vs-pill">VS</div>', unsafe_allow_html=True)
with col2:
    team_b_name = st.selectbox("Team 2", team_names, index=team_names.index(default_b) if default_b in team_names else 1)

generate = st.button("🎙️ Generate Commentary", use_container_width=True, type="primary")

if team_a_name == team_b_name:
    st.warning("Pick two different teams.")
elif generate or "commentary_data" in st.session_state:
    if generate or st.session_state.get("commentary_teams") != (team_a_name, team_b_name):
        team_a = get_team(team_a_name)
        team_b = get_team(team_b_name)
        prediction = predict_match(team_a, team_b)
        with st.spinner("AI commentator is calling the match..."):
            commentary = generate_match_commentary(prediction, team_a, team_b)
        st.session_state["commentary_data"] = commentary
        st.session_state["commentary_teams"] = (team_a_name, team_b_name)
        st.session_state["commentary_prediction"] = prediction
        st.session_state["commentary_team_a"] = team_a
        st.session_state["commentary_team_b"] = team_b

    commentary = st.session_state["commentary_data"]
    prediction = st.session_state["commentary_prediction"]
    team_a = st.session_state["commentary_team_a"]
    team_b = st.session_state["commentary_team_b"]

    st.markdown('<hr class="divider-glow">', unsafe_allow_html=True)

    header_col1, header_col2, header_col3 = st.columns([2, 1, 2])
    with header_col1:
        st.markdown(f"<h3 style='text-align:center;'>{team_a['flag']} {team_a['team_name']}</h3>", unsafe_allow_html=True)
    with header_col2:
        st.markdown(
            f"<div style='text-align:center;' class='big-number'>{prediction['predicted_goals_a']}-{prediction['predicted_goals_b']}</div>",
            unsafe_allow_html=True,
        )
    with header_col3:
        st.markdown(f"<h3 style='text-align:center;'>{team_b['team_name']} {team_b['flag']}</h3>", unsafe_allow_html=True)

    st.markdown('<hr class="divider-glow">', unsafe_allow_html=True)
    st.markdown("### 📋 Match Timeline")

    timeline_html = '<div class="glass-card">'
    for ev in commentary["timeline"]:
        icon = {"goal": "⚽", "kickoff": "🟢", "fulltime": "🏁"}.get(ev.get("type"), "🔹")
        event_class = "event-goal" if ev.get("type") == "goal" else ""
        timeline_html += (
            f'<div class="event-row">'
            f'<div class="event-minute">{ev["minute"]}\'</div>'
            f'<div>{icon} <span class="{event_class}">{ev["event"]}</span></div>'
            f'</div>'
        )
    timeline_html += '</div>'
    st.markdown(timeline_html, unsafe_allow_html=True)

    st.markdown('<hr class="divider-glow">', unsafe_allow_html=True)
    tac_col, crowd_col = st.columns(2)
    with tac_col:
        st.markdown("### 🧠 Tactical Summary")
        st.markdown(f'<div class="glass-card">{commentary["tactical_summary"]}</div>', unsafe_allow_html=True)
    with crowd_col:
        st.markdown("### 📱 Fan Reaction")
        st.markdown(f'<div class="glass-card">{commentary["crowd_reaction"]}</div>', unsafe_allow_html=True)

else:
    st.info("Select two teams and click **Generate Commentary** to call the match.")
