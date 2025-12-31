import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from uuid import uuid4
from .config import DB_PATH

RNG = np.random.default_rng(42)

def _rand_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"

def generate_synthetic_data(
    n_players: int = 20000,
    n_matches: int = 200000,
    n_sessions: int = 60000,
    n_patches: int = 6,
):
    # -----------------------------
    # Patches
    # -----------------------------
    start_date = datetime(2025, 1, 15)
    patch_versions = [f"v1.{i}" for i in range(n_patches)]
    patch_dates = [start_date + timedelta(days=21 * i) for i in range(n_patches)]

    characters = [f"op_{i}" for i in range(20)]
    patches = []
    for v, d in zip(patch_versions, patch_dates):
        touched = RNG.choice(characters, size=3, replace=False)
        delta = {c: float(np.round(RNG.normal(0, 0.03), 4)) for c in touched}
        patches.append(
            {
                "patch_version": v,
                "release_date": d.date().isoformat(),
                "balance_notes": "Synthetic balance update",
                "balance_delta_json": str(delta),
            }
        )
    df_patches = pd.DataFrame(patches)

    # -----------------------------
    # Players
    # -----------------------------
    regions = ["NA", "EU", "APAC", "LATAM"]
    platforms = ["PC", "Console", "Mobile"]
    cohort_base = datetime(2024, 9, 1)

    player_ids = [f"p_{i:05d}" for i in range(n_players)]
    df_players = pd.DataFrame(
        {
            "player_id": player_ids,
            "region": RNG.choice(regions, size=n_players, p=[0.35, 0.30, 0.25, 0.10]),
            "cohort_date": [
                (cohort_base + timedelta(days=int(x))).date().isoformat()
                for x in RNG.integers(0, 120, size=n_players)
            ],
            "platform": RNG.choice(platforms, size=n_players, p=[0.55, 0.25, 0.20]),
        }
    )

    # latent skill influences mmr + win rate
    skill = RNG.normal(0, 1, size=n_players)

    # -----------------------------
    # Matches
    # -----------------------------
    match_players = RNG.integers(0, n_players, size=n_matches)
    match_patch_idx = RNG.integers(0, n_patches, size=n_matches)

    mmr = (1200 + 250 * skill[match_players] + RNG.normal(0, 180, size=n_matches)).astype(int)
    mmr = np.clip(mmr, 1, 3000)

    def tier(m: int) -> str:
        if m < 900:
            return "Bronze"
        if m < 1200:
            return "Silver"
        if m < 1600:
            return "Gold"
        if m < 2100:
            return "Platinum"
        return "Diamond"

    rank_tier = [tier(int(m)) for m in mmr]
    char_pick = RNG.choice(characters, size=n_matches)
    opp_pick = RNG.choice(characters, size=n_matches)

    # base win probability depends on mmr (proxy for skill) + character strength noise
    char_strength = {c: RNG.normal(0, 0.03) for c in characters}
    base = 0.50 + (mmr - 1200) / 3000.0
    p_win = base + np.array([char_strength[c] for c in char_pick])
    p_win = np.clip(p_win, 0.05, 0.95)
    win = (RNG.random(n_matches) < p_win).astype(int)

    duration = RNG.integers(300, 1800, size=n_matches)
    kills = RNG.poisson(lam=6 + 3 * win, size=n_matches)
    deaths = RNG.poisson(lam=6 + 2 * (1 - win), size=n_matches)
    assists = RNG.poisson(lam=4, size=n_matches)

    # timestamps spread across patch windows
    ts = []
    for pv_i in match_patch_idx:
        window_start = patch_dates[pv_i]
        ts.append(window_start + timedelta(hours=int(RNG.integers(0, 21 * 24))))

    df_matches = pd.DataFrame(
        {
            "match_id": [_rand_id("m") for _ in range(n_matches)],
            "player_id": df_players.loc[match_players, "player_id"].values,
            "patch_version": [patch_versions[i] for i in match_patch_idx],
            "match_ts": [t.isoformat(sep=" ") for t in ts],
            "mode": RNG.choice(["Ranked", "Casual"], size=n_matches, p=[0.6, 0.4]),
            "mmr": mmr,
            "rank_tier": rank_tier,
            "character": char_pick,
            "opponent_character": opp_pick,
            "win": win,
            "duration_sec": duration,
            "kills": kills,
            "deaths": deaths,
            "assists": assists,
        }
    )

    # -----------------------------
    # Sessions
    # -----------------------------
    sess_players = RNG.integers(0, n_players, size=n_sessions)
    sess_patch_idx = RNG.integers(0, n_patches, size=n_sessions)

    sess_len = RNG.integers(600, 4 * 3600, size=n_sessions)  # 10 min to 4 hr
    sess_start = []
    for pv_i in sess_patch_idx:
        window_start = patch_dates[pv_i]
        sess_start.append(window_start + timedelta(hours=int(RNG.integers(0, 21 * 24))))
    sess_end = [s + timedelta(seconds=int(l)) for s, l in zip(sess_start, sess_len)]
    matches_played = np.clip((sess_len / 900 + RNG.normal(0, 1, size=n_sessions)).astype(int), 1, 12)

    df_sessions = pd.DataFrame(
        {
            "session_id": [_rand_id("s") for _ in range(n_sessions)],
            "player_id": df_players.loc[sess_players, "player_id"].values,
            "patch_version": [patch_versions[i] for i in sess_patch_idx],
            "session_start": [t.isoformat(sep=" ") for t in sess_start],
            "session_end": [t.isoformat(sep=" ") for t in sess_end],
            "session_length_sec": sess_len,
            "matches_played": matches_played,
        }
    )

    return df_players, df_patches, df_matches, df_sessions

def load_to_sqlite(df_players, df_patches, df_matches, df_sessions):
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        df_players.to_sql("players", conn, if_exists="replace", index=False)
        df_patches.to_sql("patches", conn, if_exists="replace", index=False)
        df_matches.to_sql("matches", conn, if_exists="replace", index=False)
        df_sessions.to_sql("sessions", conn, if_exists="replace", index=False)
    finally:
        conn.close()

def main():
    df_players, df_patches, df_matches, df_sessions = generate_synthetic_data()
    load_to_sqlite(df_players, df_patches, df_matches, df_sessions)
    print(f"Saved SQLite DB to: {DB_PATH}")
    print("Rows:")
    print(" players:", len(df_players))
    print(" patches:", len(df_patches))
    print(" matches:", len(df_matches))
    print(" sessions:", len(df_sessions))

if __name__ == "__main__":
    main()
