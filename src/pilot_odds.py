"""Reproduce Task 3's sample and conservative historical-odds feasibility audit.

No authentication, paid calls, model odds, or restricted-source scraping.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
GAME_PATH = ROOT / "data/processed/lacrosse_games_2025.csv"
EXPECTED_GAME_SHA256 = "79b43ec0168d5466d29a0e3be2c7a9bb46096038aefc25a54f70b2e0b24393a3"
PROMINENT = {
    "cornell", "maryland", "notre-dame", "duke", "syracuse", "johns-hopkins",
    "virginia", "north-carolina", "princeton", "penn-st",
}
SAMPLE_COLUMNS = [
    "game_id", "season", "game_date", "game_datetime_utc", "home_team", "away_team",
    "home_team_slug", "away_team_slug", "home_score", "away_score", "sample_stratum",
]
# This pilot found no eligible source. A future adapter needs its own provenance audit.
VERIFIED_SOURCE_ADAPTERS = frozenset()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def select_sample(games, seed=519):
    """Five games per month, spanning dates and program groups; never use scores."""
    pool = games[games.season.eq(2025) & games.game_status.eq("final")].copy()
    pool["month"] = pool.game_date.str[:7]
    pool["prominent"] = pool.home_team_slug.isin(PROMINENT) | pool.away_team_slug.isin(PROMINENT)
    pool["tie_break"] = pool.game_id.map(lambda value: hashlib.sha256(f"{seed}:{value}".encode()).hexdigest())
    selected = []

    def take(group, positions, label):
        ordered = group.sort_values(["game_date", "tie_break"])
        if len(ordered) < len(positions):
            raise ValueError(f"Insufficient games for {label}")
        indices = [round(position * (len(ordered) - 1)) for position in positions]
        part = ordered.iloc[indices].copy()
        part["sample_stratum"] = label
        selected.append(part)

    for month in ("2025-02", "2025-03", "2025-04"):
        month_pool = pool[pool.month.eq(month)]
        take(month_pool[month_pool.prominent], [0.25, 0.75], "prominent_program")
        take(month_pool[~month_pool.prominent], [0, 0.5, 1], "other_programs")
    # Purposive championship-weekend anchors test the most visible postseason games.
    may = pool[pool.month.eq("2025-05")]
    anchors = may[may.game_date.isin(["2025-05-24", "2025-05-26"])]
    if len(anchors) != 3:
        raise ValueError("Expected the two genuine semifinals and one championship game")
    anchors = anchors.copy()
    anchors["sample_stratum"] = "championship_weekend_anchor"
    selected.append(anchors)
    take(may[~may.prominent], [0, 1], "other_programs")
    sample = pd.concat(selected).sort_values(["game_date", "game_id"])[SAMPLE_COLUMNS].reset_index(drop=True)
    if len(sample) != 20 or sample.game_id.nunique() != 20:
        raise ValueError("Sample must contain exactly 20 distinct genuine game IDs")
    return sample


def match_reference(reference, games, aliases):
    """Exact reviewed aliases and date only; ambiguous identities are never accepted."""
    if reference.get("competition") != "NCAA Division I" or reference.get("gender") != "men" or reference.get("sport") != "lacrosse":
        return None, "wrong_or_unverified_competition"
    first = aliases.get(reference.get("source_team_1"))
    second = aliases.get(reference.get("source_team_2"))
    if not first or not second or first == second:
        return None, "unknown_or_ambiguous_team_alias"
    candidates = games[games.game_date.eq(reference["game_date"]) & (
        (games.home_team_slug.eq(first) & games.away_team_slug.eq(second)) |
        (games.home_team_slug.eq(second) & games.away_team_slug.eq(first)))]
    if len(candidates) != 1:
        return None, "no_unique_team_date_match"
    row = candidates.iloc[0]
    # References list teams without home/away labels, so no orientation is invented.
    return str(row.game_id), "identity_only_odds_not_accepted"


def pregame_check(record):
    """Require actual source evidence, aware timestamps and pre-start provenance."""
    if record.get("provenance_kind") != "actual_historical_response":
        return False, "not_an_actual_historical_response"
    if record.get("collection_permitted") is not True:
        return False, "collection_permission_not_established"
    if record.get("sport") != "lacrosse" or record.get("gender") != "men" or record.get("competition") != "NCAA Division I":
        return False, "wrong_or_unverified_competition"
    if not record.get("bookmaker") or not record.get("source_url"):
        return False, "missing_bookmaker_or_provenance"
    try:
        price_time = datetime.fromisoformat(record["odds_timestamp"].replace("Z", "+00:00"))
        start = datetime.fromisoformat(record["game_start_time"].replace("Z", "+00:00"))
        if price_time.utcoffset() is None or start.utcoffset() is None:
            return False, "timestamp_timezone_unknown"
        if price_time >= start:
            return False, "not_before_start"
        modified = record.get("page_modified_timestamp")
        if modified and datetime.fromisoformat(modified.replace("Z", "+00:00")) >= start:
            return False, "page_modified_after_start_without_archived_quote"
    except (KeyError, ValueError, TypeError):
        return False, "missing_or_invalid_timestamps"
    return True, "verified_pregame"


def export_verified(records, output_path):
    """Never create the odds CSV for an empty pilot or rejected evidence."""
    accepted = []
    rejected = []
    for record in records:
        okay, reason = pregame_check(record)
        if okay and record.get("match_status") == "confirmed" and record.get("source_name") in VERIFIED_SOURCE_ADAPTERS:
            accepted.append(record)
        else:
            fallback = "unconfirmed_match" if record.get("match_status") != "confirmed" else "no_verified_source_adapter"
            rejected.append({"source_url": record.get("source_url"), "reason": reason if not okay else fallback})
    if accepted:
        pd.DataFrame(accepted).to_csv(output_path, index=False)
    elif output_path.exists():
        raise ValueError("Existing odds CSV preserved; no new verified records to replace it")
    return accepted, rejected


def write_report(sample, sources, audit, summary):
    lines = [
        "# Historical NCAA Division I men's lacrosse odds feasibility", "",
        f"Research date (America/New_York): {summary['research_timestamp']}", "",
        "**Overall feasibility: NOT CONFIRMED for a free, reproducible 2025 historical pre-game odds dataset.** "
        "The paid-provider capability is advertised, but no paid archive was queried and no free quote met all admission rules.",
        "", "## Pilot results", "", "| Measure | Games | Coverage of 20 |", "| --- | ---: | ---: |",
        "| Sampled | 20 | 100% |", "| Verified historical pre-game odds | 0 | 0% |",
        "| Moneylines | 0 | 0% |", "| Spreads | 0 | 0% |", "| Totals | 0 | 0% |",
        "| At least two sportsbooks for the same game | 0 | 0% |",
        "| Multiple pre-game odds timestamps for the same game | 0 | 0% |", "",
        "Accepted odds records: **0**. Unique matched odds games: **0**. Collected sportsbooks: **0**. "
        "Three news-article game references have exact team/date identity matches but were excluded because "
        "the present pages were modified after kickoff and the quote's pre-game availability cannot be verified. "
        "These are three excluded candidate event references, not three accepted odds records. "
        "No invented or header-only `data/processed/lacrosse_odds_2025_pilot.csv` was created.",
        "", "## Sample design and preservation", "",
        "The input has 580 completed games and 77 teams. Its SHA-256 is " + f"`{summary['input_sha256']}`. "
        "The collector opens it read-only and checks its checksum before and after execution. Task 2's date gaps remain "
        "a limitation of this sampling frame; this investigation does not establish whole-season completeness.",
        "", "Five genuine games were chosen per month, February–May 2025. In February, March and April, two involve "
        "a declared prominent-program group and three involve other programs. Dates are spread using fixed positions "
        "in date-sorted strata, with SHA-256 of seed 519 and game ID as the tie-break. May deliberately includes both "
        "semifinals, the final, and two other-program games. The prominent group is a sampling convenience, not "
        "a ranking. Scores are copied after selection and never used to select games or derive odds.",
        "", "This is a purposive, small feasibility pilot, not a representative random sample. Championship-weekend "
        "inclusion favors games likely to receive coverage. Its percentages cannot be extrapolated to all 580 games.",
        "", "## Sources investigated", "",
        "| Source | Historical odds available? | Free? | Games matched | Markets available | Limitations |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    for source in sources:
        lines.append(f"| [{source['name']}]({source['urls'][0]}) | {source['historical_access']} | {source['free_access']} | 0 | {source['markets']} | {source['limitation']} |")
    for source in sources:
        lines += ["", f"### {source['name']}", ""]
        for key, title in [("urls", "Exact URLs"), ("access_observed", "Access observed"),
                           ("bulk_download", "Bulk download"), ("bookmakers", "Bookmakers"),
                           ("coverage", "Dates/games covered"), ("timestamps", "Historical timestamps"),
                           ("license_restrictions", "License/access restrictions"), ("reproducibility", "Academic reproducibility")]:
            value = source[key]
            if isinstance(value, list):
                value = "; ".join(value)
            lines.append(f"- {title}: {value}")
    lines += [
        "", "## Matching and admission rules", "",
        "Reviewed, exact aliases for Cornell, Maryland, Penn State/Penn St. and Syracuse are recorded in "
        "`reports/odds_2025_team_aliases.csv`. News article team lists are not home/away designations. "
        "The candidate audit records source names and IDs as supplied (event IDs remain null), candidate NCAA IDs, "
        "and the explicit exclusion reason. No uncertain association enters a real odds dataset.",
        "", "A collectible record must identify men's Division I lacrosse, the source/bookmaker/market, genuine "
        "prices or quoted lines, and enough evidence to show the quote predates kickoff. A retrieval time in 2026 "
        "is not an odds time in 2025. An article's original publication time does not prove an odds block was present "
        "then if that page was later modified. Documentation examples, model prices, season futures, and other "
        "sports or leagues are excluded. Missing fields stay null; no price or timestamp is inferred.",
        "", "## Acquisition recommendation", "",
        "The free route is **not confirmed**, rather than proven impossible. The clearest permitted next step is "
        "a university-held licensed archive or a provider-authorized academic export from The Odds API or Cradl. "
        "Permission or an existing suitable subscription would be needed; none was requested or purchased. "
        "Before arranging access, have the archive owner demonstrate these 20 game IDs/team pairs, actual 2025 "
        "coverage, at least two books per event, both sides of the markets, pre-kickoff snapshot times and permitted "
        "research/redistribution rights. Resolve The Odds API's conflicting advertised start dates first.",
        "", "For the professor's questions, spreads must retain their team orientation and prices. A bookmaker "
        "margin requires both outcomes of the same market/line/book at a comparable timestamp; do not calculate "
        "it from a spread number alone or combine prices from different books. Line movement needs two or more "
        "verified pre-game snapshots of the same event, book and market. This pilot supplies neither comparison.",
        "", "If no authorized 2025 archive can be obtained, document that limitation to the professor and seek "
        "approval for a future prospective collection or a revised research scope. Prospective collection would "
        "not reconstruct 2025 prices. No future season is collected in Task 3.",
        "", "## Reproduce and audit", "", "```bash", "conda activate dsf-lacrosse",
        "python src/pilot_odds.py", "python -m pytest -q", "python -m pip check", "```", "",
        "The script performs no network requests. It reproduces the sample, audited candidate identities, "
        "coverage counts and this report from the saved research register. Website findings are a dated research "
        "snapshot, not a claim that access conditions never change. Exact searches and inspected repository commits "
        "are recorded separately. Research response files are evidence, not a collected odds database. "
        "Cradl scraping was stopped after reading its terms; its API is also disallowed by robots.txt.",
        "", "## The 20 actual sampled games", "",
        "| NCAA game ID | Date | Home | Away | Final home–away | Stratum |", "| --- | --- | --- | --- | --- | --- |",
    ]
    lines += [f"| {r.game_id} | {r.game_date} | {r.home_team} | {r.away_team} | {r.home_score}–{r.away_score} | {r.sample_stratum} |" for r in sample.itertuples()]
    (ROOT / "reports/historical_odds_feasibility.md").write_text("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    before = sha256(GAME_PATH)
    if before != EXPECTED_GAME_SHA256:
        raise ValueError("Validated input game CSV changed; review the sampling frame before rerunning")
    games = pd.read_csv(GAME_PATH, dtype={"game_id": str})
    sample = select_sample(games)
    sample_path = ROOT / "data/processed/lacrosse_odds_2025_sample_games.csv"
    sample.to_csv(sample_path, index=False)
    aliases_frame = pd.read_csv(ROOT / "reports/odds_2025_team_aliases.csv")
    aliases = dict(zip(aliases_frame.source_team_name, aliases_frame.ncaa_team_slug))
    references = json.loads((ROOT / "reports/odds_2025_candidate_references.json").read_text())
    audit = []
    for reference in references:
        game_id, identity = match_reference(reference, games, aliases)
        audit.append({**reference, "candidate_ncaa_game_id": game_id,
                      "identity_match_status": identity, "accepted_odds": False})
    pd.DataFrame(audit).to_csv(ROOT / "reports/odds_2025_candidate_audit.csv", index=False)
    candidate_ids = {r["candidate_ncaa_game_id"] for r in audit if r["candidate_ncaa_game_id"]}
    coverage = sample.copy()
    coverage["verified_odds_records"] = 0
    coverage["verified_bookmakers"] = 0
    coverage["exclusion_reason"] = coverage.game_id.map(lambda value:
        "candidate_reference_excluded_postgame_page_modification" if value in candidate_ids
        else "no_eligible_free_historical_quote_obtained")
    coverage.to_csv(ROOT / "reports/odds_2025_sample_coverage.csv", index=False)
    # No investigated source supplied an admissible free raw historical quote.
    accepted, rejected = export_verified([], ROOT / "data/processed/lacrosse_odds_2025_pilot.csv")
    assert not accepted and not rejected
    sources = json.loads((ROOT / "reports/historical_odds_sources.json").read_text())["sources"]
    summary = {
        "research_timestamp": datetime.now(ZoneInfo("America/New_York")).isoformat(timespec="seconds"),
        "input_sha256": before, "sample_sha256": sha256(sample_path), "sample_seed": 519,
        "sampled_games": len(sample), "sample_games_by_month": sample.game_date.str[:7].value_counts().sort_index().to_dict(),
        "source_candidates_investigated": len(sources), "accepted_odds_records": 0, "unique_games_matched": 0,
        "sources_successfully_read_for_research": len(sources), "historical_archives_queried": 0,
        "sportsbooks_collected": 0, "moneyline_games": 0, "spread_games": 0, "totals_games": 0,
        "multiple_book_games": 0, "multiple_pregame_timestamp_games": 0,
        "verified_sample_coverage_pct": 0.0, "excluded_candidate_event_references": len(audit),
        "coverage_percentages": {key: 0.0 for key in ("historical_odds", "moneyline", "spreads", "totals", "two_sportsbooks", "multiple_pregame_timestamps")},
        "uncertain_candidate_event_references": sum(bool(r["candidate_ncaa_game_id"]) for r in audit),
        "odds_csv_created": False, "feasibility": "NOT CONFIRMED",
    }
    write_report(sample, sources, audit, summary)
    (ROOT / "reports/odds_2025_pilot_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    if sha256(GAME_PATH) != before:
        raise ValueError("Game CSV changed during pilot execution")
    print(json.dumps(summary, indent=2))
    print("\nThe 20 real sampled games:\n" + sample.to_string(index=False))
    print("\nNo verified odds: pilot odds CSV was not created. See reports/historical_odds_feasibility.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
