#!/usr/bin/env python3
"""Verify the rev0862 streamfold archive payload search proofcore lane.

The lane proves an executable recovery surface for payload bytes that may exist in
ZIP/export artifacts.  It checks hash bindings, recomputes no-candidate absence
reports, reruns ZIP-aware synthetic controls, checks the cloudtainer negative ZIP
search receipt shape, confirms the rights block, and reconstructs/replays rev0861
unless explicitly skipped.
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

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
REVISION = "rev0862"


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
        raise LaneVerifyError(f"{field} must be a POSIX relative archive path: {text!r}")
    pure = PurePosixPath(text)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise LaneVerifyError(f"{field} must be clean and relative: {text!r}")
    return pure.as_posix()


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except Exception:
        return str(path)


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


def check_ref(obj: dict[str, Any], prefix: str, *, root: Path = ROOT) -> tuple[str, str]:
    path = clean_archive_path(obj.get(f"{prefix}_path"), f"{prefix}_path")
    expected = obj.get(f"{prefix}_sha256")
    observed = sha256_file(root / path)
    if expected != observed:
        raise LaneVerifyError(f"{prefix} hash mismatch: expected {expected}, observed {observed}")
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
    verifier_path = clean_archive_path(certificate.get("verifier", {}).get("path"), "certificate verifier path")
    if certificate.get("verifier", {}).get("sha256") != sha256_file(ROOT / verifier_path):
        raise LaneVerifyError("certificate lane verifier hash mismatch")
    proof = certificate.get("proof_system", {})
    if proof.get("snark") or proof.get("zero_knowledge") or proof.get("succinct"):
        raise LaneVerifyError("certificate must not claim SNARK/ZK/succinct")
    text = "\n".join(str(x) for x in certificate.get("non_claims") or [])
    for phrase in ["not a SNARK", "not zero knowledge", "not succinct", "not a rights grant", "does not recover missing canonical payloads"]:
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


def verify_archive_search(public_inputs: dict[str, Any]) -> dict[str, Any]:
    archive = public_inputs.get("archive_payload_search")
    if not isinstance(archive, dict):
        raise LaneVerifyError("missing archive_payload_search public input")
    for key in ["contract", "archive_locator_engine", "full_absence_report", "minimum_absence_report", "selftest_report", "cloudtainer_zip_search_receipt", "audit"]:
        check_ref(archive, key)
    contract = load_json_rel(archive.get("contract_path"), "archive search contract")
    audit = load_json_rel(archive.get("audit_path"), "archive search audit")
    if contract.get("revision") != REVISION or audit.get("revision") != REVISION:
        raise LaneVerifyError("archive search contract/audit revision mismatch")
    if contract.get("status") != "zipaware_archive_search_ready_no_payload_bytes_in_overlay":
        raise LaneVerifyError("archive search contract status drifted")
    if audit.get("status") != "zipaware_archive_search_ready_payloads_still_absent":
        raise LaneVerifyError("archive search audit status drifted")
    if archive.get("expected_full_absent_count") != 17 or archive.get("expected_minimum_absent_count") != 4:
        raise LaneVerifyError("expected payload absence counts drifted")
    engine_rel = clean_archive_path(archive.get("archive_locator_engine_path"), "archive locator engine path")
    engine = import_module_from_root(ROOT, engine_rel, "ev_rev0862_archive_payload_engine")
    recomputed: dict[str, Any] = {}
    for mode, report_key in [("full", "full_absence_report"), ("minimum", "minimum_absence_report")]:
        stored = load_json_rel(archive.get(f"{report_key}_path"), f"{mode} archive absence report")
        result = engine.locate_report([], None, mode=mode)  # type: ignore[attr-defined]
        if sha256_obj(result) != sha256_obj(stored):
            raise LaneVerifyError(f"{mode} archive absence report is not recomputable")
        if stored.get("archive_locator_status") != "blocked_waiting_for_candidate_sources":
            raise LaneVerifyError(f"{mode} absence report must wait for candidate sources")
        if stored.get("stage_created") is not False:
            raise LaneVerifyError(f"{mode} absence report must not create a stage")
        recomputed[mode] = {
            "selected_path_count": stored.get("selected_path_count"),
            "overlay_payloads_absent": stored.get("overlay_payloads_absent"),
            "archive_locator_status": stored.get("archive_locator_status"),
            "missing": stored.get("status_counts", {}).get("missing"),
        }
    selftest = load_json_rel(archive.get("selftest_report_path"), "archive search self-test report")
    selftest_result = engine.self_test()  # type: ignore[attr-defined]
    if sha256_obj(selftest_result) != sha256_obj(selftest):
        raise LaneVerifyError("archive search self-test report is not recomputable")
    if selftest.get("required_controls_passed") is not True:
        raise LaneVerifyError("archive search self-test controls did not all pass")
    controls = selftest.get("controls")
    required = [
        "directory_payload_found",
        "zip_payload_found",
        "mixed_sources_staged_to_canonical_targets",
        "duplicate_hash_ambiguous",
        "ambiguous_stage_rejected",
        "zip_symlink_entry_skipped",
        "unsafe_zip_member_skipped",
        "stage_inside_overlay_rejected",
        "stage_inside_candidate_directory_rejected",
        "partial_stage_rejected",
    ]
    if not isinstance(controls, dict) or not all(controls.get(key) is True for key in required):
        raise LaneVerifyError("archive search reject/accept controls are incomplete")
    receipt = load_json_rel(archive.get("cloudtainer_zip_search_receipt_path"), "cloudtainer ZIP search receipt")
    if receipt.get("portable_validation_required") is not False:
        raise LaneVerifyError("cloudtainer receipt must be marked non-portable")
    if receipt.get("candidate_archive_count") != archive.get("cloudtainer_candidate_archive_count"):
        raise LaneVerifyError("cloudtainer candidate archive count mismatch")
    if receipt.get("total_matches") != 0 or receipt.get("matches_found_total") != 0:
        raise LaneVerifyError("cloudtainer receipt unexpectedly found payload matches")
    if archive.get("cloudtainer_payload_match_count") != receipt.get("total_matches"):
        raise LaneVerifyError("cloudtainer payload match count mismatch")
    if receipt.get("status") != "no_streamfold_sumcheck_toy_v2_payload_bytes_found_in_visible_cloudtainer_zip_artifacts":
        raise LaneVerifyError("cloudtainer receipt status drifted")
    if len(receipt.get("source_reports") or []) != receipt.get("candidate_archive_count"):
        raise LaneVerifyError("cloudtainer receipt source report count mismatch")
    return {
        "ok": True,
        "contract_id": contract.get("contract_id"),
        "absence_reports": recomputed,
        "selftest_id": selftest.get("self_test_id"),
        "cloudtainer_zip_search": {"archives": receipt.get("candidate_archive_count"), "matches": receipt.get("total_matches")},
    }


def verify_parent_checkpoint(public_inputs: dict[str, Any], *, skip_parent_replay: bool) -> dict[str, Any]:
    parent = public_inputs.get("parent_checkpoint")
    if not isinstance(parent, dict):
        raise LaneVerifyError("missing parent checkpoint")
    if parent.get("parent_revision") != "rev0861":
        raise LaneVerifyError("parent checkpoint revision mismatch")
    if skip_parent_replay:
        return {"ok": True, "parent_revision": "rev0861", "skipped_by_explicit_operator_flag": True}
    patch_path = clean_archive_path(parent.get("reconstruction_patch_path"), "parent reconstruction patch path")
    patch_abs = ROOT / patch_path
    if patch_abs.is_symlink() or not patch_abs.is_file():
        raise LaneVerifyError(f"reconstruction patch missing: {patch_path}")
    with tempfile.TemporaryDirectory(prefix="ev-rev0861-replay-") as tmp:
        tmp_root = Path(tmp) / "parent"
        def ignore(_dirpath: str, names: list[str]):
            return {name for name in names if name in {".git", "__pycache__"}}
        shutil.copytree(ROOT, tmp_root, ignore=ignore)
        result = subprocess.run(["git", "apply", "--reverse", "--whitespace=nowarn", str(patch_abs)], cwd=tmp_root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=90)
        if result.returncode != 0:
            raise LaneVerifyError(f"parent rev0861 reconstruction reverse-patch failed: {result.stderr.strip() or result.stdout.strip()}")
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
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        parent_result = subprocess.run([sys.executable, "scripts/validate_streamfold_loose_payload_locator_rev0861.py"], cwd=tmp_root, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=90)
        output = (parent_result.stdout or "") + (parent_result.stderr or "")
        if parent_result.returncode != 0 or "streamfold-loose-payload-locator-rev0861: OK" not in output:
            raise LaneVerifyError(f"parent rev0861 validator failed: {output.strip()}")
    return {"ok": True, "parent_revision": "rev0861", "replay_strategy": "reverse_rev0862_patch_restore_cyclic_surfaces_run_rev0861_loose_locator_validator"}


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
    archive_result = verify_archive_search(public_inputs)
    parent_result = verify_parent_checkpoint(public_inputs, skip_parent_replay=skip_parent_replay)
    return {"ok": True, "fixture_id": fixture.get("fixture_id"), "claim_id": claim.get("claim_id"), "archive_payload_search": archive_result, "parent": parent_result}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify rev0862 streamfold archive-payload-search proofcore lane")
    parser.add_argument("--fixture", required=True, help="fixture JSON path relative to repository root")
    parser.add_argument("--expect-fail", action="store_true", help="succeed only if verification fails")
    parser.add_argument("--skip-parent-replay", action="store_true", help="skip parent reconstruction when explicitly requested")
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
                print("streamfold-archive-payload-search-lane-rev0862: expected failure observed")
            return 0
        if args.json:
            print(json.dumps({"ok": False, "fixture": fixture_rel, "error": str(exc), "revision": REVISION}, indent=2, sort_keys=True))
        else:
            print(f"streamfold-archive-payload-search-lane-rev0862: FAIL: {exc}", file=sys.stderr)
        return 1
    if args.expect_fail:
        message = "fixture unexpectedly verified successfully"
        if args.json:
            print(json.dumps({"ok": False, "fixture": fixture_rel, "error": message, "revision": REVISION}, indent=2, sort_keys=True))
        else:
            print(f"streamfold-archive-payload-search-lane-rev0862: FAIL: {message}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("streamfold-archive-payload-search-lane-rev0862: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
