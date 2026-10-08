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


def _run_installed_editor_json(
    args: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    output_path: Path,
) -> dict[str, object]:
    """Run an installed-style editor dump through a file-backed stdout.

    Help-screen JSON can exceed small pipe buffers after docs-cue metadata grows.
    Use a temp file so this runtime-layout test measures installability instead
    of subprocess pipe scheduling.
    """

    stderr_path = output_path.with_suffix(output_path.suffix + ".stderr")
    with output_path.open("w", encoding="utf-8") as out, stderr_path.open("w", encoding="utf-8") as err:
        proc = subprocess.run(
            [sys.executable, "-m", "micromax_editor", *args],
            cwd=str(cwd),
            env=env,
            check=False,
            stdout=out,
            stderr=err,
            text=True,
            timeout=120,
        )
    assert proc.returncode == 0, stderr_path.read_text(encoding="utf-8") or output_path.read_text(encoding="utf-8")
    return json.loads(output_path.read_text(encoding="utf-8"))


def test_pyproject_declares_bundled_runtime_resource_data_files() -> None:
    data = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    data_files = data["tool"]["setuptools"]["data-files"]

    assert data["project"]["license"] == "MIT"
    assert data["project"]["license-files"] == ["LICENSE"]
    assert "share/micromax" not in data_files
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
    """A non-source checkout can open generated help and find bundled resources.

    This intentionally launches the editor once. Repeated subprocess launches from
    the same Python test parent have exposed cloudtainer scheduler stalls that are
    unrelated to the install-layout invariant. The resource probe below still
    verifies the other curated docs and plugins are present in the installed tree.
    """

    target = tmp_path / "target"
    run_dir = tmp_path / "outside-source"
    home = tmp_path / "home"
    target.mkdir()
    run_dir.mkdir()
    home.mkdir()
    _copy_fake_target_install(target)

    env = _base_env(target, home)
    effects_data = _run_installed_editor_json(
        ["--help-doc", "effect-resource-contract", "--dump-screen", "40", "120"],
        cwd=run_dir,
        env=env,
        output_path=tmp_path / "effect-contract.json",
    )
    effects_text = "\n".join(str(row.get("text", "")) for row in effects_data["rows"])
    assert effects_data["schema"] == "micromax.screen.v1"
    assert effects_data["size"] == {"lines": 40, "cols": 120}
    assert "Effect/resource contract" in effects_text
    assert "ed.fs-read" in effects_text

    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            "from micromax_editor.resource_roots import default_docs_root, default_plugins_root; "
            "d=default_docs_root(); p=default_plugins_root(); "
            "print((d/'00-vision.md').is_file()); "
            "print((d/'security-boundaries.md').is_file()); "
            "print((d/'33-effect-resource-contract.md').is_file()); "
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
    assert probe.stdout.splitlines() == ["True", "True", "True", "True", "True"]
