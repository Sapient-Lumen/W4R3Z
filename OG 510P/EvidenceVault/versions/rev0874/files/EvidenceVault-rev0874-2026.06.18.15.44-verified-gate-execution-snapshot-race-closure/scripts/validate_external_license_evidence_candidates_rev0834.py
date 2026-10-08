#!/usr/bin/env python3
"""Validate rev0834 external rights-evidence candidate ledger."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_external_license_evidence_candidates_rev0834 import build, render_markdown, LOCAL_MISSING_LICENSE  # noqa: E402

JSON_PATH = ROOT / "RIGHTS" / "external_license_evidence_candidates_rev0834.json"
MD_PATH = ROOT / "RIGHTS" / "external_license_evidence_candidates_rev0834.md"


def fail(msg: str) -> None:
    print(f"external-license-evidence-candidates-validate: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if (ROOT / LOCAL_MISSING_LICENSE).exists():
        fail("candidate validator expected the local referenced LICENSE file to remain absent until a pinned source snapshot is reviewed")
    actual = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    expected = build(ROOT)
    if actual != expected:
        fail("external license evidence candidate JSON is stale")
    if MD_PATH.read_text(encoding="utf-8") != render_markdown(expected):
        fail("external license evidence candidate markdown is stale")
    if not actual.get("does_not_grant_license"):
        fail("candidate ledger must explicitly state that it does not grant a license")
    if not actual.get("does_not_change_spdx_conclusions") or not actual.get("does_not_change_ro_crate_license"):
        fail("candidate ledger must not change SPDX or RO-Crate license conclusions")
    candidate = actual["candidates"][0]
    if candidate["external_repository"].get("commit_pinned"):
        fail("rev0834 candidate is not allowed to claim a pinned commit")
    print("external-license-evidence-candidates-validate: OK")


if __name__ == "__main__":
    main()
