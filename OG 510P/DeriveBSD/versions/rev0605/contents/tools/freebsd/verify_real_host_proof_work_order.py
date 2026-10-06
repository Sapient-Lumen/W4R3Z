#!/usr/bin/env python3
"""Verify a staged real FreeBSD host-proof work order.

This is a practical guard for the riskiest current gap: the first real host
proof still requires scarce FreeBSD time and a copied-back handoff.  The work
order must therefore fail before collection/import if its scripts or the repo
proof tools have drifted from the manifest that described them.
"""
from __future__ import annotations

import argparse
import hashlib
import json
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

from cube_digest_lib import CanonicalJsonError, canonical_digest, load_json_strict_text, pretty_json_text  # noqa: E402
import host_proof_contract as contract  # noqa: E402
import report_removable_media_local_fallback_host_proof_imports as proof_status  # noqa: E402
import stage_real_host_proof_work_order as stager  # noqa: E402

MANIFEST_NAME = stager.MANIFEST_NAME
README_NAME = stager.README_NAME
FORBIDDEN_FLAGS = ("--allow-checker-simulation", "--allow-refusal", "--allow-failed")


def _dict(obj: Any) -> dict[str, Any]:
    return obj if isinstance(obj, dict) else {}


def _list(obj: Any) -> list[Any]:
    return obj if isinstance(obj, list) else []


def _require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def _sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _load_manifest(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        value = load_json_strict_text(path.read_text(encoding="utf-8"))
    except (OSError, CanonicalJsonError) as exc:
        return None, [f"could not read manifest: {exc}"]
    if not isinstance(value, dict):
        return None, ["manifest root must be an object"]
    return value, []


def _row_map(rows: list[Any], field: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        key = row.get(field)
        if isinstance(key, str):
            out[key] = row
    return out


def _check_regular_file(errors: list[str], path: Path, label: str) -> None:
    if path.is_symlink():
        errors.append(f"{label} must not be a symlink: {path}")
        return
    if not path.exists():
        errors.append(f"{label} is missing: {path}")
        return
    if not path.is_file():
        errors.append(f"{label} must be a regular file: {path}")


def _check_digest_row(errors: list[str], root: Path, rel: str, row: dict[str, Any], *, executable_required: bool | None = None) -> None:
    path = root / rel
    _check_regular_file(errors, path, rel)
    if not path.exists() or path.is_symlink() or not path.is_file():
        return
    stat = path.stat()
    _require(errors, row.get("sha256") == _sha256_file(path), f"{rel} sha256 does not match manifest")
    _require(errors, row.get("size_bytes") == stat.st_size, f"{rel} size_bytes does not match manifest")
    observed_executable = bool(stat.st_mode & 0o111)
    if executable_required is None:
        _require(errors, row.get("executable") == observed_executable, f"{rel} executable bit does not match manifest")
    else:
        _require(errors, row.get("executable") is executable_required, f"{rel} manifest executable flag must be {executable_required}")
        _require(errors, observed_executable is executable_required, f"{rel} executable bit must be {executable_required}")


def verify(work_order_dir: Path, repo_root: Path) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    repo_root = repo_root.expanduser()
    work_order_dir = work_order_dir.expanduser()
    try:
        contract.require_no_existing_symlink_component(work_order_dir, "real-host proof work-order directory")
    except ValueError as exc:
        errors.append(str(exc))
    if work_order_dir.is_symlink() or not work_order_dir.exists() or not work_order_dir.is_dir():
        errors.append(f"work-order directory must exist as a non-symlink directory: {work_order_dir}")

    manifest_path = work_order_dir / MANIFEST_NAME
    _check_regular_file(errors, manifest_path, MANIFEST_NAME)
    manifest, load_errors = _load_manifest(manifest_path)
    errors.extend(load_errors)
    if manifest is None:
        return {}, errors

    digest = manifest.get("manifest_canonical_sha256")
    manifest_core = dict(manifest)
    manifest_core.pop("manifest_canonical_sha256", None)
    _require(errors, isinstance(digest, str) and digest.startswith("sha256:"), "manifest_canonical_sha256 must be sha256:<hex>")
    _require(errors, canonical_digest(manifest_core) == digest, "manifest_canonical_sha256 does not match canonical manifest core")

    _require(errors, manifest.get("kind") == stager.WORK_ORDER_KIND, "manifest kind mismatch")
    _require(errors, manifest.get("schema_version") == stager.WORK_ORDER_SCHEMA_VERSION, "manifest schema_version mismatch")
    _require(errors, manifest.get("work_order_policy") == stager.WORK_ORDER_POLICY, "manifest work_order_policy mismatch")
    _require(errors, manifest.get("manifest_digest_policy") == stager.WORK_ORDER_MANIFEST_DIGEST_POLICY, "manifest digest policy mismatch")
    _require(errors, manifest.get("work_order_file_digest_policy") == stager.WORK_ORDER_FILE_DIGEST_POLICY, "work-order file digest policy mismatch")
    _require(errors, manifest.get("repo_tool_digest_policy") == stager.WORK_ORDER_REPO_TOOL_DIGEST_POLICY, "repo tool digest policy mismatch")
    _require(errors, manifest.get("generated_for_version") == contract.CURRENT_CUBE_CUT_VERSION, "manifest generated_for_version does not match current cube cut")
    _require(errors, manifest.get("target_matrix", {}).get("host_target_matrix_id") == contract.HOST_TARGET_MATRIX_ID, "target matrix id mismatch")

    script_rows = _row_map(_list(manifest.get("work_order_file_digests")), "path")
    expected_scripts = set(stager.WORK_ORDER_SCRIPT_NAMES)
    _require(errors, set(script_rows) == expected_scripts, f"work_order_file_digests must cover exactly {sorted(expected_scripts)}")
    for script in sorted(expected_scripts):
        row = script_rows.get(script, {})
        _check_digest_row(errors, work_order_dir, script, row, executable_required=True)
        if script in script_rows:
            text = (work_order_dir / script).read_text(encoding="utf-8", errors="replace")
            _require(errors, text.startswith("#!/bin/sh\nset -eu"), f"{script} must be a strict /bin/sh script")
            for banned in FORBIDDEN_FLAGS:
                _require(errors, banned not in text, f"{script} must not contain non-proof flag {banned}")

    run_text = (work_order_dir / stager.RUN_ON_FREEBSD_NAME).read_text(encoding="utf-8", errors="replace") if (work_order_dir / stager.RUN_ON_FREEBSD_NAME).exists() else ""
    preflight_text = (work_order_dir / stager.PREFLIGHT_ON_FREEBSD_NAME).read_text(encoding="utf-8", errors="replace") if (work_order_dir / stager.PREFLIGHT_ON_FREEBSD_NAME).exists() else ""
    import_text = (work_order_dir / stager.IMPORT_IN_CLOUDTAINER_NAME).read_text(encoding="utf-8", errors="replace") if (work_order_dir / stager.IMPORT_IN_CLOUDTAINER_NAME).exists() else ""
    for script_name, text in [(stager.PREFLIGHT_ON_FREEBSD_NAME, preflight_text), (stager.IMPORT_IN_CLOUDTAINER_NAME, import_text)]:
        _require(errors, stager.VERIFY_WORK_ORDER_NAME in text, f"{script_name} must verify the work order before doing proof work")
    _require(errors, stager.PREFLIGHT_ON_FREEBSD_NAME in run_text, f"{stager.RUN_ON_FREEBSD_NAME} must call the standalone FreeBSD preflight before collection")
    _require(errors, contract.HOST_PROOF_PREFLIGHT_REL in preflight_text, f"{stager.PREFLIGHT_ON_FREEBSD_NAME} must run the repo FreeBSD host preflight")
    _require(errors, "sudo env PYTHON" in preflight_text and "uid" in preflight_text, f"{stager.PREFLIGHT_ON_FREEBSD_NAME} must run root-required preflight through root or sudo")
    _require(errors, "sudo env PYTHON" in run_text and "uid" in run_text, f"{stager.RUN_ON_FREEBSD_NAME} must run root-required collection through root or sudo")
    _require(errors, contract.HOST_PROOF_SEALED_HANDOFF_PREFLIGHT_REL in import_text, f"{stager.IMPORT_IN_CLOUDTAINER_NAME} must preflight the sealed archive before import")
    _require(errors, "--require-primary-target" in import_text, f"{stager.IMPORT_IN_CLOUDTAINER_NAME} must require primary target before/during audit")
    _require(errors, "--reuse-existing-import" in import_text, f"{stager.IMPORT_IN_CLOUDTAINER_NAME} must make retry idempotent through audited existing-import reuse")
    _require(errors, "--fail-if-incomplete" in import_text, f"{stager.IMPORT_IN_CLOUDTAINER_NAME} must fail if proof status is incomplete")

    repo_rows = _row_map(_list(manifest.get("repo_tool_digests")), "path")
    expected_tools = set(stager.WORK_ORDER_BOUND_TOOL_RELS)
    _require(errors, set(repo_rows) == expected_tools, "repo_tool_digests must cover exactly the work-order bound proof tools")
    for rel in sorted(expected_tools):
        row = repo_rows.get(rel, {})
        _check_digest_row(errors, repo_root, rel, row)

    expected_status = proof_status.summarize_import_root(repo_root / contract.DEFAULT_IMPORT_ROOT_REL)
    _require(errors, manifest.get("live_import_status") == expected_status, "manifest live_import_status is stale against current import root")
    risk = _dict(manifest.get("risk"))
    counts = _dict(expected_status.get("counts"))
    _require(errors, risk.get("current_status") == expected_status.get("status"), "risk.current_status must mirror live proof status")
    _require(errors, risk.get("proof_complete") == bool(expected_status.get("proof_complete")), "risk.proof_complete must mirror live proof status")
    _require(errors, risk.get("primary_production_real_host_proof") == counts.get("primary_production_real_host_proof", 0), "risk primary proof count must mirror live proof status")

    invariants = _dict(manifest.get("invariants"))
    for key in [
        "cloudtainer_import_requires_primary_target",
        "cloudtainer_import_preflights_before_publish",
        "cloudtainer_import_reuse_existing_import_is_audit_checked",
        "cloudtainer_import_uses_exclusive_import_root_lock",
        "work_order_binds_current_host_target_matrix",
        "work_order_binds_live_proof_status",
        "work_order_binds_runnable_script_digests",
        "work_order_binds_repo_tool_digests",
        "freebsd_preflight_runs_through_root_helper_before_collection",
        "preflight_only_host_check_available",
    ]:
        _require(errors, invariants.get(key) is True, f"invariant {key} must be true")
    if expected_status.get("proof_complete") is not True:
        _require(errors, invariants.get("does_not_claim_empty_import_root_is_complete") is True, "incomplete proof status must not be claimed complete")

    readme_path = work_order_dir / README_NAME
    _check_regular_file(errors, readme_path, README_NAME)
    if readme_path.exists() and not readme_path.is_symlink():
        readme = readme_path.read_text(encoding="utf-8", errors="replace")
        for token in [str(digest), stager.VERIFY_WORK_ORDER_NAME, "repo proof-tool digests", "--fail-if-incomplete", "exclusive sibling import-root lock"]:
            _require(errors, token in readme, f"README.md missing token {token!r}")

    summary = {
        "kind": "removable.media.local.freebsd.real_host_proof.work_order.verification",
        "schema_version": "0.1",
        "generated_for_version": contract.CURRENT_CUBE_CUT_VERSION,
        "work_order_dir": str(work_order_dir),
        "repo_root": str(repo_root),
        "manifest_canonical_sha256": digest,
        "script_digest_rows": len(script_rows),
        "repo_tool_digest_rows": len(repo_rows),
        "live_import_status": expected_status.get("status"),
        "proof_complete": bool(expected_status.get("proof_complete")),
        "valid": not errors,
    }
    return summary, errors


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="verify a real FreeBSD host-proof work order against this tree")
    parser.add_argument("work_order_dir", nargs="?", type=Path, default=ROOT / "validation" / "freebsd-real-host-proof-work-order" / "current")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    summary, errors = verify(args.work_order_dir, args.repo_root)
    if args.json:
        sys.stdout.write(pretty_json_text({**summary, "errors": errors}))
    elif errors:
        print("FreeBSD real-host proof work-order verification FAILED.")
        for error in errors[:80]:
            print("-", error)
        if len(errors) > 80:
            print(f"- ... {len(errors) - 80} more errors")
    else:
        print("FreeBSD real-host proof work-order verification OK")
        print(f"manifest_canonical_sha256={summary.get('manifest_canonical_sha256')}")
        print(f"repo_tool_digest_rows={summary.get('repo_tool_digest_rows')}")
        print(f"live_import_status={summary.get('live_import_status')}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
