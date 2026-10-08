#!/usr/bin/env python3
"""Verify EvidenceVault rev0853 transparent PCD envelopes.

This is not a SNARK verifier.  It is the first executable proof-carrying-data
contract for the overlay: a claim, public inputs, certificate envelope, verifier,
and accept/reject fixtures that bind local integrity and rights-block facts.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REV_RE = re.compile(r"rev(\d{4})")
PATCH_RE = re.compile(r"^rev(?P<from>\d{4})-to-rev(?P<to>\d{4})-overlay\.patch$")

class PcdVerifyError(Exception):
    pass


def sha256_file(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise PcdVerifyError(f"cannot hash non-regular file: {rel(path)}")
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def clean_archive_path(text: Any, field: str) -> str:
    if not isinstance(text, str) or not text:
        raise PcdVerifyError(f"{field} must be a non-empty string")
    if "\x00" in text or "\\" in text:
        raise PcdVerifyError(f"{field} must be POSIX relative: {text!r}")
    pure = PurePosixPath(text)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise PcdVerifyError(f"{field} must be clean and relative: {text!r}")
    return pure.as_posix()


def load_json_rel(path_text: str, field: str) -> dict[str, Any]:
    rel_path = clean_archive_path(path_text, field)
    path = ROOT / rel_path
    if path.is_symlink() or not path.is_file():
        raise PcdVerifyError(f"{field} is not a regular file: {rel_path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise PcdVerifyError(f"{field} is invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise PcdVerifyError(f"{field} must contain a JSON object")
    return data


def apply_mutation(obj: Any, pointer: str, value: Any) -> None:
    if not pointer.startswith("/"):
        raise PcdVerifyError(f"mutation path must be a JSON pointer: {pointer!r}")
    parts = [p.replace("~1", "/").replace("~0", "~") for p in pointer.strip("/").split("/")]
    current = obj
    for part in parts[:-1]:
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
        else:
            raise PcdVerifyError(f"mutation path does not exist: {pointer}")
    last = parts[-1]
    if isinstance(current, dict) and last in current:
        current[last] = value
    elif isinstance(current, list) and last.isdigit() and int(last) < len(current):
        current[int(last)] = value
    else:
        raise PcdVerifyError(f"mutation target does not exist: {pointer}")


def all_regular_file_paths() -> set[str]:
    paths: set[str] = set()
    symlinks: list[str] = []
    for path in ROOT.rglob("*"):
        if path.is_symlink():
            symlinks.append(rel(path))
        elif path.is_file():
            paths.add(rel(path))
    if symlinks:
        raise PcdVerifyError("extracted overlay contains symlinks: " + ", ".join(sorted(symlinks)[:10]))
    return paths


def verify_manifest(public_inputs: dict[str, Any]) -> None:
    spec = public_inputs.get("overlay_manifest")
    if not isinstance(spec, dict):
        raise PcdVerifyError("public inputs missing overlay_manifest")
    manifest_path = clean_archive_path(spec.get("path"), "overlay_manifest.path")
    sidecar_path = clean_archive_path(spec.get("sidecar_path"), "overlay_manifest.sidecar_path")
    manifest = load_json_rel(manifest_path, "overlay manifest")
    entries = manifest.get("files")
    if not isinstance(entries, list):
        raise PcdVerifyError("overlay manifest files must be a list")
    if manifest.get("file_count") != len(entries):
        raise PcdVerifyError("overlay manifest file_count mismatch")
    sidecar = (ROOT / sidecar_path).read_text(encoding="utf-8").strip()
    expected_sidecar = f"{sha256_file(ROOT / manifest_path)}  {manifest_path}"
    if sidecar != expected_sidecar:
        raise PcdVerifyError("overlay manifest sidecar mismatch")
    manifest_paths: set[str] = set()
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise PcdVerifyError(f"overlay manifest entry {idx} not an object")
        path_text = clean_archive_path(entry.get("path"), f"overlay manifest files[{idx}].path")
        if path_text in manifest_paths:
            raise PcdVerifyError(f"duplicate overlay manifest path: {path_text}")
        path = ROOT / path_text
        if path.is_symlink() or not path.is_file():
            raise PcdVerifyError(f"manifest path not regular file: {path_text}")
        if entry.get("bytes") != path.stat().st_size or entry.get("sha256") != sha256_file(path):
            raise PcdVerifyError(f"manifest digest/size mismatch for {path_text}")
        manifest_paths.add(path_text)
    excluded = set(spec.get("excluded_from_manifest") or [])
    actual = all_regular_file_paths() - excluded
    if manifest_paths != actual:
        missing = sorted(actual - manifest_paths)[:10]
        extra = sorted(manifest_paths - actual)[:10]
        raise PcdVerifyError(f"manifest file set mismatch; missing={missing} extra={extra}")


def verify_patch_chain(public_inputs: dict[str, Any]) -> None:
    expected = public_inputs.get("expected_patch_chain")
    if not isinstance(expected, dict):
        raise PcdVerifyError("missing expected_patch_chain")
    start = expected.get("start_revision")
    end = expected.get("end_revision")
    if not (isinstance(start, str) and isinstance(end, str)):
        raise PcdVerifyError("patch-chain revisions must be strings")
    start_n = int(start.replace("rev", ""))
    end_n = int(end.replace("rev", ""))
    edges: list[tuple[int, int, str]] = []
    for patch in (ROOT / "PATCHES").glob("*.patch"):
        m = PATCH_RE.match(patch.name)
        if m:
            edges.append((int(m.group("from")), int(m.group("to")), patch.name))
    edges.sort()
    if not edges:
        raise PcdVerifyError("no overlay patches found")
    if edges[0][0] != start_n:
        raise PcdVerifyError(f"patch chain starts at rev{edges[0][0]:04d}, expected {start}")
    for a, b in zip(edges, edges[1:]):
        if a[1] != b[0] or a[1] != a[0] + 1:
            raise PcdVerifyError(f"patch chain gap around {a[2]} / {b[2]}")
    if edges[-1][1] != end_n:
        raise PcdVerifyError(f"patch chain ends at rev{edges[-1][1]:04d}, expected {end}")
    minimum = expected.get("minimum_overlay_patch_count")
    if isinstance(minimum, int) and len(edges) < minimum:
        raise PcdVerifyError(f"patch chain too short: {len(edges)} < {minimum}")


def verify_required_files(public_inputs: dict[str, Any]) -> None:
    for idx, item in enumerate(public_inputs.get("required_files") or []):
        path_text = clean_archive_path(item, f"required_files[{idx}]")
        path = ROOT / path_text
        if path.is_symlink() or not path.is_file():
            raise PcdVerifyError(f"required file missing or not regular: {path_text}")


def verify_rights(public_inputs: dict[str, Any]) -> None:
    exp = public_inputs.get("rights_expectation")
    if not isinstance(exp, dict):
        raise PcdVerifyError("missing rights_expectation")
    ledger_path = clean_archive_path(exp.get("ledger_path"), "rights_expectation.ledger_path")
    ledger = load_json_rel(ledger_path, "rights ledger")
    if ledger.get("status") != exp.get("status"):
        raise PcdVerifyError(f"rights status mismatch: {ledger.get('status')} != {exp.get('status')}")
    if ledger.get("root_license_or_notice_file_present") is not exp.get("root_license_or_notice_file_present"):
        raise PcdVerifyError("root license/notice ledger expectation mismatch")
    for sentinel in exp.get("forbidden_root_sentinels") or []:
        path_text = clean_archive_path(sentinel, "forbidden root sentinel")
        if (ROOT / path_text).exists():
            raise PcdVerifyError(f"forbidden root rights sentinel exists: {path_text}")


def verify_index_and_map(public_inputs: dict[str, Any]) -> None:
    idx_exp = public_inputs.get("canonical_index_expectation")
    map_exp = public_inputs.get("path_role_map_expectation")
    if not isinstance(idx_exp, dict) or not isinstance(map_exp, dict):
        raise PcdVerifyError("missing index/map expectations")
    index_path = clean_archive_path(idx_exp.get("index_path"), "canonical_index_expectation.index_path")
    with (ROOT / index_path).open(newline="", encoding="utf-8") as f:
        index_rows = list(csv.DictReader(f))
    if len(index_rows) < int(idx_exp.get("minimum_rows", 0)):
        raise PcdVerifyError("canonical index row count below expectation")
    path_set = {row.get("path") for row in index_rows}
    missing_sentinels = sorted(set(idx_exp.get("required_sentinel_paths") or []) - path_set)
    if missing_sentinels:
        raise PcdVerifyError("canonical index missing sentinel proof paths: " + ", ".join(missing_sentinels))
    map_path = clean_archive_path(map_exp.get("path"), "path_role_map_expectation.path")
    if map_exp.get("map_sha256") != sha256_file(ROOT / map_path):
        raise PcdVerifyError("path role map SHA-256 mismatch")
    with (ROOT / map_path).open(newline="", encoding="utf-8") as f:
        map_rows = list(csv.DictReader(f))
    if len(map_rows) != map_exp.get("expected_rows"):
        raise PcdVerifyError(f"path role map row count mismatch: {len(map_rows)} != {map_exp.get('expected_rows')}")
    if len(map_rows) < int(idx_exp.get("minimum_proof_signal_paths", 0)):
        raise PcdVerifyError("path role map below proof-signal threshold")
    roles = {row.get("role") for row in map_rows}
    for role in map_exp.get("expected_roles_present") or []:
        if role not in roles:
            raise PcdVerifyError(f"expected role absent from map: {role}")
    absent_payloads = [row for row in map_rows if row.get("present_in_overlay") != "false"]
    if absent_payloads:
        raise PcdVerifyError("map assumption changed: canonical proof payloads appear in overlay")


def verify_certificate(certificate: dict[str, Any], claim: dict[str, Any], public_inputs: dict[str, Any]) -> None:
    if certificate.get("certificate_type") != "transparent_public_pcd_envelope":
        raise PcdVerifyError("unsupported certificate type")
    proof_system = certificate.get("proof_system")
    if not isinstance(proof_system, dict):
        raise PcdVerifyError("missing proof_system")
    if proof_system.get("snark") or proof_system.get("zero_knowledge") or proof_system.get("succinct"):
        raise PcdVerifyError("transparent lane cannot claim SNARK/ZK/succinct properties")
    for label, obj, loaded in [
        ("claim", certificate.get("claim"), claim),
        ("public_inputs", certificate.get("public_inputs"), public_inputs),
    ]:
        if not isinstance(obj, dict):
            raise PcdVerifyError(f"certificate missing {label}")
        path_text = clean_archive_path(obj.get("path"), f"certificate.{label}.path")
        digest = obj.get("sha256")
        if digest != sha256_file(ROOT / path_text):
            raise PcdVerifyError(f"certificate {label} hash mismatch")
    verifier = certificate.get("verifier")
    if not isinstance(verifier, dict):
        raise PcdVerifyError("certificate missing verifier")
    verifier_path = clean_archive_path(verifier.get("path"), "certificate.verifier.path")
    if verifier.get("sha256") != sha256_file(ROOT / verifier_path):
        raise PcdVerifyError("certificate verifier hash mismatch")
    if claim.get("revision") != public_inputs.get("revision") or claim.get("revision") != "rev0853":
        raise PcdVerifyError("claim/public input revision mismatch")
    non_claim_items = list(claim.get("non_claims") or []) + list(public_inputs.get("non_claims") or [])
    non_claims = "\n".join(str(item) for item in non_claim_items)
    for phrase in ["not a zk-SNARK", "zero knowledge", "publication rights"]:
        if phrase.lower() not in non_claims.lower():
            raise PcdVerifyError(f"required non-claim phrase missing: {phrase}")


def verify_fixture(fixture_path: Path) -> dict[str, Any]:
    fixture = load_json_rel(rel(fixture_path), "fixture")
    claim = load_json_rel(fixture.get("claim_path"), "fixture.claim_path")
    public_inputs = load_json_rel(fixture.get("public_inputs_path"), "fixture.public_inputs_path")
    certificate = load_json_rel(fixture.get("certificate_path"), "fixture.certificate_path")
    # Apply controlled mutations after loading and before checks.
    for mutation in fixture.get("mutations") or []:
        if not isinstance(mutation, dict) or mutation.get("target") != "public_inputs":
            raise PcdVerifyError("only public_inputs fixture mutations are supported")
        if mutation.get("op") != "replace":
            raise PcdVerifyError("only replace mutations are supported")
        apply_mutation(public_inputs, mutation.get("path"), mutation.get("value"))
    verify_certificate(certificate, claim, public_inputs)
    verify_required_files(public_inputs)
    verify_patch_chain(public_inputs)
    verify_manifest(public_inputs)
    verify_rights(public_inputs)
    verify_index_and_map(public_inputs)
    return {"ok": True, "fixture_id": fixture.get("fixture_id"), "claim_id": claim.get("claim_id")}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify EvidenceVault rev0853 transparent PCD envelope")
    parser.add_argument("--fixture", required=True, help="fixture JSON path relative to repository root")
    parser.add_argument("--expect-fail", action="store_true", help="succeed only if verification fails")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)
    fixture_rel = clean_archive_path(args.fixture, "--fixture")
    try:
        result = verify_fixture(ROOT / fixture_rel)
    except Exception as exc:
        if args.expect_fail:
            payload = {"ok": True, "expected_failure_observed": True, "fixture": fixture_rel, "failure": str(exc)}
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print("pcd-envelope-rev0853: expected failure observed")
            return 0
        payload = {"ok": False, "fixture": fixture_rel, "error": str(exc)}
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"pcd-envelope-rev0853: FAIL: {exc}", file=sys.stderr)
        return 1
    if args.expect_fail:
        msg = "fixture unexpectedly verified successfully"
        if args.json:
            print(json.dumps({"ok": False, "fixture": fixture_rel, "error": msg}, indent=2, sort_keys=True))
        else:
            print(f"pcd-envelope-rev0853: FAIL: {msg}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("pcd-envelope-rev0853: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
