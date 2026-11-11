"""Check actual downloaded releases and the audit's failure/competition boundaries."""

import io
import json
import zipfile
from pathlib import Path

import pandas as pd
import pytest

from src import audit_kaggle as audit
from src.research_integrity import assert_research_snapshot


def test_every_official_file_is_preserved_exactly():
    records = json.loads((audit.ROOT / "research/kaggle/download_log.json").read_text())
    assert len(records) == 2
    for record in records:
        archive = audit.ROOT / record["archive_path"]
        assert audit.checksum(archive) == record["archive_sha256"]
        listing = json.loads((audit.RAW / f"{record['dataset_ref'].replace('/', '__')}.list.response").read_bytes())
        with zipfile.ZipFile(archive) as handle:
            assert handle.testzip() is None
            assert set(handle.namelist()) == {item["name"] for item in listing["datasetFiles"]}
            for file in record["files"]:
                original = audit.ROOT / file["local_path"]
                assert original.read_bytes() == handle.read(file["name"])
                assert original.stat().st_size == file["bytes"]
                assert audit.checksum(original) == file["sha256"]


def test_actual_odds_are_2026_pll_not_2025_ncaa():
    path = audit.RAW / "harsh21x/live-sports-betting-odds-snapshot/files/sports.csv"
    frame, profile = audit.inspect_csv(path)
    ncaa = pd.read_csv(audit.GAME_PATH)
    result = audit.inspect_odds(frame, ncaa)
    assert (profile["rows"], profile["columns_count"]) == (225, 10)
    assert result["event_years"] == [2026]
    assert result["lacrosse_rows"] == 24 and result["lacrosse_events"] == 1
    assert result["sports_competitions_row_counts"]["PLL"] == 24
    assert result["ncaa_lacrosse_rows"] == result["all_sport_2025_rows"] == 0
    assert result["eligible_2025_ncaa_rows"] == result["matched_ncaa_games"] == 0
    assert result["quote_timestamp_columns"] == []
    assert [column for column in frame if "time" in column.lower()] == ["commence_time"]
    assert result["decimal_prices_at_or_below_one"] == 4


def test_player_files_do_not_invent_missing_league_or_game_identity():
    base = audit.RAW / "tjmulderig/professional-lacrosse-statistics-pll-mll/files"
    total_rows = 0
    for path in base.glob("*.csv"):
        frame, _ = audit.inspect_csv(path)
        total_rows += len(frame)
        result = audit.inspect_players(frame)
        assert result["game_date_columns"] == result["bookmaker_columns"] == result["odds_price_columns"] == []
        assert result["matched_ncaa_games"] == 0
        if "2021" in path.name:
            assert result["league_values"] is None and result["team_id_values"] is None
            assert frame.shortHandedGoalsAgainst.isna().all()
        else:
            assert set(result["league_values"]) == {"PLL", "MLL"}
    assert total_rows == 1333


def test_exported_index_does_not_hide_statistic_duplicates():
    path = audit.RAW / "tjmulderig/professional-lacrosse-statistics-pll-mll/files/2019_postseason_stats.csv"
    _, profile = audit.inspect_csv(path)
    assert profile["duplicate_rows_including_index"] == 0
    assert profile["duplicate_rows_excluding_exported_index"] == 4


def test_html_and_truncated_csv_are_rejected(monkeypatch, tmp_path):
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    path = tmp_path / "bad.csv"
    path.write_bytes(b"<html>Login required</html>")
    with pytest.raises(ValueError, match="HTML"):
        audit.inspect_csv(path)
    # Truncate one record from the real CSV in a test-only copy.
    source = audit.RAW / "harsh21x/live-sports-betting-odds-snapshot/files/sports.csv"
    lines = source.read_text().splitlines()
    lines[1] = lines[1].rsplit(",", 1)[0]
    path.write_text("\n".join(lines))
    with pytest.raises(ValueError, match="width mismatch"):
        audit.inspect_csv(path)


def test_zip_path_traversal_is_rejected(tmp_path):
    # Test-only unsafe filename, carrying the genuine source CSV bytes.
    source = audit.RAW / "harsh21x/live-sports-betting-odds-snapshot/files/sports.csv"
    raw = source.read_bytes()
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as handle:
        handle.writestr("../sports.csv", raw)
    buffer.seek(0)
    with pytest.raises(ValueError, match="Unsafe"):
        audit.extract_originals(buffer, [{"name": "../sports.csv", "totalBytes": len(raw)}], tmp_path / "files")
    assert not (tmp_path / "sports.csv").exists()


def test_inaccessible_dataset_is_unverified_not_zero_coverage():
    report = audit.render_report({
        "generated_at": "test-only", "datasets": [
            {"reference": reference, "version": version, "status": "UNVERIFIED", "files": [], "error": "Access not established"}
            for reference, version in audit.DATASETS.items()
        ],
    })
    assert "UNVERIFIED" in report
    assert "Missing access or metadata must not be interpreted as zero" in report
    assert "zero matches" not in report
    assert "kaggle auth login" in report


def test_all_preexisting_files_retain_checksums():
    manifest = json.loads((audit.ROOT / "research/kaggle/existing_files_manifest.json").read_text())
    assert_research_snapshot(audit.ROOT, manifest)
