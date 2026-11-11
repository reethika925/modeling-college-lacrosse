"""Read-only integrity checks for research artifacts in historical snapshots.

Snapshots also recorded then-current source code and documentation. Those files
are maintained software, rather than frozen research observations. Preserve the
original snapshot unchanged and check its data, evidence, reports and results.
"""
from __future__ import annotations

import hashlib
from pathlib import Path, PurePosixPath


MUTABLE_DIRECTORIES = {"src", "tests", "docs"}
MUTABLE_ROOT_FILES = {"README.md", ".gitignore"}


def assert_research_snapshot(root, manifest):
    """Raise on missing/changed protected files; return the number checked.

    Only code, tests, technical docs and the root README/gitignore are exempt.
    In particular, every reports/, results/, research/ and data/ entry remains
    protected, regardless of extension or evidence classification.
    """
    root = Path(root).resolve()
    changed = []
    checked = 0
    for name, expected in manifest.items():
        relative = PurePosixPath(name)
        if relative.is_absolute() or ".." in relative.parts or not relative.parts:
            raise ValueError(f"Unsafe snapshot path: {name}")
        if name in MUTABLE_ROOT_FILES or relative.parts[0] in MUTABLE_DIRECTORIES:
            continue
        checked += 1
        path = root / relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            changed.append(name)
    if changed:
        raise ValueError(f"Protected research files missing or changed: {changed}")
    return checked
