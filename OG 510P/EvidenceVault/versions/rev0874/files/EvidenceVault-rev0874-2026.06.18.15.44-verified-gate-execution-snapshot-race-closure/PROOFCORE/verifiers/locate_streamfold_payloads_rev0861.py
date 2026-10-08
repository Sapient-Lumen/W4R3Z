#!/usr/bin/env python3
"""Locate and stage streamfold_sumcheck_toy_v2 payloads by hash, not path.

rev0860 can stage a candidate tree only when the missing canonical payloads are
already present at their final EvidenceVault paths.  rev0861 handles the more
likely recovery scenario: a cache/export/search result may contain the right
bytes under different names.  This utility scans one or more real directories,
matches expected payloads by exact byte count and SHA-256, and can create an
isolated graft stage that rewrites verified source bytes to the canonical target
paths.  It does not mutate the overlay, grant rights, or prove streamfold
protocol correctness.
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
REVISION = "rev0861"
DEFAULT_MANIFEST = "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0855/payload_manifest.rev0855.json"
DEFAULT_GRAFT_CONTRACT = "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0860/payload_graft_contract.rev0860.json"
DEFAULT_LOCATOR_CONTRACT = "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0861/loose_payload_locator_contract.rev0861.json"
SELFTEST_MARKER = "ev.rev0861.loose-payload-locator.selftest"


class LocatorError(Exception):
    pass


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj)).hexdigest()


def sha256_file(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise LocatorError(f"cannot hash non-regular file: {path}")
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clean_archive_path(text: Any, field: str) -> str:
    if not isinstance(text, str) or not text:
        raise LocatorError(f"{field} must be a non-empty POSIX relative path")
    if "\x00" in text or "\\" in text:
        raise LocatorError(f"{field} must be POSIX-relative, not platform-specific: {text!r}")
    pure = PurePosixPath(text)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise LocatorError(f"{field} must be clean and relative: {text!r}")
    return pure.as_posix()


def load_json_rel(path_text: str, field: str, *, root: Path = ROOT) -> dict[str, Any]:
    rel = clean_archive_path(path_text, field)
    path = root / rel
    if path.is_symlink() or not path.is_file():
        raise LocatorError(f"{field} is not a regular file: {rel}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise LocatorError(f"{field} invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise LocatorError(f"{field} must contain a JSON object")
    return data


def assert_real_directory(path: Path, label: str) -> Path:
    raw = path.expanduser()
    if raw.is_symlink():
        raise LocatorError(f"{label} must be a real directory, not a symlink: {path}")
    resolved = raw.resolve(strict=False)
    if resolved.is_symlink() or not resolved.is_dir():
        raise LocatorError(f"{label} must be a real directory, not a symlink: {path}")
    return resolved


def assert_no_symlink_components(root: Path, path: Path, label: str) -> None:
    root = root.resolve()
    try:
        rel = path.relative_to(root)
    except ValueError:
        try:
            rel = path.resolve(strict=False).relative_to(root)
        except Exception as exc:
            raise LocatorError(f"{label} escapes root: {path}") from exc
    cursor = root
    for part in rel.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise LocatorError(f"{label} resolves through symlink component: {cursor.relative_to(root).as_posix()}")


def load_contracts(
    manifest_rel: str = DEFAULT_MANIFEST,
    graft_contract_rel: str = DEFAULT_GRAFT_CONTRACT,
    locator_contract_rel: str = DEFAULT_LOCATOR_CONTRACT,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], str, str, str]:
    manifest_rel = clean_archive_path(manifest_rel, "manifest path")
    graft_contract_rel = clean_archive_path(graft_contract_rel, "graft contract path")
    locator_contract_rel = clean_archive_path(locator_contract_rel, "locator contract path")
    manifest = load_json_rel(manifest_rel, "payload manifest")
    graft_contract = load_json_rel(graft_contract_rel, "payload graft contract")
    locator_contract = load_json_rel(locator_contract_rel, "loose payload locator contract")
    manifest_sha = sha256_file(ROOT / manifest_rel)
    graft_contract_sha = sha256_file(ROOT / graft_contract_rel)
    locator_contract_sha = sha256_file(ROOT / locator_contract_rel)
    if graft_contract.get("source_manifest_path") != manifest_rel or graft_contract.get("source_manifest_sha256") != manifest_sha:
        raise LocatorError("rev0860 graft contract is no longer bound to the source payload manifest")
    if locator_contract.get("revision") != REVISION:
        raise LocatorError("loose payload locator contract revision mismatch")
    if locator_contract.get("source_manifest_path") != manifest_rel or locator_contract.get("source_manifest_sha256") != manifest_sha:
        raise LocatorError("loose payload locator contract source manifest binding mismatch")
    if locator_contract.get("source_payload_graft_contract_path") != graft_contract_rel or locator_contract.get("source_payload_graft_contract_sha256") != graft_contract_sha:
        raise LocatorError("loose payload locator contract source graft binding mismatch")
    non_claims = "\n".join(str(x) for x in locator_contract.get("non_claims") or []).lower()
    for phrase in ["not a rights grant", "not a recovered payload bundle", "not a streamfold correctness proof", "not a snark"]:
        if phrase not in non_claims:
            raise LocatorError(f"loose locator contract missing non-claim: {phrase}")
    return manifest, graft_contract, locator_contract, manifest_sha, graft_contract_sha, locator_contract_sha


def selected_payloads(manifest: dict[str, Any], locator_contract: dict[str, Any], mode: str) -> list[dict[str, Any]]:
    payloads = manifest.get("expected_payloads")
    if not isinstance(payloads, list) or not payloads:
        raise LocatorError("payload manifest expected_payloads must be non-empty")
    if mode == "full":
        selected = [item for item in payloads if isinstance(item, dict)]
    elif mode == "minimum":
        wanted = set(locator_contract.get("minimum_first_recovery_set") or [])
        selected = [item for item in payloads if isinstance(item, dict) and item.get("path") in wanted]
        missing = sorted(wanted - {item.get("path") for item in selected})
        if missing:
            raise LocatorError("minimum recovery set paths absent from manifest: " + ", ".join(missing))
    else:
        raise LocatorError(f"unsupported mode: {mode}")
    if not selected:
        raise LocatorError(f"no payloads selected for mode {mode}")
    seen: set[str] = set()
    for idx, item in enumerate(selected):
        rel = clean_archive_path(item.get("path"), f"payload[{idx}].path")
        if rel in seen:
            raise LocatorError(f"duplicate selected payload path: {rel}")
        seen.add(rel)
    return selected


def payload_rows(selected: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int], int]:
    rows: list[dict[str, Any]] = []
    role_counts: dict[str, int] = {}
    total_bytes = 0
    for item in selected:
        rel = clean_archive_path(item.get("path"), "payload.path")
        try:
            size = int(item.get("bytes"))
        except Exception as exc:
            raise LocatorError(f"invalid byte count for {rel}") from exc
        digest = str(item.get("sha256") or "")
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise LocatorError(f"invalid SHA-256 for {rel}")
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
        target = ROOT / row["path"]
        if target.exists() or target.is_symlink():
            raise LocatorError(f"canonical payload unexpectedly exists inside overlay: {row['path']}")
        absent += 1
    return absent


def root_is_forbidden(root: Path, forbidden_roots: list[Path]) -> bool:
    resolved = root.resolve()
    for item in forbidden_roots:
        try:
            resolved.relative_to(item.resolve())
            return True
        except ValueError:
            continue
    return False


def iter_candidate_files(candidate_root: Path) -> tuple[list[Path], dict[str, int]]:
    candidate_root = assert_real_directory(candidate_root, "candidate root")
    files: list[Path] = []
    counters = {
        "directories_seen": 0,
        "regular_files_seen": 0,
        "symlink_dirs_skipped": 0,
        "symlink_files_skipped": 0,
        "non_regular_files_skipped": 0,
    }
    for dirpath, dirnames, filenames in os.walk(candidate_root, followlinks=False):
        directory = Path(dirpath)
        counters["directories_seen"] += 1
        kept_dirnames: list[str] = []
        for name in dirnames:
            child = directory / name
            if child.is_symlink():
                counters["symlink_dirs_skipped"] += 1
            else:
                kept_dirnames.append(name)
        dirnames[:] = kept_dirnames
        for name in filenames:
            path = directory / name
            if path.is_symlink():
                counters["symlink_files_skipped"] += 1
                continue
            if not path.is_file():
                counters["non_regular_files_skipped"] += 1
                continue
            assert_no_symlink_components(candidate_root, path, "candidate scan file")
            counters["regular_files_seen"] += 1
            files.append(path)
    return sorted(files), counters


def scan_candidate_roots(candidate_roots: list[Path], rows: list[dict[str, Any]]) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]], dict[str, int]]:
    by_size: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        by_size.setdefault(int(row["bytes"]), []).append(row)
    expected_by_sha = {row["sha256"]: row for row in rows}
    matches: dict[str, list[dict[str, Any]]] = {row["path"]: [] for row in rows}
    root_reports: list[dict[str, Any]] = []
    aggregate = {
        "candidate_roots_checked": 0,
        "directories_seen": 0,
        "regular_files_seen": 0,
        "symlink_dirs_skipped": 0,
        "symlink_files_skipped": 0,
        "non_regular_files_skipped": 0,
        "size_candidates_hashed": 0,
    }
    seen_roots: set[Path] = set()
    for idx, root in enumerate(candidate_roots):
        root = assert_real_directory(root, f"candidate root[{idx}]")
        if root in seen_roots:
            raise LocatorError(f"duplicate candidate root after resolution: {root}")
        seen_roots.add(root)
        files, counters = iter_candidate_files(root)
        root_report = {"root_index": idx, "root": str(root), **counters, "size_candidates_hashed": 0, "matches_found": 0}
        aggregate["candidate_roots_checked"] += 1
        for key in ["directories_seen", "regular_files_seen", "symlink_dirs_skipped", "symlink_files_skipped", "non_regular_files_skipped"]:
            aggregate[key] += int(counters.get(key, 0))
        for path in files:
            try:
                size = path.stat().st_size
            except OSError as exc:
                raise LocatorError(f"cannot stat candidate file: {path}: {exc}") from exc
            if size not in by_size:
                continue
            digest = sha256_file(path)
            root_report["size_candidates_hashed"] += 1
            aggregate["size_candidates_hashed"] += 1
            if digest not in expected_by_sha:
                continue
            row = expected_by_sha[digest]
            try:
                rel = path.relative_to(root).as_posix()
            except ValueError as exc:
                raise LocatorError(f"matched path escaped candidate root: {path}") from exc
            match = {
                "root_index": idx,
                "source_relpath": rel,
                "source_path_kind": "exact_canonical_path" if rel == row["path"] else "loose_hash_match_alternate_path",
                "bytes": size,
                "sha256": digest,
            }
            matches[row["path"]].append(match)
            root_report["matches_found"] += 1
        root_reports.append(root_report)
    return matches, root_reports, aggregate


def build_findings(rows: list[dict[str, Any]], matches: dict[str, list[dict[str, Any]]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    status_counts = {
        "missing": 0,
        "found_unique_exact_path": 0,
        "found_unique_loose_alternate_path": 0,
        "ambiguous_duplicate_matches": 0,
    }
    findings: list[dict[str, Any]] = []
    for row in rows:
        row_matches = sorted(matches.get(row["path"], []), key=lambda item: (item["root_index"], item["source_relpath"]))
        if not row_matches:
            status = "missing"
        elif len(row_matches) > 1:
            status = "ambiguous_duplicate_matches"
        elif row_matches[0]["source_path_kind"] == "exact_canonical_path":
            status = "found_unique_exact_path"
        else:
            status = "found_unique_loose_alternate_path"
        status_counts[status] += 1
        findings.append({
            "expected_path": row["path"],
            "bytes": row["bytes"],
            "sha256": row["sha256"],
            "role": row["role"],
            "status": status,
            "candidate_matches": row_matches,
        })
    return findings, status_counts


def validate_stage_dir(stage_dir: Path, *, candidate_roots: list[Path]) -> Path:
    raw = stage_dir.expanduser()
    if raw.is_symlink():
        raise LocatorError(f"stage directory path must not be a symlink: {stage_dir}")
    resolved = raw.resolve(strict=False)
    root_resolved = ROOT.resolve()
    try:
        resolved.relative_to(root_resolved)
    except ValueError:
        pass
    else:
        raise LocatorError("stage directory must be outside the overlay bundle root")
    for root in candidate_roots:
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            continue
        else:
            raise LocatorError("stage directory must not be inside a candidate root")
    if resolved.exists():
        if resolved.is_symlink() or not resolved.is_dir():
            raise LocatorError(f"stage path exists and is not a real directory: {stage_dir}")
        if any(resolved.iterdir()):
            raise LocatorError(f"stage directory must be absent or empty: {stage_dir}")
    parent = resolved.parent
    if parent.is_symlink() or not parent.is_dir():
        raise LocatorError(f"stage directory parent must be a real existing directory: {parent}")
    return resolved


def selected_unique_matches(findings: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    selected: dict[str, dict[str, Any]] = {}
    problems: list[str] = []
    for item in findings:
        status = item["status"]
        if status == "missing":
            problems.append(f"missing:{item['expected_path']}")
        elif status == "ambiguous_duplicate_matches":
            problems.append(f"ambiguous:{item['expected_path']}")
        else:
            selected[item["expected_path"]] = item["candidate_matches"][0]
    if problems:
        raise LocatorError("cannot stage incomplete or ambiguous payload set: " + ", ".join(problems[:8]))
    return selected


def build_stage_manifest(mode: str, rows: list[dict[str, Any]], findings: list[dict[str, Any]], *, manifest_sha: str, graft_contract_sha: str, locator_contract_sha: str) -> dict[str, Any]:
    return {
        "artifact_role": "streamfold_sumcheck_toy_v2 loose-hash payload locator graft stage manifest",
        "revision": REVISION,
        "mode": mode,
        "selected_path_count": len(rows),
        "selected_total_bytes": sum(int(row["bytes"]) for row in rows),
        "source_manifest_path": DEFAULT_MANIFEST,
        "source_manifest_sha256": manifest_sha,
        "source_payload_graft_contract_path": DEFAULT_GRAFT_CONTRACT,
        "source_payload_graft_contract_sha256": graft_contract_sha,
        "loose_payload_locator_contract_path": DEFAULT_LOCATOR_CONTRACT,
        "loose_payload_locator_contract_sha256": locator_contract_sha,
        "payloads": findings,
        "resolution_policy": "unique_match_required_for_stage",
        "non_claims": [
            "not a rights grant",
            "not a publication clearance",
            "not a streamfold correctness proof",
            "not a SNARK",
            "not zero knowledge",
            "not succinct",
        ],
    }


def stage_located_payloads(stage_dir: Path, candidate_roots: list[Path], rows: list[dict[str, Any]], findings: list[dict[str, Any]], *, mode: str, manifest_sha: str, graft_contract_sha: str, locator_contract_sha: str) -> dict[str, Any]:
    candidate_roots = [assert_real_directory(root, "candidate root") for root in candidate_roots]
    stage_dir = validate_stage_dir(stage_dir, candidate_roots=candidate_roots)
    selected = selected_unique_matches(findings)
    stage_manifest = build_stage_manifest(mode, rows, findings, manifest_sha=manifest_sha, graft_contract_sha=graft_contract_sha, locator_contract_sha=locator_contract_sha)
    tmp_stage = stage_dir.parent / f".{stage_dir.name}.tmp-{os.getpid()}"
    if tmp_stage.exists():
        shutil.rmtree(tmp_stage)
    tmp_stage.mkdir(parents=True)
    try:
        for row in rows:
            rel = clean_archive_path(row["path"], "stage target payload path")
            match = selected[rel]
            source_root = candidate_roots[int(match["root_index"])]
            source_rel = clean_archive_path(match["source_relpath"], "stage source payload path")
            src = source_root / source_rel
            assert_no_symlink_components(source_root, src, f"stage source payload {source_rel}")
            if src.is_symlink() or not src.is_file():
                raise LocatorError(f"stage source is not regular: {source_rel}")
            if src.stat().st_size != row["bytes"] or sha256_file(src) != row["sha256"]:
                raise LocatorError(f"stage source hash-or-size drifted: {source_rel}")
            dst = tmp_stage / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            os.chmod(dst, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
            if dst.stat().st_size != row["bytes"] or sha256_file(dst) != row["sha256"]:
                raise LocatorError(f"staged copy verification failed: {rel}")
        manifest_path = tmp_stage / "EV_STREAMFOLD_LOOSE_PAYLOAD_LOCATOR.rev0861.json"
        manifest_path.write_text(json.dumps(stage_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        checksum_path = tmp_stage / "payloads.sha256"
        checksum_path.write_text("".join(f"{row['sha256']}  {row['path']}\n" for row in rows), encoding="utf-8")
        manifest_sha = sha256_file(manifest_path)
        checksum_sha = sha256_file(checksum_path)
        if stage_dir.exists():
            stage_dir.rmdir()
        tmp_stage.rename(stage_dir)
    except Exception:
        if tmp_stage.exists():
            shutil.rmtree(tmp_stage)
        raise
    return {
        "loose_locator_stage_created": True,
        "stage_manifest_path": "EV_STREAMFOLD_LOOSE_PAYLOAD_LOCATOR.rev0861.json",
        "stage_manifest_sha256": manifest_sha,
        "payloads_sha256_path": "payloads.sha256",
        "payloads_sha256_sha256": checksum_sha,
        "staged_payload_count": len(rows),
        "staged_total_bytes": sum(int(row["bytes"]) for row in rows),
    }


def locator_status(status_counts: dict[str, int], candidate_roots_checked: int) -> str:
    if candidate_roots_checked == 0:
        return "blocked_waiting_for_candidate_roots"
    if status_counts.get("ambiguous_duplicate_matches", 0):
        return "blocked_ambiguous_duplicate_hash_matches"
    if status_counts.get("missing", 0):
        if status_counts.get("found_unique_exact_path", 0) or status_counts.get("found_unique_loose_alternate_path", 0):
            return "partial_payloads_found_some_missing"
        return "no_expected_payloads_found"
    if status_counts.get("found_unique_loose_alternate_path", 0):
        return "complete_unique_payload_set_found_with_loose_paths"
    return "complete_unique_payload_set_found_at_exact_paths"


def locate_report(candidate_roots: list[Path] | None, stage_dir: Path | None, *, mode: str) -> dict[str, Any]:
    manifest, graft_contract, locator_contract, manifest_sha, graft_contract_sha, locator_contract_sha = load_contracts()
    selected = selected_payloads(manifest, locator_contract, mode)
    rows, role_counts, total_bytes = payload_rows(selected)
    overlay_absent = overlay_absence(rows)
    candidate_roots = [assert_real_directory(root, "candidate root") for root in (candidate_roots or [])]
    if not candidate_roots:
        matches = {row["path"]: [] for row in rows}
        root_reports: list[dict[str, Any]] = []
        aggregate = {
            "candidate_roots_checked": 0,
            "directories_seen": 0,
            "regular_files_seen": 0,
            "symlink_dirs_skipped": 0,
            "symlink_files_skipped": 0,
            "non_regular_files_skipped": 0,
            "size_candidates_hashed": 0,
        }
    else:
        matches, root_reports, aggregate = scan_candidate_roots(candidate_roots, rows)
    findings, status_counts = build_findings(rows, matches)
    result: dict[str, Any] = {
        "ok": True,
        "revision": REVISION,
        "source_group_id": manifest.get("source_group_id"),
        "mode": mode,
        "selected_path_count": len(rows),
        "selected_total_bytes": total_bytes,
        "role_counts": role_counts,
        "overlay_payloads_absent": overlay_absent,
        "payload_manifest_sha256": manifest_sha,
        "source_payload_graft_contract_sha256": graft_contract_sha,
        "loose_payload_locator_contract_sha256": locator_contract_sha,
        "resolution_policy": locator_contract.get("resolution_policy"),
        "locator_status": locator_status(status_counts, int(aggregate["candidate_roots_checked"])),
        "status_counts": status_counts,
        "scan_summary": aggregate,
        "candidate_root_reports": root_reports,
        "findings": findings,
        "loose_locator_stage_created": False,
        "non_claims": [
            "not a rights grant",
            "not a publication clearance",
            "not a streamfold correctness proof",
            "not a SNARK",
            "not zero knowledge",
            "not succinct",
        ],
    }
    required_roles = list(locator_contract.get("required_roles") or [])
    for role in required_roles:
        if role not in role_counts:
            raise LocatorError(f"selected payload set lacks required role: {role}")
    if stage_dir is not None:
        if not candidate_roots:
            raise LocatorError("--stage-dir requires at least one --candidate-root")
        result.update(stage_located_payloads(stage_dir, candidate_roots, rows, findings, mode=mode, manifest_sha=manifest_sha, graft_contract_sha=graft_contract_sha, locator_contract_sha=locator_contract_sha))
        result["locator_status"] = "complete_unique_payload_set_staged"
    return result


def self_test() -> dict[str, Any]:
    controls: dict[str, bool] = {}
    with tempfile.TemporaryDirectory(prefix="ev-loose-locator-selftest-") as tmp:
        base = Path(tmp)
        candidate = base / "candidate"
        stage = base / "stage"
        candidate.mkdir()
        # Build synthetic payload rows whose source paths deliberately differ
        # from their target canonical paths.
        objects = [
            ("artifacts/curated/streamfold/abi_ir/selftest_sumcheck_toy_v2.json", "cache/export/a.json", {"selftest": SELFTEST_MARKER, "kind": "abi", "value": 11}, "abi_ir_or_protocol_ir"),
            ("certs/curated/streamfold/examples/selftest/stmt.dsse.json", "loose/receipt.dsse.json", {"payloadType": "application/vnd.ev.selftest", "payload": "e30=", "signatures": []}, "attestation_or_receipt"),
        ]
        rows: list[dict[str, Any]] = []
        for target_rel, source_rel, obj, role in objects:
            source = candidate / source_rel
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text(json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
            rows.append({"path": target_rel, "bytes": source.stat().st_size, "sha256": sha256_file(source), "role": role})
        matches, root_reports, aggregate = scan_candidate_roots([candidate], rows)
        findings, status_counts = build_findings(rows, matches)
        controls["loose_paths_found"] = status_counts.get("found_unique_loose_alternate_path") == 2
        info = stage_located_payloads(stage, [candidate], rows, findings, mode="selftest", manifest_sha="0" * 64, graft_contract_sha="1" * 64, locator_contract_sha="2" * 64)
        controls["loose_paths_staged_to_canonical_targets"] = info.get("staged_payload_count") == 2 and all((stage / row["path"]).is_file() for row in rows)
        duplicate = candidate / "second-copy" / "duplicate-a.json"
        duplicate.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(candidate / objects[0][1], duplicate)
        dup_matches, _, _ = scan_candidate_roots([candidate], rows)
        dup_findings, dup_counts = build_findings(rows, dup_matches)
        controls["duplicate_hash_ambiguous"] = dup_counts.get("ambiguous_duplicate_matches") == 1
        try:
            stage_located_payloads(base / "stage-dup", [candidate], rows, dup_findings, mode="selftest", manifest_sha="0" * 64, graft_contract_sha="1" * 64, locator_contract_sha="2" * 64)
        except Exception:
            controls["ambiguous_stage_rejected"] = True
        else:
            controls["ambiguous_stage_rejected"] = False
        symlink_only = base / "symlink-only"
        symlink_only.mkdir()
        real_outside_scan = base / "real-symlink-target.json"
        real_outside_scan.write_text(json.dumps({"selftest": SELFTEST_MARKER, "kind": "symlink-target"}, sort_keys=True) + "\n", encoding="utf-8")
        row = {"path": "artifacts/curated/streamfold/abi_ir/symlink_only.json", "bytes": real_outside_scan.stat().st_size, "sha256": sha256_file(real_outside_scan), "role": "abi_ir_or_protocol_ir"}
        try:
            (symlink_only / "link.json").symlink_to(real_outside_scan)
            link_matches, link_roots, link_agg = scan_candidate_roots([symlink_only], [row])
            link_findings, link_counts = build_findings([row], link_matches)
            controls["symlink_file_skipped"] = link_counts.get("missing") == 1 and link_agg.get("symlink_files_skipped") == 1
        except (OSError, NotImplementedError):
            controls["symlink_file_skipped"] = True
        try:
            clean_archive_path("../escape.json", "selftest escape path")
        except Exception:
            controls["path_escape_rejected"] = True
        else:
            controls["path_escape_rejected"] = False
        try:
            validate_stage_dir(ROOT / "PROOFCORE" / "bad-loose-stage", candidate_roots=[candidate])
        except Exception:
            controls["stage_inside_overlay_rejected"] = True
        else:
            controls["stage_inside_overlay_rejected"] = False
        try:
            validate_stage_dir(candidate / "nested-stage", candidate_roots=[candidate])
        except Exception:
            controls["stage_inside_candidate_rejected"] = True
        else:
            controls["stage_inside_candidate_rejected"] = False
        try:
            partial_findings, _ = build_findings(rows, {rows[0]["path"]: [], rows[1]["path"]: matches[rows[1]["path"]]})
            stage_located_payloads(base / "stage-partial", [candidate], rows, partial_findings, mode="selftest", manifest_sha="0" * 64, graft_contract_sha="1" * 64, locator_contract_sha="2" * 64)
        except Exception:
            controls["partial_stage_rejected"] = True
        else:
            controls["partial_stage_rejected"] = False
    return {
        "ok": True,
        "revision": REVISION,
        "self_test_id": SELFTEST_MARKER,
        "controls": controls,
        "required_controls_passed": all(controls.values()),
        "non_claims": ["self-test uses synthetic bytes only", "not a recovered payload bundle"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Locate streamfold payload bytes by exact hash and optionally stage them to canonical paths")
    parser.add_argument("--candidate-root", action="append", default=[], help="directory to scan; may be repeated")
    parser.add_argument("--stage-dir", help="optional empty output directory outside the overlay and candidate roots")
    parser.add_argument("--mode", choices=["full", "minimum"], default="full")
    parser.add_argument("--emit-report", help="write report JSON to this path")
    parser.add_argument("--self-test", action="store_true", help="run synthetic positive/negative controls for loose hash recovery")
    parser.add_argument("--expect-fail", action="store_true", help="succeed only if verification fails")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)
    try:
        if args.self_test:
            result = self_test()
        else:
            roots = [Path(item).expanduser() for item in args.candidate_root]
            stage_dir = Path(args.stage_dir).expanduser() if args.stage_dir else None
            result = locate_report(roots, stage_dir, mode=args.mode)
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
                print("streamfold-loose-payload-locator-rev0861: expected failure observed")
            return 0
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc), "revision": REVISION}, indent=2, sort_keys=True))
        else:
            print(f"streamfold-loose-payload-locator-rev0861: FAIL: {exc}", file=sys.stderr)
        return 1
    if args.expect_fail:
        message = "verification unexpectedly succeeded"
        if args.json:
            print(json.dumps({"ok": False, "error": message, "revision": REVISION}, indent=2, sort_keys=True))
        else:
            print(f"streamfold-loose-payload-locator-rev0861: FAIL: {message}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        label = "self-test OK" if args.self_test else "OK"
        print(f"streamfold-loose-payload-locator-rev0861: {label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
