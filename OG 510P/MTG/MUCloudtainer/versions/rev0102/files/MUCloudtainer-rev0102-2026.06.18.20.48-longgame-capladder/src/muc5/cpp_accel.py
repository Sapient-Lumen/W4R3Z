from __future__ import annotations

import ctypes
import json
import os
import shutil
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np

PROBE_COLUMNS: Tuple[str, ...] = (
    "p_keepable_2_to_5_islands",
    "p_force_plus_pitch_open7",
    "p_counterspell_online_turn2_play",
    "p_overlord_impending_turn3_play",
    "p_jace_turn4_play",
    "p_overlord_full_turn5_play",
    "crude_probe_score",
)


@dataclass(frozen=True)
class CppToolchainStatus:
    gpp: str | None
    source_exists: bool
    shared_exists: bool
    kernel_version: int | None
    usable: bool
    error: str | None = None

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def source_path() -> Path:
    return project_root() / "cpp" / "muc5_probe_kernel.cpp"


def shared_path() -> Path:
    suffix = ".dylib" if os.name == "posix" and os.uname().sysname == "Darwin" else ".so"  # type: ignore[attr-defined]
    return project_root() / "build" / f"libmuc5_probe_kernel{suffix}"


def build_probe_kernel(*, force: bool = False) -> Path:
    src = source_path()
    out = shared_path()
    out.parent.mkdir(parents=True, exist_ok=True)
    gpp = shutil.which("g++")
    if not gpp:
        raise RuntimeError("g++ not available in this cloudtainer")
    if not src.exists():
        raise RuntimeError(f"C++ source missing: {src}")
    if force or not out.exists() or src.stat().st_mtime > out.stat().st_mtime:
        cmd = [gpp, "-O3", "-std=c++17", "-shared", "-fPIC", str(src), "-o", str(out)]
        subprocess.run(cmd, check=True, cwd=str(project_root()), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return out


class CppProbeKernel:
    def __init__(self, *, build: bool = True) -> None:
        lib_path = build_probe_kernel() if build else shared_path()
        self.lib_path = Path(lib_path)
        self.lib = ctypes.CDLL(str(self.lib_path))
        self.lib.muc5_probe_kernel_version.argtypes = []
        self.lib.muc5_probe_kernel_version.restype = ctypes.c_int
        self.lib.muc5_fill_probe_table.argtypes = [
            np.ctypeslib.ndpointer(dtype=np.int32, ndim=2, flags="C_CONTIGUOUS"),
            ctypes.c_int,
            np.ctypeslib.ndpointer(dtype=np.float64, ndim=2, flags="C_CONTIGUOUS"),
        ]
        self.lib.muc5_fill_probe_table.restype = ctypes.c_int
        self.version = int(self.lib.muc5_probe_kernel_version())

    def probe_table(self, deck_rows: np.ndarray) -> np.ndarray:
        arr = np.ascontiguousarray(deck_rows, dtype=np.int32)
        if arr.ndim != 2 or arr.shape[1] != 6:
            raise ValueError("deck_rows must be an n x 6 array: deck_size,island,counterspell,force,jace,overlord")
        out = np.empty((arr.shape[0], len(PROBE_COLUMNS)), dtype=np.float64)
        rc = int(self.lib.muc5_fill_probe_table(arr, int(arr.shape[0]), out))
        if rc != 0:
            raise RuntimeError(f"muc5_fill_probe_table failed with code {rc}")
        return out


def cpp_toolchain_status(*, try_build: bool = True) -> CppToolchainStatus:
    err = None
    version = None
    usable = False
    try:
        if try_build:
            build_probe_kernel()
        if shared_path().exists():
            k = CppProbeKernel(build=False)
            version = k.version
            usable = version >= 1500
    except Exception as exc:  # status reporting should not explode audits
        err = repr(exc)
    return CppToolchainStatus(
        gpp=shutil.which("g++"),
        source_exists=source_path().exists(),
        shared_exists=shared_path().exists(),
        kernel_version=version,
        usable=usable,
        error=err,
    )


def probe_table_cpp(deck_rows: np.ndarray) -> np.ndarray:
    return CppProbeKernel().probe_table(deck_rows)


def write_toolchain_status(path: str | Path) -> None:
    Path(path).write_text(json.dumps(cpp_toolchain_status().as_dict(), indent=2, sort_keys=True))
