"""Synthetic file-content fixtures only; no invented sports observations."""
import hashlib

import pytest

from src.research_integrity import assert_research_snapshot


def digest(content):
    return hashlib.sha256(content).hexdigest()


@pytest.mark.parametrize("directory", ["data", "research", "reports", "results"])
def test_research_changes_and_missing_files_still_fail(tmp_path, directory):
    path = tmp_path / directory / "synthetic_test_fixture.txt"
    path.parent.mkdir()
    path.write_bytes(b"SYNTHETIC FILE CONTENT ONLY")
    manifest = {str(path.relative_to(tmp_path)): digest(path.read_bytes())}
    assert assert_research_snapshot(tmp_path, manifest) == 1
    path.write_bytes(b"CHANGED SYNTHETIC FILE CONTENT")
    with pytest.raises(ValueError, match="Protected research files"):
        assert_research_snapshot(tmp_path, manifest)
    path.unlink()
    with pytest.raises(ValueError, match="Protected research files"):
        assert_research_snapshot(tmp_path, manifest)


def test_code_and_documentation_are_not_frozen_research(tmp_path):
    manifest = {name: digest(b"OLD SYNTHETIC CONTENT") for name in
                ["README.md", ".gitignore", "src/synthetic.py",
                 "tests/test_synthetic.py", "docs/synthetic.md"]}
    assert assert_research_snapshot(tmp_path, manifest) == 0


@pytest.mark.parametrize("path", ["../synthetic", "/tmp/synthetic", "data/../synthetic"])
def test_snapshot_cannot_refer_outside_repository(tmp_path, path):
    with pytest.raises(ValueError, match="Unsafe snapshot path"):
        assert_research_snapshot(tmp_path, {path: digest(b"SYNTHETIC")})
