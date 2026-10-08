#!/usr/bin/env python3
"""Audit a cube ZIP for deterministic metadata, safe names, and tree parity."""
from __future__ import annotations

import argparse
import hashlib
import json
import stat
import sys
import unicodedata
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from cube_runtime import canonical_json, digest_stream, sha256_path  # noqa: E402

CONTRACT_PATH = Path("data/current_zip_contract.json")


def _stream_digest(handle: BinaryIO) -> str:
    digest, _size = digest_stream(handle)
    return digest


def audit_zip(path: Path, *, root: Path | None = None, contract_root: Path | None = None) -> dict[str, Any]:
    path = path.resolve()
    contract_root = (contract_root or root or ROOT).resolve()
    contract = json.loads((contract_root / CONTRACT_PATH).read_text(encoding="utf-8"))
    timestamp = tuple(contract["fixed_timestamp"])
    errors: list[str] = []
    checks: list[dict[str, Any]] = []

    def add(check_id: str, passed: bool, detail: Any = "") -> None:
        checks.append({"check_id": check_id, "status": "pass" if passed else "fail", "detail": detail})
        if not passed:
            errors.append(f"{check_id}: {detail}")

    if not path.is_file():
        return {"status": "fail", "zip": str(path), "errors": ["ZIP does not exist"], "checks": []}

    expected_root = path.stem
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        add("ZIP integrity", archive.testzip() is None)
        add("ZIP comment empty", archive.comment == b"", {
            "bytes": len(archive.comment),
            "hex": archive.comment.hex(),
        })
        add("members nonempty", bool(infos), len(infos))
        add("raw member names unique", len(names) == len(set(names)), len(names) - len(set(names)))

        normalized = [unicodedata.normalize("NFC", name) for name in names]
        add("member names already NFC", normalized == names)
        add("NFC member names unique", len(normalized) == len(set(normalized)))
        folded = [name.casefold() for name in normalized]
        add("casefold member names unique", len(folded) == len(set(folded)))

        safe = True
        for name in names:
            pure = PurePosixPath(name)
            if not name or "\\" in name or "\x00" in name or pure.is_absolute() or ".." in pure.parts:
                safe = False
                break
        add("portable safe member paths", safe)

        root_name = expected_root + "/"
        add("root directory first", bool(names) and names[0] == root_name, names[:1])
        root_entries = [info for info in infos if info.is_dir()]
        add("root-only directory entry", len(root_entries) == 1 and root_entries[0].filename == root_name,
            [info.filename for info in root_entries])
        add("all files under expected root", all(name == root_name or name.startswith(root_name) for name in names))
        relative_files = [name[len(root_name):] for name in names[1:] if name.startswith(root_name)]
        add("file members lexicographic", relative_files == sorted(relative_files))
        add("no empty relative file names", all(relative_files))

        add("fixed timestamps", all(info.date_time == timestamp for info in infos),
            sorted({info.date_time for info in infos}))
        add("root stored", bool(infos) and infos[0].compress_type == zipfile.ZIP_STORED)
        add("files deflated", all(info.compress_type == zipfile.ZIP_DEFLATED for info in infos[1:]))
        add("no encrypted members", all(not (info.flag_bits & 0x1) for info in infos))
        modes = [((info.external_attr >> 16) & 0xFFFF) for info in infos]
        add("no symlink members", all(not stat.S_ISLNK(mode) for mode in modes))
        add("root mode", bool(modes) and stat.S_ISDIR(modes[0]) and stat.S_IMODE(modes[0]) == 0o755,
            oct(modes[0]) if modes else "")
        file_modes_ok = all(
            stat.S_ISREG(mode) and stat.S_IMODE(mode) in {0o644, 0o755}
            for mode in modes[1:]
        )
        add("file modes canonical", file_modes_ok)

        tree_files = 0
        if root is not None:
            root = root.resolve()
            add("filesystem root matches ZIP stem", root.name == expected_root, root.name)
            expected: dict[str, tuple[str, int, int]] = {}
            symlinks: list[str] = []
            for item in sorted(root.rglob("*")):
                relative = item.relative_to(root).as_posix()
                if item.is_symlink():
                    symlinks.append(relative)
                elif item.is_file():
                    mode = 0o755 if item.stat().st_mode & 0o111 else 0o644
                    expected[relative] = (sha256_path(item), item.stat().st_size, mode)
            add("filesystem has no symlinks", not symlinks, symlinks)
            actual_names = set(relative_files)
            add("ZIP and filesystem file sets equal", actual_names == set(expected), {
                "missing": sorted(set(expected) - actual_names)[:20],
                "extra": sorted(actual_names - set(expected))[:20],
            })
            content_mismatches: list[str] = []
            mode_mismatches: list[str] = []
            for info in infos[1:]:
                relative = info.filename[len(root_name):]
                if relative not in expected:
                    continue
                expected_digest, expected_size, expected_mode = expected[relative]
                with archive.open(info) as handle:
                    digest = _stream_digest(handle)
                if digest != expected_digest or info.file_size != expected_size:
                    content_mismatches.append(relative)
                actual_mode = stat.S_IMODE((info.external_attr >> 16) & 0xFFFF)
                if actual_mode != expected_mode:
                    mode_mismatches.append(relative)
            add("ZIP content digests match filesystem", not content_mismatches, content_mismatches[:20])
            add("ZIP modes match filesystem policy", not mode_mismatches, mode_mismatches[:20])
            tree_files = len(expected)

    return {
        "status": "pass" if not errors else "fail",
        "zip": path.name,
        "zip_sha256": sha256_path(path),
        "zip_bytes": path.stat().st_size,
        "members": len(checks) and len(names) or 0,
        "tree_files": tree_files,
        "checks_passed": sum(row["status"] == "pass" for row in checks),
        "checks_total": len(checks),
        "checks": checks,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", dest="zip_path", type=Path, required=True)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--contract-root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        result = audit_zip(args.zip_path, root=args.root, contract_root=args.contract_root)
    except Exception as exc:
        result = {"status": "fail", "errors": [f"{type(exc).__name__}: {exc}"]}
    print(canonical_json(result), end="")
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
