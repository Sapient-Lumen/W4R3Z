#!/usr/bin/env python3
"""Check the synthetic Example County pilot path is wired together.

This is not a live-pilot success criterion.  It is a release-gate tripwire that
proves the archive's smallest pilot rehearsal has resolvable packet pointers,
clear non-claims, and current-version smoke-test bookkeeping.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = ROOT / "artifacts" / "examples" / "example_county_2026_municipal_pilot" / "scenario.json"
PUBLIC_SUMMARY = ROOT / "artifacts" / "examples" / "example_county_2026_municipal_pilot" / "public-summary.md"
ADOPTER_SMOKES = ROOT / "artifacts" / "registries" / "adopter-path-smoke-tests.csv"
TURNOUT = ROOT / "artifacts" / "registries" / "turnout-oracle-risk-assessments.csv"
PILOT_LEDGER = ROOT / "artifacts" / "registries" / "pilot-data-ledger.csv"
VERSION = ROOT / "VERSION"

REQUIRED_PHASES = {
    "setup_official_channels",
    "election_parameters_and_witnesses",
    "notice_publication",
    "public_surface_monitoring",
    "results_and_closeout",
    "incident_and_recovery",
    "verifier_outputs",
}
REQUIRED_EVALS = {f"EVAL-{i:03d}" for i in range(1, 11)}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]


def main() -> int:
    errors: list[str] = []
    version = VERSION.read_text(encoding="utf-8").strip() if VERSION.exists() else ""

    if not SCENARIO.exists():
        errors.append(f"missing scenario: {SCENARIO.relative_to(ROOT)}")
    else:
        try:
            scenario = json.loads(SCENARIO.read_text(encoding="utf-8"))
        except Exception as exc:
            scenario = {}
            errors.append(f"scenario JSON parse failed: {exc}")

        if scenario.get("archive_version") != version:
            errors.append(f"scenario archive_version {scenario.get('archive_version')!r} does not match VERSION {version!r}")
        if scenario.get("synthetic_only") is not True:
            errors.append("scenario must set synthetic_only=true")
        if scenario.get("no_live_deployment_claim") is not True:
            errors.append("scenario must set no_live_deployment_claim=true")

        phases = scenario.get("phases") or []
        if not isinstance(phases, list):
            errors.append("scenario phases must be an array")
            phases = []
        have_phases = {str(p.get("phase_id", "")).strip() for p in phases if isinstance(p, dict)}
        missing_phases = sorted(REQUIRED_PHASES - have_phases)
        if missing_phases:
            errors.append("scenario missing required phases: " + ", ".join(missing_phases))

        packet_count = 0
        for p in phases:
            if not isinstance(p, dict):
                errors.append("scenario phase is not an object")
                continue
            if not (p.get("public_sentence") or "").strip():
                errors.append(f"phase {p.get('phase_id', '?')} missing public_sentence")
            packets = p.get("packets") or []
            if not isinstance(packets, list) or not packets:
                errors.append(f"phase {p.get('phase_id', '?')} must list packets")
                continue
            for pkt in packets:
                if not isinstance(pkt, dict):
                    errors.append(f"phase {p.get('phase_id', '?')} packet entry is not an object")
                    continue
                rel = str(pkt.get("path") or "").strip()
                kind = str(pkt.get("kind") or "").strip()
                if not rel:
                    errors.append(f"phase {p.get('phase_id', '?')} packet missing path")
                    continue
                if not kind.startswith("hfv."):
                    errors.append(f"phase {p.get('phase_id', '?')} packet {rel} has non-hfv kind {kind!r}")
                pp = ROOT / rel
                if not pp.exists():
                    errors.append(f"packet path missing: {rel}")
                    continue
                if not (pp / "manifest.json").exists():
                    errors.append(f"packet path lacks manifest.json: {rel}")
                packet_count += 1
        if packet_count < 12:
            errors.append(f"scenario packet coverage too small: {packet_count} packet(s)")

        evals = set(str(x).strip() for x in (scenario.get("evaluation_scenarios") or []))
        if REQUIRED_EVALS - evals:
            errors.append("scenario missing evaluation scenarios: " + ", ".join(sorted(REQUIRED_EVALS - evals)))

        non_claims = "\n".join(str(x) for x in (scenario.get("non_claims") or []))
        for phrase in ["does not prove", "does not replace", "does not contain live deployment data"]:
            if phrase not in non_claims:
                errors.append(f"scenario non_claims must include phrase: {phrase!r}")

    if not PUBLIC_SUMMARY.exists():
        errors.append(f"missing public summary: {PUBLIC_SUMMARY.relative_to(ROOT)}")
    else:
        text = PUBLIC_SUMMARY.read_text(encoding="utf-8")
        for phrase in [
            "Synthetic example only",
            "does not prove that an election outcome is correct",
            "missing evidence into proof of intent or fraud",
        ]:
            if phrase not in text:
                errors.append(f"public summary missing non-claim phrase: {phrase!r}")

    try:
        smokes = read_csv(ADOPTER_SMOKES)
    except Exception as exc:
        smokes = []
        errors.append(f"cannot read adopter smoke tests: {exc}")
    if not any((r.get("archive_version") == version and r.get("result") in {"synthetic_pass", "manual_pass"}) for r in smokes):
        errors.append(f"adopter-path-smoke-tests.csv must include a pass row for {version}")

    try:
        turns = read_csv(TURNOUT)
    except Exception as exc:
        turns = []
        errors.append(f"cannot read turnout-oracle-risk-assessments.csv: {exc}")
    if not turns:
        errors.append("turnout-oracle-risk-assessments.csv must include at least one bounded pre-pilot assessment row")
    elif not any((r.get("outcome") or "").strip() for r in turns):
        errors.append("turnout-oracle-risk-assessments.csv rows must declare outcome")

    try:
        ledger = read_csv(PILOT_LEDGER)
    except Exception as exc:
        ledger = []
        errors.append(f"cannot read pilot-data-ledger.csv: {exc}")
    if not any(r.get("archive_version") == version and r.get("status") == "synthetic_smoke_harness" for r in ledger):
        errors.append(f"pilot-data-ledger.csv must include a synthetic_smoke_harness row for {version}")
    if not any(r.get("archive_version") == version and r.get("status") == "pre_pilot_empty" for r in ledger):
        errors.append(f"pilot-data-ledger.csv must preserve a pre_pilot_empty live-evidence row for {version}")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2

    print(f"PASS: synthetic pilot readiness ({version})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
