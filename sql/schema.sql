DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS sessions;
DROP TABLE IF EXISTS patches;
DROP TABLE IF EXISTS purchases;

CREATE TABLE players (
  player_id TEXT PRIMARY KEY,
  region TEXT,
  cohort_date TEXT,
  platform TEXT
);

CREATE TABLE patches (
  patch_version TEXT PRIMARY KEY,
  release_date TEXT,
  balance_notes TEXT,
  balance_delta_json TEXT
);

CREATE TABLE matches (
  match_id TEXT PRIMARY KEY,
  player_id TEXT,
  patch_version TEXT,
  match_ts TEXT,
  mode TEXT,
  mmr INTEGER,
  rank_tier TEXT,
  character TEXT,
  opponent_character TEXT,
  win INTEGER,
  duration_sec INTEGER,
  kills INTEGER,
  deaths INTEGER,
  assists INTEGER,
  FOREIGN KEY(player_id) REFERENCES players(player_id),
  FOREIGN KEY(patch_version) REFERENCES patches(patch_version)
);

CREATE TABLE sessions (
  session_id TEXT PRIMARY KEY,
  player_id TEXT,
  patch_version TEXT,
  session_start TEXT,
  session_end TEXT,
  session_length_sec INTEGER,
  matches_played INTEGER,
  FOREIGN KEY(player_id) REFERENCES players(player_id),
  FOREIGN KEY(patch_version) REFERENCES patches(patch_version)
);

CREATE TABLE purchases (
  purchase_id TEXT PRIMARY KEY,
  player_id TEXT,
  patch_version TEXT,
  purchase_ts TEXT,
  amount_usd REAL,
  sku TEXT,
  FOREIGN KEY(player_id) REFERENCES players(player_id),
  FOREIGN KEY(patch_version) REFERENCES patches(patch_version)
);

CREATE INDEX idx_matches_player ON matches(player_id);
CREATE INDEX idx_matches_patch ON matches(patch_version);
CREATE INDEX idx_sessions_player ON sessions(player_id);
CREATE INDEX idx_sessions_patch ON sessions(patch_version);
