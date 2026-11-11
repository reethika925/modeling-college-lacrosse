"""Synthetic ZIP safety cases only; no invented research observations."""

import stat
import zipfile

import pytest

from src import inspect_grok_package as inspector


@pytest.mark.parametrize("name", ["../outside.txt", "/outside.txt", "a/../../outside.txt", "C:/outside.txt",
                                    "a\\outside.txt", "a/./b.txt", "a//b.txt", "a/b:stream", "a./b.txt"])
def test_unsafe_member_paths_are_rejected(name):
    with pytest.raises(ValueError):
        inspector.check_members([zipfile.ZipInfo(name)])


@pytest.mark.parametrize("names", [["a.txt", "a.txt"], ["A.txt", "a.txt"], ["a", "a/b.txt"], ["caf\u00e9.txt", "cafe\u0301.txt"]])
def test_colliding_or_conflicting_paths_are_rejected(names):
    with pytest.raises(ValueError):
        inspector.check_members([zipfile.ZipInfo(name) for name in names])


def test_symlinks_and_encryption_are_rejected():
    link = zipfile.ZipInfo("synthetic_link")
    link.external_attr = (stat.S_IFLNK | 0o777) << 16
    with pytest.raises(ValueError, match="Symlink"):
        inspector.check_members([link])
    encrypted = zipfile.ZipInfo("synthetic_encrypted.txt")
    encrypted.flag_bits |= 1
    with pytest.raises(ValueError, match="Encrypted"):
        inspector.check_members([encrypted])


def test_nul_truncation_and_excessive_expansion_are_rejected():
    with pytest.raises(ValueError, match="truncated"):
        inspector.check_members([zipfile.ZipInfo("safe\x00unsafe")])
    large = zipfile.ZipInfo("synthetic_large.txt")
    large.file_size = inspector.MAX_MEMBER_BYTES + 1
    with pytest.raises(ValueError, match="size"):
        inspector.check_members([large])
    large.file_size, large.compress_size = 2 * 1024 ** 2, 1
    with pytest.raises(ValueError, match="ratio"):
        inspector.check_members([large])


def test_safe_extraction_preserves_bytes_and_does_not_execute_scripts(tmp_path):
    archive = tmp_path / "synthetic_only.zip"
    payload = b"SYNTHETIC TEST PAYLOAD ONLY\n"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("synthetic/a.txt", payload)
        bundle.writestr("synthetic/never_run.py", 'raise AssertionError("SYNTHETIC CODE MUST NOT EXECUTE")\n')
    before = inspector.sha256(archive)
    destination = tmp_path / "isolated"
    result = inspector.inspect_and_extract(archive, destination)
    assert (destination / "synthetic/a.txt").read_bytes() == payload
    assert inspector.sha256(archive) == before == result["archive_sha256"]
    assert result["crc_and_decompression"] == "PASS_ALL_MEMBERS"
    assert result["file_count"] == 2 and result["packaged_scripts_executed"] == 0
    assert not (destination / "synthetic/never_run.py").stat().st_mode & 0o111
    with pytest.raises(FileExistsError):
        inspector.inspect_and_extract(archive, destination)
    assert (destination / "synthetic/a.txt").read_bytes() == payload


def test_traversal_is_rejected_before_any_extraction(tmp_path):
    archive = tmp_path / "synthetic_traversal.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("../synthetic_escape.txt", "SYNTHETIC TEST ONLY")
    destination = tmp_path / "isolated"
    with pytest.raises(ValueError):
        inspector.inspect_and_extract(archive, destination)
    assert not destination.exists() and not (tmp_path / "synthetic_escape.txt").exists()


def test_corrupt_member_crc_is_rejected_before_extraction(tmp_path):
    archive = tmp_path / "synthetic_corrupt.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as bundle:
        bundle.writestr("synthetic.txt", b"SYNTHETIC_KNOWN_PAYLOAD")
    content = archive.read_bytes().replace(b"SYNTHETIC_KNOWN_PAYLOAD", b"SYNTHETIC_BROKE_PAYLOAD")
    archive.write_bytes(content)
    destination = tmp_path / "isolated"
    with pytest.raises(zipfile.BadZipFile):
        inspector.inspect_and_extract(archive, destination)
    assert not destination.exists()
