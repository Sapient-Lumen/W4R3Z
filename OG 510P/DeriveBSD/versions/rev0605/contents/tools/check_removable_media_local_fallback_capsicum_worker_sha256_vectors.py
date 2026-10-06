#!/usr/bin/env python3
"""Run fd-only SHA-256 execution vectors for the FreeBSD Capsicum worker.

The cloudtainer cannot prove real FreeBSD Capsicum execution, but it can compile
and execute the C worker through the named probe shim.  This check exercises the
worker-reported input_sha256 path across SHA-256 padding/block-boundary cases so
host-smoke cannot later rely on an under-tested embedded digest implementation.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import removable_media_capsicum_worker_bridge as bridge
import removable_media_fd_slot_launcher as fd_slots

ROOT = Path(__file__).resolve().parents[1]
VALIDATION_REL = "validation/removable-media-capsicum-worker-sha256-vectors.json"
VALIDATION = ROOT / VALIDATION_REL
VECTOR_CASES: list[tuple[str, bytes]] = [
    ("empty", b""),
    ("one-byte", b"x"),
    ("sha-padding-55", b"a" * 55),
    ("sha-padding-56", b"b" * 56),
    ("one-block-64", bytes(range(64))),
    ("block-plus-one-65", bytes(range(65))),
    ("multi-block-4097", (b"DeriveBSD fd-only worker digest vector\n" * 114) + b"tail"),
]


def fail(messages: list[str] | str) -> int:
    print("Capsicum worker SHA-256 vector check FAILED.")
    if isinstance(messages, str):
        messages = [messages]
    for message in messages:
        print(f"- {message}")
    return 1


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def run_vector(binary: Path, tmpdir: Path, name: str, payload: bytes) -> dict[str, Any]:
    input_path = tmpdir / f"{name}.input.bin"
    output_path = tmpdir / f"{name}.worker-output.json"
    canary_path = tmpdir / f"{name}.broker-nonmedia-fd5-canary"
    input_path.write_bytes(payload)
    canary_path.write_text("broker-owned non-media inherited-fd canary\n", encoding="utf-8")

    slot_guard = fd_slots.FdSlotGuard(fd_slots.TARGET_FDS).save_and_clear()
    input_fd: int | None = os.open(input_path, os.O_RDONLY)
    output_fd: int | None = os.open(output_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    canary_fd: int | None = os.open(canary_path, os.O_RDONLY)
    try:
        slot_guard.install_owned_fd(input_fd, 3)
        input_fd = None
        slot_guard.install_owned_fd(output_fd, 4)
        output_fd = None
        slot_guard.install_owned_fd(canary_fd, 5)
        canary_fd = None
        try:
            proc = subprocess.run(
                [str(binary)],
                cwd=ROOT,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10,
                check=False,
                pass_fds=(3, 4, 5),
            )
            stdout = proc.stdout or ""
            stderr = proc.stderr or ""
            return_code = int(proc.returncode)
            timed_out = False
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""
            if isinstance(stdout, bytes):
                stdout = stdout.decode("utf-8", errors="replace")
            if isinstance(stderr, bytes):
                stderr = stderr.decode("utf-8", errors="replace")
            stderr = (str(stderr) + "\n" if stderr else "") + "TIMEOUT after 10 seconds"
            return_code = 124
            timed_out = True
    finally:
        slot_guard.restore()
        for fd in (input_fd, output_fd, canary_fd):
            if fd is not None:
                try:
                    os.close(fd)
                except OSError:
                    pass
    slot_evidence = slot_guard.evidence()

    output_bytes = output_path.read_bytes() if output_path.exists() else b""
    output_text = output_bytes.decode("utf-8", errors="replace")
    try:
        report: dict[str, Any] | None = json.loads(output_text) if output_text.strip() else None
        parse_error = None
    except json.JSONDecodeError as exc:
        report = None
        parse_error = str(exc)

    return {
        "case": name,
        "input_size_bytes": len(payload),
        "expected_input_sha256": sha256_bytes(payload),
        "return_code": return_code,
        "timed_out": timed_out,
        "stdout_bytes": len(stdout.encode("utf-8", errors="replace")),
        "stderr_bytes": len(stderr.encode("utf-8", errors="replace")),
        "stdout_sha256": sha256_bytes(stdout.encode("utf-8", errors="replace")),
        "stderr_sha256": sha256_bytes(stderr.encode("utf-8", errors="replace")),
        "output_report_sha256": sha256_bytes(output_bytes),
        "output_report_bytes": len(output_bytes),
        "output_report": report,
        "output_parse_error": parse_error,
        "pass_fds": [3, 4, 5],
        "extra_fd_canary": 5,
        "extra_fd_canary_source": "broker-nonmedia-canary-not-source-media",
        "launcher_fd_slot_policy": fd_slots.POLICY,
        "launcher_fd_slot_evidence": slot_evidence,
        "launcher_restored_parent_fd_slots": slot_evidence.get("preexisting_parent_fd_slots_preserved") is True,
        "launcher_preserved_parent_fd_inheritable_flags": slot_evidence.get("preexisting_parent_fd_inheritable_flags_preserved") is True,
    }


def build_binary(binary_path: Path) -> dict[str, Any]:
    result = bridge._run_compile_for_execution_probe(binary_path)  # shared command template; intentionally private to bridge module
    return result


def validate_vector(row: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    report = row.get("output_report") if isinstance(row.get("output_report"), dict) else {}
    prefix = f"{row.get('case')}: "
    checks = [
        (row.get("return_code") == 0, "worker must exit 0"),
        (row.get("timed_out") is False, "worker must not time out"),
        (row.get("stdout_bytes") == 0, "worker must not write stdout"),
        (row.get("stderr_bytes") == 0, "worker must not write stderr"),
        (row.get("output_parse_error") is None, "worker output must parse as JSON"),
        (report.get("result") == "passed", "worker report must pass"),
        (report.get("input_bytes") == row.get("input_size_bytes"), "worker input byte count must match vector"),
        (report.get("input_sha256") == row.get("expected_input_sha256"), "worker input_sha256 must match Python hashlib"),
        (report.get("extra_fd_canary_observed_before_closefrom") is True, "worker must observe fd-5 canary before closefrom"),
        (report.get("extra_fds_closed_before_cap_enter") is True, "worker must close extra fds before cap_enter"),
        (report.get("stdio_fds_closed_before_cap_enter") is True, "worker must close stdio before cap_enter"),
        (row.get("pass_fds") == [3, 4, 5], "probe must pass fd 5 into child"),
        (row.get("launcher_fd_slot_policy") == fd_slots.POLICY, "vector probe must use shared fd-slot launcher"),
        (row.get("launcher_restored_parent_fd_slots") is True, "vector probe must restore parent fd slots"),
        (row.get("launcher_preserved_parent_fd_inheritable_flags") is True, "vector probe must restore parent fd inheritability flags"),
    ]
    for ok, message in checks:
        if not ok:
            errors.append(prefix + message)
    return errors


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="derivebsd-capsicum-sha256-vectors-") as td:
        tmpdir = Path(td)
        binary = tmpdir / bridge.BINARY_BASENAME
        compile_result = build_binary(binary)
        vectors: list[dict[str, Any]] = []
        errors: list[str] = []
        if compile_result.get("return_code") != 0 or compile_result.get("timed_out") is not False:
            errors.append("probe executable compile failed")
        else:
            for name, payload in VECTOR_CASES:
                row = run_vector(binary, tmpdir, name, payload)
                vectors.append(row)
                errors.extend(validate_vector(row))

    receipt = {
        "kind": "removable.media.capsicum.worker.sha256.vector.probe",
        "schema_version": "0.1",
        "generated_for_version": bridge.VERSION,
        "bridge_id": bridge.BRIDGE_ID,
        "claim": "cloudtainer-shim-execution-probe-not-capsicum-execution",
        "source": {
            "path": bridge.SOURCE_REL,
            "sha256": bridge.sha256_file(bridge.SOURCE),
            "probe_shim": bridge.SHIM_REL,
            "probe_define": "DERIVEBSD_CAPSICUM_COMPILE_PROBE",
        },
        "compile_result": compile_result,
        "vector_count": len(VECTOR_CASES),
        "vectors": vectors,
        "invariants": {
            "covers_empty_input": any(row.get("case") == "empty" for row in vectors),
            "covers_sha256_padding_55_56": {"sha-padding-55", "sha-padding-56"}.issubset({str(row.get("case")) for row in vectors}),
            "covers_block_boundary_64_65": {"one-block-64", "block-plus-one-65"}.issubset({str(row.get("case")) for row in vectors}),
            "all_vectors_passed": not errors,
            "fd5_canary_passed_to_child_for_all_vectors": all(row.get("pass_fds") == [3, 4, 5] for row in vectors),
            "shared_fd_slot_launcher_used_for_all_vectors": all(row.get("launcher_fd_slot_policy") == fd_slots.POLICY for row in vectors),
            "parent_fd_inheritable_flags_preserved_for_all_vectors": all(row.get("launcher_preserved_parent_fd_inheritable_flags") is True for row in vectors),
        },
        "result": "passed" if not errors else "failed",
    }
    VALIDATION.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if errors:
        return fail(errors)
    print("Capsicum worker SHA-256 vector check OK")
    print(f"Vectors: {len(vectors)} worker-reported input_sha256 values matched Python hashlib across padding/block-boundary cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
