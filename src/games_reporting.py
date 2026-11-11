"""Write the game's coverage audit without overwriting the Task 1 inventory."""

import json
from collections import Counter
from datetime import date


def write_reports(root, summary, frame, coverage, args):
    missing_dates = summary["failed_or_unchecked_dates"]
    summary["http_failure_counts"] = dict(Counter(str(r["http_status"]) for r in coverage if r["result"] == "failed"))
    full_window = args.start_date == date(args.season, 1, 1) and args.end_date == date(args.season, 6, 30)
    summary["window_coverage_verified"] = not missing_dates
    summary["season_completeness"] = "VERIFIED_WINDOW" if not missing_dates and full_window else "NOT_VERIFIED"
    summary["overtime_games"] = int(frame.overtime.fillna(False).sum())
    summary["total_missing_cells"] = sum(summary["missing_values"].values())
    (root / f"reports/games_{args.season}_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    champ = summary["independent_championship_validation"]
    lines = [
        f"# {args.season} NCAA DI men's lacrosse game results validation", "",
        f"- Report generated (America/New_York): {summary['retrieved_at']}",
        f"- Source: {summary['source_name']}",
        "- Official scoreboard: https://www.ncaa.com/scoreboard/lacrosse-men/d1",
        "- Exact daily URL pattern: `https://data.ncaa.com/casablanca/scoreboard/lacrosse-men/d1/YYYY/MM/DD/scoreboard.json`",
        f"- Window: {args.start_date} through {args.end_date}, inclusive",
        f"- Output: `{summary['output_path']}`", f"- SHA-256: `{summary['sha256']}`",
        f"- Collection status: {'INCOMPLETE — unverified dates remain' if missing_dates else 'SUCCESS — requested window verified'}",
        f"- Season completeness: {summary['season_completeness']}", "",
        "## Source choice and parsing", "",
        "Sources were investigated in the requested order. Ordinary Python requests retrieved the NCAA HTML "
        "scoreboard with HTTP 200; the browsing tool encountered a JavaScript challenge. NCAA daily Casablanca JSON "
        "was selected because actual responses contained regular-season games and the championship, explicit "
        "home/away objects, source game IDs, scores, dates and winner flags. ESPN's robots.txt returned HTTP 403, "
        "so its candidate scoreboard URLs were not requested. No access restrictions were bypassed.", "",
        "`reports/games_source_probes.json` records status, content type, event count and actual schema samples. "
        "Original probe bodies are cached in `data/raw/games/2025/probes/`. March 15 returned 32 games, "
        "May 26 returned one, and January 1 returned HTTP 404 with an XML error.", "",
        "The parser reads `games[].game`, preserves `gameID` as a string, and uses the explicit `home` and `away` "
        "objects. It parses `startDate` and nonempty integer score strings. Source winner flags are retained and "
        "checked against scores independently. The `lacrosse-men/d1` URL selects gender and division; individual "
        "game objects do not repeat division labels. No other sport or division was queried.", "",
        "## Results", "", "| Check | Result |", "| --- | ---: |",
    ]
    checks = {
        "Raw game records": summary["raw_game_records"],
        "Raw duplicate game IDs (extra rows)": summary["raw_duplicate_game_ids"],
        "Evidence-backed duplicate records removed": summary["resolved_duplicate_records"],
        "Processed games": summary["total_games"], "Columns": summary["column_count"], "Completed games": summary["completed_games"],
        "Completed games with valid scores": summary["completed_valid_scores"],
        "Unique teams (source SEO slugs)": summary["unique_teams"],
        "Remaining duplicate game IDs": summary["duplicate_game_ids"],
        "Duplicate unordered matchups on same date": summary["duplicate_matchups_same_date"],
        "Games with negative scores": summary["negative_scores"],
        "Games with invalid score formats": summary["invalid_score_formats"],
        "Completed games missing scores": summary["completed_missing_scores"],
        "Completed tied games": summary["completed_ties"],
        "Winner disagreements": summary["winner_disagreements"],
        "Completed games missing winner": summary["completed_missing_winner"],
        "Overtime games": summary["overtime_games"],
        "Dates requested": summary["requested_dates"], "Dates with verified JSON": summary["checked_successfully"],
        "Failed or unchecked dates": len(missing_dates),
    }
    lines += [f"| {key} | {value} |" for key, value in checks.items()]
    lines += ["", f"Actual game dates: {summary['first_game_date']} through {summary['last_game_date']}.",
              f"Statuses: `{summary['status_counts']}`.", "", "### Games by month", "",
              "| Month | Games |", "| --- | ---: |"]
    lines += [f"| {month} | {count} |" for month, count in summary["games_by_month"].items()]
    lines += ["", "### Missing values", "", f"Total missing cells: {summary['total_missing_cells']}.", "",
              "| Column | Missing cells |", "| --- | ---: |"]
    lines += [f"| `{column}` | {count} |" for column, count in summary["missing_values"].items()]
    lines += [
        "", "## Duplicate investigation", "",
        "The NCAA lists game ID `6311207` (Le Moyne–Lafayette, 4–15) on both February 22 and February 23, "
        "with the same game detail URL. Lafayette's official final recap confirms February 22. "
        "`reports/games_2025_duplicate_resolutions.json` records that evidence and selects the existing February 22 "
        "record. Both raw responses remain unchanged; both duplicate rows are exported to "
        "`reports/games_2025_duplicate_records.csv`. No scores, dates, IDs or venues are edited or invented. "
        "Other unresolved duplicate IDs would remain visible and fail validation.", "",
        "Evidence: https://goleopards.com/news/2025/2/22/mens-lacrosse-mens-lacrosse-dominates-le-moyne-on-the-road.aspx",
        "", "## Independent championship validation", "", f"Result: **{champ['result']}**.",
        f"Source: {champ['source_url']}",
        f"NCAA history record: {champ.get('ncaa_history_record', champ.get('error', 'Unavailable'))}",
        f"Evidence retrieved: {champ.get('retrieved_at', 'Unavailable')}; HTTP {champ.get('http_status', 'Unavailable')}.",
        "The dataset must contain exactly one final Cornell–Maryland game on May 26, 2025, with Cornell 13, "
        "Maryland 10 and Cornell as winner. This comparison never inserts or corrects a game.",
        "", "## Coverage and failures", "",
        f"Latest failed HTTP statuses by date: `{summary['http_failure_counts']}`.",
        "HTTP 404 means no daily JSON object was available. It is not counted as a verified empty day. Only a "
        "schema-valid HTTP 200 JSON response with `games: []` establishes an empty day. Every requested date has "
        "a row in `reports/games_collection_log.csv`; resumed attempts append new rows. Original successful "
        "retrieval timestamps, HTTP status and SHA-256 values are retained in the raw metadata files. "
        "This report uses the latest state for each requested date, not the count of all historical log rows.",
        "", "Failed or unchecked dates:", "", ", ".join(missing_dates) if missing_dates else "None.",
        "", "## Limitations and permitted alternatives", "",
        "- Date coverage gaps prevent a whole-season completeness claim. Genuine games from successful dates "
        "are saved, including postseason. Failed dates cannot be proved empty by this endpoint.",
        "- Numeric team IDs, venue and neutral-site flags are absent from the verified JSON schema and remain "
        "missing. Verified SEO slugs and short codes are separate fields. Source home/away labels at neutral sites "
        "are retained without assuming the first team is home.",
        "- Regular-season TBA start times have placeholder epochs. UTC timestamps stay missing for TBA games; "
        "the raw epoch is retained separately. No actual start time is inferred.",
        "- Postseason=True requires bracket metadata. Missing bracket fields leave postseason unknown; they do "
        "not establish a regular-season game. Conference-tournament classification is incomplete.",
        "- Cancellation and postponement records are retained if supplied, with missing scores preserved. "
        "The source may omit such contests. Overtime is read from the source's finalMessage/currentPeriod.",
        "- For unresolved dates, consult the official historical scoreboard in a normal browser or public 2025 "
        "team schedules. Save any permitted manual export separately with its URL, date and provenance. "
        "Do not insert inferred games, bypass a challenge, or save an HTML error as JSON.",
        "", "## Reproduce", "", "```bash", "conda activate dsf-lacrosse",
        f"python src/collect_games.py --season {args.season} --probe-only",
        f"python src/collect_games.py --season {args.season} --start-date {args.start_date} --end-date {args.end_date} --resume",
        f"python src/collect_games.py --season {args.season} --start-date {args.start_date} --end-date {args.end_date} --offline",
        "python -m pytest -q", "```", "",
        "Exit code 2 means coverage is incomplete or a required data check failed. The partial CSV and reports "
        "are still saved. Offline mode validates cache and previous failure logs without making requests.",
        "", "## First ten actual rows", "", "```csv", frame.head(10).to_csv(index=False).strip(), "```", "",
    ]
    (root / f"reports/games_{args.season}_validation.md").write_text("\n".join(lines))
    inventory_path = root / "reports/data_inventory.md"
    inventory = inventory_path.read_text() if inventory_path.exists() else "# Data inventory\n"
    marker, end_marker = "<!-- games-collection:start -->", "<!-- games-collection:end -->"
    section = "\n".join([
        marker, f"## Task 2 — {args.season} game-by-game results", "",
        f"- Dataset: {summary['source_name']}",
        "- Source webpage: https://www.ncaa.com/scoreboard/lacrosse-men/d1",
        "- Exact download URLs: `source_url` in each CSV row and the collection log; daily URL pattern in validation report.",
        f"- Inventory updated: {summary['retrieved_at']}; original per-response retrieval dates are in the raw metadata and collection log.",
        f"- Local file: `{summary['output_path']}`",
        f"- Status: {'INCOMPLETE' if missing_dates else 'SUCCESS'}; season completeness: {summary['season_completeness']}",
        f"- Rows: {len(frame)}; columns: {len(frame.columns)}; completed: {summary['completed_games']}; unique teams: {summary['unique_teams']}",
        f"- Verified dates: {summary['checked_successfully']}/{summary['requested_dates']}; failed or unchecked: {len(missing_dates)}; HTTP failures: {summary['http_failure_counts']}",
        f"- Missing cells: {summary['total_missing_cells']}; full column names and by-column counts in `reports/games_{args.season}_validation.md`.",
        f"- Duplicate IDs: {summary['duplicate_game_ids']} after {summary['resolved_duplicate_records']} documented duplicate removal; raw duplicate IDs: {summary['raw_duplicate_game_ids']}",
        f"- SHA-256: `{summary['sha256']}`",
        f"- Independent NCAA championship validation: {champ['result']}; {champ['source_url']}",
        "- Parsing: explicit home/away objects, source game IDs and integer scores; raw source bytes unchanged.",
        "- Limitations: failed dates unverified; numeric team IDs, venues and neutral flags absent; TBA times unknown; postseason metadata incomplete.",
        "- Game-level records are distinct from Task 1 team-season aggregates. No additional seasons, boxscores, odds or models collected.",
        end_marker,
    ])
    if marker in inventory and end_marker in inventory:
        start = inventory.index(marker)
        end = inventory.index(end_marker, start) + len(end_marker)
        inventory = inventory[:start] + section + inventory[end:]
    else:
        inventory = inventory.rstrip() + "\n\n" + section + "\n"
    inventory_path.write_text(inventory)
