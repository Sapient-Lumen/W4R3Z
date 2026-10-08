#!/usr/bin/env python3
"""Verify the rev0857 streamfold payload-admission and transcript-prefix PCD lane.

This parent-linked transparent verifier replays the rev0856 checkpoint, verifies
that canonical payload admission has become an executable candidate-root check,
and runs the stricter prefix-bound sumcheck transcript fixtures.  It remains a
PCD-shaped audit harness, not a SNARK, not zero knowledge, not succinct, and not
a rights grant.
"""
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
REVISION = "rev0857"


class LaneVerifyError(Exception):
    pass


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


def clean_candidate_root(text: str | None) -> Path | None:
    if text is None:
        return None
    candidate = Path(text).expanduser().resolve(strict=False)
    if candidate.is_symlink() or not candidate.is_dir():
        raise LaneVerifyError(f"candidate root must be a real directory: {text}")
    return candidate


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


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
        raise LaneVerifyError(f"{field} must be a JSON object")
    return data


def apply_mutation(obj: Any, pointer: str, value: Any) -> None:
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise LaneVerifyError("mutation path must be a JSON pointer")
    parts = [part.replace("~1", "/").replace("~0", "~") for part in pointer.strip("/").split("/") if part]
    target = obj
    for part in parts[:-1]:
        if isinstance(target, dict) and part in target:
            target = target[part]
        else:
            raise LaneVerifyError(f"mutation path not found: {pointer}")
    if not parts:
        raise LaneVerifyError("refusing to replace whole object")
    last = parts[-1]
    if not isinstance(target, dict) or last not in target:
        raise LaneVerifyError(f"mutation target not found: {pointer}")
    target[last] = value


def run_command(args: list[str], *, cwd: Path = ROOT, marker: str | None = None) -> str:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(args, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0:
        raise LaneVerifyError(f"command failed {args}: {output.strip()}")
    if marker and marker not in output:
        raise LaneVerifyError(f"command output missing marker {marker!r}: {output.strip()}")
    return output


def run_command_inherited(args: list[str], *, cwd: Path = ROOT, marker: str | None = None) -> str:
    """Run nested parent-replay commands without pipe capture.

    The rev0856 verifier intentionally lets its own child verifiers inherit
    terminal streams. Capturing that verifier again from rev0857 can leave
    nested descriptors open long enough to look like a hang in this cloudtainer.
    For the parent checkpoint, zero exit status is the contract; visible output
    gives operators progress.
    """
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(args, cwd=cwd, env=env, text=True, check=False)
    if result.returncode != 0:
        raise LaneVerifyError(f"command failed {args}: returncode={result.returncode}")
    return marker or ""


def verify_certificate(certificate: dict[str, Any], claim: dict[str, Any], public_inputs: dict[str, Any], commitments: dict[str, Any]) -> None:
    if claim.get("revision") != REVISION or public_inputs.get("revision") != REVISION or certificate.get("revision") != REVISION or commitments.get("revision") != REVISION:
        raise LaneVerifyError("claim/public_inputs/commitments/certificate revision mismatch")
    if certificate.get("claim", {}).get("sha256") != sha256_file(ROOT / clean_archive_path(certificate.get("claim", {}).get("path"), "certificate.claim.path")):
        raise LaneVerifyError("certificate claim hash mismatch")
    for label in ["public_inputs", "commitments", "verifier", "payload_candidate_verifier", "transcript_prefix_verifier", "payload_manifest", "payload_admission_contract", "transcript_prefix_contract", "protocol_profile"]:
        obj = certificate.get(label)
        if not isinstance(obj, dict):
            raise LaneVerifyError(f"certificate missing {label}")
        path_text = clean_archive_path(obj.get("path"), f"certificate.{label}.path")
        if obj.get("sha256") != sha256_file(ROOT / path_text):
            raise LaneVerifyError(f"certificate {label} hash mismatch")
    proof_system = certificate.get("proof_system")
    if not isinstance(proof_system, dict):
        raise LaneVerifyError("certificate missing proof_system")
    for forbidden in ["snark", "zero_knowledge", "succinct"]:
        if proof_system.get(forbidden):
            raise LaneVerifyError(f"certificate must not claim {forbidden}")
    non_claims = "\n".join(str(x) for x in list(claim.get("non_claims") or []) + list(public_inputs.get("non_claims") or []) + list(certificate.get("non_claims") or []))
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
    with tempfile.TemporaryDirectory(prefix="ev-rev0856-replay-") as tmp:
        tmp_root = Path(tmp) / "parent"
        def ignore(_dirpath: str, names: list[str]):
            return {name for name in names if name in {".git", "__pycache__"}}
        shutil.copytree(ROOT, tmp_root, ignore=ignore)
        result = subprocess.run(["git", "apply", "--reverse", "--whitespace=nowarn", str(patch_abs)], cwd=tmp_root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if result.returncode != 0:
            raise LaneVerifyError(f"parent rev0856 reconstruction reverse-patch failed: {result.stderr.strip() or result.stdout.strip()}")
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
        run_command_inherited([sys.executable, verifier_path, "--fixture", fixture_path, "--skip-parent-replay"], cwd=tmp_root, marker="streamfold-sumcheck-fs-lane-rev0856: OK")
    return {"parent_revision": parent.get("parent_revision"), "ok": True, "marker": "streamfold-sumcheck-fs-lane-rev0856: OK"}


def verify_payload_admission(public_inputs: dict[str, Any], candidate_root: Path | None, mode: str) -> dict[str, Any]:
    payload = public_inputs.get("payload_admission")
    if not isinstance(payload, dict):
        raise LaneVerifyError("missing payload_admission")
    for label in ["manifest", "contract", "verifier"]:
        path = clean_archive_path(payload.get(f"{label}_path"), f"payload_admission.{label}_path")
        if payload.get(f"{label}_sha256") != sha256_file(ROOT / path):
            raise LaneVerifyError(f"payload admission {label} hash mismatch")
    if payload.get("expected_path_count") != 17 or payload.get("expected_missing_in_overlay") != 17:
        raise LaneVerifyError("payload admission expected counts drifted")
    verifier = clean_archive_path(payload.get("verifier_path"), "payload_admission.verifier_path")
    command = [sys.executable, verifier, "--mode", mode]
    if candidate_root is not None:
        command += ["--candidate-root", str(candidate_root)]
    output = run_command(command, marker="streamfold-payload-candidate-rev0857: OK")
    return {"ok": True, "mode": mode, "candidate_root_checked": candidate_root is not None, "command_output": output.strip().splitlines()[-1] if output.strip() else ""}


def verify_transcript_prefix_harness(public_inputs: dict[str, Any]) -> dict[str, Any]:
    harness = public_inputs.get("transcript_prefix_harness")
    if not isinstance(harness, dict):
        raise LaneVerifyError("missing transcript_prefix_harness")
    for label in ["contract", "protocol_profile", "verifier", "accept_fixture", "reject_bad_prefix_fixture", "reject_contract_tamper_fixture"]:
        path = clean_archive_path(harness.get(f"{label}_path"), f"transcript_prefix_harness.{label}_path")
        if harness.get(f"{label}_sha256") != sha256_file(ROOT / path):
            raise LaneVerifyError(f"transcript prefix {label} hash mismatch")
    verifier = clean_archive_path(harness.get("verifier_path"), "transcript_prefix_harness.verifier_path")
    accept = clean_archive_path(harness.get("accept_fixture_path"), "transcript_prefix_harness.accept_fixture_path")
    reject_bad_prefix = clean_archive_path(harness.get("reject_bad_prefix_fixture_path"), "transcript_prefix_harness.reject_bad_prefix_fixture_path")
    reject_contract_tamper = clean_archive_path(harness.get("reject_contract_tamper_fixture_path"), "transcript_prefix_harness.reject_contract_tamper_fixture_path")
    run_command([sys.executable, verifier, "--fixture", accept], marker="sumcheck-fs-prefix-transcript-rev0857: OK")
    run_command([sys.executable, verifier, "--fixture", reject_bad_prefix, "--expect-fail"], marker="sumcheck-fs-prefix-transcript-rev0857: expected failure observed")
    run_command([sys.executable, verifier, "--fixture", reject_contract_tamper, "--expect-fail"], marker="sumcheck-fs-prefix-transcript-rev0857: expected failure observed")
    return {"ok": True, "accept_fixture": accept, "reject_fixtures": [reject_bad_prefix, reject_contract_tamper], "derived_accept_challenges": harness.get("derived_accept_challenges")}


def verify_fixture(fixture_path: Path, candidate_root: Path | None = None, *, mode: str = "full", skip_parent_replay: bool = False) -> dict[str, Any]:
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
    payload_result = verify_payload_admission(public_inputs, candidate_root, mode)
    transcript_result = verify_transcript_prefix_harness(public_inputs)
    if skip_parent_replay:
        parent_result = {"ok": True, "parent_revision": public_inputs.get("parent_checkpoint", {}).get("parent_revision"), "skipped_by_explicit_operator_flag": True}
    else:
        parent_result = verify_parent_checkpoint(public_inputs)
    return {"ok": True, "fixture_id": fixture.get("fixture_id"), "claim_id": claim.get("claim_id"), "parent": parent_result, "payload_admission": payload_result, "transcript_prefix_harness": transcript_result}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify EvidenceVault rev0857 streamfold payload-admission/transcript-prefix lane")
    parser.add_argument("--fixture", required=True, help="fixture JSON path relative to repository root")
    parser.add_argument("--candidate-root", help="optional full canonical/candidate tree root to check against the payload manifest")
    parser.add_argument("--mode", choices=["full", "minimum"], default="full", help="payload-admission mode for candidate roots")
    parser.add_argument("--skip-parent-replay", action="store_true", help="validate current rev0857 surfaces without replaying rev0856 parent; for fast local validators only")
    parser.add_argument("--expect-fail", action="store_true", help="succeed only if verification fails")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)
    fixture_rel = clean_archive_path(args.fixture, "--fixture")
    try:
        candidate_root = clean_candidate_root(args.candidate_root)
        result = verify_fixture(ROOT / fixture_rel, candidate_root=candidate_root, mode=args.mode, skip_parent_replay=args.skip_parent_replay)
    except Exception as exc:
        if args.expect_fail:
            payload = {"ok": True, "expected_failure_observed": True, "fixture": fixture_rel, "failure": str(exc)}
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print("streamfold-payload-admission-lane-rev0857: expected failure observed")
            return 0
        if args.json:
            print(json.dumps({"ok": False, "fixture": fixture_rel, "error": str(exc)}, indent=2, sort_keys=True))
        else:
            print(f"streamfold-payload-admission-lane-rev0857: FAIL: {exc}", file=sys.stderr)
        return 1
    if args.expect_fail:
        message = "fixture unexpectedly verified successfully"
        if args.json:
            print(json.dumps({"ok": False, "fixture": fixture_rel, "error": message}, indent=2, sort_keys=True))
        else:
            print(f"streamfold-payload-admission-lane-rev0857: FAIL: {message}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("streamfold-payload-admission-lane-rev0857: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
