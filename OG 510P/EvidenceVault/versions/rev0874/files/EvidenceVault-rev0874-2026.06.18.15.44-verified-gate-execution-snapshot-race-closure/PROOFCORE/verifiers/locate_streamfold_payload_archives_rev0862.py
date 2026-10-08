#!/usr/bin/env python3
"""Locate streamfold_sumcheck_toy_v2 payloads across directories and ZIP archives.

rev0861 can locate loose payload bytes in directories. rev0862 adds the missing
cloudtainer-shaped recovery path: many candidate exports arrive as ZIP files and
should be searchable without full extraction. This verifier scans real
directories and ZIP archives by exact byte count and SHA-256, can stage complete
unique matches to canonical EvidenceVault paths, and emits deterministic absence
or search receipts. It does not mutate the overlay, grant rights, or claim any
streamfold/SNARK protocol correctness.
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
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
REVISION = "rev0862"
DEFAULT_MANIFEST = "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0855/payload_manifest.rev0855.json"
DEFAULT_LOCATOR_CONTRACT = "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0861/loose_payload_locator_contract.rev0861.json"
DEFAULT_ARCHIVE_CONTRACT = "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0862/archive_payload_search_contract.rev0862.json"
SELFTEST_MARKER = "ev.rev0862.archive-payload-search.selftest"


class ArchiveSearchError(Exception):
    pass


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj)).hexdigest()


def sha256_file(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise ArchiveSearchError(f"cannot hash non-regular file: {path}")
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clean_archive_path(text: Any, field: str) -> str:
    if not isinstance(text, str) or not text:
        raise ArchiveSearchError(f"{field} must be a non-empty POSIX relative path")
    if "\x00" in text or "\\" in text:
        raise ArchiveSearchError(f"{field} must be POSIX-relative, not platform-specific: {text!r}")
    pure = PurePosixPath(text)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise ArchiveSearchError(f"{field} must be clean and relative: {text!r}")
    return pure.as_posix()


def load_json_rel(path_text: str, field: str, *, root: Path = ROOT) -> dict[str, Any]:
    rel = clean_archive_path(path_text, field)
    path = root / rel
    if path.is_symlink() or not path.is_file():
        raise ArchiveSearchError(f"{field} is not a regular file: {rel}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ArchiveSearchError(f"{field} invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ArchiveSearchError(f"{field} must contain a JSON object")
    return data


def load_contracts(
    manifest_rel: str = DEFAULT_MANIFEST,
    locator_contract_rel: str = DEFAULT_LOCATOR_CONTRACT,
    archive_contract_rel: str = DEFAULT_ARCHIVE_CONTRACT,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], str, str, str]:
    manifest_rel = clean_archive_path(manifest_rel, "manifest path")
    locator_contract_rel = clean_archive_path(locator_contract_rel, "rev0861 locator contract path")
    archive_contract_rel = clean_archive_path(archive_contract_rel, "archive search contract path")
    manifest = load_json_rel(manifest_rel, "payload manifest")
    locator_contract = load_json_rel(locator_contract_rel, "rev0861 loose locator contract")
    archive_contract = load_json_rel(archive_contract_rel, "rev0862 archive search contract")
    manifest_sha = sha256_file(ROOT / manifest_rel)
    locator_contract_sha = sha256_file(ROOT / locator_contract_rel)
    archive_contract_sha = sha256_file(ROOT / archive_contract_rel)
    if locator_contract.get("source_manifest_path") != manifest_rel or locator_contract.get("source_manifest_sha256") != manifest_sha:
        raise ArchiveSearchError("rev0861 loose locator contract is no longer bound to the source payload manifest")
    if archive_contract.get("revision") != REVISION:
        raise ArchiveSearchError("archive payload search contract revision mismatch")
    if archive_contract.get("source_manifest_path") != manifest_rel or archive_contract.get("source_manifest_sha256") != manifest_sha:
        raise ArchiveSearchError("archive search contract source manifest binding mismatch")
    if archive_contract.get("source_loose_locator_contract_path") != locator_contract_rel or archive_contract.get("source_loose_locator_contract_sha256") != locator_contract_sha:
        raise ArchiveSearchError("archive search contract source loose-locator binding mismatch")
    non_claims = "\n".join(str(x) for x in archive_contract.get("non_claims") or []).lower()
    for phrase in ["not a rights grant", "not a recovered payload bundle", "not a streamfold correctness proof", "not a snark"]:
        if phrase not in non_claims:
            raise ArchiveSearchError(f"archive search contract missing non-claim: {phrase}")
    return manifest, locator_contract, archive_contract, manifest_sha, locator_contract_sha, archive_contract_sha


def selected_payloads(manifest: dict[str, Any], archive_contract: dict[str, Any], mode: str) -> list[dict[str, Any]]:
    payloads = manifest.get("expected_payloads")
    if not isinstance(payloads, list) or not payloads:
        raise ArchiveSearchError("payload manifest expected_payloads must be non-empty")
    if mode == "full":
        selected = [item for item in payloads if isinstance(item, dict)]
    elif mode == "minimum":
        wanted = set(archive_contract.get("minimum_first_recovery_set") or [])
        selected = [item for item in payloads if isinstance(item, dict) and item.get("path") in wanted]
        missing = sorted(wanted - {item.get("path") for item in selected})
        if missing:
            raise ArchiveSearchError("minimum recovery set paths absent from manifest: " + ", ".join(missing))
    else:
        raise ArchiveSearchError(f"unsupported mode: {mode}")
    seen: set[str] = set()
    for idx, item in enumerate(selected):
        rel = clean_archive_path(item.get("path"), f"payload[{idx}].path")
        if rel in seen:
            raise ArchiveSearchError(f"duplicate selected payload path: {rel}")
        seen.add(rel)
    if not selected:
        raise ArchiveSearchError(f"no payloads selected for mode {mode}")
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
            raise ArchiveSearchError(f"invalid byte count for {rel}") from exc
        digest = str(item.get("sha256") or "")
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ArchiveSearchError(f"invalid SHA-256 for {rel}")
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
            raise ArchiveSearchError(f"canonical payload unexpectedly exists inside overlay: {row['path']}")
        absent += 1
    return absent


def assert_real_directory(path: Path, label: str) -> Path:
    raw = path.expanduser()
    if raw.is_symlink():
        raise ArchiveSearchError(f"{label} must be a real directory, not a symlink: {path}")
    resolved = raw.resolve(strict=False)
    if resolved.is_symlink() or not resolved.is_dir():
        raise ArchiveSearchError(f"{label} must be a real directory, not a symlink: {path}")
    return resolved


def assert_regular_zip(path: Path, label: str) -> Path:
    raw = path.expanduser()
    if raw.is_symlink():
        raise ArchiveSearchError(f"{label} must be a real ZIP file, not a symlink: {path}")
    resolved = raw.resolve(strict=False)
    if resolved.is_symlink() or not resolved.is_file():
        raise ArchiveSearchError(f"{label} must be a real ZIP file, not a symlink: {path}")
    if not zipfile.is_zipfile(resolved):
        raise ArchiveSearchError(f"{label} is not a readable ZIP archive: {path}")
    return resolved


def assert_no_symlink_components(root: Path, path: Path, label: str) -> None:
    root = root.resolve()
    try:
        rel = path.relative_to(root)
    except ValueError:
        try:
            rel = path.resolve(strict=False).relative_to(root)
        except Exception as exc:
            raise ArchiveSearchError(f"{label} escapes root: {path}") from exc
    cursor = root
    for part in rel.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ArchiveSearchError(f"{label} resolves through symlink component: {cursor.relative_to(root).as_posix()}")


def classify_source(path: Path) -> tuple[str, Path]:
    raw = path.expanduser()
    if raw.is_symlink():
        raise ArchiveSearchError(f"candidate source must not be a symlink: {path}")
    if raw.is_dir():
        return "directory", assert_real_directory(raw, "candidate directory")
    if raw.is_file():
        return "zip", assert_regular_zip(raw, "candidate archive")
    raise ArchiveSearchError(f"candidate source is neither a directory nor a ZIP file: {path}")


def source_is_forbidden(stage: Path, roots: list[Path]) -> bool:
    resolved = stage.resolve(strict=False)
    for item in roots:
        try:
            resolved.relative_to(item.resolve(strict=False))
            return True
        except ValueError:
            continue
    return False


def validate_stage_dir(stage_dir: Path, *, candidate_directory_roots: list[Path]) -> Path:
    raw = stage_dir.expanduser()
    if raw.exists() and raw.is_symlink():
        raise ArchiveSearchError(f"stage dir must not be a symlink: {stage_dir}")
    resolved = raw.resolve(strict=False)
    if source_is_forbidden(resolved, [ROOT]):
        raise ArchiveSearchError("stage dir must be outside the overlay bundle")
    if source_is_forbidden(resolved, candidate_directory_roots):
        raise ArchiveSearchError("stage dir must be outside candidate directory roots")
    if resolved.exists() and any(resolved.iterdir()):
        raise ArchiveSearchError(f"stage dir must be absent or empty: {stage_dir}")
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def sha256_zip_member(zf: zipfile.ZipFile, info: zipfile.ZipInfo) -> str:
    h = hashlib.sha256()
    with zf.open(info, "r") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_directory(source_index: int, root: Path, rows_by_size: dict[int, list[dict[str, Any]]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    root = assert_real_directory(root, "candidate directory")
    matches: list[dict[str, Any]] = []
    counters = {
        "directories_seen": 0,
        "regular_files_seen": 0,
        "symlink_dirs_skipped": 0,
        "symlink_files_skipped": 0,
        "non_regular_files_skipped": 0,
        "size_candidate_files_hashed": 0,
    }
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        directory = Path(dirpath)
        counters["directories_seen"] += 1
        kept_dirs = []
        for name in dirnames:
            child = directory / name
            if child.is_symlink():
                counters["symlink_dirs_skipped"] += 1
            else:
                kept_dirs.append(name)
        dirnames[:] = kept_dirs
        for name in filenames:
            child = directory / name
            if child.is_symlink():
                counters["symlink_files_skipped"] += 1
                continue
            if not child.is_file():
                counters["non_regular_files_skipped"] += 1
                continue
            counters["regular_files_seen"] += 1
            try:
                size = child.stat().st_size
            except OSError:
                continue
            if size not in rows_by_size:
                continue
            assert_no_symlink_components(root, child, "candidate file")
            digest = sha256_file(child)
            counters["size_candidate_files_hashed"] += 1
            for row in rows_by_size[size]:
                if row["sha256"] == digest:
                    matches.append({
                        "payload_path": row["path"],
                        "source_kind": "directory",
                        "source_index": source_index,
                        "source_label": root.name,
                        "relative_path": child.relative_to(root).as_posix(),
                        "bytes": size,
                        "sha256": digest,
                        "_source_path": str(child),
                    })
    report = {"source_index": source_index, "source_kind": "directory", "source_label": root.name, **counters, "matches_found": len(matches)}
    return matches, report


def is_zip_symlink(info: zipfile.ZipInfo) -> bool:
    mode = (info.external_attr >> 16) & 0o170000
    return stat.S_ISLNK(mode)


def scan_zip(source_index: int, zip_path: Path, rows_by_size: dict[int, list[dict[str, Any]]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    zip_path = assert_regular_zip(zip_path, "candidate archive")
    matches: list[dict[str, Any]] = []
    counters = {
        "zip_entries_seen": 0,
        "zip_file_entries_seen": 0,
        "zip_dir_entries_skipped": 0,
        "zip_symlink_entries_skipped": 0,
        "zip_unsafe_names_skipped": 0,
        "zip_size_candidate_entries_hashed": 0,
    }
    archive_sha = sha256_file(zip_path)
    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in zf.infolist():
            counters["zip_entries_seen"] += 1
            if info.is_dir():
                counters["zip_dir_entries_skipped"] += 1
                continue
            if is_zip_symlink(info):
                counters["zip_symlink_entries_skipped"] += 1
                continue
            try:
                member = clean_archive_path(info.filename, "zip member name")
            except Exception:
                counters["zip_unsafe_names_skipped"] += 1
                continue
            counters["zip_file_entries_seen"] += 1
            size = int(info.file_size)
            if size not in rows_by_size:
                continue
            digest = sha256_zip_member(zf, info)
            counters["zip_size_candidate_entries_hashed"] += 1
            for row in rows_by_size[size]:
                if row["sha256"] == digest:
                    matches.append({
                        "payload_path": row["path"],
                        "source_kind": "zip",
                        "source_index": source_index,
                        "source_label": zip_path.name,
                        "archive_sha256": archive_sha,
                        "member_path": member,
                        "bytes": size,
                        "sha256": digest,
                        "_archive_path": str(zip_path),
                        "_member_path": member,
                    })
    report = {"source_index": source_index, "source_kind": "zip", "source_label": zip_path.name, "source_sha256": archive_sha, **counters, "matches_found": len(matches)}
    return matches, report


def scan_sources(candidate_sources: list[Path], rows: list[dict[str, Any]]) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]], dict[str, int], list[Path]]:
    rows_by_size: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        rows_by_size.setdefault(int(row["bytes"]), []).append(row)
    all_matches: dict[str, list[dict[str, Any]]] = {row["path"]: [] for row in rows}
    source_reports: list[dict[str, Any]] = []
    aggregate: dict[str, int] = {"candidate_source_count": 0, "directory_source_count": 0, "zip_source_count": 0, "matches_found_total": 0}
    candidate_directory_roots: list[Path] = []
    for idx, source in enumerate(candidate_sources):
        kind, resolved = classify_source(source)
        aggregate["candidate_source_count"] += 1
        if kind == "directory":
            aggregate["directory_source_count"] += 1
            candidate_directory_roots.append(resolved)
            matches, report = scan_directory(idx, resolved, rows_by_size)
        elif kind == "zip":
            aggregate["zip_source_count"] += 1
            matches, report = scan_zip(idx, resolved, rows_by_size)
        else:  # pragma: no cover
            raise ArchiveSearchError(f"unsupported source kind: {kind}")
        source_reports.append(report)
        aggregate["matches_found_total"] += len(matches)
        for match in matches:
            all_matches.setdefault(match["payload_path"], []).append(match)
    return all_matches, source_reports, aggregate, candidate_directory_roots


def public_match(match: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in match.items() if not k.startswith("_")}


def build_findings(rows: list[dict[str, Any]], matches: dict[str, list[dict[str, Any]]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    findings: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    for row in rows:
        rel = row["path"]
        found = matches.get(rel, [])
        if not found:
            status = "missing"
        elif len(found) == 1:
            status = "found_unique_archive" if found[0].get("source_kind") == "zip" else "found_unique_directory"
        else:
            status = "ambiguous_duplicate_matches"
        counts[status] = counts.get(status, 0) + 1
        findings.append({
            "path": rel,
            "bytes": row["bytes"],
            "sha256": row["sha256"],
            "role": row["role"],
            "status": status,
            "match_count": len(found),
            "matches": [public_match(item) for item in found],
        })
    return findings, dict(sorted(counts.items()))


def status_from_counts(counts: dict[str, int], *, staged: bool) -> str:
    if counts.get("ambiguous_duplicate_matches"):
        return "ambiguous_duplicate_matches_block_staging"
    if counts.get("missing"):
        return "incomplete_missing_payloads"
    if staged:
        return "complete_unique_matches_staged"
    return "complete_unique_matches_ready_to_stage"


def write_payload_from_match(match: dict[str, Any], target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if match.get("source_kind") == "directory":
        source = Path(str(match["_source_path"]))
        if source.is_symlink() or not source.is_file():
            raise ArchiveSearchError(f"source match is no longer a regular file: {source}")
        shutil.copyfile(source, target)
    elif match.get("source_kind") == "zip":
        archive = Path(str(match["_archive_path"]))
        member = str(match["_member_path"])
        if archive.is_symlink() or not archive.is_file():
            raise ArchiveSearchError(f"source archive is no longer a regular file: {archive}")
        with zipfile.ZipFile(archive, "r") as zf:
            with zf.open(member, "r") as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)
    else:
        raise ArchiveSearchError("unsupported source kind for staging")


def stage_located_payloads(stage_dir: Path, candidate_directory_roots: list[Path], rows: list[dict[str, Any]], findings: list[dict[str, Any]], raw_matches: dict[str, list[dict[str, Any]]], *, mode: str, manifest_sha: str, archive_contract_sha: str) -> dict[str, Any]:
    incomplete = [f for f in findings if f.get("status") != "found_unique_archive" and f.get("status") != "found_unique_directory"]
    if incomplete:
        raise ArchiveSearchError("cannot stage unless every selected payload has exactly one trusted source match")
    stage_root = validate_stage_dir(stage_dir, candidate_directory_roots=candidate_directory_roots)
    staged: list[dict[str, Any]] = []
    for row in rows:
        rel = row["path"]
        match = raw_matches[rel][0]
        target = stage_root / rel
        write_payload_from_match(match, target)
        observed_size = target.stat().st_size
        observed_hash = sha256_file(target)
        if observed_size != row["bytes"] or observed_hash != row["sha256"]:
            raise ArchiveSearchError(f"staged payload identity mismatch: {rel}")
        staged.append({"path": rel, "bytes": observed_size, "sha256": observed_hash, "source_kind": match.get("source_kind"), "source_label": match.get("source_label")})
    graft_manifest = {
        "ok": True,
        "revision": REVISION,
        "stage_type": "streamfold_sumcheck_toy_v2_archive_payload_stage",
        "mode": mode,
        "source_manifest_sha256": manifest_sha,
        "archive_search_contract_sha256": archive_contract_sha,
        "staged_payload_count": len(staged),
        "staged_payloads": staged,
        "non_claims": ["not a rights grant", "not a publication-ready recovered bundle", "not a streamfold/SNARK proof"],
    }
    (stage_root / "EV_STREAMFOLD_ARCHIVE_PAYLOAD_STAGE.rev0862.json").write_text(json.dumps(graft_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (stage_root / "payloads.sha256").write_text("".join(f"{item['sha256']}  {item['path']}\n" for item in staged), encoding="utf-8")
    return {"stage_created": True, "stage_root_label": stage_root.name, "staged_payload_count": len(staged), "stage_manifest": "EV_STREAMFOLD_ARCHIVE_PAYLOAD_STAGE.rev0862.json", "payload_sha256_manifest": "payloads.sha256"}


def locate_report(candidate_sources: list[Path], stage_dir: Path | None, *, mode: str = "full") -> dict[str, Any]:
    manifest, _locator_contract, archive_contract, manifest_sha, locator_contract_sha, archive_contract_sha = load_contracts()
    selected = selected_payloads(manifest, archive_contract, mode)
    rows, role_counts, total_bytes = payload_rows(selected)
    absent_count = overlay_absence(rows)
    if not candidate_sources:
        findings = [{"path": row["path"], "bytes": row["bytes"], "sha256": row["sha256"], "role": row["role"], "status": "missing", "match_count": 0, "matches": []} for row in rows]
        return {
            "ok": True,
            "revision": REVISION,
            "mode": mode,
            "source_manifest_path": DEFAULT_MANIFEST,
            "source_manifest_sha256": manifest_sha,
            "source_loose_locator_contract_path": DEFAULT_LOCATOR_CONTRACT,
            "source_loose_locator_contract_sha256": locator_contract_sha,
            "archive_search_contract_path": DEFAULT_ARCHIVE_CONTRACT,
            "archive_search_contract_sha256": archive_contract_sha,
            "selected_path_count": len(rows),
            "selected_total_bytes": total_bytes,
            "role_counts": role_counts,
            "overlay_payloads_absent": absent_count,
            "candidate_source_count": 0,
            "source_reports": [],
            "findings": findings,
            "status_counts": {"missing": len(rows)},
            "archive_locator_status": "blocked_waiting_for_candidate_sources",
            "stage_created": False,
            "non_claims": ["absence report only", "not a recovered payload bundle", "not a rights grant"],
        }
    raw_matches, source_reports, aggregate, candidate_directory_roots = scan_sources(candidate_sources, rows)
    findings, status_counts = build_findings(rows, raw_matches)
    staged_info: dict[str, Any] = {"stage_created": False}
    if stage_dir is not None:
        staged_info = stage_located_payloads(stage_dir, candidate_directory_roots, rows, findings, raw_matches, mode=mode, manifest_sha=manifest_sha, archive_contract_sha=archive_contract_sha)
    status = status_from_counts(status_counts, staged=bool(staged_info.get("stage_created")))
    return {
        "ok": True,
        "revision": REVISION,
        "mode": mode,
        "source_manifest_path": DEFAULT_MANIFEST,
        "source_manifest_sha256": manifest_sha,
        "source_loose_locator_contract_path": DEFAULT_LOCATOR_CONTRACT,
        "source_loose_locator_contract_sha256": locator_contract_sha,
        "archive_search_contract_path": DEFAULT_ARCHIVE_CONTRACT,
        "archive_search_contract_sha256": archive_contract_sha,
        "selected_path_count": len(rows),
        "selected_total_bytes": total_bytes,
        "role_counts": role_counts,
        "overlay_payloads_absent": absent_count,
        **aggregate,
        "source_reports": source_reports,
        "findings": findings,
        "status_counts": status_counts,
        "archive_locator_status": status,
        **staged_info,
        "non_claims": ["search/stage report only", "not a rights grant", "not a streamfold correctness proof", "not a SNARK"],
    }


def make_zip(path: Path, members: list[tuple[str, bytes, int | None]]) -> None:
    with zipfile.ZipFile(path, "w") as zf:
        for name, payload, mode in members:
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            if mode is not None:
                info.external_attr = (mode & 0xFFFF) << 16
            zf.writestr(info, payload)


def self_test() -> dict[str, Any]:
    controls: dict[str, bool] = {}
    with tempfile.TemporaryDirectory(prefix="ev-archive-locator-selftest-") as tmp:
        base = Path(tmp)
        candidate_dir = base / "candidate-dir"
        candidate_dir.mkdir()
        candidate_zip = base / "candidate.zip"
        stage = base / "stage"
        objects = [
            ("artifacts/curated/streamfold/abi_ir/selftest_sumcheck_toy_v2.json", "loose/a.json", {"selftest": SELFTEST_MARKER, "kind": "dir", "value": 17}, "abi_ir_or_protocol_ir"),
            ("certs/curated/streamfold/examples/selftest/stmt.dsse.json", "exports/receipt.dsse.json", {"payloadType": "application/vnd.ev.selftest", "payload": "e30=", "signatures": [], "selftest": SELFTEST_MARKER}, "attestation_or_receipt"),
        ]
        rows: list[dict[str, Any]] = []
        dir_payload = json.dumps(objects[0][2], sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"
        dir_source = candidate_dir / objects[0][1]
        dir_source.parent.mkdir(parents=True, exist_ok=True)
        dir_source.write_bytes(dir_payload)
        zip_payload = json.dumps(objects[1][2], sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"
        make_zip(candidate_zip, [(objects[1][1], zip_payload, stat.S_IFREG | 0o644)])
        rows.append({"path": objects[0][0], "bytes": len(dir_payload), "sha256": hashlib.sha256(dir_payload).hexdigest(), "role": objects[0][3]})
        rows.append({"path": objects[1][0], "bytes": len(zip_payload), "sha256": hashlib.sha256(zip_payload).hexdigest(), "role": objects[1][3]})
        matches, reports, aggregate, dir_roots = scan_sources([candidate_dir, candidate_zip], rows)
        findings, counts = build_findings(rows, matches)
        controls["directory_payload_found"] = counts.get("found_unique_directory") == 1
        controls["zip_payload_found"] = counts.get("found_unique_archive") == 1
        info = stage_located_payloads(stage, dir_roots, rows, findings, matches, mode="selftest", manifest_sha="0" * 64, archive_contract_sha="1" * 64)
        controls["mixed_sources_staged_to_canonical_targets"] = info.get("staged_payload_count") == 2 and all((stage / row["path"]).is_file() for row in rows)
        duplicate = candidate_dir / "duplicate" / "copy-a.json"
        duplicate.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(dir_source, duplicate)
        dup_matches, _, _, dup_dirs = scan_sources([candidate_dir, candidate_zip], rows)
        dup_findings, dup_counts = build_findings(rows, dup_matches)
        controls["duplicate_hash_ambiguous"] = dup_counts.get("ambiguous_duplicate_matches") == 1
        try:
            stage_located_payloads(base / "stage-dup", dup_dirs, rows, dup_findings, dup_matches, mode="selftest", manifest_sha="0" * 64, archive_contract_sha="1" * 64)
        except Exception:
            controls["ambiguous_stage_rejected"] = True
        else:
            controls["ambiguous_stage_rejected"] = False
        symlink_zip = base / "symlink-entry.zip"
        make_zip(symlink_zip, [("link.json", b"target", stat.S_IFLNK | 0o777)])
        row = {"path": "artifacts/curated/streamfold/abi_ir/symlink_only.json", "bytes": 6, "sha256": hashlib.sha256(b"target").hexdigest(), "role": "abi_ir_or_protocol_ir"}
        sy_matches, sy_reports, _, _ = scan_sources([symlink_zip], [row])
        sy_findings, sy_counts = build_findings([row], sy_matches)
        controls["zip_symlink_entry_skipped"] = sy_counts.get("missing") == 1 and sy_reports[0].get("zip_symlink_entries_skipped") == 1
        unsafe_zip = base / "unsafe-entry.zip"
        make_zip(unsafe_zip, [("../escape.json", b"payload", stat.S_IFREG | 0o644)])
        unsafe_row = {"path": "artifacts/curated/streamfold/abi_ir/unsafe.json", "bytes": 7, "sha256": hashlib.sha256(b"payload").hexdigest(), "role": "abi_ir_or_protocol_ir"}
        unsafe_matches, unsafe_reports, _, _ = scan_sources([unsafe_zip], [unsafe_row])
        unsafe_findings, unsafe_counts = build_findings([unsafe_row], unsafe_matches)
        controls["unsafe_zip_member_skipped"] = unsafe_counts.get("missing") == 1 and unsafe_reports[0].get("zip_unsafe_names_skipped") == 1
        try:
            validate_stage_dir(ROOT / "PROOFCORE" / "bad-archive-stage", candidate_directory_roots=[candidate_dir])
        except Exception:
            controls["stage_inside_overlay_rejected"] = True
        else:
            controls["stage_inside_overlay_rejected"] = False
        try:
            validate_stage_dir(candidate_dir / "nested-stage", candidate_directory_roots=[candidate_dir])
        except Exception:
            controls["stage_inside_candidate_directory_rejected"] = True
        else:
            controls["stage_inside_candidate_directory_rejected"] = False
        try:
            partial_findings, _ = build_findings(rows, {rows[0]["path"]: [], rows[1]["path"]: matches[rows[1]["path"]]})
            stage_located_payloads(base / "stage-partial", dir_roots, rows, partial_findings, matches, mode="selftest", manifest_sha="0" * 64, archive_contract_sha="1" * 64)
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
        "non_claims": ["self-test uses synthetic bytes only", "not a recovered payload bundle", "not a rights grant"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Locate streamfold payload bytes across directories and ZIP archives")
    parser.add_argument("--candidate-source", action="append", default=[], help="directory or ZIP archive to scan; may be repeated")
    parser.add_argument("--stage-dir", help="optional empty output directory outside the overlay and candidate directory roots")
    parser.add_argument("--mode", choices=["full", "minimum"], default="full")
    parser.add_argument("--emit-report", help="write report JSON to this path")
    parser.add_argument("--self-test", action="store_true", help="run synthetic positive/negative controls for ZIP-aware recovery")
    parser.add_argument("--expect-fail", action="store_true", help="succeed only if verification fails")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)
    try:
        if args.self_test:
            result = self_test()
        else:
            sources = [Path(item).expanduser() for item in args.candidate_source]
            stage_dir = Path(args.stage_dir).expanduser() if args.stage_dir else None
            result = locate_report(sources, stage_dir, mode=args.mode)
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
                print("streamfold-archive-payload-search-rev0862: expected failure observed")
            return 0
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc), "revision": REVISION}, indent=2, sort_keys=True))
        else:
            print(f"streamfold-archive-payload-search-rev0862: FAIL: {exc}", file=sys.stderr)
        return 1
    if args.expect_fail:
        message = "verification unexpectedly succeeded"
        if args.json:
            print(json.dumps({"ok": False, "error": message, "revision": REVISION}, indent=2, sort_keys=True))
        else:
            print(f"streamfold-archive-payload-search-rev0862: FAIL: {message}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        label = "self-test OK" if args.self_test else "OK"
        print(f"streamfold-archive-payload-search-rev0862: {label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
