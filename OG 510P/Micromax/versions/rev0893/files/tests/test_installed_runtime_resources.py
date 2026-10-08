from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tomllib


REPO_ROOT = Path(__file__).resolve().parents[1]


def _installed_help_manifest() -> list[str]:
    rows: list[str] = []
    for raw in (REPO_ROOT / "docs" / "installed-help-manifest.txt").read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        rows.append(line)
    return rows


def _base_env(target: Path, home: Path) -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(target)
    env["HOME"] = str(home)
    env["MICROMAX_INIT"] = str(home / "missing-init.mx")
    env.pop("MICROMAX_DOCS", None)
    env.pop("PYTEST_ADDOPTS", None)
    return env


def _copy_fake_target_install(target: Path) -> None:
    """Create a pip-target-like runtime layout without invoking pip.

    The separate pyproject test below guards the data-files declarations. This
    layout test keeps the runtime fallback regression fast and deterministic in
    constrained cloudtainers while still launching a non-source-checkout Python
    process against the installed-style package/data tree.
    """

    shutil.copytree(REPO_ROOT / "src" / "micromax", target / "micromax")
    shutil.copytree(REPO_ROOT / "src" / "micromax_editor", target / "micromax_editor")

    docs_root = target / "share" / "micromax" / "docs"
    docs_root.mkdir(parents=True)
    for rel in _installed_help_manifest():
        doc = REPO_ROOT / rel
        shutil.copy2(doc, docs_root / doc.name)

    plugins_root = target / "share" / "micromax" / "plugins"
    for name in ("core", "capdemo"):
        shutil.copytree(REPO_ROOT / "plugins" / name, plugins_root / name)


def test_pyproject_declares_bundled_runtime_resource_data_files() -> None:
    data = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    data_files = data["tool"]["setuptools"]["data-files"]

    bundled_docs = data_files["share/micromax/docs"]
    manifest_docs = _installed_help_manifest()
    assert bundled_docs == manifest_docs
    assert "docs/00-vision.md" in bundled_docs
    assert "docs/security-boundaries.md" in bundled_docs
    assert "docs/installed-help-manifest.txt" not in bundled_docs
    assert len(bundled_docs) < len(list((REPO_ROOT / "docs").glob("*.md"))) // 4
    assert "plugins/core/init.mx" in data_files["share/micromax/plugins/core"]
    assert "plugins/core/plugin.json" in data_files["share/micromax/plugins/core"]
    assert "plugins/capdemo/init.mx" in data_files["share/micromax/plugins/capdemo"]
    assert "plugins/capdemo/plugin.json" in data_files["share/micromax/plugins/capdemo"]


def test_target_install_layout_exposes_bundled_docs_and_plugins(tmp_path) -> None:
    """A non-source checkout can still open help topics and find default plugins."""

    target = tmp_path / "target"
    run_dir = tmp_path / "outside-source"
    home = tmp_path / "home"
    target.mkdir()
    run_dir.mkdir()
    home.mkdir()
    _copy_fake_target_install(target)

    env = _base_env(target, home)
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "micromax_editor",
            "--help-doc",
            "00-vision",
            "--dump-screen",
            "8",
            "80",
        ],
        cwd=str(run_dir),
        env=env,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=120,
    )
    data = json.loads(proc.stdout)
    assert data["lines"] == 8
    assert data["cols"] == 80
    assert any("Micromax" in str(row.get("text", "")) for row in data["edit_window"]["rows"])

    proc2 = subprocess.run(
        [
            sys.executable,
            "-m",
            "micromax_editor",
            "--help-doc",
            "docs/00-vision.md",
            "--dump-screen",
            "4",
            "80",
        ],
        cwd=str(run_dir),
        env=env,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=120,
    )
    assert json.loads(proc2.stdout)["lines"] == 4

    security_proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "micromax_editor",
            "--help-doc",
            "security-boundaries",
            "--dump-screen",
            "8",
            "80",
        ],
        cwd=str(run_dir),
        env=env,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=120,
    )
    security_data = json.loads(security_proc.stdout)
    assert any(
        "security boundaries" in str(row.get("text", "")).lower()
        for row in security_data["edit_window"]["rows"]
    )

    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            "from micromax_editor.resource_roots import default_docs_root, default_plugins_root; "
            "d=default_docs_root(); p=default_plugins_root(); "
            "print((d/'00-vision.md').is_file()); "
            "print((d/'security-boundaries.md').is_file()); "
            "print((p/'core'/'init.mx').is_file()); "
            "print((p/'capdemo'/'plugin.json').is_file())",
        ],
        cwd=str(run_dir),
        env=env,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=120,
    )
    assert probe.stdout.splitlines() == ["True", "True", "True", "True"]
