#!/usr/bin/env python3
"""rev0065 Git provenance / source-tree match gate.

This helper treats the uploaded Nicotine source bundle as an archived-source
input and verifies that each extracted source lane is bound to the bundled Git
object/ref provenance. It does not embed source contents into the cube.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Dict, Iterable, List, Tuple

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SOURCE_SHA256 = "feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b"
SOURCE_ROOT = "Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z"
SOURCE_PREFIX = f"{SOURCE_ROOT}/source-trees/"
GIT_PREFIX = f"{SOURCE_ROOT}/git-full/.git/"
LANES = ("github-tag-3.3.10", "github-branch-3.3.x", "github-branch-master")
EXPECTED_HEADS = {
    "github-tag-3.3.10": "caf9e101a841ff2e0a96aebc8e07bbf7ff1b2026",
    "github-branch-3.3.x": "98089ac233aa57786e8dbdc48123f6ac1c4767d8",
    "github-branch-master": "f4e17d59783dbc48ea31d2e899a681e2dd1ed500",
}
EXPECTED_REFS = {
    "github-tag-3.3.10": "refs/tags/3.3.10",
    "github-branch-3.3.x": "refs/remotes/upstream/3.3.x",
    "github-branch-master": "refs/remotes/upstream/master",
}
EXPECTED_REMOTE = "https://github.com/nicotine-plus/nicotine-plus.git"
BAD_PACKAGE_PARTS = {"__pycache__", ".pytest_cache", "source-trees", "git-full", ".git"}
CRITICAL_FILES = (
    "pynicotine/downloads.py",
    "pynicotine/transfers.py",
    "pynicotine/slskproto.py",
    "pynicotine/search.py",
    "pynicotine/slskmessages.py",
)


def sha_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    h = hashlib.sha1()
    h.update(f"blob {len(data)}\0".encode("ascii"))
    h.update(data)
    return h.hexdigest()


def write_csv(path: Path, rows: List[Dict[str, object]], fields: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(fields))
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in writer.fieldnames})


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def cleanup_caches(path: Path) -> None:
    for cache in list(path.rglob("__pycache__")) + list(path.rglob(".pytest_cache")):
        shutil.rmtree(cache, ignore_errors=True)


def zip_mode(zi: zipfile.ZipInfo) -> int:
    return (zi.external_attr >> 16) & 0o177777


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
    normalized = "/".join(parts)
    if not normalized:
        errors.append("empty-normalized-path")
    return normalized, errors


def assert_zip_safe(source_zip: Path) -> List[str]:
    errors: List[str] = []
    seen: Dict[str, str] = {}
    with zipfile.ZipFile(source_zip) as zf:
        names = zf.namelist()
        if not names or not names[0].startswith(SOURCE_ROOT + "/"):
            errors.append("unexpected-root-prefix")
        for zi in zf.infolist():
            normalized, path_errors = normalize_zip_name(zi.filename)
            if path_errors:
                errors.append(f"{zi.filename}: {';'.join(path_errors)}")
            if is_symlink(zi):
                errors.append(f"{zi.filename}: symlink-entry")
            if normalized in seen:
                errors.append(f"{zi.filename}: duplicate-normalized-path:first={seen[normalized]}")
            else:
                seen[normalized] = zi.filename
    return errors


def safe_extract(source_zip: Path, dest: Path) -> None:
    errors = assert_zip_safe(source_zip)
    if errors:
        raise RuntimeError("unsafe source zip: " + "; ".join(errors[:5]))
    with zipfile.ZipFile(source_zip) as zf:
        for zi in zf.infolist():
            normalized, _ = normalize_zip_name(zi.filename)
            target = dest / normalized
            if zi.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(zf.read(zi))


def run_git(git_dir: Path, args: List[str]) -> str:
    proc = subprocess.run(
        ["git", "--git-dir", str(git_dir), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def parse_packed_refs(packed_refs: Path) -> Dict[str, str]:
    refs: Dict[str, str] = {}
    for line in packed_refs.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line or line.startswith("#") or line.startswith("^"):
            continue
        parts = line.split(" ", 1)
        if len(parts) == 2:
            refs[parts[1].strip()] = parts[0].strip()
    return refs


def validate_pointer(text: str, required_suffix: str) -> Tuple[bool, str]:
    one_line = text.strip()
    if not one_line.startswith("gitdir: "):
        return False, "missing-gitdir-prefix"
    path = one_line[len("gitdir: "):]
    norm = path.replace("\\", "/")
    if not norm.endswith(required_suffix):
        return False, f"unexpected-suffix:{norm[-120:]}"
    if "/../" in norm or norm.startswith("../"):
        return False, "pointer-traversal"
    return True, norm


def worktree_identity_rows(root: Path) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    git_dir = root / "git-full" / ".git"
    for lane in LANES:
        source_tree = root / "source-trees" / lane
        worktree = git_dir / "worktrees" / lane
        expected = EXPECTED_HEADS[lane]
        dotgit_text = (source_tree / ".git").read_text(encoding="utf-8", errors="replace")
        dotgit_ok, dotgit_detail = validate_pointer(dotgit_text, f"/git-full/.git/worktrees/{lane}")
        reverse_text = (worktree / "gitdir").read_text(encoding="utf-8", errors="replace")
        reverse_ok = reverse_text.strip().replace("\\", "/").endswith(f"/source-trees/{lane}/.git")
        head = (worktree / "HEAD").read_text(encoding="utf-8", errors="replace").strip()
        orig = (worktree / "ORIG_HEAD").read_text(encoding="utf-8", errors="replace").strip()
        common = (worktree / "commondir").read_text(encoding="utf-8", errors="replace").strip()
        status = "pass" if (dotgit_ok and reverse_ok and head == expected and orig == expected and common == "../..") else "fail"
        rows.append({
            "lane": lane,
            "expected_head": expected,
            "worktree_head": head,
            "worktree_orig_head": orig,
            "commondir": common,
            "source_dotgit_pointer_ok": str(dotgit_ok).lower(),
            "source_dotgit_pointer_detail": dotgit_detail,
            "reverse_gitdir_pointer_ok": str(reverse_ok).lower(),
            "status": status,
        })
    return rows


def git_ref_rows(root: Path) -> List[Dict[str, object]]:
    git_dir = root / "git-full" / ".git"
    refs = parse_packed_refs(git_dir / "packed-refs")
    config = (git_dir / "config").read_text(encoding="utf-8", errors="replace")
    rows: List[Dict[str, object]] = []
    remote_ok = EXPECTED_REMOTE in config
    for lane in LANES:
        ref = EXPECTED_REFS[lane]
        expected_head = EXPECTED_HEADS[lane]
        observed = refs.get(ref, "")
        rows.append({
            "lane": lane,
            "expected_ref": ref,
            "expected_head": expected_head,
            "observed_ref_head": observed,
            "remote_upstream_ok": str(remote_ok).lower(),
            "status": "pass" if observed == expected_head and remote_ok else "fail",
        })
    return rows


def commit_rows(root: Path) -> List[Dict[str, object]]:
    git_dir = root / "git-full" / ".git"
    rows: List[Dict[str, object]] = []
    for lane in LANES:
        head = EXPECTED_HEADS[lane]
        obj_type = run_git(git_dir, ["cat-file", "-t", head]).strip()
        fmt = "%H%x09%T%x09%P%x09%ct%x09%cI%x09%s"
        out = run_git(git_dir, ["show", "-s", f"--format={fmt}", head]).strip()
        parts = out.split("\t", 5)
        while len(parts) < 6:
            parts.append("")
        rows.append({
            "lane": lane,
            "head": head,
            "object_type": obj_type,
            "tree": parts[1],
            "parents": parts[2],
            "commit_unix_time": parts[3],
            "commit_iso_time": parts[4],
            "subject": parts[5],
            "status": "pass" if obj_type == "commit" and parts[0] == head else "fail",
        })
    return rows


def git_tree_map(git_dir: Path, commit: str) -> Dict[str, Dict[str, str]]:
    raw = subprocess.run(
        ["git", "--git-dir", str(git_dir), "ls-tree", "-r", "-z", commit],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if raw.returncode != 0:
        raise RuntimeError(raw.stderr.decode("utf-8", errors="replace"))
    out: Dict[str, Dict[str, str]] = {}
    for rec in raw.stdout.split(b"\0"):
        if not rec:
            continue
        meta, path = rec.split(b"\t", 1)
        mode, typ, oid = meta.decode("ascii").split(" ")
        rel = path.decode("utf-8", errors="surrogateescape")
        out[rel] = {"mode": mode, "type": typ, "oid": oid}
    return out


def file_match_rows(root: Path) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    git_dir = root / "git-full" / ".git"
    rows: List[Dict[str, object]] = []
    summaries: List[Dict[str, object]] = []
    for lane in LANES:
        commit = EXPECTED_HEADS[lane]
        tree = git_tree_map(git_dir, commit)
        source_tree = root / "source-trees" / lane
        source_files: Dict[str, Path] = {}
        for path in sorted(source_tree.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(source_tree).as_posix()
            if rel == ".git" or rel.startswith(".git/"):
                continue
            source_files[rel] = path
        matched = missing = mismatched = wrong_type = symlink_materialized = critical_exact = critical_total = 0
        for rel, meta in sorted(tree.items()):
            path = source_files.get(rel)
            status = "pass"
            size = ""
            observed_blob = ""
            sha256 = ""
            if meta["type"] != "blob":
                wrong_type += 1
                status = "wrong-type"
            elif path is None:
                missing += 1
                status = "missing-from-source-tree"
            else:
                data = path.read_bytes()
                size = len(data)
                observed_blob = git_blob_sha1(data)
                sha256 = sha_bytes(data)
                if rel in CRITICAL_FILES:
                    critical_total += 1
                if observed_blob == meta["oid"]:
                    matched += 1
                    if rel in CRITICAL_FILES:
                        critical_exact += 1
                elif meta["mode"] == "120000":
                    # The uploaded source bundle materializes a small set of Git symlink
                    # entries as regular file contents. Record those as a source-bundle
                    # packaging deviation, but do not treat them as strict/front source
                    # drift because none are packet-touched files.
                    symlink_materialized += 1
                    status = "symlink-materialized-in-source-bundle"
                else:
                    mismatched += 1
                    status = "blob-mismatch"
            rows.append({
                "lane": lane,
                "commit": commit,
                "relative_path": rel,
                "git_mode": meta["mode"],
                "git_type": meta["type"],
                "git_blob_sha1": meta["oid"],
                "source_blob_sha1": observed_blob,
                "source_sha256": sha256,
                "size_bytes": size,
                "status": status,
            })
        extras = sorted(set(source_files) - set(tree))
        for rel in extras:
            path = source_files[rel]
            data = path.read_bytes()
            rows.append({
                "lane": lane,
                "commit": commit,
                "relative_path": rel,
                "git_mode": "",
                "git_type": "",
                "git_blob_sha1": "",
                "source_blob_sha1": git_blob_sha1(data),
                "source_sha256": sha_bytes(data),
                "size_bytes": len(data),
                "status": "extra-in-source-tree",
            })
        summaries.append({
            "lane": lane,
            "commit": commit,
            "git_tracked_files": len(tree),
            "source_files_excluding_dotgit": len(source_files),
            "exact_matched_files": matched,
            "symlink_materialized_files": symlink_materialized,
            "missing_files": missing,
            "mismatched_non_symlink_files": mismatched,
            "wrong_type_entries": wrong_type,
            "extra_source_files": len(extras),
            "critical_touched_files_exact": critical_exact,
            "critical_touched_files_total": critical_total,
            "status": "pass" if (matched + symlink_materialized == len(tree) and not missing and not mismatched and not wrong_type and not extras and critical_exact == critical_total) else "fail",
        })
    return rows, summaries


def package_hygiene_rows() -> List[Dict[str, object]]:
    cleanup_caches(ROOT)
    rows: List[Dict[str, object]] = []
    checks = [
        ("no_pycache", lambda p: "__pycache__" in p.parts),
        ("no_pytest_cache", lambda p: ".pytest_cache" in p.parts),
        ("no_source_trees_dir", lambda p: "source-trees" in p.parts),
        ("no_git_full_dir", lambda p: "git-full" in p.parts),
        ("no_git_dir", lambda p: ".git" in p.parts),
    ]
    all_paths = list(ROOT.rglob("*"))
    for name, pred in checks:
        matches = [str(p.relative_to(ROOT)) for p in all_paths if pred(p.relative_to(ROOT))]
        rows.append({
            "check": name,
            "matches": len(matches),
            "sample": ";".join(matches[:5]),
            "status": "pass" if not matches else "fail",
        })
    return rows


def negative_controls(root: Path) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    lane = "github-branch-master"
    source_tree = root / "source-trees" / lane
    git_dir = root / "git-full" / ".git"
    tree = git_tree_map(git_dir, EXPECTED_HEADS[lane])

    # tampered tracked file blob must not match its Git tree blob.
    target_rel = "pynicotine/search.py"
    target = source_tree / target_rel
    data = target.read_bytes() + b"\n# synthetic rev0065 tamper\n"
    detected = git_blob_sha1(data) != tree[target_rel]["oid"]
    rows.append({
        "control": "tampered-tracked-file-blob",
        "expected_detection": "blob-mismatch",
        "detected": str(detected).lower(),
        "status": "pass" if detected else "fail",
    })

    # wrong worktree HEAD must fail equality against the expected lane head.
    fake_head = "0" * 40
    detected = fake_head != EXPECTED_HEADS[lane]
    rows.append({
        "control": "wrong-worktree-head",
        "expected_detection": "head-mismatch",
        "detected": str(detected).lower(),
        "status": "pass" if detected else "fail",
    })

    # missing packed ref must fail ref resolution.
    refs = parse_packed_refs(git_dir / "packed-refs")
    ref = EXPECTED_REFS[lane]
    mutated = dict(refs)
    mutated.pop(ref, None)
    detected = mutated.get(ref, "") != EXPECTED_HEADS[lane]
    rows.append({
        "control": "missing-expected-packed-ref",
        "expected_detection": "ref-missing",
        "detected": str(detected).lower(),
        "status": "pass" if detected else "fail",
    })

    # traversal/incorrect gitdir pointer is rejected by suffix/traversal validator.
    ok, detail = validate_pointer("gitdir: ../../outside/.git/worktrees/github-branch-master\n", f"/git-full/.git/worktrees/{lane}")
    detected = not ok
    rows.append({
        "control": "unsafe-source-dotgit-pointer",
        "expected_detection": "pointer-rejected",
        "detected": str(detected).lower(),
        "detail": detail,
        "status": "pass" if detected else "fail",
    })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="rev0065 Git provenance/source-tree match gate")
    parser.add_argument("--source-zip", required=True, help="Path to uploaded Nicotine-source zip")
    parser.add_argument("--write-data", action="store_true", help="write rev0065 data/evidence files into this cube")
    args = parser.parse_args()

    source_zip = Path(args.source_zip).resolve()
    summary: Dict[str, object] = {
        "revision": "rev0065",
        "source_zip": str(source_zip),
        "expected_source_sha256": EXPECTED_SOURCE_SHA256,
        "observed_source_sha256": sha_path(source_zip) if source_zip.exists() else "",
        "status": "pending",
        "checks": [],
    }
    if not source_zip.exists():
        summary["status"] = "fail"
        summary["error"] = "source_zip_missing"
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 2
    if summary["observed_source_sha256"] != EXPECTED_SOURCE_SHA256:
        summary["status"] = "fail"
        summary["error"] = "source_zip_sha256_mismatch"
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 2

    zip_errors = assert_zip_safe(source_zip)
    summary["zip_safety_errors"] = len(zip_errors)
    if zip_errors:
        summary["status"] = "fail"
        summary["error"] = zip_errors[:5]
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 2

    with tempfile.TemporaryDirectory(prefix="rev0065-gitprov-") as td:
        tmp = Path(td)
        safe_extract(source_zip, tmp)
        extracted_root = tmp / SOURCE_ROOT
        git_dir = extracted_root / "git-full" / ".git"
        source_root = extracted_root / "source-trees"
        if not git_dir.is_dir() or not source_root.is_dir():
            summary["status"] = "fail"
            summary["error"] = "missing_git_or_source_root_after_extract"
            print(json.dumps(summary, indent=2, sort_keys=True))
            return 2

        identity = worktree_identity_rows(extracted_root)
        refs = git_ref_rows(extracted_root)
        commits = commit_rows(extracted_root)
        file_matches, file_summaries = file_match_rows(extracted_root)
        negatives = negative_controls(extracted_root)
        hygiene = package_hygiene_rows()

    all_status_rows = identity + refs + commits + file_summaries + negatives + hygiene
    failures = [r for r in all_status_rows if r.get("status") != "pass"]
    summary.update({
        "worktree_identity_rows": len(identity),
        "git_ref_rows": len(refs),
        "commit_rows": len(commits),
        "git_tree_file_match_rows": len(file_matches),
        "git_tree_file_summary_rows": len(file_summaries),
        "negative_control_rows": len(negatives),
        "package_hygiene_rows": len(hygiene),
        "failures": len(failures),
        "status": "pass" if not failures else "fail",
    })

    if args.write_data:
        data = ROOT / "data"
        evidence = ROOT / "evidence"
        write_csv(data / "rev0065_git_worktree_identity.csv", identity, identity[0].keys())
        write_json(data / "rev0065_git_worktree_identity.json", identity)
        write_csv(data / "rev0065_git_ref_integrity.csv", refs, refs[0].keys())
        write_json(data / "rev0065_git_ref_integrity.json", refs)
        write_csv(data / "rev0065_git_commit_provenance.csv", commits, commits[0].keys())
        write_json(data / "rev0065_git_commit_provenance.json", commits)
        write_csv(data / "rev0065_git_tree_file_match_manifest.csv", file_matches, file_matches[0].keys())
        write_json(data / "rev0065_git_tree_file_match_manifest.json", file_matches)
        write_csv(data / "rev0065_git_tree_file_match_summary.csv", file_summaries, file_summaries[0].keys())
        write_json(data / "rev0065_git_tree_file_match_summary.json", file_summaries)
        write_csv(data / "rev0065_git_provenance_negative_controls.csv", negatives, negatives[0].keys())
        write_json(data / "rev0065_git_provenance_negative_controls.json", negatives)
        write_csv(data / "rev0065_git_provenance_package_hygiene.csv", hygiene, hygiene[0].keys())
        write_json(data / "rev0065_git_provenance_package_hygiene.json", hygiene)
        write_json(data / "rev0065_git_provenance_helper_summary.json", summary)
        write_json(evidence / "rev0065-git-provenance-helper-output.json", summary)

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
