#!/usr/bin/env python3
"""Validate candidate roots for the streamfold_sumcheck_toy_v2 payload gate.

This verifier makes the rev0856 payload admission contract operational.  It can
verify that the overlay still carries no canonical payload bytes, or check a
future mounted canonical tree/candidate root against exact path, byte, SHA-256,
JSON-parse, and role-count expectations.  It does not copy payloads, grant
rights, or prove streamfold correctness.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REVISION = "rev0857"
DEFAULT_MANIFEST = "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0855/payload_manifest.rev0855.json"
DEFAULT_CONTRACT = "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0857/payload_admission_contract.rev0857.json"


class CandidateVerifyError(Exception):
    pass


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_file(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise CandidateVerifyError(f"cannot hash non-regular file: {path}")
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clean_archive_path(text: Any, field: str) -> str:
    if not isinstance(text, str) or not text:
        raise CandidateVerifyError(f"{field} must be a non-empty string")
    if "\x00" in text or "\\" in text:
        raise CandidateVerifyError(f"{field} must be a POSIX relative path: {text!r}")
    pure = PurePosixPath(text)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise CandidateVerifyError(f"{field} must be clean and relative: {text!r}")
    return pure.as_posix()


def load_json_rel(path_text: str, field: str) -> dict[str, Any]:
    rel = clean_archive_path(path_text, field)
    path = ROOT / rel
    if path.is_symlink() or not path.is_file():
        raise CandidateVerifyError(f"{field} is not a regular file: {rel}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise CandidateVerifyError(f"{field} invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise CandidateVerifyError(f"{field} must contain a JSON object")
    return data


def resolve_candidate_root(text: str | None) -> Path | None:
    if text is None:
        return None
    raw = Path(text).expanduser()
    if raw.is_symlink():
        raise CandidateVerifyError(f"candidate root must be a real directory, not a symlink: {text}")
    candidate = raw.resolve(strict=False)
    if candidate.is_symlink() or not candidate.is_dir():
        raise CandidateVerifyError(f"candidate root must be a real directory, not a symlink: {text}")
    return candidate


def load_index_rows() -> dict[str, dict[str, str]]:
    path = ROOT / "INDEX/files.csv"
    if path.is_symlink() or not path.is_file():
        raise CandidateVerifyError("INDEX/files.csv is missing")
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return {row.get("path", ""): row for row in rows}


def load_contract_and_manifest(manifest_rel: str, contract_rel: str) -> tuple[dict[str, Any], dict[str, Any], str, str]:
    manifest_rel = clean_archive_path(manifest_rel, "manifest path")
    contract_rel = clean_archive_path(contract_rel, "contract path")
    manifest = load_json_rel(manifest_rel, "payload manifest")
    contract = load_json_rel(contract_rel, "payload admission contract")
    manifest_sha = sha256_file(ROOT / manifest_rel)
    contract_sha = sha256_file(ROOT / contract_rel)
    if contract.get("revision") != REVISION:
        raise CandidateVerifyError("payload admission contract revision mismatch")
    if contract.get("source_manifest_path") != manifest_rel:
        raise CandidateVerifyError("contract source manifest path mismatch")
    if contract.get("source_manifest_sha256") != manifest_sha:
        raise CandidateVerifyError("contract source manifest hash mismatch")
    for phrase in ["not a rights grant", "not a streamfold correctness proof", "not a recovered payload bundle"]:
        if phrase.lower() not in "\n".join(str(x) for x in contract.get("non_claims") or []).lower():
            raise CandidateVerifyError(f"contract missing non-claim: {phrase}")
    return manifest, contract, manifest_sha, contract_sha


def selected_payloads(manifest: dict[str, Any], contract: dict[str, Any], mode: str) -> list[dict[str, Any]]:
    payloads = manifest.get("expected_payloads")
    if not isinstance(payloads, list) or not payloads:
        raise CandidateVerifyError("payload manifest expected_payloads must be non-empty")
    if mode == "full":
        selected = payloads
    elif mode == "minimum":
        wanted = set(contract.get("minimum_first_recovery_set") or [])
        if not wanted:
            raise CandidateVerifyError("contract lacks minimum_first_recovery_set")
        selected = [item for item in payloads if isinstance(item, dict) and item.get("path") in wanted]
        missing = sorted(wanted - {item.get("path") for item in selected if isinstance(item, dict)})
        if missing:
            raise CandidateVerifyError("minimum recovery set paths absent from manifest: " + ", ".join(missing))
    else:
        raise CandidateVerifyError(f"unsupported mode: {mode}")
    return selected


def parse_json_candidate(path: Path, rel_path: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise CandidateVerifyError(f"candidate payload is not parseable JSON: {rel_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise CandidateVerifyError(f"candidate payload JSON is not an object: {rel_path}")
    return data


def classify_structure(rel_path: str, data: dict[str, Any]) -> dict[str, Any]:
    """Lightweight structural lint. Exact hash remains the admission authority."""
    result: dict[str, Any] = {"json_object": True}
    if rel_path.endswith(".dsse.json"):
        dsse_keys = {"payload", "payloadType", "signatures"}
        present = sorted(dsse_keys.intersection(data))
        result.update({
            "expected_family": "dsse_like_envelope_or_project_curated_attestation",
            "dsse_standard_keys_present": present,
            "strict_dsse_envelope": all(key in data for key in dsse_keys) and isinstance(data.get("signatures"), list),
            "strict_dsse_note": "exact SHA-256 is authoritative; strict DSSE shape is reported but not required because project-curated SCITT/DSSE wrappers may vary",
        })
    elif "/abi_ir/" in rel_path:
        result.update({
            "expected_family": "streamfold_abi_or_protocol_ir_json",
            "top_level_key_count": len(data),
        })
    return result


def verify_payloads(candidate_root: Path | None, manifest: dict[str, Any], contract: dict[str, Any], *, mode: str) -> dict[str, Any]:
    selected = selected_payloads(manifest, contract, mode)
    index = load_index_rows()
    seen: set[str] = set()
    role_counts: dict[str, int] = {}
    total_bytes = 0
    overlay_absent = 0
    candidate_present = 0
    structural_reports: list[dict[str, Any]] = []
    mismatches: list[str] = []
    for idx, item in enumerate(selected):
        if not isinstance(item, dict):
            raise CandidateVerifyError(f"payload item {idx} must be an object")
        rel_path = clean_archive_path(item.get("path"), f"payload[{idx}].path")
        if rel_path in seen:
            raise CandidateVerifyError(f"duplicate payload path: {rel_path}")
        seen.add(rel_path)
        expected_sha = str(item.get("sha256") or "")
        try:
            expected_bytes = int(item.get("bytes"))
        except Exception as exc:
            raise CandidateVerifyError(f"payload bytes is invalid for {rel_path}") from exc
        row = index.get(rel_path)
        if row is None:
            raise CandidateVerifyError(f"payload path absent from INDEX/files.csv: {rel_path}")
        if row.get("sha256") != expected_sha or int(row.get("size") or 0) != expected_bytes:
            raise CandidateVerifyError(f"INDEX/files.csv mismatch for {rel_path}")
        role = str(item.get("role") or "unknown")
        role_counts[role] = role_counts.get(role, 0) + 1
        total_bytes += expected_bytes
        if (ROOT / rel_path).exists():
            raise CandidateVerifyError(f"payload unexpectedly present inside overlay bundle: {rel_path}")
        overlay_absent += 1
        if candidate_root is not None:
            candidate_path = candidate_root / rel_path
            try:
                resolved = candidate_path.resolve(strict=False)
                resolved.relative_to(candidate_root)
            except Exception as exc:
                raise CandidateVerifyError(f"candidate path escapes root: {rel_path}") from exc
            if candidate_path.is_symlink() or not candidate_path.is_file():
                mismatches.append(f"missing:{rel_path}")
                continue
            candidate_present += 1
            size = candidate_path.stat().st_size
            digest = sha256_file(candidate_path)
            if size != expected_bytes or digest != expected_sha:
                mismatches.append(f"hash-or-size:{rel_path}")
                continue
            if rel_path.endswith(".json"):
                data = parse_json_candidate(candidate_path, rel_path)
                structural_reports.append({"path": rel_path, **classify_structure(rel_path, data)})
    required_roles = list(contract.get("required_roles") or [])
    for role in required_roles:
        if role not in role_counts:
            raise CandidateVerifyError(f"selected payload set lacks required role: {role}")
    if candidate_root is not None and mismatches:
        shown = ", ".join(mismatches[:10])
        suffix = "" if len(mismatches) <= 10 else f"; +{len(mismatches) - 10} more"
        raise CandidateVerifyError(f"candidate root does not satisfy {mode} payload gate: {shown}{suffix}")
    return {
        "ok": True,
        "revision": REVISION,
        "source_group_id": manifest.get("source_group_id"),
        "mode": mode,
        "selected_path_count": len(selected),
        "selected_total_bytes": total_bytes,
        "role_counts": dict(sorted(role_counts.items())),
        "overlay_payloads_absent": overlay_absent,
        "candidate_root_checked": candidate_root is not None,
        "candidate_payloads_present": candidate_present,
        "candidate_admission_status": "candidate_payloads_admitted_by_exact_hash" if candidate_root is not None else "blocked_waiting_for_candidate_root",
        "structural_reports": structural_reports,
        "non_claims": [
            "not a rights grant",
            "not a proof of streamfold protocol correctness",
            "not a payload copy operation",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify streamfold_sumcheck_toy_v2 payload candidates by exact manifest identity")
    parser.add_argument("--candidate-root", help="optional canonical/candidate tree root containing expected payload paths")
    parser.add_argument("--mode", choices=["full", "minimum"], default="full", help="check all 17 paths or only the minimum first recovery set")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST, help="payload manifest path relative to repository root")
    parser.add_argument("--contract", default=DEFAULT_CONTRACT, help="admission contract path relative to repository root")
    parser.add_argument("--emit-report", help="write verification report JSON to a path")
    parser.add_argument("--expect-fail", action="store_true", help="succeed only if verification fails")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)
    try:
        candidate_root = resolve_candidate_root(args.candidate_root)
        manifest, contract, manifest_sha, contract_sha = load_contract_and_manifest(args.manifest, args.contract)
        result = verify_payloads(candidate_root, manifest, contract, mode=args.mode)
        result["payload_manifest_sha256"] = manifest_sha
        result["payload_admission_contract_sha256"] = contract_sha
        if args.emit_report:
            report_path = Path(args.emit_report)
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except Exception as exc:
        if args.expect_fail:
            payload = {"ok": True, "expected_failure_observed": True, "failure": str(exc), "mode": args.mode}
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print("streamfold-payload-candidate-rev0857: expected failure observed")
            return 0
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc), "mode": args.mode}, indent=2, sort_keys=True))
        else:
            print(f"streamfold-payload-candidate-rev0857: FAIL: {exc}", file=sys.stderr)
        return 1
    if args.expect_fail:
        message = "candidate unexpectedly verified successfully"
        if args.json:
            print(json.dumps({"ok": False, "error": message, "mode": args.mode}, indent=2, sort_keys=True))
        else:
            print(f"streamfold-payload-candidate-rev0857: FAIL: {message}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("streamfold-payload-candidate-rev0857: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
