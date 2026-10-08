#!/usr/bin/env python3
"""Verify the rev0858 parent-linked framed-transcript + payload-receipt lane."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REVISION = "rev0858"


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


def clean_archive_path(text: Any, field: str) -> str:
    if not isinstance(text, str) or not text:
        raise LaneVerifyError(f"{field} must be a non-empty string")
    if "\x00" in text or "\\" in text:
        raise LaneVerifyError(f"{field} must be a POSIX relative path: {text!r}")
    pure = PurePosixPath(text)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise LaneVerifyError(f"{field} must be clean and relative: {text!r}")
    return pure.as_posix()


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def load_json_rel(path_text: str, field: str) -> dict[str, Any]:
    rel_path = clean_archive_path(path_text, field)
    path = ROOT / rel_path
    if path.is_symlink() or not path.is_file():
        raise LaneVerifyError(f"{field} is not a regular file: {rel_path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise LaneVerifyError(f"{field} invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise LaneVerifyError(f"{field} must contain a JSON object")
    return data


def clean_candidate_root(text: str | None) -> Path | None:
    if text is None:
        return None
    raw = Path(text).expanduser()
    if raw.is_symlink():
        raise LaneVerifyError(f"candidate root must be a real directory, not a symlink: {text}")
    path = raw.resolve(strict=False)
    if path.is_symlink() or not path.is_dir():
        raise LaneVerifyError(f"candidate root must be a real directory, not a symlink: {text}")
    return path


def run_command(args: list[str], *, marker: str, cwd: Path | None = None) -> str:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(args, cwd=cwd or ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0:
        raise LaneVerifyError(f"command failed {args}: stdout={result.stdout!r} stderr={result.stderr!r}")
    if marker not in output:
        raise LaneVerifyError(f"command output missing marker {marker!r}: {output!r}")
    return output


def run_command_inherited(args: list[str], *, marker: str, cwd: Path) -> None:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(args, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    output = result.stdout or ""
    if result.returncode != 0:
        raise LaneVerifyError(f"parent command failed {args}: output={output!r}")
    if marker not in output:
        raise LaneVerifyError(f"parent command output missing marker {marker!r}: {output!r}")


def apply_mutation(obj: Any, pointer: str, value: Any) -> None:
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise LaneVerifyError(f"mutation path must be a JSON pointer: {pointer!r}")
    parts = [part.replace("~1", "/").replace("~0", "~") for part in pointer.strip("/").split("/")]
    cursor = obj
    for part in parts[:-1]:
        if isinstance(cursor, dict):
            cursor = cursor[part]
        elif isinstance(cursor, list):
            cursor = cursor[int(part)]
        else:
            raise LaneVerifyError(f"mutation path cannot traverse {part!r}")
    last = parts[-1]
    if isinstance(cursor, dict):
        if last not in cursor:
            raise LaneVerifyError(f"mutation path missing key: {last}")
        cursor[last] = value
    elif isinstance(cursor, list):
        cursor[int(last)] = value
    else:
        raise LaneVerifyError("mutation target is not mutable")


def verify_certificate(certificate: dict[str, Any], claim: dict[str, Any], public_inputs: dict[str, Any], commitments: dict[str, Any]) -> None:
    if certificate.get("revision") != REVISION or claim.get("revision") != REVISION or public_inputs.get("revision") != REVISION or commitments.get("revision") != REVISION:
        raise LaneVerifyError("revision mismatch in claim/public-input/commitment/certificate set")
    if certificate.get("proof_system", {}).get("snark") or certificate.get("proof_system", {}).get("zero_knowledge") or certificate.get("proof_system", {}).get("succinct"):
        raise LaneVerifyError("certificate overclaims SNARK/ZK/succinct proof material")
    refs = {
        "claim": (certificate.get("claim", {}) or {}).get("path"),
        "public_inputs": (certificate.get("public_inputs", {}) or {}).get("path"),
        "commitments": (certificate.get("commitments", {}) or {}).get("path"),
        "verifier": (certificate.get("verifier", {}) or {}).get("path"),
    }
    expected = {
        "claim": sha256_file(ROOT / clean_archive_path(refs["claim"], "certificate claim path")),
        "public_inputs": sha256_file(ROOT / clean_archive_path(refs["public_inputs"], "certificate public_inputs path")),
        "commitments": sha256_file(ROOT / clean_archive_path(refs["commitments"], "certificate commitments path")),
        "verifier": sha256_file(ROOT / clean_archive_path(refs["verifier"], "certificate verifier path")),
    }
    for key in ["claim", "public_inputs", "commitments", "verifier"]:
        path = clean_archive_path(refs[key], f"certificate {key} path")
        ref = certificate.get(key, {})
        if ref.get("sha256") != expected[key]:
            raise LaneVerifyError(f"certificate {key} hash mismatch")
        if key != "verifier" and path != {
            "claim": "PROOFCORE/claims/ev-streamfold-framed-receipt.rev0858.claim.json",
            "public_inputs": "PROOFCORE/public_inputs/ev-streamfold-framed-receipt.rev0858.public-input.json",
            "commitments": "PROOFCORE/commitments/ev-streamfold-framed-receipt.rev0858.commitments.json",
        }[key]:
            raise LaneVerifyError(f"certificate {key} path mismatch")
    non_claims = "\n".join(str(item) for item in certificate.get("non_claims") or [])
    for phrase in ["not a SNARK", "not zero knowledge", "not succinct", "not a rights grant"]:
        if phrase.lower() not in non_claims.lower():
            raise LaneVerifyError(f"certificate missing non-claim: {phrase}")


def verify_rights(public_inputs: dict[str, Any]) -> None:
    rights = load_json_rel("RIGHTS/component_license_ledger.json", "rights ledger")
    if rights.get("status") != "publication_blocked_pending_rights_decision":
        raise LaneVerifyError("rights ledger status drifted")
    if public_inputs.get("rights_status") != rights.get("status"):
        raise LaneVerifyError("public input rights status does not match ledger")
    for sentinel in ["LICENSE", "COPYING", "NOTICE"]:
        if (ROOT / sentinel).exists():
            raise LaneVerifyError(f"root rights sentinel was invented: {sentinel}")


def verify_parent_checkpoint(public_inputs: dict[str, Any]) -> dict[str, Any]:
    parent = public_inputs.get("parent_checkpoint")
    if not isinstance(parent, dict):
        raise LaneVerifyError("missing parent_checkpoint")
    patch_path = clean_archive_path(parent.get("reconstruction_patch_path"), "parent.reconstruction_patch_path")
    patch_abs = ROOT / patch_path
    if patch_abs.is_symlink() or not patch_abs.is_file():
        raise LaneVerifyError(f"reconstruction patch missing: {patch_path}")
    with tempfile.TemporaryDirectory(prefix="ev-rev0857-replay-") as tmp:
        tmp_root = Path(tmp) / "parent"
        def ignore(_dirpath: str, names: list[str]):
            return {name for name in names if name in {".git", "__pycache__"}}
        shutil.copytree(ROOT, tmp_root, ignore=ignore)
        result = subprocess.run(["git", "apply", "--reverse", "--whitespace=nowarn", str(patch_abs)], cwd=tmp_root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if result.returncode != 0:
            raise LaneVerifyError(f"parent rev0857 reconstruction reverse-patch failed: {result.stderr.strip() or result.stdout.strip()}")
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
        verifier_path = clean_archive_path(parent.get("parent_verifier_path"), "parent verifier path")
        fixture_path = clean_archive_path(parent.get("parent_accept_fixture"), "parent accept fixture")
        run_command_inherited([sys.executable, verifier_path, "--fixture", fixture_path, "--skip-parent-replay"], cwd=tmp_root, marker="streamfold-payload-admission-lane-rev0857: OK")
    return {"parent_revision": parent.get("parent_revision"), "ok": True, "marker": "streamfold-payload-admission-lane-rev0857: OK"}


def verify_payload_receipts(public_inputs: dict[str, Any]) -> dict[str, Any]:
    payload = public_inputs.get("payload_receipts")
    if not isinstance(payload, dict):
        raise LaneVerifyError("missing payload_receipts")
    for label in ["receipt_contract", "receipt_verifier", "full_absence_receipt", "minimum_absence_receipt", "reject_tampered_receipt"]:
        path = clean_archive_path(payload.get(f"{label}_path"), f"payload_receipts.{label}_path")
        if payload.get(f"{label}_sha256") != sha256_file(ROOT / path):
            raise LaneVerifyError(f"payload receipt {label} hash mismatch")
    verifier = clean_archive_path(payload.get("receipt_verifier_path"), "payload_receipts.receipt_verifier_path")
    full = clean_archive_path(payload.get("full_absence_receipt_path"), "payload_receipts.full_absence_receipt_path")
    minimum = clean_archive_path(payload.get("minimum_absence_receipt_path"), "payload_receipts.minimum_absence_receipt_path")
    reject = clean_archive_path(payload.get("reject_tampered_receipt_path"), "payload_receipts.reject_tampered_receipt_path")
    run_command([sys.executable, verifier, "--receipt", full], marker="streamfold-payload-receipt-rev0858: OK")
    run_command([sys.executable, verifier, "--receipt", minimum], marker="streamfold-payload-receipt-rev0858: OK")
    run_command([sys.executable, verifier, "--receipt", reject, "--expect-fail"], marker="streamfold-payload-receipt-rev0858: expected failure observed")
    return {"ok": True, "receipts": [full, minimum], "reject_receipt": reject}


def verify_framed_transcript_harness(public_inputs: dict[str, Any]) -> dict[str, Any]:
    harness = public_inputs.get("framed_transcript_harness")
    if not isinstance(harness, dict):
        raise LaneVerifyError("missing framed_transcript_harness")
    for label in ["contract", "protocol_profile", "verifier", "accept_fixture", "reject_reordered_fixture", "reject_label_swap_fixture"]:
        path = clean_archive_path(harness.get(f"{label}_path"), f"framed_transcript_harness.{label}_path")
        if harness.get(f"{label}_sha256") != sha256_file(ROOT / path):
            raise LaneVerifyError(f"framed transcript {label} hash mismatch")
    verifier = clean_archive_path(harness.get("verifier_path"), "framed_transcript_harness.verifier_path")
    accept = clean_archive_path(harness.get("accept_fixture_path"), "framed_transcript_harness.accept_fixture_path")
    reject_reordered = clean_archive_path(harness.get("reject_reordered_fixture_path"), "framed_transcript_harness.reject_reordered_fixture_path")
    reject_label = clean_archive_path(harness.get("reject_label_swap_fixture_path"), "framed_transcript_harness.reject_label_swap_fixture_path")
    accept_data = load_json_rel(accept, "framed transcript accept fixture")
    rounds = accept_data.get("transcript", {}).get("rounds", [])
    actual_challenges = [round_data.get("challenge") for round_data in rounds if isinstance(round_data, dict)]
    if harness.get("derived_accept_challenges") != actual_challenges:
        raise LaneVerifyError("framed transcript derived challenge public input mismatch")
    if harness.get("accept_final_evaluation_mod_p") != accept_data.get("transcript", {}).get("final_evaluation"):
        raise LaneVerifyError("framed transcript final evaluation public input mismatch")
    run_command([sys.executable, verifier, "--fixture", accept], marker="sumcheck-fs-framed-transcript-rev0858: OK")
    run_command([sys.executable, verifier, "--fixture", reject_reordered, "--expect-fail"], marker="sumcheck-fs-framed-transcript-rev0858: expected failure observed")
    run_command([sys.executable, verifier, "--fixture", reject_label, "--expect-fail"], marker="sumcheck-fs-framed-transcript-rev0858: expected failure observed")
    return {"ok": True, "accept_fixture": accept, "reject_fixtures": [reject_reordered, reject_label], "derived_accept_challenges": actual_challenges}


def verify_candidate_attack_matrix(public_inputs: dict[str, Any]) -> dict[str, Any]:
    matrix = public_inputs.get("candidate_attack_matrix")
    if not isinstance(matrix, dict):
        raise LaneVerifyError("missing candidate_attack_matrix")
    path = clean_archive_path(matrix.get("path"), "candidate_attack_matrix.path")
    if matrix.get("sha256") != sha256_file(ROOT / path):
        raise LaneVerifyError("candidate attack matrix hash mismatch")
    data = load_json_rel(path, "candidate attack matrix")
    if data.get("revision") != REVISION or data.get("status") != "negative_controls_documented_and_exercised_by_validator":
        raise LaneVerifyError("candidate attack matrix status drifted")
    expected = set(matrix.get("expected_failure_classes") or [])
    actual = {item.get("failure_class") for item in data.get("negative_controls") or [] if isinstance(item, dict)}
    if not expected.issubset(actual):
        raise LaneVerifyError("candidate attack matrix is missing expected failure classes")
    return {"ok": True, "negative_control_count": len(actual), "failure_classes": sorted(actual)}


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
            raise LaneVerifyError("only replace mutations are supported")
        apply_mutation(public_inputs, mutation.get("path"), mutation.get("value"))
    verify_certificate(certificate, claim, public_inputs, commitments)
    verify_rights(public_inputs)
    receipts_result = verify_payload_receipts(public_inputs)
    transcript_result = verify_framed_transcript_harness(public_inputs)
    attack_matrix_result = verify_candidate_attack_matrix(public_inputs)
    if skip_parent_replay:
        parent_result = {"ok": True, "parent_revision": public_inputs.get("parent_checkpoint", {}).get("parent_revision"), "skipped_by_explicit_operator_flag": True}
    else:
        parent_result = verify_parent_checkpoint(public_inputs)
    return {
        "ok": True,
        "fixture_id": fixture.get("fixture_id"),
        "claim_id": claim.get("claim_id"),
        "parent": parent_result,
        "payload_receipts": receipts_result,
        "framed_transcript_harness": transcript_result,
        "candidate_attack_matrix": attack_matrix_result,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify EvidenceVault rev0858 streamfold framed-transcript receipt lane")
    parser.add_argument("--fixture", required=True, help="fixture JSON path relative to repository root")
    parser.add_argument("--skip-parent-replay", action="store_true", help="validate current rev0858 surfaces without replaying rev0857 parent; for fast local validators only")
    parser.add_argument("--expect-fail", action="store_true", help="succeed only if verification fails")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)
    fixture_rel = clean_archive_path(args.fixture, "--fixture")
    try:
        result = verify_fixture(ROOT / fixture_rel, skip_parent_replay=args.skip_parent_replay)
    except Exception as exc:
        if args.expect_fail:
            payload = {"ok": True, "expected_failure_observed": True, "fixture": fixture_rel, "failure": str(exc)}
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print("streamfold-framed-receipt-lane-rev0858: expected failure observed")
            return 0
        if args.json:
            print(json.dumps({"ok": False, "fixture": fixture_rel, "error": str(exc)}, indent=2, sort_keys=True))
        else:
            print(f"streamfold-framed-receipt-lane-rev0858: FAIL: {exc}", file=sys.stderr)
        return 1
    if args.expect_fail:
        message = "fixture unexpectedly verified successfully"
        if args.json:
            print(json.dumps({"ok": False, "fixture": fixture_rel, "error": message}, indent=2, sort_keys=True))
        else:
            print(f"streamfold-framed-receipt-lane-rev0858: FAIL: {message}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("streamfold-framed-receipt-lane-rev0858: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
