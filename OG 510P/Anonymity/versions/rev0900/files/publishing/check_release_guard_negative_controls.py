#!/usr/bin/env python3
"""Static and functional negative-control coverage for release blockers.

Most guards remain checked by static fail-closed signal coverage to keep routine
fixed-point rebuilds inexpensive.  The highest-risk detector boundaries now also
run small functional drills against synthetic inputs: secret/private-key marker
detection, public-key/code-pin enforcement, and pre-extraction zip safety edge
cases.  These drills do not mutate the live archive and do not require the final
release zip sidecars.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import sys
import tempfile
import zipfile
from types import ModuleType
from typing import Any, Callable

CONTROL_SPECS: list[dict[str, Any]] = [
    {
        "name": "manifest_verifier_rejects_file_hash_drift",
        "guard": "publishing/verify_manifest_sha256.py",
        "synthetic_mutation": "modify VERSION without regenerating MANIFEST.sha256",
        "expected_signals": ["mismatched_paths", "missing_paths"],
    },
    {
        "name": "publication_boundary_rejects_unclassified_published_tex",
        "guard": "publishing/check_publication_boundary.py",
        "synthetic_mutation": "add an unclassified post-policy published/ Anonymity .tex entry",
        "expected_signals": ["published_tex_not_classified", "publication_receipt_missing", "new_release_not_in_citation_heads"],
    },
    {
        "name": "evidence_pack_integrity_rejects_manifest_hash_drift",
        "guard": "publishing/check_evidence_pack_integrity.py",
        "synthetic_mutation": "modify an evidence-pack file after its manifest is written",
        "expected_signals": ["pack_path_sha256_mismatch"],
    },
    {
        "name": "freeze_packet_integrity_rejects_frozen_source_drift",
        "guard": "publishing/check_freeze_packet_integrity.py",
        "synthetic_mutation": "modify FROZEN_SOURCE.tex after the freeze-packet manifest is written",
        "expected_signals": ["frozen_source_sha256_mismatch", "packet_path_sha256_mismatch"],
    },
    {
        "name": "publish_decision_scan_rejects_incomplete_authorization",
        "guard": "publishing/check_publication_decision_authorization.py",
        "synthetic_mutation": "add an incomplete Publication action: publish decision note",
        "expected_signals": ["required_field_missing", "placeholder_present", "source_sha256_mismatch", "ready_to_execute_guarded_publication_helper"],
    },
    {
        "name": "guarded_publication_helper_rejects_pending_compile_gate",
        "guard": "publishing/create_published_entry.py",
        "synthetic_mutation": "set compile_gate_status to pending before invoking the guarded publisher",
        "expected_signals": ["compile witness does not close", "compile_gate_status"],
    },
    {
        "name": "secret_quarantine_rejects_pem_private_key_in_signing_surface",
        "guard": "publishing/check_secret_material_quarantine.py",
        "synthetic_mutation": "accidentally ship a PEM private signing key next to the public package-attestation key",
        "expected_signals": [".pem", "pem_private_key_marker", "secret_detector_negative_controls"],
    },
    {
        "name": "package_attestation_rejects_tampered_or_unpinned_dsse_sidecars",
        "guard": "publishing/check_package_attestation.py",
        "synthetic_mutation": "mutate package attestation bytes after signing, omit the required DSSE envelope, or run release-evidence checking without a public-key pin",
        "expected_signals": ["dsse_payload_does_not_match_package_attestation", "dsse_signature_envelope_missing", "dsse_signature_verification_failed", "public_key_fingerprint_pin_required", "public_key_fingerprint_pin_mismatch"],
    },
    {
        "name": "external_artifact_set_verifier_runs_tamper_drills",
        "guard": "publishing/verify_release_artifact_set.py",
        "synthetic_mutation": "verify a delivered zip from local verifier code only, require external public-key and local code fingerprint pins, and run receipt/attestation/signature/zip tamper controls",
        "expected_signals": ["negative_control_not_detected", "sha256_receipt_digest_mismatch", "dsse_payload_does_not_match_package_attestation", "dsse_signature_envelope_missing", "local_sibling_checker_no_extracted_code_execution", "public_key_fingerprint_pin_required", "public_key_fingerprint_pin_mismatch", "local_verifier_fingerprint_pin_required", "local_verifier_fingerprint_pin_mismatch", "local_package_checker_fingerprint_pin_mismatch", "zip_member_compression_ratio_exceeds_limit", "zip_member_unsafe_path_component", "zip_member_absolute_path", "zip_member_file_directory_prefix_collision", "zip_member_casefold_collision", "duplicate_zip_member_names", "zip_member_compression_type_not_allowed", "zip_member_symlink", "safe_extract_failed"],
    },
    {
        "name": "surface_schema_validation_rejects_malformed_report",
        "guard": "publishing/check_surface_schemas.py",
        "synthetic_mutation": "change a report field to violate its schema",
        "expected_signals": ["iter_errors", "error_count"],
        "companion": "schemas/publication_rehearsal.schema.json",
    },
]


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_module(root: pathlib.Path, rel: str, name: str) -> ModuleType:
    path = root / rel
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {rel}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_control(root: pathlib.Path, spec: dict[str, Any]) -> dict[str, Any]:
    guard_rel = str(spec["guard"])
    guard_path = root / guard_rel
    haystack = ""
    failures: list[dict[str, Any]] = []
    if not guard_path.exists():
        failures.append({"category": "guard_missing", "path": guard_rel})
    else:
        haystack += guard_path.read_text(encoding="utf-8", errors="replace")
    companion = spec.get("companion")
    if companion:
        comp_path = root / str(companion)
        if not comp_path.exists():
            failures.append({"category": "companion_missing", "path": companion})
        else:
            haystack += "\n" + comp_path.read_text(encoding="utf-8", errors="replace")
    observed = [signal for signal in spec.get("expected_signals", []) if signal in haystack]
    missing = [signal for signal in spec.get("expected_signals", []) if signal not in haystack]
    if missing:
        failures.append({"category": "expected_guard_signal_missing", "signals": missing})
    ok = not failures
    return {
        "name": spec["name"],
        "guard": guard_rel,
        "synthetic_mutation": spec["synthetic_mutation"],
        "mode": "static_fail_closed_signal_coverage",
        "expected_signals": list(spec.get("expected_signals", [])),
        "observed_signals": observed,
        "missing_signals": missing,
        "expected_failure_observed": ok,
        "status": "pass" if ok else "fail",
        "failures": failures,
    }


def secret_detector_functional_drill(root: pathlib.Path) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    try:
        module = load_module(root, "publishing/check_secret_material_quarantine.py", "guard_secret_quarantine")
        controls, detector_failures = module.detector_negative_controls()
        failures.extend(detector_failures)
        categories = sorted({cat for row in controls for cat in row.get("detected_categories", [])})
        required = {"pem_private_key_marker", "pgp_private_key_marker"}
        missing = sorted(required - set(categories))
        if missing:
            failures.append({"category": "secret_detector_functional_category_missing", "categories": missing})
        public_rows = [row for row in controls if row.get("name") == "public_key_not_private"]
        if not public_rows or public_rows[0].get("detected_categories"):
            failures.append({"category": "secret_detector_public_key_false_positive"})
    except Exception as exc:  # noqa: BLE001
        failures.append({"category": "secret_detector_functional_drill_exception", "error": str(exc)})
    return {
        "name": "functional_secret_detector_negative_controls",
        "guard": "publishing/check_secret_material_quarantine.py",
        "mode": "functional_detector_drill",
        "synthetic_mutation": "call the detector negative controls directly without creating live archive files",
        "expected_failure_observed": not failures,
        "status": "pass" if not failures else "fail",
        "failures": failures,
    }


def write_absolute_path_zip(dst: pathlib.Path) -> None:
    with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.writestr("/absolute.txt", b"absolute")


def zip_security_functional_drill(root: pathlib.Path) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    try:
        module = load_module(root, "publishing/verify_release_artifact_set.py", "guard_artifact_set_verifier")
        writers: list[tuple[str, Callable[[pathlib.Path], None], str]] = [
            ("zip_bomb_ratio_guard", module.write_compression_bomb_zip, "zip_member_compression_ratio_exceeds_limit"),
            ("zip_path_traversal_guard", module.write_path_traversal_zip, "zip_member_unsafe_path_component"),
            ("zip_absolute_path_guard", write_absolute_path_zip, "zip_member_absolute_path"),
            ("zip_prefix_collision_guard", module.write_prefix_collision_zip, "zip_member_file_directory_prefix_collision"),
            ("zip_casefold_collision_guard", module.write_casefold_collision_zip, "zip_member_casefold_collision"),
            ("zip_duplicate_member_guard", module.write_duplicate_member_zip, "duplicate_zip_member_names"),
            ("zip_stored_member_guard", module.write_stored_member_zip, "zip_member_compression_type_not_allowed"),
            ("zip_symlink_member_guard", module.write_symlink_member_zip, "zip_member_symlink"),
        ]
        with tempfile.TemporaryDirectory(prefix="anonymity_release_guard_zip_") as tmp_s:
            tmp = pathlib.Path(tmp_s)
            for name, writer, expected in writers:
                path = tmp / f"{name}.zip"
                writer(path)
                _names, guard_failures, summary = module.zip_member_security(path)
                categories = sorted(str(row.get("category", "")) for row in guard_failures)
                ok = expected in categories
                row = {
                    "name": name,
                    "status": "pass" if ok else "fail",
                    "expected_category": expected,
                    "observed_categories": categories,
                    "zip_security_summary": summary,
                }
                if not ok:
                    failures.append({"category": "zip_security_functional_drill_not_detected", **row})
                rows.append(row)
    except Exception as exc:  # noqa: BLE001
        failures.append({"category": "zip_security_functional_drill_exception", "error": str(exc)})
    return {
        "name": "functional_zip_preextract_negative_controls",
        "guard": "publishing/verify_release_artifact_set.py",
        "mode": "functional_zip_security_drill",
        "synthetic_mutation": "generate malformed zip inputs in a temporary directory and require pre-extraction rejection categories",
        "expected_failure_observed": not failures,
        "status": "pass" if not failures else "fail",
        "drill_rows": rows,
        "failures": failures,
    }


def pin_enforcement_functional_drill(root: pathlib.Path) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    try:
        artifact_module = load_module(root, "publishing/verify_release_artifact_set.py", "guard_artifact_pin")
        package_module = load_module(root, "publishing/check_package_attestation.py", "guard_package_pin")
        with tempfile.TemporaryDirectory(prefix="anonymity_release_guard_pin_") as tmp_s:
            tmp = pathlib.Path(tmp_s)
            public_key = tmp / "public.pem"
            public_key.write_text("-----BEGIN PUBLIC KEY-----\nsynthetic\n-----END PUBLIC KEY-----\n", encoding="utf-8")
            local_summary, local_failures = artifact_module.local_verifier_code_pin_report(
                "",
                artifact_module.sha256_file(root / "publishing/check_package_attestation.py"),
                allow_unpinned_verifier_code=False,
            )
            key_summary, key_failures = artifact_module.public_key_pin_report(public_key, "", allow_unpinned_key=False)
            pkg_summary, pkg_failures = package_module.key_pin_failures(
                public_key,
                "",
                require_public_key_pin=True,
                allow_unpinned_key=False,
            )
            drills = [
                ("external_verifier_requires_local_code_pin", local_failures, "local_verifier_fingerprint_pin_required", local_summary),
                ("external_verifier_requires_public_key_pin", key_failures, "public_key_fingerprint_pin_required", key_summary),
                ("package_checker_requires_public_key_pin", pkg_failures, "public_key_fingerprint_pin_required", pkg_summary),
            ]
            for name, drill_failures, expected, summary in drills:
                categories = sorted(str(row.get("category", "")) for row in drill_failures)
                ok = expected in categories
                sanitized_summary = {
                    key: value
                    for key, value in summary.items()
                    if key not in {"local_verifier_path", "local_package_checker_path"}
                }
                row = {"name": name, "status": "pass" if ok else "fail", "expected_category": expected, "observed_categories": categories, "summary": sanitized_summary}
                if not ok:
                    failures.append({"category": "pin_functional_drill_not_detected", **row})
                rows.append(row)
    except Exception as exc:  # noqa: BLE001
        failures.append({"category": "pin_functional_drill_exception", "error": str(exc)})
    return {
        "name": "functional_key_and_code_pin_negative_controls",
        "guard": "publishing/verify_release_artifact_set.py + publishing/check_package_attestation.py",
        "mode": "functional_pin_enforcement_drill",
        "synthetic_mutation": "call pin-enforcement helpers with missing expected pins and require fail-closed categories",
        "expected_failure_observed": not failures,
        "status": "pass" if not failures else "fail",
        "drill_rows": rows,
        "failures": failures,
    }


def functional_controls(root: pathlib.Path) -> list[dict[str, Any]]:
    return [
        secret_detector_functional_drill(root),
        zip_security_functional_drill(root),
        pin_enforcement_functional_drill(root),
    ]


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    static_controls = [check_control(root, spec) for spec in CONTROL_SPECS]
    func_controls = functional_controls(root)
    controls = static_controls + func_controls
    failed = [row for row in controls if row["status"] != "pass"]
    return {
        "status": "pass" if not failed else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "mode": "mixed_static_signal_and_functional_negative_control_coverage",
        "controls": controls,
        "summary": {
            "control_count": len(controls),
            "static_signal_control_count": len(static_controls),
            "functional_drill_count": len(func_controls),
            "controls_failed": len(failed),
            "expected_failures_observed": len(controls) - len(failed),
            "functional_drills_failed": sum(1 for row in func_controls if row["status"] != "pass"),
            "static_signal_only_count": len(static_controls),
        },
        "failures": failed,
        "fail_closed_rule": "If a guard no longer exposes the expected failure signals, or if the functional private-key, pin, or zip pre-extraction drills stop failing closed, default to no publication and repair the release guard before trusting the release lane.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = root / args.write_report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
