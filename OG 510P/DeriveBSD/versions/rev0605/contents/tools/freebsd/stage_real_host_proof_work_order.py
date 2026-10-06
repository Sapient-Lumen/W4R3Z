#!/usr/bin/env python3
"""Stage the next real FreeBSD host-proof work order.

This tool is intentionally practical: it does not create a new registry or make
an empty import root sound successful.  It writes a small operator handoff kit
with the exact FreeBSD collection command, the exact cloudtainer import command,
and a machine-readable manifest that binds the current target matrix and live
proof-status report.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
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

from cube_digest_lib import canonical_digest, pretty_json_text  # noqa: E402
import host_proof_contract as contract  # noqa: E402
import report_removable_media_local_fallback_host_proof_imports as proof_status  # noqa: E402

DEFAULT_OUT = ROOT / "validation" / "freebsd-real-host-proof-work-order" / "current"
MANIFEST_NAME = "real-host-proof-work-order.json"
RUN_ON_FREEBSD_NAME = "RUN_ON_FREEBSD.sh"
IMPORT_IN_CLOUDTAINER_NAME = "IMPORT_IN_CLOUDTAINER.sh"
README_NAME = "README.md"
VERIFY_WORK_ORDER_NAME = "VERIFY_WORK_ORDER.sh"
PREFLIGHT_ON_FREEBSD_NAME = "PREFLIGHT_ON_FREEBSD.sh"
WORK_ORDER_KIND = "removable.media.local.freebsd.real_host_proof.work_order"
WORK_ORDER_SCHEMA_VERSION = "0.1"
WORK_ORDER_POLICY = "one-small-runbook-kit-to-close-the-empty-real-host-proof-import-gap"
WORK_ORDER_MANIFEST_DIGEST_POLICY = "canonical-sha256-over-manifest-excluding-manifest_canonical_sha256"
WORK_ORDER_FILE_DIGEST_POLICY = "manifest-binds-runnable-work-order-scripts-by-size-mode-and-sha256"
WORK_ORDER_REPO_TOOL_DIGEST_POLICY = "manifest-binds-host-proof-repo-tools-that-the-work-order-will-execute"
WORK_ORDER_SCRIPT_NAMES = (PREFLIGHT_ON_FREEBSD_NAME, RUN_ON_FREEBSD_NAME, IMPORT_IN_CLOUDTAINER_NAME, VERIFY_WORK_ORDER_NAME)
WORK_ORDER_BOUND_TOOL_RELS = (
    contract.HOST_PROOF_CONTRACT_REL,
    contract.HOST_PROOF_PREFLIGHT_REL,
    contract.HOST_SMOKE_COLLECTOR_REL,
    contract.HOST_SMOKE_RUNNER_REL,
    contract.HOST_SMOKE_VALIDATOR_REL,
    contract.HOST_PROOF_FINALIZER_REL,
    contract.HOST_PROOF_BUNDLE_VALIDATOR_REL,
    contract.HOST_PROOF_HANDOFF_VERIFIER_REL,
    contract.HOST_PROOF_HANDOFF_SEALER_REL,
    contract.HOST_PROOF_SEALED_HANDOFF_IMPORTER_REL,
    contract.HOST_PROOF_SEALED_HANDOFF_PREFLIGHT_REL,
    contract.HOST_PROOF_IMPORT_AUDITOR_REL,
    contract.HOST_PROOF_IMPORT_STATUS_REPORTER_REL,
    contract.HOST_PROOF_CHECKED_IMPORT_GATE_REL,
    contract.HOST_PROOF_THEATRE_GATE_REL,
    contract.HOST_PROOF_WORK_ORDER_STAGER_REL,
    contract.HOST_PROOF_WORK_ORDER_VERIFIER_REL,
    "tools/cube_digest_lib.py",
)


def _rel_or_abs(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _script_header() -> str:
    return "#!/bin/sh\nset -eu\n\n"


def _sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _repo_file_row(rel: str) -> dict[str, Any]:
    path = ROOT / rel
    stat = path.stat()
    return {
        "path": rel,
        "sha256": "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest(),
        "size_bytes": stat.st_size,
        "executable": bool(stat.st_mode & 0o111),
    }


def _work_order_script_rows(scripts: dict[str, str]) -> list[dict[str, Any]]:
    return [
        {
            "path": name,
            "sha256": _sha256_text(scripts[name]),
            "size_bytes": len(scripts[name].encode("utf-8")),
            "executable": True,
        }
        for name in WORK_ORDER_SCRIPT_NAMES
    ]


def verify_work_order_script() -> str:
    return _script_header() + f"""# Verify that this work order still matches the checked-out DeriveBSD tree.
# Usage: sh {VERIFY_WORK_ORDER_NAME} [/path/to/DeriveBSD] [work-order-dir]
SCRIPT_DIR=$(CDPATH= cd "$(dirname "$0")" && pwd -P)
REPO_ROOT=${{1:-$(pwd)}}
WORK_ORDER_DIR=${{2:-$SCRIPT_DIR}}
PYTHON=${{PYTHON:-python3}}

cd "$REPO_ROOT"

"$PYTHON" -B -S "$REPO_ROOT/{contract.HOST_PROOF_WORK_ORDER_VERIFIER_REL}" \
  "$WORK_ORDER_DIR" \
  --repo-root "$REPO_ROOT"

printf '%s\n' "real FreeBSD host-proof work order verified against checked-out tree"
"""


def preflight_on_freebsd_script() -> str:
    return _script_header() + f"""# Run this from a real FreeBSD host before spending collection time.
# Usage: sh {PREFLIGHT_ON_FREEBSD_NAME} [/path/to/DeriveBSD]
SCRIPT_DIR=$(CDPATH= cd "$(dirname "$0")" && pwd -P)
REPO_ROOT=${{1:-$(pwd)}}
PYTHON=${{PYTHON:-python3}}

run_root_preflight() {{
  uid=$(/usr/bin/id -u 2>/dev/null || id -u 2>/dev/null || printf unknown)
  if [ "$uid" = "0" ]; then
    env PYTHON="$PYTHON" "$REPO_ROOT/{contract.HOST_PROOF_PREFLIGHT_REL}"
  else
    if ! command -v sudo >/dev/null 2>&1; then
      printf '%s\\n' "host-proof preflight FAILED: run as root or install sudo; observed uid $uid" >&2
      exit 1
    fi
    sudo env PYTHON="$PYTHON" "$REPO_ROOT/{contract.HOST_PROOF_PREFLIGHT_REL}"
  fi
}}

cd "$REPO_ROOT"

"$SCRIPT_DIR/{VERIFY_WORK_ORDER_NAME}" "$REPO_ROOT" "$SCRIPT_DIR"
run_root_preflight

printf '%s\\n' "real FreeBSD host-proof preflight passed for checked-out tree"
"""


def run_on_freebsd_script() -> str:
    return _script_header() + f"""# Run this from a real FreeBSD host with a checked-out DeriveBSD tree.
# Usage: sh {RUN_ON_FREEBSD_NAME} [/path/to/DeriveBSD] [/tmp/handoff-dir] [archive.zip]
SCRIPT_DIR=$(CDPATH= cd "$(dirname "$0")" && pwd -P)
REPO_ROOT=${{1:-$(pwd)}}
HANDOFF_DIR=${{2:-/tmp/derivebsd-host-proof-handoff}}
ARCHIVE=${{3:-derivebsd-freebsd-host-proof-handoff.zip}}
PYTHON=${{PYTHON:-python3}}

run_root_collector() {{
  uid=$(/usr/bin/id -u 2>/dev/null || id -u 2>/dev/null || printf unknown)
  if [ "$uid" = "0" ]; then
    env PYTHON="$PYTHON" DERIVEBSD_HOST_PROOF_HANDOFF_REPLACE=${{DERIVEBSD_HOST_PROOF_HANDOFF_REPLACE:-0}} "$REPO_ROOT/{contract.HOST_SMOKE_COLLECTOR_REL}" "$HANDOFF_DIR/{contract.RECEIPT_NAME}" "$HANDOFF_DIR/{contract.BUNDLE_NAME}" "$HANDOFF_DIR"
  else
    if ! command -v sudo >/dev/null 2>&1; then
      printf '%s\\n' "host-proof collection FAILED: run as root or install sudo; observed uid $uid" >&2
      exit 1
    fi
    sudo env PYTHON="$PYTHON" DERIVEBSD_HOST_PROOF_HANDOFF_REPLACE=${{DERIVEBSD_HOST_PROOF_HANDOFF_REPLACE:-0}} "$REPO_ROOT/{contract.HOST_SMOKE_COLLECTOR_REL}" "$HANDOFF_DIR/{contract.RECEIPT_NAME}" "$HANDOFF_DIR/{contract.BUNDLE_NAME}" "$HANDOFF_DIR"
  fi
}}

cd "$REPO_ROOT"

# Verify the copied work-order kit and run the root FreeBSD preflight before
# collection.  This avoids a split where collection runs through sudo but the
# root-required preflight runs as the invoking user.
"$SCRIPT_DIR/{PREFLIGHT_ON_FREEBSD_NAME}" "$REPO_ROOT"

# Collect the scarce evidence.  This path intentionally uses no checker-only or
# failed/refusal proof flags.
run_root_collector

"$PYTHON" -B -S "$REPO_ROOT/{contract.HOST_PROOF_HANDOFF_VERIFIER_REL}" "$HANDOFF_DIR"
"$PYTHON" -B -S "$REPO_ROOT/{contract.HOST_PROOF_HANDOFF_SEALER_REL}" "$HANDOFF_DIR" --output "$ARCHIVE"

printf '%s\\n' "real FreeBSD host-proof handoff sealed: $ARCHIVE"
printf '%s\\n' "bring this archive back to the cloudtainer and run {IMPORT_IN_CLOUDTAINER_NAME}"
"""

def import_in_cloudtainer_script() -> str:
    return _script_header() + f"""# Run this in the cloudtainer with the same DeriveBSD tree after the archive
# from {RUN_ON_FREEBSD_NAME} has been copied back.
# Usage: sh {IMPORT_IN_CLOUDTAINER_NAME} [/path/to/DeriveBSD] [archive.zip]
SCRIPT_DIR=$(CDPATH= cd "$(dirname "$0")" && pwd -P)
REPO_ROOT=${{1:-$(pwd)}}
ARCHIVE=${{2:-derivebsd-freebsd-host-proof-handoff.zip}}
PYTHON=${{PYTHON:-python3}}

cd "$REPO_ROOT"

"$SCRIPT_DIR/{VERIFY_WORK_ORDER_NAME}" "$REPO_ROOT" "$SCRIPT_DIR"

"$PYTHON" -B -S "$REPO_ROOT/{contract.HOST_PROOF_SEALED_HANDOFF_PREFLIGHT_REL}" \\
  "$ARCHIVE" \\
  --import-root "{contract.DEFAULT_IMPORT_ROOT_REL}" \\
  --require-primary-target \\
  --reuse-existing-import
"$PYTHON" -B -S "$REPO_ROOT/{contract.HOST_PROOF_SEALED_HANDOFF_IMPORTER_REL}" \\
  "$ARCHIVE" \\
  --import-root "{contract.DEFAULT_IMPORT_ROOT_REL}" \\
  --require-primary-target \\
  --reuse-existing-import
"$PYTHON" -B -S "$REPO_ROOT/{contract.HOST_PROOF_IMPORT_AUDITOR_REL}" \\
  "{contract.DEFAULT_IMPORT_ROOT_REL}" \\
  --require-primary-target
"$PYTHON" -B -S "$REPO_ROOT/{contract.HOST_PROOF_IMPORT_STATUS_REPORTER_REL}" \\
  --fail-if-incomplete
"$PYTHON" -B -S "$REPO_ROOT/{contract.HOST_PROOF_CHECKED_IMPORT_GATE_REL}"
"$PYTHON" -B -S "$REPO_ROOT/{contract.HOST_PROOF_THEATRE_GATE_REL}"

printf '%s\n' "primary-production real FreeBSD host proof imported and gated"
"""


def readme_text(manifest_digest: str) -> str:
    return f"""# DeriveBSD real FreeBSD host-proof work order

This directory is the next concrete work packet for the highest-risk unfinished
item: the cube still has no checked-in primary-production real FreeBSD host
proof import.

Files:

- `{PREFLIGHT_ON_FREEBSD_NAME}`: run on the real FreeBSD host before collection; it verifies the kit and runs the root-required host preflight through root or sudo.
- `{RUN_ON_FREEBSD_NAME}`: run on the real FreeBSD host from a checked-out tree after preflight is green.
- `{IMPORT_IN_CLOUDTAINER_NAME}`: run after bringing the sealed handoff archive back.
- `{VERIFY_WORK_ORDER_NAME}`: run before either step to ensure this kit still matches the tree.
- `{MANIFEST_NAME}`: machine-readable target, status, and success criteria.

Current target:

- Primary: `{contract.PRIMARY_FREEBSD_RELEASE}` / `kern.osreldate >= {contract.PRIMARY_FREEBSD_OSRELDATE_MINIMUM}` / `{contract.HOST_TARGET_PRIMARY_TIER}`.
- Supported floor: `{contract.SUPPORTED_FREEBSD_RELEASE_FLOOR}` / `kern.osreldate >= {contract.MIN_FREEBSD_OSRELDATE}` / `{contract.HOST_TARGET_LEGACY_TIER}`.

Manifest digest: `{manifest_digest}`

The manifest also binds the runnable work-order script digests and the exact
repo proof-tool digests that the scripts execute.  Verification is deliberately
first in runnable scripts so a stale copied kit fails before scarce host
time or returned proof is spent.  The FreeBSD-side preflight can now be run
by itself and is invoked through root/sudo before collection, closing the
earlier sudo/preflight split.  Cloudtainer import also runs the sealed-import
preflight before publish so target-tier/collision failures are caught without
writing an import.  Cloudtainer reruns use `--reuse-existing-import`, so an
interrupted session can verify and reuse the already-published matching sealed
digest import instead of failing as a duplicate or replacing evidence.  The
sealed importer also takes an exclusive sibling import-root lock around the
publish/reuse/replace decision, so concurrent cloudtainer retries fail before
they can interleave with scarce proof publication.

Do not use checker-simulation or refusal flags for this work order.  A successful
run must make `report_removable_media_local_fallback_host_proof_imports.py
--fail-if-incomplete` exit zero.
"""


def build_manifest(output_dir: Path, generated_at_utc: str, scripts: dict[str, str]) -> dict[str, Any]:
    status_report = proof_status.summarize_import_root()
    work_order_core: dict[str, Any] = {
        "kind": WORK_ORDER_KIND,
        "schema_version": WORK_ORDER_SCHEMA_VERSION,
        "work_order_policy": WORK_ORDER_POLICY,
        "manifest_digest_policy": WORK_ORDER_MANIFEST_DIGEST_POLICY,
        "work_order_file_digest_policy": WORK_ORDER_FILE_DIGEST_POLICY,
        "repo_tool_digest_policy": WORK_ORDER_REPO_TOOL_DIGEST_POLICY,
        "generated_for_version": contract.CURRENT_CUBE_CUT_VERSION,
        "generated_at_utc": generated_at_utc,
        "work_order_id": f"freebsd-real-host-proof-work-order-{contract.CURRENT_CUBE_CUT_VERSION.replace('-', '').lower()}",
        "default_output_dir": "validation/freebsd-real-host-proof-work-order/current",
        "risk": {
            "highest_risk_unfinished_item": "no-imported-primary-production-real-freebsd-host-proof",
            "why_this_work_order_exists": "make the next operator run concrete, replayable, and proof-status-gated instead of adding doctrine",
            "current_status": status_report.get("status"),
            "proof_complete": bool(status_report.get("proof_complete")),
            "primary_production_real_host_proof": status_report.get("counts", {}).get("primary_production_real_host_proof", 0),
        },
        "target_matrix": {
            "host_target_matrix_id": contract.HOST_TARGET_MATRIX_ID,
            "primary": {
                "freebsd_release": contract.PRIMARY_FREEBSD_RELEASE,
                "minimum_kern_osreldate": contract.PRIMARY_FREEBSD_OSRELDATE_MINIMUM,
                "tier": contract.HOST_TARGET_PRIMARY_TIER,
                "eol": contract.PRIMARY_FREEBSD_RELEASE_EOL,
            },
            "supported_floor": {
                "freebsd_release": contract.SUPPORTED_FREEBSD_RELEASE_FLOOR,
                "minimum_kern_osreldate": contract.MIN_FREEBSD_OSRELDATE,
                "tier": contract.HOST_TARGET_LEGACY_TIER,
                "eol": contract.SUPPORTED_FREEBSD_RELEASE_FLOOR_EOL,
            },
            "target_tier_policy": contract.HOST_TARGET_TIER_POLICY,
        },
        "live_import_status": status_report,
        "files": [
            {"path": PREFLIGHT_ON_FREEBSD_NAME, "purpose": "verify the kit and run root FreeBSD preflight without collection"},
            {"path": RUN_ON_FREEBSD_NAME, "purpose": "preflight, collect, verify, and seal one real FreeBSD handoff"},
            {"path": IMPORT_IN_CLOUDTAINER_NAME, "purpose": "import, audit, status-gate, and theatre-gate the returned handoff"},
            {"path": VERIFY_WORK_ORDER_NAME, "purpose": "preflight that scripts and repo tools still match this manifest"},
            {"path": MANIFEST_NAME, "purpose": "bind current targets, live proof status, and success criteria"},
            {"path": README_NAME, "purpose": "short human handoff notes"},
        ],
        "work_order_file_digests": _work_order_script_rows(scripts),
        "repo_tool_digests": [_repo_file_row(rel) for rel in WORK_ORDER_BOUND_TOOL_RELS],
        "required_commands": {
            "freebsd_host": [
                VERIFY_WORK_ORDER_NAME,
                PREFLIGHT_ON_FREEBSD_NAME,
                contract.HOST_PROOF_PREFLIGHT_REL,
                contract.HOST_SMOKE_COLLECTOR_REL,
                contract.HOST_PROOF_HANDOFF_VERIFIER_REL,
                contract.HOST_PROOF_HANDOFF_SEALER_REL,
            ],
            "cloudtainer": [
                VERIFY_WORK_ORDER_NAME,
                contract.HOST_PROOF_SEALED_HANDOFF_PREFLIGHT_REL,
                contract.HOST_PROOF_SEALED_HANDOFF_IMPORTER_REL,
                contract.HOST_PROOF_IMPORT_AUDITOR_REL,
                f"{contract.HOST_PROOF_IMPORT_STATUS_REPORTER_REL} --fail-if-incomplete",
                contract.HOST_PROOF_CHECKED_IMPORT_GATE_REL,
                contract.HOST_PROOF_THEATRE_GATE_REL,
            ],
        },
        "success_criteria": [
            "work order verifies its runnable scripts and repo proof-tool digests before collection and import",
            "host-side preflight can be run by itself before collection and runs root-required checks through root or sudo",
            "sealed handoff archive returns from a real FreeBSD host",
            "sealed import preflight predicts a primary-production import without publishing",
            "sealed importer is also run with --require-primary-target, so an archive swapped after preflight still fails before publish",
            "cloudtainer retry with the same sealed archive is idempotent through --reuse-existing-import and verifies the existing digest import before reuse",
            "sealed importer holds an exclusive sibling import-root lock during publish, replace, or verified reuse",
            "import auditor passes in default real-proof mode with --require-primary-target",
            "proof status reporter exits zero with --fail-if-incomplete",
            "checked import-root gate passes without checker-simulation allowances",
            "real-host proof theatre gate passes",
        ],
        "forbidden_flags": ["--allow-checker-simulation", "--allow-refusal", "--allow-failed"],
        "invariants": {
            "does_not_claim_empty_import_root_is_complete": status_report.get("proof_complete") is not True,
            "no_checker_simulation_flags_in_scripts": True,
            "cloudtainer_import_requires_primary_target": True,
            "cloudtainer_importer_rechecks_primary_target_before_publish": True,
            "cloudtainer_import_preflights_before_publish": True,
            "cloudtainer_import_reuse_existing_import_is_audit_checked": True,
            "cloudtainer_import_uses_exclusive_import_root_lock": True,
            "freebsd_preflight_runs_through_root_helper_before_collection": True,
            "preflight_only_host_check_available": True,
            "work_order_binds_live_proof_status": True,
            "work_order_binds_current_host_target_matrix": True,
            "work_order_binds_runnable_script_digests": True,
            "work_order_binds_repo_tool_digests": True,
        },
    }
    return {**work_order_core, "manifest_canonical_sha256": canonical_digest(work_order_core)}


def write_work_order(output_dir: Path, generated_at_utc: str, *, replace: bool) -> dict[str, Any]:
    output_dir = output_dir.expanduser()
    contract.require_no_existing_symlink_component(output_dir, "host proof work-order output directory")
    if output_dir.exists():
        if output_dir.is_symlink() or not output_dir.is_dir():
            raise ValueError(f"work-order output must be a directory and not a symlink: {output_dir}")
        if any(output_dir.iterdir()):
            if not replace:
                raise ValueError(f"work-order output is not empty: {output_dir} (use --replace for deliberate refresh)")
            for child in output_dir.iterdir():
                if child.is_dir() and not child.is_symlink():
                    shutil.rmtree(child)
                else:
                    child.unlink()
    output_dir.mkdir(parents=True, exist_ok=True)

    scripts = {
        PREFLIGHT_ON_FREEBSD_NAME: preflight_on_freebsd_script(),
        RUN_ON_FREEBSD_NAME: run_on_freebsd_script(),
        IMPORT_IN_CLOUDTAINER_NAME: import_in_cloudtainer_script(),
        VERIFY_WORK_ORDER_NAME: verify_work_order_script(),
    }
    manifest = build_manifest(output_dir, generated_at_utc, scripts)
    for name, text in scripts.items():
        (output_dir / name).write_text(text, encoding="utf-8")
        os.chmod(output_dir / name, 0o755)
    (output_dir / MANIFEST_NAME).write_text(pretty_json_text(manifest), encoding="utf-8")
    (output_dir / README_NAME).write_text(readme_text(manifest["manifest_canonical_sha256"]), encoding="utf-8")
    return manifest


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="stage the next real FreeBSD host-proof work order")
    parser.add_argument("output_dir", nargs="?", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--generated-at", default=contract.CURRENT_CUBE_CUT_VERSION, help="deterministic timestamp/id stamp for generated work order")
    parser.add_argument("--replace", action="store_true", help="replace an existing non-empty work-order directory")
    parser.add_argument("--json", action="store_true", help="print manifest JSON to stdout after writing")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        manifest = write_work_order(args.output_dir, args.generated_at, replace=args.replace)
    except Exception as exc:  # noqa: BLE001
        print(f"real-host proof work-order staging FAILED: {exc}", file=sys.stderr)
        return 1
    if args.json:
        sys.stdout.write(pretty_json_text(manifest))
    else:
        print(f"wrote real-host proof work order: {_rel_or_abs(args.output_dir)}")
        print(f"status={manifest['risk']['current_status']}")
        print(f"proof_complete={str(manifest['risk']['proof_complete']).lower()}")
        print(f"manifest_canonical_sha256={manifest['manifest_canonical_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
