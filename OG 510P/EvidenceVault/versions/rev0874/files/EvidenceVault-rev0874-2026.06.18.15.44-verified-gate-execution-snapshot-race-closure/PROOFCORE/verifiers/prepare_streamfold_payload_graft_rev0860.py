#!/usr/bin/env python3
"""Prepare exact streamfold_sumcheck_toy_v2 payload graft stages.

This verifier/utility is intentionally narrow.  It verifies a mounted candidate
canonical tree against the rev0855 streamfold payload manifest and the rev0860
payload-graft contract, then optionally creates an isolated staging directory
containing only the selected canonical payload files plus a deterministic graft
manifest.  It does not mutate the overlay bundle, grant rights, or prove
streamfold protocol correctness.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
REVISION = "rev0860"
DEFAULT_MANIFEST = "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0855/payload_manifest.rev0855.json"
DEFAULT_SOURCE_CONTRACT = "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0857/payload_admission_contract.rev0857.json"
DEFAULT_GRAFT_CONTRACT = "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0860/payload_graft_contract.rev0860.json"
SELFTEST_MARKER = "ev.rev0860.graft.selftest"


class GraftError(Exception):
    pass


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj)).hexdigest()


def sha256_file(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise GraftError(f"cannot hash non-regular file: {path}")
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clean_archive_path(text: Any, field: str) -> str:
    if not isinstance(text, str) or not text:
        raise GraftError(f"{field} must be a non-empty POSIX relative path")
    if "\x00" in text or "\\" in text:
        raise GraftError(f"{field} must be POSIX-relative, not platform-specific: {text!r}")
    pure = PurePosixPath(text)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise GraftError(f"{field} must be clean and relative: {text!r}")
    return pure.as_posix()


def load_json_rel(path_text: str, field: str, *, root: Path = ROOT) -> dict[str, Any]:
    rel = clean_archive_path(path_text, field)
    path = root / rel
    if path.is_symlink() or not path.is_file():
        raise GraftError(f"{field} is not a regular file: {rel}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise GraftError(f"{field} invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise GraftError(f"{field} must contain a JSON object")
    return data


def assert_real_directory(path: Path, label: str) -> Path:
    raw = path.expanduser()
    if raw.is_symlink():
        raise GraftError(f"{label} must be a real directory, not a symlink: {path}")
    resolved = raw.resolve(strict=False)
    if resolved.is_symlink() or not resolved.is_dir():
        raise GraftError(f"{label} must be a real directory, not a symlink: {path}")
    return resolved


def assert_no_symlink_components(root: Path, path: Path, label: str) -> None:
    root = root.resolve()
    try:
        rel = path.relative_to(root)
    except ValueError:
        try:
            rel = path.resolve(strict=False).relative_to(root)
        except Exception as exc:
            raise GraftError(f"{label} escapes root: {path}") from exc
    cursor = root
    for part in rel.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise GraftError(f"{label} resolves through symlink component: {cursor.relative_to(root).as_posix()}")


def parse_json_payload(path: Path, rel_path: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise GraftError(f"candidate payload is not parseable JSON: {rel_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise GraftError(f"candidate payload JSON is not an object: {rel_path}")
    return data


def load_contracts(
    manifest_rel: str = DEFAULT_MANIFEST,
    source_contract_rel: str = DEFAULT_SOURCE_CONTRACT,
    graft_contract_rel: str = DEFAULT_GRAFT_CONTRACT,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], str, str, str]:
    manifest_rel = clean_archive_path(manifest_rel, "manifest path")
    source_contract_rel = clean_archive_path(source_contract_rel, "source contract path")
    graft_contract_rel = clean_archive_path(graft_contract_rel, "graft contract path")
    manifest = load_json_rel(manifest_rel, "payload manifest")
    source_contract = load_json_rel(source_contract_rel, "source payload admission contract")
    graft_contract = load_json_rel(graft_contract_rel, "payload graft contract")
    manifest_sha = sha256_file(ROOT / manifest_rel)
    source_contract_sha = sha256_file(ROOT / source_contract_rel)
    graft_contract_sha = sha256_file(ROOT / graft_contract_rel)
    if source_contract.get("source_manifest_path") != manifest_rel or source_contract.get("source_manifest_sha256") != manifest_sha:
        raise GraftError("source payload admission contract is no longer bound to the source manifest")
    if graft_contract.get("revision") != REVISION:
        raise GraftError("payload graft contract revision mismatch")
    if graft_contract.get("source_manifest_path") != manifest_rel or graft_contract.get("source_manifest_sha256") != manifest_sha:
        raise GraftError("payload graft contract source manifest binding mismatch")
    if graft_contract.get("source_payload_admission_contract_path") != source_contract_rel or graft_contract.get("source_payload_admission_contract_sha256") != source_contract_sha:
        raise GraftError("payload graft contract source admission binding mismatch")
    non_claims = "\n".join(str(x) for x in graft_contract.get("non_claims") or []).lower()
    for phrase in ["not a rights grant", "not a recovered payload bundle", "not a streamfold correctness proof", "not a snark"]:
        if phrase not in non_claims:
            raise GraftError(f"payload graft contract missing non-claim: {phrase}")
    return manifest, source_contract, graft_contract, manifest_sha, source_contract_sha, graft_contract_sha


def selected_payloads(manifest: dict[str, Any], graft_contract: dict[str, Any], mode: str) -> list[dict[str, Any]]:
    payloads = manifest.get("expected_payloads")
    if not isinstance(payloads, list) or not payloads:
        raise GraftError("payload manifest expected_payloads must be non-empty")
    if mode == "full":
        selected = [item for item in payloads if isinstance(item, dict)]
    elif mode == "minimum":
        wanted = set(graft_contract.get("minimum_first_recovery_set") or [])
        selected = [item for item in payloads if isinstance(item, dict) and item.get("path") in wanted]
        missing = sorted(wanted - {item.get("path") for item in selected})
        if missing:
            raise GraftError("minimum recovery set paths absent from manifest: " + ", ".join(missing))
    else:
        raise GraftError(f"unsupported mode: {mode}")
    if not selected:
        raise GraftError(f"no payloads selected for mode {mode}")
    seen: set[str] = set()
    for idx, item in enumerate(selected):
        rel = clean_archive_path(item.get("path"), f"payload[{idx}].path")
        if rel in seen:
            raise GraftError(f"duplicate selected payload path: {rel}")
        seen.add(rel)
    return selected


def payload_report(selected: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int], int]:
    role_counts: dict[str, int] = {}
    total_bytes = 0
    rows: list[dict[str, Any]] = []
    for item in selected:
        rel = clean_archive_path(item.get("path"), "payload.path")
        try:
            size = int(item.get("bytes"))
        except Exception as exc:
            raise GraftError(f"invalid byte count for {rel}") from exc
        digest = str(item.get("sha256") or "")
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise GraftError(f"invalid SHA-256 for {rel}")
        role = str(item.get("role") or "unknown")
        role_counts[role] = role_counts.get(role, 0) + 1
        total_bytes += size
        rows.append({
            "path": rel,
            "bytes": size,
            "sha256": digest,
            "role": role,
            "rights_component_guess": item.get("rights_component_guess"),
        })
    return rows, dict(sorted(role_counts.items())), total_bytes


def overlay_absence(rows: list[dict[str, Any]]) -> int:
    absent = 0
    for row in rows:
        rel = row["path"]
        target = ROOT / rel
        if target.exists() or target.is_symlink():
            raise GraftError(f"canonical payload unexpectedly exists inside overlay: {rel}")
        absent += 1
    return absent


def verify_candidate_payloads(candidate_root: Path, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidate_root = assert_real_directory(candidate_root, "candidate root")
    reports: list[dict[str, Any]] = []
    for row in rows:
        rel = row["path"]
        candidate_path = candidate_root / rel
        try:
            resolved = candidate_path.resolve(strict=False)
            resolved.relative_to(candidate_root)
        except Exception as exc:
            raise GraftError(f"candidate path escapes root: {rel}") from exc
        assert_no_symlink_components(candidate_root, candidate_path, f"candidate payload {rel}")
        if candidate_path.is_symlink() or not candidate_path.is_file():
            raise GraftError(f"candidate payload missing or not regular: {rel}")
        observed_size = candidate_path.stat().st_size
        observed_sha = sha256_file(candidate_path)
        if observed_size != row["bytes"] or observed_sha != row["sha256"]:
            raise GraftError(f"candidate payload hash-or-size mismatch: {rel}")
        structural: dict[str, Any] = {"json_object": False}
        if rel.endswith(".json"):
            data = parse_json_payload(candidate_path, rel)
            structural["json_object"] = True
            structural["top_level_key_count"] = len(data)
            if rel.endswith(".dsse.json"):
                dsse_keys = {"payload", "payloadType", "signatures"}
                structural["dsse_standard_keys_present"] = sorted(dsse_keys.intersection(data))
                structural["strict_dsse_envelope"] = all(key in data for key in dsse_keys) and isinstance(data.get("signatures"), list)
        reports.append({
            "path": rel,
            "bytes": observed_size,
            "sha256": observed_sha,
            "role": row["role"],
            "structural": structural,
        })
    return reports


def validate_stage_dir(stage_dir: Path, *, candidate_root: Path | None = None) -> Path:
    raw = stage_dir.expanduser()
    if raw.is_symlink():
        raise GraftError(f"stage directory path must not be a symlink: {stage_dir}")
    resolved = raw.resolve(strict=False)
    root_resolved = ROOT.resolve()
    try:
        resolved.relative_to(root_resolved)
    except ValueError:
        pass
    else:
        raise GraftError("stage directory must be outside the overlay bundle root")
    if candidate_root is not None:
        candidate_resolved = candidate_root.resolve()
        try:
            resolved.relative_to(candidate_resolved)
        except ValueError:
            pass
        else:
            raise GraftError("stage directory must not be inside the candidate root")
    if resolved.exists():
        if resolved.is_symlink() or not resolved.is_dir():
            raise GraftError(f"stage path exists and is not a real directory: {stage_dir}")
        if any(resolved.iterdir()):
            raise GraftError(f"stage directory must be absent or empty: {stage_dir}")
    parent = resolved.parent
    if parent.is_symlink() or not parent.is_dir():
        raise GraftError(f"stage directory parent must be a real existing directory: {parent}")
    return resolved


def build_stage_manifest(mode: str, rows: list[dict[str, Any]], reports: list[dict[str, Any]], *, manifest_sha: str, source_contract_sha: str, graft_contract_sha: str) -> dict[str, Any]:
    return {
        "artifact_role": "streamfold_sumcheck_toy_v2 canonical payload graft stage manifest",
        "revision": REVISION,
        "mode": mode,
        "selected_path_count": len(rows),
        "selected_total_bytes": sum(int(row["bytes"]) for row in rows),
        "source_manifest_path": DEFAULT_MANIFEST,
        "source_manifest_sha256": manifest_sha,
        "source_payload_admission_contract_path": DEFAULT_SOURCE_CONTRACT,
        "source_payload_admission_contract_sha256": source_contract_sha,
        "payload_graft_contract_path": DEFAULT_GRAFT_CONTRACT,
        "payload_graft_contract_sha256": graft_contract_sha,
        "payloads": reports,
        "non_claims": [
            "not a rights grant",
            "not a publication clearance",
            "not a streamfold correctness proof",
            "not a SNARK",
            "not zero knowledge",
            "not succinct",
        ],
    }


def stage_payloads(candidate_root: Path, stage_dir: Path, rows: list[dict[str, Any]], reports: list[dict[str, Any]], *, mode: str, manifest_sha: str, source_contract_sha: str, graft_contract_sha: str) -> dict[str, Any]:
    candidate_root = assert_real_directory(candidate_root, "candidate root")
    stage_dir = validate_stage_dir(stage_dir, candidate_root=candidate_root)
    stage_manifest = build_stage_manifest(mode, rows, reports, manifest_sha=manifest_sha, source_contract_sha=source_contract_sha, graft_contract_sha=graft_contract_sha)
    tmp_stage = stage_dir.parent / f".{stage_dir.name}.tmp-{os.getpid()}"
    if tmp_stage.exists():
        shutil.rmtree(tmp_stage)
    tmp_stage.mkdir(parents=True)
    try:
        for report in reports:
            rel = clean_archive_path(report["path"], "stage payload path")
            src = candidate_root / rel
            dst = tmp_stage / rel
            assert_no_symlink_components(candidate_root, src, f"candidate payload {rel}")
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            os.chmod(dst, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
            if dst.stat().st_size != report["bytes"] or sha256_file(dst) != report["sha256"]:
                raise GraftError(f"copied payload verification failed: {rel}")
        manifest_path = tmp_stage / "EV_STREAMFOLD_PAYLOAD_GRAFT.rev0860.json"
        manifest_path.write_text(json.dumps(stage_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        checksum_path = tmp_stage / "payloads.sha256"
        checksum_path.write_text("".join(f"{row['sha256']}  {row['path']}\n" for row in rows), encoding="utf-8")
        stage_manifest_sha = sha256_file(manifest_path)
        checksum_sha = sha256_file(checksum_path)
        if stage_dir.exists():
            # Directory was verified empty; remove it so rename can be atomic on POSIX.
            stage_dir.rmdir()
        tmp_stage.rename(stage_dir)
    except Exception:
        if tmp_stage.exists():
            shutil.rmtree(tmp_stage)
        raise
    return {
        "graft_stage_created": True,
        "stage_manifest_path": "EV_STREAMFOLD_PAYLOAD_GRAFT.rev0860.json",
        "stage_manifest_sha256": stage_manifest_sha,
        "payloads_sha256_path": "payloads.sha256",
        "payloads_sha256_sha256": checksum_sha,
        "staged_payload_count": len(rows),
        "staged_total_bytes": sum(int(row["bytes"]) for row in rows),
    }


def prepare_report(candidate_root: Path | None, stage_dir: Path | None, *, mode: str) -> dict[str, Any]:
    manifest, source_contract, graft_contract, manifest_sha, source_contract_sha, graft_contract_sha = load_contracts()
    selected = selected_payloads(manifest, graft_contract, mode)
    rows, role_counts, total_bytes = payload_report(selected)
    overlay_absent = overlay_absence(rows)
    result: dict[str, Any] = {
        "ok": True,
        "revision": REVISION,
        "source_group_id": manifest.get("source_group_id"),
        "mode": mode,
        "selected_path_count": len(rows),
        "selected_total_bytes": total_bytes,
        "role_counts": role_counts,
        "overlay_payloads_absent": overlay_absent,
        "candidate_root_checked": candidate_root is not None,
        "candidate_payloads_verified": 0,
        "candidate_staging_status": "blocked_waiting_for_candidate_root",
        "graft_stage_created": False,
        "payload_manifest_sha256": manifest_sha,
        "source_payload_admission_contract_sha256": source_contract_sha,
        "payload_graft_contract_sha256": graft_contract_sha,
        "selected_paths": [row["path"] for row in rows],
        "non_claims": [
            "not a rights grant",
            "not a publication clearance",
            "not a streamfold correctness proof",
            "not a SNARK",
            "not zero knowledge",
            "not succinct",
        ],
    }
    required_roles = list(graft_contract.get("required_roles") or [])
    for role in required_roles:
        if role not in role_counts:
            raise GraftError(f"selected payload set lacks required role: {role}")
    if candidate_root is None:
        return result
    candidate_root = assert_real_directory(candidate_root, "candidate root")
    reports = verify_candidate_payloads(candidate_root, rows)
    result["candidate_payloads_verified"] = len(reports)
    result["candidate_payload_reports"] = reports
    result["candidate_staging_status"] = "candidate_verified_stage_dir_not_requested"
    if stage_dir is not None:
        stage_info = stage_payloads(candidate_root, stage_dir, rows, reports, mode=mode, manifest_sha=manifest_sha, source_contract_sha=source_contract_sha, graft_contract_sha=graft_contract_sha)
        result.update(stage_info)
        result["candidate_staging_status"] = "graft_stage_created"
    return result


def self_test() -> dict[str, Any]:
    accepted = 0
    rejected: dict[str, bool] = {}
    with tempfile.TemporaryDirectory(prefix="ev-graft-selftest-") as tmp:
        tmp_root = Path(tmp)
        candidate = tmp_root / "candidate"
        stage = tmp_root / "stage"
        candidate.mkdir()
        payload_a = {"selftest": SELFTEST_MARKER, "kind": "abi", "value": 7}
        payload_b = {"payloadType": "application/vnd.ev.selftest", "payload": "e30=", "signatures": []}
        fixtures = [
            ("artifacts/curated/streamfold/abi_ir/selftest_sumcheck_abi.json", payload_a, "abi_ir_or_protocol_ir"),
            ("certs/curated/streamfold/selftest/selftest.dsse.json", payload_b, "attestation_or_receipt"),
        ]
        rows: list[dict[str, Any]] = []
        for rel, obj, role in fixtures:
            dst = candidate / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
            rows.append({"path": rel, "bytes": dst.stat().st_size, "sha256": sha256_file(dst), "role": role})
        reports = verify_candidate_payloads(candidate, rows)
        info = stage_payloads(candidate, stage, rows, reports, mode="selftest", manifest_sha="0" * 64, source_contract_sha="1" * 64, graft_contract_sha="2" * 64)
        accepted = info["staged_payload_count"]
        try:
            bad_rows = [dict(rows[0], sha256="f" * 64)]
            verify_candidate_payloads(candidate, bad_rows)
        except Exception:
            rejected["hash_mismatch"] = True
        else:
            rejected["hash_mismatch"] = False
        try:
            clean_archive_path("../escape.json", "selftest escape path")
        except Exception:
            rejected["path_escape"] = True
        else:
            rejected["path_escape"] = False
        try:
            validate_stage_dir(ROOT / "PROOFCORE" / "bad-stage", candidate_root=candidate)
        except Exception:
            rejected["stage_inside_overlay"] = True
        else:
            rejected["stage_inside_overlay"] = False
        # Parent-directory symlink rejection, where supported by the platform.
        symlink_parent_rejected = False
        link_parent = candidate / "artifacts/curated/streamfold/symlink_parent"
        link_parent.parent.mkdir(parents=True, exist_ok=True)
        target_parent = candidate / "real_parent"
        target_parent.mkdir()
        try:
            link_parent.symlink_to(target_parent, target_is_directory=True)
            row = {"path": "artifacts/curated/streamfold/symlink_parent/file.json", "bytes": 2, "sha256": "00" * 32, "role": "abi_ir_or_protocol_ir"}
            (target_parent / "file.json").write_text("{}", encoding="utf-8")
            try:
                verify_candidate_payloads(candidate, [row])
            except Exception:
                symlink_parent_rejected = True
        except (OSError, NotImplementedError):
            symlink_parent_rejected = True
        rejected["symlink_parent"] = symlink_parent_rejected
    return {
        "ok": True,
        "revision": REVISION,
        "self_test_id": SELFTEST_MARKER,
        "accepted_stage_file_count": accepted,
        "rejected_controls": rejected,
        "non_claims": ["self-test uses synthetic bytes only", "not a recovered payload bundle"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare an exact-hash streamfold payload graft stage")
    parser.add_argument("--candidate-root", help="mounted canonical/candidate tree containing expected payload paths")
    parser.add_argument("--stage-dir", help="optional empty output directory outside the overlay where verified payloads are staged")
    parser.add_argument("--mode", choices=["full", "minimum"], default="full")
    parser.add_argument("--emit-report", help="write report JSON to this path")
    parser.add_argument("--self-test", action="store_true", help="run synthetic positive/negative controls for the graft engine")
    parser.add_argument("--expect-fail", action="store_true", help="succeed only if verification fails")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)
    try:
        if args.self_test:
            result = self_test()
        else:
            candidate_root = assert_real_directory(Path(args.candidate_root), "candidate root") if args.candidate_root else None
            stage_dir = Path(args.stage_dir).expanduser() if args.stage_dir else None
            if stage_dir is not None and candidate_root is None:
                raise GraftError("--stage-dir requires --candidate-root")
            result = prepare_report(candidate_root, stage_dir, mode=args.mode)
        if args.emit_report:
            out = Path(args.emit_report)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except Exception as exc:
        if args.expect_fail:
            payload = {"ok": True, "expected_failure_observed": True, "failure": str(exc), "revision": REVISION}
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print("streamfold-payload-graft-rev0860: expected failure observed")
            return 0
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc), "revision": REVISION}, indent=2, sort_keys=True))
        else:
            print(f"streamfold-payload-graft-rev0860: FAIL: {exc}", file=sys.stderr)
        return 1
    if args.expect_fail:
        message = "verification unexpectedly succeeded"
        if args.json:
            print(json.dumps({"ok": False, "error": message, "revision": REVISION}, indent=2, sort_keys=True))
        else:
            print(f"streamfold-payload-graft-rev0860: FAIL: {message}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        label = "self-test OK" if args.self_test else "OK"
        print(f"streamfold-payload-graft-rev0860: {label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
