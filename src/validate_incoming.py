"""Read-only local CSV checks. Mechanical validity never approves an import.

Python 3.11 standard library only. No network, source edits, repairs, moves,
deduplication, inferred team matching, or changes to existing reports/results.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

DEFAULT_NULLS = ["", "NA", "N/A", "NULL", "NONE", "NAN"]
LIST_OPTIONS = {"expected_columns", "required_columns", "non_nullable", "unique_key", "source_url_columns", "null_tokens"}
SCHEMA_OPTIONS = LIST_OPTIONS | {"date_columns", "dataset_source_url"}


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_schema(schema):
    if not isinstance(schema, dict) or set(schema) - SCHEMA_OPTIONS:
        raise ValueError("Schema must be an object containing only documented options")
    for option in LIST_OPTIONS & schema.keys():
        values = schema[option]
        if not isinstance(values, list) or not all(isinstance(v, str) for v in values) or len(values) != len(set(values)):
            raise ValueError(f"{option} must be a list of distinct strings")
    dates = schema.get("date_columns", {})
    if not isinstance(dates, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in dates.items()):
        raise ValueError("date_columns must map column names to format strings")
    for spec in dates.values():
        if spec not in {"ISO_DATE", "ISO_DATETIME"} and "%" not in spec:
            raise ValueError("Use ISO_DATE, ISO_DATETIME, or an explicit strptime format")
    if "dataset_source_url" in schema and not isinstance(schema["dataset_source_url"], str):
        raise ValueError("dataset_source_url must be a string")


def valid_url(value):
    """Syntax only: never request, resolve, or certify the URL's provenance."""
    if not value or any(char.isspace() or ord(char) < 32 or ord(char) == 127 for char in value):
        return False
    try:
        parts = urlsplit(value)
        if parts.scheme not in {"http", "https"} or not parts.hostname or parts.username is not None or parts.password is not None:
            return False
        parts.port  # Raises for malformed/out-of-range ports.
        host = parts.hostname.encode("idna").decode("ascii")
        return bool(re.fullmatch(r"[A-Za-z0-9.:-]+", host))
    except (ValueError, UnicodeError):
        return False


def valid_date(value, spec):
    try:
        if spec == "ISO_DATE":
            return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value)) and bool(date.fromisoformat(value))
        if spec == "ISO_DATETIME":
            # Require an explicit UTC Z or numeric offset; never invent a timezone.
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})", value):
                return False
            return datetime.fromisoformat(value.replace("Z", "+00:00")).utcoffset() is not None
        parsed = datetime.strptime(value, spec)
        return parsed.strftime(spec) == value
    except (ValueError, OverflowError):
        return False


def discover_dates(columns):
    result = {}
    for name in columns:
        lower = name.casefold()
        if "timestamp" in lower or "datetime" in lower or lower.endswith("_at"):
            result[name] = "ISO_DATETIME"
        elif lower == "date" or lower.endswith("_date"):
            result[name] = "ISO_DATE"
    return result


def inspect_csv(path, *, schema=None, expected_sha256=None, delimiter=","):
    """Return an audit dict; all reads preserve bytes and original cell strings."""
    path = Path(path).resolve()
    supplied_schema = schema is not None
    schema = {} if schema is None else schema
    validate_schema(schema)
    if len(delimiter) != 1 or delimiter in {"\r", "\n", '"'}:
        raise ValueError("Delimiter must be one supported character")
    if expected_sha256 is not None and not re.fullmatch(r"[0-9a-fA-F]{64}", expected_sha256):
        raise ValueError("Expected SHA-256 must be exactly 64 hexadecimal characters")
    before = sha256(path)
    result = {
        "file": str(path), "file_bytes": path.stat().st_size,
        "sha256_before": before, "sha256_after": None, "input_unchanged_during_check": None,
        "expected_sha256": expected_sha256.lower() if expected_sha256 else None,
        "checksum_comparison": "NOT_PROVIDED", "schema_supplied": supplied_schema,
        "encoding": "utf-8-sig (strict)", "delimiter": delimiter,
        "columns": [], "column_count": 0, "data_rows_seen": 0, "rows_with_valid_width": 0,
        "blank_records": 0, "malformed_width_rows": 0, "parsing_complete": False,
        "duplicate_full_rows_extra": 0, "duplicate_key_rows_extra": 0, "missing_key_rows": 0,
        "unique_key": schema.get("unique_key", []), "missing_by_column": {},
        "date_checks": {}, "source_url_checks": {}, "errors": [], "warnings": [],
        "trust_status": "UNVERIFIED", "import_approved": False,
        "recommended_action": "Hold for independent provenance, permissions and domain review",
    }
    errors, warnings = result["errors"], result["warnings"]
    if expected_sha256:
        result["checksum_comparison"] = "MATCH" if before == expected_sha256.lower() else "MISMATCH"
        if result["checksum_comparison"] == "MISMATCH":
            errors.append("SHA-256 disagrees with expected checksum")
    else:
        warnings.append("Checksum computed only; no independently obtained expected hash supplied")
    if not supplied_schema:
        warnings.append("No reviewed schema supplied; date/URL column discovery is provisional")
    if not schema.get("unique_key"):
        warnings.append("No unique key configured; only full-row duplication is assessed")
    if not schema.get("expected_columns"):
        warnings.append("Complete expected column list not configured")
    nulls = {token.strip().casefold() for token in schema.get("null_tokens", DEFAULT_NULLS)} | {""}
    required_nonnull = set(schema.get("non_nullable", []))
    seen_rows, seen_keys = set(), set()
    dataset_url = schema.get("dataset_source_url")
    if dataset_url is not None:
        result["dataset_source_url_syntax_valid"] = valid_url(dataset_url)
        if not valid_url(dataset_url):
            errors.append("Dataset-level source URL is missing or has invalid HTTP(S) syntax")
    try:
        with path.open("r", encoding="utf-8-sig", errors="strict", newline="") as handle:
            prefix = handle.read(2048).lstrip().casefold()
            handle.seek(0)
            if prefix.startswith(("<!doctype html", "<html", "<head", "<body", "<?xml")):
                errors.append("HTML/XML content detected instead of CSV")
            else:
                reader = csv.reader(handle, delimiter=delimiter, strict=True)
                columns = next(reader, [])
                result.update(columns=columns, column_count=len(columns))
                invalid_header = not columns or any(not name.strip() for name in columns)
                invalid_header |= len(set(name.strip().casefold() for name in columns)) != len(columns)
                if invalid_header:
                    errors.append("Missing, blank or duplicate/ambiguous header names")
                elif any(name != name.strip() for name in columns):
                    errors.append("Header names contain surrounding whitespace; not renamed automatically")
                if not invalid_header:
                    if schema.get("expected_columns") is not None and columns != schema["expected_columns"]:
                        errors.append("Column names/order differ from expected_columns")
                    date_specs = schema.get("date_columns", discover_dates(columns))
                    url_columns = schema.get("source_url_columns", [name for name in columns if name.casefold() == "url" or name.casefold().endswith("_url")])
                    referenced = set(schema.get("required_columns", [])) | required_nonnull | set(result["unique_key"]) | set(date_specs) | set(url_columns)
                    if referenced - set(columns):
                        errors.append(f"Configured columns absent: {sorted(referenced - set(columns))}")
                    if not date_specs:
                        warnings.append("No date columns assessed; applicability/format requires human review")
                    if not url_columns and dataset_url is None:
                        warnings.append("No record-level or dataset-level source URL assessed")
                    result["missing_by_column"] = dict.fromkeys(columns, 0)
                    result["date_checks"] = {name: {"format": spec, "valid": 0, "missing": 0, "invalid": 0, "invalid_line_examples": []} for name, spec in date_specs.items() if name in columns}
                    result["source_url_checks"] = {name: {"valid_syntax": 0, "missing": 0, "invalid": 0, "invalid_line_examples": []} for name in url_columns if name in columns}
                    for row in reader:
                        if not row:
                            result["blank_records"] += 1
                            continue
                        result["data_rows_seen"] += 1
                        if len(row) != len(columns):
                            result["malformed_width_rows"] += 1
                            continue
                        result["rows_with_valid_width"] += 1
                        cells = dict(zip(columns, row))
                        missing = {name for name, value in cells.items() if value.strip().casefold() in nulls}
                        for name in missing:
                            result["missing_by_column"][name] += 1
                        # Hash the parsed row with unambiguous serialization; no cell normalization.
                        fingerprint = hashlib.sha256(json.dumps(row, ensure_ascii=False).encode("utf-8")).digest()
                        result["duplicate_full_rows_extra"] += int(fingerprint in seen_rows)
                        seen_rows.add(fingerprint)
                        keys = result["unique_key"]
                        if keys and set(keys).issubset(cells):
                            if set(keys) & missing:
                                result["missing_key_rows"] += 1
                            else:
                                key = tuple(cells[name] for name in keys)
                                result["duplicate_key_rows_extra"] += int(key in seen_keys)
                                seen_keys.add(key)
                        for name, stats in result["date_checks"].items():
                            outcome = "missing" if name in missing else "valid" if valid_date(cells[name], stats["format"]) else "invalid"
                            stats[outcome] += 1
                            if outcome == "invalid" and len(stats["invalid_line_examples"]) < 5:
                                stats["invalid_line_examples"].append(reader.line_num)
                        for name, stats in result["source_url_checks"].items():
                            outcome = "missing" if name in missing else "valid_syntax" if valid_url(cells[name]) else "invalid"
                            stats[outcome] += 1
                            if outcome == "invalid" and len(stats["invalid_line_examples"]) < 5:
                                stats["invalid_line_examples"].append(reader.line_num)
                    result["parsing_complete"] = True
    except (UnicodeError, csv.Error) as exc:
        # Do not include data values in error messages or guess a replacement encoding.
        errors.append(f"CSV decoding/parsing failed ({type(exc).__name__}); counts may be partial")
    if result["data_rows_seen"] == 0:
        errors.append("No data records parsed")
    for field in ("malformed_width_rows", "duplicate_full_rows_extra", "duplicate_key_rows_extra", "missing_key_rows"):
        if result[field]:
            errors.append(f"{field}: {result[field]}")
    if result["blank_records"]:
        warnings.append(f"Blank CSV records present: {result['blank_records']}; counted, not removed")
    for name in required_nonnull:
        if result["missing_by_column"].get(name, 0):
            errors.append(f"Required non-null column has missing cells: {name}")
    for name, stats in {**result["date_checks"], **result["source_url_checks"]}.items():
        if stats["invalid"]:
            errors.append(f"Invalid date or URL format in column: {name}")
        if stats["missing"]:
            warnings.append(f"Missing date/URL values in column: {name}")
    after = sha256(path)
    result.update(sha256_after=after, input_unchanged_during_check=before == after)
    if before != after:
        errors.append("Input changed during validation; discard this report and investigate")
    result["automated_status"] = "FAIL" if errors else "PASS"
    if errors:
        result["recommended_action"] = "Quarantine review recommended; preserve original and investigate failures"
    result["limitations"] = [
        "PASS covers the reported mechanical checks only; import_approved always remains false.",
        "Source URL checks are syntactic only; no network/DNS request or independent source verification occurs.",
        "Neither checksums nor valid CSV establish authenticity, licensing, competition, date truth or pre-game availability.",
        "Missing counts cover valid-width rows only; parsing failures can leave partial counts.",
        "Duplicate checks use exact parsed strings; no fuzzy matching, alias resolution or within-day ordering is inferred.",
    ]
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path, help="CSV files or directories (recursively find *.csv)")
    parser.add_argument("--schema", type=Path, help="Reviewed JSON schema; see checklist for fields")
    parser.add_argument("--expected-sha256", help="Expected original-file SHA-256; single input CSV only")
    parser.add_argument("--delimiter", default=",", help="Single delimiter character; default comma")
    parser.add_argument("--report", type=Path, help="Create a NEW JSON report; never overwrite an existing path")
    args = parser.parse_args(argv)
    try:
        schema = json.loads(args.schema.read_text(encoding="utf-8")) if args.schema else None
        if schema is not None:
            validate_schema(schema)
        paths = set()
        for supplied in args.inputs:
            if supplied.is_dir():
                paths.update(path.resolve() for path in supplied.rglob("*") if path.is_file() and path.suffix.casefold() == ".csv")
            elif supplied.is_file() and supplied.suffix.casefold() == ".csv":
                paths.add(supplied.resolve())
            else:
                raise ValueError("Every input must be an existing CSV file or directory")
        if not paths:
            raise ValueError("No CSV files found; nothing validated")
        if args.expected_sha256 and len(paths) != 1:
            raise ValueError("--expected-sha256 requires exactly one input CSV")
        if args.report and args.report.exists():
            raise ValueError("Report path already exists; choose a new filename")
        files = [inspect_csv(path, schema=schema, expected_sha256=args.expected_sha256, delimiter=args.delimiter) for path in sorted(paths)]
        report = {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "trust_status": "UNVERIFIED", "import_approved": False,
            "csv_files_checked": len(files), "failed_files": sum(f["automated_status"] == "FAIL" for f in files),
            "schema_sha256": sha256(args.schema) if args.schema else None,
            "files": files,
        }
        encoded = json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
        if args.report:
            # Exclusive creation also rejects symlinks/hard links to existing inputs.
            with args.report.open("x", encoding="utf-8") as handle:
                handle.write(encoded)
        print(encoded, end="")
        return 1 if report["failed_files"] else 0
    except (OSError, ValueError) as exc:
        print(f"Validation could not complete: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
