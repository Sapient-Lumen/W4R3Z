#!/usr/bin/env python3
"""Verify the rev0856 parent-linked streamfold sumcheck transcript-binding lane.

The lane composes: rev0855 parent replay, exact missing-payload gate, deterministic
Fiat-Shamir-style toy sumcheck transcript binding, and the rights block.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REVISION = "rev0856"

class LaneVerifyError(Exception):
    pass


def sha256_file(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise LaneVerifyError(f"cannot hash non-regular file: {rel(path)}")
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
        raise LaneVerifyError(f"{field} must be a non-empty string")
    if "\x00" in text or "\\" in text:
        raise LaneVerifyError(f"{field} must be POSIX relative: {text!r}")
    pure = PurePosixPath(text)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise LaneVerifyError(f"{field} must be clean and relative: {text!r}")
    return pure.as_posix()


def clean_candidate_root(text: str | None) -> Path | None:
    if text is None:
        return None
    path = Path(text).resolve()
    if path.is_symlink() or not path.is_dir():
        raise LaneVerifyError(f"candidate root must be a real directory: {path}")
    return path


def load_json_rel(path_text: str, field: str, *, root: Path = ROOT) -> dict[str, Any]:
    rel_path = clean_archive_path(path_text, field)
    path = root / rel_path
    if path.is_symlink() or not path.is_file():
        raise LaneVerifyError(f"{field} is not a regular file: {rel_path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise LaneVerifyError(f"{field} is invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise LaneVerifyError(f"{field} must contain a JSON object")
    return data


def apply_mutation(obj: Any, pointer: str, value: Any) -> None:
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise LaneVerifyError(f"mutation path must be a JSON pointer: {pointer!r}")
    parts = [p.replace("~1", "/").replace("~0", "~") for p in pointer.strip("/").split("/")]
    current = obj
    for part in parts[:-1]:
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
        else:
            raise LaneVerifyError(f"mutation path does not exist: {pointer}")
    last = parts[-1]
    if isinstance(current, dict) and last in current:
        current[last] = value
    elif isinstance(current, list) and last.isdigit() and int(last) < len(current):
        current[int(last)] = value
    else:
        raise LaneVerifyError(f"mutation target does not exist: {pointer}")


def run_command(args: list[str], *, cwd: Path = ROOT, marker: str | None = None) -> str:
    # Do not capture nested verifier output. Parent-replay commands can spawn
    # subprocesses of their own; inherited pipes have caused validation hangs in
    # this cloudtainer. A zero exit status is the contract, while visible child
    # output gives operators progress during long parent replay.
    print(f"rev0856 lane subprocess: {' '.join(str(a) for a in args)}", file=sys.stderr, flush=True)
    result = subprocess.run(args, cwd=cwd, text=True, check=False)
    if result.returncode != 0:
        raise LaneVerifyError(f"command failed {args}: returncode={result.returncode}")
    return marker or ""


def verify_certificate(certificate: dict[str, Any], claim: dict[str, Any], public_inputs: dict[str, Any]) -> None:
    if certificate.get("certificate_type") != "transparent_public_pcd_sumcheck_fs_lane_envelope":
        raise LaneVerifyError("unsupported certificate type")
    if claim.get("revision") != REVISION or public_inputs.get("revision") != REVISION or certificate.get("revision") != REVISION:
        raise LaneVerifyError("claim/public-input/certificate revision mismatch")
    proof_system = certificate.get("proof_system")
    if not isinstance(proof_system, dict):
        raise LaneVerifyError("certificate missing proof_system")
    for forbidden in ["snark", "zero_knowledge", "succinct"]:
        if proof_system.get(forbidden):
            raise LaneVerifyError(f"certificate must not claim {forbidden}")
    for label in ["claim", "public_inputs", "commitments", "verifier", "payload_manifest", "protocol_profile", "transcript_contract", "sumcheck_fs_verifier", "payload_admission_contract"]:
        obj = certificate.get(label)
        if not isinstance(obj, dict):
            raise LaneVerifyError(f"certificate missing {label}")
        path_text = clean_archive_path(obj.get("path"), f"certificate.{label}.path")
        if obj.get("sha256") != sha256_file(ROOT / path_text):
            raise LaneVerifyError(f"certificate {label} hash mismatch")
    non_claims = "\n".join(str(x) for x in list(claim.get("non_claims") or []) + list(public_inputs.get("non_claims") or []))
    for phrase in ["not a SNARK", "not zero knowledge", "not a rights grant", "does not recover missing canonical payloads", "not a production Fiat-Shamir transform"]:
        if phrase.lower() not in non_claims.lower():
            raise LaneVerifyError(f"required non-claim phrase missing: {phrase}")


def verify_rights(public_inputs: dict[str, Any]) -> None:
    exp = public_inputs.get("rights_expectation")
    if not isinstance(exp, dict):
        raise LaneVerifyError("missing rights_expectation")
    ledger_path = clean_archive_path(exp.get("ledger_path"), "rights_expectation.ledger_path")
    ledger = load_json_rel(ledger_path, "rights ledger")
    if ledger.get("status") != exp.get("status"):
        raise LaneVerifyError("rights status mismatch")
    for sentinel in exp.get("forbidden_root_sentinels") or []:
        sent = clean_archive_path(sentinel, "forbidden root sentinel")
        if (ROOT / sent).exists():
            raise LaneVerifyError(f"forbidden root rights sentinel exists: {sent}")


def verify_parent_checkpoint(public_inputs: dict[str, Any]) -> dict[str, Any]:
    parent = public_inputs.get("parent_checkpoint")
    if not isinstance(parent, dict):
        raise LaneVerifyError("missing parent_checkpoint")
    patch_path = clean_archive_path(parent.get("reconstruction_patch_path"), "parent.reconstruction_patch_path")
    patch_abs = ROOT / patch_path
    if patch_abs.is_symlink() or not patch_abs.is_file():
        raise LaneVerifyError(f"reconstruction patch missing: {patch_path}")
    with tempfile.TemporaryDirectory(prefix="ev-rev0855-replay-") as tmp:
        tmp_root = Path(tmp) / "parent"
        def ignore(dirpath: str, names: list[str]):
            return {name for name in names if name in {".git", "__pycache__"}}
        shutil.copytree(ROOT, tmp_root, ignore=ignore)
        result = subprocess.run(["git", "apply", "--reverse", "--whitespace=nowarn", str(patch_abs)], cwd=tmp_root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if result.returncode != 0:
            raise LaneVerifyError(f"parent rev0855 reconstruction reverse-patch failed: {result.stderr.strip() or result.stdout.strip()}")
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
        run_command([sys.executable, verifier_path, "--fixture", fixture_path], cwd=tmp_root, marker="streamfold-sumcheck-lane-rev0855: OK")
    return {"parent_revision": parent.get("parent_revision"), "ok": True, "marker": "streamfold-sumcheck-lane-rev0855: OK"}


def load_index_rows() -> dict[str, dict[str, str]]:
    with (ROOT / "INDEX/files.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return {row.get("path", ""): row for row in rows}


def verify_payload_gate(public_inputs: dict[str, Any], candidate_root: Path | None = None) -> dict[str, Any]:
    gate = public_inputs.get("payload_gate")
    if not isinstance(gate, dict):
        raise LaneVerifyError("missing payload_gate")
    manifest_path = clean_archive_path(gate.get("manifest_path"), "payload_gate.manifest_path")
    if gate.get("manifest_sha256") != sha256_file(ROOT / manifest_path):
        raise LaneVerifyError("payload manifest hash mismatch")
    manifest = load_json_rel(manifest_path, "payload manifest")
    if manifest.get("source_group_id") != gate.get("source_group_id"):
        raise LaneVerifyError("payload group id mismatch")
    if manifest.get("status") != gate.get("status"):
        raise LaneVerifyError("payload status mismatch")
    payloads = manifest.get("expected_payloads")
    if not isinstance(payloads, list) or not payloads:
        raise LaneVerifyError("payload manifest expected_payloads must be non-empty")
    if len(payloads) != gate.get("expected_path_count"):
        raise LaneVerifyError("payload expected path count mismatch")
    index = load_index_rows()
    seen: set[str] = set()
    role_counts: dict[str, int] = {}
    missing_in_overlay = 0
    present_in_candidate = 0
    candidate_mismatches: list[str] = []
    for item in payloads:
        if not isinstance(item, dict):
            raise LaneVerifyError("payload item must be an object")
        path_text = clean_archive_path(item.get("path"), "payload path")
        if path_text in seen:
            raise LaneVerifyError(f"duplicate payload path: {path_text}")
        seen.add(path_text)
        row = index.get(path_text)
        if row is None:
            raise LaneVerifyError(f"payload path absent from INDEX/files.csv: {path_text}")
        expected_sha = str(item.get("sha256"))
        expected_bytes = int(item.get("bytes"))
        if row.get("sha256") != expected_sha or int(row.get("size") or 0) != expected_bytes:
            raise LaneVerifyError(f"payload index mismatch: {path_text}")
        role = str(item.get("role") or "unknown")
        role_counts[role] = role_counts.get(role, 0) + 1
        overlay_path = ROOT / path_text
        if overlay_path.exists():
            raise LaneVerifyError(f"payload unexpectedly present inside overlay bundle: {path_text}")
        missing_in_overlay += 1
        if candidate_root is not None:
            candidate_path = candidate_root / path_text
            if candidate_path.is_symlink() or not candidate_path.is_file():
                candidate_mismatches.append(f"missing:{path_text}")
            else:
                present_in_candidate += 1
                if candidate_path.stat().st_size != expected_bytes or sha256_file(candidate_path) != expected_sha:
                    candidate_mismatches.append(f"hash-or-size:{path_text}")
    for role in gate.get("required_roles") or []:
        if role not in role_counts:
            raise LaneVerifyError(f"payload gate lacks required role {role}")
    if missing_in_overlay != gate.get("expected_missing_in_overlay"):
        raise LaneVerifyError("payload missing-in-overlay count mismatch")
    if candidate_root is not None and candidate_mismatches:
        shown = ", ".join(candidate_mismatches[:10])
        raise LaneVerifyError(f"candidate root does not satisfy payload gate: {shown}")
    return {"payloads": len(payloads), "missing_in_overlay": missing_in_overlay, "candidate_root_checked": candidate_root is not None, "present_in_candidate": present_in_candidate, "role_counts": dict(sorted(role_counts.items()))}


def verify_fs_harness(public_inputs: dict[str, Any]) -> dict[str, Any]:
    harness = public_inputs.get("fs_sumcheck_harness")
    if not isinstance(harness, dict):
        raise LaneVerifyError("missing fs_sumcheck_harness")
    for label in ["protocol_profile", "transcript_contract", "verifier", "accept_fixture", "reject_bad_challenge_fixture", "reject_omit_payload_binding_fixture", "payload_admission_contract"]:
        path_key = f"{label}_path" if label in {"protocol_profile", "transcript_contract", "payload_admission_contract"} else label
        # verifier/fixture fields already store paths under their own key names.
    protocol_profile = clean_archive_path(harness.get("protocol_profile_path"), "fs_sumcheck_harness.protocol_profile_path")
    transcript_contract = clean_archive_path(harness.get("transcript_contract_path"), "fs_sumcheck_harness.transcript_contract_path")
    verifier = clean_archive_path(harness.get("verifier_path"), "fs_sumcheck_harness.verifier_path")
    admission = clean_archive_path(harness.get("payload_admission_contract_path"), "fs_sumcheck_harness.payload_admission_contract_path")
    if harness.get("protocol_profile_sha256") != sha256_file(ROOT / protocol_profile):
        raise LaneVerifyError("protocol profile hash mismatch")
    if harness.get("transcript_contract_sha256") != sha256_file(ROOT / transcript_contract):
        raise LaneVerifyError("transcript contract hash mismatch")
    if harness.get("verifier_sha256") != sha256_file(ROOT / verifier):
        raise LaneVerifyError("FS sumcheck verifier hash mismatch")
    if harness.get("payload_admission_contract_sha256") != sha256_file(ROOT / admission):
        raise LaneVerifyError("payload admission contract hash mismatch")
    accept = clean_archive_path(harness.get("accept_fixture"), "fs_sumcheck_harness.accept_fixture")
    reject_challenge = clean_archive_path(harness.get("reject_bad_challenge_fixture"), "fs_sumcheck_harness.reject_bad_challenge_fixture")
    reject_omit = clean_archive_path(harness.get("reject_omit_payload_binding_fixture"), "fs_sumcheck_harness.reject_omit_payload_binding_fixture")
    if harness.get("accept_fixture_sha256") != sha256_file(ROOT / accept):
        raise LaneVerifyError("FS accept fixture hash mismatch")
    if harness.get("reject_bad_challenge_fixture_sha256") != sha256_file(ROOT / reject_challenge):
        raise LaneVerifyError("FS reject-bad-challenge fixture hash mismatch")
    if harness.get("reject_omit_payload_binding_fixture_sha256") != sha256_file(ROOT / reject_omit):
        raise LaneVerifyError("FS reject-omit-binding fixture hash mismatch")
    run_command([sys.executable, verifier, "--fixture", accept], marker="sumcheck-fs-transcript-rev0856: OK")
    run_command([sys.executable, verifier, "--fixture", reject_challenge, "--expect-fail"], marker="sumcheck-fs-transcript-rev0856: expected failure observed")
    run_command([sys.executable, verifier, "--fixture", reject_omit, "--expect-fail"], marker="sumcheck-fs-transcript-rev0856: expected failure observed")
    return {"accept_fixture": accept, "reject_fixtures": [reject_challenge, reject_omit], "ok": True}


def verify_fixture(fixture_path: Path, candidate_root: Path | None = None, *, skip_parent_replay: bool = False) -> dict[str, Any]:
    fixture = load_json_rel(rel(fixture_path), "fixture")
    claim = load_json_rel(fixture.get("claim_path"), "fixture.claim_path")
    public_inputs = load_json_rel(fixture.get("public_inputs_path"), "fixture.public_inputs_path")
    certificate = load_json_rel(fixture.get("certificate_path"), "fixture.certificate_path")
    for mutation in fixture.get("mutations") or []:
        if not isinstance(mutation, dict) or mutation.get("target") != "public_inputs":
            raise LaneVerifyError("only public_inputs fixture mutations are supported")
        if mutation.get("op") != "replace":
            raise LaneVerifyError("only replace mutations are supported")
        apply_mutation(public_inputs, mutation.get("path"), mutation.get("value"))
    verify_certificate(certificate, claim, public_inputs)
    verify_rights(public_inputs)
    # Check the new rev0856 transcript-binding surface before the expensive
    # parent replay.  Accept fixtures still replay the parent; reject fixtures
    # that tamper the new surface fail quickly and specifically.
    payload_result = verify_payload_gate(public_inputs, candidate_root=candidate_root)
    harness_result = verify_fs_harness(public_inputs)
    if skip_parent_replay:
        parent_result = {"ok": True, "parent_revision": public_inputs.get("parent_checkpoint", {}).get("parent_revision"), "skipped_by_explicit_operator_flag": True}
    else:
        parent_result = verify_parent_checkpoint(public_inputs)
    return {"ok": True, "fixture_id": fixture.get("fixture_id"), "claim_id": claim.get("claim_id"), "parent": parent_result, "payload_gate": payload_result, "fs_sumcheck_harness": harness_result}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify EvidenceVault rev0856 streamfold sumcheck transcript-binding lane")
    parser.add_argument("--fixture", required=True, help="fixture JSON path relative to repository root")
    parser.add_argument("--candidate-root", help="optional full canonical tree root to check against payload manifest")
    parser.add_argument("--skip-parent-replay", action="store_true", help="validate current rev0856 surfaces without replaying the rev0855 parent; for fast local validators only")
    parser.add_argument("--expect-fail", action="store_true", help="succeed only if verification fails")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)
    fixture_rel = clean_archive_path(args.fixture, "--fixture")
    try:
        candidate_root = clean_candidate_root(args.candidate_root)
        result = verify_fixture(ROOT / fixture_rel, candidate_root=candidate_root, skip_parent_replay=args.skip_parent_replay)
    except Exception as exc:
        if args.expect_fail:
            payload = {"ok": True, "expected_failure_observed": True, "fixture": fixture_rel, "failure": str(exc)}
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print("streamfold-sumcheck-fs-lane-rev0856: expected failure observed")
            return 0
        if args.json:
            print(json.dumps({"ok": False, "fixture": fixture_rel, "error": str(exc)}, indent=2, sort_keys=True))
        else:
            print(f"streamfold-sumcheck-fs-lane-rev0856: FAIL: {exc}", file=sys.stderr)
        return 1
    if args.expect_fail:
        message = "fixture unexpectedly verified successfully"
        if args.json:
            print(json.dumps({"ok": False, "fixture": fixture_rel, "error": message}, indent=2, sort_keys=True))
        else:
            print(f"streamfold-sumcheck-fs-lane-rev0856: FAIL: {message}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("streamfold-sumcheck-fs-lane-rev0856: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
