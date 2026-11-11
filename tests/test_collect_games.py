"""Unit tests: real fixture plus explicitly labeled test-only mutations."""

import copy
import hashlib
import json
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest
import requests

from src import collect_games as games

DAY = date(2025, 5, 26)


@pytest.fixture
def payload():
    path = Path(__file__).parent / "fixtures/ncaa_championship_2025.json"
    return json.loads(path.read_bytes())


def parse(payload):
    return games.parse_games(payload, DAY, 2025, games.daily_url(DAY))


def test_real_championship_uses_explicit_home_and_away(payload):
    # The JSON lists away before home. Object position must not decide home status.
    row, = parse(payload)
    assert row["game_id"] == "589856"
    assert row["home_team"] == "Cornell"
    assert row["away_team"] == "Maryland"
    assert (row["home_score"], row["away_score"], row["winner"]) == (13, 10, "Cornell")
    assert row["game_datetime_utc"] == "2025-05-26T17:00:00+00:00"
    assert row["postseason"] is True
    assert row["home_team_id"] is None
    assert row["neutral_site"] is None
    assert row["venue"] is None


def test_cancelled_missing_scores_stay_missing(payload):
    # Test-only cancellation; never a claim about the actual championship.
    game = payload["games"][0]["game"]
    game["gameState"] = "cancelled"
    game["home"]["score"] = ""
    game["away"]["score"] = None
    row, = parse(payload)
    assert row["home_score"] is None and row["away_score"] is None
    assert row["winner"] is None
    summary = games.validate(games.frame_from_rows([row]))
    assert summary["completed_games"] == 0
    assert summary["invalid_score_formats"] == 0


def test_tba_epoch_is_not_treated_as_actual_start_time(payload):
    # Test-only TBA mutation; the source includes placeholder epochs for TBA games.
    payload["games"][0]["game"]["startTime"] = "TBA"
    row, = parse(payload)
    assert row["game_datetime_utc"] is None
    assert row["start_time_epoch_raw"] == "1748278800"


def test_overtime_and_unknown_postseason(payload):
    # Test-only overtime/no-bracket scenario; missing metadata does not mean False.
    game = payload["games"][0]["game"]
    game.update(finalMessage="FINAL (2OT)", currentPeriod="2OT", bracketId="", bracketRound="")
    row, = parse(payload)
    assert row["overtime"] is True
    assert row["postseason"] is None


@pytest.mark.parametrize("bad_score,negative,invalid", [("-1", 1, 0), ("1.5", 0, 1), ("bad", 0, 1)])
def test_invalid_scores_are_reported(payload, bad_score, negative, invalid):
    # Test-only corrupted scores; preserve the raw value for diagnosis.
    payload["games"][0]["game"]["home"]["score"] = bad_score
    rows = parse(payload)
    assert rows[0]["home_score_raw"] == bad_score
    summary = games.validate(games.frame_from_rows(rows))
    assert summary["negative_scores"] == negative
    assert summary["invalid_score_formats"] == invalid


def test_source_winner_is_checked_against_score(payload):
    # Test-only incorrect flags must be detected, not corrected during parsing.
    game = payload["games"][0]["game"]
    game["home"]["winner"] = False
    game["away"]["winner"] = True
    frame = games.frame_from_rows(parse(payload))
    assert frame.iloc[0].winner == "Maryland"
    assert games.validate(frame)["winner_disagreements"] == 1


def test_duplicate_game_and_reversed_matchup_are_detected(payload):
    original, = parse(payload)
    duplicate = copy.deepcopy(original)
    duplicate.update(home_team_slug=original["away_team_slug"], away_team_slug=original["home_team_slug"])
    summary = games.validate(games.frame_from_rows([original, duplicate]))
    assert summary["duplicate_game_ids"] == 1
    assert summary["duplicate_matchups_same_date"] == 1


def test_empty_day_is_valid_only_with_explicit_games_list():
    frame = games.frame_from_rows(games.parse_games({"games": []}, DAY, 2025, games.daily_url(DAY)))
    assert games.validate(frame)["total_games"] == 0
    with pytest.raises(ValueError, match="Expected JSON"):
        games.load_payload(b"<html>Access denied</html>", "text/html")
    with pytest.raises(ValueError, match="schema"):
        games.load_payload(b'{"error": "not found"}')


def test_wrong_date_response_is_rejected(payload):
    with pytest.raises(ValueError, match="does not match requested"):
        games.parse_games(payload, date(2025, 5, 25), 2025, "test-only-url")


def test_resume_uses_hash_verified_original_cache(monkeypatch, tmp_path, payload):
    monkeypatch.setattr(games, "ROOT", tmp_path)
    raw_dir = tmp_path / "data/raw/games/2025"
    raw_dir.mkdir(parents=True)
    (tmp_path / "reports").mkdir()
    raw = json.dumps(payload).encode()
    (raw_dir / f"{DAY}.json").write_bytes(raw)
    metadata = dict.fromkeys(games.LOG_COLUMNS, "")
    metadata.update(source_url=games.daily_url(DAY), content_type="application/json",
                    sha256=hashlib.sha256(raw).hexdigest(), http_status=200)
    (raw_dir / f"{DAY}.meta.json").write_text(json.dumps(metadata))
    args = SimpleNamespace(season=2025, start_date=DAY, end_date=DAY, resume=True, offline=False)
    client = games.Fetcher()
    monkeypatch.setattr(client, "get", lambda url: pytest.fail("Resume must not request cached dates"))
    frame, coverage = games.collect(args, client)
    assert len(frame) == 1 and coverage[0]["result"] == "cached"
    # A tampered cache must not be silently trusted.
    (raw_dir / f"{DAY}.json").write_bytes(raw + b" ")
    frame, coverage = games.collect(args, client)
    assert frame.empty and coverage[0]["result"] == "failed"
    assert "hash/URL mismatch" in coverage[0]["error"]
    client.session.close()


def response(status, body=b"", content_type="application/json"):
    item = requests.Response()
    item.status_code = status
    item._content = body
    item.headers["Content-Type"] = content_type
    return item


def test_bounded_retries_and_404_not_retried(monkeypatch):
    client = games.Fetcher()
    replies = iter([response(404), response(503), response(503), response(200)])
    monkeypatch.setattr(client, "request", lambda *args: next(replies))
    sleeps = []
    monkeypatch.setattr(games.time, "sleep", sleeps.append)
    assert client.get(games.daily_url(DAY)).status_code == 200
    assert client.attempts == 3
    assert sleeps == [2, 4]
    # Established robots policy; this 404 is an actual daily response.
    monkeypatch.setattr(client, "request", lambda *args: response(404))
    assert client.get(games.daily_url(DAY)).status_code == 404
    assert client.attempts == 1
    client.session.close()


@pytest.mark.parametrize("status", [403, 429])
def test_access_denial_stops_without_retries(monkeypatch, status):
    client = games.Fetcher()
    calls = []

    def request(url, *args):
        calls.append(url)
        return response(404 if url.endswith("robots.txt") else status)

    monkeypatch.setattr(client, "request", request)
    with pytest.raises(games.AccessStopped):
        client.get(games.daily_url(DAY))
    with pytest.raises(games.AccessStopped):
        client.get(games.daily_url(DAY))
    assert len(calls) == 2  # robots once, endpoint once; no repeated denial.
    client.session.close()


def test_known_duplicate_selects_existing_verified_row(monkeypatch, tmp_path):
    fixture_dir = Path(__file__).parent / "fixtures"
    payloads = json.loads((fixture_dir / "ncaa_duplicate_records_2025.json").read_text())
    rows = [row for day, payload in payloads.items()
            for row in games.parse_games(payload, date.fromisoformat(day), 2025, games.daily_url(date.fromisoformat(day)))]
    frame = games.frame_from_rows(rows)
    manifest = games.ROOT / "reports/games_2025_duplicate_resolutions.json"
    (tmp_path / "reports").mkdir()
    (tmp_path / "reports" / manifest.name).write_bytes(manifest.read_bytes())
    monkeypatch.setattr(games, "ROOT", tmp_path)
    selected, removed = games.resolve_duplicates(frame, 2025)
    assert removed == 1 and len(selected) == 1
    assert selected.iloc[0].game_date == "2025-02-22"
    assert selected.iloc[0].source_url.endswith("2025/02/22/scoreboard.json")
    assert frame.equals(games.frame_from_rows(rows))  # Original parsed rows unchanged.
    audit = tmp_path / "reports/games_2025_duplicate_records.csv"
    assert len(__import__("pandas").read_csv(audit)) == 2
    # Test-only corruption must invalidate the documented selection rule.
    frame.loc[0, "home_score"] = None
    with pytest.raises(ValueError, match="does not match"):
        games.resolve_duplicates(frame, 2025)


def test_unknown_duplicate_is_not_silently_removed(monkeypatch, tmp_path, payload):
    (tmp_path / "reports").mkdir()
    monkeypatch.setattr(games, "ROOT", tmp_path)
    rows = parse(payload)
    frame = games.frame_from_rows(rows + rows)
    selected, removed = games.resolve_duplicates(frame, 2025)
    assert len(selected) == 2 and removed == 0
    assert games.validate(selected)["duplicate_game_ids"] == 1


def test_independent_history_check_uses_cached_real_record(monkeypatch, tmp_path, payload):
    raw = (Path(__file__).parent / "fixtures/ncaa_history_2025_excerpt.html").read_bytes()
    cache = tmp_path / "data/raw/games/2025/championship_history.html"
    cache.parent.mkdir(parents=True)
    cache.write_bytes(raw)
    cache.with_suffix(".meta.json").write_text(json.dumps({
        "source_url": games.HISTORY_URL, "http_status": 200,
        "sha256": hashlib.sha256(raw).hexdigest(), "retrieved_at": "fixture",
    }))
    monkeypatch.setattr(games, "ROOT", tmp_path)
    client = games.Fetcher()
    monkeypatch.setattr(client, "get", lambda url: pytest.fail("Offline validation must not request network"))
    frame = games.frame_from_rows(parse(payload))
    assert games.verify_championship(frame, 2025, client, offline=True)["result"] == "PASS"
    # Test-only absent score must fail validation without crashing or filling it.
    frame.loc[0, "home_score"] = None
    assert games.verify_championship(frame, 2025, client, offline=True)["result"] == "FAILED"
    assert games.verify_championship(frame.iloc[:0], 2025, client, offline=True)["result"] == "FAILED"
    client.session.close()


def test_reports_preserve_inventory_and_do_not_claim_full_coverage(monkeypatch, tmp_path, payload):
    from src.games_reporting import write_reports

    (tmp_path / "reports").mkdir()
    inventory = tmp_path / "reports/data_inventory.md"
    inventory.write_text("# Task 1 existing content\n")
    frame = games.frame_from_rows(parse(payload))
    summary = games.validate(frame)
    summary.update(
        retrieved_at="fixture", source_name=games.SOURCE_NAME, output_path="test-only.csv", sha256="fixture",
        raw_game_records=1, raw_duplicate_game_ids=0, resolved_duplicate_records=0,
        requested_dates=181, checked_successfully=1, failed_or_unchecked_dates=["2025-01-01"],
        independent_championship_validation={"source_url": games.HISTORY_URL, "result": "PASS"},
    )
    coverage = [{"result": "failed", "http_status": 404}]
    args = SimpleNamespace(season=2025, start_date=date(2025, 1, 1), end_date=date(2025, 6, 30))
    write_reports(tmp_path, summary, frame, coverage, args)
    write_reports(tmp_path, summary, frame, coverage, args)
    assert inventory.read_text().startswith("# Task 1 existing content")
    assert inventory.read_text().count("<!-- games-collection:start -->") == 1
    assert summary["window_coverage_verified"] is False
    assert summary["season_completeness"] == "NOT_VERIFIED"
    assert "INCOMPLETE" in (tmp_path / "reports/games_2025_validation.md").read_text()


def test_offline_cannot_be_combined_with_network_probes():
    with pytest.raises(SystemExit) as error:
        games.main(["--offline", "--probe-only"])
    assert error.value.code == 2
