from __future__ import annotations

import json
import os
import subprocess
import sys
import tomllib
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
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_date_epoch = int(pyproject["tool"]["micromax"]["release"]["source_date_epoch"])
    build_env = dict(os.environ)
    build_env.update(
        {
            "SOURCE_DATE_EPOCH": str(source_date_epoch),
            "PYTHONHASHSEED": "0",
            "PYTHONDONTWRITEBYTECODE": "1",
            "TZ": "UTC",
            "PIP_CONFIG_FILE": os.devnull,
        }
    )
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
        env=build_env,
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
        metadata_name = next(name for name in names if name.endswith(".dist-info/METADATA"))
        metadata = zf.read(metadata_name).decode("utf-8")
        timestamps = {info.date_time for info in zf.infolist()}
    assert "micromax/stdlib/core.mx" in names
    assert "micromax = micromax.repl:main" in entry_points
    assert "micromax-editor = micromax_editor.__main__:main" in entry_points
    assert "micromax-screen = micromax_editor.screen_consumer:main" in entry_points
    assert "micromax_editor/screen_budget.py" in names
    assert "micromax_editor/screen_consumer.py" in names
    assert "micromax_editor/screen_contract.py" in names
    assert "micromax_editor/schemas/micromax-screen-v1.schema.json" in names
    assert any(name.endswith(".dist-info/licenses/LICENSE") for name in names)
    assert "License-Expression: MIT" in metadata
    assert "License-File: LICENSE" in metadata
    assert len(timestamps) == 1
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
from micromax_editor import Editor
from micromax_editor.screen_consumer import screen_contract_summary
from micromax_editor.screen_contract import load_screen_contract_schema
vm = VM(strict_stdlib=True)
editor = Editor()
editor.new_buffer("*scratch*", "")
summary = screen_contract_summary(editor.screen_contract(4, 16))
schema = load_screen_contract_schema()
print(json.dumps({
    "stdlib": vm.stdlib_health(),
    "has_finally": vm.find_word("finally") is not None,
    "has_2drop": vm.find_word("2drop") is not None,
    "diagnostics": vm.startup_diagnostics,
    "screen_schema": schema["properties"]["schema"]["const"],
    "screen_rows": summary["rows"],
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
    assert payload["screen_schema"] == "micromax.screen.v1"
    assert payload["screen_rows"] == 4
