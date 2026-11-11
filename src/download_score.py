"""Download and audit the publisher's men's lacrosse team-season CSV only."""

from __future__ import annotations

import csv
import hashlib
import io
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from urllib.robotparser import RobotFileParser
from zoneinfo import ZoneInfo

import pandas as pd
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = "https://data.scorenetwork.org/lacrosse/lacrosse_ncaa_div1.html"
FILENAME = "lacrosse_men_ncaa_div1_2022_2023.csv"
DATA_PATH = ROOT / "data/raw/score" / FILENAME
REPORT_PATH = ROOT / "reports/data_inventory.md"
USER_AGENT = "CSE519-Lacrosse-Data/1.0"
EXPECTED_SHAPE = (72, 22)
REQUIRED_COLUMNS = {"Team", "W", "L", "faceoff_win_pct"}


class PublicDownloader:
    """Check robots.txt, honor request spacing, and stop on HTTP errors."""

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        self.policies: dict[str, RobotFileParser] = {}
        self.last_request: dict[str, float] = {}
        self.robots_status: dict[str, int] = {}

    def get(self, url: str) -> requests.Response:
        parts = urlsplit(url)
        origin = f"{parts.scheme}://{parts.netloc}"
        if parts.scheme != "https" or origin != "https://data.scorenetwork.org":
            raise ValueError(f"Unexpected download host or protocol: {url}")
        if origin not in self.policies:
            robots_url = origin + "/robots.txt"
            response = self.session.get(robots_url, timeout=30, allow_redirects=False)
            self.robots_status[robots_url] = response.status_code
            policy = RobotFileParser(robots_url)
            if response.status_code in (404, 410):
                policy.parse([])  # No published policy at this URL.
            elif response.status_code == 200:
                policy.parse(response.text.splitlines())
            else:
                raise ValueError(f"Cannot establish robots.txt permission: HTTP {response.status_code}")
            self.policies[origin] = policy
            self.last_request[origin] = time.monotonic()
        policy = self.policies[origin]
        if not policy.can_fetch(USER_AGENT, url):
            raise ValueError(f"robots.txt disallows {url}")
        delay = max(1, policy.crawl_delay(USER_AGENT) or 0)
        rate = policy.request_rate(USER_AGENT)
        if rate:
            # Conservative spacing also respects published request-rate windows.
            delay = max(delay, rate.seconds)
        time.sleep(max(0, delay - (time.monotonic() - self.last_request[origin])))
        response = self.session.get(url, timeout=30, allow_redirects=False)
        self.last_request[origin] = time.monotonic()
        # Stop on redirects too; never follow an unchecked destination.
        if response.status_code != 200:
            raise requests.HTTPError(f"HTTP {response.status_code} for {url}", response=response)
        return response


def find_download_url(html: str) -> str:
    """Use the exact men's CSV link on the source page; never substitute data."""
    soup = BeautifulSoup(html, "html.parser")
    links = {
        urljoin(SOURCE_URL, anchor["href"])
        for anchor in soup.find_all("a", href=True)
        if Path(urlsplit(urljoin(SOURCE_URL, anchor["href"])).path).name == FILENAME
    }
    if len(links) != 1:
        raise ValueError(f"Expected one unique link to {FILENAME}; found {len(links)}")
    url = links.pop()
    if urlsplit(url).netloc != "data.scorenetwork.org":
        raise ValueError(f"Unexpected publisher link: {url}")
    return url


def validate_csv(content: bytes, content_type: str) -> pd.DataFrame:
    """Reject HTML/error bodies and malformed rows before saving any raw bytes."""
    if any(kind in content_type.lower() for kind in ("html", "json", "xml")):
        raise ValueError(f"Expected CSV; received Content-Type {content_type!r}")
    decoded = content.decode("utf-8-sig")
    if not decoded.strip() or decoded.lstrip().startswith("<"):
        raise ValueError("Response is empty or contains markup instead of CSV")
    reader = csv.reader(io.StringIO(decoded), strict=True)
    header = next(reader)
    if len(header) != len(set(header)) or any(not name.strip() for name in header):
        raise ValueError("CSV has blank or duplicate column names")
    if not REQUIRED_COLUMNS.issubset(header):
        raise ValueError(f"Unexpected dataset schema: missing {sorted(REQUIRED_COLUMNS - set(header))}")
    for line, row in enumerate(reader, start=2):
        if len(row) != len(header):
            raise ValueError(f"CSV record {line} has {len(row)} fields; expected {len(header)}")
    frame = pd.read_csv(io.BytesIO(content), encoding="utf-8-sig")
    if frame.empty:
        raise ValueError("CSV contains no data rows")
    return frame


def write_inventory(metadata: dict, frame: pd.DataFrame | None, error: str | None) -> None:
    """Always record this attempt, including a useful report if collection fails."""
    lines = [
        "# Data inventory", "",
        "- Dataset: NCAA Division I Men's Lacrosse 2022–2023 team-season statistics (SCORE)",
        f"- Source webpage: {SOURCE_URL}",
        f"- Exact download URL: {metadata.get('download_url', 'Not resolved from publisher page')}",
        f"- Collection attempt (America/New_York): {metadata['attempted_at']}",
        f"- Date downloaded (America/New_York): {metadata.get('downloaded_at', 'Not downloaded')}",
        f"- Local file path: `{DATA_PATH.relative_to(ROOT).as_posix()}`",
        f"- Source page HTTP status: {metadata.get('source_status', 'Not received')}",
        f"- CSV HTTP response status: {metadata.get('csv_status', 'Not received')}",
        f"- CSV Content-Type: `{metadata.get('content_type', 'Not received')}`",
        f"- Robots.txt HTTP status: {metadata.get('robots_status', {})}",
        f"- Collection status: {'FAILED' if error else 'SUCCESS'}",
        f"- SHA-256 (raw file bytes): `{metadata.get('sha256', 'Not available')}`",
        f"- Downloaded size in bytes: {metadata.get('bytes', 'Not available')}",
        "",
    ]
    if frame is not None:
        missing = frame.isna().sum()
        lines += [
            f"- Actual row count: {len(frame)}",
            f"- Actual column count: {len(frame.columns)}",
            f"- Fully duplicate rows: {int(frame.duplicated().sum())}",
            f"- Total missing cells (pandas default NA recognition): {int(missing.sum())}",
            f"- Rows with at least one missing value: {int(frame.isna().any(axis=1).sum())}",
            f"- Publisher reports 72 rows and 22 columns; actual dimensions match: {frame.shape == EXPECTED_SHAPE}",
            "", "## Column names and missing values", "",
            "| Column | Missing cells |", "| --- | ---: |",
        ]
        lines += [f"| `{column}` | {int(missing[column])} |" for column in frame.columns]
        if frame.shape != EXPECTED_SHAPE:
            lines += [
                "", f"Dimension discrepancy: the publisher reports 72 × 22, but the linked CSV "
                f"contains {frame.shape[0]} × {frame.shape[1]}. All downloaded columns are preserved; "
                "the webpage's dimension description may be outdated.",
            ]
    else:
        lines += ["- Row count, column count, column names, missing values, duplicates: unavailable (validation did not complete)."]
    if error:
        lines += [
            "", "## Collection failure", "", error, "",
            "Any existing CSV from an earlier run is preserved; it does not indicate success for this attempt.",
            "Manual alternative: open the source webpage in a browser, click the men's CSV link, "
            f"and save it as `{DATA_PATH.relative_to(ROOT).as_posix()}`. "
            "Honor access restrictions and rate limits; do not save an error page as CSV. "
            "Use the README's local validation command afterward.",
        ]
    lines += [
        "", "## Provenance and known limitations", "",
        "- Each record is a team-season aggregate, not an individual game. "
        "There are no game dates, opponents, game scores, or sportsbook odds in this collection.",
        "- The publisher labels the coverage 2022–2023. The file itself has no season/year field; "
        "do not infer that it contains separate observations for both calendar years.",
        "- The publisher credits Jack Fay, A.J. Dykstra, and Ivan Ramler (published July 24, 2023), "
        "and identifies NCAA statistics as its underlying source. This download is from SCORE, not directly from NCAA.",
        "- Raw bytes are preserved without imputation, deduplication, or statistics corrections. "
        "Missing values and duplicate rows are reported, not silently changed.",
        "- A successful CSV/schema check verifies format and basic identity, not the accuracy of every statistic. "
        "The publisher may revise the file; the checksum identifies this exact download.",
        "- This task collects only the linked men's dataset. No models, additional seasons, or odds have been collected.",
        "",
    ]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    metadata = {"attempted_at": datetime.now(ZoneInfo("America/New_York")).isoformat(timespec="seconds")}
    client = PublicDownloader()
    frame = None
    try:
        source = client.get(SOURCE_URL)
        metadata["source_status"] = source.status_code
        metadata["download_url"] = find_download_url(source.text)
        response = client.get(metadata["download_url"])
        metadata.update(csv_status=response.status_code, content_type=response.headers.get("Content-Type", ""))
        frame = validate_csv(response.content, metadata["content_type"])
        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        temporary = DATA_PATH.with_suffix(".csv.part")
        temporary.write_bytes(response.content)
        temporary.replace(DATA_PATH)
        saved_bytes = DATA_PATH.read_bytes()
        if saved_bytes != response.content:
            raise ValueError("Saved bytes do not match downloaded bytes")
        metadata.update(
            downloaded_at=datetime.now(ZoneInfo("America/New_York")).isoformat(timespec="seconds"),
            sha256=hashlib.sha256(saved_bytes).hexdigest(),
            bytes=len(saved_bytes),
        )
    except (requests.RequestException, ValueError, OSError, csv.Error) as exc:
        if isinstance(exc, requests.HTTPError) and exc.response is not None:
            key = "csv_status" if "download_url" in metadata else "source_status"
            metadata[key] = exc.response.status_code
        metadata["robots_status"] = client.robots_status
        write_inventory(metadata, frame, str(exc))
        print(f"FAILED: {exc}\nSee {REPORT_PATH} for the manual alternative.", file=sys.stderr)
        return 1
    finally:
        client.session.close()
    metadata["robots_status"] = client.robots_status
    write_inventory(metadata, frame, None)
    print(f"SUCCESS: {DATA_PATH}\nHTTP status: {metadata['csv_status']}")
    print(f"Rows: {len(frame)}; columns: {len(frame.columns)}")
    print("Column names:", frame.columns.tolist())
    print("\nFirst five rows:\n" + frame.head().to_string(index=False))
    print("\nMissing values by column:\n" + frame.isna().sum().to_string())
    print(f"Total missing cells: {int(frame.isna().sum().sum())}")
    print(f"Fully duplicate rows: {int(frame.duplicated().sum())}")
    print(f"Publisher dimensions match: {frame.shape == EXPECTED_SHAPE}")
    print(f"SHA-256: {metadata['sha256']}")
    print(f"Inventory: {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
