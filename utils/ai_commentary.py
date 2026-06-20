"""
FIFA 2026 AI ORACLE — AI Commentary Engine
Uses the Anthropic API (Claude) to generate broadcast-style minute-by-minute
match commentary, tactical breakdowns, and post-match analysis, grounded in
the ML-predicted scoreline and stats so the narrative stays consistent with
the simulation.

Set the ANTHROPIC_API_KEY environment variable before running, or pass a
key directly into get_client(). Swapping providers (e.g. to OpenAI or
Gemini) only requires editing this file — the rest of the app calls the
functions below, not the SDK directly.
"""

import os
import json
import re

try:
    import anthropic
except ImportError:
    anthropic = None

MODEL_NAME = "claude-sonnet-4-6"


def get_client():
    if anthropic is None:
        return None
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    return anthropic.Anthropic(api_key=api_key)


def _extract_json(text):
    """Strip markdown code fences if the model wraps JSON in them."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def generate_match_commentary(prediction: dict, team_a_meta: dict, team_b_meta: dict):
    """
    Returns a dict: {"timeline": [{"minute": int, "event": str, "type": str}, ...],
                      "tactical_summary": str, "crowd_reaction": str}
    Falls back to a deterministic templated commentary if no API key is set,
    so the app remains fully demoable without credentials.
    """
    client = get_client()
    if client is None:
        return _fallback_commentary(prediction, team_a_meta, team_b_meta)

    prompt = f"""You are a world-class football broadcast commentator (think Sky Sports / EA FC presentation style).

Generate minute-by-minute commentary for a FIFA World Cup 2026 match:

{team_a_meta['team_name']} ({team_a_meta['nickname']}) vs {team_b_meta['team_name']} ({team_b_meta['nickname']})

Final score: {prediction['team_a']} {prediction['predicted_goals_a']} - {prediction['predicted_goals_b']} {prediction['team_b']}
xG: {prediction['xg_a']} vs {prediction['xg_b']}
Possession: {prediction['possession_a']}% - {prediction['possession_b']}%

Generate exactly {prediction['predicted_goals_a'] + prediction['predicted_goals_b'] + 4} key match events spread across 90 minutes (kickoff, goals matching the final score exactly, a couple of near-misses/cards/tactical shifts, and full-time), each with a minute (1-90) and a vivid one-to-two sentence broadcast-style description. Make sure exactly {prediction['predicted_goals_a']} goal events are attributed to {team_a_meta['team_name']} and exactly {prediction['predicted_goals_b']} to {team_b_meta['team_name']}.

Respond ONLY with valid JSON, no preamble, no markdown fences, in this exact shape:
{{
  "timeline": [
    {{"minute": 1, "event": "...", "type": "kickoff"}},
    {{"minute": 23, "event": "...", "type": "goal", "team": "{team_a_meta['team_name']}"}},
    {{"minute": 90, "event": "...", "type": "fulltime"}}
  ],
  "tactical_summary": "2-3 sentence tactical breakdown of why the match unfolded this way",
  "crowd_reaction": "1-2 sentence social-media-style fan reaction"
}}
"""

    try:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in response.content if hasattr(block, "text"))
        data = json.loads(_extract_json(text))
        data["timeline"] = sorted(data["timeline"], key=lambda e: e["minute"])
        return data
    except Exception:
        return _fallback_commentary(prediction, team_a_meta, team_b_meta)


def generate_ai_analysis(question: str, teams_context: str):
    """
    Powers the AI Analyst chatbot. `teams_context` should be a compact text
    summary of relevant team stats (built by the caller from the DB) so the
    model reasons over real numbers rather than guessing.
    """
    client = get_client()
    if client is None:
        return ("AI Analyst requires an ANTHROPIC_API_KEY to be set in your environment. "
                "Once configured, I can answer questions like this grounded in live team stats.")

    prompt = f"""You are an expert football analyst for the FIFA 2026 AI Oracle platform.

Use this team data to answer the user's question accurately and with specific numbers where relevant:

{teams_context}

User question: {question}

Answer in 3-5 sentences, confident and analytical in tone, like a professional football pundit. Reference specific stats (FIFA rank, Elo, attack/midfield/defense scores) where useful. If the question can't be answered from the data, say so briefly rather than inventing facts."""

    try:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in response.content if hasattr(block, "text"))
    except Exception as e:
        return f"AI Analyst is temporarily unavailable ({type(e).__name__}). Please try again."


def generate_match_preview(team_a_meta: dict, team_b_meta: dict, prediction: dict):
    client = get_client()
    if client is None:
        return _fallback_preview(team_a_meta, team_b_meta, prediction)

    prompt = f"""Write a punchy, broadcast-style match preview (3-4 sentences) for:

{team_a_meta['team_name']} vs {team_b_meta['team_name']} — FIFA World Cup 2026

Model prediction: {prediction['win_prob_a']}% win / {prediction['draw_prob']}% draw / {prediction['win_prob_b']}% win, predicted score {prediction['predicted_score']}.

{team_a_meta['team_name']} are ranked #{team_a_meta['fifa_rank']} (Elo {team_a_meta['elo_rating']}), {team_b_meta['team_name']} are ranked #{team_b_meta['fifa_rank']} (Elo {team_b_meta['elo_rating']}).

Write it like a Sky Sports pre-match teaser. No markdown, plain text only."""

    try:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in response.content if hasattr(block, "text"))
    except Exception:
        return _fallback_preview(team_a_meta, team_b_meta, prediction)


# ---------------------------------------------------------------------------
# Deterministic fallbacks — keep the app fully functional with zero API key
# ---------------------------------------------------------------------------

def _fallback_commentary(prediction, team_a_meta, team_b_meta):
    timeline = [{"minute": 1, "event": f"Kickoff! {team_a_meta['team_name']} get us underway.", "type": "kickoff"}]
    goals_a, goals_b = prediction["predicted_goals_a"], prediction["predicted_goals_b"]
    minute_pool = sorted(__import__("random").sample(range(5, 89), goals_a + goals_b))
    gi = 0
    for _ in range(goals_a):
        timeline.append({
            "minute": minute_pool[gi],
            "event": f"GOAL! {team_a_meta['team_name']} break through — the {team_a_meta['nickname']} faithful erupt.",
            "type": "goal", "team": team_a_meta["team_name"],
        })
        gi += 1
    for _ in range(goals_b):
        timeline.append({
            "minute": minute_pool[gi],
            "event": f"GOAL! {team_b_meta['team_name']} respond in style.",
            "type": "goal", "team": team_b_meta["team_name"],
        })
        gi += 1
    timeline.append({"minute": 90, "event": "Full time! A result that matches the script written long before kickoff.", "type": "fulltime"})
    timeline.sort(key=lambda e: e["minute"])

    return {
        "timeline": timeline,
        "tactical_summary": (
            f"{team_a_meta['team_name']} controlled the tempo through midfield, while "
            f"{team_b_meta['team_name']} looked to hit on the counter. The final scoreline "
            f"reflects the underlying xG battle of {prediction['xg_a']} to {prediction['xg_b']}."
        ),
        "crowd_reaction": "Fans on both sides call it an instant classic. #WorldCup2026",
    }


def _fallback_preview(team_a_meta, team_b_meta, prediction):
    favorite = team_a_meta["team_name"] if prediction["win_prob_a"] > prediction["win_prob_b"] else team_b_meta["team_name"]
    return (
        f"{team_a_meta['team_name']} and {team_b_meta['team_name']} go head-to-head in a clash "
        f"that promises real tactical intrigue. With {favorite} given the edge by the model, "
        f"expect a tightly contested 90 minutes finishing somewhere near "
        f"{prediction['predicted_score']}."
    )
