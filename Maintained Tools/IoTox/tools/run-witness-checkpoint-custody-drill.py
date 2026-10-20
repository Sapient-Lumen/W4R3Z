#!/usr/bin/env python3
"""Retain content-free evidence for one witness-checkpoint custody drill."""

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


SCHEMA = "iotox.witness-checkpoint-custody-drill.v1"
HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")


class CustodyDrillError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CustodyDrillError(message)


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


def custody_tokens(args: argparse.Namespace) -> list[str]:
    labels = (
        args.custody_system,
        args.custody_generation,
        args.custody_failure_domain,
    )
    present = [label is not None for label in labels]
    require(
        not any(present) or all(present),
        "custody labels must be supplied all-or-none",
    )
    if not all(present):
        return []
    for field, name in (
        (args.custody_system, "custody-system"),
        (args.custody_generation, "custody-generation"),
        (args.custody_failure_domain, "custody-failure-domain"),
    ):
        validate_label(field, name)
    return [
        f"custody-system={args.custody_system}",
        f"custody-generation={args.custody_generation}",
        f"custody-failure-domain={args.custody_failure_domain}",
    ]


def parse_report(text: str) -> dict[str, str]:
    lines = text.splitlines()
    require(
        lines and lines[0] == "iotox-witness-checkpoint-custody-v1",
        "unexpected witness custody report schema",
    )
    fields: dict[str, str] = {"report-schema": lines[0]}
    for line in lines[1:]:
        key, separator, value = line.partition("=")
        require(separator == "=" and key and value != "", "bad custody report line")
        require(key not in fields, f"duplicate custody report field: {key}")
        fields[key] = value
    return fields


def require_uint(fields: dict[str, str], name: str) -> int:
    value = fields.get(name, "")
    require(value.isdigit(), f"{name} is absent or not unsigned")
    return int(value)


def validate_report(
    fields: dict[str, str],
    service_public_key: str,
    operator_custody: list[str],
) -> dict[str, object]:
    require(
        fields.get("checkpoint-authenticated") == "1",
        "checkpoint was not authenticated",
    )
    require(
        fields.get("outside-service-root") == "1",
        "checkpoint is not outside the service root",
    )
    require(
        fields.get("operational-independence") == "not-assessed",
        "custody report overclaimed operational independence",
    )
    require(
        fields.get("public-key", "").lower() == service_public_key.lower(),
        "custody report public key does not match the requested key",
    )
    if operator_custody:
        require(
            fields.get("operator-custody") == "present",
            "operator custody was not retained",
        )
        for token in operator_custody:
            key, value = token.split("=", 1)
            require(
                fields.get(f"{key}-hex") == hex_text(value),
                f"{key} was not bound into the custody report",
            )
    else:
        require(
            fields.get("operator-custody") == "absent",
            "unexpected operator custody state",
        )

    service_root_hex = fields.get("service-root-hex", "")
    checkpoint_path_hex = fields.get("checkpoint-path-hex", "")
    require(service_root_hex != "", "service root path evidence is absent")
    require(checkpoint_path_hex != "", "checkpoint path evidence is absent")
    return {
        "checkpoint_authenticated": True,
        "outside_service_root": True,
        "checkpoint_root_devices_differ": require_uint(
            fields, "checkpoint-root-devices-differ"
        ),
        "checkpoint_records": require_uint(fields, "checkpoint-records"),
        "operator_custody": fields.get("operator-custody", "absent"),
        "service_root_path_hex_sha256": sha256_text(service_root_hex),
        "checkpoint_path_hex_sha256": sha256_text(checkpoint_path_hex),
        "service_public_key_sha256": sha256_text(service_public_key.lower()),
    }


def write_json_atomic(path: Path, record: dict[str, object]) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.chmod(0o600)
    os.replace(temporary, path)


def run_drill(args: argparse.Namespace) -> dict[str, object]:
    iotox = args.iotox.resolve()
    evidence = args.evidence.resolve()
    service_root = args.service_root.resolve()
    checkpoint = args.checkpoint.resolve()
    public_key = args.service_public_key_hex
    require(iotox.is_file(), "IoTox binary is absent")
    require(
        HEX64.fullmatch(public_key) is not None,
        "service public key must be 64 hex characters",
    )
    service_metadata = service_root.lstat()
    checkpoint_metadata = checkpoint.lstat()
    require(stat.S_ISDIR(service_metadata.st_mode), "service root is not a directory")
    require(
        stat.S_ISREG(checkpoint_metadata.st_mode),
        "checkpoint is not a regular file",
    )
    require(
        service_root != checkpoint and service_root not in checkpoint.parents,
        "checkpoint must be outside the service root",
    )
    operator_custody = custody_tokens(args)
    command = [
        str(iotox),
        "witness-service-checkpoint-custody",
        str(service_root),
        str(checkpoint),
        public_key,
        *operator_custody,
    ]
    result = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=args.timeout,
        check=False,
    )
    if result.returncode != 0:
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
            "checkpoint_sha256": sha256_file(checkpoint),
            "contains_secrets": False,
        }
        write_json_atomic(evidence, record)
        return record
    report_text = result.stdout
    fields = parse_report(report_text)
    validated = validate_report(fields, public_key, operator_custody)
    custody_requirement_satisfied = (
        not args.require_custody_labels or bool(operator_custody)
    )
    device_requirement_satisfied = (
        not args.require_different_device
        or validated["checkpoint_root_devices_differ"] == 1
    )
    local_requirements_satisfied = (
        custody_requirement_satisfied and device_requirement_satisfied
    )
    record: dict[str, object] = {
        "schema": SCHEMA,
        "status": "passed" if local_requirements_satisfied else "rejected",
        "report_sha256": sha256_text(report_text),
        "iotox_binary_sha256": sha256_file(iotox),
        "checkpoint_sha256": sha256_file(checkpoint),
        "operator_custody_bound": bool(operator_custody),
        "custody_labels_required": bool(args.require_custody_labels),
        "different_device_required": bool(args.require_different_device),
        "custody_requirement_satisfied": custody_requirement_satisfied,
        "device_requirement_satisfied": device_requirement_satisfied,
        "local_requirements_satisfied": local_requirements_satisfied,
        "operational_independence": "operator-evidence-required",
        "contains_secrets": False,
        **validated,
    }
    if operator_custody:
        record.update(
            {
                "custody_system_sha256": sha256_text(args.custody_system),
                "custody_generation_sha256": sha256_text(args.custody_generation),
                "custody_failure_domain_sha256": sha256_text(
                    args.custody_failure_domain
                ),
            }
        )
    write_json_atomic(evidence, record)
    return record


def self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="iotox-witness-custody-drill-") as raw:
        root = Path(raw)
        service = root / "service"
        checkpoint = root / "checkpoint" / "service.checkpoint"
        service.mkdir(mode=0o700)
        checkpoint.parent.mkdir(mode=0o700)
        checkpoint.write_bytes(b"fake checkpoint")
        fake = root / "iotox"
        public_key = "11" * 32
        fake.write_text(
            """#!/usr/bin/env python3
import sys
def hx(value):
    return value.encode("utf-8").hex().upper()
args = sys.argv[1:]
tokens = [arg for arg in args if "=" in arg]
print("iotox-witness-checkpoint-custody-v1")
print("checkpoint-authenticated=1")
print("service-root-hex=2F73657276696365")
print("checkpoint-path-hex=2F636865636B706F696E74")
print("outside-service-root=1")
print("checkpoint-root-devices-differ=1")
print("checkpoint-records=2")
print("public-key=" + args[3])
print("operator-custody=" + ("present" if tokens else "absent"))
for token in tokens:
    key, value = token.split("=", 1)
    print(key + "-hex=" + hx(value))
print("operational-independence=not-assessed")
""",
            encoding="utf-8",
        )
        fake.chmod(0o700)
        evidence = root / "receipt.json"
        namespace = argparse.Namespace(
            iotox=fake,
            service_root=service,
            checkpoint=checkpoint,
            service_public_key_hex=public_key,
            evidence=evidence,
            custody_system="restic",
            custody_generation="checkpoint-1",
            custody_failure_domain="external-disk",
            require_custody_labels=True,
            require_different_device=True,
            timeout=10,
        )
        record = run_drill(namespace)
        require(record["status"] == "passed", "valid custody drill failed")
        require(record["checkpoint_records"] == 2, "record count was not retained")
        require(
            record["operator_custody_bound"] is True,
            "custody labels were not bound",
        )
        require(record["local_requirements_satisfied"] is True,
                "required local custody constraints were not satisfied")
        require(evidence.is_file(), "receipt was not written")

        missing_evidence = root / "missing-custody.json"
        missing = argparse.Namespace(
            iotox=fake,
            service_root=service,
            checkpoint=checkpoint,
            service_public_key_hex=public_key,
            evidence=missing_evidence,
            custody_system=None,
            custody_generation=None,
            custody_failure_domain=None,
            require_custody_labels=True,
            require_different_device=False,
            timeout=10,
        )
        missing_record = run_drill(missing)
        require(
            missing_record["status"] == "rejected",
            "missing required custody labels did not reject",
        )
        require(
            missing_record["local_requirements_satisfied"] is False,
            "missing required custody labels were marked locally satisfied",
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("service_root", type=Path, nargs="?")
    parser.add_argument("checkpoint", type=Path, nargs="?")
    parser.add_argument("service_public_key_hex", nargs="?")
    parser.add_argument("--iotox", type=Path, default=Path("build/iotox"))
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--custody-system")
    parser.add_argument("--custody-generation")
    parser.add_argument("--custody-failure-domain")
    parser.add_argument("--require-custody-labels", action="store_true")
    parser.add_argument("--require-different-device", action="store_true")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("witness-checkpoint-custody-drill-self-test=pass")
        return 0
    if (
        args.service_root is None
        or args.checkpoint is None
        or args.service_public_key_hex is None
    ):
        parser.error("SERVICE_ROOT CHECKPOINT SERVICE_PUBLIC_KEY_HEX are required")
    if args.evidence is None:
        parser.error("--evidence is required")
    require(1 <= args.timeout <= 3600, "timeout is invalid")
    try:
        record = run_drill(args)
    except (CustodyDrillError, OSError, subprocess.SubprocessError) as error:
        print(f"witness checkpoint custody drill failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(record, indent=2, sort_keys=True))
    return 0 if record["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
