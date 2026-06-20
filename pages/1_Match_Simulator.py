"""
FIFA 2026 AI ORACLE — Match Simulator Page
Pick two teams, get a full AI/ML-driven match prediction: win probability,
predicted scoreline, xG, possession, shots, and a generated AI match preview.
"""

import streamlit as st
import sys
import os
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.theme import inject_theme
from utils.db import get_team, get_team_names, get_players_by_team, save_match_prediction
from utils.predictor import predict_match
from utils.ai_commentary import generate_match_preview

st.set_page_config(page_title="Match Simulator — FIFA 2026 AI Oracle", page_icon="⚔️", layout="wide")
inject_theme()

st.markdown(
    '<div class="oracle-hero"><span class="stat-eyebrow">MATCH SIMULATOR</span>'
    '<h1 style="margin:0.3rem 0;">⚔️ Predict Any Matchup</h1>'
    '<p style="color:var(--text-muted);">Select two national teams and let the ML prediction engine break down the matchup.</p></div>',
    unsafe_allow_html=True,
)

team_names = get_team_names()

col1, col_vs, col2 = st.columns([5, 1, 5])
with col1:
    team_a_name = st.selectbox("Team 1", team_names, index=team_names.index("Argentina") if "Argentina" in team_names else 0)
with col_vs:
    st.markdown('<div style="text-align:center; padding-top:1.8rem;" class="vs-pill">VS</div>', unsafe_allow_html=True)
with col2:
    default_b = "France" if "France" in team_names else team_names[1]
    team_b_name = st.selectbox("Team 2", team_names, index=team_names.index(default_b))

simulate = st.button("🎮 Simulate Match", use_container_width=True, type="primary")

if team_a_name == team_b_name:
    st.warning("Pick two different teams to simulate a match.")
elif simulate or "last_prediction" in st.session_state:
    if simulate or st.session_state.get("last_teams") != (team_a_name, team_b_name):
        team_a = get_team(team_a_name)
        team_b = get_team(team_b_name)
        prediction = predict_match(team_a, team_b)
        st.session_state["last_prediction"] = prediction
        st.session_state["last_teams"] = (team_a_name, team_b_name)
        st.session_state["team_a_meta"] = team_a
        st.session_state["team_b_meta"] = team_b
        save_match_prediction(
            team_a_name, team_b_name, prediction["predicted_score"],
            prediction["win_prob_a"], prediction["draw_prob"], prediction["win_prob_b"],
            prediction["xg_a"], prediction["xg_b"], prediction["possession_a"],
        )

    prediction = st.session_state["last_prediction"]
    team_a = st.session_state["team_a_meta"]
    team_b = st.session_state["team_b_meta"]

    st.markdown('<hr class="divider-glow">', unsafe_allow_html=True)

    # --- Scoreboard ---
    sb1, sb2, sb3 = st.columns([2, 1, 2])
    with sb1:
        st.markdown(
            f"""<div class="glass-card" style="text-align:center;">
                <div class="team-flag-large">{team_a['flag']}</div>
                <h3 style="margin:0.3rem 0;">{team_a['team_name']}</h3>
                <span class="rank-badge">FIFA #{team_a['fifa_rank']}</span>
                <div class="nickname-tag">{team_a['nickname']}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with sb2:
        st.markdown(
            f"""<div style="text-align:center; padding-top:1.5rem;">
                <div class="big-number" style="font-size:3.2rem;">{prediction['predicted_goals_a']} - {prediction['predicted_goals_b']}</div>
                <div class="stat-eyebrow">PREDICTED SCORE</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with sb3:
        st.markdown(
            f"""<div class="glass-card" style="text-align:center;">
                <div class="team-flag-large">{team_b['flag']}</div>
                <h3 style="margin:0.3rem 0;">{team_b['team_name']}</h3>
                <span class="rank-badge">FIFA #{team_b['fifa_rank']}</span>
                <div class="nickname-tag">{team_b['nickname']}</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="divider-glow">', unsafe_allow_html=True)

    # --- Win Probability ---
    st.markdown("### 📊 Win Probability")
    p1, p2, p3 = st.columns(3)
    with p1:
        st.metric(f"{team_a['team_name']} Win", f"{prediction['win_prob_a']}%")
        st.progress(min(1.0, prediction['win_prob_a'] / 100))
    with p2:
        st.metric("Draw", f"{prediction['draw_prob']}%")
        st.progress(min(1.0, prediction['draw_prob'] / 100))
    with p3:
        st.metric(f"{team_b['team_name']} Win", f"{prediction['win_prob_b']}%")
        st.progress(min(1.0, prediction['win_prob_b'] / 100))

    st.caption(f"Prediction engine: {prediction['model_used']} (selected via cross-validated comparison — see Historical Insights for model benchmarks)")

    st.markdown('<hr class="divider-glow">', unsafe_allow_html=True)

    # --- Match stats charts ---
    st.markdown("### ⚙️ Match Statistics")
    stat_col1, stat_col2 = st.columns(2)

    with stat_col1:
        fig_xg = go.Figure(data=[
            go.Bar(name=team_a['team_name'], x=["Expected Goals (xG)"], y=[prediction['xg_a']], marker_color="#00d4ff"),
            go.Bar(name=team_b['team_name'], x=["Expected Goals (xG)"], y=[prediction['xg_b']], marker_color="#ffd166"),
        ])
        fig_xg.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=320, barmode="group", title="Expected Goals (xG)",
        )
        st.plotly_chart(fig_xg, use_container_width=True)

    with stat_col2:
        fig_poss = go.Figure(data=[go.Pie(
            labels=[team_a['team_name'], team_b['team_name']],
            values=[prediction['possession_a'], prediction['possession_b']],
            hole=0.55, marker_colors=["#00d4ff", "#ffd166"],
        )])
        fig_poss.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=320, title="Possession %",
        )
        st.plotly_chart(fig_poss, use_container_width=True)

    fig_radar = go.Figure()
    categories = ["Attack", "Midfield", "Defense", "Form", "Elo Strength"]
    a_vals = [team_a['attack_score'], team_a['midfield_score'], team_a['defense_score'],
              team_a['form_points'] / 15 * 100, min(100, team_a['elo_rating'] / 21)]
    b_vals = [team_b['attack_score'], team_b['midfield_score'], team_b['defense_score'],
              team_b['form_points'] / 15 * 100, min(100, team_b['elo_rating'] / 21)]
    fig_radar.add_trace(go.Scatterpolar(r=a_vals + [a_vals[0]], theta=categories + [categories[0]], fill='toself', name=team_a['team_name'], line_color="#00d4ff"))
    fig_radar.add_trace(go.Scatterpolar(r=b_vals + [b_vals[0]], theta=categories + [categories[0]], fill='toself', name=team_b['team_name'], line_color="#ffd166"))
    fig_radar.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=420,
        title="Team Strength Radar",
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    shot_col1, shot_col2 = st.columns(2)
    with shot_col1:
        st.markdown(
            f"""<div class="glass-card">
                <div class="stat-eyebrow">SHOTS / ON TARGET — {team_a['team_name']}</div>
                <div class="big-number">{prediction['shots_a']} / {prediction['shots_on_target_a']}</div>
            </div>""", unsafe_allow_html=True,
        )
    with shot_col2:
        st.markdown(
            f"""<div class="glass-card">
                <div class="stat-eyebrow">SHOTS / ON TARGET — {team_b['team_name']}</div>
                <div class="big-number">{prediction['shots_b']} / {prediction['shots_on_target_b']}</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="divider-glow">', unsafe_allow_html=True)

    # --- Man of the match (best player from favored team) ---
    favored_team_name = team_a['team_name'] if prediction['win_prob_a'] >= prediction['win_prob_b'] else team_b['team_name']
    players = get_players_by_team(favored_team_name)
    if not players.empty:
        motm = players.iloc[0]
        st.markdown("### 🏅 Predicted Man of the Match")
        st.markdown(
            f"""<div class="glass-card" style="display:flex; align-items:center; gap:1.2rem;">
                <div style="font-size:2.4rem;">🏅</div>
                <div>
                    <div style="font-weight:700; font-size:1.2rem;">{motm['name']}</div>
                    <div class="nickname-tag">{motm['position']} · {favored_team_name} · Rating {motm['rating']}</div>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="divider-glow">', unsafe_allow_html=True)

    # --- AI Match Preview ---
    st.markdown("### 🤖 AI Match Preview")
    with st.spinner("Generating AI preview..."):
        preview = generate_match_preview(team_a, team_b, prediction)
    st.markdown(f'<div class="glass-card">{preview}</div>', unsafe_allow_html=True)

    st.page_link("pages/2_AI_Match_Commentary.py", label="▶️ Watch full AI minute-by-minute commentary", icon="🎙️")

else:
    st.info("Select two teams above and click **Simulate Match** to generate a full AI-powered prediction.")
