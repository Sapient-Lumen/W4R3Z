#!/usr/bin/env python3
"""Smoke-check measurement tools for fail-closed, schema-shaped behavior."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
EXAMPLES = ROOT / "artifacts" / "examples"


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)


def fail(msg: str, proc: subprocess.CompletedProcess[str] | None = None) -> int:
    print("FAIL:", msg, file=sys.stderr)
    if proc is not None:
        if proc.stdout:
            print(proc.stdout, file=sys.stderr)
        if proc.stderr:
            print(proc.stderr, file=sys.stderr)
    return 2


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="tes_measurement_tools_") as td:
        tmp = Path(td)
        atlas_out = tmp / "atlas"
        proc = run([
            sys.executable,
            str(TOOLS / "atlas_urp_generator.py"),
            "--plan",
            str(EXAMPLES / "atlas_measurement_plan_example.json"),
            "--ethics",
            str(EXAMPLES / "ethics_guardrails_policy_example.json"),
            "--outdir",
            str(atlas_out),
            "--start",
            "1771696800",
            "--stop",
            "1771697400",
        ])
        if proc.returncode != 0:
            return fail("atlas dry-run failed", proc)
        receipt = json.loads((atlas_out / "AtlasMeasurementReceipt.json").read_text(encoding="utf-8"))
        payload = json.loads((atlas_out / "ripe_atlas_create_payload.json").read_text(encoding="utf-8"))
        if receipt.get("created_measurement_ids") != [] or "dry_run" not in str(receipt.get("notes")):
            return fail("atlas dry-run did not remain non-creating", proc)
        if not payload.get("definitions") or not payload.get("probes"):
            return fail("atlas create payload is still empty after refactor", proc)

        proc = run([
            sys.executable,
            str(TOOLS / "atlas_urp_generator.py"),
            "--plan",
            str(EXAMPLES / "atlas_measurement_plan_example.json"),
            "--ethics",
            str(EXAMPLES / "ethics_guardrails_policy_example.json"),
            "--outdir",
            str(tmp / "atlas_create_blocked"),
            "--start",
            "1771696800",
            "--stop",
            "1771697400",
            "--create",
        ])
        if proc.returncode == 0 or "--operator-reviewed-payload" not in proc.stderr:
            return fail("atlas --create did not fail closed without explicit operator-reviewed payload", proc)

        ooni_out = tmp / "ooni.json"
        proc = run([
            sys.executable,
            str(TOOLS / "ooni_corroborator.py"),
            "--out",
            str(ooni_out),
            "--country",
            "US",
            "--asn",
            "AS7922",
            "--test-name",
            "web_connectivity",
            "--from",
            "2026-02-21T14:00:00Z",
            "--to",
            "2026-02-21T18:00:00Z",
        ])
        if proc.returncode != 0:
            return fail("OONI dry-run failed", proc)
        ooni = json.loads(ooni_out.read_text(encoding="utf-8"))
        if set(ooni.keys()) != {"window", "filters", "summary", "pointers"}:
            return fail("OONI output has schema-hostile top-level fields", proc)
        if ooni.get("summary", {}).get("status") != "dry_run_no_api_query":
            return fail("OONI default path did not remain dry-run/no-network", proc)
        if ooni.get("summary", {}).get("raw_measurements_embedded") is not False:
            return fail("OONI output must not embed raw measurement bodies", proc)

    print("PASS: measurement tool boundaries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
