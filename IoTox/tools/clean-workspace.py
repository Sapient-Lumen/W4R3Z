#!/usr/bin/env python3
"""Audit and prune bounded IoTox workspace products.

The default is a dry run. Deletion requires --apply and is confined to
allowlisted immediate children of known ignored roots. Sandwurm proof roots
named by tracked documentation are always protected.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
HOST_RM = Path("/run/current-system/sw/bin/rm")
TEMP_ROOT = ROOT / ".sandworm/home/tmp"
SANDWORM_TRASH_FILES_ROOT = ROOT / ".sandworm/home/.local/share/Trash/files"
SANDWORM_TRASH_INFO_ROOT = ROOT / ".sandworm/home/.local/share/Trash/info"
LAB_ROOT = ROOT / ".sandwurm/lab"
SANDWURM_ROOT = ROOT / ".sandwurm"
OPERATOR_TOR_ROOT = ROOT / ".sandwurm/operator-tor"
COMPACT_PAIR_ROOT = ROOT / ".sandwurm/exports/pairs"
THREE_WRITER_LAB_ROOT = LAB_ROOT / "three-writer"
COMPACT_THREE_WRITER_ROOT = ROOT / ".sandwurm/exports/three-writer"
SYNC_SHADOW_LAB_ROOT = LAB_ROOT / "sync-shadow"
COMPACT_SYNC_SHADOW_ROOT = ROOT / ".sandwurm/exports/sync-shadow"
SYNC_RECOVERY_CUSTODY_LAB_ROOT = LAB_ROOT / "sync-recovery-custody-loopback"
COMPACT_SYNC_RECOVERY_CUSTODY_ROOT = (
    ROOT / ".sandwurm/exports/sync-recovery-custody"
)
SYNC_DISHONEST_STORAGE_LAB_ROOT = LAB_ROOT / "sync-dishonest-storage"
COMPACT_SYNC_DISHONEST_STORAGE_ROOT = (
    ROOT / ".sandwurm/exports/sync-dishonest-storage"
)
SYNC_LOG_WRITES_PREFIX_LAB_ROOT = LAB_ROOT / "sync-log-writes-prefix"
COMPACT_SYNC_LOG_WRITES_PREFIX_ROOT = (
    ROOT / ".sandwurm/exports/sync-log-writes-prefix"
)
SYNC_PRODUCTION_PREFIX_LAB_ROOT = LAB_ROOT / "sync-production-prefix"
COMPACT_SYNC_PRODUCTION_PREFIX_ROOT = (
    ROOT / ".sandwurm/exports/sync-production-prefix"
)
METADATA_CORRUPTION_LAB_ROOT = LAB_ROOT / "sync-metadata-corruption"
COMPACT_METADATA_CORRUPTION_ROOT = (
    ROOT / ".sandwurm/exports/sync-metadata-corruption"
)
PROJECTION_DESCRIPTOR_LAB_ROOT = LAB_ROOT / "sync-projection-descriptor"
COMPACT_PROJECTION_DESCRIPTOR_ROOT = (
    ROOT / ".sandwurm/exports/sync-projection-descriptor"
)
POWER_CUT_LAB_ROOTS = (
    LAB_ROOT / "sync-power-cut",
    LAB_ROOT / "sync-power-cut-post-exchange",
    LAB_ROOT / "sync-power-cut-receive-staging",
    LAB_ROOT / "sync-power-cut-cas-install",
    LAB_ROOT / "sync-power-cut-manifest-install",
    LAB_ROOT / "sync-power-cut-branch-record-install",
    LAB_ROOT / "sync-power-cut-branch-pointer-update",
    LAB_ROOT / "sync-power-cut-manifest-directory-fsync",
    LAB_ROOT / "sync-power-cut-branch-record-directory-fsync",
    LAB_ROOT / "sync-power-cut-branch-pointer-directory-fsync",
)
COMPACT_POWER_CUT_ROOT = ROOT / ".sandwurm/exports/sync-power-cut"
BUILD_ROOTS = (
    ROOT / "build",
    ROOT / ".build",
    ROOT / "components/toxsync/build",
)
TEMP_NAME = re.compile(
    r"^(?:"
    r"toxsync-(?:benchmark|large-bench|content-bench|fabric-bench)-[^/]+|"
    r"iotox-[A-Za-z0-9_.-]+-test-[^/]+|"
    r"nix-shell\.[A-Za-z0-9]+|nix-[0-9]+-[0-9]+|tmp\.[A-Za-z0-9]+"
    r")$"
)
SANDWORM_TRASH_NAME = re.compile(
    r"^(?:"
    r"run\.[A-Za-z0-9_]+|"
    r"pair\.[A-Za-z0-9_]+|"
    r"gcc-coverage(?:\.[0-9]+)?|"
    r"tmp\.[A-Za-z0-9]+|"
    r"rev[0-9]{4,}"
    r")$"
)
PROOF_NAMES = {
    "pairs": re.compile(r"^pair\.[A-Za-z0-9_]+$"),
    "client": re.compile(r"^run\.[A-Za-z0-9]+$"),
    "device": re.compile(r"^run\.[A-Za-z0-9]+$"),
}
THREE_WRITER_NAME = re.compile(r"^run\.[A-Za-z0-9_]+$")
THREE_WRITER_NEAR_CEILING_LAB_NAME = re.compile(
    r"^three-writer-near-ceiling-cap-(?:1|4|8|16|32|64)$"
)
THREE_WRITER_SOAK_LAB_NAME = re.compile(r"^three-writer-soak-(?:smoke|24h)$")
SYNC_SHADOW_NAME = re.compile(r"^run\.[A-Za-z0-9_]+$")
SYNC_RECOVERY_CUSTODY_NAME = re.compile(r"^run\.[A-Za-z0-9_]+$")
SYNC_DISHONEST_STORAGE_NAME = re.compile(r"^run\.[A-Za-z0-9_]+$")
SYNC_LOG_WRITES_PREFIX_NAME = re.compile(r"^run\.[A-Za-z0-9_]+$")
SYNC_PRODUCTION_PREFIX_NAME = re.compile(r"^run\.[A-Za-z0-9_]+$")
METADATA_CORRUPTION_NAME = re.compile(r"^run\.[A-Za-z0-9_]+$")
PROJECTION_DESCRIPTOR_NAME = re.compile(r"^run\.[A-Za-z0-9_]+$")
POWER_CUT_NAME = re.compile(r"^run\.[A-Za-z0-9_]+$")
OPERATOR_TOR_NAME = re.compile(r"^run\.[A-Za-z0-9_]+$")
DEVICE_REPAIR_NAME = re.compile(r"^iotox-device-repair\.[A-Za-z0-9_]+$")
KEPT_BUILD_NAMES = {"gcc-debug"}
TOP_LEVEL_BUILD_NAME = re.compile(r"^build-[A-Za-z0-9][A-Za-z0-9_.-]*$")
BUILD_FILE_NAME = re.compile(
    r"^(?:"
    r"\.[A-Za-z0-9_.-]+\.lock|"
    r"[A-Za-z0-9_.#-]+\.(?:gcov|log|exit|stdout|sha256|txt)"
    r")$"
)


@dataclass(frozen=True)
class Candidate:
    category: str
    path: Path
    allocated_bytes: int
    age_hours: float
    reason: str


def fail(message: str) -> None:
    raise RuntimeError(message)


def allocated_bytes(path: Path) -> int:
    if not path.exists() and not path.is_symlink():
        return 0
    command = ["du", "-s", "--block-size=1", "--", str(path)]
    result = subprocess.run(
        command,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        if not path.exists() and not path.is_symlink():
            return 0
        result = subprocess.run(
            ["sudo", "-n", *command],
            check=True,
            text=True,
            capture_output=True,
        )
    return int(result.stdout.split(maxsplit=1)[0])


def format_size(value: int) -> str:
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    amount = float(value)
    for unit in units:
        if amount < 1024.0 or unit == units[-1]:
            return f"{amount:.1f} {unit}"
        amount /= 1024.0
    raise AssertionError("unreachable")


@lru_cache(maxsize=1)
def tracked_proof_roots() -> set[Path]:
    result = subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={ROOT}",
            "-C",
            str(ROOT),
            "grep",
            "-hoE",
            r"\.sandwurm/lab/(pairs/pair\.[A-Za-z0-9_]+|(client|device)/run\.[A-Za-z0-9]+|(three-writer|three-writer-near-ceiling-cap-(1|4|8|16|32|64)|three-writer-soak-(smoke|24h)|sync-shadow|sync-recovery-custody-loopback|sync-dishonest-storage|sync-log-writes-prefix|sync-production-prefix|sync-metadata-corruption|sync-projection-descriptor|sync-power-cut(-post-exchange|-receive-staging|-cas-install|-manifest-install|-branch-record-install|-branch-pointer-update|-manifest-directory-fsync|-branch-record-directory-fsync|-branch-pointer-directory-fsync)?)/run\.[A-Za-z0-9_]+)",
            "--",
            "*.md",
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode not in (0, 1):
        fail("unable to inspect tracked proof-root references")
    return {(ROOT / line).resolve() for line in result.stdout.splitlines() if line}


@lru_cache(maxsize=1)
def tracked_compact_pair_roots() -> set[Path]:
    result = subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={ROOT}",
            "-C",
            str(ROOT),
            "grep",
            "-hoE",
            r"pair\.[A-Za-z0-9_]+",
            "--",
            "*.md",
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode not in (0, 1):
        fail("unable to inspect tracked compact-proof references")
    return {
        (COMPACT_PAIR_ROOT / line).resolve()
        for line in result.stdout.splitlines()
        if line
    }


@lru_cache(maxsize=1)
def tracked_compact_three_writer_roots() -> set[Path]:
    result = subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={ROOT}",
            "-C",
            str(ROOT),
            "grep",
            "-hoE",
            r"\.sandwurm/exports/three-writer/run\.[A-Za-z0-9_]+",
            "--",
            "*.md",
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode not in (0, 1):
        fail("unable to inspect tracked three-writer compact-proof references")
    return {(ROOT / line).resolve() for line in result.stdout.splitlines() if line}


@lru_cache(maxsize=1)
def tracked_compact_sync_shadow_roots() -> set[Path]:
    result = subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={ROOT}",
            "-C",
            str(ROOT),
            "grep",
            "-hoE",
            r"\.sandwurm/exports/sync-shadow/run\.[A-Za-z0-9_]+",
            "--",
            "*.md",
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode not in (0, 1):
        fail("unable to inspect tracked sync-shadow compact-proof references")
    return {(ROOT / line).resolve() for line in result.stdout.splitlines() if line}


@lru_cache(maxsize=1)
def tracked_compact_sync_recovery_custody_roots() -> set[Path]:
    result = subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={ROOT}",
            "-C",
            str(ROOT),
            "grep",
            "-hoE",
            r"\.sandwurm/exports/sync-recovery-custody/run\.[A-Za-z0-9_]+",
            "--",
            "*.md",
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode not in (0, 1):
        fail("unable to inspect tracked sync-recovery-custody references")
    return {(ROOT / line).resolve() for line in result.stdout.splitlines() if line}


@lru_cache(maxsize=1)
def tracked_compact_sync_dishonest_storage_roots() -> set[Path]:
    result = subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={ROOT}",
            "-C",
            str(ROOT),
            "grep",
            "-hoE",
            r"\.sandwurm/exports/sync-dishonest-storage/run\.[A-Za-z0-9_]+",
            "--",
            "*.md",
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode not in (0, 1):
        fail("unable to inspect tracked sync dishonest-storage references")
    return {(ROOT / line).resolve() for line in result.stdout.splitlines() if line}


@lru_cache(maxsize=1)
def tracked_compact_sync_log_writes_prefix_roots() -> set[Path]:
    result = subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={ROOT}",
            "-C",
            str(ROOT),
            "grep",
            "-hoE",
            r"\.sandwurm/exports/sync-log-writes-prefix/run\.[A-Za-z0-9_]+",
            "--",
            "*.md",
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode not in (0, 1):
        fail("unable to inspect tracked sync log-writes prefix references")
    return {(ROOT / line).resolve() for line in result.stdout.splitlines() if line}


@lru_cache(maxsize=1)
def tracked_compact_sync_production_prefix_roots() -> set[Path]:
    result = subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={ROOT}",
            "-C",
            str(ROOT),
            "grep",
            "-hoE",
            r"\.sandwurm/exports/sync-production-prefix/run\.[A-Za-z0-9_]+",
            "--",
            "*.md",
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode not in (0, 1):
        fail("unable to inspect tracked sync production-prefix references")
    return {(ROOT / line).resolve() for line in result.stdout.splitlines() if line}


@lru_cache(maxsize=1)
def tracked_compact_metadata_corruption_roots() -> set[Path]:
    result = subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={ROOT}",
            "-C",
            str(ROOT),
            "grep",
            "-hoE",
            r"\.sandwurm/exports/sync-metadata-corruption/run\.[A-Za-z0-9_]+",
            "--",
            "*.md",
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode not in (0, 1):
        fail("unable to inspect tracked metadata-corruption compact references")
    return {(ROOT / line).resolve() for line in result.stdout.splitlines() if line}


@lru_cache(maxsize=1)
def tracked_compact_projection_descriptor_roots() -> set[Path]:
    result = subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={ROOT}",
            "-C",
            str(ROOT),
            "grep",
            "-hoE",
            r"\.sandwurm/exports/sync-projection-descriptor/run\.[A-Za-z0-9_]+",
            "--",
            "*.md",
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode not in (0, 1):
        fail("unable to inspect tracked projection-descriptor compact references")
    return {(ROOT / line).resolve() for line in result.stdout.splitlines() if line}


@lru_cache(maxsize=1)
def tracked_compact_power_cut_roots() -> set[Path]:
    result = subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={ROOT}",
            "-C",
            str(ROOT),
            "grep",
            "-hoE",
            r"\.sandwurm/exports/sync-power-cut/run\.[A-Za-z0-9_]+",
            "--",
            "*.md",
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode not in (0, 1):
        fail("unable to inspect tracked power-cut compact-proof references")
    return {(ROOT / line).resolve() for line in result.stdout.splitlines() if line}


def immediate_children(path: Path) -> list[Path]:
    if not path.is_dir():
        return []
    return list(path.iterdir())


def three_writer_lab_roots() -> tuple[Path, ...]:
    extra = [
        path
        for path in immediate_children(LAB_ROOT)
        if not path.is_symlink()
        and path.is_dir()
        and (
            THREE_WRITER_NEAR_CEILING_LAB_NAME.fullmatch(path.name) is not None
            or THREE_WRITER_SOAK_LAB_NAME.fullmatch(path.name) is not None
        )
    ]
    extra.sort()
    return (THREE_WRITER_LAB_ROOT, *extra)


def age_hours(path: Path, now: float) -> float:
    try:
        mtime = path.lstat().st_mtime
    except FileNotFoundError:
        return 0.0
    return max(0.0, (now - mtime) / 3600.0)


def sort_mtime(path: Path) -> float:
    try:
        return path.lstat().st_mtime
    except FileNotFoundError:
        return 0.0


def candidate(path: Path, category: str, reason: str, now: float) -> Candidate:
    return Candidate(category, path, allocated_bytes(path), age_hours(path, now), reason)


def temp_candidates(now: float, minimum_age: float) -> list[Candidate]:
    values = []
    for path in immediate_children(TEMP_ROOT):
        if path.is_symlink() or TEMP_NAME.fullmatch(path.name) is None:
            continue
        if age_hours(path, now) >= minimum_age:
            values.append(candidate(path, "temp", "allowlisted stale temporary", now))
    return values


def sandbox_trash_candidates(now: float, minimum_age: float) -> list[Candidate]:
    values = []
    for path in immediate_children(SANDWORM_TRASH_FILES_ROOT):
        if path.is_symlink() or SANDWORM_TRASH_NAME.fullmatch(path.name) is None:
            continue
        if age_hours(path, now) >= minimum_age:
            values.append(
                candidate(
                    path,
                    "temp",
                    "allowlisted nested sandbox trash payload",
                    now,
                )
            )
    for path in immediate_children(SANDWORM_TRASH_INFO_ROOT):
        if (
            path.is_symlink()
            or not path.is_file()
            or not path.name.endswith(".trashinfo")
        ):
            continue
        base = path.name.removesuffix(".trashinfo")
        if SANDWORM_TRASH_NAME.fullmatch(base) is None:
            continue
        if age_hours(path, now) >= minimum_age:
            values.append(
                candidate(
                    path,
                    "temp",
                    "allowlisted nested sandbox trash metadata",
                    now,
                )
            )
    return values


def proof_candidates(now: float, keep_unreferenced: int) -> list[Candidate]:
    protected = tracked_proof_roots()
    values = []
    for group, name_pattern in PROOF_NAMES.items():
        parent = LAB_ROOT / group
        unreferenced = [
            path
            for path in immediate_children(parent)
            if not path.is_symlink()
            and path.is_dir()
            and name_pattern.fullmatch(path.name) is not None
            and path.resolve() not in protected
            and open_reference(path.resolve()) is None
        ]
        unreferenced.sort(key=sort_mtime, reverse=True)
        for path in unreferenced[keep_unreferenced:]:
            values.append(
                candidate(path, "sandwurm", "unreferenced superseded proof root", now)
            )
    return values


def three_writer_proof_candidates(
    now: float, keep_unreferenced: int
) -> list[Candidate]:
    protected = tracked_proof_roots()
    unreferenced = []
    for parent in three_writer_lab_roots():
        unreferenced.extend(
            path
            for path in immediate_children(parent)
            if not path.is_symlink()
            and path.is_dir()
            and THREE_WRITER_NAME.fullmatch(path.name) is not None
            and path.resolve() not in protected
            and open_reference(path.resolve()) is None
        )
    unreferenced.sort(key=sort_mtime, reverse=True)
    return [
        candidate(path, "sandwurm", "unreferenced superseded three-writer proof root", now)
        for path in unreferenced[keep_unreferenced:]
    ]


def sync_shadow_proof_candidates(
    now: float, keep_unreferenced: int
) -> list[Candidate]:
    protected = tracked_proof_roots()
    unreferenced = [
        path
        for path in immediate_children(SYNC_SHADOW_LAB_ROOT)
        if not path.is_symlink()
        and path.is_dir()
        and SYNC_SHADOW_NAME.fullmatch(path.name) is not None
        and path.resolve() not in protected
        and open_reference(path.resolve()) is None
    ]
    unreferenced.sort(key=sort_mtime, reverse=True)
    return [
        candidate(path, "sandwurm", "unreferenced superseded sync-shadow proof root", now)
        for path in unreferenced[keep_unreferenced:]
    ]


def sync_recovery_custody_proof_candidates(
    now: float, keep_unreferenced: int
) -> list[Candidate]:
    protected = tracked_proof_roots()
    unreferenced = [
        path
        for path in immediate_children(SYNC_RECOVERY_CUSTODY_LAB_ROOT)
        if not path.is_symlink()
        and path.is_dir()
        and SYNC_RECOVERY_CUSTODY_NAME.fullmatch(path.name) is not None
        and path.resolve() not in protected
        and open_reference(path.resolve()) is None
    ]
    unreferenced.sort(key=sort_mtime, reverse=True)
    return [
        candidate(
            path,
            "sandwurm",
            "unreferenced superseded sync recovery-custody raw root",
            now,
        )
        for path in unreferenced[keep_unreferenced:]
    ]


def sync_dishonest_storage_proof_candidates(
    now: float, keep_unreferenced: int
) -> list[Candidate]:
    protected = tracked_proof_roots()
    unreferenced = [
        path
        for path in immediate_children(SYNC_DISHONEST_STORAGE_LAB_ROOT)
        if not path.is_symlink()
        and path.is_dir()
        and SYNC_DISHONEST_STORAGE_NAME.fullmatch(path.name) is not None
        and path.resolve() not in protected
        and open_reference(path.resolve()) is None
    ]
    unreferenced.sort(key=sort_mtime, reverse=True)
    return [
        candidate(
            path,
            "sandwurm",
            "unreferenced superseded sync dishonest-storage raw root",
            now,
        )
        for path in unreferenced[keep_unreferenced:]
    ]


def sync_log_writes_prefix_proof_candidates(
    now: float, keep_unreferenced: int
) -> list[Candidate]:
    protected = tracked_proof_roots()
    unreferenced = [
        path
        for path in immediate_children(SYNC_LOG_WRITES_PREFIX_LAB_ROOT)
        if not path.is_symlink()
        and path.is_dir()
        and SYNC_LOG_WRITES_PREFIX_NAME.fullmatch(path.name) is not None
        and path.resolve() not in protected
        and open_reference(path.resolve()) is None
    ]
    unreferenced.sort(key=sort_mtime, reverse=True)
    return [
        candidate(
            path,
            "sandwurm",
            "unreferenced superseded sync log-writes prefix raw root",
            now,
        )
        for path in unreferenced[keep_unreferenced:]
    ]


def sync_production_prefix_proof_candidates(
    now: float, keep_unreferenced: int
) -> list[Candidate]:
    protected = tracked_proof_roots()
    unreferenced = [
        path
        for path in immediate_children(SYNC_PRODUCTION_PREFIX_LAB_ROOT)
        if not path.is_symlink()
        and path.is_dir()
        and SYNC_PRODUCTION_PREFIX_NAME.fullmatch(path.name) is not None
        and path.resolve() not in protected
        and open_reference(path.resolve()) is None
    ]
    unreferenced.sort(key=sort_mtime, reverse=True)
    return [
        candidate(
            path,
            "sandwurm",
            "unreferenced superseded sync production-prefix raw root",
            now,
        )
        for path in unreferenced[keep_unreferenced:]
    ]


def metadata_corruption_proof_candidates(
    now: float, keep_unreferenced: int
) -> list[Candidate]:
    protected = tracked_proof_roots()
    unreferenced = [
        path
        for path in immediate_children(METADATA_CORRUPTION_LAB_ROOT)
        if not path.is_symlink()
        and path.is_dir()
        and METADATA_CORRUPTION_NAME.fullmatch(path.name) is not None
        and path.resolve() not in protected
        and open_reference(path.resolve()) is None
    ]
    unreferenced.sort(key=sort_mtime, reverse=True)
    return [
        candidate(
            path,
            "sandwurm",
            "unreferenced superseded sync metadata-corruption proof root",
            now,
        )
        for path in unreferenced[keep_unreferenced:]
    ]


def projection_descriptor_proof_candidates(
    now: float, keep_unreferenced: int
) -> list[Candidate]:
    protected = tracked_proof_roots()
    unreferenced = [
        path
        for path in immediate_children(PROJECTION_DESCRIPTOR_LAB_ROOT)
        if not path.is_symlink()
        and path.is_dir()
        and PROJECTION_DESCRIPTOR_NAME.fullmatch(path.name) is not None
        and path.resolve() not in protected
        and open_reference(path.resolve()) is None
    ]
    unreferenced.sort(key=sort_mtime, reverse=True)
    return [
        candidate(
            path,
            "sandwurm",
            "unreferenced superseded sync projection-descriptor proof root",
            now,
        )
        for path in unreferenced[keep_unreferenced:]
    ]


def power_cut_proof_candidates(
    now: float, keep_unreferenced: int
) -> list[Candidate]:
    protected = tracked_proof_roots()
    values = []
    for parent in POWER_CUT_LAB_ROOTS:
        unreferenced = [
            path
            for path in immediate_children(parent)
            if not path.is_symlink()
            and path.is_dir()
            and POWER_CUT_NAME.fullmatch(path.name) is not None
            and path.resolve() not in protected
            and open_reference(path.resolve()) is None
        ]
        unreferenced.sort(key=sort_mtime, reverse=True)
        values.extend(
            candidate(
                path,
                "sandwurm",
                "unreferenced superseded sync power-cut proof root",
                now,
            )
            for path in unreferenced[keep_unreferenced:]
        )
    return values


def compact_proof_candidates(now: float, keep_unreferenced: int) -> list[Candidate]:
    protected = tracked_compact_pair_roots()
    unreferenced = [
        path
        for path in immediate_children(COMPACT_PAIR_ROOT)
        if not path.is_symlink()
        and path.is_dir()
        and PROOF_NAMES["pairs"].fullmatch(path.name) is not None
        and path.resolve() not in protected
    ]
    unreferenced.sort(key=sort_mtime, reverse=True)
    return [
        candidate(
            path,
            "sandwurm",
            "unreferenced superseded compact proof root",
            now,
        )
        for path in unreferenced[keep_unreferenced:]
    ]


def compact_three_writer_candidates(
    now: float, keep_unreferenced: int
) -> list[Candidate]:
    protected = tracked_compact_three_writer_roots()
    unreferenced = [
        path
        for path in immediate_children(COMPACT_THREE_WRITER_ROOT)
        if not path.is_symlink()
        and path.is_dir()
        and THREE_WRITER_NAME.fullmatch(path.name) is not None
        and path.resolve() not in protected
    ]
    unreferenced.sort(key=sort_mtime, reverse=True)
    return [
        candidate(
            path,
            "sandwurm",
            "unreferenced superseded compact three-writer proof root",
            now,
        )
        for path in unreferenced[keep_unreferenced:]
    ]


def compact_sync_shadow_candidates(
    now: float, keep_unreferenced: int
) -> list[Candidate]:
    protected = tracked_compact_sync_shadow_roots()
    unreferenced = [
        path
        for path in immediate_children(COMPACT_SYNC_SHADOW_ROOT)
        if not path.is_symlink()
        and path.is_dir()
        and SYNC_SHADOW_NAME.fullmatch(path.name) is not None
        and path.resolve() not in protected
    ]
    unreferenced.sort(key=sort_mtime, reverse=True)
    return [
        candidate(
            path,
            "sandwurm",
            "unreferenced superseded compact sync-shadow proof root",
            now,
        )
        for path in unreferenced[keep_unreferenced:]
    ]


def compact_sync_recovery_custody_candidates(
    now: float, keep_unreferenced: int
) -> list[Candidate]:
    protected = tracked_compact_sync_recovery_custody_roots()
    unreferenced = [
        path
        for path in immediate_children(COMPACT_SYNC_RECOVERY_CUSTODY_ROOT)
        if not path.is_symlink()
        and path.is_dir()
        and SYNC_RECOVERY_CUSTODY_NAME.fullmatch(path.name) is not None
        and path.resolve() not in protected
    ]
    unreferenced.sort(key=sort_mtime, reverse=True)
    return [
        candidate(
            path,
            "sandwurm",
            "unreferenced superseded compact sync recovery-custody root",
            now,
        )
        for path in unreferenced[keep_unreferenced:]
    ]


def compact_sync_dishonest_storage_candidates(
    now: float, keep_unreferenced: int
) -> list[Candidate]:
    protected = tracked_compact_sync_dishonest_storage_roots()
    unreferenced = [
        path
        for path in immediate_children(COMPACT_SYNC_DISHONEST_STORAGE_ROOT)
        if not path.is_symlink()
        and path.is_dir()
        and SYNC_DISHONEST_STORAGE_NAME.fullmatch(path.name) is not None
        and path.resolve() not in protected
    ]
    unreferenced.sort(key=sort_mtime, reverse=True)
    return [
        candidate(
            path,
            "sandwurm",
            "unreferenced superseded compact sync dishonest-storage root",
            now,
        )
        for path in unreferenced[keep_unreferenced:]
    ]


def compact_sync_log_writes_prefix_candidates(
    now: float, keep_unreferenced: int
) -> list[Candidate]:
    protected = tracked_compact_sync_log_writes_prefix_roots()
    unreferenced = [
        path
        for path in immediate_children(COMPACT_SYNC_LOG_WRITES_PREFIX_ROOT)
        if not path.is_symlink()
        and path.is_dir()
        and SYNC_LOG_WRITES_PREFIX_NAME.fullmatch(path.name) is not None
        and path.resolve() not in protected
    ]
    unreferenced.sort(key=sort_mtime, reverse=True)
    return [
        candidate(
            path,
            "sandwurm",
            "unreferenced superseded compact sync log-writes prefix root",
            now,
        )
        for path in unreferenced[keep_unreferenced:]
    ]


def compact_sync_production_prefix_candidates(
    now: float, keep_unreferenced: int
) -> list[Candidate]:
    protected = tracked_compact_sync_production_prefix_roots()
    unreferenced = [
        path
        for path in immediate_children(COMPACT_SYNC_PRODUCTION_PREFIX_ROOT)
        if not path.is_symlink()
        and path.is_dir()
        and SYNC_PRODUCTION_PREFIX_NAME.fullmatch(path.name) is not None
        and path.resolve() not in protected
    ]
    unreferenced.sort(key=sort_mtime, reverse=True)
    return [
        candidate(
            path,
            "sandwurm",
            "unreferenced superseded compact sync production-prefix root",
            now,
        )
        for path in unreferenced[keep_unreferenced:]
    ]


def compact_metadata_corruption_candidates(
    now: float, keep_unreferenced: int
) -> list[Candidate]:
    protected = tracked_compact_metadata_corruption_roots()
    unreferenced = [
        path
        for path in immediate_children(COMPACT_METADATA_CORRUPTION_ROOT)
        if not path.is_symlink()
        and path.is_dir()
        and METADATA_CORRUPTION_NAME.fullmatch(path.name) is not None
        and path.resolve() not in protected
    ]
    unreferenced.sort(key=sort_mtime, reverse=True)
    return [
        candidate(
            path,
            "sandwurm",
            "unreferenced superseded compact metadata-corruption proof root",
            now,
        )
        for path in unreferenced[keep_unreferenced:]
    ]


def compact_projection_descriptor_candidates(
    now: float, keep_unreferenced: int
) -> list[Candidate]:
    protected = tracked_compact_projection_descriptor_roots()
    unreferenced = [
        path
        for path in immediate_children(COMPACT_PROJECTION_DESCRIPTOR_ROOT)
        if not path.is_symlink()
        and path.is_dir()
        and PROJECTION_DESCRIPTOR_NAME.fullmatch(path.name) is not None
        and path.resolve() not in protected
    ]
    unreferenced.sort(key=sort_mtime, reverse=True)
    return [
        candidate(
            path,
            "sandwurm",
            "unreferenced superseded compact projection-descriptor proof root",
            now,
        )
        for path in unreferenced[keep_unreferenced:]
    ]


def compact_power_cut_candidates(
    now: float, keep_unreferenced: int
) -> list[Candidate]:
    protected = tracked_compact_power_cut_roots()
    unreferenced = [
        path
        for path in immediate_children(COMPACT_POWER_CUT_ROOT)
        if not path.is_symlink()
        and path.is_dir()
        and POWER_CUT_NAME.fullmatch(path.name) is not None
        and path.resolve() not in protected
    ]
    unreferenced.sort(key=sort_mtime, reverse=True)
    return [
        candidate(
            path,
            "sandwurm",
            "unreferenced superseded compact sync power-cut proof root",
            now,
        )
        for path in unreferenced[keep_unreferenced:]
    ]


def device_repair_candidates(now: float) -> list[Candidate]:
    return [
        candidate(
            path,
            "sandwurm",
            "allowlisted offline guest-disk repair workspace",
            now,
        )
        for path in immediate_children(SANDWURM_ROOT)
        if not path.is_symlink()
        and path.is_dir()
        and DEVICE_REPAIR_NAME.fullmatch(path.name) is not None
    ]


def operator_tor_candidates(now: float, keep_unreferenced: int) -> list[Candidate]:
    unreferenced = [
        path
        for path in immediate_children(OPERATOR_TOR_ROOT)
        if not path.is_symlink()
        and path.is_dir()
        and OPERATOR_TOR_NAME.fullmatch(path.name) is not None
        and open_reference(path.resolve()) is None
    ]
    unreferenced.sort(key=sort_mtime, reverse=True)
    return [
        candidate(path, "operator-tor", "failed or explicitly retained Tor route root", now)
        for path in unreferenced[keep_unreferenced:]
    ]


def build_candidates(now: float, drop_current_builds: bool) -> list[Candidate]:
    values = []
    for parent in BUILD_ROOTS:
        for path in immediate_children(parent):
            if path.is_symlink():
                continue
            if path.is_file() and BUILD_FILE_NAME.fullmatch(path.name) is not None:
                values.append(
                    candidate(path, "build", "reproducible stale build file", now)
                )
                continue
            if not path.is_dir():
                continue
            if (
                parent == ROOT / "build"
                and path.name in KEPT_BUILD_NAMES
                and not drop_current_builds
            ):
                continue
            reason = (
                "reproducible current build tree"
                if parent == ROOT / "build" and path.name in KEPT_BUILD_NAMES
                else "reproducible non-current build tree"
            )
            values.append(candidate(path, "build", reason, now))
    for path in immediate_children(ROOT):
        if (
            path.is_symlink()
            or not path.is_dir()
            or TOP_LEVEL_BUILD_NAME.fullmatch(path.name) is None
        ):
            continue
        values.append(
            candidate(path, "build", "reproducible top-level build tree", now)
        )
    return values


def mount_paths() -> tuple[Path, ...]:
    result = subprocess.run(
        ["findmnt", "-rn", "-o", "TARGET"],
        check=True,
        text=True,
        capture_output=True,
    )
    return tuple(Path(line).resolve() for line in result.stdout.splitlines() if line)


def path_contains(parent: Path, child: Path) -> bool:
    return child == parent or child.is_relative_to(parent)


def open_reference(candidate_path: Path) -> str | None:
    for process in Path("/proc").iterdir():
        if not process.name.isdigit():
            continue
        for relative in ("cwd", "root"):
            try:
                target = (process / relative).resolve(strict=True)
            except (FileNotFoundError, PermissionError, OSError):
                continue
            if path_contains(candidate_path, target):
                return f"pid {process.name} {relative}"
        descriptors = process / "fd"
        try:
            entries = tuple(descriptors.iterdir())
        except (FileNotFoundError, PermissionError, OSError):
            continue
        for descriptor in entries:
            try:
                target = descriptor.resolve(strict=True)
            except (FileNotFoundError, PermissionError, OSError):
                continue
            if path_contains(candidate_path, target):
                return f"pid {process.name} fd {descriptor.name}"
    return None


def validate_deletion(item: Candidate, mounts: tuple[Path, ...]) -> None:
    path = item.path
    allowed_parents = (
        TEMP_ROOT,
        SANDWORM_TRASH_FILES_ROOT,
        SANDWORM_TRASH_INFO_ROOT,
        LAB_ROOT / "pairs",
        LAB_ROOT / "client",
        LAB_ROOT / "device",
        *three_writer_lab_roots(),
        SYNC_SHADOW_LAB_ROOT,
        SYNC_RECOVERY_CUSTODY_LAB_ROOT,
        SYNC_DISHONEST_STORAGE_LAB_ROOT,
        SYNC_LOG_WRITES_PREFIX_LAB_ROOT,
        SYNC_PRODUCTION_PREFIX_LAB_ROOT,
        METADATA_CORRUPTION_LAB_ROOT,
        PROJECTION_DESCRIPTOR_LAB_ROOT,
        *POWER_CUT_LAB_ROOTS,
        COMPACT_PAIR_ROOT,
        COMPACT_THREE_WRITER_ROOT,
        COMPACT_SYNC_SHADOW_ROOT,
        COMPACT_SYNC_RECOVERY_CUSTODY_ROOT,
        COMPACT_SYNC_DISHONEST_STORAGE_ROOT,
        COMPACT_SYNC_LOG_WRITES_PREFIX_ROOT,
        COMPACT_SYNC_PRODUCTION_PREFIX_ROOT,
        COMPACT_METADATA_CORRUPTION_ROOT,
        COMPACT_PROJECTION_DESCRIPTOR_ROOT,
        COMPACT_POWER_CUT_ROOT,
        SANDWURM_ROOT,
        OPERATOR_TOR_ROOT,
        *BUILD_ROOTS,
    )
    top_level_build = (
        item.category == "build"
        and path.parent == ROOT
        and TOP_LEVEL_BUILD_NAME.fullmatch(path.name) is not None
    )
    if path.parent not in allowed_parents and not top_level_build:
        fail(f"candidate escaped an allowlisted parent: {path}")
    if (
        path.parent == SANDWURM_ROOT
        and DEVICE_REPAIR_NAME.fullmatch(path.name) is None
    ):
        fail(f"candidate is not an allowlisted guest-disk repair root: {path}")
    if path == ROOT or not path.is_relative_to(ROOT):
        fail(f"candidate escaped the repository: {path}")
    if path.is_symlink() or not path.exists():
        fail(f"candidate changed type or disappeared: {path}")
    for mount in mounts:
        if path_contains(path, mount):
            fail(f"candidate contains a mount point: {path} contains {mount}")
    reference = open_reference(path)
    if reference is not None:
        fail(f"candidate is live ({reference}): {path}")


def remove_candidate(item: Candidate) -> None:
    try:
        shutil.rmtree(item.path) if item.path.is_dir() else item.path.unlink()
        return
    except PermissionError:
        # Sandwurm launch and receipt steps may leave root-owned files beneath
        # an otherwise user-owned, already validated proof root. Escalate only
        # for this exact allowlisted candidate after all confinement, mount,
        # symlink, and live-reference checks have passed.
        subprocess.run(
            [
                "sudo",
                "-n",
                str(HOST_RM),
                "-rf",
                "--one-file-system",
                "--",
                str(item.path),
            ],
            check=True,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scope",
        action="append",
        choices=(
            "temp",
            "sandwurm",
            "sync-shadow",
            "sync-recovery-custody",
            "sync-dishonest-storage",
            "sync-log-writes-prefix",
            "sync-production-prefix",
            "sync-metadata-corruption",
            "sync-projection-descriptor",
            "sync-power-cut",
            "operator-tor",
            "build",
            "all",
        ),
        help="category to audit; repeatable (default: temp and sandwurm)",
    )
    parser.add_argument("--apply", action="store_true", help="delete listed candidates")
    parser.add_argument(
        "--min-temp-age-hours",
        type=float,
        default=24.0,
        help="minimum age for allowlisted sandbox temporary entries",
    )
    parser.add_argument(
        "--keep-unreferenced-proofs",
        type=int,
        default=1,
        help="newest undocumented proof roots retained per Sandwurm role/class",
    )
    parser.add_argument(
        "--keep-unreferenced-three-writer-proofs",
        type=int,
        default=1,
        help="newest undocumented raw three-writer roots retained",
    )
    parser.add_argument(
        "--drop-current-builds",
        action="store_true",
        help="also prune kept current build trees such as build/gcc-debug",
    )
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def self_test() -> int:
    if OPERATOR_TOR_NAME.fullmatch("run.a_b9") is None:
        fail("operator-Tor cleanup name alphabet omitted underscore")
    if OPERATOR_TOR_NAME.fullmatch("run.bad/name") is not None:
        fail("operator-Tor cleanup name pattern accepted a path separator")
    if METADATA_CORRUPTION_NAME.fullmatch("run.a_b9") is None:
        fail("metadata-corruption cleanup name alphabet omitted underscore")
    if METADATA_CORRUPTION_NAME.fullmatch("run.bad/name") is not None:
        fail("metadata-corruption cleanup accepted a path separator")
    if SYNC_DISHONEST_STORAGE_NAME.fullmatch("run.a_b9") is None:
        fail("dishonest-storage cleanup name alphabet omitted underscore")
    if SYNC_DISHONEST_STORAGE_NAME.fullmatch("run.bad/name") is not None:
        fail("dishonest-storage cleanup accepted a path separator")
    OPERATOR_TOR_ROOT.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix="run.", dir=OPERATOR_TOR_ROOT)).resolve()
    try:
        selected = {
            item.path.resolve()
            for item in operator_tor_candidates(time.time(), keep_unreferenced=0)
        }
        if scratch not in selected:
            fail("operator-Tor cleanup self-test root was not selected")
    finally:
        scratch.rmdir()
    repair = Path(
        tempfile.mkdtemp(prefix="iotox-device-repair.", dir=SANDWURM_ROOT)
    ).resolve()
    try:
        selected = {
            item.path.resolve()
            for item in device_repair_candidates(time.time())
        }
        if repair not in selected:
            fail("guest-disk repair cleanup self-test root was not selected")
    finally:
        repair.rmdir()
    COMPACT_PAIR_ROOT.mkdir(parents=True, exist_ok=True)
    compact = Path(tempfile.mkdtemp(prefix="pair.", dir=COMPACT_PAIR_ROOT)).resolve()
    try:
        selected = {
            item.path.resolve()
            for item in compact_proof_candidates(time.time(), keep_unreferenced=0)
        }
        if compact not in selected:
            fail("compact-proof cleanup self-test root was not selected")
    finally:
        compact.rmdir()
    THREE_WRITER_LAB_ROOT.mkdir(parents=True, exist_ok=True)
    COMPACT_THREE_WRITER_ROOT.mkdir(parents=True, exist_ok=True)
    three_writer = Path(
        tempfile.mkdtemp(prefix="run.", dir=THREE_WRITER_LAB_ROOT)
    ).resolve()
    try:
        selected = {
            item.path.resolve()
            for item in three_writer_proof_candidates(
                time.time(), keep_unreferenced=0
            )
        }
        if three_writer not in selected:
            fail("unreferenced three-writer raw proof was not selected")
    finally:
        shutil.rmtree(three_writer)
    near_ceiling_parent = LAB_ROOT / "three-writer-near-ceiling-cap-8"
    near_ceiling_parent.mkdir(parents=True, exist_ok=True)
    near_ceiling_three_writer = Path(
        tempfile.mkdtemp(prefix="run.", dir=near_ceiling_parent)
    ).resolve()
    try:
        selected = {
            item.path.resolve()
            for item in three_writer_proof_candidates(
                time.time(), keep_unreferenced=0
            )
        }
        if near_ceiling_three_writer not in selected:
            fail("unreferenced near-ceiling three-writer raw proof was not selected")
    finally:
        shutil.rmtree(near_ceiling_three_writer)
    soak_parent = LAB_ROOT / "three-writer-soak-smoke"
    soak_parent.mkdir(parents=True, exist_ok=True)
    soak_three_writer = Path(
        tempfile.mkdtemp(prefix="run.", dir=soak_parent)
    ).resolve()
    try:
        selected = {
            item.path.resolve()
            for item in three_writer_proof_candidates(
                time.time(), keep_unreferenced=0
            )
        }
        if soak_three_writer not in selected:
            fail("unreferenced soak three-writer raw proof was not selected")
    finally:
        shutil.rmtree(soak_three_writer)
    SYNC_SHADOW_LAB_ROOT.mkdir(parents=True, exist_ok=True)
    COMPACT_SYNC_SHADOW_ROOT.mkdir(parents=True, exist_ok=True)
    sync_shadow = Path(
        tempfile.mkdtemp(prefix="run.", dir=SYNC_SHADOW_LAB_ROOT)
    ).resolve()
    try:
        sentinel = sync_shadow / "active"
        sentinel.write_bytes(b"active")
        with sentinel.open("rb"):
            selected = {
                item.path.resolve()
                for item in sync_shadow_proof_candidates(
                    time.time(), keep_unreferenced=0
                )
            }
            if sync_shadow in selected:
                fail("active sync-shadow raw proof was selected")
        selected = {
            item.path.resolve()
            for item in sync_shadow_proof_candidates(
                time.time(), keep_unreferenced=0
            )
        }
        if sync_shadow not in selected:
            fail("unreferenced sync-shadow raw proof was not selected")
    finally:
        shutil.rmtree(sync_shadow)
    compact_shadow = Path(
        tempfile.mkdtemp(prefix="run.", dir=COMPACT_SYNC_SHADOW_ROOT)
    ).resolve()
    try:
        selected = {
            item.path.resolve()
            for item in compact_sync_shadow_candidates(
                time.time(), keep_unreferenced=0
            )
        }
        if compact_shadow not in selected:
            fail("unreferenced sync-shadow compact proof was not selected")
    finally:
        shutil.rmtree(compact_shadow)
    SYNC_RECOVERY_CUSTODY_LAB_ROOT.mkdir(parents=True, exist_ok=True)
    COMPACT_SYNC_RECOVERY_CUSTODY_ROOT.mkdir(parents=True, exist_ok=True)
    recovery_custody = Path(
        tempfile.mkdtemp(prefix="run.", dir=SYNC_RECOVERY_CUSTODY_LAB_ROOT)
    ).resolve()
    try:
        selected = {
            item.path.resolve()
            for item in sync_recovery_custody_proof_candidates(
                time.time(), keep_unreferenced=0
            )
        }
        if recovery_custody not in selected:
            fail("unreferenced recovery-custody raw proof was not selected")
    finally:
        shutil.rmtree(recovery_custody)
    compact_recovery_custody = Path(
        tempfile.mkdtemp(prefix="run.", dir=COMPACT_SYNC_RECOVERY_CUSTODY_ROOT)
    ).resolve()
    try:
        selected = {
            item.path.resolve()
            for item in compact_sync_recovery_custody_candidates(
                time.time(), keep_unreferenced=0
            )
        }
        if compact_recovery_custody not in selected:
            fail("unreferenced recovery-custody compact proof was not selected")
    finally:
        shutil.rmtree(compact_recovery_custody)
    SYNC_DISHONEST_STORAGE_LAB_ROOT.mkdir(parents=True, exist_ok=True)
    COMPACT_SYNC_DISHONEST_STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
    dishonest_storage = Path(
        tempfile.mkdtemp(prefix="run.", dir=SYNC_DISHONEST_STORAGE_LAB_ROOT)
    ).resolve()
    try:
        selected = {
            item.path.resolve()
            for item in sync_dishonest_storage_proof_candidates(
                time.time(), keep_unreferenced=0
            )
        }
        if dishonest_storage not in selected:
            fail("unreferenced dishonest-storage raw proof was not selected")
    finally:
        shutil.rmtree(dishonest_storage)
    compact_dishonest_storage = Path(
        tempfile.mkdtemp(prefix="run.", dir=COMPACT_SYNC_DISHONEST_STORAGE_ROOT)
    ).resolve()
    try:
        selected = {
            item.path.resolve()
            for item in compact_sync_dishonest_storage_candidates(
                time.time(), keep_unreferenced=0
            )
        }
        if compact_dishonest_storage not in selected:
            fail("unreferenced dishonest-storage compact proof was not selected")
    finally:
        shutil.rmtree(compact_dishonest_storage)
    SYNC_LOG_WRITES_PREFIX_LAB_ROOT.mkdir(parents=True, exist_ok=True)
    COMPACT_SYNC_LOG_WRITES_PREFIX_ROOT.mkdir(parents=True, exist_ok=True)
    log_writes_prefix = Path(
        tempfile.mkdtemp(prefix="run.", dir=SYNC_LOG_WRITES_PREFIX_LAB_ROOT)
    ).resolve()
    try:
        selected = {
            item.path.resolve()
            for item in sync_log_writes_prefix_proof_candidates(
                time.time(), keep_unreferenced=0
            )
        }
        if log_writes_prefix not in selected:
            fail("unreferenced log-writes prefix raw proof was not selected")
    finally:
        shutil.rmtree(log_writes_prefix)
    compact_log_writes_prefix = Path(
        tempfile.mkdtemp(prefix="run.", dir=COMPACT_SYNC_LOG_WRITES_PREFIX_ROOT)
    ).resolve()
    try:
        selected = {
            item.path.resolve()
            for item in compact_sync_log_writes_prefix_candidates(
                time.time(), keep_unreferenced=0
            )
        }
        if compact_log_writes_prefix not in selected:
            fail("unreferenced log-writes prefix compact proof was not selected")
    finally:
        shutil.rmtree(compact_log_writes_prefix)
    SYNC_PRODUCTION_PREFIX_LAB_ROOT.mkdir(parents=True, exist_ok=True)
    COMPACT_SYNC_PRODUCTION_PREFIX_ROOT.mkdir(parents=True, exist_ok=True)
    production_prefix = Path(
        tempfile.mkdtemp(prefix="run.", dir=SYNC_PRODUCTION_PREFIX_LAB_ROOT)
    ).resolve()
    try:
        selected = {
            item.path.resolve()
            for item in sync_production_prefix_proof_candidates(
                time.time(), keep_unreferenced=0
            )
        }
        if production_prefix not in selected:
            fail("unreferenced production prefix raw proof was not selected")
    finally:
        shutil.rmtree(production_prefix)
    compact_production_prefix = Path(
        tempfile.mkdtemp(prefix="run.", dir=COMPACT_SYNC_PRODUCTION_PREFIX_ROOT)
    ).resolve()
    try:
        selected = {
            item.path.resolve()
            for item in compact_sync_production_prefix_candidates(
                time.time(), keep_unreferenced=0
            )
        }
        if compact_production_prefix not in selected:
            fail("unreferenced production prefix compact proof was not selected")
    finally:
        shutil.rmtree(compact_production_prefix)
    METADATA_CORRUPTION_LAB_ROOT.mkdir(parents=True, exist_ok=True)
    COMPACT_METADATA_CORRUPTION_ROOT.mkdir(parents=True, exist_ok=True)
    metadata_corruption = Path(
        tempfile.mkdtemp(prefix="run.", dir=METADATA_CORRUPTION_LAB_ROOT)
    ).resolve()
    try:
        sentinel = metadata_corruption / "active"
        sentinel.write_bytes(b"active")
        with sentinel.open("rb"):
            selected = {
                item.path.resolve()
                for item in metadata_corruption_proof_candidates(
                    time.time(), keep_unreferenced=0
                )
            }
            if metadata_corruption in selected:
                fail("active metadata-corruption raw proof was selected")
        selected = {
            item.path.resolve()
            for item in metadata_corruption_proof_candidates(
                time.time(), keep_unreferenced=0
            )
        }
        if metadata_corruption not in selected:
            fail("unreferenced metadata-corruption raw proof was not selected")
    finally:
        shutil.rmtree(metadata_corruption)
    compact_metadata_corruption = Path(
        tempfile.mkdtemp(prefix="run.", dir=COMPACT_METADATA_CORRUPTION_ROOT)
    ).resolve()
    try:
        selected = {
            item.path.resolve()
            for item in compact_metadata_corruption_candidates(
                time.time(), keep_unreferenced=0
            )
        }
        if compact_metadata_corruption not in selected:
            fail(
                "unreferenced metadata-corruption compact proof was not selected"
            )
    finally:
        shutil.rmtree(compact_metadata_corruption)
    COMPACT_POWER_CUT_ROOT.mkdir(parents=True, exist_ok=True)
    for power_cut_parent in POWER_CUT_LAB_ROOTS:
        power_cut_parent.mkdir(parents=True, exist_ok=True)
        power_cut = Path(
            tempfile.mkdtemp(prefix="run.", dir=power_cut_parent)
        ).resolve()
        try:
            selected = {
                item.path.resolve()
                for item in power_cut_proof_candidates(
                    time.time(), keep_unreferenced=0
                )
            }
            if power_cut not in selected:
                fail(
                    "unreferenced sync power-cut raw proof was not selected: "
                    f"{power_cut_parent.name}"
                )
        finally:
            shutil.rmtree(power_cut)
    compact_power_cut = Path(
        tempfile.mkdtemp(prefix="run.", dir=COMPACT_POWER_CUT_ROOT)
    ).resolve()
    try:
        selected = {
            item.path.resolve()
            for item in compact_power_cut_candidates(
                time.time(), keep_unreferenced=0
            )
        }
        if compact_power_cut not in selected:
            fail("unreferenced sync power-cut compact proof was not selected")
    finally:
        shutil.rmtree(compact_power_cut)
    SANDWORM_TRASH_FILES_ROOT.mkdir(parents=True, exist_ok=True)
    SANDWORM_TRASH_INFO_ROOT.mkdir(parents=True, exist_ok=True)
    disappeared = Path(
        tempfile.mkdtemp(prefix="run.", dir=SANDWORM_TRASH_FILES_ROOT)
    ).resolve()
    shutil.rmtree(disappeared)
    if allocated_bytes(disappeared) != 0:
        fail("disappeared candidate size calculation did not fail open")
    sandbox_trash = Path(
        tempfile.mkdtemp(prefix="run.", dir=SANDWORM_TRASH_FILES_ROOT)
    ).resolve()
    sandbox_info = SANDWORM_TRASH_INFO_ROOT / f"{sandbox_trash.name}.trashinfo"
    try:
        sandbox_info.write_text(
            "[Trash Info]\nPath=/workspace/.sandwurm/lab/three-writer/"
            f"{sandbox_trash.name}\n",
            encoding="utf-8",
        )
        selected = {
            item.path.resolve()
            for item in sandbox_trash_candidates(time.time(), minimum_age=0.0)
        }
        if sandbox_trash not in selected:
            fail("nested sandbox trash payload was not selected")
        if sandbox_info.resolve() not in selected:
            fail("nested sandbox trash metadata was not selected")
    finally:
        shutil.rmtree(sandbox_trash)
        sandbox_info.unlink(missing_ok=True)
    print("iotox workspace cleaner self-test: PASS")
    return 0


def main() -> int:
    args = parse_args()
    if args.self_test:
        return self_test()
    if args.min_temp_age_hours < 1.0:
        fail("minimum temporary age must be at least one hour")
    if args.keep_unreferenced_proofs < 0:
        fail("proof retention count cannot be negative")
    if args.keep_unreferenced_three_writer_proofs < 0:
        fail("three-writer proof retention count cannot be negative")
    scopes = set(args.scope or ("temp", "sandwurm", "operator-tor"))
    if "all" in scopes:
        scopes = {"temp", "sandwurm", "operator-tor", "build"}
    now = time.time()
    candidates = []
    if "temp" in scopes:
        candidates.extend(temp_candidates(now, args.min_temp_age_hours))
        candidates.extend(sandbox_trash_candidates(now, args.min_temp_age_hours))
    if "sandwurm" in scopes:
        candidates.extend(proof_candidates(now, args.keep_unreferenced_proofs))
        candidates.extend(
            three_writer_proof_candidates(
                now, args.keep_unreferenced_three_writer_proofs
            )
        )
        candidates.extend(
            sync_shadow_proof_candidates(now, args.keep_unreferenced_proofs)
        )
        candidates.extend(
            sync_recovery_custody_proof_candidates(
                now, args.keep_unreferenced_proofs
            )
        )
        candidates.extend(
            sync_dishonest_storage_proof_candidates(
                now, args.keep_unreferenced_proofs
            )
        )
        candidates.extend(
            sync_log_writes_prefix_proof_candidates(
                now, args.keep_unreferenced_proofs
            )
        )
        candidates.extend(
            sync_production_prefix_proof_candidates(
                now, args.keep_unreferenced_proofs
            )
        )
        candidates.extend(
            metadata_corruption_proof_candidates(
                now, args.keep_unreferenced_proofs
            )
        )
        candidates.extend(
            projection_descriptor_proof_candidates(
                now, args.keep_unreferenced_proofs
            )
        )
        candidates.extend(
            power_cut_proof_candidates(now, args.keep_unreferenced_proofs)
        )
        candidates.extend(compact_proof_candidates(now, args.keep_unreferenced_proofs))
        candidates.extend(
            compact_three_writer_candidates(now, args.keep_unreferenced_proofs)
        )
        candidates.extend(
            compact_sync_shadow_candidates(now, args.keep_unreferenced_proofs)
        )
        candidates.extend(
            compact_sync_recovery_custody_candidates(
                now, args.keep_unreferenced_proofs
            )
        )
        candidates.extend(
            compact_sync_dishonest_storage_candidates(
                now, args.keep_unreferenced_proofs
            )
        )
        candidates.extend(
            compact_sync_log_writes_prefix_candidates(
                now, args.keep_unreferenced_proofs
            )
        )
        candidates.extend(
            compact_sync_production_prefix_candidates(
                now, args.keep_unreferenced_proofs
            )
        )
        candidates.extend(
            compact_metadata_corruption_candidates(
                now, args.keep_unreferenced_proofs
            )
        )
        candidates.extend(
            compact_projection_descriptor_candidates(
                now, args.keep_unreferenced_proofs
            )
        )
        candidates.extend(
            compact_power_cut_candidates(now, args.keep_unreferenced_proofs)
        )
        candidates.extend(device_repair_candidates(now))
    elif "sync-shadow" in scopes:
        candidates.extend(
            sync_shadow_proof_candidates(now, args.keep_unreferenced_proofs)
        )
        candidates.extend(
            compact_sync_shadow_candidates(now, args.keep_unreferenced_proofs)
        )
    elif "sync-recovery-custody" in scopes:
        candidates.extend(
            sync_recovery_custody_proof_candidates(
                now, args.keep_unreferenced_proofs
            )
        )
        candidates.extend(
            compact_sync_recovery_custody_candidates(
                now, args.keep_unreferenced_proofs
            )
        )
    elif "sync-dishonest-storage" in scopes:
        candidates.extend(
            sync_dishonest_storage_proof_candidates(
                now, args.keep_unreferenced_proofs
            )
        )
        candidates.extend(
            compact_sync_dishonest_storage_candidates(
                now, args.keep_unreferenced_proofs
            )
        )
    elif "sync-log-writes-prefix" in scopes:
        candidates.extend(
            sync_log_writes_prefix_proof_candidates(
                now, args.keep_unreferenced_proofs
            )
        )
        candidates.extend(
            compact_sync_log_writes_prefix_candidates(
                now, args.keep_unreferenced_proofs
            )
        )
    elif "sync-production-prefix" in scopes:
        candidates.extend(
            sync_production_prefix_proof_candidates(
                now, args.keep_unreferenced_proofs
            )
        )
        candidates.extend(
            compact_sync_production_prefix_candidates(
                now, args.keep_unreferenced_proofs
            )
        )
    elif "sync-metadata-corruption" in scopes:
        candidates.extend(
            metadata_corruption_proof_candidates(
                now, args.keep_unreferenced_proofs
            )
        )
        candidates.extend(
            compact_metadata_corruption_candidates(
                now, args.keep_unreferenced_proofs
            )
        )
    elif "sync-projection-descriptor" in scopes:
        candidates.extend(
            projection_descriptor_proof_candidates(
                now, args.keep_unreferenced_proofs
            )
        )
        candidates.extend(
            compact_projection_descriptor_candidates(
                now, args.keep_unreferenced_proofs
            )
        )
    elif "sync-power-cut" in scopes:
        candidates.extend(
            power_cut_proof_candidates(now, args.keep_unreferenced_proofs)
        )
        candidates.extend(
            compact_power_cut_candidates(now, args.keep_unreferenced_proofs)
        )
    if "operator-tor" in scopes:
        candidates.extend(operator_tor_candidates(now, args.keep_unreferenced_proofs))
    if "build" in scopes:
        candidates.extend(build_candidates(now, args.drop_current_builds))
    candidates.sort(key=lambda item: (item.category, str(item.path)))

    total = sum(item.allocated_bytes for item in candidates)
    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"mode={mode} candidates={len(candidates)} allocated={format_size(total)}")
    for item in candidates:
        relative = item.path.relative_to(ROOT)
        print(
            f"{item.category:9} {format_size(item.allocated_bytes):>10} "
            f"age={item.age_hours:7.1f}h {relative} ({item.reason})"
        )
    if not args.apply:
        print("nothing deleted; repeat with --apply after reviewing this exact scope")
        return 0

    mounts = mount_paths()
    for item in candidates:
        validate_deletion(item, mounts)
    for item in candidates:
        remove_candidate(item)
    print(f"deleted={len(candidates)} reclaimed-allocated={format_size(total)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"workspace cleanup refused: {error}", file=sys.stderr)
        raise SystemExit(1)
