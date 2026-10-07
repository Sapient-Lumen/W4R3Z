#!/usr/bin/env python3
"""Build the release zip from the current archive root.

The packager is deterministic with respect to member ordering, compression mode,
member timestamps, and member permission bits. It refuses to package a tree
whose current bytes no longer match MANIFEST.sha256, so MANIFEST.json is the
file-list boundary and MANIFEST.sha256 is the content-lock boundary. Permission
bits are declared by archive policy rather than copied from the local extraction
filesystem, because ordinary Python zip extraction may drop executable bits.
"""

from __future__ import annotations

import argparse
import calendar
import datetime as _dt
import hashlib
import json
import os
import pathlib
import zipfile
from typing import Any

EXCLUDE_DIR_NAMES = {".git", "__pycache__", ".pytest_cache", ".mypy_cache"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".aux", ".log", ".out", ".toc", ".fls", ".fdb_latexmk", ".synctex.gz"}
ALLOWED_UNLISTED_SHA256 = {"MANIFEST.sha256"}
EXECUTABLE_ZIP_PATHS = frozenset({
    "publishing/check_worked_example_validation.py",
})
PACKAGE_ATTESTATION_PREDICATE_TYPE = "https://slsa.dev/provenance/v1"
PACKAGE_ATTESTATION_STATEMENT_TYPE = "https://in-toto.io/Statement/v1"


def zip_member_permissions(rel: str) -> int:
    """Return the canonical Unix permission bits for a zip member.

    Do not derive this from path.stat(); cloudtainer extraction paths can lose
    executable metadata even when file bytes and manifest digests are intact.
    """
    return 0o755 if rel in EXECUTABLE_ZIP_PATHS else 0o644


def zip_sha256_receipt_path(out_path: pathlib.Path) -> pathlib.Path:
    return out_path.with_suffix(out_path.suffix + ".sha256")


def package_attestation_path(out_path: pathlib.Path) -> pathlib.Path:
    return out_path.with_suffix(out_path.suffix + ".package.intoto.jsonl")


def package_dsse_envelope_path(out_path: pathlib.Path) -> pathlib.Path:
    return out_path.with_suffix(out_path.suffix + ".package.dsse.json")


def package_dsse_public_key_sidecar_path(out_path: pathlib.Path) -> pathlib.Path:
    return out_path.with_suffix(out_path.suffix + ".package.dsse.pub.pem")


def output_artifact_paths(out_path: pathlib.Path | None) -> set[pathlib.Path]:
    if out_path is None:
        return set()
    return {
        out_path.resolve(),
        zip_sha256_receipt_path(out_path).resolve(),
        package_attestation_path(out_path).resolve(),
        package_dsse_envelope_path(out_path).resolve(),
        package_dsse_public_key_sidecar_path(out_path).resolve(),
    }


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def release_date_parts(release: dict[str, Any]) -> tuple[int, int, int]:
    parts = str(release["timestamp"]).split(".")
    if len(parts) < 3:
        raise RuntimeError(f"release timestamp is not YYYY.MM.DD.*: {release.get('timestamp')!r}")
    return int(parts[0]), int(parts[1]), int(parts[2])


def release_date_midnight_epoch(release: dict[str, Any]) -> int:
    year, month, day = release_date_parts(release)
    return calendar.timegm((year, month, day, 0, 0, 0))


def dos_datetime_from_epoch(epoch: int) -> tuple[int, int, int, int, int, int]:
    dt = _dt.datetime.fromtimestamp(epoch, tz=_dt.timezone.utc)
    if dt.year < 1980:
        raise RuntimeError("SOURCE_DATE_EPOCH resolves before the ZIP timestamp lower bound of 1980-01-01")
    return (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)


def zip_timestamp_policy(release: dict[str, Any]) -> dict[str, Any]:
    """Return the canonical timestamp policy for release zip members.

    The archive now names SOURCE_DATE_EPOCH as the reproducible-build input, but
    it is not allowed to silently change member timestamps.  If the environment
    variable is supplied it must equal the release-date midnight epoch in UTC;
    otherwise the packager defaults to that same epoch.
    """
    expected_epoch = release_date_midnight_epoch(release)
    raw = os.environ.get("SOURCE_DATE_EPOCH")
    if raw is None or raw.strip() == "":
        effective_epoch = expected_epoch
        status = "unset_defaulted_to_release_date_midnight_utc"
        source = "release_manifest_timestamp_date"
    else:
        try:
            effective_epoch = int(raw.strip())
        except ValueError as exc:
            raise RuntimeError(f"SOURCE_DATE_EPOCH must be an integer Unix epoch, got {raw!r}") from exc
        if effective_epoch != expected_epoch:
            raise RuntimeError(
                "SOURCE_DATE_EPOCH must match the release date at 00:00:00 UTC "
                f"for this deterministic archive: expected {expected_epoch}, got {effective_epoch}"
            )
        status = "set_matches_release_date_midnight_utc"
        source = "SOURCE_DATE_EPOCH"
    zip_dt = dos_datetime_from_epoch(effective_epoch)
    return {
        "environment_variable": "SOURCE_DATE_EPOCH",
        "status": status,
        "source": source,
        "provided_value": raw.strip() if raw is not None else "",
        "expected_epoch_utc": expected_epoch,
        "effective_epoch_utc": effective_epoch,
        "zip_datetime": list(zip_dt),
        "rule": "SOURCE_DATE_EPOCH is accepted only when it equals the release date at midnight UTC; unset defaults to that value.",
    }


def zip_datetime(release: dict[str, Any]) -> tuple[int, int, int, int, int, int]:
    return tuple(int(x) for x in zip_timestamp_policy(release)["zip_datetime"])


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def should_exclude(path: pathlib.Path, root: pathlib.Path, out_path: pathlib.Path | None) -> bool:
    rel = path.relative_to(root).as_posix()
    parts = rel.split("/")
    if any(part in EXCLUDE_DIR_NAMES for part in parts):
        return True
    if path.name == ".DS_Store":
        return True
    if any(path.name.endswith(suffix) for suffix in EXCLUDE_SUFFIXES):
        return True
    if out_path is not None:
        try:
            if path.resolve() in output_artifact_paths(out_path):
                return True
        except FileNotFoundError:
            pass
    return False


def candidate_files(root: pathlib.Path, out_path: pathlib.Path | None = None) -> list[pathlib.Path]:
    return sorted(
        (p for p in root.rglob("*") if p.is_file() and not should_exclude(p, root, out_path)),
        key=lambda p: p.relative_to(root).as_posix(),
    )


def manifest_files(root: pathlib.Path) -> list[str]:
    manifest = load_json(root / "MANIFEST.json")
    files = manifest.get("files", [])
    if not isinstance(files, list):
        raise RuntimeError("MANIFEST.json does not contain a files array")
    return sorted(str(x) for x in files)


def parse_manifest_sha256(path: pathlib.Path) -> tuple[dict[str, str], list[dict[str, Any]]]:
    entries: dict[str, str] = {}
    failures: list[dict[str, Any]] = []
    if not path.exists():
        return entries, [{"category": "manifest_sha256_missing", "path": "MANIFEST.sha256"}]
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 64 or any(ch not in "0123456789abcdef" for ch in parts[0]):
            failures.append({"category": "manifest_sha256_malformed_line", "line": lineno})
            continue
        digest, rel = parts
        if rel in entries:
            failures.append({"category": "manifest_sha256_duplicate_path", "path": rel, "line": lineno})
        entries[rel] = digest
    return entries, failures


def manifest_digest_report(root: pathlib.Path, manifest_rels: list[str]) -> dict[str, Any]:
    entries, parse_failures = parse_manifest_sha256(root / "MANIFEST.sha256")
    manifest_set = set(manifest_rels)
    digest_required = manifest_set - ALLOWED_UNLISTED_SHA256
    entry_set = set(entries)
    missing_entries = sorted(digest_required - entry_set)
    extra_entries = sorted(entry_set - digest_required)
    digest_mismatches: list[dict[str, str]] = []
    for rel in sorted(digest_required & entry_set):
        path = root / rel
        if not path.exists() or not path.is_file():
            digest_mismatches.append({"path": rel, "expected": entries[rel], "actual": "missing"})
            continue
        actual = sha256_file(path)
        if actual != entries[rel]:
            digest_mismatches.append({"path": rel, "expected": entries[rel], "actual": actual})
    failures = []
    if parse_failures:
        failures.append({"category": "manifest_sha256_parse_failures", "failures": parse_failures[:50], "count": len(parse_failures)})
    if missing_entries:
        failures.append({"category": "manifest_sha256_missing_entries", "paths": missing_entries[:50], "count": len(missing_entries)})
    if extra_entries:
        failures.append({"category": "manifest_sha256_extra_entries", "paths": extra_entries[:50], "count": len(extra_entries)})
    if digest_mismatches:
        failures.append({"category": "manifest_sha256_digest_mismatch", "mismatches": digest_mismatches[:50], "count": len(digest_mismatches)})
    return {
        "status": "pass" if not failures else "fail",
        "manifest_sha256_path": "MANIFEST.sha256",
        "allowed_unlisted_sha256_paths": sorted(ALLOWED_UNLISTED_SHA256),
        "entry_count": len(entries),
        "digest_required_count": len(digest_required),
        "missing_entry_count": len(missing_entries),
        "extra_entry_count": len(extra_entries),
        "digest_mismatch_count": len(digest_mismatches),
        "parse_failure_count": len(parse_failures),
        "failures": failures[:50],
    }


def package_attestation_statement(root: pathlib.Path, out_path: pathlib.Path, zip_digest: str, zip_bytes: int, input_file_count: int, timestamp_policy: dict[str, Any]) -> dict[str, Any]:
    """Build a deterministic package-level provenance statement for the zip.

    The in-archive provenance binds important source/report surfaces, but it
    cannot name the final zip digest without a circular dependency.  This sidecar
    statement binds the final zip itself to the exact manifest digest lock and
    deterministic packaging policy.  It is deliberately unsigned; callers can
    sign the sidecar or zip with an external identity key without changing the
    archive bytes.
    """
    release = load_json(root / "RELEASE_MANIFEST.json")
    receipt = load_json(root / "REVISION_RECEIPT.json")
    return {
        "_type": PACKAGE_ATTESTATION_STATEMENT_TYPE,
        "subject": [
            {
                "name": out_path.name,
                "digest": {"sha256": zip_digest},
            }
        ],
        "predicateType": PACKAGE_ATTESTATION_PREDICATE_TYPE,
        "predicate": {
            "buildDefinition": {
                "buildType": "https://example.invalid/anonymity-datacube/deterministic-zip-package/v1",
                "externalParameters": {
                    "project": release["project"],
                    "revision": release["revision"],
                    "timestamp": release["timestamp"],
                    "bundle": release["bundle"],
                    "slug": release.get("slug", ""),
                    "publication_action": receipt.get("publication_action", "none"),
                    "publication_authorized": False,
                    "source_date_epoch": timestamp_policy,
                },
                "internalParameters": {
                    "packaging_script": "publishing/build_archive_zip.py",
                    "member_order": "lexicographic repo-relative path",
                    "compression": "ZIP_DEFLATED level 9",
                    "member_permission_policy": "declared_archive_policy_not_ambient_filesystem_mode",
                    "executable_zip_paths": sorted(EXECUTABLE_ZIP_PATHS),
                    "input_file_count": input_file_count,
                    "manifest_file_count": input_file_count,
                    "package_attestation_authentication": "unsigned_sidecar_statement_with_dsse_envelope; verify digest binding locally and require DSSE verification plus external public-key and local verifier/checker fingerprint pins when distributing as release evidence",
                    "package_attestation_signing_public_key": "signing/package_attestation_public_key.pem",
                },
                "resolvedDependencies": [
                    digest_entry(root, "MANIFEST.sha256"),
                    digest_entry(root, "MANIFEST.json"),
                    digest_entry(root, "RELEASE_MANIFEST.json"),
                    digest_entry(root, "REVISION_RECEIPT.json"),
                    digest_entry(root, "release_provenance.intoto.jsonl"),
                    digest_entry(root, "requirements.txt"),
                    digest_entry(root, "signing/package_attestation_public_key.pem"),
                    digest_entry(root, "publishing/build_archive_zip.py"),
                    digest_entry(root, "publishing/check_package_attestation.py"),
                    digest_entry(root, "publishing/sign_package_attestation_dsse.py"),
                    digest_entry(root, "publishing/verify_release_artifact_set.py"),
                ],
            },
            "runDetails": {
                "builder": {"id": "https://example.invalid/anonymity-datacube/local-cloudtainer-packager"},
                "metadata": {
                    "reproducible": True,
                    "completeness": {"parameters": True, "environment": False, "materials": True},
                    "zip_bytes": zip_bytes,
                    "zip_sha256": zip_digest,
                    "sidecar_scope": "final zip digest plus deterministic package recipe; not an identity signature",
                },
            },
        },
    }


def digest_entry(root: pathlib.Path, rel: str) -> dict[str, Any]:
    return {"uri": "file:" + rel, "digest": {"sha256": sha256_file(root / rel)}}


def write_package_attestation(root: pathlib.Path, out_path: pathlib.Path, zip_digest: str, zip_bytes: int, input_file_count: int, timestamp_policy: dict[str, Any]) -> pathlib.Path:
    statement = package_attestation_statement(root, out_path, zip_digest, zip_bytes, input_file_count, timestamp_policy)
    attestation_path = package_attestation_path(out_path)
    attestation_path.write_text(json.dumps(statement, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return attestation_path


def write_package_public_key_sidecar(root: pathlib.Path, out_path: pathlib.Path) -> pathlib.Path:
    src = root / "signing" / "package_attestation_public_key.pem"
    dst = package_dsse_public_key_sidecar_path(out_path)
    dst.write_bytes(src.read_bytes())
    return dst


def package_report(root: pathlib.Path, out_dir: pathlib.Path | None) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    bundle = str(release["bundle"])
    out_path = (out_dir / bundle).resolve() if out_dir else None
    files = candidate_files(root, out_path)
    file_rels = [p.relative_to(root).as_posix() for p in files]
    manifest_rels = manifest_files(root)
    missing_from_zip = sorted(set(manifest_rels) - set(file_rels))
    extra_in_zip = sorted(set(file_rels) - set(manifest_rels))
    digest_check = manifest_digest_report(root, manifest_rels)
    ok = not missing_from_zip and not extra_in_zip and digest_check.get("status") == "pass"
    timestamp_policy = zip_timestamp_policy(release)
    zip_dt = tuple(int(x) for x in timestamp_policy["zip_datetime"])
    return {
        "status": "pass" if ok else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": bundle,
        "publication_authorized": False,
        "bundle": bundle,
        "zip_timestamp_policy": "SOURCE_DATE_EPOCH_or_release_date_midnight_utc",
        "source_date_epoch": timestamp_policy,
        "zip_timestamp": list(zip_dt),
        "compression": "ZIP_DEFLATED level 9",
        "member_order": "lexicographic repo-relative path",
        "member_permission_policy": "declared_archive_policy_not_ambient_filesystem_mode",
        "package_attestation_policy": "external_in_toto_slsa_statement_with_required_dsse_signature_external_public_key_pin_and_local_verifier_code_pins_for_release_evidence",
        "package_attestation_public_key_sidecar_policy": "packager_copies_manifest_bound_public_key_next_to_zip_for_external_verifiers",
        "package_attestation_statement_type": PACKAGE_ATTESTATION_STATEMENT_TYPE,
        "package_attestation_predicate_type": PACKAGE_ATTESTATION_PREDICATE_TYPE,
        "executable_zip_paths": sorted(EXECUTABLE_ZIP_PATHS),
        "input_file_count": len(file_rels),
        "manifest_file_count": len(manifest_rels),
        "missing_from_zip": missing_from_zip[:50],
        "extra_in_zip": extra_in_zip[:50],
        "manifest_digest_check": digest_check,
        "summary": {
            "checks_failed": 0 if ok else 1,
            "input_file_count": len(file_rels),
            "manifest_file_count": len(manifest_rels),
            "missing_from_zip_count": len(missing_from_zip),
            "extra_in_zip_count": len(extra_in_zip),
            "manifest_digest_status": digest_check.get("status"),
            "manifest_digest_mismatch_count": digest_check.get("digest_mismatch_count", 0),
            "manifest_sha256_entry_count": digest_check.get("entry_count", 0),
        },
        "fail_closed_rule": "If packaging inputs differ from MANIFEST.json, current bytes differ from MANIFEST.sha256, or the signing public key is not manifest-bound, rebuild surfaces before producing a release zip.",
    }


def build_zip(root: pathlib.Path, out_dir: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = (out_dir / release["bundle"]).resolve()
    report = package_report(root, out_dir)
    if report["status"] != "pass":
        raise RuntimeError("packaging recipe failed manifest filename or digest parity check")
    files = candidate_files(root, out_path)
    zip_dt = zip_datetime(release)
    tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")
    if tmp_path.exists():
        tmp_path.unlink()
    with zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in files:
            rel = path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(rel, date_time=zip_dt)
            perms = zip_member_permissions(rel)
            info.external_attr = (perms & 0xFFFF) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            with path.open("rb") as handle:
                zf.writestr(info, handle.read(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    tmp_path.replace(out_path)
    digest = sha256_file(out_path)
    sha_path = zip_sha256_receipt_path(out_path)
    sha_path.write_text(f"{digest}  {out_path.name}\n", encoding="utf-8")
    attestation_path = write_package_attestation(root, out_path, digest, out_path.stat().st_size, len(files), zip_timestamp_policy(release))
    public_key_sidecar_path = write_package_public_key_sidecar(root, out_path)
    report.update({
        "status": "pass",
        "written_zip": str(out_path),
        "written_sha256_receipt": str(sha_path),
        "written_package_attestation": str(attestation_path),
        "written_public_key_sidecar": str(public_key_sidecar_path),
        "zip_sha256": digest,
        "zip_bytes": out_path.stat().st_size,
        "package_attestation_sha256": sha256_file(attestation_path),
        "package_attestation_public_key_sidecar_sha256": sha256_file(public_key_sidecar_path),
    })
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default="..")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    out_dir = pathlib.Path(args.out_dir).resolve()
    try:
        report = package_report(root, out_dir) if args.dry_run else build_zip(root, out_dir)
    except Exception as exc:  # noqa: BLE001 - user-facing packager error
        report = {"status": "fail", "error": str(exc)}
    text = json.dumps(report, indent=2) + "\n"
    if args.json or args.dry_run:
        print(text, end="")
    else:
        if report.get("status") == "pass":
            print(report.get("written_zip"))
            print(report.get("zip_sha256"))
        else:
            print(text, file=__import__('sys').stderr)
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
