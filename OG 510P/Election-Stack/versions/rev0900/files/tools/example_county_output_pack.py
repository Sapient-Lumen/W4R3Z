#!/usr/bin/env python3
"""Build the synthetic Example County public/verifier/court output pack.

The output pack is a deterministic convenience layer over scenario.json. It is
not live deployment evidence. It writes:
- smoke-report.json: verifier status for every scenario packet
- evidence-map.json: phase/kind/path/digest map for public and observer readers
- court-packet-index.csv: preservation-oriented packet index with non-claims
- public-verifier-quickstart.md: short offline commands and boundaries
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from example_county_common import DEFAULT_SCENARIO as SCENARIO, ROOT, load_json, iter_packet_refs, verify_packet

OUTDIR = SCENARIO.parent
NON_CLAIM = "Digest integrity and publication-state evidence only; not outcome certification or proof of intent/fraud."


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def build_smoke_report(scenario: dict[str, Any]) -> dict[str, Any]:
    results = []
    for phase_id, _public_sentence, kind, rel in iter_packet_refs(scenario):
        r = verify_packet(rel)
        r["phase_id"] = phase_id
        r["kind"] = kind
        results.append(r)
    failures = [r for r in results if r.get("returncode") != 0 or r.get("status") != "PASS"]
    return {
        "scenario_id": scenario.get("scenario_id"),
        "archive_version": scenario.get("archive_version"),
        "synthetic_only": scenario.get("synthetic_only") is True,
        "packets_checked": len(results),
        "status": "PASS" if not failures else "FAIL",
        "results": results,
        "non_claim": "Synthetic rehearsal only; not live deployment evidence and not an outcome certification.",
    }


def build_evidence_map(scenario: dict[str, Any], smoke: dict[str, Any]) -> dict[str, Any]:
    smoke_by_packet = {str(r.get("packet")): r for r in smoke.get("results") or [] if isinstance(r, dict)}
    phases = []
    packet_count = 0
    for phase in scenario.get("phases") or []:
        if not isinstance(phase, dict):
            continue
        out_packets = []
        for packet in phase.get("packets") or []:
            if not isinstance(packet, dict):
                continue
            rel = str(packet.get("path") or "").strip()
            if not rel:
                continue
            manifest = ROOT / rel / "manifest.json"
            out_packets.append({
                "kind": str(packet.get("kind") or ""),
                "path": rel,
                "manifest_sha256": sha256_file(manifest) if manifest.exists() else "",
                "verification_status": str(smoke_by_packet.get(rel, {}).get("status") or "NOT_RUN"),
                "verification_command": f"python3 tools/observer_verify_packet.py {rel} --public --json",
            })
            packet_count += 1
        phases.append({
            "phase_id": str(phase.get("phase_id") or ""),
            "goal": str(phase.get("goal") or ""),
            "public_sentence": str(phase.get("public_sentence") or ""),
            "packets": out_packets,
        })
    return {
        "archive_version": scenario.get("archive_version"),
        "scenario_id": scenario.get("scenario_id"),
        "synthetic_only": scenario.get("synthetic_only") is True,
        "no_live_deployment_claim": scenario.get("no_live_deployment_claim") is True,
        "packet_count": packet_count,
        "smoke_status": smoke.get("status"),
        "public_summary": scenario.get("public_summary"),
        "phases": phases,
        "non_claims": scenario.get("non_claims") or [],
    }


def build_court_rows(evidence_map: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    n = 1
    for phase in evidence_map.get("phases") or []:
        if not isinstance(phase, dict):
            continue
        phase_id = str(phase.get("phase_id") or "")
        public_sentence = str(phase.get("public_sentence") or "")
        for packet in phase.get("packets") or []:
            if not isinstance(packet, dict):
                continue
            kind = str(packet.get("kind") or "")
            purpose = "preserve packet manifest, payload digest, verifier status, and phase context"
            if "incident" in kind:
                purpose = "preserve bounded incident/recovery evidence without inferring motive"
            elif "results" in kind:
                purpose = "preserve exactly released result/closeout bytes without certifying outcome correctness"
            elif "public_surface" in kind or "publication" in kind or "public.notice" in kind:
                purpose = "preserve publication-state, parity, freshness, or missingness evidence"
            elif "witness" in kind:
                purpose = "preserve witness-set context for independent verification"
            rows.append({
                "packet_id": f"P{n:03d}",
                "phase_id": phase_id,
                "kind": kind,
                "path": str(packet.get("path") or ""),
                "manifest_sha256": str(packet.get("manifest_sha256") or ""),
                "verification_status": str(packet.get("verification_status") or ""),
                "preservation_purpose": purpose,
                "public_sentence": public_sentence,
                "non_claim": NON_CLAIM,
                "verification_command": str(packet.get("verification_command") or ""),
            })
            n += 1
    return rows


def quickstart_text(scenario: dict[str, Any], evidence_map: dict[str, Any]) -> str:
    version = scenario.get("archive_version")
    scenario_id = scenario.get("scenario_id")
    packet_count = evidence_map.get("packet_count")
    return f"""# Example County public verifier quickstart

**Synthetic example only. This is not live election evidence.**

Scenario: `{scenario_id}`  
Archive version: `{version}`  
Packets listed: `{packet_count}`

## One-command rehearsal

```bash
python3 tools/example_county_pilot_smoke.py --json
```

Expected synthetic result: `PASS` for every listed packet.

## Output pack files

- `artifacts/examples/example_county_2026_municipal_pilot/evidence-map.json` maps phases to packet kinds, paths, manifest digests, and verifier commands.
- `artifacts/examples/example_county_2026_municipal_pilot/smoke-report.json` records the synthetic verifier run for every listed packet.
- `artifacts/examples/example_county_2026_municipal_pilot/court-packet-index.csv` gives a preservation-oriented index with non-claims.
- `artifacts/examples/example_county_2026_municipal_pilot/mission-kernel-closeout-index.json` maps the seven mission-kernel elements to actual packets, owner roles, and live blockers.
- `artifacts/examples/example_county_2026_municipal_pilot/public-summary.md` gives safe public-language phrases.

## Boundary

This rehearsal checks packet integrity, digest linkage, manifest closure, and bounded publication-state evidence. It does not prove that an election outcome is correct, does not replace canvass, audit, certification, recount, or court procedure, and does not turn missingness, parity divergence, or incident evidence into proof of intent or fraud.
"""


def write_output_pack(scenario_path: Path = SCENARIO) -> dict[str, Any]:
    scenario = load_json(scenario_path)
    smoke = build_smoke_report(scenario)
    evidence_map = build_evidence_map(scenario, smoke)
    rows = build_court_rows(evidence_map)

    (OUTDIR / "smoke-report.json").write_text(json.dumps(smoke, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    (OUTDIR / "evidence-map.json").write_text(json.dumps(evidence_map, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    with (OUTDIR / "court-packet-index.csv").open("w", encoding="utf-8", newline="") as f:
        fields = ["packet_id", "phase_id", "kind", "path", "manifest_sha256", "verification_status", "preservation_purpose", "public_sentence", "non_claim", "verification_command"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow(row)
    (OUTDIR / "public-verifier-quickstart.md").write_text(quickstart_text(scenario, evidence_map), encoding="utf-8")
    return {"smoke": smoke, "evidence_map": evidence_map, "court_rows": rows}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default=str(SCENARIO), help="Scenario JSON path")
    ap.add_argument("--write", action="store_true", help="Write deterministic output-pack files")
    ap.add_argument("--json", action="store_true", help="Print the evidence map JSON")
    args = ap.parse_args()

    scenario_path = Path(args.scenario)
    if not scenario_path.is_absolute():
        scenario_path = ROOT / scenario_path

    if args.write:
        out = write_output_pack(scenario_path)
        if args.json:
            print(json.dumps(out["evidence_map"], sort_keys=True, separators=(",", ":")))
        else:
            print(f"PASS: wrote Example County output pack ({out['evidence_map']['packet_count']} packet(s))")
        return 0 if out["smoke"].get("status") == "PASS" else 2

    scenario = load_json(scenario_path)
    smoke = build_smoke_report(scenario)
    evidence_map = build_evidence_map(scenario, smoke)
    if args.json:
        print(json.dumps(evidence_map, sort_keys=True, separators=(",", ":")))
    else:
        print(f"scenario={evidence_map['scenario_id']} version={evidence_map['archive_version']} status={evidence_map['smoke_status']} packets={evidence_map['packet_count']}")
    return 0 if smoke.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
