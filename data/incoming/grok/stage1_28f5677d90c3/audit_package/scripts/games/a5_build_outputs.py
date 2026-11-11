"""Build audit outputs: game_date_corrections.csv, games_stats_excluded_or_unverified.csv, *_corrected.csv copies, usable counts.
Originals in /workspace/final_package are read only; corrected copies are written here."""
import json, glob, os, pandas as pd, numpy as np
FP = "/workspace/final_package"; RAW = "/workspace/lax_data/raw"; OUT = "/workspace/audit/games"
games = {2023: pd.read_csv(f"{FP}/ncaa_lacrosse_games_2023.csv", dtype={"game_id": str}),
         2024: pd.read_csv(f"{FP}/ncaa_lacrosse_games_2024.csv", dtype={"game_id": str}),
         2025: pd.read_csv(f"{FP}/ncaa_lacrosse_game_index_2025.csv", dtype={"game_id": str})}
DSN = {2023: "ncaa_lacrosse_games_2023", 2024: "ncaa_lacrosse_games_2024", 2025: "ncaa_lacrosse_game_index_2025"}
t = pd.read_csv(f"{FP}/ncaa_lacrosse_team_game_stats_2023_2025.csv", dtype={"game_id": str})
p = pd.read_csv(f"{FP}/ncaa_lacrosse_player_stats_2023_2025.csv", dtype={"game_id": str}, low_memory=False)
cw = pd.read_csv(f"{FP}/odds_game_to_ncaa_game_crosswalk.csv", dtype=str)
dup = pd.read_csv(f"{FP}/qa/excluded_or_flagged_duplicate_listings.csv", dtype={"game_id": str, "suspected_duplicate_of": str})
esv = pd.read_csv(f"{FP}/qa/validation_espn_crosscheck.csv", dtype={"game_id": str})
cmp_ = pd.read_csv(f"{OUT}/school_schedule_comparison.csv", dtype={"game_id": str})
reval = pd.read_csv(f"{OUT}/revalidation_issues.csv")
R = json.load(open(f"{OUT}/revalidation_results.json"))
# ESPN event -> local (ET) date
ed = {}
for f in glob.glob(f"{RAW}/espn_scoreboards/*/*.json"):
    for e in json.load(open(f)).get("events", []):
        ed[str(e["id"])] = pd.Timestamp(e["date"]).tz_convert("America/New_York").date().isoformat()
G = pd.concat([g.assign(_ds=DSN[s]) for s, g in games.items()], ignore_index=True)
G["espn_date"] = G.espn_event_id.map(lambda x: ed.get(str(int(x))) if pd.notna(x) else None)
EV = {"bing": "evidence/binghamton_2025_schedule.html", "umbc_recap": "evidence/umbc_recap_2025-04-12.html"}
corr = []  # game-level corrections: game_id, field, orig, new, url, evfile, reason, status
def C(gid, field, orig, new, url, ev, reason, status): corr.append(dict(game_id=gid, field=field, original_value=orig, corrected_value=new, source_url=url, evidence_file=ev, reason=reason, status=status))
# --- A. date corrections from school pages (same opponent + same score, date differs) ---
sc = cmp_[(cmp_.match == "opponent+score") & (cmp_.date_agrees == False)]
for gid, grp in sc.groupby("game_id"):
    g = G[G.game_id == gid].iloc[0]
    if gid in set(dup.game_id): continue  # phantom duplicates are rejected, not re-dated
    dates = grp.school_date.unique()
    if gid == "6449835":
        urls = "https://binghamtonbearcats.com/sports/mens-lacrosse/schedule/2025 | https://umbcretrievers.com/news/2025/4/12/mens-lacrosse-runs-away-from-binghamton-on-senior-day.aspx"
        evs = f"{EV['bing']} | {EV['umbc_recap']}" + "".join(f" | {e}" for e in grp.evidence_file if "binghamton" not in e)
    else:
        urls = " | ".join(grp.school_page); evs = " | ".join(grp.evidence_file)
    st = "verified" if len(dates) == 1 else "provisional"
    espn = f"; ESPN date {g.espn_date}" if g.espn_date else "; no ESPN listing"
    C(gid, "game_date", g.game_date, dates[0], urls, evs, f"{g.home_team} {g.home_score:.0f}-{g.away_score:.0f} {g.away_team}: NCAA scoreboard lists it on {g.game_date}; official school schedule(s) {len(grp)} page(s) list same opponent and score on {', '.join(dates)}{espn}", st)
# --- B. missing result: games NCAA left as 'pre' but school page shows a final ---
for _, r in cmp_[(cmp_.status == "pre") & cmp_.school_result.notna()].iterrows():
    g = G[G.game_id == r.game_id].iloc[0]; res, sco = r.school_result.split(" "); a, b = map(int, sco.split("-"))
    ts, os_ = (max(a, b), min(a, b)) if res == "W" else (min(a, b), max(a, b))
    home = g.home_team_seo == r.team; hs, as_ = (ts, os_) if home else (os_, ts)
    for fld, o, n in [("status", g.status, "final"), ("home_score", g.home_score, hs), ("away_score", g.away_score, as_)]:
        C(r.game_id, fld, o, n, r.school_page, r.evidence_file, f"NCAA scoreboard never posted a result for {g.home_team} vs {g.away_team} ({g.game_date}); official {r.team} schedule shows {r.school_result} on {r.school_date}. No NCAA box score, so no team/player stats.", "verified")
# --- C. neutral-site flags (2023/2024 files only) ---
for _, r in cmp_[cmp_.homeaway_status == "neutral_or_nominal_home"].iterrows():
    g = G[G.game_id == r.game_id].iloc[0]
    if g._ds == DSN[2025] or g.neutral_site == True: continue
    explicit = r.school_ha_class == "neutral"
    C(r.game_id, "neutral_site", g.neutral_site, True, r.school_page, r.evidence_file,
      f"school page lists the game at {r.school_loc} ({'neutral class' if explicit else 'vs at a venue that is not either listed home team campus'}); NCAA home/away kept as nominal designation",
      "verified" if explicit else "provisional")
CORR = pd.DataFrame(corr).drop_duplicates(["game_id", "field"])
# --- apply to game files ---
def apply_games(df):
    df = df.copy(); df["original_game_date"] = df.game_date; df["corrections_applied"] = ""
    for _, c in CORR[CORR.game_id.isin(df.game_id)].iterrows():
        if c.field not in df.columns: continue
        m = df.game_id == c.game_id
        if c.field == "neutral_site": df.loc[m, "neutral_site_basis"] = "official_school_schedule_" + c.status
        df.loc[m, c.field] = c.corrected_value; df.loc[m, "corrections_applied"] += f"{c.field}:{c.original_value}->{c.corrected_value}({c.status});"
    return df
out_rows = []
def gc(row_key, ds, c):
    out_rows.append(dict(record_key=row_key, dataset=ds, field=c.field, original_value=c.original_value, corrected_value=c.corrected_value,
                         source_url=c.source_url, evidence_file=c.evidence_file, reason=c.reason, status=c.status))
for _, c in CORR.iterrows():
    s = int(G[G.game_id == c.game_id].season.iloc[0]); gc(f"game_id={c.game_id}", DSN[s], c)
    if c.field == "game_date":
        for _, r in t[t.game_id == c.game_id].iterrows(): gc(f"game_id={c.game_id}|team_id_ncaa={r.team_id_ncaa}", "ncaa_lacrosse_team_game_stats_2023_2025", c)
        n = int((p.game_id == c.game_id).sum())
        if n: gc(f"game_id={c.game_id} (all {n} player rows)", "ncaa_lacrosse_player_stats_2023_2025", c)
        for _, r in cw[cw.ncaa_game_id == c.game_id].iterrows(): gc(f"odds_game_id={r.odds_game_id}", "odds_game_to_ncaa_game_crosswalk (ncaa_game_date)", c)
        if c.game_id == "6449835":  # start time: Binghamton page lists noon ET
            out_rows.append(dict(record_key="game_id=6449835", dataset=DSN[2025], field="start_time_utc", original_value=G[G.game_id == "6449835"].start_time_utc.iloc[0],
                                 corrected_value="2025-04-12T16:00:00+00:00", source_url="https://binghamtonbearcats.com/sports/mens-lacrosse/schedule/2025", evidence_file=EV["bing"],
                                 reason="Binghamton schedule lists 'Apr 12 (Sat) noon at UMBC' (12:00 EDT = 16:00 UTC)", status="verified"))
GDC = pd.DataFrame(out_rows); GDC.to_csv(f"{OUT}/game_date_corrections.csv", index=False)
# --- statuses ---
school_ok = cmp_[(cmp_.date_agrees == True) & (cmp_.score_agrees == True)].game_id
school_ok = set(school_ok) | set(CORR[(CORR.status == "verified") & CORR.field.isin(["game_date", "status"])].game_id)
espn_ok = set(esv[esv.espn_scores_agree == True].game_id)
espn_date_ok = set(G[(G.espn_date.notna()) & (G.espn_date == G.game_date)].game_id)
ED = G.set_index("game_id").espn_date.to_dict()
rejected = {"6444405": "phantom duplicate listing of 6386334 (Hampton 4-29 Fairfield); Hampton and Fairfield official schedules show only one meeting, on 2025-03-15",
            "6455124": "LIU 10-9 Quinnipiac (OT) 2025-04-20 appears on neither LIU's nor Quinnipiac's official 2025 schedule; ~11 of 24 players per side appear in no other 2025 game for that team; likely an exhibition/non-countable contest posted to the NCAA scoreboard"}
school_ok.add("espn_401658258")  # Princeton official schedule: 2024-05-05 vs Penn W 18-11 (ESPN-only row has no NCAA team ids, so the matcher could not pair it)
ex = []
def X(rec, ds, st, reason, ev): ex.append(dict(record=rec, dataset=ds, status=st, reason=reason, evidence=ev))
def status_games(df, s):
    df = df.copy(); st, rs = [], []
    for _, g in df.iterrows():
        if g.game_id in rejected: st.append("rejected"); rs.append(rejected[g.game_id]); continue
        if g.status != "final" or pd.isna(g.home_score): st.append("rejected"); rs.append("no final result"); continue
        reasons = []
        if g.game_id in school_ok: reasons.append("official school schedule agrees (date/score)")
        if g.game_id in espn_ok: reasons.append("ESPN score agrees" + (" and same date" if g.game_id in espn_date_ok else f" (ESPN date {ED.get(g.game_id)})"))
        if g.game_id == "espn_401658258": reasons.append("ESPN-only row (missing from NCAA scoreboard; no box score); Princeton official schedule confirms")
        conflict = g.game_id in set(esv[esv.espn_scores_agree == False].game_id)
        if conflict and g.game_id in school_ok: reasons.append("NCAA vs ESPN score conflict resolved in favour of NCAA by official school schedule"); conflict = False
        verified = (g.game_id in school_ok) or (g.game_id in espn_ok and (g.game_id in espn_date_ok or ED.get(g.game_id) == g.game_date) and g.game_id != "espn_401658258")
        if conflict: reasons.append("NCAA vs ESPN score conflict")
        st.append("verified" if verified and not conflict else "provisional"); rs.append("; ".join(reasons) or "NCAA scoreboard only (single source, internally consistent)")
    df["audit_status"] = st; df["audit_basis"] = rs
    return df
CG = {}
for s, g in games.items():
    c = status_games(apply_games(g), s)
    nd = c.involves_non_d1_opponent.fillna(False).astype(bool) if "involves_non_d1_opponent" in c else pd.Series(False, index=c.index)
    if s == 2025:  # derive from alias table D-I membership via team stats flag
        nd1 = set(t[(t.season == 2025) & (t.involves_non_d1_opponent == True)].game_id); nd = c.game_id.isin(nd1)
    c["involves_non_d1_opponent_audit"] = nd
    c["usable_result"] = c.audit_status != "rejected"
    c["usable_d1_vs_d1"] = c.usable_result & ~nd
    CG[s] = c
    c.drop(columns=[x for x in ["_ds"] if x in c]).to_csv(f"{OUT}/{DSN[s]}_corrected.csv", index=False)
# team / player / crosswalk corrected copies
dmap = CORR[CORR.field == "game_date"].set_index("game_id").corrected_value.to_dict(); dst = CORR[CORR.field == "game_date"].set_index("game_id").status.to_dict()
gstat = pd.concat([CG[s][["game_id", "audit_status"]] for s in CG]).set_index("game_id").audit_status.to_dict()
for df, name in [(t, "ncaa_lacrosse_team_game_stats_2023_2025"), (p, "ncaa_lacrosse_player_stats_2023_2025")]:
    d = df.copy(); d.insert(d.columns.get_loc("game_date") + 1, "original_game_date", d.game_date)
    d["game_date"] = d.game_id.map(dmap).fillna(d.game_date); d["date_correction_status"] = d.game_id.map(dst).fillna("")
    if "start_time_utc" in d: d.loc[d.game_id == "6449835", "start_time_utc"] = "2025-04-12T16:00:00+00:00"
    d["game_audit_status"] = d.game_id.map(gstat).fillna("not_in_game_files")
    d.to_csv(f"{OUT}/{name}_corrected.csv", index=False)
c2 = cw.copy(); c2["original_ncaa_game_date"] = c2.ncaa_game_date; c2["ncaa_game_date"] = c2.ncaa_game_id.map(dmap).fillna(c2.ncaa_game_date)
c2["ncaa_game_audit_status"] = c2.ncaa_game_id.map(gstat).fillna("")
c2.to_csv(f"{OUT}/odds_game_to_ncaa_game_crosswalk_corrected.csv", index=False)
# --- excluded / unverified list ---
for _, d in dup.iterrows():
    X(f"game_id={d.game_id} ({d.home_team} {d.home_score:.0f}-{d.away_score:.0f} {d.away_team}, {d.game_date})", DSN[int(d.season)], "rejected",
      f"phantom duplicate of {d.suspected_duplicate_of}; {d.action}; no box score" + ("; Hampton official schedule shows one meeting (2025-03-15)" if d.game_id == "6444405" else
      "; official school schedule shows a single meeting on the kept game's date"), " | ".join(cmp_[cmp_.game_id == d.suspected_duplicate_of].evidence_file.unique()) or d.source_url)
for s, c in CG.items():
    for _, g in c[c.audit_status == "rejected"].iterrows():
        if g.game_id in set(dup.game_id): continue
        X(f"game_id={g.game_id}", DSN[s], "rejected", g.audit_basis, g.source_url)
    for _, g in c[c.corrections_applied.str.len() > 0].iterrows():
        X(f"game_id={g.game_id}", DSN[s], "provisional" if "provisional" in g.corrections_applied else "verified", "kept after correction: " + g.corrections_applied, " | ".join(CORR[CORR.game_id == g.game_id].evidence_file.unique()))
    for _, g in c[(c.audit_status == "provisional") & (c.audit_basis.str.contains("conflict|ESPN-only"))].iterrows():
        X(f"game_id={g.game_id}", DSN[s], "provisional", g.audit_basis, g.source_url)
    for _, g in c[c.involves_non_d1_opponent_audit & c.usable_result].iterrows():
        X(f"game_id={g.game_id} ({g.home_team} vs {g.away_team})", DSN[s], "provisional", "not a D-I vs D-I contest (Hartford was moving to D-III and NCAA box lists division 3 for its games; St. Andrews and Wabash are non-D-I); result real, exclude from D-I vs D-I models", g.source_url)
    n_only = c[(c.audit_status == "provisional") & (c.audit_basis.str.startswith("NCAA scoreboard only"))]
    X(f"{len(n_only)} games (see audit_status/audit_basis in {DSN[s]}_corrected.csv)", DSN[s], "provisional", "NCAA scoreboard only: no ESPN listing and no school page checked; internally consistent with box score", "")
for _, r in reval.iterrows(): X(r.record, r.dataset, r.status, r.reason, r.evidence)
X("game_id=6269867 player Pio (Jacksonville)", "ncaa_lacrosse_player_stats_2023_2025", "provisional", "player shots_on_goal 3 > shots 1 as published by NCAA box", "https://www.ncaa.com/game/6269867/boxscore")
for r in R["crosswalk_matched_with_date_shift"]:
    ok = r["ncaa_game_id"] in school_ok
    X(f"odds_game_id={r['odds_game_id']} -> ncaa {r['ncaa_game_id']}", "odds_game_to_ncaa_game_crosswalk", "provisional",
      f"odds date {r['odds_game_date']} vs NCAA {r['ncaa_game_date']}; " + ("official school schedule confirms NCAA date, so the odds-side date is a day early (for the odds worker)" if ok else "not checked against school page"),
      " | ".join(cmp_[cmp_.game_id == r["ncaa_game_id"]].evidence_file.unique()))
# NCAA vs ESPN calendar-date disagreements and how each was resolved
for s_, c in CG.items():
    c = c.merge(G[["game_id", "espn_date"]], on="game_id", how="left")
    for _, g in c[c.espn_date.notna() & (c.espn_date != c.original_game_date)].iterrows():
        sch = cmp_[(cmp_.game_id == g.game_id) & cmp_.school_date.notna()]
        res = (f"official school date {sch.school_date.iloc[0]} -> " + ("NCAA date correct, ESPN date wrong" if sch.school_date.iloc[0] == g.original_game_date else "NCAA date corrected")) if len(sch) else "no school page checked"
        X(f"game_id={g.game_id} ({g.home_team} vs {g.away_team})", DSN[s_], "verified" if len(sch) else "provisional", f"NCAA date {g.original_game_date} vs ESPN date {g.espn_date}: {res}", " | ".join(sch.evidence_file.unique()))
# genuine back-to-back appearances confirmed by school pages
for gid_pair, team, note in [(("6085513", "6085540"), "high-point", "High Point played Navy 02-25 and Hampton 02-26"), (("6085414", "6085425"), "navy", "Navy played Mount St. Mary's 02-04 and Queens 02-05"),
                             (("6269576", "6269597"), "mercer", "Mercer two games on consecutive days"), (("6386142", "6386144"), "iona", "Iona two games on consecutive days"),
                             (("6386158", "6454179"), "stony-brook", "Stony Brook 02-14 then Queens on 02-16 (after date correction)"), (("6386543", "6449835"), "umbc", "UMBC vs UMass Lowell 04-04; Binghamton game is 04-12 after correction")]:
    sch = cmp_[cmp_.game_id.isin(gid_pair) & (cmp_.team == team)]
    X(f"game_ids={'/'.join(gid_pair)}", "same_team_within_1_day", "verified" if len(sch) == 2 and sch.score_agrees.all() else "provisional",
      f"{note}; both games on official {team} schedule with same scores: genuine, not duplicates" if len(sch) == 2 else note, " | ".join(sch.evidence_file.unique()))
EX = pd.DataFrame(ex); EX.to_csv(f"{OUT}/games_stats_excluded_or_unverified.csv", index=False)
# --- counts ---
cnt = {}
for s, c in CG.items():
    tg = set(t[t.season == s].game_id)
    cnt[s] = dict(original_rows=len(games[s]), original_final=int((games[s].status == "final").sum()), rejected=int((c.audit_status == "rejected").sum()),
                  usable_games=int(c.usable_result.sum()), usable_d1_vs_d1=int(c.usable_d1_vs_d1.sum()), verified=int((c.audit_status == "verified").sum()),
                  provisional=int(((c.audit_status == "provisional") & c.usable_result).sum()), usable_with_box_stats=int((c.usable_result & c.game_id.isin(tg)).sum()),
                  date_corrections=int((c.game_date != c.original_game_date).sum()), verified_by_school_page=int((c.game_id.isin(school_ok) & c.usable_result).sum()),
                  verified_by_espn_score=int((c.game_id.isin(espn_ok) & c.usable_result).sum()))
json.dump(dict(counts=cnt, corrections=len(CORR), correction_rows=len(GDC), excluded_rows=len(EX), status_counts=EX.status.value_counts().to_dict()), open(f"{OUT}/final_usable_counts.json", "w"), indent=1)
print(CORR[["game_id", "field", "original_value", "corrected_value", "status"]].to_string()); print(pd.DataFrame(cnt).to_string()); print(EX.status.value_counts())
