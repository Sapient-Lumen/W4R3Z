#!/usr/bin/env python3
"""Verify the rev0859 payload-receipt liveness proofcore lane.

This lane keeps the rev0858 payload receipts and framed transcript artifacts
hash-stable, but stops relying on the legacy rev0858 receipt verifier as an
active endpoint.  Parent replay reconstructs rev0858 and validates its receipt
and transcript surfaces with the rev0859 in-process replay path.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REVISION = "rev0859"


class LaneVerifyError(Exception):
    pass


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj)).hexdigest()


def sha256_file(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise LaneVerifyError(f"cannot hash non-regular file: {path}")
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except Exception:
        return str(path)


def clean_archive_path(text: Any, field: str) -> str:
    if not isinstance(text, str) or not text:
        raise LaneVerifyError(f"{field} must be a non-empty string")
    if "\x00" in text or "\\" in text:
        raise LaneVerifyError(f"{field} must be a POSIX relative archive path: {text!r}")
    pure = PurePosixPath(text)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise LaneVerifyError(f"{field} must be clean and relative: {text!r}")
    return pure.as_posix()


def load_json_rel(path_text: Any, field: str, *, root: Path = ROOT) -> dict[str, Any]:
    rel_path = clean_archive_path(path_text, field)
    path = root / rel_path
    if path.is_symlink() or not path.is_file():
        raise LaneVerifyError(f"{field} is not a regular file: {rel_path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise LaneVerifyError(f"{field} invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise LaneVerifyError(f"{field} must contain a JSON object")
    return data


def apply_mutation(obj: Any, pointer: str, value: Any) -> None:
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise LaneVerifyError(f"unsupported mutation pointer: {pointer!r}")
    parts = [part.replace("~1", "/").replace("~0", "~") for part in pointer.strip("/").split("/")]
    cur = obj
    for part in parts[:-1]:
        if isinstance(cur, list):
            cur = cur[int(part)]
        elif isinstance(cur, dict):
            cur = cur[part]
        else:
            raise LaneVerifyError(f"cannot traverse mutation pointer through {type(cur).__name__}")
    last = parts[-1]
    if isinstance(cur, list):
        cur[int(last)] = value
    elif isinstance(cur, dict):
        cur[last] = value
    else:
        raise LaneVerifyError(f"cannot set mutation pointer on {type(cur).__name__}")


def run_command(args: list[str], *, marker: str, cwd: Path = ROOT, timeout: int = 30) -> str:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(args, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=timeout)
    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0:
        raise LaneVerifyError(f"command failed {args}: stdout={result.stdout!r} stderr={result.stderr!r}")
    if marker not in output:
        raise LaneVerifyError(f"command output missing marker {marker!r}: {output!r}")
    return output




def import_module_from_root(root: Path, rel_path: str, module_name: str) -> ModuleType:
    path = root / clean_archive_path(rel_path, f"{module_name} path")
    if path.is_symlink() or not path.is_file():
        raise LaneVerifyError(f"module path is not a regular file: {rel_path}")
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise LaneVerifyError(f"cannot import module: {rel_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    if hasattr(module, "ROOT"):
        module.ROOT = root  # type: ignore[attr-defined]
    return module

def check_ref(obj: dict[str, Any], prefix: str, *, root: Path = ROOT) -> tuple[str, str]:
    path = clean_archive_path(obj.get(f"{prefix}_path"), f"{prefix}_path")
    expected = obj.get(f"{prefix}_sha256")
    observed = sha256_file(root / path)
    if expected != observed:
        raise LaneVerifyError(f"{prefix} hash mismatch")
    return path, observed


def verify_certificate(certificate: dict[str, Any], claim: dict[str, Any], public_inputs: dict[str, Any], commitments: dict[str, Any]) -> None:
    if certificate.get("revision") != REVISION or claim.get("revision") != REVISION or public_inputs.get("revision") != REVISION or commitments.get("revision") != REVISION:
        raise LaneVerifyError("revision mismatch")
    if certificate.get("claim", {}).get("sha256") != sha256_obj(claim):
        raise LaneVerifyError("certificate claim hash mismatch")
    if certificate.get("public_inputs", {}).get("sha256") != sha256_obj(public_inputs):
        raise LaneVerifyError("certificate public-input hash mismatch")
    if certificate.get("commitments", {}).get("sha256") != sha256_obj(commitments):
        raise LaneVerifyError("certificate commitments hash mismatch")
    if certificate.get("verifier", {}).get("sha256") != sha256_file(ROOT / certificate.get("verifier", {}).get("path", "")):
        raise LaneVerifyError("certificate lane verifier hash mismatch")
    proof = certificate.get("proof_system", {})
    if proof.get("snark") or proof.get("zero_knowledge") or proof.get("succinct"):
        raise LaneVerifyError("certificate must not claim SNARK/ZK/succinct")
    text = "\n".join(str(x) for x in certificate.get("non_claims") or [])
    for phrase in ["not a SNARK", "not zero knowledge", "not succinct", "not a rights grant"]:
        if phrase.lower() not in text.lower():
            raise LaneVerifyError(f"certificate missing non-claim: {phrase}")


def verify_rights(public_inputs: dict[str, Any]) -> None:
    rights = load_json_rel("RIGHTS/component_license_ledger.json", "rights ledger")
    if rights.get("status") != "publication_blocked_pending_rights_decision":
        raise LaneVerifyError("rights ledger status drifted")
    if public_inputs.get("rights_status") != rights.get("status"):
        raise LaneVerifyError("public input rights status mismatch")
    for sentinel in ["LICENSE", "COPYING", "NOTICE"]:
        if (ROOT / sentinel).exists():
            raise LaneVerifyError(f"root rights sentinel was invented: {sentinel}")


def verify_liveness_contract(public_inputs: dict[str, Any]) -> dict[str, Any]:
    live = public_inputs.get("receipt_liveness")
    if not isinstance(live, dict):
        raise LaneVerifyError("missing receipt_liveness public input")
    for key in [
        "contract", "inprocess_receipt_verifier", "legacy_receipt_verifier", "payload_candidate_verifier",
        "full_absence_receipt", "minimum_absence_receipt", "reject_tampered_receipt", "audit",
    ]:
        check_ref(live, key)
    contract = load_json_rel(live.get("contract_path"), "receipt liveness contract")
    audit = load_json_rel(live.get("audit_path"), "liveness audit")
    if contract.get("revision") != REVISION or audit.get("revision") != REVISION:
        raise LaneVerifyError("liveness contract/audit revision mismatch")
    if contract.get("status") != "active_inprocess_receipt_replay_replaces_legacy_subprocess_pipe_endpoint":
        raise LaneVerifyError("liveness contract status drifted")
    if audit.get("status") != "legacy_subprocess_receipt_verifier_quarantined_inprocess_replay_active":
        raise LaneVerifyError("liveness audit status drifted")
    if live.get("legacy_receipt_verifier_status") != "historical_hash_bound_liveness_quarantined_not_active_endpoint":
        raise LaneVerifyError("legacy receipt verifier is not quarantined")
    if live.get("expected_full_absent_count") != 17 or live.get("expected_minimum_absent_count") != 4:
        raise LaneVerifyError("payload absence counts drifted")
    legacy_path = live.get("legacy_receipt_verifier_path")
    legacy_text = (ROOT / clean_archive_path(legacy_path, "legacy verifier path")).read_text(encoding="utf-8")
    source_block = legacy_text[legacy_text.find("def run_source_verifier"):legacy_text.find("def verify_rights_blocked")]
    if "stdout=subprocess.PIPE" not in source_block or "stderr=subprocess.PIPE" not in source_block:
        raise LaneVerifyError("legacy liveness risk source shape changed; audit needs refresh")
    if "timeout=" in source_block:
        raise LaneVerifyError("legacy run_source_verifier now has a timeout; audit should be regenerated")
    return {"ok": True, "contract_id": contract.get("contract_id"), "audit_status": audit.get("status")}


def verify_receipts(public_inputs: dict[str, Any], *, root: Path = ROOT) -> dict[str, Any]:
    live = public_inputs.get("receipt_liveness")
    if not isinstance(live, dict):
        raise LaneVerifyError("missing receipt_liveness public input")
    verifier = clean_archive_path(live.get("inprocess_receipt_verifier_path"), "inprocess receipt verifier")
    full = clean_archive_path(live.get("full_absence_receipt_path"), "full receipt")
    minimum = clean_archive_path(live.get("minimum_absence_receipt_path"), "minimum receipt")
    reject = clean_archive_path(live.get("reject_tampered_receipt_path"), "reject receipt")
    # Do not spawn a child process here. The point of rev0859 is to remove
    # subprocess-pipe liveness from the active receipt replay path. Import the
    # verifier and call its pure verification function directly.
    receipt_module = import_module_from_root(ROOT, verifier, "ev_rev0859_inprocess_receipt_for_lane")
    for receipt in [full, minimum]:
        result = receipt_module.verify_receipt(root, receipt)  # type: ignore[attr-defined]
        if not isinstance(result, dict) or result.get("ok") is not True:
            raise LaneVerifyError(f"in-process receipt verification failed for {receipt}")
    try:
        receipt_module.verify_receipt(root, reject)  # type: ignore[attr-defined]
    except Exception:
        pass
    else:
        raise LaneVerifyError("tampered payload receipt unexpectedly verified")
    return {"ok": True, "verified_receipts": [full, minimum], "reject_receipt": reject, "execution_model": "in_process_no_subprocess"}


def verify_transcript_harness(public_inputs: dict[str, Any], *, root: Path = ROOT) -> dict[str, Any]:
    transcript = public_inputs.get("framed_transcript_parent_surface")
    if not isinstance(transcript, dict):
        raise LaneVerifyError("missing framed_transcript_parent_surface")
    for key in ["verifier", "accept_fixture", "reject_reordered_fixture", "reject_label_swap_fixture"]:
        check_ref(transcript, key, root=root)
    verifier = clean_archive_path(transcript.get("verifier_path"), "transcript verifier")
    accept = clean_archive_path(transcript.get("accept_fixture_path"), "transcript accept fixture")
    reject_reordered = clean_archive_path(transcript.get("reject_reordered_fixture_path"), "transcript reject reordered fixture")
    reject_label = clean_archive_path(transcript.get("reject_label_swap_fixture_path"), "transcript reject label fixture")
    transcript_module = import_module_from_root(root, verifier, f"ev_rev0858_framed_transcript_{abs(hash(str(root))) }")
    accept_data = transcript_module.load_json_rel(accept, "accept fixture")  # type: ignore[attr-defined]
    result = transcript_module.verify_fixture_data(accept_data)  # type: ignore[attr-defined]
    if not isinstance(result, dict) or result.get("ok") is not True:
        raise LaneVerifyError("framed transcript accept fixture failed")
    for fixture_rel in [reject_reordered, reject_label]:
        data = transcript_module.load_json_rel(fixture_rel, "reject fixture")  # type: ignore[attr-defined]
        try:
            transcript_module.verify_fixture_data(data)  # type: ignore[attr-defined]
        except Exception:
            continue
        raise LaneVerifyError(f"framed transcript reject fixture unexpectedly verified: {fixture_rel}")
    return {"ok": True, "transcript_revision": "rev0858", "execution_model": "in_process_no_subprocess"}


def verify_parent_checkpoint(public_inputs: dict[str, Any], *, skip_parent_replay: bool) -> dict[str, Any]:
    parent = public_inputs.get("parent_checkpoint")
    if not isinstance(parent, dict):
        raise LaneVerifyError("missing parent checkpoint")
    if parent.get("parent_revision") != "rev0858":
        raise LaneVerifyError("parent checkpoint revision mismatch")
    if skip_parent_replay:
        return {"ok": True, "parent_revision": "rev0858", "skipped_by_explicit_operator_flag": True}
    patch_path = clean_archive_path(parent.get("reconstruction_patch_path"), "parent reconstruction patch path")
    patch_abs = ROOT / patch_path
    if patch_abs.is_symlink() or not patch_abs.is_file():
        raise LaneVerifyError(f"reconstruction patch missing: {patch_path}")
    with tempfile.TemporaryDirectory(prefix="ev-rev0858-replay-") as tmp:
        tmp_root = Path(tmp) / "parent"
        def ignore(_dirpath: str, names: list[str]):
            return {name for name in names if name in {".git", "__pycache__"}}
        shutil.copytree(ROOT, tmp_root, ignore=ignore)
        result = subprocess.run(["git", "apply", "--reverse", "--whitespace=nowarn", str(patch_abs)], cwd=tmp_root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=60)
        if result.returncode != 0:
            raise LaneVerifyError(f"parent rev0858 reconstruction reverse-patch failed: {result.stderr.strip() or result.stdout.strip()}")
        reconstructed_patch = tmp_root / patch_path
        if reconstructed_patch.exists():
            if reconstructed_patch.is_symlink() or not reconstructed_patch.is_file():
                raise LaneVerifyError(f"reconstructed patch path is not a removable regular file: {patch_path}")
            reconstructed_patch.unlink()
        for item in parent.get("cyclic_surface_snapshots") or []:
            if not isinstance(item, dict):
                raise LaneVerifyError("parent snapshot item must be an object")
            snapshot = clean_archive_path(item.get("snapshot_path"), "parent snapshot path")
            destination = clean_archive_path(item.get("destination"), "parent snapshot destination")
            snap_abs = ROOT / snapshot
            if item.get("sha256") != sha256_file(snap_abs):
                raise LaneVerifyError(f"parent snapshot hash mismatch: {snapshot}")
            dest_abs = tmp_root / destination
            dest_abs.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(snap_abs, dest_abs)
        verify_receipts(public_inputs, root=tmp_root)
        verify_transcript_harness(public_inputs, root=tmp_root)
    return {"ok": True, "parent_revision": "rev0858", "replay_strategy": "reverse_patch_plus_rev0859_inprocess_receipt_replay"}


def verify_fixture(fixture_path: Path, *, skip_parent_replay: bool = False) -> dict[str, Any]:
    fixture = load_json_rel(rel(fixture_path), "fixture")
    claim = load_json_rel(fixture.get("claim_path"), "fixture.claim_path")
    public_inputs = load_json_rel(fixture.get("public_inputs_path"), "fixture.public_inputs_path")
    commitments = load_json_rel(fixture.get("commitments_path"), "fixture.commitments_path")
    certificate = load_json_rel(fixture.get("certificate_path"), "fixture.certificate_path")
    for mutation in fixture.get("mutations") or []:
        if not isinstance(mutation, dict) or mutation.get("target") != "public_inputs":
            raise LaneVerifyError("only public_inputs fixture mutations are supported")
        if mutation.get("op") != "replace":
            raise LaneVerifyError("only replace fixture mutations are supported")
        apply_mutation(public_inputs, mutation.get("path"), mutation.get("value"))
    verify_certificate(certificate, claim, public_inputs, commitments)
    verify_rights(public_inputs)
    liveness_result = verify_liveness_contract(public_inputs)
    receipt_result = verify_receipts(public_inputs)
    transcript_result = verify_transcript_harness(public_inputs)
    parent_result = verify_parent_checkpoint(public_inputs, skip_parent_replay=skip_parent_replay)
    return {
        "ok": True,
        "fixture_id": fixture.get("fixture_id"),
        "claim_id": claim.get("claim_id"),
        "parent": parent_result,
        "liveness": liveness_result,
        "receipts": receipt_result,
        "transcript": transcript_result,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify rev0859 payload-receipt liveness proofcore lane")
    parser.add_argument("--fixture", required=True, help="fixture JSON path relative to repository root")
    parser.add_argument("--expect-fail", action="store_true", help="succeed only if verification fails")
    parser.add_argument("--skip-parent-replay", action="store_true", help="skip expensive parent reconstruction when explicitly requested")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)
    fixture_rel = clean_archive_path(args.fixture, "--fixture")
    try:
        result = verify_fixture(ROOT / fixture_rel, skip_parent_replay=args.skip_parent_replay)
    except Exception as exc:
        if args.expect_fail:
            payload = {"ok": True, "expected_failure_observed": True, "fixture": fixture_rel, "failure": str(exc), "revision": REVISION}
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print("streamfold-payload-receipt-liveness-lane-rev0859: expected failure observed")
            return 0
        if args.json:
            print(json.dumps({"ok": False, "fixture": fixture_rel, "error": str(exc), "revision": REVISION}, indent=2, sort_keys=True))
        else:
            print(f"streamfold-payload-receipt-liveness-lane-rev0859: FAIL: {exc}", file=sys.stderr)
        return 1
    if args.expect_fail:
        message = "fixture unexpectedly verified successfully"
        if args.json:
            print(json.dumps({"ok": False, "fixture": fixture_rel, "error": message, "revision": REVISION}, indent=2, sort_keys=True))
        else:
            print(f"streamfold-payload-receipt-liveness-lane-rev0859: FAIL: {message}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("streamfold-payload-receipt-liveness-lane-rev0859: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
