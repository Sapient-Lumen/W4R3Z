from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "proj"
    (project_dir / "macros").mkdir(parents=True)

    (project_dir / "macros" / "reply.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "reply",
                "steps": [
                    {"type": "PromptForm", "title": "Reply", "fields": [{"name": "name", "label": "Name"}]},
                    {"type": "TypeText", "text": "Hello ${reply.name}"},
                ],
            },
            sort_keys=False,
        )
    )

    (project_dir / "macros" / "vision.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "vision",
                "steps": [
                    {"type": "WaitForImage", "needle_path": "assets/button.png", "timeout_ms": 5000},
                    {"type": "MouseClickAt", "x": 100, "y": 200},
                ],
            },
            sort_keys=False,
        )
    )

    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj",
                "settings": {"desktop_backend": "wayland"},
                "bindings": [{"keys": "Mod4+V", "macro": "vision"}],
                "hotstrings": [{"trigger": ":reply", "macro": "reply"}],
            },
            sort_keys=False,
        )
    )
    return project_dir



def test_gen_runtime_pack_writes_docs_and_handoff(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(app, ["gen-runtime-pack", str(project_dir), "--force", "--quiet"])
    assert res.exit_code == 0, res.output

    doc = (project_dir / "docs" / "VHK_RUNTIME.md").read_text()
    plan = json.loads((project_dir / "docs" / "VHK_RUNTIME_PLAN.json").read_text())
    script = (project_dir / "scripts" / "vhk_refresh_runtime_pack.sh").read_text()

    assert "# VHK runtime pack for proj" in doc
    assert "## Runtime posture" in doc
    assert "## Runtime dependencies" in doc
    assert "opencv-python>=4.7" in doc

    story = dict(plan["runtime_story"])
    assert story["package_name"] == "vhk"
    assert story["package_version"]
    assert story["bundle_kind"] == "project"
    assert story["dependency_count"] >= 3
    assert "PyYAML>=6.0" in story["dependencies"]

    assert script.startswith("#!/usr/bin/env sh\n")
    assert "vhk gen-runtime-pack . --force --quiet" in script
    assert "vhk gen-distribution-pack . --force --quiet" in script

    runtime_root = project_dir / "build" / "publish" / "proj" / "runtime"
    assert (runtime_root / "README.md").exists()
    assert (runtime_root / "vhk_runtime_handoff.json").exists()
    assert (runtime_root / "refresh_runtime_inputs.sh").exists()
    assert (runtime_root / "requirements.runtime.txt").read_text().strip()
    assert (runtime_root / "wheelhouse" / "README.md").exists()

    wheelhouse_script = (runtime_root / "build_wheelhouse.sh").read_text()
    assert 'python -m pip wheel --wheel-dir "$WHEELHOUSE_DIR" .' in wheelhouse_script
    assert 'python -m pip wheel --wheel-dir "$WHEELHOUSE_DIR" -r "$REQ_FILE"' in wheelhouse_script

    smoke_script = (runtime_root / "smoke_test_offline_install.sh").read_text()
    assert 'python -m venv "$VENV_DIR"' in smoke_script
    assert '"$VENV_DIR/bin/python" -m pip install --no-index --find-links "$WHEELHOUSE_DIR" vhk' in smoke_script

    flatpak_script = (runtime_root / "emit_flatpak_python_modules.sh").read_text()
    assert "flatpak-pip-generator --requirements-file=\"$REQ_FILE\"" in flatpak_script

    appimage_launcher = (project_dir / "build" / "publish" / "proj" / "distribution" / "appimage" / "AppDir" / "usr" / "bin" / "vhk-launch").read_text()
    assert 'EMBEDDED_VHK="$APPDIR/usr/lib/vhk-runtime/bin/vhk"' in appimage_launcher



def test_gen_runtime_pack_stage_target_updates_bundle_story(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(
        app,
        [
            "gen-runtime-pack",
            str(project_dir),
            "--bundle-target-profile",
            "gnome-wayland",
            "--app-id",
            "org.example.vhkdemo",
            "--force",
            "--quiet",
        ],
    )
    assert res.exit_code == 0, res.output

    plan = json.loads((project_dir / "docs" / "VHK_RUNTIME_PLAN.json").read_text())
    story = dict(plan["runtime_story"])
    assert story["app_id"] == "org.example.vhkdemo"
    assert story["bundle_kind"] == "release-stage"
    assert story["bundle_profile_id"] == "gnome-wayland"

    runtime_root = project_dir / "build" / "publish" / "proj-gnome-wayland" / "runtime"
    manifest = json.loads((runtime_root / "vhk_runtime_handoff.json").read_text())
    assert manifest["bundle_kind"] == "release-stage"
    assert manifest["bundle_profile_id"] == "gnome-wayland"

    refresh = (runtime_root / "refresh_runtime_inputs.sh").read_text()
    assert "--bundle-target-profile gnome-wayland" in refresh

    run_bundle = (runtime_root / "run_bundle_with_runtime.sh").read_text()
    assert "proj-gnome-wayland.zip" in run_bundle

    dist_launcher = (project_dir / "build" / "publish" / "proj-gnome-wayland" / "distribution" / "flatpak" / "files" / "bin" / "vhk-launch").read_text()
    assert 'EMBEDDED_VHK="/app/lib/vhk-runtime/bin/vhk"' in dist_launcher
