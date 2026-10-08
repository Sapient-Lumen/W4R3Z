#!/usr/bin/env python3
"""Release-gate the synthetic election-event log chain.

A replayed result and a ballot-accounting reconciliation are not enough if the
archive cannot prove which event chained which artifact bytes.  This check keeps
that event-chain seam executable, current-versioned, and bounded as synthetic
only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import election_event_log_reconciler as event_replay  # noqa: E402
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REV = VERSION.removeprefix("v").zfill(4)
TOOL = ROOT / "tools" / "election_event_log_reconciler.py"
CDF_DIR = ROOT / "artifacts" / "examples" / "example_county_2026_municipal_pilot" / "cdf"
EVENT_LOG = CDF_DIR / "election-event-log-minimal.json"
REPORT = ROOT / "artifacts" / "reports" / f"election-event-log-reconciliation-rev{REV}.json"
PUBLIC = CDF_DIR / "public-election-event-log-reconciliation.md"
VECTORS = ROOT / "artifacts" / "test-vectors" / "election-event-log"
PASS_DECISION = "SYNTHETIC_EVENT_LOG_CHAIN_PASS_NOT_LIVE_EEL"
REQUIRED = [TOOL, EVENT_LOG, REPORT, PUBLIC]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def run_tool(event_log: Path = EVENT_LOG) -> tuple[int, dict[str, Any], str]:
    """Run the event-log reconciler in-process inside the release-gate child."""

    obj = event_replay.build_report(event_log)
    code = 0 if obj.get("decision") == PASS_DECISION else 2
    return code, obj, ""


def require_negative(label: str, path: Path, want_prefix: str, errors: list[str]) -> None:
    code, obj, stderr = run_tool(path)
    if code == 0:
        errors.append(f"{label}: negative control exited 0")
    if obj.get("decision") != "FAIL_EVENT_LOG_CHAIN_RECONCILIATION":
        errors.append(f"{label}: decision {obj.get('decision')!r} != FAIL_EVENT_LOG_CHAIN_RECONCILIATION")
    problems = [str(e) for e in obj.get("errors") or []]
    if not any(p.startswith(want_prefix) for p in problems):
        errors.append(f"{label}: missing problem prefix {want_prefix!r}; got {problems!r}; stderr={stderr!r}")


def main() -> int:
    errors: list[str] = []
    for path in REQUIRED:
        if not path.exists():
            errors.append(f"missing {path.relative_to(ROOT)}")
    for name in [
        "election-event-log-broken-prev-hash.json",
        "election-event-log-digest-mismatch.json",
        "election-event-log-timestamp-regression.json",
        "election-event-log-missing-required-role.json",
    ]:
        if not (VECTORS / name).exists():
            errors.append(f"missing {VECTORS.relative_to(ROOT)}/{name}")
    if errors:
        for error in errors:
            print("ERROR:", error, file=sys.stderr)
        return 2

    code, generated, stderr = run_tool()
    if code != 0:
        errors.append(f"default election-event-log reconciliation failed rc={code}: {stderr}")
    shipped = load_json(REPORT)
    if shipped != generated:
        errors.append("election-event-log reconciliation report is stale; run tools/election_event_log_reconciler.py --write")
    if shipped.get("archive_version") != VERSION:
        errors.append("election-event-log reconciliation archive_version mismatch")
    if shipped.get("decision") != PASS_DECISION:
        errors.append("event-log reconciliation must pass only as synthetic non-live EEL evidence")
    for flag in ["synthetic_only", "no_live_deployment_claim", "no_live_election_event_log_claim", "no_full_nist_eel_or_cdf_conformance_claim", "no_nist_cdf_test_method_claim", "no_certification_claim", "no_outcome_proof_claim"]:
        if shipped.get(flag) is not True:
            errors.append(f"event-log reconciliation missing boundary flag {flag}")
    counts = shipped.get("counts") or {}
    if counts.get("event_count") != 12 or counts.get("required_role_count") != 12:
        errors.append(f"unexpected event-log fixture counts: {counts!r}")
    if counts.get("error_count") != 0 or counts.get("missing_required_role_count") != 0:
        errors.append("default event-log reconciliation must have zero errors and all required artifact roles present")
    if counts.get("artifact_digest_match_count") != counts.get("event_count"):
        errors.append("all event-log artifact digests must match existing shipped bytes")
    if not str(shipped.get("event_log_hash") or "").startswith("sha256:") or shipped.get("event_log_hash") != shipped.get("computed_event_log_hash"):
        errors.append("event-log hash must be present and self-consistent")

    public = PUBLIC.read_text(encoding="utf-8", errors="replace").lower()
    for phrase in ["not live election event log evidence", "not full nist eel or cdf conformance", "not the nist cdf test method", "not certification", "not outcome proof", "not current voter instruction", "not legal advice", "does not authorize live pilot use"]:
        if phrase not in public:
            errors.append(f"public event-log summary missing boundary phrase {phrase!r}")
    for bad in ["full nist eel conformance pass", "certifies", "proves the outcome", "authorizes live pilot"]:
        if bad in public:
            errors.append(f"public event-log summary contains prohibited overclaim {bad!r}")

    require_negative("broken-prev-hash", VECTORS / "election-event-log-broken-prev-hash.json", "EVENT_PREVIOUS_HASH_MISMATCH:", errors)
    require_negative("digest-mismatch", VECTORS / "election-event-log-digest-mismatch.json", "EVENT_ARTIFACT_DIGEST_MISMATCH:", errors)
    require_negative("timestamp-regression", VECTORS / "election-event-log-timestamp-regression.json", "EVENT_TIMESTAMP_REGRESSION:", errors)
    require_negative("missing-required-role", VECTORS / "election-event-log-missing-required-role.json", "EVENT_REQUIRED_ROLE_MISSING:", errors)

    if errors:
        for error in errors:
            print("ERROR:", error, file=sys.stderr)
        return 2
    print(f"PASS: election-event-log reconciliation ({VERSION}, events={counts.get('event_count')})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
