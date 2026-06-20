"""
FIFA 2026 AI ORACLE — Predictor Utility
Loads the trained outcome classifier + expected-goals regressors and exposes
a single `predict_match(team_a, team_b)` function used by the Streamlit app.
"""

import os
import json
import random
import joblib
import numpy as np

HERE = os.path.dirname(__file__)
ROOT = os.path.dirname(HERE)
MODELS_DIR = os.path.join(ROOT, "models")

_outcome_model = None
_scaler = None
_xg_model_a = None
_xg_model_b = None
_metadata = None


def _load_models():
    global _outcome_model, _scaler, _xg_model_a, _xg_model_b, _metadata
    if _outcome_model is None:
        _outcome_model = joblib.load(os.path.join(MODELS_DIR, "outcome_model.joblib"))
        _scaler = joblib.load(os.path.join(MODELS_DIR, "scaler.joblib"))
        _xg_model_a = joblib.load(os.path.join(MODELS_DIR, "xg_model_a.joblib"))
        _xg_model_b = joblib.load(os.path.join(MODELS_DIR, "xg_model_b.joblib"))
        with open(os.path.join(MODELS_DIR, "model_metadata.json")) as f:
            _metadata = json.load(f)
    return _outcome_model, _scaler, _xg_model_a, _xg_model_b, _metadata


def build_feature_vector(team_a: dict, team_b: dict):
    rank_diff = team_b["fifa_rank"] - team_a["fifa_rank"]
    elo_diff = team_a["elo_rating"] - team_b["elo_rating"]
    attack_diff = team_a["attack_score"] - team_b["attack_score"]
    midfield_diff = team_a["midfield_score"] - team_b["midfield_score"]
    defense_diff = team_a["defense_score"] - team_b["defense_score"]
    form_diff = team_a["form_points"] - team_b["form_points"]
    return np.array([[rank_diff, elo_diff, attack_diff, midfield_diff, defense_diff, form_diff]])


def predict_match(team_a: dict, team_b: dict, seed: int = None):
    """
    Returns a full prediction dict: win/draw probabilities, predicted scoreline,
    xG, possession split, and a simulated shots/stats profile.
    """
    if seed is not None:
        random.seed(seed)

    model, scaler, reg_a, reg_b, metadata = _load_models()
    X = build_feature_vector(team_a, team_b)

    if metadata["needs_scaler"]:
        X_input = scaler.transform(X)
    else:
        X_input = X

    proba = model.predict_proba(X_input)[0]  # [P(A win), P(Draw), P(B win)]
    win_a, draw, win_b = float(proba[0]), float(proba[1]), float(proba[2])

    xg_a = max(0.2, float(reg_a.predict(X)[0]))
    xg_b = max(0.2, float(reg_b.predict(X)[0]))
    # Keep expected goals in a realistic international-football band
    xg_a = min(xg_a, 3.2)
    xg_b = min(xg_b, 3.2)

    outcome = max([("A", win_a), ("D", draw), ("B", win_b)], key=lambda t: t[1])[0]
    goals_a, goals_b = _sample_scoreline(xg_a, xg_b, outcome)

    strength_a = (team_a["attack_score"] + team_a["midfield_score"] + team_a["defense_score"]) / 3
    strength_b = (team_b["attack_score"] + team_b["midfield_score"] + team_b["defense_score"]) / 3
    possession_a = round(50 + (strength_a - strength_b) * 0.6 + random.uniform(-4, 4), 1)
    possession_a = max(30, min(70, possession_a))

    shots_a = max(3, int(xg_a * random.uniform(4.5, 6.5)))
    shots_b = max(3, int(xg_b * random.uniform(4.5, 6.5)))
    shots_on_target_a = max(1, int(shots_a * random.uniform(0.35, 0.55)))
    shots_on_target_b = max(1, int(shots_b * random.uniform(0.35, 0.55)))

    return {
        "team_a": team_a["team_name"],
        "team_b": team_b["team_name"],
        "win_prob_a": round(win_a * 100, 1),
        "draw_prob": round(draw * 100, 1),
        "win_prob_b": round(win_b * 100, 1),
        "predicted_goals_a": goals_a,
        "predicted_goals_b": goals_b,
        "predicted_score": f"{goals_a} - {goals_b}",
        "xg_a": round(xg_a, 2),
        "xg_b": round(xg_b, 2),
        "possession_a": possession_a,
        "possession_b": round(100 - possession_a, 1),
        "shots_a": shots_a,
        "shots_b": shots_b,
        "shots_on_target_a": shots_on_target_a,
        "shots_on_target_b": shots_on_target_b,
        "model_used": metadata["best_model"],
    }


def _sample_scoreline(xg_a, xg_b, outcome, max_attempts=40):
    """
    Samples a realistic scoreline from independent Poisson(xg_a), Poisson(xg_b)
    distributions, rejecting samples until the result matches the model's
    predicted outcome. Keeps goal totals realistic (no inflation) while
    staying consistent with the classifier's predicted result.
    """
    ga, gb = 0, 0
    for _ in range(max_attempts):
        ga = _poisson_like(xg_a, max_goals=6)
        gb = _poisson_like(xg_b, max_goals=6)
        if outcome == "A" and ga > gb:
            return ga, gb
        if outcome == "B" and gb > ga:
            return ga, gb
        if outcome == "D" and ga == gb:
            return ga, gb

    # Fallback: apply the smallest possible correction to the last sample
    # rather than escalating goal totals.
    if outcome == "A":
        return (ga, gb - 1) if gb > 0 else (ga + 1, gb)
    if outcome == "B":
        return (ga - 1, gb) if ga > 0 else (ga, gb + 1)
    lower = min(ga, gb)
    return lower, lower


def _poisson_like(lam, max_goals=7):
    """Lightweight Poisson sampler (Knuth's algorithm) without a numpy.random dependency mismatch."""
    import math
    L = math.exp(-lam)
    k = 0
    p = 1.0
    while True:
        k += 1
        p *= random.random()
        if p <= L:
            return min(k - 1, max_goals)


def get_model_comparison():
    _, _, _, _, metadata = _load_models()
    return metadata["comparison"], metadata["best_model"]
