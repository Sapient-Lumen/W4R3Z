#!/usr/bin/env python3
"""Fail-closed verifier for a full-source AnonSync release directory or ZIP."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Callable

MANIFEST_RE = re.compile(r"^([0-9a-f]{64})  (.+)$")
REVISION_RE = re.compile(r"^rev[0-9]{4}$")
ACTIVE_PROJECTION_V1_PREFIXES = ("include/", "src/", "tests/", "tools/", "third_party/")
ACTIVE_PROJECTION_V2_PREFIXES = (*ACTIVE_PROJECTION_V1_PREFIXES, "fuzz/")
ACTIVE_PROJECTION_FIXED_FILES = {".gitignore", "CMakeLists.txt"}
FORBIDDEN_SUFFIXES = {
    ".a", ".o", ".obj", ".so", ".dylib", ".dll", ".exe", ".pdb", ".pyc",
    ".profraw", ".gcda", ".gcno", ".class",
}
FORBIDDEN_PARTS = {
    ".git", ".svn", "__pycache__", "CMakeFiles", "Testing", "node_modules",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compute_active_projection(
    names: set[str],
    read: Callable[[str], bytes],
    *,
    include_fuzz: bool,
) -> dict[str, object]:
    prefixes = ACTIVE_PROJECTION_V2_PREFIXES if include_fuzz else ACTIVE_PROJECTION_V1_PREFIXES
    active_names = sorted(
        name for name in names
        if name in ACTIVE_PROJECTION_FIXED_FILES or name.startswith(prefixes)
    )
    files: list[dict[str, object]] = []
    material = bytearray()
    total_bytes = 0
    for name in active_names:
        data = read(name)
        digest = sha256_bytes(data)
        total_bytes += len(data)
        files.append({"bytes": len(data), "path": name, "sha256": digest})
        material.extend(f"{digest}  {name}\n".encode("utf-8"))
    return {
        "bytes": total_bytes,
        "file_count": len(files),
        "files": files,
        "sha256": sha256_bytes(bytes(material)),
    }


def normalized_member(name: str) -> PurePosixPath:
    if "\\" in name or "\x00" in name:
        raise ValueError(f"unsafe archive member spelling: {name!r}")
    path = PurePosixPath(name)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"unsafe archive member path: {name!r}")
    return path


def parse_manifest(data: bytes) -> dict[str, str]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"MANIFEST.sha256 is not UTF-8: {error}") from error
    result: dict[str, str] = {}
    for line_number, line in enumerate(text.splitlines(), 1):
        match = MANIFEST_RE.fullmatch(line)
        if not match:
            raise ValueError(f"invalid manifest line {line_number}: {line!r}")
        digest, rel = match.groups()
        path = normalized_member(rel)
        canonical = path.as_posix()
        if canonical == "MANIFEST.sha256":
            raise ValueError("manifest must not recursively list itself")
        if canonical in result:
            raise ValueError(f"duplicate manifest path: {canonical}")
        result[canonical] = digest
    return result


def package_checks(names: set[str], read: Callable[[str], bytes], expected_revision: str | None) -> tuple[list[dict[str, object]], dict[str, object]]:
    checks: list[dict[str, object]] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append({"check_id": check_id, "passed": bool(condition), "detail": detail})

    required = {
        "CMakeLists.txt",
        "README.md",
        "RELEASE_GATE.json",
        "MANIFEST.sha256",
        "include/anonsync_core.hpp",
        "src/sync_sqlite_process_incarnation.cpp",
        "src/sync_sqlite_handle_slot.hpp",
        "src/sync_sqlite_handle_slot.cpp",
        "src/sync_sqlite_support.cpp",
        "src/sqlite_replay_ledger.cpp",
        "tests/sqlite_process_authority_fork_test.cpp",
        "tools/audit_sqlite_process_authority.py",
        "tools/verify_release_package.py",
    }
    missing = sorted(required - names)
    require(not missing, "required_files_present", "missing: " + ", ".join(missing) if missing else "all required source, test, audit, and release files are present")

    source_cpp = sorted(name for name in names if name.startswith("src/") and name.endswith((".cpp", ".cc", ".cxx")))
    source_headers = sorted(name for name in names if name.startswith(("src/", "include/")) and name.endswith((".h", ".hpp", ".hh", ".hxx")))
    tests = sorted(name for name in names if name.startswith("tests/") and name.endswith((".cpp", ".cc", ".cxx")))
    require(len(source_cpp) >= 20, "full_source_tree_present", f"production implementation files={len(source_cpp)} (minimum 20)")
    require(len(source_headers) >= 10, "full_header_tree_present", f"production header files={len(source_headers)} (minimum 10)")
    require(len(tests) >= 10, "full_test_tree_present", f"test implementation files={len(tests)} (minimum 10)")

    forbidden: list[str] = []
    for name in sorted(names):
        path = PurePosixPath(name)
        if any(part in FORBIDDEN_PARTS or part.startswith("build-") for part in path.parts):
            forbidden.append(name)
        elif path.suffix.lower() in FORBIDDEN_SUFFIXES:
            forbidden.append(name)
        elif path.name in {"CMakeCache.txt", "cmake_install.cmake", "core", "core.dump"}:
            forbidden.append(name)
    require(not forbidden, "generated_and_binary_artifacts_absent", "forbidden entries: " + ", ".join(forbidden[:30]) if forbidden else "no VCS metadata, build trees, object files, binaries, or Python cache files")

    release_gate: dict[str, object] = {}
    try:
        release_gate = json.loads(read("RELEASE_GATE.json"))
        require(isinstance(release_gate, dict), "release_gate_is_json_object", "RELEASE_GATE.json parses as one object")
    except Exception as error:
        require(False, "release_gate_is_json_object", f"RELEASE_GATE.json parse failed: {error}")
    revision = str(release_gate.get("revision", "")) if isinstance(release_gate, dict) else ""
    require(bool(REVISION_RE.fullmatch(revision)), "release_gate_revision_is_canonical", f"revision={revision!r}")
    if expected_revision is not None:
        require(revision == expected_revision, "release_gate_revision_matches_expected", f"expected={expected_revision} actual={revision}")
    require(release_gate.get("required_gate_passed") is True, "required_release_gate_passed", "the package may not publish a failed or absent required gate")
    required_gate = release_gate.get("required") if isinstance(release_gate, dict) else None
    require(isinstance(required_gate, dict) and bool(required_gate) and all(value is True for value in required_gate.values()), "every_required_gate_entry_is_true", "all named required release conditions must be true")

    if REVISION_RE.fullmatch(revision):
        revision_files = {
            f"REVISION_NOTES_{revision}.md",
            f"REVISION_EVIDENCE/{revision}/ACTIVE_IMPLEMENTATION_PROJECTION.json",
            f"REVISION_EVIDENCE/{revision}/AUDIT.md",
            f"REVISION_EVIDENCE/{revision}/LINEAGE.md",
            f"REVISION_EVIDENCE/{revision}/LINEAGE.json",
            f"REVISION_EVIDENCE/{revision}/validation/VALIDATION_SUMMARY.json",
        }
        missing_revision = sorted(revision_files - names)
        require(not missing_revision, "revision_handoff_evidence_present", "missing: " + ", ".join(missing_revision) if missing_revision else "revision notes, lineage, active projection, audit, and validation summary are present")

        projection_path = f"REVISION_EVIDENCE/{revision}/ACTIVE_IMPLEMENTATION_PROJECTION.json"
        try:
            projection = json.loads(read(projection_path))
            projection_format = projection.get("format")
            include_fuzz = projection_format == "anonsync-active-implementation-projection-v2"
            require(
                projection_format in {None, "anonsync-active-projection-v1",
                                      "anonsync-active-implementation-projection-v1",
                                      "anonsync-active-implementation-projection-v2"},
                "active_projection_format_supported",
                f"format={projection_format!r}; absent format is the legacy v1 representation",
            )
            actual_projection = compute_active_projection(
                names, read, include_fuzz=include_fuzz)
            declared_digest = projection.get("sha256", projection.get("expected_sha256"))
            require(
                declared_digest == actual_projection["sha256"],
                "active_projection_digest_matches",
                f"declared={declared_digest} actual={actual_projection['sha256']}",
            )
            require(
                projection.get("file_count") == actual_projection["file_count"],
                "active_projection_file_count_matches",
                f"declared={projection.get('file_count')} actual={actual_projection['file_count']}",
            )
            require(
                projection.get("bytes") == actual_projection["bytes"],
                "active_projection_byte_count_matches",
                f"declared={projection.get('bytes')} actual={actual_projection['bytes']}",
            )
            require(
                projection.get("files") == actual_projection["files"],
                "active_projection_file_inventory_matches",
                "every active path, byte count, and file digest matches the recomputed projection",
            )
            if projection_format == "anonsync-active-implementation-projection-v2":
                fuzz_sources = [entry for entry in actual_projection["files"]
                                if str(entry["path"]).startswith("fuzz/")]
                require(
                    bool(fuzz_sources),
                    "active_projection_v2_binds_fuzz_sources",
                    f"fuzz source files={len(fuzz_sources)}",
                )
        except Exception as error:
            require(False, "active_projection_parses_and_recomputes", str(error))

    manifest: dict[str, str] = {}
    try:
        manifest = parse_manifest(read("MANIFEST.sha256"))
        require(True, "manifest_parses", f"manifest entries={len(manifest)}")
    except Exception as error:
        require(False, "manifest_parses", str(error))
    expected_manifest_names = names - {"MANIFEST.sha256"}
    require(set(manifest) == expected_manifest_names, "manifest_has_exact_file_set", f"missing={sorted(expected_manifest_names - set(manifest))[:20]} extra={sorted(set(manifest) - expected_manifest_names)[:20]}")
    mismatches: list[str] = []
    for name, expected_digest in sorted(manifest.items()):
        try:
            actual = sha256_bytes(read(name))
        except Exception as error:
            mismatches.append(f"{name}: unreadable ({error})")
            continue
        if actual != expected_digest:
            mismatches.append(f"{name}: expected {expected_digest} actual {actual}")
    require(not mismatches, "manifest_hashes_verify", "; ".join(mismatches[:20]) if mismatches else "every manifested file matches its SHA-256")

    metadata = {
        "revision": revision,
        "file_count": len(names),
        "source_cpp_count": len(source_cpp),
        "source_header_count": len(source_headers),
        "test_cpp_count": len(tests),
        "manifest_entry_count": len(manifest),
        "forbidden_entries": forbidden,
    }
    return checks, metadata


def verify_zip(path: Path, expected_revision: str | None) -> dict[str, object]:
    checks: list[dict[str, object]] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append({"check_id": check_id, "passed": bool(condition), "detail": detail})

    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        duplicate_names = sorted({info.filename for info in infos if sum(other.filename == info.filename for other in infos) > 1})
        require(not duplicate_names, "zip_member_names_are_unique", f"duplicates={duplicate_names[:20]}")
        unsafe: list[str] = []
        symlinks: list[str] = []
        for info in infos:
            try:
                normalized_member(info.filename.rstrip("/"))
            except ValueError:
                unsafe.append(info.filename)
            mode = (info.external_attr >> 16) & 0xFFFF
            if stat.S_ISLNK(mode):
                symlinks.append(info.filename)
        require(not unsafe, "zip_paths_are_safe", f"unsafe={unsafe[:20]}")
        require(not symlinks, "zip_contains_no_symlinks", f"symlinks={symlinks[:20]}")
        roots = {PurePosixPath(info.filename).parts[0] for info in infos if info.filename and PurePosixPath(info.filename).parts}
        require(roots == {"AnonSync"}, "zip_has_one_anonsync_root", f"roots={sorted(roots)}")
        names = {
            PurePosixPath(info.filename).relative_to("AnonSync").as_posix()
            for info in infos
            if not info.is_dir() and PurePosixPath(info.filename).parts and PurePosixPath(info.filename).parts[0] == "AnonSync"
        }

        def read(name: str) -> bytes:
            return archive.read(f"AnonSync/{name}")

        package, metadata = package_checks(names, read, expected_revision)
        checks.extend(package)
        bad_member = archive.testzip()
        require(bad_member is None, "zip_crc_integrity_passes", f"bad_member={bad_member}")
    return {"metadata": metadata, "checks": checks}


def verify_directory(path: Path, expected_revision: str | None) -> dict[str, object]:
    root = path / "AnonSync" if (path / "AnonSync").is_dir() else path
    names: set[str] = set()
    symlinks: list[str] = []
    for item in sorted(root.rglob("*")):
        rel = item.relative_to(root).as_posix()
        if item.is_symlink():
            symlinks.append(rel)
        elif item.is_file():
            names.add(rel)

    def read(name: str) -> bytes:
        return (root / name).read_bytes()

    checks, metadata = package_checks(names, read, expected_revision)
    checks.insert(0, {"check_id": "directory_contains_no_symlinks", "passed": not symlinks, "detail": f"symlinks={symlinks[:20]}"})
    return {"metadata": metadata, "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--expected-revision")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    path = args.path.resolve()
    try:
        if path.is_file() and zipfile.is_zipfile(path):
            result = verify_zip(path, args.expected_revision)
            kind = "zip"
        elif path.is_dir():
            result = verify_directory(path, args.expected_revision)
            kind = "directory"
        else:
            raise ValueError("path is neither a release directory nor a ZIP archive")
        checks = result["checks"]
        passed = all(bool(check["passed"]) for check in checks)
        report = {
            "format": "anonsync-release-package-verification-v1",
            "path": str(path),
            "kind": kind,
            "passed": passed,
            "check_count": len(checks),
            "passed_check_count": sum(bool(check["passed"]) for check in checks),
            "checks": checks,
            **result["metadata"],
        }
    except Exception as error:
        report = {
            "format": "anonsync-release-package-verification-v1",
            "path": str(path),
            "passed": False,
            "fatal_error": str(error),
        }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report.get("passed") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
