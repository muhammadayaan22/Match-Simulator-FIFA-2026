"""
FIFA 2026 AI ORACLE — Historical Match Dataset Generator
Synthesizes a realistic match-outcome dataset for model training by simulating
matches between the 48 qualified teams using a strength-differential model with
controlled randomness (upsets included). This mimics real football variance:
favorites win more often, but not always.
"""

import json
import random
import os
import math

random.seed(7)


def load_teams():
    here = os.path.dirname(__file__)
    with open(os.path.join(here, "teams.json")) as f:
        return json.load(f)


def team_strength(team):
    """Composite strength score blending Elo, FIFA rank, sub-scores, and form."""
    elo_component = team["elo_rating"] / 22.0
    rank_component = max(0, 50 - team["fifa_rank"] * 0.6)
    sub_scores = (team["attack_score"] + team["midfield_score"] + team["defense_score"]) / 3
    form_component = team["form_points"] / 15 * 10
    return elo_component * 0.4 + rank_component * 0.2 + sub_scores * 0.3 + form_component * 0.1


def simulate_match(team_a, team_b):
    s_a = team_strength(team_a)
    s_b = team_strength(team_b)
    diff = s_a - s_b

    # Logistic-style win probability from strength differential, with home/neutral noise
    prob_a = 1 / (1 + math.exp(-diff / 8.0))
    prob_a = max(0.05, min(0.92, prob_a))
    prob_draw_base = 0.27 - abs(diff) * 0.004
    prob_draw = max(0.10, min(0.30, prob_draw_base))
    prob_b = max(0.03, 1 - prob_a - prob_draw)
    # renormalize
    total = prob_a + prob_draw + prob_b
    prob_a, prob_draw, prob_b = prob_a / total, prob_draw / total, prob_b / total

    outcome = random.choices(["A", "D", "B"], weights=[prob_a, prob_draw, prob_b], k=1)[0]

    atk_a = team_a["attack_score"] / 100
    atk_b = team_b["attack_score"] / 100
    dfn_a = team_a["defense_score"] / 100
    dfn_b = team_b["defense_score"] / 100

    lambda_a = max(0.3, 1.6 * atk_a / max(0.4, dfn_b) * random.uniform(0.7, 1.3))
    lambda_b = max(0.3, 1.6 * atk_b / max(0.4, dfn_a) * random.uniform(0.7, 1.3))

    goals_a = poisson_sample(lambda_a)
    goals_b = poisson_sample(lambda_b)

    # Adjust goals to respect sampled outcome (keeps labels consistent with scoreline)
    if outcome == "A" and goals_a <= goals_b:
        goals_a = goals_b + random.choice([1, 1, 2])
    elif outcome == "B" and goals_b <= goals_a:
        goals_b = goals_a + random.choice([1, 1, 2])
    elif outcome == "D":
        goals_b = goals_a

    xg_a = round(lambda_a + random.uniform(-0.3, 0.3), 2)
    xg_b = round(lambda_b + random.uniform(-0.3, 0.3), 2)
    possession_a = round(50 + (s_a - s_b) * 0.8 + random.uniform(-5, 5), 1)
    possession_a = max(28, min(72, possession_a))

    return {
        "team_a": team_a["team_name"],
        "team_b": team_b["team_name"],
        "fifa_rank_a": team_a["fifa_rank"],
        "fifa_rank_b": team_b["fifa_rank"],
        "elo_a": team_a["elo_rating"],
        "elo_b": team_b["elo_rating"],
        "attack_a": team_a["attack_score"],
        "attack_b": team_b["attack_score"],
        "midfield_a": team_a["midfield_score"],
        "midfield_b": team_b["midfield_score"],
        "defense_a": team_a["defense_score"],
        "defense_b": team_b["defense_score"],
        "form_points_a": team_a["form_points"],
        "form_points_b": team_b["form_points"],
        "goals_a": goals_a,
        "goals_b": goals_b,
        "xg_a": max(0.1, xg_a),
        "xg_b": max(0.1, xg_b),
        "possession_a": possession_a,
        "result": outcome,  # A = team_a win, D = draw, B = team_b win
    }


def poisson_sample(lam):
    # Knuth's algorithm — avoids a numpy dependency for this small simulator
    L = math.exp(-lam)
    k = 0
    p = 1.0
    while True:
        k += 1
        p *= random.random()
        if p <= L:
            return k - 1


def generate_dataset(teams, n_matches=6000):
    matches = []
    n = len(teams)
    for _ in range(n_matches):
        i, j = random.sample(range(n), 2)
        match = simulate_match(teams[i], teams[j])
        matches.append(match)
    return matches


if __name__ == "__main__":
    teams = load_teams()
    matches = generate_dataset(teams, n_matches=6000)

    out_dir = os.path.dirname(__file__)
    with open(os.path.join(out_dir, "historical_matches.json"), "w") as f:
        json.dump(matches, f)

    print(f"Generated {len(matches)} synthetic historical matches for training.")
    results = {"A": 0, "D": 0, "B": 0}
    for m in matches:
        results[m["result"]] += 1
    print("Result distribution:", results)
