#!/usr/bin/env python3
"""Syntax-build guard for the FreeBSD Capsicum fd-only worker scaffold.

The cloudtainer cannot prove FreeBSD Capsicum execution.  This check performs a
syntax-only compile using the same probe command generator as the durable
Capsicum worker bridge receipt.  Keeping the command in one implementation path
prevents the checker from passing a different compile than the bridge records.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import removable_media_capsicum_worker_bridge as bridge

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / bridge.SOURCE_REL
SHIM = ROOT / bridge.SHIM_REL
VALIDATION = ROOT / "validation" / "removable-media-capsicum-worker-build-probe.receipt.json"


def fail(message: str) -> int:
    print("Capsicum worker syntax-build check FAILED.")
    print(f"- {message}")
    return 1


def write_probe_receipt(result: dict[str, Any]) -> None:
    receipt = {
        "kind": "removable.media.capsicum.worker.build.probe",
        "schema_version": "0.1",
        "generated_for_version": bridge.VERSION,
        "bridge_id": bridge.BRIDGE_ID,
        "source": {
            "path": bridge.SOURCE_REL,
            "sha256": bridge.sha256_file(SOURCE),
            "probe_shim": bridge.SHIM_REL,
            "probe_define": "DERIVEBSD_CAPSICUM_COMPILE_PROBE",
        },
        "claim": "cloudtainer-syntax-probe-only-not-capsicum-execution",
        "command_result": result,
        "result": "passed" if result.get("return_code") == 0 and result.get("timed_out") is False else "failed",
    }
    VALIDATION.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    if not SOURCE.exists():
        return fail(f"missing {SOURCE.relative_to(ROOT)}")
    if not SHIM.exists():
        return fail(f"missing {SHIM.relative_to(ROOT)}")

    text = SOURCE.read_text(encoding="utf-8", errors="replace")
    shim_text = SHIM.read_text(encoding="utf-8", errors="replace")
    for token in [
        "#ifdef __FreeBSD__",
        "#include <sys/capsicum.h>",
        "DERIVEBSD_CAPSICUM_COMPILE_PROBE",
        "#error",
    ]:
        if token not in text:
            return fail(f"source missing build-gate token {token!r}")
    for token in ["not a Capsicum implementation", "cap_rights_limit", "cap_enter", "#define closefrom"]:
        if token not in shim_text:
            return fail(f"probe shim missing token {token!r}")

    cmd = bridge.probe_compile_command()
    if cmd is None:
        result = bridge.run_cloudtainer_compile_probe()
        write_probe_receipt(result)
        return fail("no C compiler available for syntax-only probe")

    expected = bridge.production_build_command_template()
    if "-DDERIVEBSD_CAPSICUM_COMPILE_PROBE=1" not in cmd:
        return fail("shared probe command is missing the named compile-probe define")
    if "DERIVEBSD_CAPSICUM_COMPILE_PROBE" in " ".join(expected):
        return fail("production build command template must not include the cloudtainer probe define")

    result = bridge.run_cloudtainer_compile_probe()
    write_probe_receipt(result)
    if result.get("return_code") != 0 or result.get("timed_out") is not False:
        print("Capsicum worker syntax-build check FAILED.")
        print("- command:", " ".join(result.get("command", [])))
        print("- stdout_sha256:", result.get("stdout_sha256"))
        print("- stderr_sha256:", result.get("stderr_sha256"))
        return 1

    print("Capsicum worker syntax-build check OK")
    print("Probe: shared bridge command syntax-checks the FreeBSD-only worker with DERIVEBSD_CAPSICUM_COMPILE_PROBE shim")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
