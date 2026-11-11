"""Task 3 checks use genuine local games; no invented price fixtures."""

import json

import pandas as pd
import pytest

from src import pilot_odds as pilot
from src.research_integrity import assert_research_snapshot


@pytest.fixture
def games():
    return pd.read_csv(pilot.GAME_PATH, dtype={"game_id": str})


def test_sample_is_twenty_actual_games_with_five_per_month(games):
    sample = pilot.select_sample(games)
    assert len(sample) == sample.game_id.nunique() == 20
    assert sample.game_date.str[:7].value_counts().to_dict() == {
        "2025-02": 5, "2025-03": 5, "2025-04": 5, "2025-05": 5,
    }
    original = games.set_index("game_id")
    for row in sample.itertuples():
        actual = original.loc[row.game_id]
        assert (row.home_team, row.away_team, row.home_score, row.away_score) == (
            actual.home_team, actual.away_team, actual.home_score, actual.away_score)
    assert {"589857", "589858", "589856"}.issubset(set(sample.game_id))
    assert {"iona", "umass-lowell", "le-moyne"}.issubset(set(sample.home_team_slug) | set(sample.away_team_slug))


def test_sampling_is_independent_of_input_order_and_final_scores(games):
    before = pilot.select_sample(games).game_id.tolist()
    # Test-only permutation of real score values tests that selection never uses them.
    changed = games.sample(frac=1, random_state=42).copy()
    changed["home_score"] = changed.home_score.iloc[::-1].to_numpy()
    changed["away_score"] = changed.away_score.iloc[::-1].to_numpy()
    assert pilot.select_sample(changed).game_id.tolist() == before


def aliases():
    frame = pd.read_csv(pilot.ROOT / "reports/odds_2025_team_aliases.csv")
    assert not frame.source_team_name.duplicated().any()
    return dict(zip(frame.source_team_name, frame.ncaa_team_slug))


def test_actual_references_match_identities_without_accepting_odds(games):
    references = json.loads((pilot.ROOT / "reports/odds_2025_candidate_references.json").read_text())
    matched = [pilot.match_reference(ref, games, aliases()) for ref in references]
    assert [item[0] for item in matched] == ["589857", "589858", "589856"]
    assert all(item[1] == "identity_only_odds_not_accepted" for item in matched)
    assert all(ref["source_event_id"] is None and ref["odds_timestamp"] is None for ref in references)


def test_ambiguous_identity_is_rejected(games):
    reference = json.loads((pilot.ROOT / "reports/odds_2025_candidate_references.json").read_text())[0]
    # Repeat a real row in memory to simulate an ambiguous join, not another game.
    duplicated = pd.concat([games, games[games.game_id.eq("589857")]])
    assert pilot.match_reference(reference, duplicated, aliases()) == (None, "no_unique_team_date_match")


def test_unknown_alias_or_unverified_competition_is_rejected(games):
    reference = json.loads((pilot.ROOT / "reports/odds_2025_candidate_references.json").read_text())[0]
    assert pilot.match_reference(reference, games, {})[0] is None
    modified = {**reference, "gender": None}
    assert pilot.match_reference(modified, games, aliases()) == (None, "wrong_or_unverified_competition")


def test_documentation_examples_never_become_collected_odds(tmp_path):
    # Metadata-only fixture; no example prices or fictional game records.
    example = {"provenance_kind": "documentation_example", "source_url": "https://the-odds-api.com/sports/ncaa-lacrosse-odds.html"}
    output = tmp_path / "pilot.csv"
    accepted, rejected = pilot.export_verified([example], output)
    assert accepted == []
    assert rejected[0]["reason"] == "not_an_actual_historical_response"
    assert not output.exists()


def test_no_accepted_odds_creates_no_csv_and_preserves_existing_files(tmp_path):
    output = tmp_path / "pilot.csv"
    assert pilot.export_verified([], output) == ([], [])
    assert not output.exists()
    # Use a real local file to demonstrate existing bytes cannot be overwritten.
    raw = pilot.GAME_PATH.read_bytes()
    output.write_bytes(raw)
    with pytest.raises(ValueError, match="preserved"):
        pilot.export_verified([], output)
    assert output.read_bytes() == raw


def test_all_preexisting_project_files_are_preserved():
    manifest = json.loads((pilot.ROOT / "reports/odds_2025_existing_files_manifest.json").read_text())
    assert_research_snapshot(pilot.ROOT, manifest["sha256"])


def test_pilot_reports_zero_coverage_without_fabricated_odds_file():
    summary = json.loads((pilot.ROOT / "reports/odds_2025_pilot_summary.json").read_text())
    audit = pd.read_csv(pilot.ROOT / "reports/odds_2025_candidate_audit.csv")
    coverage = pd.read_csv(pilot.ROOT / "reports/odds_2025_sample_coverage.csv")
    assert summary["sampled_games"] == 20
    assert summary["accepted_odds_records"] == summary["unique_games_matched"] == 0
    assert summary["sportsbooks_collected"] == 0
    assert all(value == 0 for value in summary["coverage_percentages"].values())
    assert not audit.accepted_odds.any()
    assert len(audit) == 3 and len(coverage) == 20
    assert coverage.verified_odds_records.sum() == 0
    assert summary["feasibility"] == "NOT CONFIRMED"
    assert not (pilot.ROOT / "data/processed/lacrosse_odds_2025_pilot.csv").exists()
