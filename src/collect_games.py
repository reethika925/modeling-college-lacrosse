"""Collect NCAA DI men's daily results, preserving raw responses and coverage gaps."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser
from zoneinfo import ZoneInfo

import pandas as pd
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SOURCE_NAME = "NCAA Casablanca DI men's lacrosse scoreboard"
SOURCE_PAGE = "https://www.ncaa.com/scoreboard/lacrosse-men/d1"
HISTORY_URL = "https://www.ncaa.com/history/lacrosse-men/d1"
USER_AGENT = "CSE519-Lacrosse-Data/1.0 (university research)"
COLUMNS = [
    "game_id", "season", "game_date", "game_datetime_utc", "home_team", "away_team",
    "home_team_id", "away_team_id", "home_score", "away_score", "winner", "game_status",
    "neutral_site", "venue", "postseason", "source_name", "source_url",
    "home_team_slug", "away_team_slug", "home_team_code", "away_team_code",
    "home_winner_flag", "away_winner_flag", "bracket_round", "bracket_id",
    "final_message", "current_period", "overtime", "start_time_text", "start_time_epoch_raw",
    "home_score_raw", "away_score_raw", "invalid_score_format", "game_page_url",
]
LOG_COLUMNS = ["season", "date", "source_url", "retrieved_at", "result", "http_status",
               "content_type", "event_count", "attempts", "error", "raw_path", "sha256"]


def timestamp() -> str:
    return datetime.now(ZoneInfo("America/New_York")).isoformat(timespec="seconds")


def daily_url(day: date) -> str:
    return f"https://data.ncaa.com/casablanca/scoreboard/lacrosse-men/d1/{day:%Y/%m/%d}/scoreboard.json"


class AccessStopped(RuntimeError):
    """Access restrictions must stop further requests to this source."""


class Fetcher:
    """One request per second maximum, robots checks, bounded transient retries."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        self.last_start = 0.0
        self.policies = {}
        self.blocked = set()
        self.robots_log = []
        self.last_status = None
        self.attempts = 0

    def request(self, url, delay=1.05):
        time.sleep(max(0, delay - (time.monotonic() - self.last_start)))
        self.last_start = time.monotonic()
        return self.session.get(url, timeout=(10, 30), allow_redirects=False)

    def get(self, url):
        self.last_status = None
        self.attempts = 0
        parts = urlsplit(url)
        origin = f"{parts.scheme}://{parts.netloc}"
        if parts.scheme != "https" or parts.netloc not in {
            "www.ncaa.com", "data.ncaa.com", "site.api.espn.com"
        }:
            raise AccessStopped(f"Unexpected host or protocol: {url}")
        if origin in self.blocked:
            raise AccessStopped(f"Source previously denied access: {origin}")
        if origin not in self.policies:
            response = self.request(origin + "/robots.txt")
            self.robots_log.append({"url": origin + "/robots.txt", "http_status": response.status_code,
                                    "retrieved_at": timestamp(), "body": response.text})
            policy = RobotFileParser()
            if response.status_code == 200:
                if "<html" in response.text.lower():
                    raise AccessStopped(f"robots.txt returned an HTML challenge: {origin}")
                policy.parse(response.text.splitlines())
            elif response.status_code in (404, 410):
                policy.parse([])
            else:
                self.blocked.add(origin)
                raise AccessStopped(f"robots.txt HTTP {response.status_code}: {origin}; endpoint not requested")
            self.policies[origin] = policy
        policy = self.policies[origin]
        if not policy.can_fetch(USER_AGENT, url):
            raise AccessStopped(f"robots.txt disallows {url}")
        delay = max(1.05, policy.crawl_delay(USER_AGENT) or 0)
        rate = policy.request_rate(USER_AGENT)
        if rate:
            delay = max(delay, rate.seconds)
        for attempt in range(3):
            self.attempts = attempt + 1
            try:
                response = self.request(url, delay)
                self.last_status = response.status_code
            except requests.RequestException:
                if attempt == 2:
                    raise
                time.sleep(2 ** (attempt + 1))
                continue
            if response.status_code in (401, 403, 429):
                self.blocked.add(origin)
                raise AccessStopped(f"HTTP {response.status_code} access denial/rate limit: {url}; collection stopped")
            if response.status_code >= 500 and attempt < 2:
                time.sleep(2 ** (attempt + 1))
                continue
            # Redirects are not followed to unchecked URLs. 404 is not an empty day.
            return response
        raise RuntimeError("Unreachable retry state")


def load_payload(raw: bytes, content_type: str = "application/json") -> dict:
    if "json" not in content_type.lower():
        raise ValueError(f"Expected JSON; received {content_type}")
    payload = json.loads(raw)
    if not isinstance(payload, dict) or not isinstance(payload.get("games"), list):
        raise ValueError("Unrecognized scoreboard schema: expected a games list")
    return payload


def score_value(value):
    if value is None or str(value).strip() == "":
        return None, False
    if isinstance(value, bool) or not re.fullmatch(r"-?\d+", str(value).strip()):
        return None, True
    return int(value), False


def parse_games(payload: dict, requested_day: date, season: int, source_url: str) -> list[dict]:
    rows = []
    for wrapper in payload["games"]:
        game = wrapper.get("game")
        if not isinstance(game, dict) or not game.get("gameID"):
            raise ValueError("Missing game object or source gameID")
        game_day = datetime.strptime(game["startDate"], "%m-%d-%Y").date()
        if game_day != requested_day:
            raise ValueError(f"Game date {game_day} does not match requested day {requested_day}")
        home, away = game.get("home"), game.get("away")
        if not isinstance(home, dict) or not isinstance(away, dict):
            raise ValueError("Missing explicit home/away objects")
        hn, an = home.get("names", {}), away.get("names", {})
        home_name, away_name = hn.get("short") or hn.get("full"), an.get("short") or an.get("full")
        if not home_name or not away_name:
            raise ValueError("Missing team name")
        hs, bad_home = score_value(home.get("score"))
        aws, bad_away = score_value(away.get("score"))
        state = game.get("gameState") or None
        hw, aw = home.get("winner"), away.get("winner")
        completed = str(state).lower() == "final"
        winner = None
        if completed and hw is True and aw is False:
            winner = home_name
        elif completed and aw is True and hw is False:
            winner = away_name
        time_text = game.get("startTime") or ""
        epoch = game.get("startTimeEpoch")
        # TBA dates have placeholder epochs: do not pretend those are actual start times.
        utc = None
        if epoch and time_text.strip().upper() not in {"", "TBA", "TBD"}:
            utc = datetime.fromtimestamp(int(epoch), timezone.utc).isoformat()
        bracket_round = game.get("bracketRound") or None
        bracket_id = game.get("bracketId") or None
        final_message = game.get("finalMessage") or None
        period = game.get("currentPeriod") or None
        page = game.get("url")
        rows.append(dict(zip(COLUMNS, [
            str(game["gameID"]), season, game_day.isoformat(), utc, home_name, away_name,
            None, None, hs, aws, winner, state,
            game.get("neutralSite") if isinstance(game.get("neutralSite"), bool) else None,
            game.get("venue") if isinstance(game.get("venue"), str) else None,
            True if bracket_round or bracket_id else None,
            SOURCE_NAME, source_url, hn.get("seo"), an.get("seo"), hn.get("char6"), an.get("char6"),
            hw, aw, bracket_round, bracket_id, final_message, period,
            bool(re.search(r"\b\d*OT\b", f"{final_message} {period}", re.I)) if completed else None,
            time_text or None, epoch, home.get("score"), away.get("score"), bad_home or bad_away,
            "https://www.ncaa.com" + page if isinstance(page, str) and page.startswith("/game/") else None,
        ])))
    return rows


def frame_from_rows(rows):
    frame = pd.DataFrame(rows, columns=COLUMNS)
    for column in ("home_score", "away_score", "season"):
        frame[column] = pd.array(frame[column], dtype="Int64")
    return frame.sort_values(["game_date", "game_id"], kind="stable").reset_index(drop=True)


def validate(frame: pd.DataFrame) -> dict:
    completed = frame.game_status.eq("final")
    valid_scores = frame.home_score.notna() & frame.away_score.notna()
    negative = frame.home_score.lt(0).fillna(False) | frame.away_score.lt(0).fillna(False)
    tied = completed & valid_scores & frame.home_score.eq(frame.away_score)
    score_winner = frame.home_team.where(frame.home_score.gt(frame.away_score).fillna(False), frame.away_team)
    wrong_winner = completed & valid_scores & ~tied & frame.winner.notna() & frame.winner.ne(score_winner)
    matchup_keys = [tuple(sorted((str(h), str(a)))) for h, a in zip(frame.home_team_slug, frame.away_team_slug)]
    matchups = pd.DataFrame({"date": frame.game_date, "teams": matchup_keys})
    teams = set(frame.home_team_slug.dropna()) | set(frame.away_team_slug.dropna())
    return {
        "total_games": len(frame), "column_count": len(frame.columns), "completed_games": int(completed.sum()),
        "completed_valid_scores": int((completed & valid_scores & ~negative & ~tied).sum()),
        "unique_teams": len(teams),
        "games_by_month": frame.game_date.str[:7].value_counts().sort_index().to_dict(),
        "duplicate_game_ids": int(frame.game_id.duplicated().sum()),
        "duplicate_matchups_same_date": int(matchups.duplicated().sum()),
        "missing_values": {k: int(v) for k, v in frame.isna().sum().items()},
        "negative_scores": int(negative.sum()),
        "invalid_score_formats": int(frame.invalid_score_format.fillna(False).sum()),
        "completed_missing_scores": int((completed & ~valid_scores).sum()),
        "completed_ties": int(tied.sum()), "winner_disagreements": int(wrong_winner.sum()),
        "completed_missing_winner": int((completed & frame.winner.isna()).sum()),
        "first_game_date": frame.game_date.min() if len(frame) else None,
        "last_game_date": frame.game_date.max() if len(frame) else None,
        "status_counts": frame.game_status.fillna("MISSING").value_counts().to_dict(),
    }


def verify_championship(frame, season, client, offline=False):
    """Compare the collected game with the independent NCAA history table."""
    evidence = {"source_url": HISTORY_URL, "result": "FAILED"}
    if season != 2025:
        return {**evidence, "result": "NOT_CHECKED", "reason": "Check defined for 2025 only"}
    raw_path = ROOT / "data/raw/games/2025/championship_history.html"
    meta_path = raw_path.with_suffix(".meta.json")
    try:
        if raw_path.exists() and meta_path.exists():
            raw = raw_path.read_bytes()
            metadata = json.loads(meta_path.read_text())
            if hashlib.sha256(raw).hexdigest() != metadata["sha256"]:
                raise ValueError("Championship history cache checksum mismatch")
        elif offline:
            raise ValueError("No independent history cache; offline mode")
        else:
            response = client.get(HISTORY_URL)
            if response.status_code != 200:
                raise ValueError(f"Championship history HTTP {response.status_code}")
            raw = response.content
            metadata = {"source_url": HISTORY_URL, "http_status": response.status_code,
                        "retrieved_at": timestamp(), "sha256": hashlib.sha256(raw).hexdigest()}
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            raw_path.write_bytes(raw)
            meta_path.write_text(json.dumps(metadata, indent=2) + "\n")
        evidence.update(metadata)
        soup = BeautifulSoup(raw, "html.parser")
        records = [row.get_text(" | ", strip=True) for row in soup.select("tr")
                   if row.get_text(" ", strip=True).startswith("2025 ")]
        if len(records) != 1:
            raise ValueError("Could not uniquely identify the NCAA history table's 2025 row")
        record = records[0]
        evidence["ncaa_history_record"] = record
        history_matches = all(token in record for token in ("Cornell", "Maryland", "13-10"))
        matchup = frame[
            frame.game_date.eq("2025-05-26") &
            ((frame.home_team.eq("Cornell") & frame.away_team.eq("Maryland")) |
             (frame.home_team.eq("Maryland") & frame.away_team.eq("Cornell")))
        ]
        matches = False
        if len(matchup) == 1:
            row = matchup.iloc[0]
            scores = {row.home_team: row.home_score, row.away_team: row.away_score}
            matches = all(pd.notna(value) for value in scores.values()) and scores == {"Cornell": 13, "Maryland": 10} and row.game_status == "final" and row.winner == "Cornell"
        evidence.update(result="PASS" if history_matches and matches else "FAILED",
                        dataset_matches=bool(matches), matching_dataset_rows=len(matchup))
    except (requests.RequestException, AccessStopped, ValueError, KeyError, OSError) as exc:
        evidence["error"] = str(exc)
    return evidence


def resolve_duplicates(frame, season):
    """Select only existing, evidence-backed records; leave unknown conflicts visible."""
    duplicate_rows = frame[frame.game_id.duplicated(keep=False)]
    duplicate_rows.to_csv(ROOT / f"reports/games_{season}_duplicate_records.csv", index=False)
    manifest_path = ROOT / f"reports/games_{season}_duplicate_resolutions.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {"resolutions": []}
    removed = []
    for decision in manifest["resolutions"]:
        group = frame[frame.game_id.eq(decision["game_id"])]
        if len(group) < 2:
            continue
        consistent = all(group[column].notna().all() and group[column].eq(decision[column]).all() for column in (
            "home_team_slug", "away_team_slug", "home_score", "away_score", "game_page_url"))
        selected = group.game_date.eq(decision["keep_game_date"])
        if not consistent or selected.sum() != 1 or not decision.get("evidence_url"):
            raise ValueError(f"Duplicate resolution does not match actual source rows: {decision['game_id']}")
        discarded = group[~selected]
        removed.extend(discarded.index.tolist())
    return frame.drop(index=removed).reset_index(drop=True), len(removed)


def probe_sources(client: Fetcher, season: int, raw_dir: Path) -> list[dict]:
    """Probe requested sources in order, retaining status and actual schema samples."""
    probes = [("NCAA webpage", SOURCE_PAGE)]
    days = [date(season, 1, 1), date(season, 3, 15), date(season, 5, 26)]
    probes += [("NCAA JSON", daily_url(day)) for day in days]
    probes += [("ESPN JSON", "https://site.api.espn.com/apis/site/v2/sports/lacrosse/"
                f"mens-college-lacrosse/scoreboard?dates={day:%Y%m%d}") for day in days[1:]]
    results = []
    raw_dir.mkdir(parents=True, exist_ok=True)
    for index, (name, url) in enumerate(probes):
        record = {"source": name, "url": url, "retrieved_at": timestamp(),
                  "http_status": None, "content_type": None, "available_event_count": None}
        try:
            response = client.get(url)
            record.update(http_status=response.status_code, content_type=response.headers.get("Content-Type"))
            (raw_dir / f"probe_{index}.body").write_bytes(response.content)
            try:
                payload = response.json()
                record["top_level_keys"] = list(payload) if isinstance(payload, dict) else None
                events = payload.get("games", payload.get("events")) if isinstance(payload, dict) else None
                record["available_event_count"] = len(events) if isinstance(events, list) else None
                record["schema_sample"] = events[:1] if isinstance(events, list) else payload
            except ValueError:
                record["response_excerpt"] = response.text[:200]
        except (AccessStopped, requests.RequestException) as exc:
            record["error"] = str(exc)
        print(json.dumps(record, indent=2), flush=True)
        results.append(record)
    (ROOT / "reports/games_source_probes.json").write_text(
        json.dumps({"probes": results, "robots_checks": client.robots_log}, indent=2) + "\n")
    return results


def collect(args, client: Fetcher):
    raw_dir = ROOT / f"data/raw/games/{args.season}"
    raw_dir.mkdir(parents=True, exist_ok=True)
    log_path = ROOT / "reports/games_collection_log.csv"
    prior = {}
    if log_path.exists():
        with log_path.open(newline="") as handle:
            prior = {(r["season"], r["date"]): r for r in csv.DictReader(handle)}
    records, rows = [], []
    day = args.start_date
    halted = None
    while day <= args.end_date:
        raw_path = raw_dir / f"{day}.json"
        meta_path = raw_dir / f"{day}.meta.json"
        record = dict.fromkeys(LOG_COLUMNS, "")
        record.update(season=args.season, date=day.isoformat(), source_url=daily_url(day),
                      retrieved_at=timestamp(), result="unchecked")
        try:
            if (args.resume or args.offline) and raw_path.exists() and meta_path.exists():
                metadata = json.loads(meta_path.read_text())
                raw = raw_path.read_bytes()
                if metadata["source_url"] != daily_url(day) or hashlib.sha256(raw).hexdigest() != metadata["sha256"]:
                    raise ValueError("Cached response hash/URL mismatch; remove damaged cache before retrying")
                payload = load_payload(raw, metadata["content_type"])
                parsed = parse_games(payload, day, args.season, daily_url(day))
                record.update(metadata, result="cached", attempts=0)
            elif args.offline:
                record.update(prior.get((str(args.season), day.isoformat()), {}))
                record["error"] = record["error"] or "No verified response in local cache; offline mode"
                parsed = []
            elif halted:
                record["error"] = halted
                parsed = []
            else:
                response = client.get(daily_url(day))
                record.update(http_status=response.status_code, content_type=response.headers.get("Content-Type", ""),
                              attempts=client.attempts)
                if response.status_code != 200:
                    raise ValueError(f"HTTP {response.status_code}; cannot verify games or an empty day")
                payload = load_payload(response.content, record["content_type"])
                parsed = parse_games(payload, day, args.season, daily_url(day))
                record.update(result="success", event_count=len(payload["games"]),
                              raw_path=str(raw_path.relative_to(ROOT)),
                              sha256=hashlib.sha256(response.content).hexdigest())
                temporary = raw_path.with_suffix(".json.part")
                temporary.write_bytes(response.content)
                temporary.replace(raw_path)
                meta_path.write_text(json.dumps(record, indent=2) + "\n")
            rows.extend(parsed)
        except (AccessStopped, requests.RequestException, ValueError, KeyError, TypeError) as exc:
            record.update(result="failed", error=str(exc))
            if isinstance(exc, AccessStopped):
                halted = str(exc)
            if client.last_status is not None and record["http_status"] == "":
                record["http_status"] = client.last_status
            if record["attempts"] == "":
                record["attempts"] = client.attempts
        records.append(record)
        if len(records) % 15 == 0 or record["result"] == "failed":
            print(f"{day}: {record['result']}; games={record['event_count'] or 0}; HTTP={record['http_status']}", flush=True)
        # Append each checked day immediately so an interrupted run retains its failure log.
        if not args.offline:
            with log_path.open("a", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=LOG_COLUMNS)
                if handle.tell() == 0:
                    writer.writeheader()
                writer.writerow(record)
        day += timedelta(days=1)
    return frame_from_rows(rows), records


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--season", type=int, default=2025)
    parser.add_argument("--start-date", type=date.fromisoformat)
    parser.add_argument("--end-date", type=date.fromisoformat)
    parser.add_argument("--resume", action="store_true", help="Reuse successful, hash-verified daily responses")
    parser.add_argument("--offline", action="store_true", help="Validate cache and previous log without network requests")
    parser.add_argument("--probe-only", action="store_true", help="Probe sources; do not collect the season")
    args = parser.parse_args(argv)
    if args.offline and args.probe_only:
        parser.error("--offline and --probe-only cannot be combined")
    args.start_date = args.start_date or date(args.season, 1, 1)
    args.end_date = args.end_date or date(args.season, 6, 30)
    if args.start_date > args.end_date or any(d.year != args.season for d in (args.start_date, args.end_date)):
        parser.error("Dates must be ordered and within the requested season year")
    (ROOT / "reports").mkdir(exist_ok=True)
    client = Fetcher()
    try:
        if args.probe_only:
            probe_sources(client, args.season, ROOT / f"data/raw/games/{args.season}/probes")
            return 0
        frame, coverage = collect(args, client)
        raw_summary = validate(frame)
        frame, resolved_duplicates = resolve_duplicates(frame, args.season)
        output = ROOT / f"data/processed/lacrosse_games_{args.season}.csv"
        output.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(output, index=False)
        summary = validate(frame)
        summary.update(source_name=SOURCE_NAME, source_template=daily_url(date(args.season, 1, 1)),
                       retrieved_at=timestamp(), collection_start=str(args.start_date), collection_end=str(args.end_date),
                       checked_successfully=sum(r["result"] in {"success", "cached"} for r in coverage),
                       requested_dates=len(coverage),
                       failed_or_unchecked_dates=[r["date"] for r in coverage if r["result"] not in {"success", "cached"}],
                       output_path=str(output.relative_to(ROOT)), sha256=hashlib.sha256(output.read_bytes()).hexdigest())
        summary.update(raw_game_records=raw_summary["total_games"], raw_duplicate_game_ids=raw_summary["duplicate_game_ids"],
                       resolved_duplicate_records=resolved_duplicates,
                       independent_championship_validation=verify_championship(frame, args.season, client, args.offline))
        if __package__:
            from .games_reporting import write_reports
        else:
            from games_reporting import write_reports
        write_reports(ROOT, summary, frame, coverage, args)
        print(json.dumps(summary, indent=2))
        print("\nFirst ten actual rows:\n" + frame.head(10).to_string(index=False))
        invalid = any(summary[key] for key in (
            "duplicate_game_ids", "duplicate_matchups_same_date", "negative_scores", "invalid_score_formats",
            "completed_missing_scores", "completed_ties", "winner_disagreements", "completed_missing_winner"))
        return 0 if not summary["failed_or_unchecked_dates"] and not invalid and summary["independent_championship_validation"]["result"] == "PASS" else 2
    finally:
        client.session.close()


if __name__ == "__main__":
    sys.exit(main())
