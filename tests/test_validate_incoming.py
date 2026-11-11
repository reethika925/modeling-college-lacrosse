"""TEST ONLY: synthetic validator fixtures, never research observations."""

import hashlib
import json
from pathlib import Path

import pytest
import requests

from src import validate_incoming as validator
from src.research_integrity import assert_research_snapshot

FIXTURES = Path(__file__).parent / "fixtures/grok_import_synthetic"
SCHEMA = json.loads((FIXTURES / "schema.json").read_text())


def test_valid_synthetic_csv_stays_unverified_and_byte_identical():
    path = FIXTURES / "valid.csv"
    original = path.read_bytes()
    checksum = hashlib.sha256(original).hexdigest()
    result = validator.inspect_csv(path, schema=SCHEMA, expected_sha256=checksum)
    assert result["automated_status"] == "PASS"
    assert result["trust_status"] == "UNVERIFIED" and result["import_approved"] is False
    assert result["checksum_comparison"] == "MATCH"
    assert result["sha256_before"] == result["sha256_after"] == checksum
    assert result["input_unchanged_during_check"] and path.read_bytes() == original
    assert result["data_rows_seen"] == result["rows_with_valid_width"] == 2
    assert result["column_count"] == 6 and result["parsing_complete"]
    assert result["missing_by_column"]["notes"] == 1
    assert result["date_checks"]["captured_at"]["valid"] == 2
    assert result["source_url_checks"]["source_url"]["valid_syntax"] == 2


def test_invalid_synthetic_csv_reports_failures_without_repair():
    path = FIXTURES / "invalid.csv"
    before = path.read_bytes()
    result = validator.inspect_csv(path, schema=SCHEMA)
    assert result["automated_status"] == "FAIL"
    assert result["data_rows_seen"] == 4 and result["rows_with_valid_width"] == 3
    assert result["malformed_width_rows"] == 1
    assert result["duplicate_full_rows_extra"] == result["duplicate_key_rows_extra"] == 1
    assert result["missing_key_rows"] == 1
    assert result["missing_by_column"]["measurement"] == 3
    assert result["date_checks"]["event_date"]["invalid"] == 3
    assert result["date_checks"]["captured_at"]["invalid"] == 2
    assert result["source_url_checks"]["source_url"]["invalid"] == 2
    assert result["source_url_checks"]["source_url"]["missing"] == 1
    assert path.read_bytes() == before


@pytest.mark.parametrize("content", [
    "", "record_id,record_id\nSYNTHETIC_001,SYNTHETIC_002\n",
    "record_id, Record_ID\nSYNTHETIC_001,SYNTHETIC_002\n",
    ",event_date\nSYNTHETIC_001,2025-02-01\n",
    "<html><body>TEST_ONLY error page</body></html>",
    "<?xml version='1.0'?><error>TEST_ONLY</error>",
    'record_id,notes\nSYNTHETIC_001,"TEST_ONLY unclosed quote\n',
])
def test_bad_csv_structure_fails(tmp_path, content):
    path = tmp_path / "synthetic_bad.csv"
    path.write_text(content)
    before = path.read_bytes()
    result = validator.inspect_csv(path)
    assert result["automated_status"] == "FAIL"
    assert result["errors"] and path.read_bytes() == before


def test_utf8_bom_quoted_commas_multiline_and_leading_zero_ids_are_preserved(tmp_path):
    path = tmp_path / "synthetic_quoted.csv"
    data = '\ufeffrecord_id,notes\r\n0001,"TEST_ONLY, first\nsecond"\r\n0002,TEST_ONLY\r\n'
    path.write_bytes(data.encode("utf-8"))
    result = validator.inspect_csv(path, schema={"unique_key": ["record_id"]})
    assert result["automated_status"] == "PASS"
    assert result["columns"] == ["record_id", "notes"]
    assert result["data_rows_seen"] == 2 and result["duplicate_key_rows_extra"] == 0
    assert path.read_bytes() == data.encode("utf-8")


def test_invalid_utf8_is_not_silently_replaced(tmp_path):
    path = tmp_path / "synthetic_encoding.csv"
    data = b"record_id,notes\nSYNTHETIC_001,\xff\n"
    path.write_bytes(data)
    result = validator.inspect_csv(path)
    assert result["automated_status"] == "FAIL" and not result["parsing_complete"]
    assert path.read_bytes() == data


@pytest.mark.parametrize("value,spec,expected", [
    ("2024-02-29", "ISO_DATE", True), ("2025-02-29", "ISO_DATE", False),
    ("2025-2-01", "ISO_DATE", False), ("02/01/2025", "ISO_DATE", False),
    ("02/01/2025", "%m/%d/%Y", True),
    ("2025-02-01T12:00:00Z", "ISO_DATETIME", True),
    ("2025-02-01T12:00:00-05:00", "ISO_DATETIME", True),
    ("2025-02-01T12:00:00", "ISO_DATETIME", False),
    ("2025-02-01T12:00:00+99:00", "ISO_DATETIME", False),
])
def test_explicit_date_formats_and_timezone_requirements(value, spec, expected):
    assert validator.valid_date(value, spec) is expected


@pytest.mark.parametrize("value,expected", [
    ("https://example.invalid/synthetic-only", True), ("http://example.invalid", True),
    ("javascript:TEST_ONLY", False), ("file:///tmp/synthetic.csv", False),
    ("https:///synthetic-only", False), ("https://example.invalid:bad", False),
    ("https://name:TEST_ONLY@example.invalid", False),
    ("https://example.invalid/test only", False), ("", False),
])
def test_url_syntax_without_asserting_a_real_provider(value, expected):
    assert validator.valid_url(value) is expected


def test_schema_missing_columns_and_required_nulls_are_errors():
    result = validator.inspect_csv(FIXTURES / "valid.csv", schema={"required_columns": ["synthetic_missing_column"]})
    assert result["automated_status"] == "FAIL"
    assert any("Configured columns absent" in error for error in result["errors"])
    result = validator.inspect_csv(FIXTURES / "valid.csv", schema={"non_nullable": ["notes"]})
    assert result["automated_status"] == "FAIL"


def test_composite_keys_allow_multiple_observations_for_one_identifier(tmp_path):
    path = tmp_path / "synthetic_repeated_id.csv"
    path.write_text("record_id,version\nSYNTHETIC_001,1\nSYNTHETIC_001,2\n")
    result = validator.inspect_csv(path, schema={"unique_key": ["record_id", "version"]})
    assert result["automated_status"] == "PASS" and result["duplicate_key_rows_extra"] == 0
    result = validator.inspect_csv(path, schema={"unique_key": ["record_id"]})
    assert result["automated_status"] == "FAIL" and result["duplicate_key_rows_extra"] == 1


def test_checksum_mismatch_fails_and_invalid_expected_hash_is_rejected():
    result = validator.inspect_csv(FIXTURES / "valid.csv", expected_sha256="0" * 64)
    assert result["checksum_comparison"] == "MISMATCH" and result["automated_status"] == "FAIL"
    with pytest.raises(ValueError, match="64 hexadecimal"):
        validator.inspect_csv(FIXTURES / "valid.csv", expected_sha256="TEST_ONLY")


def test_input_change_during_validation_is_detected(monkeypatch):
    checksums = iter(["0" * 64, "1" * 64])
    monkeypatch.setattr(validator, "sha256", lambda path: next(checksums))
    result = validator.inspect_csv(FIXTURES / "valid.csv", schema=SCHEMA)
    assert result["automated_status"] == "FAIL"
    assert result["input_unchanged_during_check"] is False


def test_no_network_or_source_writes_are_attempted(monkeypatch, capsys):
    def forbidden(*args, **kwargs):
        pytest.fail("Incoming validator must never contact a website")
    monkeypatch.setattr(requests.sessions.Session, "request", forbidden)
    original_open = Path.open
    def readonly(self, mode="r", *args, **kwargs):
        assert not any(flag in mode for flag in "wax+"), "Unexpected write without --report"
        return original_open(self, mode, *args, **kwargs)
    monkeypatch.setattr(Path, "open", readonly)
    assert validator.main([str(FIXTURES / "valid.csv"), "--schema", str(FIXTURES / "schema.json")]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["import_approved"] is False


def test_cli_creates_only_a_new_report_and_refuses_overwriting(tmp_path, capsys):
    report_path = tmp_path / "synthetic_report.json"
    args = [str(FIXTURES / "valid.csv"), "--schema", str(FIXTURES / "schema.json"), "--report", str(report_path)]
    assert validator.main(args) == 0
    before = report_path.read_bytes()
    capsys.readouterr()
    assert validator.main(args) == 2
    assert report_path.read_bytes() == before
    capsys.readouterr()
    source = FIXTURES / "valid.csv"
    original = source.read_bytes()
    assert validator.main([str(source), "--report", str(source)]) == 2
    assert source.read_bytes() == original


def test_existing_report_symlink_cannot_modify_an_input(tmp_path, capsys):
    source = FIXTURES / "valid.csv"
    report = tmp_path / "synthetic_symlink.json"
    report.symlink_to(source.resolve())
    before = source.read_bytes()
    assert validator.main([str(source), "--report", str(report)]) == 2
    assert source.read_bytes() == before


def test_directory_scan_reports_each_csv_and_failure_exit_status(capsys):
    assert validator.main([str(FIXTURES), "--schema", str(FIXTURES / "schema.json")]) == 1
    result = json.loads(capsys.readouterr().out)
    assert result["csv_files_checked"] == 2 and result["failed_files"] == 1
    assert result["trust_status"] == "UNVERIFIED"


def test_empty_directory_never_reports_success(tmp_path, capsys):
    assert validator.main([str(tmp_path)]) == 2
    assert "No CSV files found" in capsys.readouterr().err


def test_all_preexisting_project_files_are_unchanged():
    root = Path(__file__).resolve().parents[1]
    protected = json.loads((root / "reports/grok_import_existing_checksums.json").read_text())
    assert_research_snapshot(root, protected)
