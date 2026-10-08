#!/usr/bin/env python3
"""Verify the synthetic Example County output pack is fresh and non-claiming."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = ROOT / "artifacts/examples/example_county_2026_municipal_pilot/scenario.json"
OUTDIR = SCENARIO.parent
TOOL = ROOT / "tools/example_county_output_pack.py"
VERSION = ROOT / "VERSION"
REQUIRED = {
    "evidence-map.json",
    "smoke-report.json",
    "court-packet-index.csv",
    "public-verifier-quickstart.md",
}
NON_CLAIM_PHRASES = [
    "not live election evidence",
    "does not prove that an election outcome is correct",
    "does not turn missingness",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def run_tool_to_temp() -> dict[str, bytes]:
    with tempfile.TemporaryDirectory(prefix="tes_output_pack_check_") as td:
        tmp_root = Path(td) / "repo"
        # Copy only the files the tool writes so we can compare deterministic output
        # without mutating the working tree during a check.
        # The tool itself writes to the repo path, so instead snapshot current bytes,
        # run it, read the new bytes, and restore on mismatch-safe best effort.
        before = {name: (OUTDIR / name).read_bytes() if (OUTDIR / name).exists() else b"" for name in REQUIRED}
        proc = subprocess.run([sys.executable, str(TOOL), "--write"], cwd=ROOT, stdin=subprocess.DEVNULL, text=True, capture_output=True, timeout=120)
        after = {name: (OUTDIR / name).read_bytes() if (OUTDIR / name).exists() else b"" for name in REQUIRED}
        # Restore exact bytes; this check is not the writer of record.
        for name, data in before.items():
            (OUTDIR / name).write_bytes(data)
        if proc.returncode != 0:
            raise RuntimeError(f"output-pack tool failed rc={proc.returncode}: {proc.stdout} {proc.stderr}")
        return after


def main() -> int:
    errors: list[str] = []
    version = VERSION.read_text(encoding="utf-8").strip()

    if not TOOL.exists():
        errors.append("missing tools/example_county_output_pack.py")
    if not SCENARIO.exists():
        errors.append("missing scenario.json")

    for name in REQUIRED:
        if not (OUTDIR / name).exists():
            errors.append(f"missing output-pack file: {name}")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2

    try:
        generated = run_tool_to_temp()
    except Exception as exc:
        print("ERROR:", exc, file=sys.stderr)
        return 2
    for name, got in generated.items():
        have = (OUTDIR / name).read_bytes()
        if got != have:
            errors.append(f"output-pack drift: {name}; run `python3 tools/example_county_output_pack.py --write`")

    scenario = load_json(SCENARIO)
    evidence = load_json(OUTDIR / "evidence-map.json")
    smoke = load_json(OUTDIR / "smoke-report.json")
    if scenario.get("archive_version") != version:
        errors.append("scenario archive_version does not match VERSION")
    if evidence.get("archive_version") != version:
        errors.append("evidence-map archive_version does not match VERSION")
    if smoke.get("archive_version") != version:
        errors.append("smoke-report archive_version does not match VERSION")
    if evidence.get("scenario_id") != scenario.get("scenario_id"):
        errors.append("evidence-map scenario_id does not match scenario")
    if smoke.get("scenario_id") != scenario.get("scenario_id"):
        errors.append("smoke-report scenario_id does not match scenario")
    if smoke.get("status") != "PASS":
        errors.append("smoke-report status must be PASS")

    packets = []
    for phase in evidence.get("phases") or []:
        if isinstance(phase, dict):
            packets.extend([p for p in (phase.get("packets") or []) if isinstance(p, dict)])
    if evidence.get("packet_count") != len(packets):
        errors.append("evidence-map packet_count does not match listed packets")
    for p in packets:
        rel = str(p.get("path") or "")
        manifest = ROOT / rel / "manifest.json"
        if not manifest.exists():
            errors.append(f"packet manifest missing: {rel}")
            continue
        if p.get("manifest_sha256") != sha256_file(manifest):
            errors.append(f"manifest_sha256 drift for {rel}")
        if p.get("verification_status") != "PASS":
            errors.append(f"packet verification status is not PASS: {rel}")

    with (OUTDIR / "court-packet-index.csv").open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != len(packets):
        errors.append("court-packet-index row count does not match packet count")
    seen_ids: set[str] = set()
    for r in rows:
        pid = (r.get("packet_id") or "").strip()
        if not pid:
            errors.append("court-packet-index row missing packet_id")
        if pid in seen_ids:
            errors.append(f"court-packet-index duplicate packet_id {pid}")
        seen_ids.add(pid)
        if r.get("verification_status") != "PASS":
            errors.append(f"court-packet-index packet not PASS: {pid}")
        nc = (r.get("non_claim") or "").lower()
        for phrase in ["not outcome certification", "not", "intent/fraud"]:
            if phrase not in nc:
                errors.append(f"court-packet-index non_claim too weak for {pid}")
                break

    quick = (OUTDIR / "public-verifier-quickstart.md").read_text(encoding="utf-8").lower()
    for phrase in NON_CLAIM_PHRASES:
        if phrase not in quick:
            errors.append(f"quickstart missing non-claim phrase: {phrase}")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    print(f"PASS: Example County output pack ({version}, {len(packets)} packet(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
