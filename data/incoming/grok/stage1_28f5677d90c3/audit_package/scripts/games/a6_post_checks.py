"""Post-correction checks on the *_corrected.csv copies."""
import pandas as pd, json
G = pd.concat([pd.read_csv(f, dtype={"game_id": str}) for f in ["ncaa_lacrosse_games_2023_corrected.csv", "ncaa_lacrosse_games_2024_corrected.csv", "ncaa_lacrosse_game_index_2025_corrected.csv"]])
U = G[G.usable_result]; R = {}
long = pd.concat([U[["game_id", "season", "game_date", "home_team"]].rename(columns={"home_team": "team"}), U[["game_id", "season", "game_date", "away_team"]].rename(columns={"away_team": "team"})])
long["d"] = pd.to_datetime(long.game_date); long = long.sort_values(["team", "d"])
long["gap"] = long.groupby(["season", "team"]).d.diff().dt.days
R["same_team_within_1_day_after"] = long[long.gap <= 1][["season", "team", "game_id", "game_date", "gap"]].to_dict("records")
U2 = U.assign(pair=U.apply(lambda r: "|".join(sorted([r.home_team, r.away_team])), axis=1), sc=U.apply(lambda r: "-".join(map(str, sorted([r.home_score, r.away_score]))), axis=1))
d = U2[U2.duplicated(["season", "pair", "sc"], keep=False)]
R["repeated_pairing_identical_score_after"] = d[["season", "game_id", "game_date", "pair", "sc"]].to_dict("records")
t = pd.read_csv("ncaa_lacrosse_team_game_stats_2023_2025_corrected.csv", dtype={"game_id": str}); p = pd.read_csv("ncaa_lacrosse_player_stats_2023_2025_corrected.csv", dtype={"game_id": str}, low_memory=False)
gd = G.set_index("game_id").game_date
R["team_date_mismatch"] = int((t.game_date != t.game_id.map(gd)).sum()); R["player_date_mismatch"] = int((p.game_date != p.game_id.map(gd)).sum())
R["team_rows_by_game_status"] = t.game_audit_status.value_counts().to_dict(); R["player_rows_by_game_status"] = p.game_audit_status.value_counts().to_dict()
R["team_rows_usable"] = int((t.game_audit_status != "rejected").sum()); R["player_rows_usable"] = int((p.game_audit_status != "rejected").sum())
c = pd.read_csv("odds_game_to_ncaa_game_crosswalk_corrected.csv", dtype=str); m = c[c.match_status == "matched"]
R["crosswalk_matched"] = len(m); R["crosswalk_to_rejected_games"] = int((m.ncaa_game_audit_status == "rejected").sum()); R["crosswalk_date_mismatch_vs_corrected_games"] = int((m.ncaa_game_date != m.ncaa_game_id.map(gd)).sum())
json.dump(R, open("post_correction_checks.json", "w"), indent=1, default=str); print(json.dumps(R, indent=1, default=str))
