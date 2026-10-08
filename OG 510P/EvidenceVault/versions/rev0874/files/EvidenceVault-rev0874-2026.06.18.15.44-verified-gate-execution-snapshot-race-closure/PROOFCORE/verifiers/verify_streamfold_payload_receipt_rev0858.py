#!/usr/bin/env python3
"""Verify rev0858 transparent payload-admission receipts.

A receipt records the deterministic output of the rev0857 streamfold payload
candidate verifier for the current overlay absence state.  This verifier
recomputes the source report and checks that the receipt is an honest, portable
record of that check.  It does not admit payload bytes, copy payloads, grant
rights, or prove streamfold correctness.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REVISION = "rev0858"


class ReceiptVerifyError(Exception):
    pass


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj)).hexdigest()


def sha256_file(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise ReceiptVerifyError(f"cannot hash non-regular file: {path}")
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clean_archive_path(text: Any, field: str) -> str:
    if not isinstance(text, str) or not text:
        raise ReceiptVerifyError(f"{field} must be a non-empty string")
    if "\x00" in text or "\\" in text:
        raise ReceiptVerifyError(f"{field} must be a POSIX relative path: {text!r}")
    pure = PurePosixPath(text)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise ReceiptVerifyError(f"{field} must be clean and relative: {text!r}")
    return pure.as_posix()


def load_json_rel(path_text: str, field: str) -> dict[str, Any]:
    rel = clean_archive_path(path_text, field)
    path = ROOT / rel
    if path.is_symlink() or not path.is_file():
        raise ReceiptVerifyError(f"{field} is not a regular file: {rel}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ReceiptVerifyError(f"{field} invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ReceiptVerifyError(f"{field} must contain a JSON object")
    return data


def check_ref(obj: dict[str, Any], key: str) -> tuple[str, str]:
    ref = obj.get(key)
    if not isinstance(ref, dict):
        raise ReceiptVerifyError(f"missing reference: {key}")
    rel = clean_archive_path(ref.get("path"), f"{key}.path")
    observed = sha256_file(ROOT / rel)
    if ref.get("sha256") != observed:
        raise ReceiptVerifyError(f"{key} hash mismatch")
    return rel, observed


def run_source_verifier(verifier_rel: str, mode: str) -> dict[str, Any]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [sys.executable, verifier_rel, "--mode", mode, "--json"],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise ReceiptVerifyError(f"source verifier failed: stdout={result.stdout!r} stderr={result.stderr!r}")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ReceiptVerifyError(f"source verifier did not emit JSON: {exc}: {result.stdout!r}") from exc
    if not isinstance(payload, dict) or payload.get("ok") is not True:
        raise ReceiptVerifyError(f"source verifier emitted unexpected payload: {payload}")
    return payload


def verify_rights_blocked() -> None:
    rights = load_json_rel("RIGHTS/component_license_ledger.json", "rights ledger")
    if rights.get("status") != "publication_blocked_pending_rights_decision":
        raise ReceiptVerifyError("rights status drifted")
    for sentinel in ["LICENSE", "COPYING", "NOTICE"]:
        if (ROOT / sentinel).exists():
            raise ReceiptVerifyError(f"root rights sentinel was invented: {sentinel}")


def check_non_claims(items: Any, field: str) -> None:
    text = "\n".join(str(item) for item in (items or []))
    for phrase in ["not a rights grant", "not a recovered payload bundle", "not a streamfold correctness proof"]:
        if phrase.lower() not in text.lower():
            raise ReceiptVerifyError(f"{field} missing non-claim: {phrase}")


def verify_receipt(receipt_rel: str) -> dict[str, Any]:
    receipt = load_json_rel(receipt_rel, "receipt")
    if receipt.get("revision") != REVISION:
        raise ReceiptVerifyError("receipt revision mismatch")
    if receipt.get("receipt_type") != "streamfold_payload_candidate_absence_receipt":
        raise ReceiptVerifyError("unsupported receipt type")
    mode = receipt.get("mode")
    if mode not in {"full", "minimum"}:
        raise ReceiptVerifyError("receipt mode must be full or minimum")
    check_non_claims(receipt.get("non_claims"), "receipt")
    verifier_rel, verifier_sha = check_ref(receipt, "source_verifier")
    manifest_rel, manifest_sha = check_ref(receipt, "payload_manifest")
    source_contract_rel, source_contract_sha = check_ref(receipt, "source_payload_admission_contract")
    receipt_contract_rel, receipt_contract_sha = check_ref(receipt, "payload_receipt_contract")
    contract = load_json_rel(receipt_contract_rel, "payload receipt contract")
    if contract.get("revision") != REVISION:
        raise ReceiptVerifyError("receipt contract revision mismatch")
    if contract.get("source_payload_admission_contract_sha256") != source_contract_sha:
        raise ReceiptVerifyError("receipt contract does not bind source admission contract")
    if contract.get("payload_manifest_sha256") != manifest_sha:
        raise ReceiptVerifyError("receipt contract does not bind payload manifest")
    check_non_claims(contract.get("non_claims"), "payload receipt contract")
    embedded = receipt.get("source_report")
    if not isinstance(embedded, dict):
        raise ReceiptVerifyError("receipt source_report must be an object")
    if receipt.get("source_report_sha256") != sha256_obj(embedded):
        raise ReceiptVerifyError("receipt source_report hash mismatch")
    recomputed = run_source_verifier(verifier_rel, mode)
    if embedded != recomputed:
        raise ReceiptVerifyError("embedded source_report does not match recomputed source verifier output")
    expected_counts = {"full": 17, "minimum": 4}
    if embedded.get("selected_path_count") != expected_counts[mode]:
        raise ReceiptVerifyError("selected path count drifted")
    if embedded.get("overlay_payloads_absent") != expected_counts[mode]:
        raise ReceiptVerifyError("overlay absence count drifted")
    if embedded.get("candidate_admission_status") != "blocked_waiting_for_candidate_root":
        raise ReceiptVerifyError("absence receipt must remain blocked waiting for candidate root")
    if embedded.get("candidate_root_checked") is not False or embedded.get("candidate_payloads_present") != 0:
        raise ReceiptVerifyError("absence receipt unexpectedly records candidate-root payloads")
    verify_rights_blocked()
    return {
        "ok": True,
        "revision": REVISION,
        "receipt": receipt_rel,
        "mode": mode,
        "source_verifier_sha256": verifier_sha,
        "payload_manifest_sha256": manifest_sha,
        "source_payload_admission_contract_sha256": source_contract_sha,
        "payload_receipt_contract_sha256": receipt_contract_sha,
        "overlay_manifest_policy": "not_bound_to_avoid_self_referential_manifest_cycle",
        "selected_path_count": embedded.get("selected_path_count"),
        "overlay_payloads_absent": embedded.get("overlay_payloads_absent"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify rev0858 streamfold payload absence/admission receipts")
    parser.add_argument("--receipt", required=True, help="receipt JSON path relative to repository root")
    parser.add_argument("--expect-fail", action="store_true", help="succeed only if verification fails")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)
    receipt_rel = clean_archive_path(args.receipt, "--receipt")
    try:
        result = verify_receipt(receipt_rel)
    except Exception as exc:
        if args.expect_fail:
            payload = {"ok": True, "expected_failure_observed": True, "receipt": receipt_rel, "failure": str(exc)}
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print("streamfold-payload-receipt-rev0858: expected failure observed")
            return 0
        if args.json:
            print(json.dumps({"ok": False, "receipt": receipt_rel, "error": str(exc)}, indent=2, sort_keys=True))
        else:
            print(f"streamfold-payload-receipt-rev0858: FAIL: {exc}", file=sys.stderr)
        return 1
    if args.expect_fail:
        message = "receipt unexpectedly verified successfully"
        if args.json:
            print(json.dumps({"ok": False, "receipt": receipt_rel, "error": message}, indent=2, sort_keys=True))
        else:
            print(f"streamfold-payload-receipt-rev0858: FAIL: {message}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("streamfold-payload-receipt-rev0858: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
