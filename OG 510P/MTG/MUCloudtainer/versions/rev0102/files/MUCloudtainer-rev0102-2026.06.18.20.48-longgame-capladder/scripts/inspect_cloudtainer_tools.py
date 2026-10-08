#!/usr/bin/env python3
from __future__ import annotations

import importlib.metadata as md
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

PACKAGE_NAMES = [
    "numpy",
    "scipy",
    "pandas",
    "sklearn",
    "torch",
    "jax",
    "numba",
    "Cython",
    "xgboost",
    "lightgbm",
    "gymnasium",
    "pettingzoo",
    "stable_baselines3",
    "sb3_contrib",
]

DIST_NAME = {
    "sklearn": "scikit-learn",
}


def package_info(import_name: str) -> dict[str, object]:
    dist = DIST_NAME.get(import_name, import_name)
    out: dict[str, object] = {"import_name": import_name, "installed": False}
    try:
        out["version"] = md.version(dist)
        out["installed"] = True
    except md.PackageNotFoundError:
        out["version"] = None
    return out


def read_meminfo() -> dict[str, int]:
    path = Path("/proc/meminfo")
    if not path.exists():
        return {}
    vals: dict[str, int] = {}
    for line in path.read_text().splitlines():
        key, _, rest = line.partition(":")
        parts = rest.strip().split()
        if parts and parts[0].isdigit():
            vals[key] = int(parts[0])
    return vals


def command_version(cmd: str, args: list[str]) -> dict[str, object]:
    exe = shutil.which(cmd)
    out: dict[str, object] = {"command": cmd, "path": exe, "available": bool(exe)}
    if not exe:
        return out
    try:
        cp = subprocess.run([exe, *args], capture_output=True, text=True, timeout=5)
        out["returncode"] = cp.returncode
        out["stdout"] = cp.stdout.strip().splitlines()[:3]
        out["stderr"] = cp.stderr.strip().splitlines()[:3]
    except Exception as exc:  # pragma: no cover - diagnostic only
        out["error"] = repr(exc)
    return out


def main() -> None:
    meminfo = read_meminfo()
    payload = {
        "purpose": "Document the cloudtainer-bound office for future archive openers.",
        "python": {
            "version": sys.version,
            "executable": sys.executable,
        },
        "platform": {
            "machine": platform.machine(),
            "platform": platform.platform(),
            "processor": platform.processor(),
            "cpu_count": os.cpu_count(),
        },
        "memory": {
            "MemTotal_kB": meminfo.get("MemTotal"),
            "MemAvailable_kB": meminfo.get("MemAvailable"),
        },
        "commands": {
            "node": command_version("node", ["--version"]),
            "gcc": command_version("gcc", ["--version"]),
            "g++": command_version("g++", ["--version"]),
        },
        "packages": {name: package_info(name) for name in PACKAGE_NAMES},
        "policy_note": "Prefer pure Python + NumPy/PyTorch/scikit-learn-style tools. Use Numba/Cython only after a measured hotspot justifies extra build complexity; do not assume future cloudtainers can compile extension modules identically.",
    }
    out = Path("data/rev0009_cloudtainer_tools.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True))
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
