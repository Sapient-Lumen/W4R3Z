from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

_SOURCE = os.environ.get("NICOTINE_SOURCE")
if _SOURCE:
    sys.path.insert(0, str(Path(_SOURCE).resolve()))
else:
    sys.path.insert(0, str(Path.cwd().resolve()))

from pynicotine.shares import Scanner  # noqa: E402


VIRTUAL_ROOT = "SharedRoot"
BASENAME = "same-name.bin"
STALE_SIZE = 123
STALE_QUALITY = (111, 0, 44100, 16)
STALE_DURATION = 7
FROZEN_MTIME = 1_700_000_000.0


class DummyWriter:
    def __init__(self):
        self.messages = []

    def put(self, msg):
        self.messages.append(msg)

    def send(self, msg):
        self.messages.append(msg)


def make_scanner(shared_folder: Path, *, rebuild: bool = False) -> Scanner:
    share_groups = ([(VIRTUAL_ROOT, str(shared_folder))], [], [])
    scanner = Scanner(
        DummyWriter(),
        share_groups,
        {},
        init=False,
        rescan=True,
        rebuild=rebuild,
        reveal_buddy_shares=False,
        reveal_trusted_shares=False,
    )
    # Current master initializes these through load_filters() during run(); direct scan probes need sane defaults.
    for attr in ("file_filter_regex", "folder_filter_regex"):
        if hasattr(scanner, attr):
            setattr(scanner, attr, None)
    return scanner


def write_file_with_frozen_mtime(shared_folder: Path, content: bytes) -> tuple[Path, float]:
    shared_folder.mkdir(parents=True, exist_ok=True)
    path = shared_folder / BASENAME
    path.write_bytes(content)
    os.utime(path, (FROZEN_MTIME, FROZEN_MTIME))
    return path, path.stat().st_mtime


def stale_cache_for(path: Path, mtime: float, virtual_root: str = VIRTUAL_ROOT):
    old_files = {
        str(path): [f"{virtual_root}\\{BASENAME}", STALE_SIZE, STALE_QUALITY, STALE_DURATION]
    }
    old_mtimes = {str(path): mtime}
    return old_mtimes, old_files


def scan_once(shared_folder: Path, old_mtimes: dict[str, float], old_files: dict[str, list], *, rebuild: bool = False):
    scanner = make_scanner(shared_folder, rebuild=rebuild)
    scanner.scan_shared_folder(str(shared_folder), old_mtimes, old_files)
    real_path = str(shared_folder / BASENAME)
    assert real_path in scanner.files
    return scanner.files[real_path]


def test_rescan_reuses_stale_size_when_mtime_matches_but_file_size_changes(tmp_path):
    shared_folder = tmp_path / "share"
    file_path, mtime = write_file_with_frozen_mtime(shared_folder, b"A" * 8192)
    old_mtimes, old_files = stale_cache_for(file_path, mtime)

    file_data = scan_once(shared_folder, old_mtimes, old_files)

    assert file_path.stat().st_size == 8192
    assert file_data[0] == f"{VIRTUAL_ROOT}\\{BASENAME}"
    assert file_data[1] == STALE_SIZE
    assert file_data[2] == STALE_QUALITY
    assert file_data[3] == STALE_DURATION


def test_rescan_reuses_stale_metadata_when_same_path_same_mtime_but_inode_replaced(tmp_path):
    shared_folder = tmp_path / "share"
    file_path, mtime = write_file_with_frozen_mtime(shared_folder, b"old")
    old_inode = file_path.stat().st_ino
    old_mtimes, old_files = stale_cache_for(file_path, mtime)

    file_path.unlink()
    file_path.write_bytes(b"B" * 4096)
    os.utime(file_path, (mtime, mtime))
    replacement_inode = file_path.stat().st_ino

    file_data = scan_once(shared_folder, old_mtimes, old_files)

    # Some filesystems may reuse inodes quickly, so the observed replacement inode is recorded but not required.
    assert file_path.stat().st_size == 4096
    assert replacement_inode == file_path.stat().st_ino
    assert old_inode == old_inode  # keep the variable visible in pytest assertion output if debugging
    assert file_data[1] == STALE_SIZE
    assert file_data[2] == STALE_QUALITY
    assert file_data[3] == STALE_DURATION


def test_mtime_change_recomputes_size_baseline(tmp_path):
    shared_folder = tmp_path / "share"
    file_path, mtime = write_file_with_frozen_mtime(shared_folder, b"A" * 8192)
    old_mtimes, old_files = stale_cache_for(file_path, mtime - 10.0)

    file_data = scan_once(shared_folder, old_mtimes, old_files)

    assert file_data[1] == 8192
    assert file_data[2] is None
    assert file_data[3] is None


def test_rebuild_recomputes_size_even_when_mtime_matches_baseline(tmp_path):
    shared_folder = tmp_path / "share"
    file_path, mtime = write_file_with_frozen_mtime(shared_folder, b"C" * 2048)
    old_mtimes, old_files = stale_cache_for(file_path, mtime)

    file_data = scan_once(shared_folder, old_mtimes, old_files, rebuild=True)

    assert file_data[1] == 2048
    assert file_data[2] is None
    assert file_data[3] is None


def test_virtual_name_update_mutates_old_cache_entry_but_keeps_stale_size(tmp_path):
    shared_folder = tmp_path / "share"
    file_path, mtime = write_file_with_frozen_mtime(shared_folder, b"D" * 4096)
    old_mtimes, old_files = stale_cache_for(file_path, mtime, virtual_root="OldVirtualRoot")

    file_data = scan_once(shared_folder, old_mtimes, old_files)

    assert old_files[str(file_path)] is file_data
    assert file_data[0] == f"{VIRTUAL_ROOT}\\{BASENAME}"
    assert file_data[1] == STALE_SIZE
