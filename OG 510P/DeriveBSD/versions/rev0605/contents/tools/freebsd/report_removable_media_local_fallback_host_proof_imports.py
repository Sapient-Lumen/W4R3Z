#!/usr/bin/env python3
"""Report whether the checked FreeBSD host-proof import root contains proof.

This is intentionally a status/report tool, not another proof validator.  It
uses the existing strict import auditor to classify imported handoffs, then makes
the product question explicit: do we have a primary-production real-host proof
checked into the cube yet?
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

THIS_DIR = Path(__file__).resolve().parent
ROOT = THIS_DIR.parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from cube_digest_lib import CanonicalJsonError, load_json_strict_text, pretty_json_text  # noqa: E402
import audit_removable_media_local_fallback_host_proof_imports as import_auditor  # noqa: E402
import host_proof_contract as contract  # noqa: E402

DEFAULT_IMPORT_ROOT = ROOT / contract.DEFAULT_IMPORT_ROOT_REL
STATUS_COMPLETE_PRIMARY = "complete-primary-real-host-proof-imported"
STATUS_DEGRADED_LEGACY = "degraded-legacy-real-host-proof-imported"
STATUS_BLOCKED_EMPTY = "blocked-no-real-host-proof-import"
STATUS_INVALID_ROOT = "invalid-import-root"
STATUS_INVALID_CONTENTS = "invalid-import-root-contents"


def _dict(obj: Any) -> dict[str, Any]:
    return obj if isinstance(obj, dict) else {}


def _rel_or_abs(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _load_json(path: Path) -> dict[str, Any]:
    return _dict(load_json_strict_text(path.read_text(encoding="utf-8")))


def _empty_report(import_root: Path, state: str) -> dict[str, Any]:
    return {
        "kind": "removable.media.local.freebsd.host.proof.import.status",
        "schema_version": "0.1",
        "generated_for_version": contract.CURRENT_CUBE_CUT_VERSION,
        "host_target_matrix_id": contract.HOST_TARGET_MATRIX_ID,
        "primary_target": {
            "freebsd_release": contract.PRIMARY_FREEBSD_RELEASE,
            "minimum_kern_osreldate": contract.PRIMARY_FREEBSD_OSRELDATE_MINIMUM,
            "tier": contract.HOST_TARGET_PRIMARY_TIER,
        },
        "supported_floor": {
            "freebsd_release": contract.SUPPORTED_FREEBSD_RELEASE_FLOOR,
            "minimum_kern_osreldate": contract.MIN_FREEBSD_OSRELDATE,
            "tier": contract.HOST_TARGET_LEGACY_TIER,
        },
        "import_root": _rel_or_abs(import_root),
        "import_root_state": state,
        "counts": {
            "entries": 0,
            "valid_import_directories": 0,
            "invalid_import_directories": 0,
            "real_host_proof": 0,
            "primary_production_real_host_proof": 0,
            "supported_legacy_floor_real_host_proof": 0,
            "checker_simulation_non_proof": 0,
            "other_proof_status": 0,
        },
        "items": [],
        "proof_complete": False,
        "status": STATUS_BLOCKED_EMPTY if state == "present" else STATUS_INVALID_ROOT,
        "operator_next_step": "collect-and-import-one-primary-production-freebsd-real-host-proof",
    }


def summarize_import_root(import_root: Path = DEFAULT_IMPORT_ROOT) -> dict[str, Any]:
    root = import_root.expanduser()
    if root.is_symlink():
        report = _empty_report(root, "symlink")
        report["status"] = STATUS_INVALID_ROOT
        return report
    if not root.exists():
        report = _empty_report(root, "missing")
        report["status"] = STATUS_BLOCKED_EMPTY
        return report
    if not root.is_dir():
        report = _empty_report(root, "not-directory")
        report["status"] = STATUS_INVALID_ROOT
        return report

    report = _empty_report(root, "present")
    counts = report["counts"]
    items: list[dict[str, Any]] = []

    for child in sorted(root.iterdir(), key=lambda p: p.name):
        counts["entries"] += 1
        item: dict[str, Any] = {"name": child.name, "path": _rel_or_abs(child)}
        if child.is_symlink() or not child.is_dir():
            counts["invalid_import_directories"] += 1
            item.update({"valid": False, "errors": ["import root entries must be directories and must not be symlinks"]})
            items.append(item)
            continue

        errors = import_auditor.validate_import_dir(
            child,
            import_root=root,
            allow_checker_simulation=True,
            require_primary_target=False,
        )
        if errors:
            counts["invalid_import_directories"] += 1
            item.update({"valid": False, "errors": errors[:20]})
            items.append(item)
            continue

        try:
            receipt = _load_json(child / contract.IMPORT_RECEIPT_NAME)
        except (OSError, CanonicalJsonError) as exc:
            counts["invalid_import_directories"] += 1
            item.update({"valid": False, "errors": [f"could not read import receipt after validation: {exc}"]})
            items.append(item)
            continue

        receipt_summary = _dict(receipt.get("receipt"))
        bundle_summary = _dict(receipt.get("bundle"))
        source_transport = _dict(receipt.get("source_transport"))
        proof_status = str(receipt.get("proof_status") or bundle_summary.get("proof_status") or "unknown")
        host_target_tier = str(
            receipt_summary.get("host_target_tier") or bundle_summary.get("host_target_tier") or "unknown"
        )
        counts["valid_import_directories"] += 1
        if proof_status == "real-host-proof":
            counts["real_host_proof"] += 1
            if host_target_tier == contract.HOST_TARGET_PRIMARY_TIER:
                counts["primary_production_real_host_proof"] += 1
            elif host_target_tier == contract.HOST_TARGET_LEGACY_TIER:
                counts["supported_legacy_floor_real_host_proof"] += 1
        elif proof_status == "checker-simulation-non-proof":
            counts["checker_simulation_non_proof"] += 1
        else:
            counts["other_proof_status"] += 1
        item.update(
            {
                "valid": True,
                "proof_status": proof_status,
                "host_target_tier": host_target_tier,
                "host_target_matrix_id": receipt_summary.get("host_target_matrix_id") or bundle_summary.get("host_target_matrix_id"),
                "host_probe_observed_system": receipt_summary.get("host_probe_observed_system"),
                "host_probe_uname_release": receipt_summary.get("host_probe_uname_release"),
                "host_probe_uname_machine": receipt_summary.get("host_probe_uname_machine"),
                "host_probe_osreldate": receipt_summary.get("host_probe_osreldate"),
                "host_probe_effective_uid": receipt_summary.get("host_probe_effective_uid"),
                "source_transport_kind": source_transport.get("kind"),
                "receipt_canonical_sha256": receipt_summary.get("canonical_sha256"),
                "bundle_canonical_sha256": bundle_summary.get("canonical_sha256"),
            }
        )
        items.append(item)

    report["items"] = items
    if counts["invalid_import_directories"]:
        report["status"] = STATUS_INVALID_CONTENTS
    elif counts["primary_production_real_host_proof"]:
        report["status"] = STATUS_COMPLETE_PRIMARY
        report["proof_complete"] = True
        report["operator_next_step"] = "keep-primary-proof-current-and-recollect-when-target-matrix-changes"
    elif counts["real_host_proof"]:
        report["status"] = STATUS_DEGRADED_LEGACY
        report["operator_next_step"] = "replace-legacy-floor-proof-with-primary-production-freebsd-proof"
    else:
        report["status"] = STATUS_BLOCKED_EMPTY
    return report


def render_text(report: dict[str, Any]) -> str:
    counts = _dict(report.get("counts"))
    lines = [
        "FreeBSD real-host proof import status",
        f"generated_for_version={report.get('generated_for_version')}",
        f"import_root={report.get('import_root')}",
        f"import_root_state={report.get('import_root_state')}",
        f"status={report.get('status')}",
        f"proof_complete={str(report.get('proof_complete')).lower()}",
        f"real_host_proof={counts.get('real_host_proof', 0)}",
        f"primary_production_real_host_proof={counts.get('primary_production_real_host_proof', 0)}",
        f"supported_legacy_floor_real_host_proof={counts.get('supported_legacy_floor_real_host_proof', 0)}",
        f"checker_simulation_non_proof={counts.get('checker_simulation_non_proof', 0)}",
        f"invalid_import_directories={counts.get('invalid_import_directories', 0)}",
        f"operator_next_step={report.get('operator_next_step')}",
    ]
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="report checked-in FreeBSD real-host proof import status")
    parser.add_argument("import_root", nargs="?", type=Path, default=DEFAULT_IMPORT_ROOT)
    parser.add_argument("--json", action="store_true", help="emit deterministic JSON instead of text")
    parser.add_argument("--fail-if-incomplete", action="store_true", help="exit nonzero unless a primary-production real-host proof import is present")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    report = summarize_import_root(args.import_root)
    if args.json:
        sys.stdout.write(pretty_json_text(report))
    else:
        sys.stdout.write(render_text(report))
    if args.fail_if_incomplete and not report.get("proof_complete"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
