#!/usr/bin/env python3
"""Verify EvidenceVault rev0854 proofcore-frontier transparent PCD envelope.

This verifier composes two concrete checks:
1. Reconstruct and re-run the rev0853 transparent PCD checkpoint by reversing the
   rev0853->rev0854 overlay patch and restoring cyclic parent surfaces from
   carried snapshots.
2. Recompute the rev0854 proof-obligation frontier from the canonical path-role
   map and check that it selects concrete P0 proofcore completion lanes.

It is not a SNARK verifier and does not prove protocol soundness.
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
REVISION = "rev0854"

class FrontierVerifyError(Exception):
    pass

ROLE_WEIGHT = {
    "verifier_code": 5,
    "witness_or_witness_policy": 5,
    "public_input_or_commitment": 4,
    "abi_ir_or_protocol_ir": 4,
    "attestation_or_receipt": 3,
    "accept_fixture": 2,
    "reject_fixture": 2,
    "schema": 2,
    "governance_or_rights": 2,
    "paper_or_render": 1,
    "source": 1,
    "unknown": 1,
}


def sha256_file(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise FrontierVerifyError(f"cannot hash non-regular file: {rel(path)}")
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj)).hexdigest()


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def clean_archive_path(text: Any, field: str) -> str:
    if not isinstance(text, str) or not text:
        raise FrontierVerifyError(f"{field} must be a non-empty string")
    if "\x00" in text or "\\" in text:
        raise FrontierVerifyError(f"{field} must be POSIX relative: {text!r}")
    pure = PurePosixPath(text)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise FrontierVerifyError(f"{field} must be clean and relative: {text!r}")
    return pure.as_posix()


def load_json_rel(path_text: str, field: str, *, root: Path = ROOT) -> dict[str, Any]:
    rel_path = clean_archive_path(path_text, field)
    path = root / rel_path
    if path.is_symlink() or not path.is_file():
        raise FrontierVerifyError(f"{field} is not a regular file: {rel_path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise FrontierVerifyError(f"{field} is invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise FrontierVerifyError(f"{field} must contain a JSON object")
    return data


def apply_mutation(obj: Any, pointer: str, value: Any) -> None:
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise FrontierVerifyError(f"mutation path must be a JSON pointer: {pointer!r}")
    parts = [p.replace("~1", "/").replace("~0", "~") for p in pointer.strip("/").split("/")]
    current = obj
    for part in parts[:-1]:
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
        else:
            raise FrontierVerifyError(f"mutation path does not exist: {pointer}")
    last = parts[-1]
    if isinstance(current, dict) and last in current:
        current[last] = value
    elif isinstance(current, list) and last.isdigit() and int(last) < len(current):
        current[int(last)] = value
    else:
        raise FrontierVerifyError(f"mutation target does not exist: {pointer}")


def verify_certificate(certificate: dict[str, Any], claim: dict[str, Any], public_inputs: dict[str, Any]) -> None:
    if certificate.get("certificate_type") != "transparent_public_pcd_frontier_envelope":
        raise FrontierVerifyError("unsupported certificate type")
    proof_system = certificate.get("proof_system")
    if not isinstance(proof_system, dict):
        raise FrontierVerifyError("missing proof_system")
    if proof_system.get("snark") or proof_system.get("zero_knowledge") or proof_system.get("succinct"):
        raise FrontierVerifyError("frontier lane cannot claim SNARK/ZK/succinct properties")
    if claim.get("revision") != REVISION or public_inputs.get("revision") != REVISION or certificate.get("revision") != REVISION:
        raise FrontierVerifyError("claim/public-input/certificate revision mismatch")
    for label, obj in [
        ("claim", certificate.get("claim")),
        ("public_inputs", certificate.get("public_inputs")),
        ("commitments", certificate.get("commitments")),
        ("verifier", certificate.get("verifier")),
    ]:
        if not isinstance(obj, dict):
            raise FrontierVerifyError(f"certificate missing {label}")
        path_text = clean_archive_path(obj.get("path"), f"certificate.{label}.path")
        if obj.get("sha256") != sha256_file(ROOT / path_text):
            raise FrontierVerifyError(f"certificate {label} hash mismatch")
    non_claims = "\n".join(str(x) for x in list(claim.get("non_claims") or []) + list(public_inputs.get("non_claims") or []))
    for phrase in ["not a zk-SNARK", "not zero knowledge", "not a publication rights grant"]:
        if phrase.lower() not in non_claims.lower():
            raise FrontierVerifyError(f"required non-claim phrase missing: {phrase}")


def verify_rights(public_inputs: dict[str, Any]) -> None:
    exp = public_inputs.get("rights_expectation")
    if not isinstance(exp, dict):
        raise FrontierVerifyError("missing rights_expectation")
    ledger_path = clean_archive_path(exp.get("ledger_path"), "rights_expectation.ledger_path")
    ledger = load_json_rel(ledger_path, "rights ledger")
    if ledger.get("status") != exp.get("status"):
        raise FrontierVerifyError("rights status mismatch")
    for sentinel in exp.get("forbidden_root_sentinels") or []:
        sent = clean_archive_path(sentinel, "forbidden root sentinel")
        if (ROOT / sent).exists():
            raise FrontierVerifyError(f"forbidden root rights sentinel exists: {sent}")


def verify_parent_checkpoint(public_inputs: dict[str, Any]) -> dict[str, Any]:
    parent = public_inputs.get("parent_checkpoint")
    if not isinstance(parent, dict):
        raise FrontierVerifyError("missing parent_checkpoint")
    patch_path = clean_archive_path(parent.get("reconstruction_patch_path"), "parent.reconstruction_patch_path")
    patch_abs = ROOT / patch_path
    if patch_abs.is_symlink() or not patch_abs.is_file():
        raise FrontierVerifyError(f"reconstruction patch missing: {patch_path}")
    # Hash is deliberately not inside this public input because the patch contains this public input.
    # The outer overlay-integrity validator checks CHECKS/patches.sha256.
    with tempfile.TemporaryDirectory(prefix="ev-parent-replay-") as tmp:
        tmp_root = Path(tmp) / "parent"
        def ignore(dirpath: str, names: list[str]):
            return {name for name in names if name in {".git", "__pycache__"}}
        shutil.copytree(ROOT, tmp_root, ignore=ignore)
        result = subprocess.run(
            ["git", "apply", "--reverse", "--whitespace=nowarn", str(patch_abs)],
            cwd=tmp_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            raise FrontierVerifyError(f"parent reconstruction reverse-patch failed: {result.stderr.strip() or result.stdout.strip()}")
        # The rev0854 overlay patch is intentionally not a self-diff, because a
        # patch that contains its own hash is cyclic. Remove it explicitly so the
        # reconstructed parent file set can match the rev0853 overlay manifest.
        reconstructed_patch = tmp_root / patch_path
        if reconstructed_patch.exists():
            if reconstructed_patch.is_symlink() or not reconstructed_patch.is_file():
                raise FrontierVerifyError(f"reconstructed patch path is not a removable regular file: {patch_path}")
            reconstructed_patch.unlink()
        for item in parent.get("cyclic_surface_snapshots") or []:
            if not isinstance(item, dict):
                raise FrontierVerifyError("parent snapshot item must be an object")
            snapshot = clean_archive_path(item.get("snapshot_path"), "parent snapshot path")
            destination = clean_archive_path(item.get("destination"), "parent snapshot destination")
            snap_abs = ROOT / snapshot
            if item.get("sha256") != sha256_file(snap_abs):
                raise FrontierVerifyError(f"parent snapshot hash mismatch: {snapshot}")
            dest_abs = tmp_root / destination
            dest_abs.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(snap_abs, dest_abs)
        verifier_path = clean_archive_path(parent.get("parent_verifier_path"), "parent verifier path")
        fixture_path = clean_archive_path(parent.get("parent_accept_fixture"), "parent accept fixture")
        parent_cmd = [sys.executable, verifier_path, "--fixture", fixture_path]
        result = subprocess.run(parent_cmd, cwd=tmp_root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if result.returncode != 0:
            raise FrontierVerifyError(f"parent rev0853 PCD checkpoint failed: stdout={result.stdout!r} stderr={result.stderr!r}")
        if "pcd-envelope-rev0853: OK" not in ((result.stdout or "") + (result.stderr or "")):
            raise FrontierVerifyError("parent rev0853 PCD checkpoint did not emit expected OK marker")
    return {"parent_revision": parent.get("parent_revision"), "ok": True}


def filter_rows(rows: list[dict[str, str]], selector: dict[str, Any]) -> list[dict[str, str]]:
    all_terms = [str(t).lower() for t in selector.get("all_contains") or []]
    any_terms = [str(t).lower() for t in selector.get("any_contains") or []]
    out: list[dict[str, str]] = []
    for row in rows:
        path = (row.get("path") or "").lower()
        if row.get("operator_priority") != "P0":
            continue
        if all(term in path for term in all_terms) and (not any_terms or any(term in path for term in any_terms)):
            out.append(row)
    out.sort(key=lambda row: row.get("path") or "")
    return out


def summarize_group(spec: dict[str, Any], rows: list[dict[str, str]]) -> dict[str, Any]:
    role_counts: dict[str, int] = {}
    priority_counts: dict[str, int] = {}
    component_counts: dict[str, int] = {}
    path_records = []
    total_bytes = 0
    risk_score = 0
    for row in rows:
        role = row.get("role") or "unknown"
        role_counts[role] = role_counts.get(role, 0) + 1
        pri = row.get("operator_priority") or ""
        priority_counts[pri] = priority_counts.get(pri, 0) + 1
        comp = row.get("rights_component_guess") or "unassigned"
        component_counts[comp] = component_counts.get(comp, 0) + 1
        try:
            b = int(row.get("size") or 0)
        except ValueError:
            b = 0
        total_bytes += b
        risk_score += ROLE_WEIGHT.get(role, 1)
        path_records.append({
            "path": row.get("path"),
            "role": role,
            "sha256": row.get("sha256"),
            "bytes": b,
            "present_in_overlay": row.get("present_in_overlay"),
            "operator_priority": pri,
            "rights_component_guess": row.get("rights_component_guess") or "",
        })
    component = spec.get("component")
    if component in {"streamfold", "zkrtp"}:
        risk_score += 10
    if {"abi_ir_or_protocol_ir", "public_input_or_commitment", "attestation_or_receipt"} <= set(role_counts):
        risk_score += 8
    group = {
        "group_id": spec.get("group_id"),
        "component": component,
        "focus": spec.get("focus"),
        "selector": spec.get("selector"),
        "path_count": len(rows),
        "total_bytes": total_bytes,
        "role_counts": dict(sorted(role_counts.items())),
        "priority_counts": dict(sorted(priority_counts.items())),
        "rights_component_guess_counts": dict(sorted(component_counts.items())),
        "risk_score": risk_score,
        "all_present_in_overlay_false": all(row.get("present_in_overlay") == "false" for row in rows),
        "closure_gate": spec.get("closure_gate"),
        "why_p0": spec.get("why_p0"),
        "recommended_next": bool(spec.get("recommended_next", False)),
        "paths": path_records,
    }
    group["group_sha256"] = sha256_obj({k: v for k, v in group.items() if k != "group_sha256"})
    return group


def verify_frontier(public_inputs: dict[str, Any]) -> dict[str, Any]:
    exp = public_inputs.get("frontier_expectation")
    if not isinstance(exp, dict):
        raise FrontierVerifyError("missing frontier_expectation")
    map_path = clean_archive_path(exp.get("source_map_path"), "frontier.source_map_path")
    if exp.get("source_map_sha256") != sha256_file(ROOT / map_path):
        raise FrontierVerifyError("source map sha mismatch")
    frontier_json_path = clean_archive_path(exp.get("frontier_json_path"), "frontier.frontier_json_path")
    frontier_csv_path = clean_archive_path(exp.get("frontier_csv_path"), "frontier.frontier_csv_path")
    if exp.get("frontier_json_sha256") != sha256_file(ROOT / frontier_json_path):
        raise FrontierVerifyError("frontier JSON sha mismatch")
    if exp.get("frontier_csv_sha256") != sha256_file(ROOT / frontier_csv_path):
        raise FrontierVerifyError("frontier CSV sha mismatch")
    frontier = load_json_rel(frontier_json_path, "frontier JSON")
    with (ROOT / map_path).open(newline="", encoding="utf-8") as f:
        map_rows = list(csv.DictReader(f))
    with (ROOT / frontier_csv_path).open(newline="", encoding="utf-8") as f:
        csv_rows = list(csv.DictReader(f))
    expected_groups = exp.get("expected_groups")
    if not isinstance(expected_groups, list) or not expected_groups:
        raise FrontierVerifyError("frontier expected_groups must be non-empty")
    derived_groups = []
    selected_paths: set[str] = set()
    for spec in expected_groups:
        if not isinstance(spec, dict):
            raise FrontierVerifyError("frontier expected group must be an object")
        group_rows = filter_rows(map_rows, spec.get("selector") or {})
        group = summarize_group(spec, group_rows)
        derived_groups.append(group)
        selected_paths.update(str(item.get("path")) for item in group["paths"])
        if group["path_count"] < int(spec.get("minimum_paths", 1)):
            raise FrontierVerifyError(f"frontier group too small: {group['group_id']}")
        for role in spec.get("required_roles") or []:
            if role not in group["role_counts"]:
                raise FrontierVerifyError(f"frontier group {group['group_id']} missing required role {role}")
        if not group["all_present_in_overlay_false"]:
            raise FrontierVerifyError(f"frontier group {group['group_id']} unexpectedly present in overlay")
        for item in group["paths"]:
            rel_path = item.get("path")
            if isinstance(rel_path, str) and (ROOT / rel_path).exists():
                raise FrontierVerifyError(f"frontier payload unexpectedly present in overlay: {rel_path}")
    if len(derived_groups) != exp.get("selected_group_count"):
        raise FrontierVerifyError("selected_group_count mismatch")
    if len(selected_paths) != exp.get("selected_unique_path_count"):
        raise FrontierVerifyError("selected_unique_path_count mismatch")
    # Compare against recorded JSON group summaries without reusing the recorded values as source of truth.
    recorded_groups = frontier.get("groups")
    if recorded_groups != derived_groups:
        raise FrontierVerifyError("recorded frontier groups do not match recomputed groups")
    recorded_csv = [
        {k: row.get(k, "") for k in ["group_id", "path", "role", "sha256", "bytes", "present_in_overlay", "operator_priority", "rights_component_guess"]}
        for row in csv_rows
    ]
    expected_csv = []
    for group in derived_groups:
        for item in group["paths"]:
            expected_csv.append({
                "group_id": group["group_id"],
                "path": str(item["path"]),
                "role": str(item["role"]),
                "sha256": str(item["sha256"]),
                "bytes": str(item["bytes"]),
                "present_in_overlay": str(item["present_in_overlay"]),
                "operator_priority": str(item["operator_priority"]),
                "rights_component_guess": str(item["rights_component_guess"]),
            })
    expected_csv.sort(key=lambda row: (row["group_id"], row["path"]))
    if recorded_csv != expected_csv:
        raise FrontierVerifyError("frontier CSV rows do not match recomputed groups")
    rec_id = exp.get("recommended_next_group_id")
    rec_groups = [g for g in derived_groups if g.get("group_id") == rec_id]
    if len(rec_groups) != 1:
        raise FrontierVerifyError("recommended next group not present exactly once")
    required_roles = set(exp.get("recommended_group_required_roles") or [])
    if not required_roles <= set(rec_groups[0].get("role_counts", {})):
        raise FrontierVerifyError("recommended group lacks required role coverage")
    recomputed_frontier = {
        k: frontier[k] for k in frontier.keys() if k not in {"frontier_sha256", "groups", "group_count", "selected_unique_path_count"}
    }
    recomputed_frontier["group_count"] = len(derived_groups)
    recomputed_frontier["selected_unique_path_count"] = len(selected_paths)
    recomputed_frontier["groups"] = derived_groups
    if frontier.get("frontier_sha256") != sha256_obj(recomputed_frontier):
        raise FrontierVerifyError("frontier self digest mismatch")
    return {"groups": len(derived_groups), "selected_unique_paths": len(selected_paths), "recommended_next_group_id": rec_id}


def verify_fixture(fixture_path: Path) -> dict[str, Any]:
    fixture = load_json_rel(rel(fixture_path), "fixture")
    claim = load_json_rel(fixture.get("claim_path"), "fixture.claim_path")
    public_inputs = load_json_rel(fixture.get("public_inputs_path"), "fixture.public_inputs_path")
    certificate = load_json_rel(fixture.get("certificate_path"), "fixture.certificate_path")
    for mutation in fixture.get("mutations") or []:
        if not isinstance(mutation, dict) or mutation.get("target") != "public_inputs":
            raise FrontierVerifyError("only public_inputs fixture mutations are supported")
        if mutation.get("op") != "replace":
            raise FrontierVerifyError("only replace mutations are supported")
        apply_mutation(public_inputs, mutation.get("path"), mutation.get("value"))
    verify_certificate(certificate, claim, public_inputs)
    verify_rights(public_inputs)
    parent_result = verify_parent_checkpoint(public_inputs)
    frontier_result = verify_frontier(public_inputs)
    return {"ok": True, "fixture_id": fixture.get("fixture_id"), "claim_id": claim.get("claim_id"), "parent": parent_result, "frontier": frontier_result}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify EvidenceVault rev0854 proofcore frontier PCD envelope")
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
                print("proofcore-frontier-pcd-rev0854: expected failure observed")
            return 0
        payload = {"ok": False, "fixture": fixture_rel, "error": str(exc)}
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"proofcore-frontier-pcd-rev0854: FAIL: {exc}", file=sys.stderr)
        return 1
    if args.expect_fail:
        msg = "fixture unexpectedly verified successfully"
        if args.json:
            print(json.dumps({"ok": False, "fixture": fixture_rel, "error": msg}, indent=2, sort_keys=True))
        else:
            print(f"proofcore-frontier-pcd-rev0854: FAIL: {msg}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("proofcore-frontier-pcd-rev0854: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
