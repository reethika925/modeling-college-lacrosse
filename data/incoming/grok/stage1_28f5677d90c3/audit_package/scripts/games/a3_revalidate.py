"""Re-validation of games 2023/2024, 2025 index, team & player game stats, alias table, odds crosswalk (read-only inputs)."""
import json, glob, os, pandas as pd, numpy as np
FP = "/workspace/final_package"; RAW = "/workspace/lax_data/raw"; R = {}; issues = []
g23, g24 = pd.read_csv(f"{FP}/ncaa_lacrosse_games_2023.csv"), pd.read_csv(f"{FP}/ncaa_lacrosse_games_2024.csv")
g25 = pd.read_csv(f"{FP}/ncaa_lacrosse_game_index_2025.csv")
G = pd.concat([g23, g24, g25], ignore_index=True); G["game_id"] = G.game_id.astype(str)
t = pd.read_csv(f"{FP}/ncaa_lacrosse_team_game_stats_2023_2025.csv"); t["game_id"] = t.game_id.astype(str)
p = pd.read_csv(f"{FP}/ncaa_lacrosse_player_stats_2023_2025.csv", low_memory=False); p["game_id"] = p.game_id.astype(str)
al = pd.read_csv(f"{FP}/ncaa_lacrosse_team_aliases.csv", dtype=str)
cw = pd.read_csv(f"{FP}/odds_game_to_ncaa_game_crosswalk.csv", dtype=str)
def add(rec, ds, status, reason, ev=""): issues.append(dict(record=rec, dataset=ds, status=status, reason=reason, evidence=ev))
# 1 sport / division / season from raw box scores
bad_sport = []
for gid in t.game_id.unique():
    f = f"{RAW}/boxscores/{gid}.json"
    if os.path.exists(f):
        b = (json.load(open(f)).get("data") or {}).get("boxscore") or {}
        if b and (b.get("sportCode") != "MLA" or b.get("division") != 1): bad_sport.append(gid)
R["boxscores_not_MLA_D1"] = bad_sport
R["season_year_mismatch"] = int((pd.to_datetime(G.game_date).dt.year != G.season).sum())
R["dates_outside_feb_may"] = G[~pd.to_datetime(G.game_date).dt.month.isin([2, 3, 4, 5])].game_id.tolist()
# 2 duplicates
R["duplicate_game_ids"] = int(G.game_id.duplicated().sum())
# 3 contradictory scores
v = pd.read_csv(f"{FP}/qa/validation_espn_crosscheck.csv"); vv = v[v.espn_scores_agree == False]
for _, r in vv.iterrows(): add(f"game {r.game_id}", "game_index_2025" if r.season == 2025 else f"games_{r.season}", "provisional",
    f"NCAA score {r.home_team} {int(r.home_score)}-{int(r.away_score)} {r.away_team} vs ESPN {r.espn_home_score:.0f}-{r.espn_away_score:.0f}", f"ESPN event {int(r.espn_event_id)}")
bx = t[t.goals.notna() & (t.goals != t.final_score_scoreboard)]
for _, r in bx.iterrows(): add(f"team_game {r.game_id}/{r.team}", "team_game_stats", "provisional", f"box-score goals {r.goals:.0f} != final score {r.final_score_scoreboard:.0f} (box incomplete; result itself verified)", r.source_url)
ps = p.groupby(["game_id", "team_id_ncaa"]).goals.sum(); tg = t.set_index(["game_id", "team_id_ncaa"]).goals
j = pd.concat([ps.rename("p"), tg.rename("t")], axis=1).dropna(); jm = j[j.p != j.t]
for (gid, tid), r in jm.iterrows(): add(f"player_rows {gid}/{tid}", "player_stats", "provisional", f"sum of player goals {r.p:.0f} != team goals {r.t:.0f}", f"https://www.ncaa.com/game/{gid}/boxscore")
R["player_goal_sum_mismatch_team_games"] = len(jm)
# 4 impossible / inconsistent stats
opp = t[["game_id", "team_id_ncaa", "shots_on_goal", "goals"]].rename(columns={"team_id_ncaa": "opponent_id_ncaa", "shots_on_goal": "opp_sog", "goals": "opp_goals"})
x = t.merge(opp, on=["game_id", "opponent_id_ncaa"], how="left")
x["save_identity_gap"] = x.saves - (x.opp_sog - x.opp_goals)
R["saves_eq_oppSOG_minus_oppGoals"] = {"rows_checked": int(x.save_identity_gap.notna().sum()), "exact": int((x.save_identity_gap == 0).sum()), "abs_gap_le_1": int((x.save_identity_gap.abs() <= 1).sum())}
for _, r in x[x.save_identity_gap.abs() > 2].iterrows():
    add(f"team_game {r.game_id}/{r.team}", "team_game_stats", "provisional", f"saves {r.saves:.0f} vs opponent SOG-goals {r.opp_sog - r.opp_goals:.0f} (gap {r.save_identity_gap:.0f})", r.source_url)
imp = {"sog_gt_shots": t.shots_on_goal > t.shots, "goals_gt_sog": t.goals > t.shots_on_goal, "fo_won_gt_att": t.faceoffs_won > t.faceoffs_attempted,
       "clears_gt_att": t.clears_completed > t.clears_attempted, "emo_goals_gt_opp": t.emo_goals > t.emo_opportunities,
       "negative": (t.select_dtypes("number") < 0).any(axis=1), "shooting_pct_gt_1": t.shooting_pct > 1,
       "faceoff_total_implausible": (t.faceoffs_attempted.notna()) & ((t.faceoffs_attempted < (t.goals + t.goals_allowed) - 2) | (t.faceoffs_attempted > (t.goals + t.goals_allowed) + 10))}
R["impossible_stats"] = {k: int(m.sum()) for k, m in imp.items()}
for _, r in t[imp["emo_goals_gt_opp"]].iterrows(): add(f"team_game {r.game_id}/{r.team}", "team_game_stats", "provisional", f"EMO goals {r.emo_goals:.0f} > EMO opportunities {r.emo_opportunities:.0f} (as published by NCAA)", r.source_url)
pi = {"player_sog_gt_shots": p.shots_on_goal > p.shots, "player_goals_gt_sog": p.goals > p.shots_on_goal, "player_points_ne_g_plus_a": p.points != p.goals + p.assists,
      "player_fo_won_gt_att": p.faceoffs_won > p.faceoffs_attempted, "player_negative": (p[["goals", "assists", "shots", "shots_on_goal", "ground_balls"]] < 0).any(axis=1)}
R["player_impossible_stats"] = {k: int(m.sum()) for k, m in pi.items()}
R["player_duplicate_rows"] = int(p.duplicated(["game_id", "team_id_ncaa", "player_last_raw", "player_first_raw", "jersey"]).sum())
# 5 alias consistency
seo_names = pd.concat([G[["home_team_seo", "home_team"]].set_axis(["seo", "name"], axis=1), G[["away_team_seo", "away_team"]].set_axis(["seo", "name"], axis=1)]).dropna()
R["seo_with_multiple_names"] = seo_names.groupby("seo").name.nunique().loc[lambda s: s > 1].to_dict()
R["name_with_multiple_seo"] = seo_names.groupby("name").seo.nunique().loc[lambda s: s > 1].to_dict()
R["alias_multi_ncaa_ids"] = al[al.ncaa_team_ids.fillna("").str.contains(r"\|")][["ncaa_seo", "ncaa_team_ids"]].to_dict("records")
R["alias_multi_espn_ids"] = al[al.espn_team_id.fillna("").str.contains(r"\|")][["ncaa_seo", "espn_team_id"]].to_dict("records")
R["alias_missing_espn_id"] = al[al.espn_team_id.isna()].ncaa_seo.tolist()
tid = pd.concat([t[["team_id_ncaa", "team_seo", "season"]]]).drop_duplicates()
R["team_id_with_multiple_seo"] = tid.groupby("team_id_ncaa").team_seo.nunique().loc[lambda s: s > 1].to_dict()
# 6 missing ids / join keys
fin = G[G.status == "final"]
R["final_games_missing_team_ids"] = fin[fin.home_team_id_ncaa.isna() | fin.away_team_id_ncaa.isna()][["game_id", "season", "game_date", "home_team", "away_team", "result_source"]].to_dict("records")
R["team_stats_game_ids_not_in_games"] = sorted(set(t.game_id) - set(G.game_id))
R["player_game_ids_not_in_team_stats"] = sorted(set(p.game_id) - set(t.game_id))
tt = t.groupby("game_id").team_id_ncaa.apply(set)
pt = p.groupby("game_id").team_id_ncaa.apply(set)
R["player_team_ids_not_in_game"] = [gid for gid in pt.index if not pt[gid] <= tt.get(gid, set())]
gi = G.set_index("game_id")
hm = t.merge(G[["game_id", "home_team_id_ncaa", "away_team_id_ncaa"]], on="game_id")
hm["ok"] = np.where(hm.home_away == "home", hm.team_id_ncaa == hm.home_team_id_ncaa, hm.team_id_ncaa == hm.away_team_id_ncaa)
R["team_stats_home_away_inconsistent_with_games"] = int((~hm.ok).sum())
R["team_stats_date_ne_games_date"] = int((t.merge(G[["game_id", "game_date"]], on="game_id", suffixes=("", "_g")).pipe(lambda d: d.game_date != d.game_date_g)).sum())
R["final_games_without_team_stats"] = {int(s): int(len(set(fin[fin.season == s].game_id) - set(t.game_id))) for s in (2023, 2024, 2025)}
c = cw[cw.match_status == "matched"]
R["crosswalk_ids_not_in_games"] = sorted(set(c.ncaa_game_id) - set(G.game_id))
R["crosswalk_matched_with_date_shift"] = c[c.odds_game_date != c.ncaa_game_date][["odds_game_id", "ncaa_game_id", "odds_game_date", "ncaa_game_date"]].to_dict("records")
json.dump(R, open("revalidation_results.json", "w"), indent=1, default=str)
pd.DataFrame(issues).to_csv("revalidation_issues.csv", index=False)
print(json.dumps(R, indent=1, default=str)[:6000]); print(len(issues), "issues")
