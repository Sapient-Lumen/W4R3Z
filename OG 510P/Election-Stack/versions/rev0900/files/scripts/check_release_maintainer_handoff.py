#!/usr/bin/env python3
"""Validate release maintainer handoff outputs and source-review triage."""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REG = ROOT / "artifacts" / "registries" / "release-maintainer-handoff.csv"
OUTDIR = ROOT / "artifacts" / "reports"
TOOL = ROOT / "tools" / "release_maintainer_handoff_pack.py"

REQUIRED_HEADER = [
    "handoff_id",
    "track",
    "phase",
    "trigger",
    "owner",
    "required_artifacts",
    "gate_refs",
    "public_boundary",
    "non_claims",
]
REQUIRED_IDS = {f"RMH-{i:03d}" for i in range(1, 14)}
ALLOWED_TRACKS = {"A", "Shared"}
ALLOWED_REF_PREFIXES = {
    "DOC": "docs/",
    "SCRIPT": "scripts/",
    "TOOL": "tools/",
    "REG": "artifacts/registries/",
    "EXAMPLE": "artifacts/examples/",
    "REPORT": "artifacts/reports/",
    "CHECK": "artifacts/checklists/",
    "TEMPLATE": "artifacts/templates/",
}
TOKEN_RE = re.compile(r"^(?P<typ>[A-Z]+):(?P<path>.+)$")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def tokens(cell: str):
    for raw in (cell or "").split(";"):
        tok = raw.strip()
        if tok:
            yield tok


def validate_registry() -> list[str]:
    errors: list[str] = []
    if not REG.exists():
        return ["missing artifacts/registries/release-maintainer-handoff.csv"]
    with REG.open("r", encoding="utf-8", newline="") as f:
        rows_raw = list(csv.reader(f))
    if not rows_raw:
        return ["release-maintainer-handoff.csv is empty"]
    header = [h.strip() for h in rows_raw[0]]
    if header != REQUIRED_HEADER:
        errors.append(f"header mismatch: got {header!r} want {REQUIRED_HEADER!r}")
    rows = read_csv(REG)
    seen: set[str] = set()
    for line_no, row in enumerate(rows, start=2):
        hid = row.get("handoff_id", "")
        if not re.fullmatch(r"RMH-\d{3}", hid):
            errors.append(f"L{line_no}: invalid handoff_id {hid!r}")
            continue
        if hid in seen:
            errors.append(f"L{line_no}: duplicate handoff_id {hid}")
        seen.add(hid)
        if row.get("track") not in ALLOWED_TRACKS:
            errors.append(f"L{line_no}: invalid track for {hid}: {row.get('track')!r}")
        for field in REQUIRED_HEADER[2:]:
            if not row.get(field):
                errors.append(f"L{line_no}: {hid} missing {field}")
        for field in ["required_artifacts", "gate_refs"]:
            for tok in tokens(row.get(field, "")):
                m = TOKEN_RE.match(tok)
                if not m:
                    errors.append(f"L{line_no}: {hid} unparseable ref token {tok!r}")
                    continue
                typ = m.group("typ")
                rel = m.group("path")
                pref = ALLOWED_REF_PREFIXES.get(typ)
                if not pref:
                    errors.append(f"L{line_no}: {hid} unknown ref type {typ!r}")
                    continue
                if not rel.startswith(pref):
                    errors.append(f"L{line_no}: {hid} {typ} ref must start with {pref!r}: {rel!r}")
                    continue
                # Generated report files are checked after generation; allow them to be created by this pass.
                if not (ROOT / rel).exists():
                    errors.append(f"L{line_no}: {hid} missing referenced file: {rel}")
        non_claim = (row.get("non_claims") or "").lower()
        if "not" not in non_claim:
            errors.append(f"L{line_no}: {hid} non_claims must state non-claims explicitly")
    missing = sorted(REQUIRED_IDS - seen)
    if missing:
        errors.append("missing required handoff ids: " + ", ".join(missing))
    return errors


def main() -> int:
    errors: list[str] = []
    for name in [
        "release-maintainer-handoff.json",
        "release-maintainer-handoff.md",
        "source-review-triage.json",
        "source-review-triage.csv",
    ]:
        if not (OUTDIR / name).exists():
            errors.append(f"missing artifacts/reports/{name}")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2

    errors.extend(validate_registry())

    proc = subprocess.run(
        [sys.executable, str(TOOL), "--json"],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        print("ERROR: tools/release_maintainer_handoff_pack.py --json failed", file=sys.stderr)
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        return 2
    try:
        generated_handoff = json.loads(proc.stdout)
    except Exception as exc:
        print(f"ERROR: generated handoff JSON parse failed: {exc}", file=sys.stderr)
        return 2

    shipped_handoff = load_json(OUTDIR / "release-maintainer-handoff.json")
    if shipped_handoff != generated_handoff:
        errors.append("release-maintainer-handoff.json is stale; run tools/release_maintainer_handoff_pack.py --write")
    triage = load_json(OUTDIR / "source-review-triage.json")

    if shipped_handoff.get("archive_version") != VERSION:
        errors.append("release handoff archive_version does not match VERSION")
    if shipped_handoff.get("synthetic_only") is not True or shipped_handoff.get("no_live_deployment_claim") is not True:
        errors.append("release handoff missing synthetic/live-evidence boundary flags")
    if not str(shipped_handoff.get("scenario_id") or "").endswith(VERSION):
        errors.append("release handoff scenario_id is stale")
    inv = shipped_handoff.get("release_gate_inventory") or {}
    if int(inv.get("child_steps") or 0) < 120:
        errors.append("release handoff child_steps unexpectedly low")
    outputs = shipped_handoff.get("current_outputs") or {}
    if outputs.get("smoke_status") != "PASS" or outputs.get("scorecard_status") != "PASS" or outputs.get("negative_control_status") != "PASS":
        errors.append("release handoff current output statuses must all PASS")
    if int(outputs.get("scorecard_total_points") or 0) != int(outputs.get("scorecard_max_points") or -1):
        errors.append("release handoff scorecard must be full synthetic PASS")
    if outputs.get("mission_kernel_full_drill_decision") != "DRILL_COMPLETE_NOT_LIVE_READY":
        errors.append("release handoff full-drill decision must remain DRILL_COMPLETE_NOT_LIVE_READY")
    if int(outputs.get("mission_kernel_full_drill_valid_drill_objects", -1)) != int(outputs.get("mission_kernel_full_drill_required_classes", -2)):
        errors.append("release handoff full-drill valid object count must equal required evidence class count")
    if int(outputs.get("mission_kernel_full_drill_live_objects", -1)) != 0:
        errors.append("release handoff full-drill live object count must remain zero")
    if int(outputs.get("mission_kernel_full_drill_complete_items", -1)) != int(outputs.get("mission_kernel_full_drill_work_items", -2)):
        errors.append("release handoff full-drill must complete every work item in drill mode")
    if int(outputs.get("mission_kernel_full_drill_leak_count", -1)) != 0 or int(outputs.get("mission_kernel_full_drill_overclaim_count", -1)) != 0:
        errors.append("release handoff full-drill must have zero local-path leaks and zero overclaim terms")
    if outputs.get("ballot_accounting_reconciliation_decision") != "SYNTHETIC_BALLOT_ACCOUNTING_RECONCILIATION_PASS_NOT_CUSTODY_EVIDENCE":
        errors.append("release handoff ballot-accounting reconciliation decision must be current synthetic pass / not custody evidence")
    if int(outputs.get("ballot_accounting_reconciliation_errors", -1)) != 0:
        errors.append("release handoff ballot-accounting reconciliation must have zero default errors")
    if outputs.get("ballot_accounting_no_live_custody_claim") is not True:
        errors.append("release handoff ballot-accounting reconciliation must preserve no-live-custody flag")
    if outputs.get("event_log_reconciliation_decision") != "SYNTHETIC_EVENT_LOG_CHAIN_PASS_NOT_LIVE_EEL":
        errors.append("release handoff event-log reconciliation decision must be current synthetic pass / not live EEL evidence")
    if int(outputs.get("event_log_reconciliation_errors", -1)) != 0:
        errors.append("release handoff event-log reconciliation must have zero default errors")
    if int(outputs.get("event_log_missing_required_roles", -1)) != 0:
        errors.append("release handoff event-log reconciliation must have zero missing required roles")
    if outputs.get("event_log_no_live_eel_claim") is not True:
        errors.append("release handoff event-log reconciliation must preserve no-live-EEL flag")

    if triage.get("archive_version") != VERSION:
        errors.append("source-review-triage.json archive_version does not match VERSION")
    if int(triage.get("source_count") or 0) < 1000:
        errors.append("source-review-triage source_count unexpectedly low")
    if int(triage.get("expired_review_count") or 0) != 0:
        errors.append("source-review-triage has expired review windows at release date")
    if int(triage.get("missing_review_by_count") or 0) != 0:
        errors.append("source-review-triage has missing review_by rows")
    rows = read_csv(OUTDIR / "source-review-triage.csv")
    categories = {r.get("category") for r in rows}
    for needed in ["pinned", "unpinned_due_within_30_days", "special_case_high_risk_due_within_30_days"]:
        if needed not in categories:
            errors.append(f"source-review-triage.csv missing category {needed}")
    if not all((r.get("non_claims") or "") for r in rows):
        errors.append("source-review-triage.csv rows must carry non_claims")

    public = (OUTDIR / "release-maintainer-handoff.md").read_text(encoding="utf-8", errors="replace").lower()
    for phrase in ["synthetic example only", "not live election evidence", "not certification", "not legal advice", "full mission-kernel non-production drill replay", "ballot-accounting reconciliation", "election-event log reconciliation", "run `python3 scripts/release_gate.py`"]:
        if phrase not in public:
            errors.append(f"release-maintainer-handoff.md missing boundary phrase {phrase!r}")
    if "certifies" in public or "proves fraud" in public:
        errors.append("release-maintainer-handoff.md contains prohibited certification/fraud inference language")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    print(f"PASS: release maintainer handoff ({VERSION}, {triage['source_count']} source(s), {triage['due_within_30_days_count']} due<=30d)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
