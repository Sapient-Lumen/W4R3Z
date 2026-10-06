#!/usr/bin/env python3
"""Guard the real FreeBSD host-proof operator preflight.

The scarce resource is not another schema: it is a successful real host run.  The
collector must fail fast, before mdconfig/mount authority, when the host is not a
supported FreeBSD root environment with Capsicum feature sysctls and required
proof tools available.  This checker proves the Linux cloudtainer refusal path
and the static wiring into the real collector/proof-tool contract.
"""
from __future__ import annotations

import platform
import subprocess
import sys
from pathlib import Path

from freebsd import host_proof_contract as contract

ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT_REL = contract.HOST_PROOF_PREFLIGHT_REL
COLLECTOR_REL = contract.HOST_SMOKE_COLLECTOR_REL
DOC_REL = "docs/current/removable-media-freebsd-host-smoke.md"
START_REL = "docs/current/start-here-now.md"


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def run_preflight() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(ROOT / PREFLIGHT_REL)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def execution_errors() -> list[str]:
    errors: list[str] = []
    if platform.system() != "FreeBSD":
        proc = run_preflight()
        require(errors, proc.returncode != 0, "preflight must refuse non-FreeBSD hosts in the cloudtainer")
        require(errors, "requires FreeBSD host" in proc.stderr, "non-FreeBSD refusal should name the FreeBSD requirement")
    return errors


def surface_errors() -> list[str]:
    errors: list[str] = []
    preflight = ROOT / PREFLIGHT_REL
    collector = ROOT / COLLECTOR_REL
    require(errors, preflight.exists(), f"missing {PREFLIGHT_REL}")
    require(errors, collector.exists(), f"missing {COLLECTOR_REL}")
    if preflight.exists():
        text = preflight.read_text(encoding="utf-8", errors="replace")
        for token in [
            "requires FreeBSD host",
            "requires root",
            "kern.osreldate",
            "kern.features.security_capability_mode",
            "kern.features.security_capabilities",
            "/usr/bin/cc",
            "/usr/sbin/makefs",
            "/sbin/mdconfig",
            "/usr/sbin/fstyp",
            "host_proof_contract",
            "SUPPORTED_FREEBSD_RELEASE_FLOOR",
            "PRIMARY_FREEBSD_RELEASE",
            "HOST_TARGET_MATRIX_ID",
            "CONTRACT_VALUES",
            "set -- $CONTRACT_VALUES",
            "target_tier",
            "primary-production",
            "supported-legacy-floor",
            "invoice.pdf",
            "seal_removable_media_local_fallback_host_proof_handoff.py",
            "unseal_removable_media_local_fallback_host_proof_handoff.py",
            "handoff sealer",
            "handoff unsealer",
            "--help",
        ]:
            require(errors, token in text, f"{PREFLIGHT_REL} missing preflight token {token!r}")
    if collector.exists():
        text = collector.read_text(encoding="utf-8", errors="replace")
        preflight_idx = text.find(PREFLIGHT_REL)
        runner_idx = text.find(contract.HOST_SMOKE_RUNNER_REL)
        require(errors, preflight_idx >= 0, "collector must invoke the preflight script")
        require(errors, runner_idx >= 0, "collector must still invoke the host-smoke runner")
        require(errors, 0 <= preflight_idx < runner_idx, "collector must run preflight before host-smoke runner")
        require(errors, "DERIVEBSD_SKIP_HOST_PROOF_PREFLIGHT" not in text, "collector must not include a skip-preflight bypass")
        for banned in ["--allow-checker-simulation", "--allow-refusal", "--allow-failed"]:
            require(errors, banned not in text, f"collector must not contain non-proof token {banned!r}")
    contract_text = (ROOT / contract.HOST_PROOF_CONTRACT_REL).read_text(encoding="utf-8", errors="replace")
    require(errors, "HOST_PROOF_PREFLIGHT_REL" in contract_text, "shared proof-tool contract must name the preflight script")
    require(errors, PREFLIGHT_REL in contract_text, "preflight script must be part of the bound proof-tool set")
    for rel in [DOC_REL, START_REL]:
        doc = ROOT / rel
        require(errors, doc.exists(), f"missing {rel}")
        if doc.exists():
            text = doc.read_text(encoding="utf-8", errors="replace")
            for token in [PREFLIGHT_REL, "preflight", "kern.osreldate", "Capsicum", "host_target_tier", "15.1-RELEASE"]:
                require(errors, token in text, f"{rel} missing preflight token {token!r}")
    return errors


def main() -> int:
    errors = execution_errors() + surface_errors()
    if errors:
        print("FreeBSD host proof preflight check FAILED.")
        for error in errors:
            print("-", error)
        return 1
    print("FreeBSD host proof preflight check OK")
    print("Collector now fails fast on unsupported/non-root/non-Capsicum hosts before mdconfig/mount authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
