#!/usr/bin/env python3
"""Plan IoTox sync precious-data gates without certifying storage media.

IoTox does not certify storage media.  This helper prepares the
remaining trust boundary: local storage-science evidence plus independent,
versioned backup custody and repeatable restore drills.  It is deliberately
non-destructive and content-free.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
HEX_PLACEHOLDER = "REPLACE_WITH_64_LOWER_HEX_SHA256"


class PlanError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PlanError(message)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def git_revision() -> str:
    result = subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={ROOT}",
            "-C",
            str(ROOT),
            "rev-parse",
            "HEAD",
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def run_json(argv: list[str]) -> dict[str, Any] | None:
    if shutil.which(argv[0]) is None:
        return None
    result = subprocess.run(argv, check=False, text=True, capture_output=True)
    if result.returncode != 0:
        return None
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def mount_for_target(target: Path | None) -> dict[str, Any] | None:
    if target is None:
        return None
    value = run_json(["findmnt", "--json", "--target", str(target)])
    if value is None:
        return {
            "target": str(target),
            "status": "not-inspected",
            "reason": "findmnt unavailable or target not mounted",
        }
    filesystems = value.get("filesystems")
    if not isinstance(filesystems, list) or not filesystems:
        return {
            "target": str(target),
            "status": "not-found",
        }
    filesystem = filesystems[0] if isinstance(filesystems[0], dict) else {}
    source = str(filesystem.get("source") or "")
    return {
        "target": str(target),
        "status": "found",
        "mount": str(filesystem.get("target") or ""),
        "source_sha256": sha256_text(source),
        "fstype": str(filesystem.get("fstype") or ""),
        "options_sha256": sha256_text(str(filesystem.get("options") or "")),
        "raw_source_redacted": True,
    }


def command_map() -> dict[str, str | None]:
    names = [
        "findmnt",
        "borg",
        "restic",
        "rsync",
        "rclone",
        "tar",
        "sha256sum",
        "b3sum",
    ]
    return {name: shutil.which(name) for name in names}


def backup_custody_template() -> dict[str, Any]:
    return {
        "schema": "iotox.sync-backup-custody.v1",
        "status": "replace-with-passed-after-real-restore",
        "run_id": "run.REPLACE",
        "contains_secrets": False,
        "backup_independent": False,
        "custody_class": "same-host-versioned",
        "immutable_or_versioned": True,
        "restore_verified": True,
        "operator_rehearsal_repeatable": True,
        "backup_system": "replace.with.borg.restic.snapshot.or.sync-external",
        "backup_generation": "replace.with.generation.label",
        "live_failure_domain": "replace.live.domain",
        "backup_failure_domain": "replace.backup.custody.domain",
        "restored_failure_domain": "replace.restore.drill.domain",
        "restore_provenance": "replace.restore.drill.label",
        "recovery_report_sha256": HEX_PLACEHOLDER,
        "backup_inventory_sha256": HEX_PLACEHOLDER,
        "restored_inventory_sha256": HEX_PLACEHOLDER,
        "recovery_comparison": {
            "matches": True,
            "contains_secrets": False,
            "backup_entries": 0,
            "restored_entries": 0,
            "roots_on_distinct_devices": False,
        },
        "nonclaims": [
            "not-storage-media-certification",
            "not-disk-loss-protection",
            "not-host-compromise-protection",
            "not-filesystem-wide-corruption-protection",
            "not-content-custody",
        ],
    }


def recovery_runbook_template() -> str:
    return "\n".join([
        "iotox-sync-recovery-runbook-review-v1",
        "schema=iotox.sync-recovery-runbook-review.v1",
        "status=replace-with-reviewed-after-native-receipt",
        "content-free=1",
        "operator-runbook=present",
        "reviewer-label=replace.with.operator.label",
        f"dataset-selector-sha256={HEX_PLACEHOLDER}",
        "access=replace-with-one-writer-or-read-write",
        "interval-seconds=30",
        f"runbook-sha256={HEX_PLACEHOLDER}",
        "runbook-bytes=0",
        "covers-stop-writers-before-restore=1",
        "covers-restore-from-versioned-recovery-custody=1",
        "covers-verify-before-resuming-sync=1",
        "covers-retire-obsolete-writers=1",
        "covers-periodic-rehearsal=1",
        "accepted-reviewed-runbook=replace-with-1-after-review",
        "not-content-custody=1",
        "boundary=invalid-template-use-iotox-sync-runbook-receipt",
        "",
    ])


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    path.chmod(0o600)


def write_text(path: Path, value: str) -> None:
    path.write_text(value, encoding="utf-8")
    path.chmod(0o600)


def write_templates(directory: Path) -> dict[str, str]:
    directory.mkdir(parents=True, exist_ok=True)
    require(directory.is_dir(), "template output is not a directory")
    paths = {
        "backup_custody_template": directory / "backup-custody.template.json",
        "recovery_runbook_review_template": directory / "sync-recovery-runbook-review.template.receipt",
    }
    write_json(paths["backup_custody_template"], backup_custody_template())
    write_text(
        paths["recovery_runbook_review_template"],
        recovery_runbook_template(),
    )
    return {name: str(path) for name, path in paths.items()}


def build_report(
    *,
    dataset: Path | None,
    template_directory: Path | None = None,
    commands: dict[str, str | None] | None = None,
) -> dict[str, Any]:
    capabilities = commands if commands is not None else command_map()
    written_templates = (
        write_templates(template_directory) if template_directory is not None else {}
    )
    return {
        "schema": "iotox.sync-precious-data-gates-plan.v2",
        "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "git_revision": git_revision(),
        "status": "planned",
        "contains_secrets": False,
        "mutated_live_media": False,
        "storage_media_qualification": "not-an-iotox-goal",
        "wrote_templates": bool(written_templates),
        "template_paths": written_templates,
        "dataset_mount": mount_for_target(dataset),
        "host_capabilities": capabilities,
        "blocked_until": [
            "accepted local storage-readiness report",
            "accepted versioned recovery-custody receipt",
            "accepted restore drill for the actual dataset",
            "reviewed operator recovery runbook",
        ],
        "safe_defaults": [
            "does-not-format-devices",
            "does-not-mount-or-unmount-devices",
            "does-not-read-file-contents",
            "does-not-qualify-or-certify-storage-media",
            "does-not-claim-disk-loss-host-compromise-or-filesystem-wide-corruption-protection",
        ],
        "next_gate_commands": [
            "tools/iotox-repo.sh storage-readiness",
            "iotox sync runbook plan DATASET read-write 30",
            "iotox sync runbook receipt DATASET read-write 30 --runbook RUNBOOK.md --reviewer owner --accept-reviewed-runbook --out PROOF_ROOT/recovery-runbook.receipt",
            "tools/iotox-repo.sh sync-backup-custody-verify PROOF_ROOT/backup-custody.json",
            "tools/iotox-repo.sh storage-readiness --backup-custody-proof BACKUP_CUSTODY_RUN_DIR",
            "tools/iotox-repo.sh stable-evidence-plan",
        ],
        "backup_custody_receipt_requires": [
            "custody-class such as same-host-versioned or off-host-versioned",
            "custody outside normal IoTox sync write/delete/GC mutation",
            "immutable or versioned generation label",
            "byte-exact inventory comparison",
            "repeatable operator rehearsal",
            "content-free recovery report and inventory hashes",
        ],
    }


def render_human(report: dict[str, Any]) -> str:
    lines = [
        "iotox-sync-precious-data-gates-plan-v2",
        f"status={report['status']}",
        f"mutated-live-media={int(bool(report['mutated_live_media']))}",
        f"contains-secrets={int(bool(report['contains_secrets']))}",
        f"storage-media-qualification={report['storage_media_qualification']}",
        "",
        "blocked-until:",
    ]
    lines.extend(f"  - {item}" for item in report["blocked_until"])
    lines.append("")
    lines.append("next commands:")
    lines.extend(f"  {command}" for command in report["next_gate_commands"])
    if report.get("template_paths"):
        lines.append("")
        lines.append("templates written:")
        for label, path in sorted(report["template_paths"].items()):
            lines.append(f"  {label}={path}")
    lines.append("")
    lines.append("safe defaults:")
    lines.extend(f"  - {item}" for item in report["safe_defaults"])
    return "\n".join(lines) + "\n"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="iotox-precious-gates-") as raw:
        out = Path(raw) / "templates"
        report = build_report(
            dataset=None,
            template_directory=out,
            commands={"findmnt": "/bin/findmnt", "borg": "/bin/borg"},
        )
        require(report["mutated_live_media"] is False, "self-test mutated media")
        require(
            report["storage_media_qualification"] == "not-an-iotox-goal",
            "self-test lost storage-media boundary",
        )
        require(
            (out / "backup-custody.template.json").is_file()
            and (out / "sync-recovery-runbook-review.template.receipt").is_file()
            and not (out / "storage-media.template.json").exists(),
            "self-test templates were wrong",
        )
        backup = load_module(
            ROOT / "tools/verify-sync-backup-custody.py",
            "iotox_precious_gate_backup_self_test",
        )
        backup.verify_record(backup.sample_receipt())
        try:
            backup.verify_record(
                json.loads((out / "backup-custody.template.json").read_text(encoding="utf-8"))
            )
        except Exception:
            pass
        else:  # pragma: no cover
            raise PlanError("backup-custody template was accepted as proof")
    print("sync-precious-data-gates-plan-self-test=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, help="optional dataset path to inspect with findmnt")
    parser.add_argument(
        "--write-templates",
        type=Path,
        help="write invalid-by-default receipt templates to this explicit directory",
    )
    parser.add_argument("--json", action="store_true", help="print the full JSON report")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    report = build_report(dataset=args.dataset, template_directory=args.write_templates)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_human(report), end="")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (PlanError, OSError, json.JSONDecodeError) as error:
        print(f"sync precious-data gate planning failed: {error}", file=sys.stderr)
        raise SystemExit(1)
