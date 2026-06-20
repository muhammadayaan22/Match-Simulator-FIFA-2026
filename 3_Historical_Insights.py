"""
FIFA 2026 AI ORACLE — Historical Insights Page
Shows full team rankings, model performance comparison (Random Forest vs
XGBoost vs Logistic Regression), and team-level trend exploration.
"""

import streamlit as st
import sys
import os
import plotly.express as px

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.theme import inject_theme
from utils.db import get_all_teams, get_players_by_team
from utils.predictor import get_model_comparison

st.set_page_config(page_title="Historical Insights — FIFA 2026 AI Oracle", page_icon="📈", layout="wide")
inject_theme()

st.markdown(
    '<div class="oracle-hero"><span class="stat-eyebrow">HISTORICAL INSIGHTS</span>'
    '<h1 style="margin:0.3rem 0;">📈 Rankings, Trends & Model Performance</h1>'
    '<p style="color:var(--text-muted);">Explore the full 48-team field and see how the prediction engine was built and benchmarked.</p></div>',
    unsafe_allow_html=True,
)

teams_df = get_all_teams()

tab1, tab2, tab3 = st.tabs(["🌍 Full Rankings", "🤖 Model Benchmarks", "🔍 Team Deep Dive"])

with tab1:
    st.markdown("### Complete FIFA World Cup 2026 Field")
    fig = px.bar(
        teams_df.sort_values("elo_rating", ascending=True).tail(20),
        x="elo_rating", y="team_name", orientation="h",
        color="elo_rating", color_continuous_scale=["#0a8cb3", "#00d4ff"],
        labels={"elo_rating": "Elo Rating", "team_name": ""},
        title="Top 20 Teams by Elo Rating",
    )
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=600)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Full Table")
    display_df = teams_df[[
        "fifa_rank", "flag", "team_name", "confederation", "elo_rating",
        "attack_score", "midfield_score", "defense_score", "recent_form", "world_cups_won"
    ]].rename(columns={
        "fifa_rank": "Rank", "flag": "", "team_name": "Team", "confederation": "Confederation",
        "elo_rating": "Elo", "attack_score": "ATK", "midfield_score": "MID", "defense_score": "DEF",
        "recent_form": "Form", "world_cups_won": "WC Won",
    })
    st.dataframe(display_df, use_container_width=True, hide_index=True, height=420)

    conf_counts = teams_df["confederation"].value_counts().reset_index()
    conf_counts.columns = ["Confederation", "Teams"]
    fig_conf = px.pie(conf_counts, names="Confederation", values="Teams", hole=0.5,
                       color_discrete_sequence=px.colors.sequential.Blues_r,
                       title="Qualified Teams by Confederation")
    fig_conf.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=400)
    st.plotly_chart(fig_conf, use_container_width=True)

with tab2:
    st.markdown("### Prediction Engine — Model Comparison")
    st.caption("Trained on 6,000 simulated historical matches with strength-differential features (rank, Elo, attack/midfield/defense, recent form).")
    comparison, best_model = get_model_comparison()

    cols = st.columns(len(comparison))
    for i, (name, metrics) in enumerate(comparison.items()):
        with cols[i]:
            is_best = name == best_model
            badge = "✅ SELECTED" if is_best else ""
            st.markdown(
                f"""<div class="glass-card" style="text-align:center; {'border-color: var(--win-green);' if is_best else ''}">
                    <div class="stat-eyebrow">{name}</div>
                    <div style="color:var(--win-green); font-size:0.75rem; font-weight:700;">{badge}</div>
                    <div class="big-number" style="font-size:1.8rem; margin-top:0.4rem;">{metrics['accuracy']*100:.1f}%</div>
                    <div class="nickname-tag">Accuracy</div>
                    <div style="margin-top:0.6rem; color:var(--text-muted); font-size:0.85rem;">
                        Log Loss: {metrics['log_loss']:.3f}<br>
                        F1 (macro): {metrics['f1']:.3f}
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )

    st.markdown(
        f'<div class="glass-card" style="margin-top:1.2rem;">'
        f'<b>{best_model}</b> was selected as the production model based on lowest log loss '
        f'(best-calibrated probability estimates), which matters most for a win-probability product like this one — '
        f'a model can have decent accuracy while still being overconfident or underconfident in its probabilities.'
        f'</div>',
        unsafe_allow_html=True,
    )

with tab3:
    st.markdown("### Team Deep Dive")
    selected_team = st.selectbox("Choose a team", teams_df["team_name"].tolist())
    team_row = teams_df[teams_df["team_name"] == selected_team].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("FIFA Rank", f"#{team_row['fifa_rank']}")
    with c2:
        st.metric("Elo Rating", f"{team_row['elo_rating']}")
    with c3:
        st.metric("World Cups Won", f"{team_row['world_cups_won']}")
    with c4:
        st.metric("Recent Form", team_row["recent_form"])

    fig_sub = px.bar(
        x=["Attack", "Midfield", "Defense"],
        y=[team_row["attack_score"], team_row["midfield_score"], team_row["defense_score"]],
        color=["Attack", "Midfield", "Defense"],
        color_discrete_sequence=["#00d4ff", "#ffd166", "#2ee6a6"],
        labels={"x": "", "y": "Score"},
        title=f"{selected_team} — Sub-score Breakdown",
    )
    fig_sub.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=380, showlegend=False)
    st.plotly_chart(fig_sub, use_container_width=True)

    st.markdown(f"### 👥 Key Squad — {selected_team}")
    players_df = get_players_by_team(selected_team)
    if not players_df.empty:
        st.dataframe(
            players_df[["name", "position", "goals", "assists", "appearances", "rating"]].rename(
                columns={"name": "Player", "position": "Pos", "goals": "Goals", "assists": "Assists",
                         "appearances": "Caps", "rating": "Rating"}
            ),
            use_container_width=True, hide_index=True,
        )
