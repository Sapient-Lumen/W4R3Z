#!/usr/bin/env python3
"""scripts/check_operator_tools_smoke.py

Release-gate smoke tests for operator-facing helper tools.

Rationale:
The archive includes small “card” tools intended for copy/paste publication.
These tools have a narrow, user-visible contract: given a canonical example packet,
they must recompute digests cleanly and exit 0.

This keeps the operator UX from silently rotting under refactors.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
EXAMPLES = ROOT / "artifacts" / "examples"


def run(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def main() -> int:
    failures: list[str] = []

    # 1) PublicNotice digest card
    code, out, err = run(
        [
            sys.executable,
            str(TOOLS / "public_notice_card.py"),
            "--packet",
            str(EXAMPLES / "evidence_packet_public_notice"),
        ]
    )
    if code != 0:
        failures.append("public_notice_card failed")
        sys.stderr.write(out)
        sys.stderr.write(err)

    # 2) Implementation-scoped verifier report card
    code, out, err = run(
        [
            sys.executable,
            str(TOOLS / "verifier_report_card.py"),
            "--packet",
            str(EXAMPLES / "evidence_packet_verifier_report_minimal"),
        ]
    )
    if code != 0:
        failures.append("verifier_report_card failed")
        sys.stderr.write(out)
        sys.stderr.write(err)

    # 3) Packet-scoped verifier output card
    code, out, err = run(
        [
            sys.executable,
            str(TOOLS / "packet_verification_report_card.py"),
            "--packet",
            str(EXAMPLES / "evidence_packet_packet_verification_report_minimal"),
        ]
    )
    if code != 0:
        failures.append("packet_verification_report_card failed")
        sys.stderr.write(out)
        sys.stderr.write(err)

    # 4) observer_verify_packet: ensure --public --json path remains usable.
    code, out, err = run(
        [
            sys.executable,
            str(TOOLS / "observer_verify_packet.py"),
            str(EXAMPLES / "evidence_packet_minimal"),
            "--public",
            "--json",
        ]
    )
    if code != 0:
        failures.append("observer_verify_packet --public --json failed")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        try:
            json.loads(out)
        except Exception as e:
            failures.append(f"observer_verify_packet JSON parse failed: {e}")

    # 4b) public_surface_pins: should emit JSON and include the two verifier comparability pins.
    code, out, err = run(
        [
            sys.executable,
            str(TOOLS / "public_surface_pins.py"),
            "--json",
        ]
    )
    if code != 0:
        failures.append("public_surface_pins --json failed")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        try:
            o = json.loads(out)
            for k in ["envelope_kinds_sha256", "verifier_problem_codes_sha256"]:
                if k not in o:
                    failures.append(f"public_surface_pins missing key: {k}")
        except Exception as e:
            failures.append(f"public_surface_pins JSON parse failed: {e}")

    # 5) evidence_object_card: dispatch should work for operator-facing example packets.
    for pkt in [
        "evidence_packet_public_notice",
        "evidence_packet_verifier_report_minimal",
        "evidence_packet_packet_verification_report_minimal",
    ]:
        code, out, err = run(
            [
                sys.executable,
                str(TOOLS / "evidence_object_card.py"),
                "--packet",
                str(EXAMPLES / pkt),
            ]
        )
        if code != 0:
            failures.append(f"evidence_object_card failed for {pkt}")
            sys.stderr.write(out)
            sys.stderr.write(err)

    # 6) Path traversal hardening: packet_common MUST reject unsafe payload_pointer.uri.
    try:
        sys.path.insert(0, str(TOOLS))
        from packet_common import recompute_payload_digest  # type: ignore

        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            (tmp / "objects").mkdir(parents=True, exist_ok=True)
            unsafe_uris = [
                "../secrets.txt",
                "%2e%2e%2fsecrets.txt",
                "..%2Fsecrets.txt",
                "%2e%2e%5csecrets.txt",
            ]
            for u in unsafe_uris:
                env = {
                    "canonicalization": "RFC8785-JCS",
                    "payload_pointer": {"uri": u, "media_type": "application/json"},
                }
                try:
                    recompute_payload_digest(env, tmp / "objects")
                    failures.append(f"packet_common did not reject unsafe payload_pointer.uri: {u!r}")
                except SystemExit:
                    pass

            # Symlink escape hardening: reject packets where objects/ is a symlink out of the packet root.
            pkt = tmp / "pkt_symlink_escape"
            pkt.mkdir(parents=True, exist_ok=True)
            outside = tmp / "outside_objects"
            outside.mkdir(parents=True, exist_ok=True)
            fname = "sha256-" + ("a" * 64) + ".json"
            (outside / fname).write_text("{\"x\": 1}\n", encoding="utf-8")
            try:
                os.symlink(outside, pkt / "objects")
            except Exception:
                # If symlinks are unavailable in this environment, skip the test.
                pass
            else:
                env = {
                    "canonicalization": "RFC8785-JCS",
                    "payload_pointer": {"uri": fname, "media_type": "application/json"},
                }
                try:
                    recompute_payload_digest(env, pkt / "objects")
                    failures.append("packet_common did not reject objects/ symlink escape")
                except SystemExit:
                    pass
    except Exception as e:
        failures.append(f"packet_common import/smoke failed: {e}")

    if failures:
        for f in failures:
            print("ERROR:", f, file=sys.stderr)
        return 2

    print("PASS: operator tools smoke")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
