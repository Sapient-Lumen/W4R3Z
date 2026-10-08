#!/usr/bin/env python3
"""Validate the Example County mission-kernel closeout pack.

This check keeps v889 focused on executable forward motion: the seven mission
kernel elements must be mapped to evidence, owner roles, and live blockers, and
the files must be freshly generated from the current scenario/evidence map.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REV = VERSION.removeprefix("v").zfill(4)
OUTDIR = ROOT / "artifacts" / "examples" / "example_county_2026_municipal_pilot"
TOOL = ROOT / "tools" / "mission_kernel_closeout.py"
INDEX = OUTDIR / "mission-kernel-closeout-index.json"
PUBLIC = OUTDIR / "public-mission-kernel-closeout.md"
REPORT = ROOT / "artifacts" / "reports" / f"mission-kernel-closeout-gaps-rev{REV}.json"
REQUIRED_ELEMENT_IDS = {
    "K01_AUTHORIZED_ELECTION_DEFINITION",
    "K02_BALLOT_ACCOUNTING_AND_CUSTODY",
    "K03_STANDARDIZED_RESULTS_EXPORTS",
    "K04_AUDIT_RECOUNT_ADJUDICATION",
    "K05_AUTHENTICATED_OFFICIAL_NOTICES",
    "K06_INDEPENDENT_VERIFIER_DISAGREEMENT_FAILURE",
    "K07_INCIDENT_DISPUTE_REMEDY_CLOSEOUT",
}
NON_CLAIM_PHRASES = ["not live election evidence", "does not prove", "does not replace", "live no-go"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def run_tool_to_bytes() -> dict[Path, bytes]:
    paths = [INDEX, PUBLIC, REPORT]
    before = {p: p.read_bytes() if p.exists() else b"" for p in paths}
    proc = subprocess.run([sys.executable, str(TOOL), "--write"], cwd=ROOT, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False, timeout=120)
    after = {p: p.read_bytes() if p.exists() else b"" for p in paths}
    for p, data in before.items():
        if data:
            p.write_bytes(data)
        elif p.exists():
            p.unlink()
    if proc.returncode != 0:
        raise RuntimeError(f"mission-kernel closeout tool failed rc={proc.returncode}: {proc.stdout} {proc.stderr}")
    return after


def main() -> int:
    errors: list[str] = []
    for p in [TOOL, INDEX, PUBLIC, REPORT]:
        if not p.exists():
            errors.append(f"missing {p.relative_to(ROOT)}")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2

    try:
        generated = run_tool_to_bytes()
    except Exception as exc:
        print("ERROR:", exc, file=sys.stderr)
        return 2
    for p, data in generated.items():
        if p.read_bytes() != data:
            errors.append(f"mission-kernel closeout drift: {p.relative_to(ROOT)}; run `python3 tools/mission_kernel_closeout.py --write`")

    closeout = load_json(INDEX)
    report = load_json(REPORT)
    if closeout.get("archive_version") != VERSION or report.get("archive_version") != VERSION:
        errors.append("closeout/report archive_version mismatch")
    if not str(closeout.get("scenario_id") or "").endswith(VERSION):
        errors.append("closeout scenario_id is stale")
    if closeout.get("synthetic_only") is not True or closeout.get("no_live_deployment_claim") is not True:
        errors.append("closeout missing synthetic/no-live flags")
    if closeout.get("readiness_verdict") != "SYNTHETIC_REPLAY_PASS_LIVE_NO_GO":
        errors.append("closeout readiness verdict must remain synthetic replay pass / live no-go")

    elements = closeout.get("kernel_elements") or []
    ids = {str(e.get("element_id") or "") for e in elements if isinstance(e, dict)}
    if ids != REQUIRED_ELEMENT_IDS:
        errors.append("kernel element ids mismatch")
    if len(elements) != 7:
        errors.append("kernel element count must be exactly seven")
    for e in elements:
        if not isinstance(e, dict):
            errors.append("kernel element is not an object")
            continue
        eid = str(e.get("element_id") or "")
        if not e.get("owner_role") or str(e.get("owner_role")).upper() == "TBD":
            errors.append(f"{eid} missing concrete owner_role")
        if not e.get("closure_test"):
            errors.append(f"{eid} missing closure_test")
        refs = e.get("evidence_refs") or []
        blockers = e.get("live_blockers") or []
        if eid != "K04_AUDIT_RECOUNT_ADJUDICATION" and not refs:
            errors.append(f"{eid} must carry at least one evidence ref")
        if e.get("status") != "SYNTHETIC_REPLAY_PASS" and not blockers:
            errors.append(f"{eid} non-pass status must carry live blockers")
        if eid == "K04_AUDIT_RECOUNT_ADJUDICATION" and e.get("status") != "LIVE_BLOCKED_MISSING_EVIDENCE":
            errors.append("audit/recount/adjudication must remain explicitly live-blocked until evidence exists")
        for ref in refs:
            if not isinstance(ref, dict):
                errors.append(f"{eid} evidence ref is not an object")
                continue
            rel = str(ref.get("path") or "")
            if not rel or not (ROOT / rel).exists():
                errors.append(f"{eid} missing evidence path {rel!r}")
            if ref.get("ref_type") == "packet":
                manifest = ROOT / rel / "manifest.json"
                if not manifest.exists():
                    errors.append(f"{eid} packet ref lacks manifest: {rel}")
                else:
                    if ref.get("manifest_sha256") != sha256_file(manifest):
                        errors.append(f"{eid} packet manifest digest drift: {rel}")
                if ref.get("verification_status") != "PASS":
                    errors.append(f"{eid} packet verification is not PASS: {rel}")

    blockers = closeout.get("highest_risk_blockers") or []
    if len(blockers) < 7:
        errors.append("expected at least seven highest-risk blockers")
    if sum(1 for b in blockers if isinstance(b, dict) and b.get("priority") == "critical") < 5:
        errors.append("expected at least five critical live blockers")
    for b in blockers:
        if not isinstance(b, dict):
            errors.append("blocker is not an object")
            continue
        for field in ["owner_role", "missing_evidence", "next_artifact", "closure_test"]:
            if not b.get(field):
                errors.append(f"{b.get('blocker_id', '?')} missing {field}")

    ra = closeout.get("refactor_audit") or {}
    dup_raw = ra.get("duplicated_verify_packet_functions_after_refactor")
    try:
        dup_count = int(dup_raw)
    except (TypeError, ValueError):
        dup_count = -1
    if ra.get("status") != "PASS" or dup_count != 0:
        errors.append("refactor audit must prove duplicated Example County verify_packet functions are gone")
    if report.get("refactor_audit") != ra:
        errors.append("report refactor_audit must match closeout index")
    if int(report.get("kernel_element_count") or 0) != 7:
        errors.append("report kernel element count mismatch")

    public = PUBLIC.read_text(encoding="utf-8", errors="replace").lower()
    for phrase in NON_CLAIM_PHRASES:
        if phrase not in public:
            errors.append(f"public mission closeout missing boundary phrase: {phrase!r}")
    if "certifies" in public or "proves fraud" in public:
        errors.append("public mission closeout contains prohibited overclaiming language")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    print(f"PASS: mission-kernel closeout pack ({VERSION}, blockers={len(blockers)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
