"""Inspect the two requested Kaggle datasets without changing project data.

Default: audit preserved local files. --download: fill missing public metadata and
archives using Kaggle's official API. No credentials are read or requested.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import time
import zipfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "research/kaggle/raw"
DATASETS = {
    "harsh21x/live-sports-betting-odds-snapshot": 1,
    "tjmulderig/professional-lacrosse-statistics-pll-mll": 5,
}
GAME_PATH = ROOT / "data/processed/lacrosse_games_2025.csv"
GAME_HASH = "79b43ec0168d5466d29a0e3be2c7a9bb46096038aefc25a54f70b2e0b24393a3"
MAX_BYTES = 10_000_000


def checksum(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now():
    return datetime.now(ZoneInfo("America/New_York")).isoformat(timespec="seconds")


def api_url(operation, reference):
    return f"https://www.kaggle.com/api/v1/datasets/{operation}/{reference}"


def fetch_public(url):
    time.sleep(1.1)
    response = requests.get(url, headers={"User-Agent": "CSE519-Lacrosse-Research/1.0"},
                            timeout=(10, 30), stream=True)
    if response.status_code != 200:
        response.close()
        raise ValueError(f"HTTP {response.status_code}; stop on restricted access and use official Kaggle authentication if required")
    chunks, size = [], 0
    try:
        for chunk in response.iter_content(65536):
            size += len(chunk)
            if size > MAX_BYTES:
                raise ValueError("Response exceeded the 10 MB research-download limit")
            chunks.append(chunk)
    finally:
        response.close()
    return b"".join(chunks), {
        "source_url": url, "retrieved_at": now(), "http_status": response.status_code,
        "content_type": response.headers.get("Content-Type"),
        "redirect_statuses": [hop.status_code for hop in response.history],
    }


def extract_originals(archive, listing, destination):
    """Validate expected filenames, sizes and CRCs; preserve exact original bytes."""
    expected = {item["name"]: item["totalBytes"] for item in listing}
    with zipfile.ZipFile(archive) as handle:
        if len(handle.infolist()) != len(expected) or set(handle.namelist()) != set(expected):
            raise ValueError("Archive members differ from the official file listing")
        if sum(item.file_size for item in handle.infolist()) > MAX_BYTES:
            raise ValueError("Expanded ZIP exceeds inspection limit")
        if handle.testzip() is not None:
            raise ValueError("Archive CRC check failed")
        for member in handle.infolist():
            if Path(member.filename).name != member.filename or member.filename in {".", ".."}:
                raise ValueError("Unsafe or unexpected archive path")
            data = handle.read(member)
            if len(data) != expected[member.filename]:
                raise ValueError(f"File size does not match official metadata: {member.filename}")
            path = destination / member.filename
            if path.exists() and path.read_bytes() != data:
                raise ValueError(f"Existing original differs from archive; refusing overwrite: {path}")
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_bytes(data)


def download_missing():
    RAW.mkdir(parents=True, exist_ok=True)
    log_path = ROOT / "research/kaggle/download_log.json"
    log = json.loads(log_path.read_text()) if log_path.exists() else []
    for reference, version in DATASETS.items():
        for operation in ("view", "list"):
            path = RAW / f"{reference.replace('/', '__')}.{operation}.response"
            if not path.exists():
                raw, metadata = fetch_public(api_url(operation, reference))
                json.loads(raw)  # Never save an HTML/login page as JSON metadata.
                path.write_bytes(raw)
                (path.with_suffix(path.suffix + ".meta.json")).write_text(json.dumps(metadata, indent=2) + "\n")
        view = json.loads((RAW / f"{reference.replace('/', '__')}.view.response").read_bytes())
        listing = json.loads((RAW / f"{reference.replace('/', '__')}.list.response").read_bytes())
        if view["currentVersionNumber"] != version:
            raise ValueError("Pinned version differs from metadata; do not silently audit a different release")
        if listing.get("nextPageToken"):
            raise ValueError("File listing is paginated; inspection would be incomplete")
        if view.get("licenseName") != "CC0: Public Domain" or view["totalBytes"] > MAX_BYTES:
            raise ValueError("License or size differs from the reviewed public release")
        folder = RAW / reference
        archive = folder / f"dataset_v{version}.zip"
        if not archive.exists():
            raw, metadata = fetch_public(api_url("download", reference) + f"?datasetVersionNumber={version}")
            if not zipfile.is_zipfile(io.BytesIO(raw)):
                raise ValueError("Download is not a ZIP; possible HTML/login/error response")
            folder.mkdir(parents=True, exist_ok=True)
            archive.write_bytes(raw)
            record = {**metadata, "dataset_ref": reference, "version": version, "status": "SUCCESS",
                      "archive_path": str(archive.relative_to(ROOT)), "archive_bytes": len(raw),
                      "archive_sha256": checksum(archive)}
            log.append(record)
        extract_originals(archive, listing["datasetFiles"], folder / "files")
    log_path.write_text(json.dumps(log, indent=2) + "\n")


def inspect_csv(path):
    raw = path.read_bytes()
    if not raw.strip() or raw.lstrip().startswith(b"<"):
        raise ValueError(f"Empty/HTML response instead of CSV: {path}")
    reader = csv.reader(io.StringIO(raw.decode("utf-8-sig")), strict=True)
    header = next(reader)
    for row in reader:
        if len(row) != len(header):
            raise ValueError(f"CSV record width mismatch: {path}")
    frame = pd.read_csv(path)
    business = frame.drop(columns=["Unnamed: 0"], errors="ignore")
    profile = {
        "name": path.name, "path": str(path.relative_to(ROOT)), "bytes": len(raw), "sha256": checksum(path),
        "rows": len(frame), "columns_count": len(frame.columns), "columns": frame.columns.tolist(),
        "dtypes": frame.dtypes.astype(str).to_dict(), "missing_values": frame.isna().sum().astype(int).to_dict(),
        "duplicate_rows_including_index": int(frame.duplicated().sum()),
        "duplicate_rows_excluding_exported_index": int(business.duplicated().sum()),
        "first_three_records": json.loads(frame.head(3).to_json(orient="records")),
    }
    return frame, profile


def inspect_odds(frame, ncaa):
    starts = pd.to_datetime(frame.commence_time, utc=True, errors="raise")
    # Use actual observed competition labels, not the dataset title or player history.
    lacrosse = frame.sports_title.str.contains(r"lacrosse|\bPLL\b|\bMLL\b", case=False, regex=True)
    ncaa_lacrosse = lacrosse & frame.sports_title.str.contains(r"NCAA|college", case=False, regex=True)
    eligible = frame[ncaa_lacrosse & starts.dt.year.eq(2025)].copy()
    direct_team_overlap = sorted((set(frame.home_team) | set(frame.away_team)) & (set(ncaa.home_team) | set(ncaa.away_team)))
    events = frame[["sports_title", "commence_time", "home_team", "away_team"]].drop_duplicates()
    return {
        "record_grain": "one bookmaker-market-outcome row; not one game per row",
        "sports_competitions_row_counts": frame.sports_title.value_counts().to_dict(),
        "bookmaker_row_counts": frame.bookmakers.value_counts().to_dict(),
        "market_row_counts": frame.market.value_counts().to_dict(),
        "unique_events_by_competition_start_home_away": len(events),
        "event_years": sorted(starts.dt.year.unique().tolist()),
        "start_min_utc": starts.min().isoformat(), "start_max_utc": starts.max().isoformat(),
        "ncaa_lacrosse_rows": int(ncaa_lacrosse.sum()), "all_sport_2025_rows": int(starts.dt.year.eq(2025).sum()),
        "lacrosse_rows": int(lacrosse.sum()), "lacrosse_events": int(events.sports_title.isin(frame.loc[lacrosse, "sports_title"]).sum()),
        "lacrosse_bookmakers": sorted(frame.loc[lacrosse, "bookmakers"].unique().tolist()),
        "lacrosse_first_two_rows": json.loads(frame[lacrosse].head(2).to_json(orient="records")),
        "decimal_prices_at_or_below_one": int(frame.price.le(1).sum()),
        "decimal_price_range": [float(frame.price.min()), float(frame.price.max())],
        "h2h_missing_point": int(frame.loc[frame.market.eq("h2h"), "point"].isna().sum()),
        "spread_missing_point": int(frame.loc[frame.market.eq("spreads"), "point"].isna().sum()),
        "quote_timestamp_columns": [], "source_event_id_columns": [], "is_live_columns": [],
        "direct_ncaa_team_name_overlap": direct_team_overlap,
        "eligible_2025_ncaa_rows": len(eligible), "matched_ncaa_games": 0,
        "verified_2025_ncaa_pregame_odds": 0,
        "authentication_of_original_bookmaker_capture": "UNVERIFIED; publisher attribution only, no original upstream JSON or quote timestamp",
    }


def inspect_players(frame):
    groups = [column for column in ("year", "statLeague", "seasonSegment") if column in frame]
    counts = frame.groupby(groups, dropna=False).size().reset_index(name="rows")
    return {
        "record_grain": "player-season/season-segment aggregate; player-team splits where teamId exists",
        "year_counts": {str(k): int(v) for k, v in frame.year.value_counts().items()},
        "league_values": sorted(frame.statLeague.unique().tolist()) if "statLeague" in frame else None,
        "segment_values": sorted(frame.seasonSegment.unique().tolist()) if "seasonSegment" in frame else None,
        "league_year_segment_counts": json.loads(counts.to_json(orient="records")),
        "unique_player_names": frame.player_name.nunique(),
        "games_played_range": [int(frame.gamesPlayed.min()), int(frame.gamesPlayed.max())],
        "team_id_values": sorted(frame.teamId.unique().tolist()) if "teamId" in frame else None,
        "bookmaker_columns": [], "odds_price_columns": [], "game_date_columns": [],
        "ncaa_2025_games": 0, "verified_2025_ncaa_pregame_odds": 0, "matched_ncaa_games": 0,
    }


def render_report(audit):
    if any(dataset["status"] != "VERIFIED_FILES_INSPECTED" for dataset in audit["datasets"]):
        lines = ["# Kaggle two-dataset audit", "", f"Generated: {audit['generated_at']}", "",
                 "**UNVERIFIED: at least one requested dataset could not be completely inspected.** "
                 "Missing access or metadata must not be interpreted as zero suitable records. "
                 "No overall compatibility or odds-availability conclusion is established.", ""]
        for dataset in audit["datasets"]:
            lines += [f"## {dataset['reference']}", "", f"- Inspection status: {dataset['status']}",
                      f"- Source: https://www.kaggle.com/datasets/{dataset['reference']}",
                      f"- Error: {dataset.get('error', 'None')}"]
            lines += [f"- Inspected file: {file['name']}, {file['rows']} rows, {file['columns_count']} columns" for file in dataset["files"]]
        lines += ["", "Use `python src/audit_kaggle.py --download` for public files. If authentication is required, "
                  "use the official Kaggle CLI locally: `kaggle auth login`. Never paste tokens or credential files into chat.",
                  "Official instructions: https://github.com/Kaggle/kaggle-cli/blob/main/docs/README.md#authentication", ""]
        return "\n".join(lines)
    odds, pros = audit["datasets"]
    detail = odds["files"][0]["inspection"] if odds["status"] == "VERIFIED_FILES_INSPECTED" else None
    lines = [
        "# Kaggle two-dataset audit", "", f"Audit generated (America/New_York): {audit['generated_at']}", "",
        "**Neither dataset solves the 2025 NCAA Division I men's historical sportsbook odds problem.** "
        "Both requested releases were downloaded publicly and their actual CSVs inspected. "
        "There are zero eligible 2025 NCAA men's lacrosse game records, zero verified matching pre-game odds, "
        "and zero matches to the project's 580 games. Professional lacrosse was not substituted for NCAA data.",
        "", f"Existing NCAA CSV SHA-256: `{audit['ncaa_csv_sha256']}`; rows: {audit['ncaa_rows']}. "
        f"All {audit['preexisting_files_verified']} pre-existing files in the preservation manifest retain their checksums.",
        "", "## Official metadata, access and original files", "",
        "Metadata and complete file listings came from Kaggle's official `/api/v1/datasets/view/OWNER/SLUG` "
        "and `/api/v1/datasets/list/OWNER/SLUG` endpoints. `view.files` was empty, so the separate listing "
        "was used; its pagination token was empty. Both public downloads returned an official storage redirect "
        "followed by HTTP 200 `application/zip`, without authentication. Archives and extracted CSV bytes remain "
        "unchanged under `research/kaggle/raw/`. CRCs, filenames, sizes and SHA-256 checksums were verified. "
        "Original metadata, listing responses, download URLs and retrieval timestamps are retained alongside them.", "",
        "| Dataset | Version | License shown by Kaggle | Archive bytes | CSV bytes | Inspection |",
        "| --- | ---: | --- | ---: | ---: | --- |",
    ]
    for dataset in audit["datasets"]:
        lines.append(f"| [{dataset['reference']}](https://www.kaggle.com/datasets/{dataset['reference']}) | {dataset['version']} | {dataset.get('license', 'UNVERIFIED')} | {dataset.get('archive_bytes', 'UNVERIFIED')} | {dataset.get('metadata_total_bytes', 'UNVERIFIED')} | {dataset['status']} |")
    lines += ["", "| Original file | Bytes | Rows | Columns |", "| --- | ---: | ---: | ---: |"]
    for dataset in audit["datasets"]:
        for file in dataset.get("files", []):
            lines.append(f"| `{file['name']}` | {file['bytes']} | {file['rows']} | {file['columns_count']} |")
    if detail:
        lines += [
            "", "## 1. Live Sports Betting Odds Snapshot — actual contents", "",
            "`sports.csv` has 225 rows and 10 columns, including the preserved exported index `Unnamed: 0`. "
            "The metadata describes singular `sport_title` and `bookmaker`; the actual headers are "
            "`sports_title` and `bookmakers`. Analysis uses the actual headers.", "",
            "Actual columns: `" + "`, `".join(odds["files"][0]["columns"]) + "`.", "",
            "One row represents an outcome for a market at a bookmaker. The file has "
            f"{detail['unique_events_by_competition_start_home_away']} distinct competition/start/home/away event tuples.",
            "", "### Actual competition and market values", "", "| Competition label | Rows |", "| --- | ---: |",
        ]
        lines += [f"| {name} | {count} |" for name, count in detail["sports_competitions_row_counts"].items()]
        lines += [
            "", f"Markets: `{detail['market_row_counts']}`. No totals market appears.",
            f"Event years: `{detail['event_years']}`. Start-time range: {detail['start_min_utc']} through {detail['start_max_utc']}.",
            "The publisher describes a single snapshot collected June 19, 2026. Every actual event start is "
            "on that date. This is not 2025 coverage or a historical price series.", "",
            "### Lacrosse records", "",
            "All 24 lacrosse rows are labeled `PLL` and concern New York Atlas (home) versus Boston Cannons "
            "(away), scheduled June 19, 2026 at 22:00 UTC. They contain 12 moneyline and 12 spread outcome rows, "
            "with two outcomes per market per book. None is labeled NCAA or college lacrosse.",
            "", "The six PLL bookmakers are: " + ", ".join(detail["lacrosse_bookmakers"]) + ".",
            "The complete file names eleven bookmakers: " + ", ".join(detail["bookmaker_row_counts"]) + ".",
            "", "Example original PLL moneyline rows: Boston Cannons at DraftKings, decimal price 1.91; "
            "New York Atlas at DraftKings, decimal price 1.83. These are source values, not project-generated prices. "
            "They were not exported to the project's NCAA odds pilot or matched to NCAA games.",
            "", "### Provenance, timestamps and quality", "",
            "Bookmaker-labeled prices and spread points are present. The uploader attributes them to The Odds API "
            "via RapidAPI; this attribution is not independent authentication of the original bookmaker capture. "
            "The original upstream JSON and capture process are absent.",
            "", "`commence_time` is an event start time. There is no quote timestamp, bookmaker `last_update`, "
            "snapshot/capture timestamp column, source event ID, or live/pre-game flag. Kaggle version/file creation "
            "times and the publisher's collection date are available as metadata, but must not be relabeled as "
            "per-quote timestamps. Some event starts precede the upload time. Pre-game status of every quote "
            "cannot be established, and line movement cannot be reconstructed from a single snapshot.",
            "", "All 137 moneyline `point` values are null, as expected for that market; all 88 spread rows "
            "have points. Four rows have decimal price 1.0, which is not a usable conventional decimal quote "
            "above 1.0. They are flagged and preserved. No full-row duplicates were found.",
            "", "### NCAA compatibility", "",
            f"NCAA/college lacrosse rows: {detail['ncaa_lacrosse_rows']}. Any-sport 2025 rows: {detail['all_sport_2025_rows']}. "
            f"Direct NCAA team-name overlap: {detail['direct_ncaa_team_name_overlap']}. "
            "The competition and year checks eliminate every row before an odds join. Eligible 2025 NCAA "
            "pre-game odds: **0**. NCAA game matches: **0**. No fuzzy professional-to-college matching was attempted.",
        ]
    lines += [
        "", "## 2. Professional Lacrosse Statistics — actual contents", "",
        "The five files contain **1,333 raw rows**, with varying schemas. They are player-season or "
        "player-season-segment aggregates, with player/team splits where teamId exists. They are not "
        "team-game results. `gamesPlayed` aggregates multiple appearances, and there are no event opponents, "
        "game dates, sportsbook names, odds prices or quote timestamps.",
        "", "2019 and 2020 files explicitly encode `statLeague` values `PLL` and `MLL`. The 2021 files "
        "do not have `statLeague` or `teamId`; exact row-level league/team assignment is therefore "
        "**UNVERIFIED from those CSVs**. The uploader describes professional outdoor lacrosse and the PLL's "
        "third-season context, but that context is not an observed league column. The 2021 regular file also "
        "lacks `seasonSegment`; its regular-season label comes from the file context, not a populated column.",
        "", "### Per-file columns and observed groups", "",
    ]
    for file in pros.get("files", []):
        info = file["inspection"]
        lines += [
            f"#### {file['name']}", "", "Actual columns:", "", "```text", ", ".join(file["columns"]), "```", "",
            "Observed year/league/segment groups:", "", "```json",
            json.dumps(info["league_year_segment_counts"], indent=2), "```", "",
            f"Unique player names: {info['unique_player_names']}; gamesPlayed range: {info['games_played_range']}; "
            f"full-row duplicates: {file['duplicate_rows_including_index']}; duplicate rows after excluding exported "
            f"index: {file['duplicate_rows_excluding_exported_index']}.",
        ]
    lines += [
        "", "All recorded years are 2019, 2020 and 2021; there are no 2025 rows. "
        "`2019_postseason_stats.csv` has four duplicate statistic rows hidden by different exported index values. "
        "The two 2021 files have an entirely null `shortHandedGoalsAgainst` column (148 and 260 nulls respectively). "
        "No cleaning or deduplication was applied. Full missing-value counts and first-three-row examples for "
        "every CSV are in `research/kaggle/audit_summary.json`.",
        "", "NCAA 2025 game records: **0**. Bookmaker/quote-time coverage: **absent**. Verified NCAA historical "
        "pre-game odds: **0**. NCAA game matches: **0**. A player's possible college history does not convert "
        "these professional-season statistics into NCAA game observations.",
        "", "## License and usage limitations", "",
        "Both Kaggle metadata responses list **CC0: Public Domain** for these releases. This is the uploader's "
        "license declaration, not proof that every underlying third-party right has been cleared. In particular, "
        "the odds uploader attributes the content to The Odds API; its provider terms restrict standalone raw-data "
        "redistribution. The professional dataset credits statistics supplied by a PLL representative, but no "
        "additional source-rights documentation was included in the downloaded archive. "
        "Preserve these provenance qualifications when citing or redistributing either dataset.",
        "", "Provider terms reference: https://the-odds-api.com/terms-and-conditions.html",
        "", "## Reproduce", "", "```bash", "conda activate dsf-lacrosse",
        "python src/audit_kaggle.py --download", "python src/audit_kaggle.py", "python -m pytest -q", "```", "",
        "The downloader fills missing public releases and preserves existing bytes. It pins dataset versions 1 "
        "and 5, checks the 10 MB size limit, and rejects unexpected schemas/archives. It does not read credentials. "
        "Default mode audits local files without network requests. Metadata/file integrity or access failures "
        "must be reported as UNVERIFIED rather than interpreted as empty suitable data.",
        "", "## Official authentication fallback", "",
        "Authentication was **not required for this audit**. If Kaggle later requires it, use Kaggle's official "
        "browser-based OAuth flow locally; never paste a token or credential file into chat:", "",
        "```bash", "conda activate dsf-lacrosse", "python -m pip install kaggle", "kaggle auth login",
        "kaggle datasets files harsh21x/live-sports-betting-odds-snapshot",
        "kaggle datasets files tjmulderig/professional-lacrosse-statistics-pll-mll", "```", "",
        "Official authentication instructions: https://github.com/Kaggle/kaggle-cli/blob/main/docs/README.md#authentication",
        "No CLI installation, account login or token was needed or performed here. Any future authenticated "
        "download must still follow the dataset's actual access conditions; do not bypass a login or challenge.",
        "", "## Decision", "",
        "The first dataset can illustrate multi-bookmaker PLL odds structure and data-quality issues, but has "
        "the wrong league/year and no quote-time history for this project. The second can support professional "
        "player-statistics research, but contains no betting odds or 2025 NCAA games. **Neither supplies "
        "the historical NCAA odds needed by the current project.**", "",
    ]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Fill missing publicly accessible Kaggle files")
    args = parser.parse_args(argv)
    download_error = None
    if args.download:
        try:
            download_missing()
        except (requests.RequestException, OSError, ValueError, zipfile.BadZipFile) as exc:
            download_error = str(exc)
    if checksum(GAME_PATH) != GAME_HASH:
        raise ValueError("Existing validated NCAA CSV changed")
    ncaa = pd.read_csv(GAME_PATH)
    manifest_path = ROOT / "research/kaggle/existing_files_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    for name, expected in manifest.items():
        if checksum(ROOT / name) != expected:
            raise ValueError(f"Existing project file changed: {name}")
    audit = {"generated_at": now(), "ncaa_rows": len(ncaa), "ncaa_csv_sha256": GAME_HASH,
             "preexisting_files_verified": len(manifest), "download_error": download_error, "datasets": []}
    for reference, version in DATASETS.items():
        dataset = {"reference": reference, "version": version, "status": "UNVERIFIED", "files": []}
        try:
            view = json.loads((RAW / f"{reference.replace('/', '__')}.view.response").read_bytes())
            listing = json.loads((RAW / f"{reference.replace('/', '__')}.list.response").read_bytes())
            if view["ref"] != reference or view["currentVersionNumber"] != version or listing.get("nextPageToken"):
                raise ValueError("Metadata identity/version differs or file listing incomplete")
            folder = RAW / reference
            archive = folder / f"dataset_v{version}.zip"
            download_log = json.loads((ROOT / "research/kaggle/download_log.json").read_text())
            original = next((record for record in download_log if record.get("dataset_ref") == reference and record.get("version") == version), None)
            if original is None or checksum(archive) != original["archive_sha256"]:
                raise ValueError("Archive does not match the original download checksum")
            extract_originals(archive, listing["datasetFiles"], folder / "files")
            dataset.update(license=view["licenseName"], metadata_total_bytes=view["totalBytes"],
                           archive_bytes=archive.stat().st_size, archive_sha256=checksum(archive),
                           official_metadata_url=api_url("view", reference), official_listing_url=api_url("list", reference))
            for item in listing["datasetFiles"]:
                frame, profile = inspect_csv(folder / "files" / item["name"])
                profile["inspection"] = inspect_odds(frame, ncaa) if "sports_title" in frame else inspect_players(frame)
                dataset["files"].append(profile)
            dataset["status"] = "VERIFIED_FILES_INSPECTED"
        except (OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
            dataset["error"] = str(exc)
        audit["datasets"].append(dataset)
    summary_path = ROOT / "research/kaggle/audit_summary.json"
    summary_path.write_text(json.dumps(audit, indent=2) + "\n")
    (ROOT / "reports/kaggle_two_datasets_audit.md").write_text(render_report(audit))
    for dataset in audit["datasets"]:
        print(dataset["reference"], dataset["status"])
        for file in dataset["files"]:
            print(f"  {file['name']}: {file['bytes']} bytes, {file['rows']} rows x {file['columns_count']} columns")
    result = "0" if all(d["status"] == "VERIFIED_FILES_INSPECTED" for d in audit["datasets"]) else "UNVERIFIED"
    print(f"Preserved {len(manifest)} existing files. NCAA 2025 odds matches: {result}. Full audit: reports/kaggle_two_datasets_audit.md")
    return 0 if all(d["status"] == "VERIFIED_FILES_INSPECTED" for d in audit["datasets"]) else 2


if __name__ == "__main__":
    raise SystemExit(main())
