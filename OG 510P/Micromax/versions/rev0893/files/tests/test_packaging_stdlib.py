from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _installed_help_manifest() -> list[str]:
    rows: list[str] = []
    for raw in (ROOT / "docs" / "installed-help-manifest.txt").read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            rows.append(line)
    return rows


def test_built_wheel_includes_stdlib_resource_and_loads_vm(tmp_path: Path) -> None:
    wheelhouse = tmp_path / "wheelhouse"
    wheelhouse.mkdir()
    build = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            "--no-deps",
            "--no-build-isolation",
            "--wheel-dir",
            str(wheelhouse),
            str(ROOT),
        ],
        cwd=str(tmp_path),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    assert build.returncode == 0, build.stdout

    wheels = sorted(wheelhouse.glob("micromax-*.whl"))
    assert len(wheels) == 1
    wheel = wheels[0]
    with zipfile.ZipFile(wheel) as zf:
        names = set(zf.namelist())
        entry_points_name = next((name for name in names if name.endswith(".dist-info/entry_points.txt")), "")
        entry_points = zf.read(entry_points_name).decode("utf-8") if entry_points_name else ""
    assert "micromax/stdlib/core.mx" in names
    assert "micromax = micromax.repl:main" in entry_points
    assert "micromax-editor = micromax_editor.__main__:main" in entry_points
    wheel_docs = sorted(name for name in names if "/share/micromax/docs/" in name and name.endswith(".md"))
    manifest_docs = _installed_help_manifest()
    assert len(wheel_docs) == len(manifest_docs)
    assert any(name.endswith("/share/micromax/docs/00-vision.md") for name in wheel_docs)
    assert not any("cloudtainer" in name for name in wheel_docs)

    target = tmp_path / "installed"
    install = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-deps",
            "--target",
            str(target),
            str(wheel),
        ],
        cwd=str(tmp_path),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    assert install.returncode == 0, install.stdout

    probe = """
import json
import sys
sys.path.insert(0, sys.argv[1])
from micromax import VM
vm = VM(strict_stdlib=True)
print(json.dumps({
    "stdlib": vm.stdlib_health(),
    "has_finally": vm.find_word("finally") is not None,
    "has_2drop": vm.find_word("2drop") is not None,
    "diagnostics": vm.startup_diagnostics,
}, sort_keys=True))
"""
    check = subprocess.run(
        [sys.executable, "-c", probe, str(target)],
        cwd=str(tmp_path),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    assert check.returncode == 0, check.stdout
    payload = json.loads(check.stdout)
    assert payload["stdlib"]["state"] == "loaded"
    assert payload["has_finally"] is True
    assert payload["has_2drop"] is True
    assert payload["diagnostics"] == []
