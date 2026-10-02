#!/usr/bin/env python3
"""Retain content-free evidence for one operator-selected sync restore drill."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
from pathlib import Path


SCHEMA = "iotox.sync-retained-recovery-drill.v1"
HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")


class DrillError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise DrillError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def hex_text(value: str) -> str:
    return value.encode("utf-8").hex().upper()


def validate_label(value: str, name: str) -> None:
    require(
        1 <= len(value.encode("utf-8")) <= 256,
        f"{name} must contain 1..256 bytes",
    )
    require(
        all(ord(byte) >= 0x20 and ord(byte) != 0x7F for byte in value),
        f"{name} contains a control byte",
    )


def provenance_tokens(args: argparse.Namespace) -> list[str]:
    labels = (
        args.backup_system,
        args.backup_generation,
        args.backup_failure_domain,
        args.restore_provenance,
    )
    present = [label is not None for label in labels]
    require(
        not any(present) or all(present),
        "backup provenance labels must be supplied all-or-none",
    )
    if not all(present):
        return []
    for field, name in (
        (args.backup_system, "backup-system"),
        (args.backup_generation, "backup-generation"),
        (args.backup_failure_domain, "backup-failure-domain"),
        (args.restore_provenance, "restore-provenance"),
    ):
        validate_label(field, name)
    return [
        f"backup-system={args.backup_system}",
        f"backup-generation={args.backup_generation}",
        f"backup-failure-domain={args.backup_failure_domain}",
        f"restore-provenance={args.restore_provenance}",
    ]


def parse_report(text: str) -> dict[str, str]:
    lines = text.splitlines()
    require(
        lines and lines[0] == "iotox-sync-recovery-verify-v1",
        "unexpected verifier report schema",
    )
    fields: dict[str, str] = {"report-schema": lines[0]}
    for line in lines[1:]:
        key, separator, value = line.partition("=")
        require(separator == "=" and key and value != "", "bad verifier report line")
        require(key not in fields, f"duplicate verifier report field: {key}")
        fields[key] = value
    return fields


def require_uint(fields: dict[str, str], name: str) -> int:
    value = fields.get(name, "")
    require(value.isdigit(), f"{name} is absent or not unsigned")
    return int(value)


def require_sha(fields: dict[str, str], name: str) -> str:
    value = fields.get(name, "")
    require(HEX64.fullmatch(value) is not None, f"{name} is not a SHA-256 hex")
    return value.lower()


def validate_report(
    fields: dict[str, str], operator_provenance: list[str]
) -> dict[str, object]:
    decision = fields.get("decision")
    require(decision in ("match", "mismatch"), "verifier decision is invalid")
    require(fields.get("model") == "tree-v2-owner-mode-v2", "unexpected model")
    require(
        fields.get("filesystem-contract") == "ready"
        and fields.get("stable-double-scan") == "ready"
        and fields.get("iotox-live-state-read") == "0",
        "verifier did not emit its strict recovery contract",
    )
    require(
        fields.get("backup-independence") == "not-assessed"
        and fields.get("restore-provenance") == "not-assessed",
        "verifier overclaimed backup independence or restore provenance",
    )
    if operator_provenance:
        require(
            fields.get("operator-provenance") == "present",
            "operator provenance was not retained",
        )
        for token in operator_provenance:
            key, value = token.split("=", 1)
            require(
                fields.get(f"{key}-hex") == hex_text(value),
                f"{key} was not bound into the verifier report",
            )
    else:
        require(
            fields.get("operator-provenance") == "absent",
            "unexpected operator provenance state",
        )

    backup_files = require_uint(fields, "backup-files")
    restored_files = require_uint(fields, "restored-files")
    backup_entries = require_uint(fields, "backup-entries")
    restored_entries = require_uint(fields, "restored-entries")
    backup_bytes = require_uint(fields, "backup-bytes")
    restored_bytes = require_uint(fields, "restored-bytes")
    return {
        "decision": decision,
        "backup_manifest": require_sha(fields, "backup-manifest"),
        "restored_manifest": require_sha(fields, "restored-manifest"),
        "backup_directories": require_uint(fields, "backup-directories"),
        "restored_directories": require_uint(fields, "restored-directories"),
        "backup_files": backup_files,
        "restored_files": restored_files,
        "backup_entries": backup_entries,
        "restored_entries": restored_entries,
        "backup_bytes": backup_bytes,
        "restored_bytes": restored_bytes,
        "maximum_bytes": require_uint(fields, "maximum-bytes"),
        "maximum_entries": require_uint(fields, "maximum-entries"),
        "root_devices_differ": require_uint(fields, "root-devices-differ"),
        "operator_provenance": fields.get("operator-provenance", "absent"),
        "backup_path_hex_sha256": sha256_text(fields.get("backup-path-hex", "")),
        "restored_path_hex_sha256": sha256_text(
            fields.get("restored-path-hex", "")
        ),
    }


def write_json_atomic(path: Path, record: dict[str, object]) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n",
                         encoding="utf-8")
    temporary.chmod(0o600)
    os.replace(temporary, path)


def run_drill(args: argparse.Namespace) -> dict[str, object]:
    iotox = args.iotox.resolve()
    evidence = args.evidence.resolve()
    backup = args.backup_root.resolve()
    restored = args.restored_root.resolve()
    require(iotox.is_file(), "IoTox binary is absent")
    for path, name in ((backup, "backup root"), (restored, "restored root")):
        metadata = path.lstat()
        require(stat.S_ISDIR(metadata.st_mode), f"{name} is not a directory")
    require(backup != restored, "backup and restored roots are identical")
    require(
        backup not in restored.parents and restored not in backup.parents,
        "backup and restored roots must be disjoint",
    )
    operator_provenance = provenance_tokens(args)
    command = [
        str(iotox),
        "sync-recovery-verify",
        str(backup),
        str(restored),
        str(args.maximum_bytes),
        str(args.maximum_entries),
        *operator_provenance,
    ]
    result = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=args.timeout,
        check=False,
    )
    report_text = result.stdout
    if not report_text.startswith("iotox-sync-recovery-verify-v1\n"):
        if result.returncode == 0:
            raise DrillError("sync-recovery-verify returned success without a v1 report")
        failure = f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        record = {
            "schema": SCHEMA,
            "status": "rejected",
            "failure_kind": "iotox-command-rejected",
            "return_code": result.returncode,
            "stdout_bytes": len(result.stdout.encode("utf-8")),
            "stderr_bytes": len(result.stderr.encode("utf-8")),
            "failure_sha256": sha256_text(failure),
            "iotox_binary_sha256": sha256_file(iotox),
            "contains_secrets": False,
        }
        write_json_atomic(evidence, record)
        return record
    fields = parse_report(report_text)
    validated = validate_report(fields, operator_provenance)
    operator_requirement_satisfied = (
        not args.require_operator_provenance or bool(operator_provenance)
    )
    device_requirement_satisfied = (
        not args.require_different_device
        or validated["root_devices_differ"] == 1
    )
    local_requirements_satisfied = (
        validated["decision"] == "match"
        and operator_requirement_satisfied
        and device_requirement_satisfied
    )
    status = "passed" if local_requirements_satisfied else "rejected"
    record: dict[str, object] = {
        "schema": SCHEMA,
        "status": status,
        "iotox_return_code": result.returncode,
        "report_sha256": sha256_text(report_text),
        "iotox_binary_sha256": sha256_file(iotox),
        "operator_provenance_bound": bool(operator_provenance),
        "operator_provenance_required": bool(args.require_operator_provenance),
        "different_device_required": bool(args.require_different_device),
        "operator_requirement_satisfied": operator_requirement_satisfied,
        "device_requirement_satisfied": device_requirement_satisfied,
        "local_requirements_satisfied": local_requirements_satisfied,
        "backup_independence": "operator-evidence-required",
        "restore_provenance_assessment": "operator-evidence-required",
        "contains_secrets": False,
        **validated,
    }
    if operator_provenance:
        record.update(
            {
                "backup_system_sha256": sha256_text(args.backup_system),
                "backup_generation_sha256": sha256_text(args.backup_generation),
                "backup_failure_domain_sha256": sha256_text(
                    args.backup_failure_domain
                ),
                "restore_provenance_sha256": sha256_text(
                    args.restore_provenance
                ),
            }
        )
    write_json_atomic(evidence, record)
    return record


def self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="iotox-retained-recovery-drill-") as raw:
        root = Path(raw)
        backup = root / "backup"
        restored = root / "restored"
        backup.mkdir(mode=0o700)
        restored.mkdir(mode=0o700)
        fake = root / "iotox"
        fake.write_text(
            """#!/usr/bin/env python3
import sys
def hx(value):
    return value.encode("utf-8").hex().upper()
args = sys.argv[1:]
tokens = [arg for arg in args if "=" in arg]
decision = "mismatch" if any("mismatch" in arg for arg in args) else "match"
print("iotox-sync-recovery-verify-v1")
print("decision=" + decision)
print("model=tree-v2-owner-mode-v2")
print("backup-path-hex=2F6261636B7570")
print("restored-path-hex=2F726573746F726564")
print("backup-manifest=" + "11" * 32)
print("restored-manifest=" + ("22" * 32 if decision == "mismatch" else "11" * 32))
print("backup-directories=0")
print("backup-files=1")
print("backup-entries=1")
print("backup-bytes=4")
print("restored-directories=0")
print("restored-files=1")
print("restored-entries=1")
print("restored-bytes=4")
print("maximum-bytes=" + args[3])
print("maximum-entries=" + args[4])
print("root-devices-differ=0")
print("filesystem-contract=ready")
print("stable-double-scan=ready")
print("iotox-live-state-read=0")
print("operator-provenance=" + ("present" if tokens else "absent"))
for token in tokens:
    key, value = token.split("=", 1)
    print(key + "-hex=" + hx(value))
print("backup-independence=not-assessed")
print("restore-provenance=not-assessed")
if decision == "mismatch":
    sys.exit(4)
""",
            encoding="utf-8",
        )
        fake.chmod(0o700)
        evidence = root / "receipt.json"
        namespace = argparse.Namespace(
            iotox=fake,
            backup_root=backup,
            restored_root=restored,
            evidence=evidence,
            maximum_bytes=64 * 1024 * 1024,
            maximum_entries=4096,
            backup_system="restic",
            backup_generation="snapshot-1",
            backup_failure_domain="external-disk",
            restore_provenance="manual-restore",
            require_operator_provenance=True,
            require_different_device=False,
            timeout=10,
        )
        record = run_drill(namespace)
        require(record["status"] == "passed", "valid retained drill failed")
        require(record["operator_provenance_bound"] is True,
                "provenance was not bound")
        require(record["operator_requirement_satisfied"] is True,
                "operator provenance requirement was not satisfied")
        require(evidence.is_file(), "receipt was not written")

        missing_evidence = root / "missing-provenance.json"
        missing = argparse.Namespace(
            iotox=fake,
            backup_root=backup,
            restored_root=restored,
            evidence=missing_evidence,
            maximum_bytes=64 * 1024 * 1024,
            maximum_entries=4096,
            backup_system=None,
            backup_generation=None,
            backup_failure_domain=None,
            restore_provenance=None,
            require_operator_provenance=True,
            require_different_device=False,
            timeout=10,
        )
        missing_record = run_drill(missing)
        require(
            missing_record["status"] == "rejected",
            "missing required provenance did not reject",
        )
        require(
            missing_record["local_requirements_satisfied"] is False,
            "missing required provenance was marked locally satisfied",
        )

        mismatch_backup = root / "mismatch-backup"
        mismatch_restored = root / "mismatch-restored"
        mismatch_backup.mkdir(mode=0o700)
        mismatch_restored.mkdir(mode=0o700)
        mismatch_evidence = root / "mismatch.json"
        mismatch = argparse.Namespace(
            iotox=fake,
            backup_root=mismatch_backup,
            restored_root=mismatch_restored,
            evidence=mismatch_evidence,
            maximum_bytes=64 * 1024 * 1024,
            maximum_entries=4096,
            backup_system="restic",
            backup_generation="snapshot-1",
            backup_failure_domain="external-disk",
            restore_provenance="manual-restore",
            require_operator_provenance=True,
            require_different_device=False,
            timeout=10,
        )
        mismatch_record = run_drill(mismatch)
        require(
            mismatch_record["status"] == "rejected",
            "mismatch report did not reject",
        )
        require(
            mismatch_record["decision"] == "mismatch"
            and mismatch_record["iotox_return_code"] == 4,
            "nonzero structured report was not retained",
        )
        require(
            "failure_kind" not in mismatch_record,
            "structured mismatch was retained as opaque failure",
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("backup_root", type=Path, nargs="?")
    parser.add_argument("restored_root", type=Path, nargs="?")
    parser.add_argument("--iotox", type=Path, default=Path("build/iotox"))
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--maximum-bytes", type=int, default=64 * 1024 * 1024)
    parser.add_argument("--maximum-entries", type=int, default=4096)
    parser.add_argument("--backup-system")
    parser.add_argument("--backup-generation")
    parser.add_argument("--backup-failure-domain")
    parser.add_argument("--restore-provenance")
    parser.add_argument("--require-operator-provenance", action="store_true")
    parser.add_argument("--require-different-device", action="store_true")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("sync-retained-recovery-drill-self-test=pass")
        return 0
    if args.backup_root is None or args.restored_root is None:
        parser.error("BACKUP_ROOT and RESTORED_ROOT are required")
    if args.evidence is None:
        parser.error("--evidence is required")
    require(1 <= args.maximum_bytes <= 1 << 60,
            "maximum bytes are outside the supported range")
    require(1 <= args.maximum_entries <= 1 << 32,
            "maximum entries are outside the supported range")
    require(1 <= args.timeout <= 3600, "timeout is invalid")
    try:
        record = run_drill(args)
    except (DrillError, OSError, subprocess.SubprocessError) as error:
        print(f"sync retained recovery drill failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(record, indent=2, sort_keys=True))
    return 0 if record["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
