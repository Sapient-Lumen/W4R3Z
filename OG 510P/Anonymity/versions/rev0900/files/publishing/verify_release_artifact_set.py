#!/usr/bin/env python3
"""Verify a delivered release artifact set from outside the zip.

This command is for the consumer side of the package boundary. It takes a zip
and its sidecars, validates the zip member names and decompression budget before
extraction, unpacks the zip to a temporary tree, and verifies the external
SHA-256 receipt, in-toto/SLSA package statement, DSSE envelope, public key
sidecar, and externally pinned local verifier/checker code fingerprints with the
verifier code next to this script.

A key trust-boundary rule is enforced: this verifier does not execute Python code
from the zip being judged. Earlier revisions extracted the candidate archive and
ran the packaged checker from that extraction. That was convenient, but a
malicious candidate zip could replace the checker it asked the operator to run.
The current path reads candidate files as data only; the only checker code that
runs is the local sibling module loaded next to this verifier.
"""

from __future__ import annotations

import argparse
import importlib.util
import hashlib
import json
import pathlib
import shutil
import tempfile
import warnings
import zipfile
from types import ModuleType
from typing import Any

DEFAULT_TIMEOUT_SECONDS = 45
MAX_ZIP_MEMBER_COUNT = 5_000
MAX_TOTAL_UNCOMPRESSED_BYTES = 128 * 1024 * 1024
MAX_MEMBER_UNCOMPRESSED_BYTES = 32 * 1024 * 1024
MAX_ZIP_MEMBER_NAME_BYTES = 512
MAX_COMPRESSION_RATIO = 100.0
ALLOWED_COMPRESSION_TYPES = {zipfile.ZIP_DEFLATED}
TRUST_BOUNDARY_MODE = "local_sibling_checker_no_extracted_code_execution"


def sha_path_for(zip_path: pathlib.Path) -> pathlib.Path:
    return zip_path.with_suffix(zip_path.suffix + ".sha256")


def attestation_path_for(zip_path: pathlib.Path) -> pathlib.Path:
    return zip_path.with_suffix(zip_path.suffix + ".package.intoto.jsonl")


def envelope_path_for(zip_path: pathlib.Path) -> pathlib.Path:
    return zip_path.with_suffix(zip_path.suffix + ".package.dsse.json")


def public_key_sidecar_path_for(zip_path: pathlib.Path) -> pathlib.Path:
    return zip_path.with_suffix(zip_path.suffix + ".package.dsse.pub.pem")


def load_json_text(text: str) -> Any:
    return json.loads(text)


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_sha256_pin(value: str) -> str:
    raw = str(value or "").strip().lower()
    if raw.startswith("sha256:"):
        raw = raw[len("sha256:"):]
    return raw


def public_key_pin_report(public_key_path: pathlib.Path, expected_public_key_sha256: str, allow_unpinned_key: bool) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    expected = normalize_sha256_pin(expected_public_key_sha256)
    actual = sha256_file(public_key_path) if public_key_path.exists() else ""
    failures: list[dict[str, Any]] = []
    if not expected and not allow_unpinned_key:
        failures.append({
            "category": "public_key_fingerprint_pin_required",
            "rule": "Provide --expected-public-key-sha256 from a trusted channel, or pass --allow-unpinned-key only for inspection/non-release use.",
        })
    elif expected and (len(expected) != 64 or any(ch not in "0123456789abcdef" for ch in expected)):
        failures.append({"category": "public_key_fingerprint_pin_malformed", "expected_public_key_sha256": expected_public_key_sha256})
    elif expected and actual and actual != expected:
        failures.append({"category": "public_key_fingerprint_pin_mismatch", "expected": expected, "actual": actual})
    return {
        "public_key_sha256": actual,
        "expected_public_key_sha256": expected,
        "public_key_fingerprint_pinned": bool(expected),
        "public_key_pin_match": bool(expected and actual == expected),
        "untrusted_unpinned_key_allowed": bool(allow_unpinned_key and not expected),
    }, failures


def local_verifier_code_pin_report(
    expected_verifier_sha256: str,
    expected_package_checker_sha256: str,
    allow_unpinned_verifier_code: bool,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Check externally supplied fingerprints for the verifier code being run.

    This does not magically establish trust in a verifier process that an
    attacker already controls. It does make the release-evidence command fail
    closed unless the operator supplies hashes for the exact local verifier and
    sibling package-attestation checker obtained from a trusted channel.
    """
    verifier_path = pathlib.Path(__file__).resolve()
    checker_path = verifier_path.parent / "check_package_attestation.py"
    expected_verifier = normalize_sha256_pin(expected_verifier_sha256)
    expected_checker = normalize_sha256_pin(expected_package_checker_sha256)
    actual_verifier = sha256_file(verifier_path) if verifier_path.exists() else ""
    actual_checker = sha256_file(checker_path) if checker_path.exists() else ""
    failures: list[dict[str, Any]] = []

    def add_pin_failure(kind: str, expected: str, actual: str, raw: str) -> None:
        if not expected and not allow_unpinned_verifier_code:
            failures.append({
                "category": f"local_{kind}_fingerprint_pin_required",
                "rule": f"Provide --expected-{kind.replace('_', '-')}-sha256 from a trusted channel, or pass --allow-unpinned-verifier-code only for inspection/non-release use.",
            })
        elif expected and (len(expected) != 64 or any(ch not in "0123456789abcdef" for ch in expected)):
            failures.append({"category": f"local_{kind}_fingerprint_pin_malformed", "expected_sha256": raw})
        elif expected and actual and actual != expected:
            failures.append({"category": f"local_{kind}_fingerprint_pin_mismatch", "expected": expected, "actual": actual})

    add_pin_failure("verifier", expected_verifier, actual_verifier, expected_verifier_sha256)
    add_pin_failure("package_checker", expected_checker, actual_checker, expected_package_checker_sha256)
    if not checker_path.exists():
        failures.append({"category": "local_package_checker_missing", "path": str(checker_path)})

    return {
        "local_verifier_path": str(verifier_path),
        "local_package_checker_path": str(checker_path),
        "local_verifier_sha256": actual_verifier,
        "local_package_checker_sha256": actual_checker,
        "expected_verifier_sha256": expected_verifier,
        "expected_package_checker_sha256": expected_checker,
        "local_verifier_fingerprint_pinned": bool(expected_verifier),
        "local_package_checker_fingerprint_pinned": bool(expected_checker),
        "local_verifier_pin_match": bool(expected_verifier and actual_verifier == expected_verifier),
        "local_package_checker_pin_match": bool(expected_checker and actual_checker == expected_checker),
        "untrusted_unpinned_verifier_code_allowed": bool(allow_unpinned_verifier_code and (not expected_verifier or not expected_checker)),
    }, failures


def load_local_attestation_checker() -> tuple[ModuleType | None, list[dict[str, Any]], dict[str, Any]]:
    """Load the checker next to this verifier, never from the candidate zip.

    This is still executable code, so release-evidence mode now requires the
    operator to pin both this verifier and the sibling checker digests. The
    important boundary here is narrower but critical: do not execute code from a
    fresh extraction of the archive whose integrity is still being evaluated.
    """
    script_dir = pathlib.Path(__file__).resolve().parent
    checker_path = script_dir / "check_package_attestation.py"
    summary = {
        "trust_boundary_mode": TRUST_BOUNDARY_MODE,
        "checker_source": str(checker_path),
        "candidate_extraction_code_executed": False,
    }
    if not checker_path.exists():
        return None, [{"category": "local_package_attestation_checker_missing", "path": str(checker_path)}], summary
    try:
        spec = importlib.util.spec_from_file_location("anonymity_local_check_package_attestation", checker_path)
        if spec is None or spec.loader is None:
            return None, [{"category": "local_package_attestation_checker_load_failed", "path": str(checker_path)}], summary
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001 - user-facing verifier error
        return None, [{"category": "local_package_attestation_checker_import_failed", "path": str(checker_path), "error": str(exc)}], summary
    if not hasattr(module, "check"):
        return None, [{"category": "local_package_attestation_checker_missing_check_function", "path": str(checker_path)}], summary
    return module, [], summary


def zip_member_security(zip_path: pathlib.Path) -> tuple[list[str], list[dict[str, Any]], dict[str, Any]]:
    """Return zip member names, extraction-safety failures, and size-budget summary."""
    failures: list[dict[str, Any]] = []
    names: list[str] = []
    total_uncompressed = 0
    total_compressed = 0
    max_member_uncompressed = 0
    max_member_ratio = 0.0
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            infos = zf.infolist()
            names = [info.filename for info in infos]
            normalized_names = [name.replace("\\", "/") for name in names]
            normalized_set = set(normalized_names)
            if len(names) != len(set(names)):
                failures.append({"category": "duplicate_zip_member_names"})
            casefold_groups: dict[str, list[str]] = {}
            for normalized_name in normalized_names:
                casefold_groups.setdefault(normalized_name.casefold(), []).append(normalized_name)
            casefold_collisions = [sorted(set(group)) for group in casefold_groups.values() if len(set(group)) > 1]
            if casefold_collisions:
                failures.append({"category": "zip_member_casefold_collision", "groups": casefold_collisions[:20], "count": len(casefold_collisions)})
            prefix_collisions: list[dict[str, str]] = []
            for normalized_name in normalized_names:
                parts_for_prefix = normalized_name.split("/")
                for idx in range(1, len(parts_for_prefix)):
                    parent = "/".join(parts_for_prefix[:idx])
                    if parent in normalized_set:
                        prefix_collisions.append({"path": normalized_name, "file_parent": parent})
                        break
            if prefix_collisions:
                failures.append({"category": "zip_member_file_directory_prefix_collision", "collisions": prefix_collisions[:20], "count": len(prefix_collisions)})
            if len(names) > MAX_ZIP_MEMBER_COUNT:
                failures.append({"category": "zip_member_count_exceeds_limit", "count": len(names), "limit": MAX_ZIP_MEMBER_COUNT})
            for info in infos:
                name = info.filename
                normalized = name.replace("\\", "/")
                parts = normalized.split("/")
                mode = (info.external_attr >> 16) & 0o777777
                file_type = mode & 0o170000
                name_bytes = len(name.encode("utf-8", errors="surrogatepass"))
                total_uncompressed += int(info.file_size)
                total_compressed += int(info.compress_size)
                max_member_uncompressed = max(max_member_uncompressed, int(info.file_size))
                ratio = float(info.file_size) / max(1.0, float(info.compress_size))
                max_member_ratio = max(max_member_ratio, ratio)
                if name != normalized:
                    failures.append({"category": "zip_member_backslash_path", "path": name})
                if normalized.startswith("/"):
                    failures.append({"category": "zip_member_absolute_path", "path": name})
                if any(part in {"", ".", ".."} for part in parts if part != parts[-1] or part):
                    failures.append({"category": "zip_member_unsafe_path_component", "path": name})
                if normalized.endswith("/"):
                    failures.append({"category": "zip_member_directory_entry", "path": name})
                if file_type == 0o120000:
                    failures.append({"category": "zip_member_symlink", "path": name})
                elif file_type not in {0, 0o100000}:
                    failures.append({"category": "zip_member_non_regular_file_type", "path": name, "file_type_octal": oct(file_type)})
                if name_bytes > MAX_ZIP_MEMBER_NAME_BYTES:
                    failures.append({"category": "zip_member_name_bytes_exceeds_limit", "path": name, "bytes": name_bytes, "limit": MAX_ZIP_MEMBER_NAME_BYTES})
                if info.compress_type not in ALLOWED_COMPRESSION_TYPES:
                    failures.append({"category": "zip_member_compression_type_not_allowed", "path": name, "compress_type": info.compress_type})
                if info.file_size > MAX_MEMBER_UNCOMPRESSED_BYTES:
                    failures.append({"category": "zip_member_uncompressed_size_exceeds_limit", "path": name, "bytes": info.file_size, "limit": MAX_MEMBER_UNCOMPRESSED_BYTES})
                if ratio > MAX_COMPRESSION_RATIO:
                    failures.append({"category": "zip_member_compression_ratio_exceeds_limit", "path": name, "ratio": round(ratio, 3), "limit": MAX_COMPRESSION_RATIO})
            if total_uncompressed > MAX_TOTAL_UNCOMPRESSED_BYTES:
                failures.append({"category": "zip_total_uncompressed_size_exceeds_limit", "bytes": total_uncompressed, "limit": MAX_TOTAL_UNCOMPRESSED_BYTES})
    except zipfile.BadZipFile as exc:
        failures.append({"category": "zip_bad_file", "error": str(exc)})
    except FileNotFoundError:
        failures.append({"category": "zip_missing", "path": str(zip_path)})
    summary = {
        "member_count": len(names),
        "total_uncompressed_bytes": total_uncompressed,
        "total_compressed_bytes": total_compressed,
        "max_member_uncompressed_bytes": max_member_uncompressed,
        "max_member_compression_ratio": round(max_member_ratio, 3),
        "member_count_limit": MAX_ZIP_MEMBER_COUNT,
        "total_uncompressed_limit_bytes": MAX_TOTAL_UNCOMPRESSED_BYTES,
        "member_uncompressed_limit_bytes": MAX_MEMBER_UNCOMPRESSED_BYTES,
        "member_name_limit_bytes": MAX_ZIP_MEMBER_NAME_BYTES,
        "compression_ratio_limit": MAX_COMPRESSION_RATIO,
        "allowed_compression_types": sorted(ALLOWED_COMPRESSION_TYPES),
    }
    return names, failures, summary


def safe_extract(zip_path: pathlib.Path, out_root: pathlib.Path) -> None:
    """Extract after zip_member_security has accepted the archive.

    The resolve/relative_to guard is redundant after the member-name precheck but
    intentionally remains here as defense in depth.
    """
    root_resolved = out_root.resolve()
    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in zf.infolist():
            target = out_root / info.filename
            resolved = target.resolve()
            try:
                resolved.relative_to(root_resolved)
            except ValueError as exc:  # pragma: no cover - precheck should catch this first.
                raise RuntimeError(f"refusing to extract outside root: {info.filename}") from exc
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info, "r") as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)


def run_local_attestation_checker(
    checker: ModuleType,
    extracted_root: pathlib.Path,
    zip_path: pathlib.Path,
    sha_path: pathlib.Path,
    attestation_path: pathlib.Path,
    envelope_path: pathlib.Path,
    public_key_path: pathlib.Path,
    *,
    require_signature: bool,
    expected_public_key_sha256: str,
) -> tuple[int, dict[str, Any], str]:
    try:
        report = checker.check(
            extracted_root,
            zip_path,
            sha_path,
            attestation_path,
            envelope_path,
            public_key_path,
            require_signature,
            expected_public_key_sha256,
            require_public_key_pin=True,
            allow_unpinned_key=False,
        )
    except Exception as exc:  # noqa: BLE001 - user-facing verifier error
        return 1, {"status": "fail", "failures": [{"category": "local_package_attestation_checker_exception", "error": str(exc)}]}, str(exc)
    return (0 if report.get("status") == "pass" else 1), report, ""


def failure_categories(report: dict[str, Any]) -> set[str]:
    categories: set[str] = set()
    for item in report.get("failures", []):
        if isinstance(item, dict) and item.get("category"):
            categories.add(str(item["category"]))
    return categories


def write_mutated_attestation(src: pathlib.Path, dst: pathlib.Path) -> None:
    rows = [line for line in src.read_text(encoding="utf-8").splitlines() if line.strip()]
    obj = json.loads(rows[0])
    predicate = obj.setdefault("predicate", {})
    run_details = predicate.setdefault("runDetails", {})
    metadata = run_details.setdefault("metadata", {})
    metadata["negative_control_mutation"] = "artifact_set_verifier_payload_mismatch"
    dst.write_text(json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def write_mutated_receipt(src: pathlib.Path, dst: pathlib.Path) -> None:
    line = next((line for line in src.read_text(encoding="utf-8").splitlines() if line.strip()), "")
    parts = line.split("  ", 1)
    filename = parts[1] if len(parts) == 2 else "mutated.zip"
    dst.write_text("0" * 64 + "  " + filename + "\n", encoding="utf-8")


def write_compression_bomb_zip(dst: pathlib.Path) -> None:
    with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.writestr("bomb.txt", b"0" * (1024 * 1024))


def write_path_traversal_zip(dst: pathlib.Path) -> None:
    with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.writestr("../escape.txt", b"escape")

def write_absolute_path_zip(dst: pathlib.Path) -> None:
    with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.writestr("/absolute.txt", b"absolute")


def write_prefix_collision_zip(dst: pathlib.Path) -> None:
    with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.writestr("collide", b"file")
        zf.writestr("collide/child.txt", b"child")


def write_casefold_collision_zip(dst: pathlib.Path) -> None:
    with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.writestr("CaseFold.txt", b"upper")
        zf.writestr("casefold.txt", b"lower")


def write_duplicate_member_zip(dst: pathlib.Path) -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            zf.writestr("dupe.txt", b"first")
            zf.writestr("dupe.txt", b"second")


def write_stored_member_zip(dst: pathlib.Path) -> None:
    with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_STORED) as zf:
        zf.writestr("stored.txt", b"stored")


def write_symlink_member_zip(dst: pathlib.Path) -> None:
    info = zipfile.ZipInfo("link")
    info.external_attr = (0o120777 & 0xFFFF) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.writestr(info, b"target", compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def run_negative_controls(
    checker: ModuleType,
    extracted_root: pathlib.Path,
    zip_path: pathlib.Path,
    sha_path: pathlib.Path,
    attestation_path: pathlib.Path,
    envelope_path: pathlib.Path,
    public_key_path: pathlib.Path,
    expected_public_key_sha256: str,
    expected_verifier_sha256: str,
    expected_package_checker_sha256: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="anonymity_artifactset_controls_") as tmp_s:
        tmp = pathlib.Path(tmp_s)
        mutated_receipt = tmp / "bad.sha256"
        mutated_attestation = tmp / "bad.package.intoto.jsonl"
        missing_envelope = tmp / "missing.package.dsse.json"
        write_mutated_receipt(sha_path, mutated_receipt)
        write_mutated_attestation(attestation_path, mutated_attestation)
        code_pin_controls = [
            {
                "name": "missing_local_verifier_code_fingerprint_pin",
                "expected_verifier_sha256": "",
                "expected_package_checker_sha256": expected_package_checker_sha256,
                "expected_category": "local_verifier_fingerprint_pin_required",
            },
            {
                "name": "wrong_local_verifier_code_fingerprint_pin",
                "expected_verifier_sha256": "0" * 64,
                "expected_package_checker_sha256": expected_package_checker_sha256,
                "expected_category": "local_verifier_fingerprint_pin_mismatch",
            },
            {
                "name": "wrong_local_package_checker_code_fingerprint_pin",
                "expected_verifier_sha256": expected_verifier_sha256,
                "expected_package_checker_sha256": "0" * 64,
                "expected_category": "local_package_checker_fingerprint_pin_mismatch",
            },
        ]
        for control in code_pin_controls:
            _summary, pin_failures = local_verifier_code_pin_report(
                str(control["expected_verifier_sha256"]),
                str(control["expected_package_checker_sha256"]),
                allow_unpinned_verifier_code=False,
            )
            categories = sorted(str(row.get("category", "")) for row in pin_failures)
            ok = str(control["expected_category"]) in categories
            row = {
                "name": control["name"],
                "status": "pass" if ok else "fail",
                "mode": "local_verifier_code_pin_tamper_drill",
                "expected_category": control["expected_category"],
                "observed_categories": categories,
            }
            if not ok:
                failures.append({"category": "negative_control_not_detected", **row})
            rows.append(row)

        package_controls = [
            {
                "name": "missing_package_checker_public_key_fingerprint_pin",
                "sha_path": sha_path,
                "attestation_path": attestation_path,
                "envelope_path": envelope_path,
                "expected_category": "public_key_fingerprint_pin_required",
                "expected_public_key_sha256": "",
            },
            {
                "name": "sha256_receipt_digest_mismatch",
                "sha_path": mutated_receipt,
                "attestation_path": attestation_path,
                "envelope_path": envelope_path,
                "expected_category": "sha256_receipt_digest_mismatch",
            },
            {
                "name": "dsse_payload_mismatch",
                "sha_path": sha_path,
                "attestation_path": mutated_attestation,
                "envelope_path": envelope_path,
                "expected_category": "dsse_payload_does_not_match_package_attestation",
            },
            {
                "name": "missing_required_dsse_envelope",
                "sha_path": sha_path,
                "attestation_path": attestation_path,
                "envelope_path": missing_envelope,
                "expected_category": "dsse_signature_envelope_missing",
                "expected_public_key_sha256": expected_public_key_sha256,
            },
            {
                "name": "wrong_public_key_fingerprint_pin",
                "sha_path": sha_path,
                "attestation_path": attestation_path,
                "envelope_path": envelope_path,
                "expected_category": "public_key_fingerprint_pin_mismatch",
                "expected_public_key_sha256": "0" * 64,
            },
        ]
        for control in package_controls:
            rc, report, error = run_local_attestation_checker(
                checker,
                extracted_root,
                zip_path,
                pathlib.Path(control["sha_path"]),
                pathlib.Path(control["attestation_path"]),
                pathlib.Path(control["envelope_path"]),
                public_key_path,
                require_signature=True,
                expected_public_key_sha256=str(control.get("expected_public_key_sha256", expected_public_key_sha256)),
            )
            categories = sorted(failure_categories(report))
            ok = rc != 0 and report.get("status") == "fail" and str(control["expected_category"]) in categories
            row = {
                "name": control["name"],
                "status": "pass" if ok else "fail",
                "mode": "local_attestation_checker_tamper_drill",
                "returncode": rc,
                "checker_status": report.get("status"),
                "expected_category": control["expected_category"],
                "observed_categories": categories,
                "error_tail": error[-500:],
            }
            if not ok:
                failures.append({"category": "negative_control_not_detected", **row})
            rows.append(row)

        zip_security_controls = [
            {
                "name": "zip_bomb_ratio_guard",
                "writer": write_compression_bomb_zip,
                "expected_category": "zip_member_compression_ratio_exceeds_limit",
            },
            {
                "name": "zip_path_traversal_guard",
                "writer": write_path_traversal_zip,
                "expected_category": "zip_member_unsafe_path_component",
            },
            {
                "name": "zip_absolute_path_guard",
                "writer": write_absolute_path_zip,
                "expected_category": "zip_member_absolute_path",
            },
            {
                "name": "zip_prefix_collision_guard",
                "writer": write_prefix_collision_zip,
                "expected_category": "zip_member_file_directory_prefix_collision",
            },
            {
                "name": "zip_casefold_collision_guard",
                "writer": write_casefold_collision_zip,
                "expected_category": "zip_member_casefold_collision",
            },
            {
                "name": "zip_duplicate_member_guard",
                "writer": write_duplicate_member_zip,
                "expected_category": "duplicate_zip_member_names",
            },
            {
                "name": "zip_stored_member_guard",
                "writer": write_stored_member_zip,
                "expected_category": "zip_member_compression_type_not_allowed",
            },
            {
                "name": "zip_symlink_member_guard",
                "writer": write_symlink_member_zip,
                "expected_category": "zip_member_symlink",
            },
        ]
        for control in zip_security_controls:
            control_zip = tmp / (control["name"] + ".zip")
            control["writer"](control_zip)
            _names, security_failures, security_summary = zip_member_security(control_zip)
            categories = sorted(str(row.get("category", "")) for row in security_failures)
            ok = str(control["expected_category"]) in categories
            row = {
                "name": control["name"],
                "status": "pass" if ok else "fail",
                "mode": "zip_security_preextract_tamper_drill",
                "expected_category": control["expected_category"],
                "observed_categories": categories,
                "zip_security_summary": security_summary,
            }
            if not ok:
                failures.append({"category": "negative_control_not_detected", **row})
            rows.append(row)
    return rows, failures


def check(
    zip_path: pathlib.Path,
    sha_path: pathlib.Path,
    attestation_path: pathlib.Path,
    envelope_path: pathlib.Path,
    public_key_path: pathlib.Path,
    *,
    require_signature: bool,
    run_controls: bool,
    timeout_seconds: int,
    expected_public_key_sha256: str,
    allow_unpinned_key: bool,
    expected_verifier_sha256: str,
    expected_package_checker_sha256: str,
    allow_unpinned_verifier_code: bool,
) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    sidecar_paths = [sha_path, attestation_path, envelope_path, public_key_path]
    key_pin_summary, key_pin_failures = public_key_pin_report(public_key_path, expected_public_key_sha256, allow_unpinned_key)
    failures.extend(key_pin_failures)
    code_pin_summary, code_pin_failures = local_verifier_code_pin_report(
        expected_verifier_sha256,
        expected_package_checker_sha256,
        allow_unpinned_verifier_code,
    )
    failures.extend(code_pin_failures)
    missing_sidecars = [str(path) for path in sidecar_paths if not path.exists()]
    if missing_sidecars:
        failures.append({"category": "artifact_sidecar_missing", "paths": missing_sidecars})
    checker_module, checker_load_failures, checker_boundary = load_local_attestation_checker()
    failures.extend(checker_load_failures)
    names, zip_failures, zip_security_summary = zip_member_security(zip_path)
    failures.extend(zip_failures)
    checker_report: dict[str, Any] = {}
    checker_rc = 127
    checker_error = ""
    controls: list[dict[str, Any]] = []
    control_failures: list[dict[str, Any]] = []
    extracted_member_count = 0
    with tempfile.TemporaryDirectory(prefix="anonymity_artifactset_extract_") as tmp_s:
        extracted = pathlib.Path(tmp_s) / "root"
        extracted.mkdir()
        if not failures and checker_module is not None:
            try:
                safe_extract(zip_path, extracted)
                extracted_member_count = sum(1 for p in extracted.rglob("*") if p.is_file())
            except Exception as exc:  # noqa: BLE001 - user-facing verifier failure
                failures.append({"category": "safe_extract_failed", "error": str(exc)})
            if not failures:
                checker_rc, checker_report, checker_error = run_local_attestation_checker(
                    checker_module,
                    extracted,
                    zip_path,
                    sha_path,
                    attestation_path,
                    envelope_path,
                    public_key_path,
                    require_signature=require_signature,
                    expected_public_key_sha256=expected_public_key_sha256,
                )
                if checker_rc != 0 or checker_report.get("status") != "pass":
                    failures.append({
                        "category": "local_package_attestation_verifier_failed",
                        "returncode": checker_rc,
                        "checker_status": checker_report.get("status"),
                        "checker_failures": checker_report.get("failures", [])[:20],
                        "error_tail": checker_error[-1000:],
                    })
                if run_controls and checker_rc == 0 and checker_report.get("status") == "pass":
                    controls, control_failures = run_negative_controls(
                        checker_module,
                        extracted,
                        zip_path,
                        sha_path,
                        attestation_path,
                        envelope_path,
                        public_key_path,
                        expected_public_key_sha256,
                        expected_verifier_sha256,
                        expected_package_checker_sha256,
                    )
                    failures.extend(control_failures)
    summary = {
        "checks_failed": len(failures),
        "zip_member_count": len(names),
        "extracted_file_count": extracted_member_count,
        "sidecar_count": len(sidecar_paths),
        "missing_sidecar_count": len(missing_sidecars),
        "zip_security_failure_count": len(zip_failures),
        "local_attestation_checker_returncode": checker_rc,
        "local_attestation_checker_status": checker_report.get("status", "not_run"),
        "candidate_package_attestation_verifier_returncode": checker_rc,
        "candidate_package_attestation_verifier_status": checker_report.get("status", "not_run"),
        "legacy_packaged_checker_alias_retained": False,
        "signature_required": require_signature,
        "negative_controls_run": run_controls,
        "negative_control_count": len(controls),
        "negative_control_failed_count": len(control_failures),
        "timeout_seconds_argument_retained_for_cli_compatibility": timeout_seconds,
        **key_pin_summary,
        **code_pin_summary,
        **checker_boundary,
        "zip_security": zip_security_summary,
    }
    return {
        "status": "pass" if not failures else "fail",
        "report_kind": "external_release_artifact_set_verification",
        "zip_path": str(zip_path),
        "sha256_receipt_path": str(sha_path),
        "package_attestation_path": str(attestation_path),
        "signature_envelope_path": str(envelope_path),
        "public_key_sidecar_path": str(public_key_path),
        "summary": summary,
        "candidate_package_attestation_summary": checker_report.get("summary", {}) if isinstance(checker_report, dict) else {},
        "local_attestation_checker_summary": checker_report.get("summary", {}) if isinstance(checker_report, dict) else {},
        "negative_controls": controls,
        "failures": failures[:100],
        "fail_closed_rule": "If the artifact set cannot be verified without executing code from the candidate extraction, without externally pinned public-key and local verifier/checker fingerprints, if zip pre-extraction budgets fail, or if tamper drills are not detected, do not treat the delivered zip/sidecars as release evidence.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="", help="Accepted for tooling-inventory symmetry; verifier code is loaded from this script's directory, not from the candidate zip.")
    parser.add_argument("--zip", required=True)
    parser.add_argument("--sha256", dest="sha_path", default="")
    parser.add_argument("--attestation", dest="attestation_path", default="")
    parser.add_argument("--signature-envelope", dest="envelope_path", default="")
    parser.add_argument("--public-key", dest="public_key_path", default="")
    parser.add_argument("--require-signature", action="store_true", default=True)
    parser.add_argument("--expected-public-key-sha256", default="", help="Required for release-evidence verification: external SHA-256 fingerprint pin for the DSSE public key.")
    parser.add_argument("--allow-unpinned-key", action="store_true", help="Permit unpinned-key inspection mode. Do not use for release evidence.")
    parser.add_argument("--expected-verifier-sha256", default="", help="Required for release-evidence verification: external SHA-256 fingerprint pin for this verifier script.")
    parser.add_argument("--expected-package-checker-sha256", default="", help="Required for release-evidence verification: external SHA-256 fingerprint pin for the local sibling package-attestation checker.")
    parser.add_argument("--allow-unpinned-verifier-code", action="store_true", help="Permit unpinned local verifier/checker code inspection mode. Do not use for release evidence.")
    parser.add_argument("--skip-negative-controls", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()
    zip_path = pathlib.Path(args.zip).resolve()
    sha_path = pathlib.Path(args.sha_path).resolve() if args.sha_path else sha_path_for(zip_path)
    attestation_path = pathlib.Path(args.attestation_path).resolve() if args.attestation_path else attestation_path_for(zip_path)
    envelope_path = pathlib.Path(args.envelope_path).resolve() if args.envelope_path else envelope_path_for(zip_path)
    public_key_path = pathlib.Path(args.public_key_path).resolve() if args.public_key_path else public_key_sidecar_path_for(zip_path)
    report = check(
        zip_path,
        sha_path,
        attestation_path,
        envelope_path,
        public_key_path,
        require_signature=args.require_signature,
        run_controls=not args.skip_negative_controls,
        timeout_seconds=max(1, args.timeout_seconds),
        expected_public_key_sha256=args.expected_public_key_sha256,
        allow_unpinned_key=args.allow_unpinned_key,
        expected_verifier_sha256=args.expected_verifier_sha256,
        expected_package_checker_sha256=args.expected_package_checker_sha256,
        allow_unpinned_verifier_code=args.allow_unpinned_verifier_code,
    )
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = pathlib.Path(args.write_report).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
