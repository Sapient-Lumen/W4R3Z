#!/usr/bin/env python3
"""Build a deterministic, single-root ZIP for the current cube revision."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import sys
import tempfile
import unicodedata
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from cube_runtime import canonical_json, sha256_path  # noqa: E402

CONTRACT_PATH = Path("data/current_zip_contract.json")


class PackageBuildError(RuntimeError):
    """Raised when the source tree cannot be represented safely."""


def load_contract(root: Path) -> dict[str, Any]:
    value = json.loads((root / CONTRACT_PATH).read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("version") != 1:
        raise PackageBuildError("unsupported ZIP contract")
    return value


def source_files(root: Path) -> list[tuple[Path, str, bool]]:
    rows: list[tuple[Path, str, bool]] = []
    normalized: dict[str, str] = {}
    casefolded: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise PackageBuildError(f"symlink rejected: {path.relative_to(root)}")
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts or "\\" in relative or "\x00" in relative:
            raise PackageBuildError(f"unsafe path: {relative}")
        nfc = unicodedata.normalize("NFC", relative)
        if nfc != relative:
            raise PackageBuildError(f"non-NFC path: {relative!r}")
        if nfc in normalized:
            raise PackageBuildError(f"normalization collision: {normalized[nfc]!r}, {relative!r}")
        normalized[nfc] = relative
        folded = nfc.casefold()
        if folded in casefolded:
            raise PackageBuildError(f"casefold collision: {casefolded[folded]!r}, {relative!r}")
        casefolded[folded] = relative
        executable = bool(path.stat().st_mode & 0o111)
        rows.append((path, relative, executable))
    # Path ordering is component-wise and differs from lexicographic POSIX
    # member ordering for prefix cases such as ``name.file`` vs ``name/sub``.
    return sorted(rows, key=lambda row: row[1])


def _zip_info(name: str, timestamp: tuple[int, int, int, int, int, int], mode: int, *, directory: bool) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=timestamp)
    info.create_system = 3
    info.flag_bits = 0x800
    info.extra = b""
    info.comment = b""
    type_mode = stat.S_IFDIR if directory else stat.S_IFREG
    info.external_attr = ((type_mode | mode) & 0xFFFF) << 16
    info.compress_type = zipfile.ZIP_STORED if directory else zipfile.ZIP_DEFLATED
    return info


def build_package(root: Path, output: Path) -> dict[str, Any]:
    root = root.resolve()
    output = output.resolve()
    if not root.is_dir():
        raise PackageBuildError(f"not a directory: {root}")
    if output.suffix.lower() != ".zip":
        raise PackageBuildError("output must end in .zip")
    if root.name != output.stem:
        raise PackageBuildError(f"root name {root.name!r} does not match output stem {output.stem!r}")
    contract = load_contract(root)
    timestamp = tuple(contract["fixed_timestamp"])
    if len(timestamp) != 6:
        raise PackageBuildError("invalid fixed timestamp")
    files = source_files(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=output.name + ".", suffix=".tmp", dir=output.parent)
    os.close(fd)
    temp_path = Path(temp_name)
    try:
        with zipfile.ZipFile(temp_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=True) as archive:
            archive.comment = b""
            root_name = root.name + "/"
            archive.writestr(_zip_info(root_name, timestamp, 0o755, directory=True), b"")
            for path, relative, executable in files:
                name = f"{root.name}/{relative}"
                mode = 0o755 if executable else 0o644
                info = _zip_info(name, timestamp, mode, directory=False)
                with path.open("rb") as source, archive.open(info, "w", force_zip64=True) as target:
                    shutil.copyfileobj(source, target, length=1 << 20)
        os.replace(temp_path, output)
    finally:
        if temp_path.exists():
            temp_path.unlink()
    return {
        "status": "pass",
        "root": root.name,
        "output": output.name,
        "files": len(files),
        "members": len(files) + 1,
        "bytes": output.stat().st_size,
        "sha256": sha256_path(output),
        "contract": CONTRACT_PATH.as_posix(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = build_package(args.root, args.output)
    except Exception as exc:
        result = {"status": "fail", "error": f"{type(exc).__name__}: {exc}"}
    print(canonical_json(result), end="")
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
