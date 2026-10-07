#!/usr/bin/env python3
"""Verify external release zip, receipts, package attestation, and DSSE signature.

The archive carries internal provenance for source/report surfaces.  The final
zip digest is necessarily a sidecar fact: putting the final zip digest inside the
zip would change the zip. This verifier checks that the sidecar SHA-256 receipt,
package-level in-toto/SLSA statement, optional DSSE envelope, public-key
fingerprint pin, and zip-internal manifest agree. When --require-signature
is used from the CLI, the DSSE envelope must verify against the manifest-bound
public key and a trusted --expected-public-key-sha256 pin is required unless the
operator deliberately chooses inspection-only unpinned mode.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import calendar
import hashlib
import json
import pathlib
import subprocess
import tempfile
import zipfile
from typing import Any

STATEMENT_TYPE = "https://in-toto.io/Statement/v1"
PREDICATE_TYPE = "https://slsa.dev/provenance/v1"
DSSE_PAYLOAD_TYPE = "application/vnd.in-toto+json"
DEFAULT_PUBLIC_KEY = "signing/package_attestation_public_key.pem"
EXPECTED_DEPENDENCY_PATHS = {
    "MANIFEST.sha256",
    "MANIFEST.json",
    "RELEASE_MANIFEST.json",
    "REVISION_RECEIPT.json",
    "release_provenance.intoto.jsonl",
    "requirements.txt",
    "signing/package_attestation_public_key.pem",
    "publishing/build_archive_zip.py",
    "publishing/check_package_attestation.py",
    "publishing/sign_package_attestation_dsse.py",
    "publishing/verify_release_artifact_set.py",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def default_paths(root: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path, pathlib.Path, pathlib.Path, pathlib.Path]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    zip_path = (root.parent / release["bundle"]).resolve()
    return (
        zip_path,
        zip_path.with_suffix(zip_path.suffix + ".sha256"),
        zip_path.with_suffix(zip_path.suffix + ".package.intoto.jsonl"),
        zip_path.with_suffix(zip_path.suffix + ".package.dsse.json"),
        (root / DEFAULT_PUBLIC_KEY).resolve(),
    )


def parse_sha256_receipt(path: pathlib.Path) -> tuple[str, str, list[dict[str, Any]]]:
    failures: list[dict[str, Any]] = []
    if not path.exists():
        return "", "", [{"category": "sha256_receipt_missing", "path": str(path)}]
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(lines) != 1:
        failures.append({"category": "sha256_receipt_line_count", "line_count": len(lines)})
        return "", "", failures
    parts = lines[0].split("  ", 1)
    if len(parts) != 2 or len(parts[0]) != 64 or any(ch not in "0123456789abcdef" for ch in parts[0]):
        failures.append({"category": "sha256_receipt_malformed"})
        return "", "", failures
    return parts[0], parts[1], failures


def load_statement(path: pathlib.Path) -> tuple[dict[str, Any], bytes, list[dict[str, Any]]]:
    failures: list[dict[str, Any]] = []
    if not path.exists():
        return {}, b"", [{"category": "package_attestation_missing", "path": str(path)}]
    raw = path.read_bytes()
    lines = [line for line in raw.decode("utf-8", errors="replace").splitlines() if line.strip()]
    if len(lines) != 1:
        failures.append({"category": "package_attestation_line_count", "line_count": len(lines)})
        return {}, raw, failures
    try:
        statement = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        return {}, raw, [{"category": "package_attestation_json_decode", "error": str(exc)}]
    return statement, raw, failures


def zip_member_bytes(zf: zipfile.ZipFile, name: str) -> bytes | None:
    try:
        return zf.read(name)
    except KeyError:
        return None


def parse_manifest_sha256(text: str) -> tuple[dict[str, str], list[dict[str, Any]]]:
    entries: dict[str, str] = {}
    failures: list[dict[str, Any]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
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


def verify_zip_manifest(zf: zipfile.ZipFile) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    failures: list[dict[str, Any]] = []
    names = sorted(info.filename for info in zf.infolist())
    if len(names) != len(set(names)):
        failures.append({"category": "zip_duplicate_member_names"})
    manifest_raw = zip_member_bytes(zf, "MANIFEST.json")
    manifest_sha_raw = zip_member_bytes(zf, "MANIFEST.sha256")
    if manifest_raw is None:
        failures.append({"category": "zip_manifest_json_missing"})
        manifest_files: list[str] = []
    else:
        try:
            manifest = json.loads(manifest_raw.decode("utf-8"))
            manifest_files = sorted(str(item) for item in manifest.get("files", []))
        except Exception as exc:  # noqa: BLE001
            failures.append({"category": "zip_manifest_json_decode", "error": str(exc)})
            manifest_files = []
    if manifest_sha_raw is None:
        failures.append({"category": "zip_manifest_sha256_missing"})
        entries: dict[str, str] = {}
    else:
        entries, parse_failures = parse_manifest_sha256(manifest_sha_raw.decode("utf-8", errors="replace"))
        failures.extend(parse_failures)
    if manifest_files and manifest_files != names:
        failures.append({
            "category": "zip_manifest_file_list_mismatch",
            "manifest_only_count": len(sorted(set(manifest_files) - set(names))),
            "zip_only_count": len(sorted(set(names) - set(manifest_files))),
            "manifest_only_sample": sorted(set(manifest_files) - set(names))[:20],
            "zip_only_sample": sorted(set(names) - set(manifest_files))[:20],
        })
    digest_required = sorted(set(names) - {"MANIFEST.sha256"})
    missing_digest_entries = sorted(set(digest_required) - set(entries))
    extra_digest_entries = sorted(set(entries) - set(digest_required))
    if missing_digest_entries:
        failures.append({"category": "zip_manifest_sha256_missing_entries", "count": len(missing_digest_entries), "paths": missing_digest_entries[:20]})
    if extra_digest_entries:
        failures.append({"category": "zip_manifest_sha256_extra_entries", "count": len(extra_digest_entries), "paths": extra_digest_entries[:20]})
    mismatches: list[dict[str, str]] = []
    for rel in digest_required:
        data = zip_member_bytes(zf, rel)
        if data is None:
            mismatches.append({"path": rel, "expected": entries.get(rel, ""), "actual": "missing"})
        elif entries.get(rel) != sha256_bytes(data):
            mismatches.append({"path": rel, "expected": entries.get(rel, ""), "actual": sha256_bytes(data)})
    if mismatches:
        failures.append({"category": "zip_manifest_sha256_digest_mismatch", "count": len(mismatches), "mismatches": mismatches[:20]})
    sidecar_members = [
        name
        for name in names
        if name.endswith(".zip.sha256")
        or name.endswith(".package.intoto.jsonl")
        or name.endswith(".package.dsse.json")
        or name.endswith(".package.dsse.pub.pem")
    ]
    if sidecar_members:
        failures.append({"category": "zip_contains_external_sidecar_members", "paths": sidecar_members[:20], "count": len(sidecar_members)})
    return {
        "zip_member_count": len(names),
        "manifest_file_count": len(manifest_files),
        "manifest_sha256_entry_count": len(entries),
        "first_members": names[:5],
        "last_members": names[-5:],
    }, failures


def dependency_paths(dependencies: list[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    for dep in dependencies:
        uri = str(dep.get("uri", ""))
        if uri.startswith("file:"):
            out.append(uri[len("file:"):])
    return sorted(out)


def dependency_digest_failures(zf: zipfile.ZipFile, dependencies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    for dep in dependencies:
        uri = str(dep.get("uri", ""))
        if not uri.startswith("file:"):
            failures.append({"category": "attestation_dependency_uri_not_file", "uri": uri})
            continue
        rel = uri[len("file:"):]
        expected = dep.get("digest", {}).get("sha256")
        if not expected:
            failures.append({"category": "attestation_dependency_missing_sha256", "uri": uri})
            continue
        data = zip_member_bytes(zf, rel)
        if data is None:
            failures.append({"category": "attestation_dependency_missing_from_zip", "path": rel})
            continue
        actual = sha256_bytes(data)
        if actual != expected:
            failures.append({"category": "attestation_dependency_digest_mismatch", "path": rel, "expected": expected, "actual": actual})
    return failures


def release_date_midnight_epoch(release: dict[str, Any]) -> int:
    year, month, day = (int(part) for part in str(release["timestamp"]).split(".")[:3])
    return calendar.timegm((year, month, day, 0, 0, 0))


def dsse_preauth_encoding(payload_type: str, payload: bytes) -> bytes:
    payload_type_bytes = payload_type.encode("utf-8")
    return b"DSSEv1 " + str(len(payload_type_bytes)).encode("ascii") + b" " + payload_type_bytes + b" " + str(len(payload)).encode("ascii") + b" " + payload


def public_key_id(public_key_path: pathlib.Path) -> str:
    return "sha256:" + sha256_file(public_key_path)


def normalize_sha256_pin(value: str) -> str:
    """Return a lowercase bare SHA-256 hex string from a bare or sha256: pin."""
    raw = str(value or "").strip().lower()
    if raw.startswith("sha256:"):
        raw = raw[len("sha256:"):]
    return raw


def key_pin_failures(
    public_key_path: pathlib.Path,
    expected_public_key_sha256: str,
    *,
    require_public_key_pin: bool = False,
    allow_unpinned_key: bool = False,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    expected = normalize_sha256_pin(expected_public_key_sha256)
    actual = sha256_file(public_key_path) if public_key_path.exists() else ""
    failures: list[dict[str, Any]] = []
    if not expected and require_public_key_pin and not allow_unpinned_key:
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
        "public_key_pin_required": bool(require_public_key_pin),
        "public_key_pin_match": bool(expected and actual == expected),
        "untrusted_unpinned_key_allowed": bool(allow_unpinned_key and not expected),
    }, failures


def verify_openssl_signature(public_key_path: pathlib.Path, preauth: bytes, signature: bytes) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory(prefix="anonymity_dsse_check_") as tmp_s:
        tmp = pathlib.Path(tmp_s)
        msg = tmp / "preauth.bin"
        sig = tmp / "signature.bin"
        msg.write_bytes(preauth)
        sig.write_bytes(signature)
        try:
            proc = subprocess.run(
                ["openssl", "pkeyutl", "-verify", "-rawin", "-pubin", "-inkey", str(public_key_path), "-in", str(msg), "-sigfile", str(sig)],
                text=True,
                capture_output=True,
                timeout=15,
            )
        except Exception as exc:  # noqa: BLE001
            return False, f"openssl verification invocation failed: {exc}"
    return proc.returncode == 0, (proc.stdout + proc.stderr)[-1000:]


def check_dsse_envelope(
    envelope_path: pathlib.Path,
    public_key_path: pathlib.Path,
    attestation_bytes: bytes,
    require_signature: bool,
    expected_public_key_sha256: str = "",
    *,
    require_public_key_pin: bool = False,
    allow_unpinned_key: bool = False,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    failures: list[dict[str, Any]] = []
    pin_summary, pin_failures = key_pin_failures(
        public_key_path,
        expected_public_key_sha256,
        require_public_key_pin=require_public_key_pin,
        allow_unpinned_key=allow_unpinned_key,
    )
    failures.extend(pin_failures)
    summary: dict[str, Any] = {
        "signature_required": require_signature,
        "signature_envelope_present": envelope_path.exists(),
        "public_key_present": public_key_path.exists(),
        "signature_verified": False,
        "keyid": "",
        **pin_summary,
    }
    if not envelope_path.exists():
        if require_signature:
            failures.append({"category": "dsse_signature_envelope_missing", "path": str(envelope_path)})
        return summary, failures
    if not public_key_path.exists():
        failures.append({"category": "dsse_public_key_missing", "path": str(public_key_path)})
        return summary, failures
    try:
        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append({"category": "dsse_envelope_json_decode", "error": str(exc)})
        return summary, failures
    if envelope.get("payloadType") != DSSE_PAYLOAD_TYPE:
        failures.append({"category": "dsse_payload_type_mismatch", "expected": DSSE_PAYLOAD_TYPE, "actual": envelope.get("payloadType")})
    try:
        payload = base64.b64decode(str(envelope.get("payload", "")), validate=True)
    except (binascii.Error, ValueError) as exc:
        failures.append({"category": "dsse_payload_base64_decode_failed", "error": str(exc)})
        payload = b""
    if payload != attestation_bytes:
        failures.append({"category": "dsse_payload_does_not_match_package_attestation", "payload_sha256": sha256_bytes(payload), "attestation_sha256": sha256_bytes(attestation_bytes)})
    signatures = envelope.get("signatures", [])
    if not isinstance(signatures, list) or len(signatures) != 1 or not isinstance(signatures[0], dict):
        failures.append({"category": "dsse_signature_count_not_one", "count": len(signatures) if isinstance(signatures, list) else "not_list"})
        return summary, failures
    sig_row = signatures[0]
    expected_keyid = public_key_id(public_key_path)
    actual_keyid = str(sig_row.get("keyid", ""))
    summary["keyid"] = actual_keyid
    if actual_keyid != expected_keyid:
        failures.append({"category": "dsse_keyid_mismatch", "expected": expected_keyid, "actual": actual_keyid})
    try:
        signature = base64.b64decode(str(sig_row.get("sig", "")), validate=True)
    except (binascii.Error, ValueError) as exc:
        failures.append({"category": "dsse_signature_base64_decode_failed", "error": str(exc)})
        return summary, failures
    ok, detail = verify_openssl_signature(public_key_path, dsse_preauth_encoding(str(envelope.get("payloadType", "")), payload), signature)
    summary["signature_verified"] = ok
    summary["openssl_verify_tail"] = detail[-200:]
    if not ok:
        failures.append({"category": "dsse_signature_verification_failed", "detail_tail": detail})
    return summary, failures


def check(
    root: pathlib.Path,
    zip_path: pathlib.Path,
    sha_path: pathlib.Path,
    attestation_path: pathlib.Path,
    envelope_path: pathlib.Path,
    public_key_path: pathlib.Path,
    require_signature: bool,
    expected_public_key_sha256: str = "",
    require_public_key_pin: bool = False,
    allow_unpinned_key: bool = False,
) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    receipt = load_json(root / "REVISION_RECEIPT.json")
    failures: list[dict[str, Any]] = []
    zip_digest = sha256_file(zip_path) if zip_path.exists() else ""
    zip_bytes = zip_path.stat().st_size if zip_path.exists() else 0
    if not zip_path.exists():
        failures.append({"category": "zip_missing", "path": str(zip_path)})

    receipt_digest, receipt_name, receipt_failures = parse_sha256_receipt(sha_path)
    failures.extend(receipt_failures)
    if receipt_digest and receipt_digest != zip_digest:
        failures.append({"category": "sha256_receipt_digest_mismatch", "expected": receipt_digest, "actual": zip_digest})
    if receipt_name and receipt_name != zip_path.name:
        failures.append({"category": "sha256_receipt_filename_mismatch", "expected": zip_path.name, "actual": receipt_name})

    statement, attestation_bytes, statement_failures = load_statement(attestation_path)
    failures.extend(statement_failures)
    subject = statement.get("subject", []) if isinstance(statement, dict) else []
    predicate = statement.get("predicate", {}) if isinstance(statement, dict) else {}
    build_definition = predicate.get("buildDefinition", {}) if isinstance(predicate, dict) else {}
    external = build_definition.get("externalParameters", {}) if isinstance(build_definition, dict) else {}
    internal = build_definition.get("internalParameters", {}) if isinstance(build_definition, dict) else {}
    dependencies = build_definition.get("resolvedDependencies", []) if isinstance(build_definition, dict) and isinstance(build_definition.get("resolvedDependencies", []), list) else []
    metadata = predicate.get("runDetails", {}).get("metadata", {}) if isinstance(predicate, dict) else {}
    deps = dependency_paths(dependencies)
    missing_expected_deps = sorted(EXPECTED_DEPENDENCY_PATHS - set(deps))

    if statement:
        if statement.get("_type") != STATEMENT_TYPE:
            failures.append({"category": "attestation_statement_type_mismatch", "actual": statement.get("_type")})
        if statement.get("predicateType") != PREDICATE_TYPE:
            failures.append({"category": "attestation_predicate_type_mismatch", "actual": statement.get("predicateType")})
        if len(subject) != 1:
            failures.append({"category": "attestation_subject_count", "count": len(subject)})
        elif subject[0].get("name") != zip_path.name or subject[0].get("digest", {}).get("sha256") != zip_digest:
            failures.append({"category": "attestation_subject_mismatch", "subject": subject[0], "expected_name": zip_path.name, "expected_sha256": zip_digest})
        expected_external = {
            "project": release["project"],
            "revision": release["revision"],
            "timestamp": release["timestamp"],
            "bundle": release["bundle"],
            "slug": release.get("slug", ""),
            "publication_action": receipt.get("publication_action", "none"),
            "publication_authorized": False,
        }
        bad_external = {key: {"expected": value, "actual": external.get(key)} for key, value in expected_external.items() if external.get(key) != value}
        if bad_external:
            failures.append({"category": "attestation_external_parameters_mismatch", "mismatches": bad_external})
        sde = external.get("source_date_epoch", {}) if isinstance(external.get("source_date_epoch", {}), dict) else {}
        expected_epoch = release_date_midnight_epoch(release)
        if sde.get("expected_epoch_utc") != expected_epoch or sde.get("effective_epoch_utc") != expected_epoch:
            failures.append({"category": "attestation_source_date_epoch_mismatch", "expected_epoch_utc": expected_epoch, "actual": sde})
        if metadata.get("zip_sha256") != zip_digest or metadata.get("zip_bytes") != zip_bytes:
            failures.append({"category": "attestation_zip_metadata_mismatch", "expected_sha256": zip_digest, "actual_sha256": metadata.get("zip_sha256"), "expected_bytes": zip_bytes, "actual_bytes": metadata.get("zip_bytes")})
        auth = str(internal.get("package_attestation_authentication", ""))
        if not (auth.startswith("unsigned_sidecar_statement_with_dsse_envelope") or auth.startswith("unsigned_sidecar_statement_with_optional_dsse_envelope")):
            failures.append({"category": "attestation_authentication_scope_missing", "actual": auth})
        if internal.get("package_attestation_signing_public_key") != DEFAULT_PUBLIC_KEY:
            failures.append({"category": "attestation_public_key_path_mismatch", "expected": DEFAULT_PUBLIC_KEY, "actual": internal.get("package_attestation_signing_public_key")})
        if missing_expected_deps:
            failures.append({"category": "attestation_missing_expected_dependencies", "paths": missing_expected_deps})

    signature_summary, signature_failures = check_dsse_envelope(
        envelope_path,
        public_key_path,
        attestation_bytes,
        require_signature,
        expected_public_key_sha256,
        require_public_key_pin=require_public_key_pin,
        allow_unpinned_key=allow_unpinned_key,
    )
    failures.extend(signature_failures)

    zip_summary: dict[str, Any] = {}
    if zip_path.exists():
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                zip_summary, zip_failures = verify_zip_manifest(zf)
                failures.extend(zip_failures)
                failures.extend(dependency_digest_failures(zf, dependencies))
                release_raw = zip_member_bytes(zf, "RELEASE_MANIFEST.json")
                if release_raw is not None:
                    packaged_release = json.loads(release_raw.decode("utf-8"))
                    if packaged_release != release:
                        failures.append({"category": "packaged_release_manifest_differs_from_root"})
                else:
                    failures.append({"category": "packaged_release_manifest_missing"})
                pub_raw = zip_member_bytes(zf, DEFAULT_PUBLIC_KEY)
                if pub_raw is not None and public_key_path.exists() and sha256_bytes(pub_raw) != sha256_file(public_key_path):
                    failures.append({"category": "packaged_public_key_differs_from_verification_key"})
                elif pub_raw is None:
                    failures.append({"category": "packaged_public_key_missing", "path": DEFAULT_PUBLIC_KEY})
        except zipfile.BadZipFile as exc:
            failures.append({"category": "zip_bad_file", "error": str(exc)})
    if internal and zip_summary:
        for key in ("input_file_count", "manifest_file_count"):
            if internal.get(key) != zip_summary.get("zip_member_count"):
                failures.append({"category": "attestation_member_count_mismatch", "field": key, "expected": zip_summary.get("zip_member_count"), "actual": internal.get(key)})

    summary = {
        "checks_failed": len(failures),
        "zip_present": zip_path.exists(),
        "zip_bytes": zip_bytes,
        "zip_sha256": zip_digest,
        "sha256_receipt_present": sha_path.exists(),
        "attestation_present": attestation_path.exists(),
        "attestation_statement_type": statement.get("_type") if isinstance(statement, dict) else "",
        "attestation_predicate_type": statement.get("predicateType") if isinstance(statement, dict) else "",
        "dependency_count": len(dependencies) if isinstance(dependencies, list) else 0,
        "expected_dependency_count": len(EXPECTED_DEPENDENCY_PATHS),
        "missing_expected_dependency_count": len(missing_expected_deps),
        **signature_summary,
        **zip_summary,
    }
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "zip_path": str(zip_path),
        "sha256_receipt_path": str(sha_path),
        "package_attestation_path": str(attestation_path),
        "signature_envelope_path": str(envelope_path),
        "package_attestation_public_key": str(public_key_path),
        "summary": summary,
        "failures": failures[:100],
        "fail_closed_rule": "If the external zip, SHA-256 receipt, package attestation, required DSSE envelope, required public-key fingerprint pin, or packaged MANIFEST.sha256 do not agree, do not distribute the package sidecars as release evidence.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--zip", dest="zip_path", default="")
    parser.add_argument("--sha256", dest="sha_path", default="")
    parser.add_argument("--attestation", dest="attestation_path", default="")
    parser.add_argument("--signature-envelope", dest="envelope_path", default="")
    parser.add_argument("--public-key", dest="public_key_path", default="")
    parser.add_argument("--require-signature", action="store_true")
    parser.add_argument("--expected-public-key-sha256", default="", help="External SHA-256 fingerprint pin for the DSSE public key, with or without a sha256: prefix.")
    parser.add_argument("--require-public-key-pin", action="store_true", help="Fail closed unless --expected-public-key-sha256 is supplied; implied by --require-signature for CLI release-evidence use.")
    parser.add_argument("--allow-unpinned-key", action="store_true", help="Permit inspection-only verification without a trusted public-key pin. Do not use for release evidence.")
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    default_zip, default_sha, default_attestation, default_envelope, default_public_key = default_paths(root)
    zip_path = pathlib.Path(args.zip_path).resolve() if args.zip_path else default_zip
    sha_path = pathlib.Path(args.sha_path).resolve() if args.sha_path else default_sha
    attestation_path = pathlib.Path(args.attestation_path).resolve() if args.attestation_path else default_attestation
    envelope_path = pathlib.Path(args.envelope_path).resolve() if args.envelope_path else default_envelope
    public_key_path = pathlib.Path(args.public_key_path).resolve() if args.public_key_path else default_public_key
    report = check(
        root,
        zip_path,
        sha_path,
        attestation_path,
        envelope_path,
        public_key_path,
        args.require_signature,
        args.expected_public_key_sha256,
        require_public_key_pin=bool(args.require_public_key_pin or args.require_signature),
        allow_unpinned_key=args.allow_unpinned_key,
    )
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = root / args.write_report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
