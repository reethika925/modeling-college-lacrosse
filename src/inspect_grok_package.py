"""Offline ZIP preflight and exclusive extraction; no packaged code is executed."""

import argparse
import csv
import hashlib
import json
import stat
import unicodedata
import zipfile
from pathlib import Path, PureWindowsPath

MAX_MEMBERS = 10_000
MAX_TOTAL_BYTES = 1024 ** 3
MAX_MEMBER_BYTES = 256 * 1024 ** 2


def sha256(path):
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def check_members(members):
    """Reject traversal, links, ambiguous names, collisions and excessive sizes."""
    if not members or len(members) > MAX_MEMBERS:
        raise ValueError("Empty archive or excessive member count")
    total, names, files = 0, {}, set()
    for member in members:
        original = member.orig_filename
        name = member.filename
        if original != name or any(ord(char) < 32 or ord(char) == 127 for char in original):
            raise ValueError("Control characters or truncated member name")
        if name.startswith(("/", "\\")) or "\\" in name or PureWindowsPath(name).drive:
            raise ValueError("Absolute, Windows-drive or backslash path")
        parts = name.rstrip("/").split("/")
        if any(part in {"", ".", ".."} or ":" in part or part != part.rstrip(" .") for part in parts):
            raise ValueError("Unsafe or ambiguous path component")
        canonical = unicodedata.normalize("NFC", "/".join(parts)).casefold()
        if canonical in names:
            raise ValueError("Duplicate or case/Unicode-colliding member paths")
        names[canonical] = member.is_dir()
        if not member.is_dir():
            files.add(canonical)
        mode = member.external_attr >> 16
        kind = stat.S_IFMT(mode)
        if kind not in {0, stat.S_IFREG, stat.S_IFDIR} or (kind == stat.S_IFDIR) != member.is_dir() and kind != 0:
            raise ValueError("Symlink, special file or inconsistent directory metadata")
        if member.flag_bits & 1:
            raise ValueError("Encrypted archive member")
        if member.compress_type not in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED, zipfile.ZIP_BZIP2, zipfile.ZIP_LZMA}:
            raise ValueError("Unsupported compression method")
        if member.file_size < 0 or member.file_size > MAX_MEMBER_BYTES:
            raise ValueError("Excessive member size")
        if member.file_size > 1024 ** 2 and member.file_size / max(member.compress_size, 1) > 1000:
            raise ValueError("Excessive compression ratio")
        total += member.file_size
    if total > MAX_TOTAL_BYTES:
        raise ValueError("Excessive total expanded size")
    for name in names:
        pieces = name.split("/")
        if any("/".join(pieces[:index]) in files for index in range(1, len(pieces))):
            raise ValueError("File/directory prefix conflict")
    return total


def inspect_and_extract(archive, destination):
    archive, destination = Path(archive).resolve(), Path(destination).absolute()
    if destination.exists() or destination.is_symlink():
        raise FileExistsError("Destination must be a new isolated directory")
    original_hash = sha256(archive)
    inventory = []
    with zipfile.ZipFile(archive) as bundle:
        members = bundle.infolist()
        total = check_members(members)
        corrupt = bundle.testzip()  # CRC and decompression checks before extraction.
        if corrupt is not None:
            raise zipfile.BadZipFile(f"CRC failed for member: {corrupt}")
        if sha256(archive) != original_hash:
            raise ValueError("Archive changed during preflight")
        destination.mkdir(parents=False, exist_ok=False)
        for member in members:
            target = destination / member.filename
            if not target.resolve().is_relative_to(destination.resolve()):
                raise ValueError("Member escapes extraction root")
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            digest, length = hashlib.sha256(), 0
            with bundle.open(member, "r") as source, target.open("xb") as output:
                while chunk := source.read(1024 * 1024):
                    length += len(chunk)
                    if length > member.file_size or length > MAX_MEMBER_BYTES:
                        raise ValueError("Expanded member exceeds declared/allowed size")
                    digest.update(chunk)
                    output.write(chunk)
            if length != member.file_size or sha256(target) != digest.hexdigest():
                raise ValueError("Extracted bytes/size differ from archive member")
            suffix = target.suffix.lower()
            formats = {".csv": "CSV", ".json": "JSON", ".md": "Markdown text", ".py": "Python source (NOT EXECUTED)",
                       ".html": "HTML evidence/response", ".txt": "Text", ".tsv": "Tab-separated text", ".out": "Text log"}
            inventory.append({"path": member.filename, "bytes": length, "format": formats.get(suffix, "Unclassified"),
                              "compressed_bytes": member.compress_size, "crc32": f"{member.CRC:08x}", "sha256": digest.hexdigest()})
    if sha256(archive) != original_hash:
        raise ValueError("Original archive changed during extraction")
    return {
        "archive": str(archive), "archive_bytes": archive.stat().st_size, "archive_sha256": original_hash,
        "expected_archive_sha256": None, "expected_archive_checksum_status": "NOT_SUPPLIED; locally computed fingerprint only",
        "unsafe_paths": 0, "member_count": len(members), "file_count": len(inventory),
        "total_uncompressed_bytes": total, "crc_and_decompression": "PASS_ALL_MEMBERS",
        "destination": str(destination.resolve()), "original_archive_unchanged": True,
        "packaged_scripts_executed": 0, "trust_status": "UNVERIFIED", "files": inventory,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--inventory", required=True, type=Path)
    args = parser.parse_args()
    for output in (args.report, args.inventory):
        if output.exists() or output.is_symlink():
            raise FileExistsError("Use new report and inventory paths")
    if args.report.resolve() == args.inventory.resolve():
        raise ValueError("Report and inventory paths must differ")
    result = inspect_and_extract(args.archive, args.destination)
    with args.report.open("x") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    with args.inventory.open("x", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "bytes", "format", "compressed_bytes", "crc32", "sha256"])
        writer.writeheader()
        writer.writerows(result["files"])
    print(json.dumps({key: value for key, value in result.items() if key != "files"}, indent=2))


if __name__ == "__main__":
    main()
