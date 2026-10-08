#!/usr/bin/env python3
"""Verify legacy rev0858 streamfold payload receipts without subprocess pipes.

rev0858 introduced portable payload absence receipts, but its receipt verifier
recomputed the rev0857 source report by spawning the rev0857 verifier with
captured stdout/stderr.  In this cloudtainer that verifier can emit the success
marker and still leave the parent waiting on the pipe.  This rev0859 verifier
keeps the historical receipt bytes intact and recomputes the same source report
in-process by loading the rev0857 candidate verifier module from the requested
root.

It does not admit payload bytes, copy payloads, grant rights, prove streamfold
correctness, or claim any SNARK/ZK/succinct property.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path, PurePosixPath
from types import ModuleType
from typing import Any

DEFAULT_ROOT = Path(__file__).resolve().parents[2]
REVISION = "rev0859"
LEGACY_RECEIPT_REVISION = "rev0858"


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
        raise ReceiptVerifyError(f"{field} must be a POSIX relative archive path: {text!r}")
    pure = PurePosixPath(text)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise ReceiptVerifyError(f"{field} must be clean and relative: {text!r}")
    return pure.as_posix()


def resolve_root(text: str | None) -> Path:
    root = DEFAULT_ROOT if text is None else Path(text).expanduser()
    if root.is_symlink() or not root.is_dir():
        raise ReceiptVerifyError(f"root must be a real directory: {root}")
    return root.resolve()


def load_json_rel(root: Path, path_text: Any, field: str) -> dict[str, Any]:
    rel = clean_archive_path(path_text, field)
    path = root / rel
    if path.is_symlink() or not path.is_file():
        raise ReceiptVerifyError(f"{field} is not a regular file: {rel}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ReceiptVerifyError(f"{field} invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ReceiptVerifyError(f"{field} must contain a JSON object")
    return data


def check_ref(root: Path, obj: dict[str, Any], key: str) -> tuple[str, str]:
    ref = obj.get(key)
    if not isinstance(ref, dict):
        raise ReceiptVerifyError(f"missing reference: {key}")
    rel = clean_archive_path(ref.get("path"), f"{key}.path")
    observed = sha256_file(root / rel)
    if ref.get("sha256") != observed:
        raise ReceiptVerifyError(f"{key} hash mismatch")
    return rel, observed


def import_candidate_verifier(root: Path, verifier_rel: str) -> ModuleType:
    verifier_path = root / clean_archive_path(verifier_rel, "source verifier path")
    if verifier_path.is_symlink() or not verifier_path.is_file():
        raise ReceiptVerifyError(f"source verifier missing: {verifier_rel}")
    spec = importlib.util.spec_from_file_location("ev_rev0857_payload_candidate_for_rev0859", verifier_path)
    if spec is None or spec.loader is None:
        raise ReceiptVerifyError(f"cannot import source verifier: {verifier_rel}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    # Be explicit.  The loaded module normally computes ROOT from its own file,
    # but parent-replay callers may load it from a temporary reconstructed root.
    module.ROOT = root  # type: ignore[attr-defined]
    return module


def run_source_verifier_inprocess(root: Path, verifier_rel: str, mode: str) -> dict[str, Any]:
    module = import_candidate_verifier(root, verifier_rel)
    for name in ["load_contract_and_manifest", "verify_payloads", "DEFAULT_MANIFEST", "DEFAULT_CONTRACT"]:
        if not hasattr(module, name):
            raise ReceiptVerifyError(f"source verifier lacks required symbol: {name}")
    manifest, contract, manifest_sha, contract_sha = module.load_contract_and_manifest(module.DEFAULT_MANIFEST, module.DEFAULT_CONTRACT)  # type: ignore[attr-defined]
    result = module.verify_payloads(None, manifest, contract, mode=mode)  # type: ignore[attr-defined]
    if not isinstance(result, dict) or result.get("ok") is not True:
        raise ReceiptVerifyError(f"source verifier emitted unexpected result: {result}")
    result["payload_manifest_sha256"] = manifest_sha
    result["payload_admission_contract_sha256"] = contract_sha
    return result


def verify_rights_blocked(root: Path) -> None:
    rights = load_json_rel(root, "RIGHTS/component_license_ledger.json", "rights ledger")
    if rights.get("status") != "publication_blocked_pending_rights_decision":
        raise ReceiptVerifyError("rights status drifted")
    for sentinel in ["LICENSE", "COPYING", "NOTICE"]:
        if (root / sentinel).exists():
            raise ReceiptVerifyError(f"root rights sentinel was invented: {sentinel}")


def check_non_claims(items: Any, field: str) -> None:
    text = "\n".join(str(item) for item in (items or []))
    for phrase in ["not a rights grant", "not a recovered payload bundle", "not a streamfold correctness proof"]:
        if phrase.lower() not in text.lower():
            raise ReceiptVerifyError(f"{field} missing non-claim: {phrase}")


def verify_receipt(root: Path, receipt_rel: str) -> dict[str, Any]:
    receipt_rel = clean_archive_path(receipt_rel, "receipt")
    receipt = load_json_rel(root, receipt_rel, "receipt")
    if receipt.get("revision") != LEGACY_RECEIPT_REVISION:
        raise ReceiptVerifyError("legacy receipt revision mismatch")
    if receipt.get("receipt_type") != "streamfold_payload_candidate_absence_receipt":
        raise ReceiptVerifyError("unsupported receipt type")
    mode = receipt.get("mode")
    if mode not in {"full", "minimum"}:
        raise ReceiptVerifyError("receipt mode must be full or minimum")
    check_non_claims(receipt.get("non_claims"), "receipt")
    verifier_rel, verifier_sha = check_ref(root, receipt, "source_verifier")
    manifest_rel, manifest_sha = check_ref(root, receipt, "payload_manifest")
    source_contract_rel, source_contract_sha = check_ref(root, receipt, "source_payload_admission_contract")
    receipt_contract_rel, receipt_contract_sha = check_ref(root, receipt, "payload_receipt_contract")
    contract = load_json_rel(root, receipt_contract_rel, "payload receipt contract")
    if contract.get("revision") != LEGACY_RECEIPT_REVISION:
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
    recomputed = run_source_verifier_inprocess(root, verifier_rel, mode)
    if embedded != recomputed:
        raise ReceiptVerifyError("embedded source_report does not match in-process recomputation")
    expected_counts = {"full": 17, "minimum": 4}
    if embedded.get("selected_path_count") != expected_counts[mode]:
        raise ReceiptVerifyError("selected path count drifted")
    if embedded.get("overlay_payloads_absent") != expected_counts[mode]:
        raise ReceiptVerifyError("overlay absence count drifted")
    if embedded.get("candidate_admission_status") != "blocked_waiting_for_candidate_root":
        raise ReceiptVerifyError("absence receipt must remain blocked waiting for candidate root")
    if embedded.get("candidate_root_checked") is not False or embedded.get("candidate_payloads_present") != 0:
        raise ReceiptVerifyError("absence receipt unexpectedly records candidate-root payloads")
    verify_rights_blocked(root)
    return {
        "ok": True,
        "revision": REVISION,
        "verified_legacy_receipt_revision": LEGACY_RECEIPT_REVISION,
        "receipt": receipt_rel,
        "mode": mode,
        "source_verifier_sha256": verifier_sha,
        "payload_manifest_sha256": manifest_sha,
        "source_payload_admission_contract_sha256": source_contract_sha,
        "payload_receipt_contract_sha256": receipt_contract_sha,
        "selected_path_count": embedded.get("selected_path_count"),
        "overlay_payloads_absent": embedded.get("overlay_payloads_absent"),
        "recomputation_mode": "in_process_import_no_subprocess_pipe",
        "non_claims": [
            "not a rights grant",
            "not a recovered payload bundle",
            "not a streamfold correctness proof",
            "not a SNARK",
            "not zero knowledge",
            "not succinct",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify rev0858 streamfold payload receipts in-process without subprocess pipes")
    parser.add_argument("--root", help="bundle/candidate root to verify; defaults to this verifier's bundle root")
    parser.add_argument("--receipt", required=True, help="receipt JSON path relative to root")
    parser.add_argument("--expect-fail", action="store_true", help="succeed only if verification fails")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)
    try:
        root = resolve_root(args.root)
        result = verify_receipt(root, args.receipt)
    except Exception as exc:
        if args.expect_fail:
            payload = {"ok": True, "expected_failure_observed": True, "receipt": args.receipt, "failure": str(exc), "revision": REVISION}
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print("streamfold-payload-receipt-inprocess-rev0859: expected failure observed")
            return 0
        if args.json:
            print(json.dumps({"ok": False, "receipt": args.receipt, "error": str(exc), "revision": REVISION}, indent=2, sort_keys=True))
        else:
            print(f"streamfold-payload-receipt-inprocess-rev0859: FAIL: {exc}", file=sys.stderr)
        return 1
    if args.expect_fail:
        message = "receipt unexpectedly verified successfully"
        if args.json:
            print(json.dumps({"ok": False, "receipt": args.receipt, "error": message, "revision": REVISION}, indent=2, sort_keys=True))
        else:
            print(f"streamfold-payload-receipt-inprocess-rev0859: FAIL: {message}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("streamfold-payload-receipt-inprocess-rev0859: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
