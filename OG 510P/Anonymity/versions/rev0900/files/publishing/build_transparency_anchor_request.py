#!/usr/bin/env python3
"""Build a post-package transparency-anchor request packet.

This helper does not submit anything to an external log and does not claim log
inclusion.  It creates the small sidecar a later operator would hand to an
outside transparency service after the zip, checksum receipt, signed DSSE
package attestation, and optional artifact-set verification report exist.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import pathlib
import sys
from typing import Any

DSSE_PAYLOAD_TYPE = "application/vnd.in-toto+json"
STATEMENT_TYPE = "https://in-toto.io/Statement/v1"
SLSA_PREDICATE_TYPE = "https://slsa.dev/provenance/v1"


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_entry(path: pathlib.Path) -> dict[str, Any]:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def default_paths(root: pathlib.Path) -> dict[str, pathlib.Path]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    zip_path = (root.parent / release["bundle"]).resolve()
    return {
        "zip": zip_path,
        "sha256": zip_path.with_suffix(zip_path.suffix + ".sha256"),
        "attestation": zip_path.with_suffix(zip_path.suffix + ".package.intoto.jsonl"),
        "dsse": zip_path.with_suffix(zip_path.suffix + ".package.dsse.json"),
        "public_key": zip_path.with_suffix(zip_path.suffix + ".package.dsse.pub.pem"),
        "artifact_verify": zip_path.with_suffix(zip_path.suffix + ".artifactset.verify.json"),
        "out": zip_path.with_suffix(zip_path.suffix + ".transparency.request.json"),
    }


def read_sha_receipt(path: pathlib.Path, zip_name: str) -> tuple[str, list[dict[str, Any]]]:
    failures: list[dict[str, Any]] = []
    text = path.read_text(encoding="utf-8").strip()
    parts = text.split()
    if len(parts) != 2:
        failures.append({"category": "sha256_receipt_malformed", "path": str(path)})
        return "", failures
    digest, name = parts
    if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
        failures.append({"category": "sha256_receipt_digest_malformed", "path": str(path), "digest": digest})
    if name != zip_name:
        failures.append({"category": "sha256_receipt_name_mismatch", "expected": zip_name, "actual": name})
    return digest, failures


def decode_dsse_payload(envelope_path: pathlib.Path) -> tuple[dict[str, Any], bytes, list[dict[str, Any]]]:
    failures: list[dict[str, Any]] = []
    envelope = load_json(envelope_path)
    if envelope.get("payloadType") != DSSE_PAYLOAD_TYPE:
        failures.append({"category": "dsse_payload_type_mismatch", "expected": DSSE_PAYLOAD_TYPE, "actual": envelope.get("payloadType")})
    signatures = envelope.get("signatures")
    if not isinstance(signatures, list) or not signatures:
        failures.append({"category": "dsse_signature_missing"})
    payload_b64 = envelope.get("payload")
    if not isinstance(payload_b64, str):
        failures.append({"category": "dsse_payload_missing"})
        return envelope, b"", failures
    try:
        payload = base64.b64decode(payload_b64.encode("ascii"), validate=True)
    except Exception as exc:  # noqa: BLE001 - user-facing report
        failures.append({"category": "dsse_payload_base64_invalid", "error": str(exc)})
        payload = b""
    return envelope, payload, failures


def package_subject_zip_digest(statement: dict[str, Any]) -> str:
    subject = statement.get("subject", [])
    if not isinstance(subject, list):
        return ""
    for row in subject:
        if isinstance(row, dict):
            digest = row.get("digest", {})
            if isinstance(digest, dict) and "sha256" in digest:
                return str(digest.get("sha256"))
    return ""


def build_request(
    root: pathlib.Path,
    zip_path: pathlib.Path,
    sha_path: pathlib.Path,
    attestation_path: pathlib.Path,
    dsse_path: pathlib.Path,
    public_key_path: pathlib.Path,
    artifact_verify_path: pathlib.Path | None,
) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    failures: list[dict[str, Any]] = []
    required_paths = {
        "zip": zip_path,
        "sha256_receipt": sha_path,
        "package_attestation": attestation_path,
        "package_dsse_envelope": dsse_path,
        "package_dsse_public_key": public_key_path,
    }
    for label, path in required_paths.items():
        if not path.exists():
            failures.append({"category": "required_artifact_missing", "label": label, "path": str(path)})

    if failures:
        return {
            "status": "fail",
            "request_kind": "external-transparency-anchor-request-v1",
            "generated_for_revision": release.get("revision", ""),
            "checked_bundle": release.get("bundle", ""),
            "publication_authorized": False,
            "failures": failures,
        }

    zip_digest = sha256_file(zip_path)
    receipt_digest, receipt_failures = read_sha_receipt(sha_path, zip_path.name)
    failures.extend(receipt_failures)
    if receipt_digest and receipt_digest != zip_digest:
        failures.append({"category": "zip_sha256_receipt_mismatch", "receipt": receipt_digest, "actual": zip_digest})

    envelope, dsse_payload, dsse_failures = decode_dsse_payload(dsse_path)
    failures.extend(dsse_failures)
    attestation_bytes = attestation_path.read_bytes()
    if dsse_payload and dsse_payload != attestation_bytes:
        failures.append({"category": "dsse_payload_not_exact_attestation_bytes"})
    try:
        statement = json.loads(attestation_bytes.decode("utf-8"))
    except Exception as exc:  # noqa: BLE001 - user-facing report
        failures.append({"category": "package_attestation_json_invalid", "error": str(exc)})
        statement = {}
    if statement.get("_type") != STATEMENT_TYPE:
        failures.append({"category": "package_attestation_statement_type_mismatch", "expected": STATEMENT_TYPE, "actual": statement.get("_type")})
    if statement.get("predicateType") != SLSA_PREDICATE_TYPE:
        failures.append({"category": "package_attestation_predicate_type_mismatch", "expected": SLSA_PREDICATE_TYPE, "actual": statement.get("predicateType")})
    subject_digest = package_subject_zip_digest(statement)
    if subject_digest != zip_digest:
        failures.append({"category": "package_attestation_subject_digest_mismatch", "expected": zip_digest, "actual": subject_digest})

    artifact_verify_entry: dict[str, Any] | None = None
    artifact_verify_status = "not_provided"
    if artifact_verify_path and artifact_verify_path.exists():
        artifact_verify_entry = file_entry(artifact_verify_path)
        try:
            artifact_verify = load_json(artifact_verify_path)
            artifact_verify_status = str(artifact_verify.get("status", "unknown"))
            if artifact_verify_status != "pass":
                failures.append({"category": "artifactset_verify_report_not_pass", "status": artifact_verify_status})
        except Exception as exc:  # noqa: BLE001 - user-facing report
            artifact_verify_status = "unreadable"
            failures.append({"category": "artifactset_verify_report_unreadable", "error": str(exc)})

    artifacts: dict[str, Any] = {label: file_entry(path) for label, path in required_paths.items()}
    if artifact_verify_entry is not None:
        artifacts["artifactset_verify_report"] = artifact_verify_entry

    pubkey_digest = artifacts["package_dsse_public_key"]["sha256"]
    signatures = envelope.get("signatures", []) if isinstance(envelope, dict) else []
    keyids = [str(sig.get("keyid", "")) for sig in signatures if isinstance(sig, dict)]

    return {
        "status": "pass" if not failures else "fail",
        "request_kind": "external-transparency-anchor-request-v1",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "external_anchor_status": "not_submitted",
        "inclusion_claim": False,
        "submission_is_authorization": False,
        "evidence_status": "request_packet_only_no_external_log_inclusion_proof",
        "artifacts": artifacts,
        "submission_materials": {
            "zip_sha256": zip_digest,
            "sha256_receipt_sha256": artifacts["sha256_receipt"]["sha256"],
            "package_attestation_sha256": artifacts["package_attestation"]["sha256"],
            "package_dsse_envelope_sha256": artifacts["package_dsse_envelope"]["sha256"],
            "package_dsse_public_key_sha256": pubkey_digest,
            "artifactset_verify_report_sha256": artifacts.get("artifactset_verify_report", {}).get("sha256", ""),
            "dsse_keyids": keyids,
        },
        "anchor_target_class": {
            "class": "third_party_append_only_transparency_log",
            "sigstore_rekor_compatible_fields_after_submission": [
                "log_id",
                "log_index",
                "integrated_time",
                "signed_entry_timestamp",
                "inclusion_proof",
                "canonicalized_entry_hash",
            ],
            "slsa_distribution_use": "publish an attestation digest or pointer outside the repository/package registry so verifiers can discover the signed provenance for the zip digest",
        },
        "artifactset_verify_status": artifact_verify_status,
        "failures": failures[:50],
        "fail_closed_rule": "This packet is not an external anchor. Treat the package as locally signed only until an outside log returns a verifiable inclusion proof for the signed attestation/zip digest and that proof is stored next to this request.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--zip", default="")
    parser.add_argument("--sha256", default="")
    parser.add_argument("--attestation", default="")
    parser.add_argument("--signature-envelope", default="")
    parser.add_argument("--public-key", default="")
    parser.add_argument("--artifactset-verify", default="")
    parser.add_argument("--write", default="")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    defaults = default_paths(root)
    zip_path = pathlib.Path(args.zip).resolve() if args.zip else defaults["zip"]
    sha_path = pathlib.Path(args.sha256).resolve() if args.sha256 else defaults["sha256"]
    attestation_path = pathlib.Path(args.attestation).resolve() if args.attestation else defaults["attestation"]
    dsse_path = pathlib.Path(args.signature_envelope).resolve() if args.signature_envelope else defaults["dsse"]
    public_key_path = pathlib.Path(args.public_key).resolve() if args.public_key else defaults["public_key"]
    artifact_verify_path = pathlib.Path(args.artifactset_verify).resolve() if args.artifactset_verify else defaults["artifact_verify"]
    out_path = pathlib.Path(args.write).resolve() if args.write else defaults["out"]
    report = build_request(root, zip_path, sha_path, attestation_path, dsse_path, public_key_path, artifact_verify_path)
    text = json.dumps(report, indent=2) + "\n"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
