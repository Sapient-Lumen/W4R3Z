from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


LIVING_DOC_LIMITS = {
    "README.md": 80_000,
    "TODO.md": 80_000,
    "docs/43-worklist.md": 80_000,
    "docs/01-llm-start-here.md": 80_000,
    "docs/02-repo-map.md": 80_000,
}


ARCHIVED_LIVING_DOCS = [
    "docs/history/README-through-rev0822.md",
    "docs/history/TODO-through-rev0822.md",
    "docs/history/43-worklist-through-rev0822.md",
    "docs/history/01-llm-start-here-through-rev0822.md",
    "docs/history/02-repo-map-through-rev0822.md",
]


def test_current_living_docs_stay_small_after_history_split() -> None:
    oversized: list[str] = []
    for rel, limit in LIVING_DOC_LIMITS.items():
        size = (ROOT / rel).stat().st_size
        if size > limit:
            oversized.append(f"{rel}: {size} > {limit}")
    assert oversized == []


def test_pre_split_living_doc_archives_are_preserved() -> None:
    missing = [rel for rel in ARCHIVED_LIVING_DOCS if not (ROOT / rel).exists()]
    assert missing == []
    for rel in ARCHIVED_LIVING_DOCS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "through rev0822" in text[:300]


def _makefile_default(name: str) -> str:
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    prefix = f"{name} ?= "
    for line in text.splitlines():
        if line.startswith(prefix):
            return line[len(prefix):].strip()
    raise AssertionError(f"missing Makefile default for {name}")


def _expected_rev() -> int:
    import re

    first = (ROOT / "TODO.md").read_text(encoding="utf-8").splitlines()[0]
    match = re.search(r"rev\s*(\d+)", first, flags=re.IGNORECASE)
    assert match is not None
    return int(match.group(1))


def test_repo_map_aggregate_lane_matches_makefile_defaults() -> None:
    """Keep the living repo map tied to the real aggregate handoff lane."""

    text = (ROOT / "docs" / "02-repo-map.md").read_text(encoding="utf-8")
    expected_rev = _expected_rev()
    expected = {
        "CHUNKS": _makefile_default("CHUNKS"),
        "MAX_NEW_TESTS": _makefile_default("MAX_NEW_TESTS"),
        "MAX_NEW_FILES": _makefile_default("MAX_NEW_FILES"),
        "TEST_BATCH_SIZE": _makefile_default("TEST_BATCH_SIZE"),
        "FILE_TIMEOUT": _makefile_default("FILE_TIMEOUT"),
        "MAX_RUNTIME_SECONDS": _makefile_default("MAX_RUNTIME_SECONDS"),
        "TEST_MANIFEST": _makefile_default("TEST_MANIFEST"),
    }

    assert f"# Repo map (rev{expected_rev:04d})" in text
    assert f"--run-chunks {expected['CHUNKS']}" in text
    assert f"--max-new-tests {expected['MAX_NEW_TESTS']}" in text
    assert f"--max-new-files {expected['MAX_NEW_FILES']}" in text
    assert f"--test-batch-size {expected['TEST_BATCH_SIZE']}" in text
    assert f"--file-timeout {expected['FILE_TIMEOUT']}" in text
    assert f"--max-runtime-seconds {expected['MAX_RUNTIME_SECONDS']}" in text
    assert f"--json {expected['TEST_MANIFEST']}" in text
    assert f"--verify-current {expected['TEST_MANIFEST']}" in text
    assert "pending evidence" not in text.lower()
    assert "--max-runtime-seconds 240" not in text
    assert ".artifacts/mxtest-all.json" not in text
