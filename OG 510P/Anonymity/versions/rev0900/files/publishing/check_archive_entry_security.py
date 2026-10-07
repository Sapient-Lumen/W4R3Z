#!/usr/bin/env python3
"""Check filesystem and zip-entry security properties for the archive.

Path portability says *names* are safe.  This guard checks entry *types* and
metadata: no symlinks or special files in the tree, executable bits only on
publishing Python tools, and deterministic zip members that are plain regular
file payloads with safe paths, modes, empty comments/extra fields, and no
archive features such as encryption.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import stat
import sys
import tempfile
import zipfile
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_archive_zip  # noqa: E402

ALLOWED_FILE_MODES = {0o644, 0o755}


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def is_allowed_executable(rel: str) -> bool:
    return rel.startswith("publishing/") and rel.endswith(".py")


def safe_zip_name(name: str) -> bool:
    parts = name.split("/")
    return bool(name) and not name.startswith(("/", "../")) and "\\" not in name and all(part not in {"", ".", ".."} for part in parts)


def check_tree_entries(root: pathlib.Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    file_count = 0
    dir_count = 0
    executable_count = 0
    symlink_count = 0
    special_count = 0
    mode_failures = 0
    for path in sorted(root.rglob("*"), key=lambda p: p.relative_to(root).as_posix()):
        rel = path.relative_to(root).as_posix()
        st = path.lstat()
        mode = st.st_mode
        if stat.S_ISLNK(mode):
            symlink_count += 1
            failures.append({"category": "tree_symlink_disallowed", "path": rel})
            continue
        if stat.S_ISDIR(mode):
            dir_count += 1
            if mode & 0o002:
                failures.append({"category": "tree_world_writable_directory", "path": rel, "mode": oct(mode & 0o777)})
            continue
        if not stat.S_ISREG(mode):
            special_count += 1
            failures.append({"category": "tree_special_file_disallowed", "path": rel, "mode": oct(mode & 0o777)})
            continue
        file_count += 1
        perms = mode & 0o777
        if perms not in ALLOWED_FILE_MODES:
            mode_failures += 1
            failures.append({"category": "tree_file_mode_not_allowed", "path": rel, "mode": oct(perms), "allowed": [oct(m) for m in sorted(ALLOWED_FILE_MODES)]})
        if perms & 0o111:
            executable_count += 1
            if not is_allowed_executable(rel):
                failures.append({"category": "tree_unexpected_executable", "path": rel, "mode": oct(perms)})
        if mode & 0o002:
            failures.append({"category": "tree_world_writable_file", "path": rel, "mode": oct(perms)})
        if st.st_nlink > 1:
            failures.append({"category": "tree_hardlink_count_gt_one", "path": rel, "nlink": st.st_nlink})
    summary = {
        "tree_file_count": file_count,
        "tree_directory_count": dir_count,
        "tree_executable_file_count": executable_count,
        "tree_symlink_count": symlink_count,
        "tree_special_file_count": special_count,
        "tree_mode_failure_count": mode_failures,
    }
    return failures, summary


def check_zip_entries(root: pathlib.Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    release = load_json(root / "RELEASE_MANIFEST.json")
    with tempfile.TemporaryDirectory(prefix="anonymity_entry_security_zip_") as tmp:
        try:
            report = build_archive_zip.build_zip(root, pathlib.Path(tmp))
        except Exception as exc:  # noqa: BLE001 - report fail-closed instead of crashing.
            return [{"category": "deterministic_zip_build_failed", "error": str(exc)}], {"zip_member_count": 0}
        zip_path = pathlib.Path(str(report.get("written_zip", pathlib.Path(tmp) / release["bundle"])))
        if report.get("status") != "pass" or not zip_path.exists():
            return [{"category": "deterministic_zip_build_failed", "report": report}], {"zip_member_count": 0}
        with zipfile.ZipFile(zip_path, "r") as zf:
            members = zf.infolist()
            if zf.comment:
                failures.append({"category": "zip_archive_comment_disallowed", "length": len(zf.comment)})
            names = [info.filename for info in members]
            for info in members:
                perms = (info.external_attr >> 16) & 0o777
                file_type = (info.external_attr >> 16) & 0o170000
                if not safe_zip_name(info.filename):
                    failures.append({"category": "zip_member_path_unsafe", "path": info.filename})
                if info.is_dir():
                    failures.append({"category": "zip_directory_entry_disallowed", "path": info.filename})
                if file_type == stat.S_IFLNK:
                    failures.append({"category": "zip_symlink_entry_disallowed", "path": info.filename})
                if perms not in ALLOWED_FILE_MODES:
                    failures.append({"category": "zip_member_mode_not_allowed", "path": info.filename, "mode": oct(perms)})
                if perms & 0o111 and not is_allowed_executable(info.filename):
                    failures.append({"category": "zip_unexpected_executable", "path": info.filename, "mode": oct(perms)})
                if info.flag_bits & 0x1:
                    failures.append({"category": "zip_encrypted_member_disallowed", "path": info.filename})
                if info.extra:
                    failures.append({"category": "zip_extra_field_disallowed", "path": info.filename, "length": len(info.extra)})
                if info.comment:
                    failures.append({"category": "zip_member_comment_disallowed", "path": info.filename, "length": len(info.comment)})
    summary = {
        "zip_member_count": len(names),
        "zip_duplicate_member_count": len(names) - len(set(names)),
        "zip_mode_failure_count": sum(1 for f in failures if f.get("category") == "zip_member_mode_not_allowed"),
        "zip_path_failure_count": sum(1 for f in failures if f.get("category") == "zip_member_path_unsafe"),
        "zip_symlink_entry_count": sum(1 for f in failures if f.get("category") == "zip_symlink_entry_disallowed"),
        "zip_directory_entry_count": sum(1 for f in failures if f.get("category") == "zip_directory_entry_disallowed"),
    }
    if summary["zip_duplicate_member_count"]:
        failures.append({"category": "zip_duplicate_members", "count": summary["zip_duplicate_member_count"]})
    return failures, summary


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    tree_failures, tree_summary = check_tree_entries(root)
    zip_failures, zip_summary = check_zip_entries(root)
    failures = tree_failures + zip_failures
    summary = {
        "checks_failed": len(failures),
        **tree_summary,
        **zip_summary,
        "unexpected_executable_count": sum(1 for f in failures if f.get("category") in {"tree_unexpected_executable", "zip_unexpected_executable"}),
        "symlink_or_special_count": tree_summary.get("tree_symlink_count", 0) + tree_summary.get("tree_special_file_count", 0) + zip_summary.get("zip_symlink_entry_count", 0),
    }
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "allowed_file_modes": [oct(m) for m in sorted(ALLOWED_FILE_MODES)],
        "allowed_executable_rule": "only publishing/*.py may carry executable bits",
        "summary": summary,
        "failures": failures[:100],
        "fail_closed_rule": "If archive entries are symlinks, special files, unexpected executables, or unsafe zip members, do not distribute the package until entry metadata is repaired.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = root / args.write_report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
