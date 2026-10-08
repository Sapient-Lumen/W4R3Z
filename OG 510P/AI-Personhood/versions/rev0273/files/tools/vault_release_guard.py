#!/usr/bin/env python3
"""Release-tree guard for private evidence vault separation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

FORBIDDEN_RAW_PREFIXES = (
    "private-evidence-vault/",
    ".private-evidence-vault/",
    "sealed-vault/",
    "raw-evidence-vault/",
    "AI-Personhood-private-evidence-vault/",
)
PUBLIC_ARTIFACT_PREFIX = "examples/artifacts/"
ALLOWLIST_PUBLIC_ARTIFACTS = {
    "examples/artifacts/result-return-counterparty-response-dryrun.txt",
    "examples/artifacts/live-evidence-drops/rev0210-result-return-dryrun-control.txt",
}


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _looks_like_synthetic_control(rel: str) -> bool:
    name = Path(rel).name.lower()
    return ("dryrun" in name or "dry-run" in name or "control" in name) and not any(token in name for token in ["live", "real", "private"])


def _ledger_refs_by_public_payload(root: Path) -> dict[str, list[str]]:
    refs: dict[str, list[str]] = {}
    for path in sorted((root / "examples").glob("live-evidence-drop-ledger*.json")):
        data = _load_json(path)
        staged = data.get("staged_payload", {}).get("quarantine_locator")
        source = data.get("source_payload", {}).get("original_locator")
        for rel in [staged, source]:
            if isinstance(rel, str) and rel.startswith(PUBLIC_ARTIFACT_PREFIX):
                refs.setdefault(rel, []).append(data.get("intake_mode", "unknown"))
    return refs


def scan_release_tree(root: Path) -> List[str]:
    """Return blocking release-vault violations."""
    root = root.resolve()
    violations: List[str] = []

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(root).as_posix()
        if rel.startswith(FORBIDDEN_RAW_PREFIXES):
            violations.append(f"private/raw vault material inside release tree: {rel}")
        if rel.startswith(PUBLIC_ARTIFACT_PREFIX):
            allowed = rel in ALLOWLIST_PUBLIC_ARTIFACTS or _looks_like_synthetic_control(rel)
            if not allowed:
                violations.append(f"non-synthetic public artifact payload would be packaged: {rel}")

    public_refs = _ledger_refs_by_public_payload(root)
    for rel, modes in public_refs.items():
        if any(mode == "live-candidate-drop" for mode in modes):
            violations.append(f"live-candidate ledger points at public release-tree payload: {rel}")
        if rel not in ALLOWLIST_PUBLIC_ARTIFACTS and not _looks_like_synthetic_control(rel):
            violations.append(f"ledger references non-allowlisted public artifact payload: {rel}")

    for ledger in sorted((root / "examples").glob("live-evidence-drop-ledger*.json")):
        data = _load_json(ledger)
        if data.get("intake_mode") != "live-candidate-drop":
            continue
        staged = data.get("staged_payload", {}).get("quarantine_locator")
        source = data.get("source_payload", {}).get("original_locator")
        if not isinstance(staged, str) or not staged.startswith("private-vault://"):
            violations.append(f"live-candidate ledger lacks private-vault locator: {ledger.relative_to(root).as_posix()}")
        if isinstance(source, str) and not source.startswith("private-source-redacted:"):
            violations.append(f"live-candidate ledger leaks source locator: {ledger.relative_to(root).as_posix()}")

    return violations


def guard_release_tree(root: Path) -> None:
    violations = scan_release_tree(root)
    if violations:
        raise SystemExit("private evidence vault release guard failed:\n- " + "\n- ".join(violations))


if __name__ == "__main__":
    guard_release_tree(Path(__file__).resolve().parents[1])
    print("vault_release_guard: OK")
