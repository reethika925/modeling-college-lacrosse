"""Permission-blocked pilot tests. Timing cases are hypothetical metadata only.

No odds values, bookmaker quotations, or archived source records are invented.
All match identities come from the genuine local NCAA CSV. No test quote is
exported to the project dataset.
"""

import csv
import json

import pandas as pd
import pytest
import requests

from src import collect_editorial_odds as editorial
from src.research_integrity import assert_research_snapshot


@pytest.fixture
def games():
    return pd.read_csv(editorial.GAMES, dtype={"game_id": str}, keep_default_na=False)


def test_terms_prohibition_overrides_robots_allowance():
    policy = json.loads((editorial.ROOT / "reports/editorial_odds_permissions.json").read_text())
    assert policy["robots_http_status"] == 200
    assert all(policy["robots_article_permissions"].values())
    assert policy["decision"] == "AUTOMATED_COLLECTION_PROHIBITED"


def test_fetch_flag_stops_before_any_network_request(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Permission-blocked collector must never request an article")

    monkeypatch.setattr(requests.sessions.Session, "request", forbidden)
    with pytest.raises(SystemExit) as result:
        editorial.main(["--fetch"])
    assert result.value.code == 2


def test_blank_source_templates_are_not_quotes_and_are_preserved(tmp_path, games):
    path = tmp_path / "manual.csv"
    editorial.ensure_worksheet(path)
    original = path.read_bytes()
    editorial.ensure_worksheet(path)
    assert path.read_bytes() == original
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert [row["source_url"] for row in rows] == editorial.ARTICLE_URLS
    assert all(not row["moneyline_odds"] and not row["point_spread"] and not row["bookmaker"] for row in rows)
    accepted, audit = editorial.process_records(rows, games, {})
    assert accepted == []
    assert all(row["result"] == "TEMPLATE_NOT_A_QUOTE" for row in audit)


@pytest.mark.parametrize("record,expected", [
    ({"article_publication_date": "2025-05-25"}, "B"),
    ({"article_publication_date": "2025-05-26"}, "C"),
    ({"article_publication_date": "2025-05-26T12:00:00Z"}, "B"),
    ({"article_publication_date": "2025-05-27"}, "C"),
    ({"article_publication_date": "2025-05-25", "article_modification_date": "2025-05-27"}, "C"),
    ({"odds_timestamp": "2025-05-26T16:00:00Z", "odds_timestamp_verified": "true"}, "A"),
    ({"odds_timestamp": "2025-05-26T18:00:00Z", "odds_timestamp_verified": "true"}, "C"),
    ({"odds_timestamp": "2025-05-26T16:00:00", "odds_timestamp_verified": "true"}, "C"),
    ({"archived_quote_verified": "true"}, "C"),
])
def test_hypothetical_timing_metadata_grades_are_conservative(record, expected):
    # Timing-only cases use the actual championship kickoff as the comparison.
    assert editorial.grade_quote(record, "2025-05-26", "2025-05-26T17:00:00+00:00")[0] == expected


def test_unknown_kickoff_does_not_create_a_same_day_time():
    record = {"article_publication_date": "2025-05-26T12:00:00Z"}
    assert editorial.grade_quote(record, "2025-05-26", "")[0] == "C"
    assert editorial.grade_quote({"article_publication_date": "2025-05-25"}, "2025-05-26", "")[0] == "B"


def actual_identity():
    return {"game_date": "2025-05-26", "source_team_1": "Maryland", "source_team_2": "Cornell",
            "sport": "lacrosse", "competition": "NCAA Division I", "gender": "men", "competition_verified": "true"}


def test_match_does_not_assume_first_team_is_home(games):
    record = actual_identity()
    aliases = {"maryland": "maryland", "cornell": "cornell"}
    row, status = editorial.match_game(record, games, aliases)
    assert row.game_id == "589856" and row.home_team == "Cornell"
    assert status == "not_stated_matchup_order_not_used_as_home_away"
    # Explicit conflicting orientation is a test-only mutation, not a new game.
    record.update(source_home_team="Maryland", source_away_team="Cornell")
    assert editorial.match_game(record, games, aliases)[0] is None


def test_ambiguous_or_unreviewed_matches_are_rejected(games):
    record = actual_identity()
    assert editorial.match_game(record, games, {})[0] is None
    repeated = pd.concat([games, games[games.game_id.eq("589856")]])
    assert editorial.match_game(record, repeated, {"maryland": "maryland", "cornell": "cornell"})[0] is None


def test_unconfirmed_entry_is_c_and_never_enters_output(games):
    # Identity-only input contains no betting quote and no invented prices.
    record = {**actual_identity(), "entry_status": "entered", "source_url": editorial.ARTICLE_URLS[0]}
    accepted, audit = editorial.process_records([record], games, {"maryland": "maryland", "cornell": "cornell"})
    assert accepted == [] and audit[0]["verification_status"] == "C"
    assert audit[0]["reason"] == "manual_collection_rights_not_confirmed"
    assert record.get("spread_price") is None


def test_initial_output_is_empty_and_prior_files_unchanged():
    summary = json.loads((editorial.ROOT / "reports/editorial_odds_summary.json").read_text())
    output = pd.read_csv(editorial.ROOT / summary["csv_path"])
    assert output.empty and output.columns.tolist() == editorial.OUTPUT_FIELDS
    assert summary["actual_odds_quotations_collected"] == summary["unique_ncaa_games_matched"] == 0
    assert summary["coverage_percent"] == 0
    assert summary["published_quote_count_on_sources"] == "NOT_ASSESSED"
    manifest = json.loads((editorial.ROOT / "reports/editorial_odds_existing_files.json").read_text())
    assert_research_snapshot(editorial.ROOT, manifest)
