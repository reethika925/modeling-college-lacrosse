"""Permission-blocked editorial pilot: generate a worksheet and audit manual entries.

USA Lacrosse prohibits automated collection. This module makes no network
requests, fetches no articles/archives, and includes no permission override.
Only explicitly confirmed, authorized manual entries can enter the A/B dataset.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
GAMES = ROOT / "data/processed/lacrosse_games_2025.csv"
GAME_HASH = "79b43ec0168d5466d29a0e3be2c7a9bb46096038aefc25a54f70b2e0b24393a3"
ARTICLE_URLS = [
    "https://www.usalacrosse.com/magazine/college/men/ncaa-mens-lacrosse-week-1-schedule-betting-odds-bluebloods",
    "https://www.usalacrosse.com/magazine/college/men/essential-ncaa-mens-lacrosse-quarterfinal-preview",
]
FIELDS = [
    "entry_status", "source_url", "game_date", "source_team_1", "source_team_2",
    "source_home_team", "source_away_team", "sport", "competition", "gender", "competition_verified",
    "bookmaker", "market", "selection", "odds_format", "moneyline_odds", "point_spread", "spread_price",
    "total_goals_line", "total_price", "article_publication_date", "article_modification_date",
    "odds_timestamp", "odds_timestamp_verified", "archive_url", "archive_timestamp", "archived_quote_verified",
    "quote_explicitly_published", "collection_permission_confirmed", "permission_basis", "review_notes",
]
OUTPUT_FIELDS = FIELDS + [
    "ncaa_game_id", "season", "game_datetime_utc", "home_team", "away_team",
    "source_orientation_status", "verification_status", "verification_reason",
]


def checksum(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def flag(value):
    return str(value).strip().casefold() in {"true", "yes", "1"}


def normalize(value):
    return " ".join(str(value or "").split()).casefold()


def ensure_worksheet(path):
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for url in ARTICLE_URLS:
            writer.writerow({"entry_status": "template", "source_url": url})


def load_aliases(games, path):
    if not path.exists():
        pairs = pd.concat([
            games[["home_team", "home_team_slug"]].rename(columns={"home_team": "source_alias", "home_team_slug": "ncaa_team_slug"}),
            games[["away_team", "away_team_slug"]].rename(columns={"away_team": "source_alias", "away_team_slug": "ncaa_team_slug"}),
        ]).drop_duplicates()
        pairs["review_basis"] = "Exact name in the validated NCAA results; no inferred nickname"
        # Reuse previously reviewed aliases; never modify the original alias file.
        reviewed = pd.read_csv(ROOT / "reports/odds_2025_team_aliases.csv")
        reviewed = reviewed.rename(columns={"source_team_name": "source_alias", "review_basis": "review_basis"})
        pairs = pd.concat([pairs, reviewed[["source_alias", "ncaa_team_slug", "review_basis"]]]).drop_duplicates("source_alias")
        pairs.sort_values("source_alias").to_csv(path, index=False)
    pairs = pd.read_csv(path, keep_default_na=False)
    aliases = {}
    valid_slugs = set(games.home_team_slug) | set(games.away_team_slug)
    for row in pairs.itertuples():
        key = normalize(row.source_alias)
        if not key or row.ncaa_team_slug not in valid_slugs or not row.review_basis:
            raise ValueError("Alias lacks a valid NCAA identity or review basis")
        if key in aliases and aliases[key] != row.ncaa_team_slug:
            raise ValueError(f"Ambiguous reviewed alias: {row.source_alias}")
        aliases[key] = row.ncaa_team_slug
    return aliases


def match_game(record, games, aliases):
    if not flag(record.get("competition_verified")) or (
        normalize(record.get("sport")), normalize(record.get("competition")), normalize(record.get("gender"))
    ) != ("lacrosse", "ncaa division i", "men"):
        return None, "competition_not_verified"
    first, second = [aliases.get(normalize(record.get(key))) for key in ("source_team_1", "source_team_2")]
    if not first or not second or first == second:
        return None, "unknown_or_ambiguous_alias"
    candidates = games[games.game_date.eq(record.get("game_date")) & (
        (games.home_team_slug.eq(first) & games.away_team_slug.eq(second)) |
        (games.home_team_slug.eq(second) & games.away_team_slug.eq(first)))]
    if len(candidates) != 1:
        return None, "no_unique_date_and_team_match"
    row = candidates.iloc[0]
    stated_home, stated_away = record.get("source_home_team"), record.get("source_away_team")
    if stated_home or stated_away:
        if (aliases.get(normalize(stated_home)), aliases.get(normalize(stated_away))) != (row.home_team_slug, row.away_team_slug):
            return None, "explicit_home_away_conflict_or_incomplete_orientation"
        orientation = "explicit_home_away_agrees"
    else:
        orientation = "not_stated_matchup_order_not_used_as_home_away"
    return row, orientation


def aware_timestamp(value):
    if not value:
        return None
    try:
        stamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return stamp if stamp.utcoffset() is not None else None
    except (ValueError, TypeError):
        return None


def before_game(value, game_date, kickoff):
    stamp = aware_timestamp(value)
    start = aware_timestamp(kickoff)
    if stamp and start:
        return stamp < start
    # Date-only evidence is sufficient only on an earlier calendar day (grade B).
    try:
        local_day = stamp.astimezone(ZoneInfo("America/New_York")).date() if stamp else date.fromisoformat(str(value)[:10])
        return local_day < date.fromisoformat(game_date)
    except (ValueError, TypeError):
        return False


def grade_quote(record, game_date, kickoff):
    """Grade supplied evidence; never generate an odds timestamp from publication."""
    if record.get("odds_timestamp"):
        if not aware_timestamp(record["odds_timestamp"]) or not before_game(record["odds_timestamp"], game_date, kickoff):
            return "C", "odds_timestamp_missing_timezone_invalid_or_not_pregame"
        if flag(record.get("odds_timestamp_verified")):
            return "A", "explicit_odds_timestamp_manually_verified_before_game"
    if flag(record.get("archived_quote_verified")):
        if record.get("archive_url") and aware_timestamp(record.get("archive_timestamp")) and before_game(record["archive_timestamp"], game_date, kickoff):
            return "A", "authorized_archived_quote_manually_verified_before_game"
        return "C", "archive_content_or_pregame_timestamp_not_verified"
    if not before_game(record.get("article_publication_date"), game_date, kickoff):
        return "C", "publication_not_established_before_game"
    modified = record.get("article_modification_date")
    if modified and not before_game(modified, game_date, kickoff):
        return "C", "modification_potentially_postgame_without_verified_snapshot"
    return "B", "pregame_dated_editorial_no_independent_snapshot_verification"


def numeric(value):
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (ValueError, TypeError):
        return None


def validate_quote(record, row, aliases):
    if not flag(record.get("collection_permission_confirmed")) or not record.get("permission_basis"):
        return "manual_collection_rights_not_confirmed"
    if not flag(record.get("quote_explicitly_published")):
        return "no_explicit_published_sportsbook_quote_confirmed"
    url = urlsplit(record.get("source_url") or "")
    if url.scheme != "https" or url.netloc != "www.usalacrosse.com" or not url.path.startswith("/magazine/"):
        return "source_not_a_target_public_editorial_url"
    market = record.get("market")
    if market in {"moneyline", "spread"}:
        selected = aliases.get(normalize(record.get("selection")))
        if selected not in {row.home_team_slug, row.away_team_slug}:
            return "selection_not_one_of_matched_teams"
    if market == "moneyline" and not record.get("moneyline_odds"):
        return "moneyline_price_missing"
    if market == "spread" and numeric(record.get("point_spread")) is None:
        return "spread_line_missing_or_invalid"
    if market == "total" and (numeric(record.get("total_goals_line")) is None or numeric(record.get("total_goals_line")) <= 0):
        return "total_line_missing_or_invalid"
    if market not in {"moneyline", "spread", "total"}:
        return "unknown_or_missing_market"
    # Prices may be absent on published spread/total lines; never default to -110.
    for field in ("moneyline_odds", "spread_price", "total_price"):
        value = record.get(field)
        if not value:
            continue
        number = numeric(value)
        kind = record.get("odds_format")
        if kind == "american" and (number is None or not number.is_integer() or abs(number) < 100):
            return "invalid_american_price"
        if kind == "decimal" and (number is None or number <= 1):
            return "invalid_decimal_price"
        if kind not in {"american", "decimal"}:
            return "price_format_not_explicitly_supported"
    return None


def process_records(records, games, aliases):
    accepted, audit = [], []
    for line, original in enumerate(records, start=2):
        record = {key: (str(value).strip() or None) if value is not None else None for key, value in original.items()}
        if record.get("entry_status") == "template":
            audit.append({"worksheet_line": line, "source_url": record.get("source_url"), "result": "TEMPLATE_NOT_A_QUOTE", "verification_status": None})
            continue
        row, match = match_game(record, games, aliases)
        reason = match if row is None else validate_quote(record, row, aliases)
        grade, temporal_reason = ("C", reason) if reason else grade_quote(record, row.game_date, row.game_datetime_utc)
        result = "ACCEPTED_PROVISIONAL" if grade in {"A", "B"} else "EXCLUDED"
        audit.append({"worksheet_line": line, "source_url": record.get("source_url"), "result": result,
                      "ncaa_game_id": None if row is None else str(row.game_id), "verification_status": grade,
                      "reason": temporal_reason})
        if grade in {"A", "B"}:
            accepted.append({**record, "ncaa_game_id": str(row.game_id), "season": 2025,
                             "game_datetime_utc": row.game_datetime_utc, "home_team": row.home_team,
                             "away_team": row.away_team, "source_orientation_status": match,
                             "verification_status": grade, "verification_reason": temporal_reason})
    return accepted, audit


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worksheet", type=Path, default=ROOT / "reports/editorial_odds_manual_entry.csv")
    parser.add_argument("--fetch", action="store_true", help="Unavailable: automated USA Lacrosse collection is prohibited")
    args = parser.parse_args(argv)
    if args.fetch:
        parser.error("USA Lacrosse terms prohibit automated collection. No requests were made; use the worksheet only after establishing appropriate reuse permission.")
    if checksum(GAMES) != GAME_HASH:
        raise ValueError("Validated NCAA input changed; review before running")
    games = pd.read_csv(GAMES, dtype={"game_id": str}, keep_default_na=False)
    ensure_worksheet(args.worksheet)
    aliases = load_aliases(games, ROOT / "reports/editorial_odds_team_aliases.csv")
    with args.worksheet.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDS:
            raise ValueError("Worksheet columns differ from the documented schema")
        accepted, audit = process_records(list(reader), games, aliases)
    output = ROOT / "data/processed/lacrosse_odds_2025_editorial.csv"
    with output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(accepted)
    pd.DataFrame(audit).to_csv(ROOT / "reports/editorial_odds_match_audit.csv", index=False)
    summary = {
        "generated_at": datetime.now(ZoneInfo("America/New_York")).isoformat(timespec="seconds"),
        "mode": "MANUAL_WORKSHEET_PERMISSION_BLOCKED", "permission_decision": "AUTOMATED_COLLECTION_PROHIBITED",
        "initial_article_pages_inspected": 2, "article_pages_collected_automatically": 0,
        "additional_article_pages_searched_or_collected": 0, "published_quote_count_on_sources": "NOT_ASSESSED",
        "actual_odds_quotations_collected": len(accepted), "unique_ncaa_games_matched": len({r["ncaa_game_id"] for r in accepted}),
        "sportsbooks_represented": len({r["bookmaker"] for r in accepted if r.get("bookmaker")}),
        "grade_A_quotes": sum(r["verification_status"] == "A" for r in accepted),
        "grade_B_quotes": sum(r["verification_status"] == "B" for r in accepted),
        "grade_C_records_excluded": sum(r.get("verification_status") == "C" for r in audit),
        "with_explicit_odds_timestamps": sum(bool(r.get("odds_timestamp")) for r in accepted),
        "ncaa_reference_games": len(games), "coverage_percent": 100 * len({r["ncaa_game_id"] for r in accepted}) / len(games),
        "dataset_state": "EMPTY_SCHEMA_ONLY" if not accepted else "PROVISIONAL_A_B_MANUAL_ENTRIES",
        "csv_path": str(output.relative_to(ROOT)), "csv_sha256": checksum(output), "ncaa_csv_sha256": checksum(GAMES),
    }
    (ROOT / "reports/editorial_odds_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
