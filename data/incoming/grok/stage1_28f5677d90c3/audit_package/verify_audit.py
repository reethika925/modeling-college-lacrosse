#!/usr/bin/env python3
"""Re-check the audit package: MANIFEST hashes/row counts, inventory counts, vocabularies, cleared file, original 1,470 hash."""
import csv, hashlib, json, os, sys
import pandas as pd
os.chdir(os.path.dirname(os.path.abspath(__file__)))
ORIG = "a156ba06389acc2a3a4e0eadaaf33af361b081cc942d3f768fdc79b1d5ed42a1"; ok = 0; bad = []
def sha(p):
    h = hashlib.sha256(); f = open(p, "rb")
    for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
def rows(p):
    with open(p, newline="", encoding="utf-8") as f: return sum(1 for _ in csv.reader(f)) - 1
def check(cond, msg):
    global ok
    if cond: ok += 1
    else: bad.append(msg)
man = list(csv.DictReader(open("MANIFEST.csv")))
listed = {m["path"] for m in man}
for m in man:
    check(os.path.exists(m["path"]), f"missing {m['path']}")
    if not os.path.exists(m["path"]): continue
    check(sha(m["path"]) == m["sha256"], f"hash {m['path']}")
    if m["rows"] != "": check(rows(m["path"]) == int(m["rows"]), f"rows {m['path']}")
actual = {os.path.relpath(os.path.join(d, f)) for d, _, fs in os.walk(".") for f in fs} - {"MANIFEST.csv"}
check(actual == listed, f"unlisted/extra files: {sorted(actual ^ listed)[:5]}")
# original 1,470-record odds CSV
check(sha("originals/ncaa_lacrosse_historical_odds_2025.csv") == ORIG and rows("originals/ncaa_lacrosse_historical_odds_2025.csv") == 1470, "original 1,470 copy hash/rows")
if os.path.exists("/workspace/ncaa_lacrosse_historical_odds_2025.csv"): check(sha("/workspace/ncaa_lacrosse_historical_odds_2025.csv") == ORIG, "workspace original 1,470 hash")
# inventory counts re-derived
inv = pd.read_csv("validated_data_inventory.csv")
for _, r in inv[inv.in_package].iterrows():
    check(sha(r.path) == r.sha256, f"inventory hash {r.path}")
    d = pd.read_csv(r.path, dtype=str, low_memory=False)
    check(len(d) == r.rows_original or "originals/" in r.path or r.path.startswith("corrected/ncaa_lacrosse_game"), f"inventory rows {r.path}")
    if "audit_status" in d:
        vc = d.audit_status.value_counts(); check((int(vc.get("verified", 0)), int(vc.get("provisional", 0)), int(vc.get("rejected", 0))) == (r.verified, r.provisional, r.rejected), f"game status {r.path}")
    if "game_audit_status" in d:
        vc = d.game_audit_status.value_counts(); check((int(vc.get("verified", 0)), int(vc.get("provisional", 0)), int(vc.get("rejected", 0))) == (r.verified, r.provisional, r.rejected), f"stat status {r.path}")
    if "technical_status" in d and "originals/" not in r.path:
        check(int((d.technical_status == "verified").sum()) == r.verified and int((d.status == "rejected").sum()) == r.rejected and int((d.status == "requires_permission").sum()) == r.requires_permission, f"odds status {r.path}")
# odds totals and cleared file
p = pd.read_csv("odds_provenance_audit.csv", dtype=str); q = pd.read_csv("odds/odds_quarantine_permission_required.csv", dtype=str)
rj = pd.read_csv("odds/odds_rejected.csv", dtype=str); cl = pd.read_csv("odds/odds_cleared_for_analysis.csv", dtype=str)
check(len(p) == 1995 and len(q) + len(rj) == 1995 and len(cl) == 0 and list(cl.columns) == list(q.columns), "odds totals / cleared file")
check((p.source_dataset == "original").sum() == 1470, "1,470 original records present in provenance audit")
check(set(q.record_id) | set(rj.record_id) == set(p.record_id), "quarantine+rejected == all records")
# games usable counts match final_usable_counts.json
fc = json.load(open("games/final_usable_counts.json"))["counts"]
for s, f in [("2023", "ncaa_lacrosse_games_2023"), ("2024", "ncaa_lacrosse_games_2024"), ("2025", "ncaa_lacrosse_game_index_2025")]:
    d = pd.read_csv(f"corrected/{f}_corrected.csv", dtype=str)
    check(int((d.usable_result == "True").sum()) == fc[s]["usable_games"] and len(d) == fc[s]["original_rows"], f"usable count {s}")
# vocab and key corrections
V = {"verified", "provisional", "requires_permission", "rejected"}
gdc = pd.read_csv("game_date_corrections.csv", dtype=str); ex = pd.read_csv("excluded_or_unverified_records.csv", dtype=str)
check(set(gdc.status) <= V and set(ex.status) <= V, "status vocabulary")
check(list(ex.columns) == ["record_id", "dataset", "status", "reason", "evidence", "source_url"], "excluded schema")
check(((gdc.record_key == "game_id=6449835") & (gdc.field == "game_date") & (gdc.corrected_value == "2025-04-12")).any(), "Binghamton/UMBC correction present")
check((gdc.dataset == "odds").sum() == 3, "3 odds date rows")
g25 = pd.read_csv("corrected/ncaa_lacrosse_game_index_2025_corrected.csv", dtype=str).set_index("game_id")
check(g25.loc["6449835", "game_date"] == "2025-04-12" and g25.loc["6449835", "original_game_date"] == "2025-04-05" and g25.loc["6386469", "game_date"] == "2025-04-05", "Binghamton games in corrected index")
print(f"{ok} checks passed, {len(bad)} failed"); [print("FAIL:", b) for b in bad]
sys.exit(1 if bad else 0)
