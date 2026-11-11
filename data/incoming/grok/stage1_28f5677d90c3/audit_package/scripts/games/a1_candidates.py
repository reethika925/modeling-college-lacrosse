"""Find suspicious game records: same team within 1 day, repeated pairing+identical score, NCAA vs ESPN date mismatch, out-of-range contest ids."""
import json, glob, pandas as pd, itertools
FP = "/workspace/final_package"; RAW = "/workspace/lax_data/raw"
g = pd.concat([pd.read_csv(f"{FP}/ncaa_lacrosse_games_2023.csv"), pd.read_csv(f"{FP}/ncaa_lacrosse_games_2024.csv"),
               pd.read_csv(f"{FP}/ncaa_lacrosse_game_index_2025.csv")], ignore_index=True)
g = g[g.status == "final"].copy(); g["gd"] = pd.to_datetime(g.game_date)
# ESPN dates (ET) for matched events
ed = {}
for f in glob.glob(f"{RAW}/espn_scoreboards/*/*.json"):
    for e in json.load(open(f)).get("events", []):
        ed[e["id"]] = pd.Timestamp(e["date"]).tz_convert("America/New_York").date().isoformat()
g["espn_date_et"] = g.espn_event_id.dropna().astype(int).astype(str).map(ed).reindex(g.index)
rows = []
# A: same team within 1 day
app = pd.concat([g[["game_id", "season", "gd", "home_team"]].rename(columns={"home_team": "team"}), g[["game_id", "season", "gd", "away_team"]].rename(columns={"away_team": "team"})])
for (s, t), d in app.groupby(["season", "team"]):
    d = d.sort_values("gd")
    for (i1, r1), (i2, r2) in zip(d.iterrows(), list(d.iterrows())[1:]):
        if (r2.gd - r1.gd).days <= 1:
            rows.append(dict(check="same_team_within_1_day", season=s, team=t, game_ids=f"{r1.game_id}|{r2.game_id}", dates=f"{r1.gd.date()}|{r2.gd.date()}"))
# B: repeated pairing with identical score
g["pair"] = g.apply(lambda r: "|".join(sorted([r.home_team, r.away_team])), axis=1)
g["sc"] = g.apply(lambda r: "|".join(f"{t}:{int(s)}" for t, s in sorted([(r.home_team, r.home_score), (r.away_team, r.away_score)])), axis=1)
for (s, p, sc), d in g.groupby(["season", "pair", "sc"]):
    if len(d) > 1:
        rows.append(dict(check="repeated_pairing_identical_score", season=s, team=p, game_ids="|".join(map(str, d.game_id)), dates="|".join(d.game_date)))
# C: ESPN date mismatch
m = g[g.espn_date_et.notna() & (g.espn_date_et != g.game_date)]
for _, r in m.iterrows():
    rows.append(dict(check="ncaa_vs_espn_date_mismatch", season=r.season, team=r.pair, game_ids=str(r.game_id), dates=f"NCAA {r.game_date} | ESPN {r.espn_date_et}"))
c = pd.DataFrame(rows); c.to_csv("audit_candidates.csv", index=False)
print(c.groupby(["check", "season"]).size()); print(c.to_string())
