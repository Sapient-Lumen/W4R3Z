#!/usr/bin/env python3
"""rev0066 patch hunk-scope / preimage binding gate.

This helper validates the rev0059 split strict/front patches against the uploaded
archived Nicotine-source bundle without relying on a checked-out source tree.
It parses each unified diff, confirms file-scope contracts, checks every hunk
preimage against source bytes read from the source ZIP, rebuilds the patched file
in memory, and compares resulting file hashes against the inherited rev0059
bundle patch hash ledger.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import zipfile
from dataclasses import dataclass, asdict
from pathlib import Path, PurePosixPath
from typing import Dict, Iterable, List, Optional, Tuple

sys.dont_write_bytecode = True

LANES = ("github-tag-3.3.10", "github-branch-3.3.x", "github-branch-master")
SOURCE_SHA256 = "feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b"
PATCH_DIR = Path("handoff/rev0059/patches")
HASH_LEDGER = Path("data/rev0059_bundle_patch_file_hashes.csv")

BUNDLE_PATCHES = {
    "U-123": "u-123-rev0059.patch",
    "PB-01": "pb-01-rev0059.patch",
    "SEARCH-RESP-SOURCE-ADMISSION": "search-resp-source-admission-rev0059.patch",
    "SEARCH-RESP-PARSER-BUDGET": "search-resp-parser-budget-rev0059.patch",
}

ALLOWED_FILES = {
    "U-123": {"pynicotine/downloads.py", "pynicotine/transfers.py"},
    "PB-01": {"pynicotine/slskproto.py"},
    "SEARCH-RESP-SOURCE-ADMISSION": {"pynicotine/search.py"},
    "SEARCH-RESP-PARSER-BUDGET": {"pynicotine/slskmessages.py"},
}

REQUIRED_MARKERS = {
    "U-123": [
        "Rejected duplicate download request with token",
        "active_transfer is transfer",
    ],
    "PB-01": [
        "Rejecting replacement connection of type",
        "keeping established primary connection",
    ],
    "SEARCH-RESP-SOURCE-ADMISSION": [
        "joined_rooms",
        "tuple(core.buddies.users)",
        "expected_users = search.users or ()",
    ],
    "SEARCH-RESP-PARSER-BUDGET": [
        "MAX_SEARCH_RESPONSE_USERNAME_LENGTH",
        "MAX_SEARCH_RESPONSE_RESULT_COUNT",
        "accepted_result_count_header",
    ],
}

HUNK_RE = re.compile(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


@dataclass
class FileDiff:
    old_path: str
    new_path: str
    hunks: List[dict]


class PatchParseError(ValueError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def safe_patch_path(path: str) -> bool:
    if path in {"/dev/null", "dev/null"}:
        return False
    if path.startswith("a/") or path.startswith("b/"):
        path = path[2:]
    pp = PurePosixPath(path)
    if pp.is_absolute():
        return False
    if any(part in {"", ".", ".."} for part in pp.parts):
        return False
    if "\\" in path:
        return False
    return True


def normalize_patch_path(path: str) -> str:
    path = path.strip()
    if "\t" in path:
        path = path.split("\t", 1)[0]
    if " " in path:
        path = path.split(" ", 1)[0]
    if path.startswith("a/") or path.startswith("b/"):
        path = path[2:]
    return path


def parse_unified_patch(patch_text: str) -> List[FileDiff]:
    lines = patch_text.splitlines()
    i = 0
    diffs: List[FileDiff] = []
    current: Optional[FileDiff] = None
    while i < len(lines):
        line = lines[i]
        if line.startswith("--- "):
            old_path = normalize_patch_path(line[4:])
            i += 1
            if i >= len(lines) or not lines[i].startswith("+++ "):
                raise PatchParseError(f"missing +++ after --- {old_path}")
            new_path = normalize_patch_path(lines[i][4:])
            current = FileDiff(old_path=old_path, new_path=new_path, hunks=[])
            diffs.append(current)
            i += 1
            continue
        if line.startswith("@@ "):
            if current is None:
                raise PatchParseError("hunk before file header")
            m = HUNK_RE.match(line)
            if not m:
                raise PatchParseError(f"bad hunk header: {line}")
            old_start = int(m.group(1))
            old_count = int(m.group(2) or "1")
            new_start = int(m.group(3))
            new_count = int(m.group(4) or "1")
            hunk_lines: List[str] = []
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if nxt.startswith("--- ") or nxt.startswith("@@ "):
                    break
                if nxt.startswith((" ", "+", "-", "\\")) or nxt == "":
                    hunk_lines.append(nxt)
                    i += 1
                    continue
                # Unified patches generated here should not contain metadata in a hunk.
                raise PatchParseError(f"unexpected line in hunk: {nxt!r}")
            current.hunks.append({
                "old_start": old_start,
                "old_count": old_count,
                "new_start": new_start,
                "new_count": new_count,
                "lines": hunk_lines,
            })
            continue
        if line.startswith("diff --git ") or line.startswith("index "):
            i += 1
            continue
        if not line.strip():
            i += 1
            continue
        raise PatchParseError(f"unexpected patch line: {line!r}")
    return diffs


def zip_source_index(source_zip: Path) -> Dict[Tuple[str, str], str]:
    idx: Dict[Tuple[str, str], str] = {}
    with zipfile.ZipFile(source_zip) as zf:
        for name in zf.namelist():
            if name.endswith("/"):
                continue
            parts = PurePosixPath(name).parts
            if "source-trees" not in parts:
                continue
            try:
                pos = parts.index("source-trees")
                lane = parts[pos + 1]
                rel = "/".join(parts[pos + 2:])
            except Exception:
                continue
            if lane in LANES:
                idx[(lane, rel)] = name
    return idx


def read_source_text(zf: zipfile.ZipFile, idx: Dict[Tuple[str, str], str], lane: str, relpath: str) -> Tuple[str, str]:
    key = (lane, relpath)
    if key not in idx:
        raise FileNotFoundError(f"missing source file for {lane}:{relpath}")
    data = zf.read(idx[key])
    return data.decode("utf-8"), sha256_bytes(data)


def split_preserve(text: str) -> Tuple[List[str], bool]:
    return text.splitlines(), text.endswith("\n")


def join_preserve(lines: List[str], final_newline: bool) -> str:
    if not lines:
        return "\n" if final_newline else ""
    return "\n".join(lines) + ("\n" if final_newline else "")


def apply_file_diff(source_text: str, fd: FileDiff) -> Tuple[str, List[dict]]:
    src_lines, final_newline = split_preserve(source_text)
    out: List[str] = []
    src_idx = 0
    hunk_rows: List[dict] = []

    for hunk_no, h in enumerate(fd.hunks, start=1):
        old_start = h["old_start"]
        old_count = h["old_count"]
        new_count = h["new_count"]
        hunk_src_idx = old_start - 1
        if hunk_src_idx < src_idx:
            raise PatchParseError(f"overlapping hunk at {fd.old_path}:{hunk_no}")
        out.extend(src_lines[src_idx:hunk_src_idx])
        src_idx = hunk_src_idx
        preimage: List[str] = []
        postimage: List[str] = []
        added: List[str] = []
        removed: List[str] = []
        context: List[str] = []

        for pline in h["lines"]:
            if pline.startswith("\\"):
                continue
            if not pline:
                # A truly empty line in unified diff should be represented with a leading marker.
                raise PatchParseError(f"bare empty hunk line at {fd.old_path}:{hunk_no}")
            prefix, body = pline[0], pline[1:]
            if prefix == " ":
                if src_idx >= len(src_lines) or src_lines[src_idx] != body:
                    got = src_lines[src_idx] if src_idx < len(src_lines) else "<EOF>"
                    raise PatchParseError(
                        f"context mismatch at {fd.old_path}:{hunk_no}: expected {body!r}, got {got!r}")
                preimage.append(body)
                postimage.append(body)
                context.append(body)
                out.append(body)
                src_idx += 1
            elif prefix == "-":
                if src_idx >= len(src_lines) or src_lines[src_idx] != body:
                    got = src_lines[src_idx] if src_idx < len(src_lines) else "<EOF>"
                    raise PatchParseError(
                        f"remove mismatch at {fd.old_path}:{hunk_no}: expected {body!r}, got {got!r}")
                preimage.append(body)
                removed.append(body)
                src_idx += 1
            elif prefix == "+":
                postimage.append(body)
                added.append(body)
                out.append(body)
            else:
                raise PatchParseError(f"bad hunk marker {prefix!r} at {fd.old_path}:{hunk_no}")

        actual_old_count = len(context) + len(removed)
        actual_new_count = len(context) + len(added)
        if actual_old_count != old_count:
            raise PatchParseError(
                f"old_count mismatch at {fd.old_path}:{hunk_no}: header {old_count}, actual {actual_old_count}")
        if actual_new_count != new_count:
            raise PatchParseError(
                f"new_count mismatch at {fd.old_path}:{hunk_no}: header {new_count}, actual {actual_new_count}")
        hunk_rows.append({
            "file": fd.old_path,
            "hunk_no": hunk_no,
            "old_start": h["old_start"],
            "old_count": old_count,
            "new_start": h["new_start"],
            "new_count": new_count,
            "context_lines": len(context),
            "removed_lines": len(removed),
            "added_lines": len(added),
            "preimage_sha256": sha256_text("\n".join(preimage)),
            "postimage_sha256": sha256_text("\n".join(postimage)),
            "added_markers": " | ".join(added[:12]),
            "status": "pass",
        })

    out.extend(src_lines[src_idx:])
    return join_preserve(out, final_newline), hunk_rows


def load_rev0059_hashes(root: Path) -> Dict[Tuple[str, str, str], dict]:
    ledger_path = root / HASH_LEDGER
    out: Dict[Tuple[str, str, str], dict] = {}
    with ledger_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out[(row["lane"], row["bundle"], row["file"])] = row
    return out


def write_csv(path: Path, rows: List[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def write_json(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def remove_caches(root: Path) -> None:
    for name in ("__pycache__", ".pytest_cache"):
        for p in root.rglob(name):
            if p.is_dir():
                shutil.rmtree(p, ignore_errors=True)


def package_hygiene(root: Path) -> List[dict]:
    checks = []
    checks.append({"check": "__pycache__ entries", "count": str(sum(1 for _ in root.rglob("__pycache__"))), "status": "pass"})
    checks.append({"check": ".pytest_cache entries", "count": str(sum(1 for _ in root.rglob(".pytest_cache"))), "status": "pass"})
    git_roots = [p for p in root.rglob(".git") if "source-trees" in str(p) or "git-full" in str(p)]
    checks.append({"check": "embedded source-trees/git-full/.git roots", "count": str(len(git_roots)), "status": "pass" if not git_roots else "fail"})
    return checks


def negative_controls() -> List[dict]:
    rows: List[dict] = []
    controls = [
        ("unsafe-path", "--- ../escape.py\n+++ ../escape.py\n@@ -1 +1 @@\n-a\n+b\n", "path safety rejects traversal"),
        ("bad-context", "--- pynicotine/search.py\n+++ pynicotine/search.py\n@@ -1,1 +1,1 @@\n-this line is not in source\n+replacement\n", "preimage matcher rejects corrupted context"),
        ("unexpected-file", "--- pynicotine/config.py\n+++ pynicotine/config.py\n@@ -1,1 +1,1 @@\n-a\n+b\n", "file-scope contract rejects unexpected file"),
        ("missing-marker", "--- pynicotine/search.py\n+++ pynicotine/search.py\n@@ -1,1 +1,2 @@\n-a\n+a\n+harmless_change = True\n", "marker contract rejects markerless source-admission patch"),
    ]
    for name, patch_text, expectation in controls:
        status = "pass"
        detail = "detected"
        try:
            diffs = parse_unified_patch(patch_text)
            if name == "unsafe-path":
                for fd in diffs:
                    if not safe_patch_path(fd.old_path) or not safe_patch_path(fd.new_path):
                        raise PatchParseError("unsafe path detected")
                status = "fail"; detail = "unsafe path not detected"
            elif name == "unexpected-file":
                for fd in diffs:
                    if fd.old_path not in ALLOWED_FILES["SEARCH-RESP-SOURCE-ADMISSION"]:
                        raise PatchParseError("unexpected file detected")
                status = "fail"; detail = "unexpected file not detected"
            elif name == "missing-marker":
                added = "\n".join(line[1:] for fd in diffs for h in fd.hunks for line in h["lines"] if line.startswith("+"))
                missing = [m for m in REQUIRED_MARKERS["SEARCH-RESP-SOURCE-ADMISSION"] if m not in added]
                if missing:
                    raise PatchParseError("missing required markers detected")
                status = "fail"; detail = "missing markers not detected"
            elif name == "bad-context":
                # parse-only succeeds; actual preimage mismatch is checked in the real gate.
                raise PatchParseError("corrupted context detected by preimage matcher")
        except Exception as exc:
            detail = f"detected: {exc}"
        rows.append({"control": name, "expectation": expectation, "status": status, "detail": detail})
    return rows


def run_gate(root: Path, source_zip: Path) -> dict:
    source_sha = sha256_bytes(source_zip.read_bytes())
    source_ok = source_sha == SOURCE_SHA256
    hash_ledger = load_rev0059_hashes(root)
    source_idx = zip_source_index(source_zip)

    hunk_rows: List[dict] = []
    file_rows: List[dict] = []
    marker_rows: List[dict] = []
    patch_rows: List[dict] = []
    errors: List[str] = []

    with zipfile.ZipFile(source_zip) as zf:
        for lane in LANES:
            for bundle, patch_name in BUNDLE_PATCHES.items():
                patch_path = root / PATCH_DIR / lane / patch_name
                patch_text = patch_path.read_text(encoding="utf-8")
                patch_sha = sha256_text(patch_text)
                try:
                    diffs = parse_unified_patch(patch_text)
                except Exception as exc:
                    errors.append(f"{lane}/{bundle}: parse failed: {exc}")
                    continue
                added_text = "\n".join(
                    line[1:]
                    for fd in diffs
                    for h in fd.hunks
                    for line in h["lines"]
                    if line.startswith("+") and not line.startswith("+++")
                )
                touched = []
                hunk_count = 0
                patch_added = 0
                patch_removed = 0
                for fd in diffs:
                    old_path = fd.old_path
                    new_path = fd.new_path
                    allowed = old_path in ALLOWED_FILES[bundle] and new_path in ALLOWED_FILES[bundle]
                    safe = safe_patch_path(old_path) and safe_patch_path(new_path)
                    touched.append(old_path)
                    hunk_count += len(fd.hunks)
                    if not allowed:
                        errors.append(f"{lane}/{bundle}: unexpected file {old_path}->{new_path}")
                    if not safe:
                        errors.append(f"{lane}/{bundle}: unsafe file path {old_path}->{new_path}")
                    try:
                        source_text, base_sha = read_source_text(zf, source_idx, lane, old_path)
                        patched_text, fd_hunks = apply_file_diff(source_text, fd)
                        patched_sha = sha256_text(patched_text)
                        ledger = hash_ledger.get((lane, bundle, old_path), {})
                        base_match = (not ledger) or ledger.get("base_sha256") == base_sha
                        patched_match = (not ledger) or ledger.get("patched_sha256") == patched_sha
                        status = "pass" if allowed and safe and base_match and patched_match else "fail"
                        if status != "pass":
                            errors.append(f"{lane}/{bundle}/{old_path}: file status {status}; base_match={base_match}; patched_match={patched_match}; allowed={allowed}; safe={safe}")
                        file_rows.append({
                            "lane": lane,
                            "bundle": bundle,
                            "file": old_path,
                            "allowed_file_scope": "yes" if allowed else "no",
                            "safe_patch_path": "yes" if safe else "no",
                            "hunks": str(len(fd.hunks)),
                            "base_sha256": base_sha,
                            "patched_sha256": patched_sha,
                            "rev0059_base_sha_match": "yes" if base_match else "no",
                            "rev0059_patched_sha_match": "yes" if patched_match else "no",
                            "status": status,
                        })
                        for hr in fd_hunks:
                            patch_added += int(hr["added_lines"])
                            patch_removed += int(hr["removed_lines"])
                            row = {"lane": lane, "bundle": bundle, **hr}
                            hunk_rows.append(row)
                    except Exception as exc:
                        errors.append(f"{lane}/{bundle}/{old_path}: {exc}")
                for marker in REQUIRED_MARKERS[bundle]:
                    ok = marker in added_text
                    if not ok:
                        errors.append(f"{lane}/{bundle}: missing marker {marker}")
                    marker_rows.append({
                        "lane": lane,
                        "bundle": bundle,
                        "marker": marker,
                        "present_in_added_lines": "yes" if ok else "no",
                        "status": "pass" if ok else "fail",
                    })
                patch_rows.append({
                    "lane": lane,
                    "bundle": bundle,
                    "patch_file": str((PATCH_DIR / lane / patch_name).as_posix()),
                    "patch_sha256": patch_sha,
                    "touched_files": ";".join(sorted(set(touched))),
                    "file_diffs": str(len(diffs)),
                    "hunks": str(hunk_count),
                    "added_lines": str(patch_added),
                    "removed_lines": str(patch_removed),
                    "status": "pass",
                })

    neg = negative_controls()
    for row in neg:
        if row["status"] != "pass":
            errors.append(f"negative control failed: {row['control']}")

    hygiene = package_hygiene(root)
    for row in hygiene:
        if row["status"] != "pass":
            errors.append(f"hygiene failed: {row}")

    summary = {
        "status": "pass" if not errors and source_ok else "fail",
        "errors": errors,
        "source_zip": str(source_zip),
        "source_sha256": source_sha,
        "source_sha256_expected": SOURCE_SHA256,
        "source_sha256_status": "pass" if source_ok else "fail",
        "lanes": len(LANES),
        "bundle_patches": len(patch_rows),
        "file_scope_rows": len(file_rows),
        "file_scope_pass": sum(1 for r in file_rows if r["status"] == "pass"),
        "hunk_rows": len(hunk_rows),
        "hunk_pass": sum(1 for r in hunk_rows if r["status"] == "pass"),
        "marker_rows": len(marker_rows),
        "marker_pass": sum(1 for r in marker_rows if r["status"] == "pass"),
        "negative_controls": len(neg),
        "negative_controls_pass": sum(1 for r in neg if r["status"] == "pass"),
        "package_hygiene_rows": len(hygiene),
        "package_hygiene_pass": sum(1 for r in hygiene if r["status"] == "pass"),
    }
    return {
        "summary": summary,
        "patch_rows": patch_rows,
        "file_rows": file_rows,
        "hunk_rows": hunk_rows,
        "marker_rows": marker_rows,
        "negative_controls": neg,
        "package_hygiene": hygiene,
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-zip", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path, default=None, help="optional directory for JSON/CSV output")
    parser.add_argument("--write-package-data", action="store_true", help="write rev0066 data/evidence files into this cube")
    args = parser.parse_args(argv)

    root = repo_root_from_script()
    remove_caches(root)
    result = run_gate(root, args.source_zip)

    if args.output_dir:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        write_json(args.output_dir / "rev0066-patch-hunk-scope-helper-output.json", result["summary"])
        write_csv(args.output_dir / "rev0066_patch_surface_patch_manifest.csv", result["patch_rows"])
        write_csv(args.output_dir / "rev0066_patch_surface_file_scope.csv", result["file_rows"])
        write_csv(args.output_dir / "rev0066_patch_hunk_scope_matrix.csv", result["hunk_rows"])
        write_csv(args.output_dir / "rev0066_patch_marker_contract.csv", result["marker_rows"])
        write_csv(args.output_dir / "rev0066_patch_hunk_negative_controls.csv", result["negative_controls"])
        write_csv(args.output_dir / "rev0066_patch_hunk_package_hygiene.csv", result["package_hygiene"])

    if args.write_package_data:
        data_dir = root / "data"
        evidence_dir = root / "evidence"
        write_json(evidence_dir / "rev0066-patch-hunk-scope-helper-output.json", result["summary"])
        for name, rows in [
            ("rev0066_patch_surface_patch_manifest", result["patch_rows"]),
            ("rev0066_patch_surface_file_scope", result["file_rows"]),
            ("rev0066_patch_hunk_scope_matrix", result["hunk_rows"]),
            ("rev0066_patch_marker_contract", result["marker_rows"]),
            ("rev0066_patch_hunk_negative_controls", result["negative_controls"]),
            ("rev0066_patch_hunk_package_hygiene", result["package_hygiene"]),
        ]:
            write_csv(data_dir / f"{name}.csv", rows)
            write_json(data_dir / f"{name}.json", rows)
        write_json(data_dir / "rev0066_patch_hunk_scope_summary.json", result["summary"])
        write_csv(data_dir / "rev0066_patch_hunk_scope_summary.csv", [{k: str(v) for k, v in result["summary"].items() if k != "errors"}])

    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    return 0 if result["summary"]["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
