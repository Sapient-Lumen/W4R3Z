#!/usr/bin/env python3
"""rev0064 source-bundle intake/safe-extraction gate.

This helper validates the uploaded Nicotine source bundle as an archived-source
input without embedding source content into the cube. It checks the source ZIP
identity, entry/path safety, lane extraction roundtrip, source-lane manifests,
critical file hashes, and fail-closed negative controls for unsafe ZIP shapes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import stat
import sys
import tempfile
import warnings
import zipfile
from pathlib import Path, PurePosixPath
from typing import Dict, Iterable, List, Tuple

sys.dont_write_bytecode = True
warnings.filterwarnings("ignore", message="Duplicate name:*", category=UserWarning, module="zipfile")
ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SOURCE_SHA256 = "feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b"
SOURCE_PREFIX = "Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z/source-trees/"
GIT_FULL_PREFIX = "Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z/git-full/"
LANES = ("github-tag-3.3.10", "github-branch-3.3.x", "github-branch-master")
CRITICAL_FILES = (
    "pynicotine/downloads.py",
    "pynicotine/transfers.py",
    "pynicotine/slskproto.py",
    "pynicotine/search.py",
    "pynicotine/slskmessages.py",
)
BAD_PACKAGE_PARTS = {"__pycache__", ".pytest_cache", "source-trees", "git-full", ".git"}


def sha_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_csv(path: Path, rows: List[Dict[str, object]], fields: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(fields))
        w.writeheader()
        for row in rows:
            w.writerow({field: row.get(field, "") for field in w.fieldnames})


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def cleanup_caches(path: Path) -> None:
    for cache in list(path.rglob("__pycache__")) + list(path.rglob(".pytest_cache")):
        shutil.rmtree(cache, ignore_errors=True)


def zip_mode(zi: zipfile.ZipInfo) -> int:
    return (zi.external_attr >> 16) & 0xFFFF


def is_symlink(zi: zipfile.ZipInfo) -> bool:
    return stat.S_IFMT(zip_mode(zi)) == stat.S_IFLNK


def normalize_zip_name(name: str) -> Tuple[str, List[str]]:
    errors: List[str] = []
    raw = name.replace("\\", "/")
    if raw.startswith("/"):
        errors.append("absolute-path")
    if ":" in raw.split("/", 1)[0]:
        errors.append("drive-prefix")
    parts = [p for p in raw.split("/") if p not in ("", ".")]
    if any(p == ".." for p in parts):
        errors.append("parent-traversal")
    # Keep directory marker semantics out of the normalized key.
    normalized = "/".join(parts)
    if not normalized:
        errors.append("empty-normalized-path")
    return normalized, errors


def entry_scope(name: str) -> Tuple[str, str, str]:
    """Return scope, lane, relative path within lane/git-full if applicable."""
    if name.startswith(SOURCE_PREFIX):
        rest = name[len(SOURCE_PREFIX):]
        lane = rest.split("/", 1)[0] if rest else ""
        rel = rest.split("/", 1)[1] if "/" in rest else ""
        if lane in LANES:
            return "source-lane", lane, rel
        return "source-prefix-other", lane, rel
    if name.startswith(GIT_FULL_PREFIX):
        return "git-full-bundle", "", name[len(GIT_FULL_PREFIX):]
    return "archive-root", "", name


def scan_entries(source_zip: Path) -> Tuple[List[Dict[str, object]], List[str]]:
    rows: List[Dict[str, object]] = []
    errors: List[str] = []
    seen: Dict[str, str] = {}
    with zipfile.ZipFile(source_zip) as zf:
        for zi in zf.infolist():
            normalized, path_errors = normalize_zip_name(zi.filename)
            scope, lane, rel = entry_scope(zi.filename)
            symlink = is_symlink(zi)
            duplicate = normalized in seen
            status = "pass"
            entry_errors: List[str] = []
            if path_errors:
                entry_errors.extend(path_errors)
            if symlink:
                entry_errors.append("symlink-entry")
            if duplicate:
                entry_errors.append(f"duplicate-normalized-path:first={seen[normalized]}")
            if entry_errors:
                status = "fail"
                errors.append(f"{zi.filename}: {';'.join(entry_errors)}")
            else:
                seen[normalized] = zi.filename
            rows.append({
                "name": zi.filename,
                "normalized_path": normalized,
                "scope": scope,
                "lane": lane,
                "relative_path": rel,
                "is_dir": str(zi.is_dir()).lower(),
                "is_symlink": str(symlink).lower(),
                "mode_octal": oct(zip_mode(zi)),
                "compressed_size": zi.compress_size,
                "file_size": zi.file_size,
                "status": status,
                "errors": ";".join(entry_errors),
            })
    return rows, errors


def source_lane_file_rows(source_zip: Path) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    with zipfile.ZipFile(source_zip) as zf:
        for zi in zf.infolist():
            scope, lane, rel = entry_scope(zi.filename)
            if scope != "source-lane" or zi.is_dir() or not rel:
                continue
            if is_symlink(zi):
                # The safety scanner will already fail this; do not follow it.
                content_sha = ""
            else:
                content_sha = sha_bytes(zf.read(zi))
            rows.append({
                "lane": lane,
                "relative_path": rel,
                "size_bytes": zi.file_size,
                "compressed_size": zi.compress_size,
                "mode_octal": oct(zip_mode(zi)),
                "sha256": content_sha,
                "status": "manifested",
            })
    rows.sort(key=lambda r: (str(r["lane"]), str(r["relative_path"])))
    return rows


def lane_manifest_digest(rows: List[Dict[str, object]], lane: str) -> str:
    material = []
    for r in rows:
        if r["lane"] == lane:
            material.append(f"{r['relative_path']}\0{r['size_bytes']}\0{r['sha256']}\n")
    return hashlib.sha256("".join(material).encode("utf-8")).hexdigest()


def lane_summaries(rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for lane in LANES:
        lane_rows = [r for r in rows if r["lane"] == lane]
        out.append({
            "lane": lane,
            "file_count": len(lane_rows),
            "total_size_bytes": sum(int(r["size_bytes"]) for r in lane_rows),
            "manifest_sha256": lane_manifest_digest(rows, lane),
            "critical_files_present": sum(1 for f in CRITICAL_FILES if any(r["relative_path"] == f for r in lane_rows)),
            "status": "pass" if lane_rows and all(any(r["relative_path"] == f for r in lane_rows) for f in CRITICAL_FILES) else "fail",
        })
    return out


def read_rev0051_manifest() -> Dict[Tuple[str, str], Dict[str, str]]:
    path = ROOT / "data" / "rev0051_source_file_manifest.csv"
    out: Dict[Tuple[str, str], Dict[str, str]] = {}
    if not path.exists():
        return out
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out[(row["lane"], row["file"])] = row
    return out


def critical_file_crosscheck(file_rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    by_key = {(str(r["lane"]), str(r["relative_path"])): r for r in file_rows}
    prior = read_rev0051_manifest()
    rows: List[Dict[str, object]] = []
    for lane in LANES:
        for rel in CRITICAL_FILES:
            current = by_key.get((lane, rel))
            previous = prior.get((lane, rel))
            cur_sha = str(current.get("sha256", "")) if current else ""
            prev_sha = previous.get("sha256", "") if previous else ""
            rows.append({
                "lane": lane,
                "file": rel,
                "current_sha256": cur_sha,
                "rev0051_sha256": prev_sha,
                "size_bytes": current.get("size_bytes", "") if current else "",
                "status": "pass" if current and previous and cur_sha == prev_sha else "fail",
            })
    return rows


def git_identity_rows(source_zip: Path) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    with zipfile.ZipFile(source_zip) as zf:
        names = set(zf.namelist())
        for lane in LANES:
            head_path = f"{GIT_FULL_PREFIX}.git/worktrees/{lane}/HEAD"
            orig_path = f"{GIT_FULL_PREFIX}.git/worktrees/{lane}/ORIG_HEAD"
            lane_git_file = f"{SOURCE_PREFIX}{lane}/.git"
            head = zf.read(head_path).decode("utf-8", errors="replace").strip() if head_path in names else ""
            orig = zf.read(orig_path).decode("utf-8", errors="replace").strip() if orig_path in names else ""
            git_file = zf.read(lane_git_file).decode("utf-8", errors="replace").strip() if lane_git_file in names else ""
            rows.append({
                "lane": lane,
                "worktree_head": head,
                "worktree_orig_head": orig,
                "lane_git_file_present": str(lane_git_file in names).lower(),
                "lane_git_file_kind": "plain-gitdir-file" if git_file.startswith("gitdir:") else ("missing" if not git_file else "other"),
                "status": "pass" if len(head) == 40 and head == orig and git_file.startswith("gitdir:") else "fail",
            })
    return rows


def safe_extract_lane(source_zip: Path, lane: str, dest: Path) -> int:
    prefix = SOURCE_PREFIX + lane + "/"
    count = 0
    dest = dest.resolve()
    with zipfile.ZipFile(source_zip) as zf:
        for zi in zf.infolist():
            if not zi.filename.startswith(prefix) or zi.is_dir():
                continue
            rel = zi.filename[len(prefix):]
            normalized, path_errors = normalize_zip_name(rel)
            if path_errors or is_symlink(zi):
                raise ValueError(f"unsafe lane entry {zi.filename}: {path_errors} symlink={is_symlink(zi)}")
            target = (dest / normalized).resolve()
            if os.path.commonpath([str(dest), str(target)]) != str(dest):
                raise ValueError(f"extract target escaped destination: {zi.filename}")
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(zi) as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)
            count += 1
    return count


def extracted_file_manifest(root: Path, lane: str) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for p in sorted(x for x in root.rglob("*") if x.is_file()):
        rel = p.relative_to(root).as_posix()
        rows.append({"lane": lane, "relative_path": rel, "size_bytes": p.stat().st_size, "sha256": sha_path(p)})
    return rows


def extraction_roundtrip(source_zip: Path, zip_rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    zip_by_lane = {lane: [r for r in zip_rows if r["lane"] == lane] for lane in LANES}
    zip_digest = {lane: lane_manifest_digest(zip_rows, lane) for lane in LANES}
    with tempfile.TemporaryDirectory(prefix="rev0064-source-extract-") as td:
        base = Path(td)
        for lane in LANES:
            dest = base / lane
            try:
                extracted_count = safe_extract_lane(source_zip, lane, dest)
                manifest = extracted_file_manifest(dest, lane)
                digest = lane_manifest_digest(manifest, lane)
                status = "pass" if extracted_count == len(zip_by_lane[lane]) and digest == zip_digest[lane] else "fail"
                detail = "safe extract count/hash matched source-lane manifest" if status == "pass" else "safe extract mismatch"
            except Exception as exc:
                extracted_count = 0
                digest = ""
                status = "fail"
                detail = str(exc)
            rows.append({
                "lane": lane,
                "zip_manifest_files": len(zip_by_lane[lane]),
                "extracted_files": extracted_count,
                "zip_manifest_sha256": zip_digest[lane],
                "extracted_manifest_sha256": digest,
                "status": status,
                "detail": detail,
            })
    return rows


def make_test_zip(entries: List[Tuple[str, bytes, int | None]]) -> bytes:
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w") as zf:
        for name, data, mode in entries:
            zi = zipfile.ZipInfo(name)
            if mode is None:
                mode = stat.S_IFREG | 0o644
            zi.external_attr = mode << 16
            zf.writestr(zi, data)
    return bio.getvalue()


def scan_zip_bytes(data: bytes) -> Tuple[List[Dict[str, object]], List[str]]:
    with tempfile.NamedTemporaryFile(prefix="rev0064-negative-", suffix=".zip", delete=False) as tf:
        tf.write(data)
        temp_name = Path(tf.name)
    try:
        return scan_entries(temp_name)
    finally:
        temp_name.unlink(missing_ok=True)


def negative_controls() -> List[Dict[str, object]]:
    controls = [
        ("parent-traversal-source-entry", make_test_zip([(SOURCE_PREFIX + LANES[0] + "/../escape.txt", b"x", None)]), "parent-traversal"),
        ("absolute-path-entry", make_test_zip([("/tmp/escape.txt", b"x", None)]), "absolute-path"),
        ("symlink-source-entry", make_test_zip([(SOURCE_PREFIX + LANES[0] + "/link", b"target", stat.S_IFLNK | 0o777)]), "symlink-entry"),
        ("duplicate-normalized-entry", make_test_zip([("dup.txt", b"one", None), ("dup.txt", b"two", None)]), "duplicate-normalized-path"),
    ]
    rows: List[Dict[str, object]] = []
    for name, data, expected in controls:
        _, errors = scan_zip_bytes(data)
        joined = " | ".join(errors)
        rejected = expected in joined
        rows.append({
            "control": name,
            "expected_rejection": expected,
            "observed_errors": joined,
            "status": "pass" if rejected else "fail",
        })
    return rows


def package_hygiene() -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for bad in BAD_PACKAGE_PARTS:
        hits = []
        for p in ROOT.rglob(bad):
            rel = p.relative_to(ROOT).as_posix()
            # Source-bundle names may occur in text files, but package paths should not include these roots.
            hits.append(rel)
        # .git as text inside docs is fine; this scans path names only.
        if bad in {"source-trees", "git-full", ".git"}:
            hits = [h for h in hits if h.split("/")[0] not in {"docs", "evidence", "data", "report_drafts", "handoff", "tools"}]
        rows.append({"path_part": bad, "hits": len(hits), "sample": ";".join(hits[:5]), "status": "pass" if not hits else "fail"})
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description="validate rev0064 source-bundle intake and safe extraction")
    ap.add_argument("--source-zip", required=True)
    ap.add_argument("--out-dir", default=str(ROOT / "evidence" / "rev0064-source-intake-gate"))
    ap.add_argument("--write-data", action="store_true")
    ns = ap.parse_args()

    source_zip = Path(ns.source_zip).resolve()
    out_dir = Path(ns.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    cleanup_caches(ROOT)

    errors: List[str] = []
    source_identity = {
        "source_zip": str(source_zip),
        "exists": source_zip.exists(),
        "sha256": sha_path(source_zip) if source_zip.exists() else "",
    }
    if source_identity["sha256"] != EXPECTED_SOURCE_SHA256:
        errors.append("source bundle SHA256 did not match expected uploaded source identity")

    entry_rows, entry_errors = scan_entries(source_zip) if source_zip.exists() else ([], ["source zip missing"])
    errors.extend(entry_errors)
    file_rows = source_lane_file_rows(source_zip) if source_zip.exists() else []
    summary_rows = lane_summaries(file_rows)
    git_rows = git_identity_rows(source_zip) if source_zip.exists() else []
    critical_rows = critical_file_crosscheck(file_rows)
    extract_rows = extraction_roundtrip(source_zip, file_rows) if source_zip.exists() else []
    negative_rows = negative_controls()
    hygiene_rows = package_hygiene()

    for name, rows in (
        ("lane summaries", summary_rows),
        ("git identity", git_rows),
        ("critical file crosscheck", critical_rows),
        ("safe extraction roundtrip", extract_rows),
        ("negative controls", negative_rows),
        ("package hygiene", hygiene_rows),
    ):
        failed = [r for r in rows if r.get("status") != "pass"]
        if failed:
            errors.append(f"{name} failures: {len(failed)}")

    status = "pass" if not errors else "fail"
    summary = {
        "revision": "rev0064",
        "status": status,
        "source_identity": source_identity,
        "source_zip_entries": len(entry_rows),
        "source_lane_file_rows": len(file_rows),
        "source_lane_total_files": sum(int(r["file_count"]) for r in summary_rows),
        "source_lane_total_bytes": sum(int(r["total_size_bytes"]) for r in summary_rows),
        "entry_safety_failures": len(entry_errors),
        "lane_summaries_pass": sum(1 for r in summary_rows if r.get("status") == "pass"),
        "git_identity_pass": sum(1 for r in git_rows if r.get("status") == "pass"),
        "critical_file_crosscheck_pass": sum(1 for r in critical_rows if r.get("status") == "pass"),
        "safe_extraction_roundtrip_pass": sum(1 for r in extract_rows if r.get("status") == "pass"),
        "negative_controls_pass": sum(1 for r in negative_rows if r.get("status") == "pass"),
        "package_hygiene_pass": sum(1 for r in hygiene_rows if r.get("status") == "pass"),
        "errors": errors,
    }

    write_csv(out_dir / "source_zip_entry_safety.csv", entry_rows, ["name", "normalized_path", "scope", "lane", "relative_path", "is_dir", "is_symlink", "mode_octal", "compressed_size", "file_size", "status", "errors"])
    write_json(out_dir / "source_zip_entry_safety.json", entry_rows)
    write_csv(out_dir / "source_lane_file_manifest.csv", file_rows, ["lane", "relative_path", "size_bytes", "compressed_size", "mode_octal", "sha256", "status"])
    write_json(out_dir / "source_lane_file_manifest.json", file_rows)
    write_csv(out_dir / "source_lane_summary.csv", summary_rows, ["lane", "file_count", "total_size_bytes", "manifest_sha256", "critical_files_present", "status"])
    write_json(out_dir / "source_lane_summary.json", summary_rows)
    write_csv(out_dir / "source_lane_git_identity.csv", git_rows, ["lane", "worktree_head", "worktree_orig_head", "lane_git_file_present", "lane_git_file_kind", "status"])
    write_json(out_dir / "source_lane_git_identity.json", git_rows)
    write_csv(out_dir / "source_critical_file_crosscheck.csv", critical_rows, ["lane", "file", "current_sha256", "rev0051_sha256", "size_bytes", "status"])
    write_json(out_dir / "source_critical_file_crosscheck.json", critical_rows)
    write_csv(out_dir / "source_safe_extraction_roundtrip.csv", extract_rows, ["lane", "zip_manifest_files", "extracted_files", "zip_manifest_sha256", "extracted_manifest_sha256", "status", "detail"])
    write_json(out_dir / "source_safe_extraction_roundtrip.json", extract_rows)
    write_csv(out_dir / "source_intake_negative_controls.csv", negative_rows, ["control", "expected_rejection", "observed_errors", "status"])
    write_json(out_dir / "source_intake_negative_controls.json", negative_rows)
    write_csv(out_dir / "source_intake_package_hygiene.csv", hygiene_rows, ["path_part", "hits", "sample", "status"])
    write_json(out_dir / "source_intake_package_hygiene.json", hygiene_rows)
    write_json(out_dir / "source_intake_summary.json", summary)

    if ns.write_data:
        mappings = {
            "source_zip_entry_safety.csv": "data/rev0064_source_zip_entry_safety.csv",
            "source_zip_entry_safety.json": "data/rev0064_source_zip_entry_safety.json",
            "source_lane_file_manifest.csv": "data/rev0064_source_lane_file_manifest.csv",
            "source_lane_file_manifest.json": "data/rev0064_source_lane_file_manifest.json",
            "source_lane_summary.csv": "data/rev0064_source_lane_summary.csv",
            "source_lane_summary.json": "data/rev0064_source_lane_summary.json",
            "source_lane_git_identity.csv": "data/rev0064_source_lane_git_identity.csv",
            "source_lane_git_identity.json": "data/rev0064_source_lane_git_identity.json",
            "source_critical_file_crosscheck.csv": "data/rev0064_source_critical_file_crosscheck.csv",
            "source_critical_file_crosscheck.json": "data/rev0064_source_critical_file_crosscheck.json",
            "source_safe_extraction_roundtrip.csv": "data/rev0064_source_safe_extraction_roundtrip.csv",
            "source_safe_extraction_roundtrip.json": "data/rev0064_source_safe_extraction_roundtrip.json",
            "source_intake_negative_controls.csv": "data/rev0064_source_intake_negative_controls.csv",
            "source_intake_negative_controls.json": "data/rev0064_source_intake_negative_controls.json",
            "source_intake_package_hygiene.csv": "data/rev0064_source_intake_package_hygiene.csv",
            "source_intake_package_hygiene.json": "data/rev0064_source_intake_package_hygiene.json",
            "source_intake_summary.json": "data/rev0064_source_intake_summary.json",
        }
        for src, dst in mappings.items():
            shutil.copy2(out_dir / src, ROOT / dst)

    print(json.dumps(summary, indent=2, sort_keys=True))
    cleanup_caches(ROOT)
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
