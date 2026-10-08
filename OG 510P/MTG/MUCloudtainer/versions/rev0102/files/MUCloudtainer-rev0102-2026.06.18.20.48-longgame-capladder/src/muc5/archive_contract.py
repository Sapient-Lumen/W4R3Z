from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import zipfile
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

from .package_contract import parse_cube_name

DEFAULT_LINKED_ARCHIVE_BUDGET_BYTES = 64 * 1024 * 1024
DEFAULT_STORED_FILE_THRESHOLD_BYTES = 1024 * 1024


@dataclass
class ArchiveContractReport:
    archive: str
    passed: bool = True
    root_name: str | None = None
    entries: int = 0
    files: int = 0
    archive_bytes: int = 0
    uncompressed_bytes: int = 0
    compressed_member_bytes: int = 0
    compression_ratio: float | None = None
    stored_file_count: int = 0
    stored_large_files: list[str] = field(default_factory=list)
    duplicate_entries: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checks: list[dict[str, Any]] = field(default_factory=list)

    def add_check(self, name: str, passed: bool, detail: str = "") -> None:
        self.checks.append({"name": name, "passed": bool(passed), "detail": detail})
        if not passed:
            self.errors.append(f"{name}: {detail}" if detail else name)
            self.passed = False

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def sha256_file(path: str | Path, *, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def _normalized_timestamp(root: Path) -> tuple[int, int, int, int, int, int]:
    identity = parse_cube_name(root.name)
    dt = datetime.strptime(identity.timestamp, "%Y.%m.%d.%H.%M")
    # ZIP timestamps have two-second resolution. A zero second is deterministic.
    return (dt.year, dt.month, dt.day, dt.hour, dt.minute, 0)


def _safe_arcname(root_name: str, relative: Path) -> str:
    return f"{root_name}/{relative.as_posix()}"


def _zip_info(name: str, *, date_time: tuple[int, int, int, int, int, int], mode: int, is_dir: bool) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name + ("/" if is_dir and not name.endswith("/") else ""), date_time=date_time)
    info.create_system = 3
    perms = mode & 0o777
    if is_dir:
        info.external_attr = ((stat.S_IFDIR | perms) << 16) | 0x10
        info.compress_type = zipfile.ZIP_STORED
    else:
        info.external_attr = (stat.S_IFREG | perms) << 16
        info.compress_type = zipfile.ZIP_DEFLATED
    return info


def build_linked_archive(
    root: str | Path,
    output: str | Path,
    *,
    compresslevel: int = 9,
    exclude_paths: Iterable[str] = (),
) -> Path:
    """Build a deterministic, explicitly deflated linked ZIP.

    Python's ``ZipFile`` defaults to ``ZIP_STORED``. This builder sets the
    compression method on every file and normalizes timestamps and modes so a
    repeated build from identical bytes produces the same archive digest.
    """

    root_path = Path(root).resolve()
    parse_cube_name(root_path.name)
    output_path = Path(output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()

    excluded = {PurePosixPath(path).as_posix() for path in exclude_paths}
    timestamp = _normalized_timestamp(root_path)
    directories = sorted(
        (path for path in root_path.rglob("*") if path.is_dir()),
        key=lambda p: p.relative_to(root_path).as_posix(),
    )
    files = sorted(
        (path for path in root_path.rglob("*") if path.is_file()),
        key=lambda p: p.relative_to(root_path).as_posix(),
    )

    with zipfile.ZipFile(
        output_path,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=compresslevel,
        allowZip64=True,
        strict_timestamps=False,
    ) as archive:
        root_info = _zip_info(root_path.name, date_time=timestamp, mode=0o755, is_dir=True)
        archive.writestr(root_info, b"")
        for directory in directories:
            relative = directory.relative_to(root_path)
            if relative.as_posix() in excluded:
                continue
            info = _zip_info(
                _safe_arcname(root_path.name, relative),
                date_time=timestamp,
                mode=0o755,
                is_dir=True,
            )
            archive.writestr(info, b"")
        for path in files:
            relative = path.relative_to(root_path)
            if relative.as_posix() in excluded:
                continue
            info = _zip_info(
                _safe_arcname(root_path.name, relative),
                date_time=timestamp,
                mode=0o644,
                is_dir=False,
            )
            info.file_size = path.stat().st_size
            with path.open("rb") as source, archive.open(info, mode="w", force_zip64=True) as target:
                shutil.copyfileobj(source, target, length=1024 * 1024)

    return output_path


def audit_linked_archive(
    archive_path: str | Path,
    *,
    expected_root: str | None = None,
    max_archive_bytes: int | None = DEFAULT_LINKED_ARCHIVE_BUDGET_BYTES,
    stored_file_threshold_bytes: int = DEFAULT_STORED_FILE_THRESHOLD_BYTES,
) -> ArchiveContractReport:
    path = Path(archive_path).resolve()
    report = ArchiveContractReport(archive=str(path), archive_bytes=path.stat().st_size if path.exists() else 0)
    report.add_check("archive_exists", path.is_file(), str(path))
    if not path.is_file():
        return report

    try:
        archive = zipfile.ZipFile(path, "r")
    except Exception as exc:
        report.add_check("zip_open", False, str(exc))
        return report

    with archive:
        infos = archive.infolist()
        report.entries = len(infos)
        file_infos = [info for info in infos if not info.is_dir()]
        report.files = len(file_infos)
        names = [info.filename for info in infos]
        seen: set[str] = set()
        report.duplicate_entries = sorted({name for name in names if name in seen or seen.add(name) is None and False})
        # The compact expression above intentionally never adds false positives;
        # recompute plainly for readability and correctness.
        seen.clear()
        duplicates: set[str] = set()
        for name in names:
            if name in seen:
                duplicates.add(name)
            seen.add(name)
        report.duplicate_entries = sorted(duplicates)
        report.add_check(
            "unique_entries",
            not report.duplicate_entries,
            "all entries unique" if not report.duplicate_entries else f"duplicates={report.duplicate_entries[:10]}",
        )

        unsafe = []
        roots: set[str] = set()
        for name in names:
            pure = PurePosixPath(name)
            if pure.is_absolute() or ".." in pure.parts:
                unsafe.append(name)
            if pure.parts:
                roots.add(pure.parts[0])
        report.add_check("safe_member_paths", not unsafe, "no absolute or traversal paths" if not unsafe else str(unsafe[:10]))
        report.add_check("single_root_directory", len(roots) == 1, f"roots={sorted(roots)}")
        if len(roots) == 1:
            report.root_name = next(iter(roots))
        if expected_root is not None:
            report.add_check("expected_root", report.root_name == expected_root, f"expected={expected_root!r}; actual={report.root_name!r}")

        report.uncompressed_bytes = sum(info.file_size for info in file_infos)
        report.compressed_member_bytes = sum(info.compress_size for info in file_infos)
        if report.uncompressed_bytes:
            report.compression_ratio = report.compressed_member_bytes / report.uncompressed_bytes
        report.stored_file_count = sum(info.compress_type == zipfile.ZIP_STORED for info in file_infos)
        report.stored_large_files = sorted(
            info.filename
            for info in file_infos
            if info.compress_type == zipfile.ZIP_STORED and info.file_size >= stored_file_threshold_bytes
        )
        report.add_check(
            "large_files_compressed",
            not report.stored_large_files,
            "no large store-only members"
            if not report.stored_large_files
            else f"stored_large={report.stored_large_files[:10]}",
        )

        bad_member = archive.testzip()
        report.add_check("crc_integrity", bad_member is None, "all members pass CRC" if bad_member is None else f"bad_member={bad_member}")

        manifest_name = f"{report.root_name}/manifest.json" if report.root_name else None
        if manifest_name and manifest_name in names:
            try:
                manifest = json.loads(archive.read(manifest_name))
            except Exception as exc:
                report.add_check("archive_manifest_json", False, str(exc))
            else:
                filename = manifest.get("filename") if isinstance(manifest, Mapping) else None
                cube_name = manifest.get("cube_name") if isinstance(manifest, Mapping) else None
                report.add_check("archive_manifest_root_alignment", cube_name == report.root_name, f"manifest cube_name={cube_name!r}")
                report.add_check("archive_manifest_filename_alignment", filename == path.name, f"manifest filename={filename!r}")
        else:
            report.add_check("archive_manifest_present", False, f"missing {manifest_name}")

    if max_archive_bytes is not None:
        report.add_check(
            "archive_size_budget",
            report.archive_bytes <= max_archive_bytes,
            f"archive_bytes={report.archive_bytes}; budget_bytes={max_archive_bytes}",
        )
    return report


__all__ = [
    "ArchiveContractReport",
    "DEFAULT_LINKED_ARCHIVE_BUDGET_BYTES",
    "DEFAULT_STORED_FILE_THRESHOLD_BYTES",
    "audit_linked_archive",
    "build_linked_archive",
    "sha256_file",
]
