"""
FIFA 2026 AI ORACLE — AI Analyst Page
A football-knowledge chatbot grounded in the live Teams/Players database.
v1 implementation: retrieves relevant team rows by name-matching in the
question and injects them as context (lightweight retrieval-augmented
generation). A full vector-embedding RAG pipeline is a natural v2 upgrade
once this is validated.
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.theme import inject_theme
from utils.db import get_all_teams
from utils.ai_commentary import generate_ai_analysis

st.set_page_config(page_title="AI Analyst — FIFA 2026 AI Oracle", page_icon="🧠", layout="wide")
inject_theme()

st.markdown(
    '<div class="oracle-hero"><span class="stat-eyebrow">AI ANALYST</span>'
    '<h1 style="margin:0.3rem 0;">🧠 Ask the Oracle</h1>'
    '<p style="color:var(--text-muted);">Ask about any team, comparison, or World Cup question — answers are grounded in real team data.</p></div>',
    unsafe_allow_html=True,
)

teams_df = get_all_teams()


def build_context(question: str, teams_df) -> str:
    """Lightweight retrieval: find any team names mentioned in the question,
    plus always include the top-10 for general questions."""
    mentioned = teams_df[teams_df["team_name"].apply(lambda t: t.lower() in question.lower())]
    base = teams_df.head(10)
    relevant = pd_concat_unique(mentioned, base)

    lines = []
    for _, t in relevant.iterrows():
        lines.append(
            f"- {t['team_name']} ({t['nickname']}): FIFA Rank #{t['fifa_rank']}, Elo {t['elo_rating']}, "
            f"Attack {t['attack_score']}, Midfield {t['midfield_score']}, Defense {t['defense_score']}, "
            f"Recent form {t['recent_form']}, World Cups won: {t['world_cups_won']}."
        )
    return "\n".join(lines)


def pd_concat_unique(df1, df2):
    import pandas as pd
    combined = pd.concat([df1, df2]).drop_duplicates(subset="team_name")
    return combined


if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

for role, message in st.session_state["chat_history"]:
    with st.chat_message(role):
        st.markdown(message)

suggestions = [
    "Can Argentina win the World Cup?",
    "Compare France vs Brazil",
    "Who has the best attack in the tournament?",
    "Which underdog could cause an upset?",
]
st.markdown("**Try asking:**")
sug_cols = st.columns(len(suggestions))
clicked_suggestion = None
for i, s in enumerate(suggestions):
    with sug_cols[i]:
        if st.button(s, use_container_width=True, key=f"sug_{i}"):
            clicked_suggestion = s

question = st.chat_input("Ask the AI Analyst anything about FIFA World Cup 2026...")
final_question = clicked_suggestion or question

if final_question:
    st.session_state["chat_history"].append(("user", final_question))
    with st.chat_message("user"):
        st.markdown(final_question)

    context = build_context(final_question, teams_df)
    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            answer = generate_ai_analysis(final_question, context)
        st.markdown(answer)
    st.session_state["chat_history"].append(("assistant", answer))
