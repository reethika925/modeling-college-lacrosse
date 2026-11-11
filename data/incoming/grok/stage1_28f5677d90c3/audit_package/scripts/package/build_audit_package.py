"""Assemble /workspace/audit_package from the two audit workstreams (sources are copied, never modified)."""
import os, shutil, json, hashlib, glob, re, datetime as dt, pandas as pd
W = "/workspace"; GA = f"{W}/audit/games"; OA = f"{W}/audit/odds"; FP = f"{W}/final_package"; PK = f"{W}/audit_package"
ORIG1470 = f"{W}/ncaa_lacrosse_historical_odds_2025.csv"; ORIG1470_SHA = "a156ba06389acc2a3a4e0eadaaf33af361b081cc942d3f768fdc79b1d5ed42a1"
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
assert sha(ORIG1470) == ORIG1470_SHA, "original 1,470-record CSV hash changed"
if os.path.exists(PK): shutil.rmtree(PK)
for d in ["corrected", "odds", "games", "evidence/games", "evidence/odds", "scripts/games", "scripts/odds", "scripts/package", "originals"]: os.makedirs(f"{PK}/{d}", exist_ok=True)
cp = lambda s, d: shutil.copy2(s, f"{PK}/{d}")
# ---------- folders ----------
for f in glob.glob(f"{GA}/*_corrected.csv"): cp(f, "corrected")
for f in ["odds_cleared_for_analysis.csv", "odds_quarantine_permission_required.csv", "odds_rejected.csv", "odds_game_usability.csv", "odds_record_corrections.csv", "odds_audit.md", "odds_audit_metrics.json"]: cp(f"{OA}/{f}", "odds")
for f in ["games_stats_audit.md", "final_usable_counts.json", "school_schedule_comparison.csv", "school_schedule_games_not_in_our_data.csv", "audit_candidates.csv", "revalidation_results.json", "revalidation_issues.csv", "post_correction_checks.json", "games_stats_excluded_or_unverified.csv", "game_date_corrections.csv"]:
    cp(f"{GA}/{f}", "games")
shutil.copytree(f"{GA}/evidence", f"{PK}/evidence/games", dirs_exist_ok=True)
shutil.copytree(f"{OA}/raw_terms", f"{PK}/evidence/odds/raw_terms")
for f in ["raw_terms_sha256.txt", "url_status_live.tsv", "source_urls.txt", "pre_sha256_deliverables_final_package.txt"]: cp(f"{OA}/{f}", "evidence/odds")
# raw odds page archives are third-party content under restricted/uncertain terms: hashed here, not redistributed
with open(f"{PK}/evidence/odds/raw_odds_evidence_sha256.txt", "w") as o:
    o.write("# sha256  path  (raw odds evidence kept at these /workspace paths; not copied into the package because the source terms restrict redistribution)\n")
    for d in ["wb", "an", "an_wb", "bol", "deliverables/raw_new"]:
        for f in sorted(glob.glob(f"{W}/{d}/**/*", recursive=True)):
            if os.path.isfile(f): o.write(f"{sha(f)}  {os.path.relpath(f, W)}\n")
for f in glob.glob(f"{GA}/scripts/*.py"): cp(f, "scripts/games")
for f in glob.glob(f"{OA}/scripts/*.py"): cp(f, "scripts/odds")
cp(os.path.abspath(__file__), "scripts/package")
cp(ORIG1470, "originals")
# ---------- 2. game_date_corrections.csv ----------
gdc = pd.read_csv(f"{GA}/game_date_corrections.csv", dtype=str)
gdc["evidence_file"] = gdc.evidence_file.fillna("").str.replace("evidence/", "evidence/games/", regex=False)
prov = pd.read_csv(f"{OA}/odds_provenance_audit.csv", dtype=str)
cmpg = pd.read_csv(f"{GA}/school_schedule_comparison.csv", dtype=str)
odds_rows = []
for og, gid in [("2023-02-04_hofstra_vs_merrimack", "6131581"), ("2023-02-04_holy-cross_vs_providence", "6085416"), ("2023-03-04_towson_vs_umbc", "6139977")]:
    recs = prov[prov.game_id == og].record_id.tolist(); sc = cmpg[cmpg.game_id == gid]
    assert len(sc) and (sc.date_agrees == "True").all(), og
    odds_rows.append(dict(record_key=f"odds_game_id={og} (records {', '.join(recs)})", dataset="odds", field="game_date (odds-source listed date)",
        original_value=og[:10], corrected_value=sc.our_date.iloc[0], source_url=" | ".join(sc.school_page.unique()) + f" | https://www.ncaa.com/game/{gid}",
        evidence_file=" | ".join(sc.evidence_file.str.replace("evidence/", "evidence/games/", regex=False).unique()),
        reason=f"Odds source lists the game on {og[:10]}; NCAA game {gid} is dated {sc.our_date.iloc[0]} and the official school schedule(s) list the same opponent and score on {sc.school_date.iloc[0]}. Odds source date is one day early. Documented only: the odds data and the original 1,470-record file are not changed.",
        status="verified"))
GDC = pd.concat([gdc, pd.DataFrame(odds_rows)], ignore_index=True); GDC.to_csv(f"{PK}/game_date_corrections.csv", index=False)
# ---------- 3. provenance + permissions ----------
cp(f"{OA}/odds_provenance_audit.csv", ".")
sp = pd.read_csv(f"{OA}/source_permissions_audit.csv", dtype=str)
hosts = sorted({re.match(r"(.+?)_(\d{4})_schedule", os.path.basename(f)).group(1) for f in glob.glob(f"{GA}/evidence/*_schedule.html")} - {"binghamton"} | {"binghamtonbearcats.com"})
now = "2026-11-10 (games audit fetches 11:55 AM-12:09 PM ET)"
add = [
 dict(source="NCAA GameCenter GraphQL (sdataprod.ncaa.com persisted queries: box score, team stats, play-by-play)", source_key="ncaa_sdataprod", url="https://sdataprod.ncaa.com/",
      tos_url="https://www.ncaa.com/tos", robots_url="https://sdataprod.ncaa.com/robots.txt (no robots file; returns a GraphQL error)", retrieved_at=now,
      clauses='Same NCAA.com ToS as the ncaa row. The saved ToS text has no clause banning robots, scraping or automated access; it bars reproducing/redistributing "NCAA Content" "except as otherwise expressly permitted under United States copyright law".',
      classification="uncertain", notes="Games worker's primary source for scores, box scores, team stats, player stats and faceoff/clear counts derived from play-by-play (1,718 games). The data are factual results. Internal academic analysis is plausible, but redistribution needs NCAA permission. The query hashes come from the MIT-licensed henrygd/ncaa-api. No authentication or bypass was involved.",
      evidence_files="evidence/odds/raw_terms/tos_ncaa.com.html; evidence/games/robots/robots_sdataprod.ncaa.com.txt; evidence/games/robots/robots_data.ncaa.com.txt"),
 dict(source="ESPN site API, games use (validation cross-check of 1,039 games; 1 ESPN-only game row)", source_key="espn_games_validation", url="https://site.api.espn.com/apis/site/v2/sports/lacrosse/mens-college-lacrosse/scoreboard",
      tos_url="https://disneytermsofuse.com/english/", robots_url="https://www.espn.com/robots.txt", retrieved_at="raw ESPN scoreboards collected earlier in the project (lax_data/raw/espn_scoreboards)",
      clauses="Disney ToU bans automated extraction for building a data set or database (see the espn row).", classification="restricted",
      notes="The games worker used ESPN for espn_event_id/espn_* columns, for score/date cross-checks, and for one ESPN-only row (espn_401658258 Princeton 18-11 Penn, 2024-05-05; the Princeton official schedule independently confirms it). Fields derived from ESPN are marked requires_permission. Game-level verification that rests on ESPN alone should be read as provisional until permission is obtained (see data_quality_audit.md).",
      evidence_files="evidence/odds/raw_terms/tos_disney.html"),
 dict(source=f"Official school athletics schedule pages used by the games audit ({len(hosts)} hosts, 28 school-season pages + 1 recap)", source_key="sidearm_games_audit", url="; ".join(f"https://{h}/sports/mens-lacrosse/schedule/" for h in hosts),
      tos_url="https://sidearmsports.com/terms-of-service", robots_url="per host /robots.txt (checked by script before each fetch; all allowed; Crawl-delay 30 honoured with 31 s per host)", retrieved_at=now,
      clauses='SIDEARM ToS: content "intended for your personal, noncommercial use"; "Copying or storing of any Content for other than personal use is expressly prohibited without prior written permission".', classification="uncertain",
      notes="Read-only schedule pages used as evidence for date/score checks. Saved copies are for verification inside this academic project only and must not be redistributed. No data rows come from these pages; they only confirm or correct NCAA facts.",
      evidence_files="evidence/games/fetch_log.tsv; evidence/games/*_schedule.html; evidence/odds/raw_terms/tos_sidearm.html"),
 dict(source="Harvard athletics (gocrimson.com) schedule page", source_key="gocrimson_blocked", url="https://gocrimson.com/sports/mens-lacrosse/schedule/2023", tos_url="https://sidearmsports.com/terms-of-service",
      robots_url="https://gocrimson.com/robots.txt", retrieved_at="2026-11-10 11:59 AM ET", clauses="The response was an Incapsula bot-protection challenge (HTTP 200 with a challenge iframe), not the schedule.",
      classification="blocked (security control) - not accessed", notes="Not circumvented and not used. Harvard games were checked through opponent pages (Vermont, Brown) instead.",
      evidence_files="evidence/games/gocrimson.com_2023_schedule.BLOCKED_incapsula.html; evidence/games/robots/robots_gocrimson.com.txt"),
 dict(source="stats.ncaa.org", source_key="stats_ncaa_org", url="https://stats.ncaa.org/", tos_url="https://www.ncaa.com/tos", robots_url="https://stats.ncaa.org/robots.txt (403 Access Denied)", retrieved_at=now,
      clauses="The edge returns 403 Access Denied even for robots.txt.", classification="blocked (security control) - not accessed", notes="Not circumvented. No data from this host.",
      evidence_files="evidence/games/robots/robots_stats.ncaa.org.txt"),
 dict(source="Massey Ratings (masseyratings.com)", source_key="massey", url="https://masseyratings.com/", tos_url="", robots_url="https://masseyratings.com/robots.txt", retrieved_at="earlier project phase",
      clauses="robots.txt disallows /data/ and /scores.php", classification="restricted (explicit robots disallow) - not used", notes="Considered and not used.", evidence_files=""),
]
SP = pd.concat([sp, pd.DataFrame(add)], ignore_index=True); SP.to_csv(f"{PK}/source_permissions_audit.csv", index=False)
# ---------- 4. excluded_or_unverified_records.csv ----------
URL = lambda e: f"https://{m.group(1)}/sports/mens-lacrosse/schedule/{m.group(2)}" if (m := re.match(r"evidence/(.+?)_(\d{4})_schedule.html", e)) else ""
ge = pd.read_csv(f"{GA}/games_stats_excluded_or_unverified.csv", dtype=str).fillna("")
rows = []
for _, r in ge.iterrows():
    parts = [x.strip() for x in r.evidence.split("|") if x.strip()]
    urls = [x for x in parts if x.startswith("http")] + [URL(x) for x in parts if URL(x)]
    files = [x.replace("evidence/", "evidence/games/", 1) for x in parts if not x.startswith("http")]
    st = r.status
    rows.append(dict(record_id=r.record, dataset=r.dataset, status=st, reason=r.reason, evidence="; ".join(files), source_url="; ".join(dict.fromkeys(urls))))
oe = pd.read_csv(f"{OA}/excluded_or_unverified_records.csv", dtype=str).fillna("")
for _, r in oe.iterrows():
    rows.append(dict(record_id=r.record_id, dataset=f"odds_{r.source_dataset}", status=r.status,
                     reason=f"technical_status={r.technical_status}; {r.reason}", evidence=r.evidence_file and f"/workspace/{r.evidence_file} (hash in evidence/odds/raw_odds_evidence_sha256.txt)",
                     source_url="; ".join(x for x in [r.source_url, r.archive_url] if x and x != "null")))
q = pd.read_csv(f"{OA}/odds_quarantine_permission_required.csv", dtype=str)
nq = int((q.technical_status == "verified").sum())
rows.append(dict(record_id=f"ODDS_QUARANTINE_TECHNICALLY_VERIFIED ({nq} records)", dataset="odds", status="requires_permission",
                 reason="technically verified odds records quarantined because no source permits collection and research reuse (Action Network/DraftKings restricted; BetMGM, Bet On Lacrosse, Lacrosse All Stars, LegalSportsBetting, Internet Archive uncertain). Listed one per row in odds/odds_quarantine_permission_required.csv",
                 evidence="odds/odds_quarantine_permission_required.csv; source_permissions_audit.csv", source_url=""))
EX = pd.DataFrame(rows, columns=["record_id", "dataset", "status", "reason", "evidence", "source_url"]); EX.to_csv(f"{PK}/excluded_or_unverified_records.csv", index=False)
# ---------- 5. validated_data_inventory.csv ----------
PERM_G = "uncertain: NCAA ToS has no automated-access ban but bars redistribution of NCAA Content except as US copyright law allows (results are facts); ESPN-derived columns restricted (Disney ToU)"
PERM_O = "requires permission: Action Network/DraftKings restricted; BetMGM, Bet On Lacrosse, Lacrosse All Stars, LegalSportsBetting and Internet Archive uncertain"
inv = []
def I(path, desc, n_orig, usable, ver, prov_, rp, rej, seasons, perm, cleared, in_pkg=True):
    full = f"{PK}/{path}" if in_pkg else path
    inv.append(dict(path=path, in_package=in_pkg, description=desc, rows_original=n_orig, rows_usable=usable, verified=ver, provisional=prov_, requires_permission=rp, rejected=rej,
                    seasons=seasons, sha256=sha(full), permission_status=perm, cleared_for_analysis=cleared))
ss = lambda s: "|".join(sorted({str(x) for x in s.dropna().unique()}))
for f, orig in [("ncaa_lacrosse_games_2023", "ncaa_lacrosse_games_2023.csv"), ("ncaa_lacrosse_games_2024", "ncaa_lacrosse_games_2024.csv"), ("ncaa_lacrosse_game_index_2025", "ncaa_lacrosse_game_index_2025.csv")]:
    d = pd.read_csv(f"{PK}/corrected/{f}_corrected.csv", dtype={"game_id": str}); o = pd.read_csv(f"{FP}/{orig}")
    vc = d.audit_status.value_counts()
    I(f"corrected/{f}_corrected.csv", f"{f}: corrected copy (dates/results fixed, audit_status, usable flags); original kept in final_package", len(o), int(d.usable_result.sum()),
      int(vc.get("verified", 0)), int(vc.get("provisional", 0)), int(d.usable_result.sum()), int(vc.get("rejected", 0)), ss(d.season), PERM_G, False)
    I(f"{FP}/{orig}", f"{orig}: ORIGINAL (unmodified, reference)", len(o), "", "", "", "", "", ss(o.season), PERM_G, False, in_pkg=False)
for f, col in [("ncaa_lacrosse_team_game_stats_2023_2025", "game_audit_status"), ("ncaa_lacrosse_player_stats_2023_2025", "game_audit_status")]:
    d = pd.read_csv(f"{PK}/corrected/{f}_corrected.csv", dtype={"game_id": str}, low_memory=False); vc = d[col].value_counts(); us = int((d[col] != "rejected").sum())
    I(f"corrected/{f}_corrected.csv", f"{f}: corrected copy (game dates fixed; game_audit_status per row)", len(d), us, int(vc.get("verified", 0)), int(vc.get("provisional", 0)), us, int(vc.get("rejected", 0)), ss(d.season), PERM_G, False)
    I(f"{FP}/{f}.csv", f"{f}.csv: ORIGINAL (unmodified, reference)", len(d), "", "", "", "", "", ss(d.season), PERM_G, False, in_pkg=False)
d = pd.read_csv(f"{PK}/corrected/odds_game_to_ncaa_game_crosswalk_corrected.csv", dtype=str); m = d.match_status == "matched"
I("corrected/odds_game_to_ncaa_game_crosswalk_corrected.csv", "odds game id -> NCAA game id crosswalk, corrected copy (verified = matched to a verified NCAA game)", len(d), int(m.sum()),
  int((m & (d.ncaa_game_audit_status == "verified")).sum()), int((~(m & (d.ncaa_game_audit_status == "verified"))).sum()), len(d), int((d.ncaa_game_audit_status == "rejected").sum()), ss(d.odds_season), PERM_O + "; " + PERM_G, False)
def oddsrow(path, desc, df, in_pkg=True, n_orig=None):
    I(path, desc, n_orig if n_orig is not None else len(df), int((df.status != "rejected").sum()), int((df.technical_status == "verified").sum()), int((df.technical_status == "provisional").sum()),
      int((df.status == "requires_permission").sum()), int((df.status == "rejected").sum()), ss(df.season), PERM_O, False, in_pkg)
oddsrow("odds_provenance_audit.csv", "all 1,995 odds records (1,470 original + 525 additional) with provenance, grades and status", prov)
oddsrow("odds/odds_quarantine_permission_required.csv", "odds records quarantined pending permission (technically verified or provisional)", q)
oddsrow("odds/odds_rejected.csv", "rejected odds records", pd.read_csv(f"{PK}/odds/odds_rejected.csv", dtype=str))
cl = pd.read_csv(f"{PK}/odds/odds_cleared_for_analysis.csv", dtype=str)
I("odds/odds_cleared_for_analysis.csv", "odds cleared for analysis (header only: nothing cleared)", 0, 0, 0, 0, 0, 0, "", "cleared set; empty until permission obtained", True)
gu = pd.read_csv(f"{PK}/odds/odds_game_usability.csv", dtype=str)
I("odds/odds_game_usability.csv", "per-game odds usability (two-sided ML, spreads, books, movement, timing)", len(gu), len(gu), "", "", int((gu.statuses == "requires_permission").sum()), 0, ss(gu.season), PERM_O, False)
po = prov[prov.source_dataset == "original"]
oddsrow("originals/ncaa_lacrosse_historical_odds_2025.csv", f"ORIGINAL 1,470-record odds file (unmodified copy; sha256 {ORIG1470_SHA}); counts from odds_provenance_audit source_dataset=original", po, n_orig=len(pd.read_csv(ORIG1470)))
pa = prov[prov.source_dataset == "additional"]
oddsrow(f"{W}/deliverables/ncaa_lacrosse_additional_odds_2023_2026.csv", "ORIGINAL additional odds file (unmodified, reference); counts from odds_provenance_audit source_dataset=additional", pa, in_pkg=False, n_orig=len(pd.read_csv(f"{W}/deliverables/ncaa_lacrosse_additional_odds_2023_2026.csv")))
INV = pd.DataFrame(inv); INV.to_csv(f"{PK}/validated_data_inventory.csv", index=False)
json.dump(dict(built=dt.datetime.now().isoformat(timespec="seconds"), excluded_status=EX.status.value_counts().to_dict(), corrections=len(GDC), permissions_rows=len(SP)), open(f"{PK}/games/_package_build_summary.json", "w"), indent=1)
print(INV[["path", "rows_original", "rows_usable", "verified", "provisional", "requires_permission", "rejected", "cleared_for_analysis"]].to_string()); print(EX.status.value_counts()); print(len(GDC), len(SP))
# ---------- 1/README/verify (hand-written docs kept beside this script) + MANIFEST ----------
DOCS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
for f in ["data_quality_audit.md", "README.md", "verify_audit.py"]: shutil.copy2(os.path.join(DOCS, f), PK); shutil.copy2(os.path.join(DOCS, f), f"{PK}/scripts/package/")
import csv
def _rows(p):
    with open(p, newline="", encoding="utf-8") as f: return sum(1 for _ in csv.reader(f)) - 1
files = sorted(os.path.relpath(os.path.join(d, f), PK) for d, _, fs in os.walk(PK) for f in fs if f != "MANIFEST.csv")
with open(f"{PK}/MANIFEST.csv", "w", newline="") as o:
    w = csv.writer(o); w.writerow(["path", "bytes", "rows", "sha256"])
    for f in files: w.writerow([f, os.path.getsize(f"{PK}/{f}"), _rows(f"{PK}/{f}") if f.endswith(".csv") else "", sha(f"{PK}/{f}")])
print("manifest files:", len(files))
