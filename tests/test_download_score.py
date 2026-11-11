"""Local checks use the genuine downloaded file; no invented statistics."""

import csv
import hashlib
import io

import pytest
import requests

from src import download_score as score


@pytest.fixture
def raw_csv():
    assert score.DATA_PATH.is_file(), "Run python src/download_score.py first"
    return score.DATA_PATH.read_bytes()


def test_real_csv_matches_inventory(raw_csv):
    frame = score.validate_csv(raw_csv, "text/csv")
    report = score.REPORT_PATH.read_text(encoding="utf-8")
    assert "Collection status: SUCCESS" in report
    assert f"Actual row count: {len(frame)}" in report
    assert f"Actual column count: {len(frame.columns)}" in report
    assert f"Total missing cells (pandas default NA recognition): {int(frame.isna().sum().sum())}" in report
    assert hashlib.sha256(raw_csv).hexdigest() in report


@pytest.mark.parametrize("content_type", ["text/html", "text/csv"])
def test_rejects_html_even_if_mislabeled(content_type):
    with pytest.raises(ValueError):
        score.validate_csv(b"<!DOCTYPE html><html>Access denied</html>", content_type)


def test_rejects_wrong_dataset_schema():
    with pytest.raises(ValueError, match="Unexpected dataset schema"):
        score.validate_csv(b"error,message\n", "text/csv")


def test_rejects_truncated_csv_record(raw_csv):
    rows = list(csv.reader(io.StringIO(raw_csv.decode("utf-8-sig"))))
    rows[1] = rows[1][:-1]
    buffer = io.StringIO()
    csv.writer(buffer).writerows(rows)
    with pytest.raises(ValueError, match="fields; expected"):
        score.validate_csv(buffer.getvalue().encode(), "text/csv")


def test_uses_exact_publisher_link():
    html = f'<a href="../data/{score.FILENAME}">Download</a>'
    assert score.find_download_url(html) == f"https://data.scorenetwork.org/data/{score.FILENAME}"
    with pytest.raises(ValueError, match="found 0"):
        score.find_download_url('<a href="other.csv">Other dataset</a>')


def test_robots_denial_prevents_dataset_request(monkeypatch):
    client = score.PublicDownloader()
    response = requests.Response()
    response.status_code = 200
    response._content = b"User-agent: *\nDisallow: /\n"
    calls = []

    def get(url, **kwargs):
        calls.append(url)
        return response

    monkeypatch.setattr(client.session, "get", get)
    with pytest.raises(ValueError, match="robots.txt disallows"):
        client.get(score.SOURCE_URL)
    assert calls == ["https://data.scorenetwork.org/robots.txt"]
    client.session.close()


def test_failed_download_records_status_and_preserves_existing_file(monkeypatch, tmp_path, raw_csv):
    data = tmp_path / score.FILENAME
    data.write_bytes(raw_csv)
    report = tmp_path / "reports/data_inventory.md"
    monkeypatch.setattr(score, "ROOT", tmp_path)
    monkeypatch.setattr(score, "DATA_PATH", data)
    monkeypatch.setattr(score, "REPORT_PATH", report)

    def get(self, url):
        response = requests.Response()
        if url == score.SOURCE_URL:
            response.status_code = 200
            response._content = f'<a href="/data/{score.FILENAME}">Download</a>'.encode()
            return response
        response.status_code = 429
        raise requests.HTTPError("HTTP 429: rate limited", response=response)

    monkeypatch.setattr(score.PublicDownloader, "get", get)
    assert score.main() == 1
    assert data.read_bytes() == raw_csv
    inventory = report.read_text(encoding="utf-8")
    assert "Collection status: FAILED" in inventory
    assert "CSV HTTP response status: 429" in inventory
    assert "Manual alternative:" in inventory
