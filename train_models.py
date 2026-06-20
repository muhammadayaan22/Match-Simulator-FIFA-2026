"""
FIFA 2026 AI ORACLE — Prediction Engine Training
Trains and compares three classifiers (Logistic Regression, Random Forest,
XGBoost) on the synthesized historical match dataset to predict match outcome
(Team A win / Draw / Team B win), then trains two small regressors to predict
each side's expected goals. The best classifier (by accuracy + log loss) is
saved for use by the live app.
"""

import json
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, log_loss, f1_score
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

HERE = os.path.dirname(__file__)
ROOT = os.path.dirname(HERE)
DATA_DIR = os.path.join(ROOT, "data")

FEATURE_COLS = [
    "rank_diff", "elo_diff", "attack_diff", "midfield_diff",
    "defense_diff", "form_diff",
]


def load_data():
    with open(os.path.join(DATA_DIR, "historical_matches.json")) as f:
        matches = json.load(f)
    df = pd.DataFrame(matches)

    df["rank_diff"] = df["fifa_rank_b"] - df["fifa_rank_a"]  # positive => team A ranked better
    df["elo_diff"] = df["elo_a"] - df["elo_b"]
    df["attack_diff"] = df["attack_a"] - df["attack_b"]
    df["midfield_diff"] = df["midfield_a"] - df["midfield_b"]
    df["defense_diff"] = df["defense_a"] - df["defense_b"]
    df["form_diff"] = df["form_points_a"] - df["form_points_b"]

    label_map = {"A": 0, "D": 1, "B": 2}
    df["label"] = df["result"].map(label_map)
    return df


def train_classifiers(df):
    X = df[FEATURE_COLS].values
    y = df["label"].values
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    results = {}

    # --- Logistic Regression ---
    lr = LogisticRegression(max_iter=1000)
    lr.fit(X_train_scaled, y_train)
    lr_preds = lr.predict(X_test_scaled)
    lr_proba = lr.predict_proba(X_test_scaled)
    results["LogisticRegression"] = {
        "model": lr,
        "accuracy": accuracy_score(y_test, lr_preds),
        "log_loss": log_loss(y_test, lr_proba),
        "f1": f1_score(y_test, lr_preds, average="macro"),
        "needs_scaler": True,
    }

    # --- Random Forest ---
    rf = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    rf_preds = rf.predict(X_test)
    rf_proba = rf.predict_proba(X_test)
    results["RandomForest"] = {
        "model": rf,
        "accuracy": accuracy_score(y_test, rf_preds),
        "log_loss": log_loss(y_test, rf_proba),
        "f1": f1_score(y_test, rf_preds, average="macro"),
        "needs_scaler": False,
    }

    # --- XGBoost ---
    xgb_model = xgb.XGBClassifier(
        n_estimators=250, max_depth=5, learning_rate=0.08,
        objective="multi:softprob", num_class=3,
        eval_metric="mlogloss", random_state=42,
    )
    xgb_model.fit(X_train, y_train)
    xgb_preds = xgb_model.predict(X_test)
    xgb_proba = xgb_model.predict_proba(X_test)
    results["XGBoost"] = {
        "model": xgb_model,
        "accuracy": accuracy_score(y_test, xgb_preds),
        "log_loss": log_loss(y_test, xgb_proba),
        "f1": f1_score(y_test, xgb_preds, average="macro"),
        "needs_scaler": False,
    }

    return results, scaler


def train_goal_regressors(df):
    """Small regressors to predict expected goals for each side, used to build scorelines."""
    X = df[FEATURE_COLS].values
    y_a = df["xg_a"].values
    y_b = df["xg_b"].values

    reg_a = RandomForestRegressor(n_estimators=150, max_depth=6, random_state=42, n_jobs=-1)
    reg_b = RandomForestRegressor(n_estimators=150, max_depth=6, random_state=42, n_jobs=-1)
    reg_a.fit(X, y_a)
    reg_b.fit(X, y_b)
    return reg_a, reg_b


def main():
    print("Loading synthetic historical match data...")
    df = load_data()
    print(f"  {len(df)} matches loaded.\n")

    print("Training and comparing classifiers...")
    results, scaler = train_classifiers(df)

    print(f"\n{'Model':<20}{'Accuracy':<12}{'Log Loss':<12}{'F1 (macro)':<12}")
    print("-" * 56)
    for name, r in results.items():
        print(f"{name:<20}{r['accuracy']:<12.4f}{r['log_loss']:<12.4f}{r['f1']:<12.4f}")

    # Pick best model by lowest log loss (well-calibrated probabilities matter for this app)
    best_name = min(results, key=lambda k: results[k]["log_loss"])
    best_model = results[best_name]["model"]
    print(f"\nBest model selected: {best_name}")

    print("\nTraining expected-goals regressors...")
    reg_a, reg_b = train_goal_regressors(df)

    models_dir = HERE
    joblib.dump(best_model, os.path.join(models_dir, "outcome_model.joblib"))
    joblib.dump(scaler, os.path.join(models_dir, "scaler.joblib"))
    joblib.dump(reg_a, os.path.join(models_dir, "xg_model_a.joblib"))
    joblib.dump(reg_b, os.path.join(models_dir, "xg_model_b.joblib"))

    metadata = {
        "best_model": best_name,
        "needs_scaler": results[best_name]["needs_scaler"],
        "feature_cols": FEATURE_COLS,
        "comparison": {
            name: {"accuracy": r["accuracy"], "log_loss": r["log_loss"], "f1": r["f1"]}
            for name, r in results.items()
        },
    }
    with open(os.path.join(models_dir, "model_metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nModels saved to {models_dir}")


if __name__ == "__main__":
    main()
