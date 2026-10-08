from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _expected_rev() -> int:
    first = (ROOT / "TODO.md").read_text(encoding="utf-8").splitlines()[0]
    match = re.search(r"rev\s*(\d+)", first, flags=re.IGNORECASE)
    assert match is not None
    return int(match.group(1))


def test_revision_index_matches_current_handoff_rev() -> None:
    payload = json.loads((ROOT / "docs" / "revision-index.json").read_text(encoding="utf-8"))
    expected_rev = _expected_rev()

    assert payload["schema"] == "micromax.revision-index.v1"
    assert payload["current_rev"] == expected_rev
    assert payload["entries"][0]["rev"] == expected_rev
    entry = payload["entries"][0]
    assert entry["docs"]
    assert entry["code"]
    assert all((ROOT / rel).exists() for rel in entry["docs"])
    assert all((ROOT / rel).exists() for rel in entry["code"])
