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

    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj",
                "settings": {"desktop_backend": "wayland"},
                "bindings": [{"keys": "Mod4+V", "macro": "reply"}],
            },
            sort_keys=False,
        )
    )
    return project_dir



def test_gen_runtime_embed_pack_writes_docs_handoff_and_hooks(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(app, ["gen-runtime-embed-pack", str(project_dir), "--force", "--quiet"])
    assert res.exit_code == 0, res.output

    doc = (project_dir / "docs" / "VHK_RUNTIME_EMBED.md").read_text()
    plan = json.loads((project_dir / "docs" / "VHK_RUNTIME_EMBED_PLAN.json").read_text())
    script = (project_dir / "scripts" / "vhk_refresh_runtime_embed_pack.sh").read_text()

    assert "# VHK runtime embed pack for proj" in doc
    assert "## Embed posture" in doc
    assert "exact path" in doc.lower() or "exact-target" in doc.lower()

    story = dict(plan["embed_story"])
    assert story["package_name"] == "vhk"
    assert story["bundle_kind"] == "project"
    assert story["targets"]["native"] == "build/publish/proj/runtime/embed/native-runtime"

    assert "vhk gen-runtime-embed-pack . --force --quiet" in script
    assert "vhk gen-runtime-pack . --force --quiet" in script

    embed_root = project_dir / "build" / "publish" / "proj" / "runtime" / "embed"
    assert (embed_root / "README.md").exists()
    assert (embed_root / "vhk_runtime_embed_handoff.json").exists()
    assert (embed_root / "bootstrap_runtime_at_target.sh").exists()
    assert (embed_root / "embed_native_runtime.sh").exists()
    assert (embed_root / "embed_appimage_runtime.sh").exists()
    assert (embed_root / "embed_flatpak_runtime.sh").exists()
    assert (embed_root / "smoke_test_embedded_runtime.sh").exists()

    bootstrap = (embed_root / "bootstrap_runtime_at_target.sh").read_text()
    assert '"$PYTHON_CMD" -m venv "$TARGET_DIR"' in bootstrap
    assert '"$TARGET_DIR/bin/python" -m pip install --no-index --find-links "$WHEELHOUSE_DIR" vhk' in bootstrap

    smoke = (embed_root / "smoke_test_embedded_runtime.sh").read_text()
    assert 'MODE="${1:-native}"' in smoke
    assert 'exec "$TARGET_DIR/bin/vhk" inspect-bundle "$BUNDLE_PATH"' in smoke

    appimage_script = (project_dir / "build" / "publish" / "proj" / "distribution" / "appimage" / "build_appimage.sh").read_text()
    assert 'VHK_EMBED_RUNTIME:-0' in appimage_script
    assert 'embed_appimage_runtime.sh' in appimage_script

    flatpak_script = (project_dir / "build" / "publish" / "proj" / "distribution" / "flatpak" / "build_flatpak.sh").read_text()
    assert 'VHK_EMBED_RUNTIME:-0' in flatpak_script
    assert 'embed_flatpak_runtime.sh' in flatpak_script



def test_gen_runtime_embed_pack_stage_target_keeps_profile_context(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(
        app,
        [
            "gen-runtime-embed-pack",
            str(project_dir),
            "--bundle-target-profile",
            "gnome-wayland",
            "--app-id",
            "org.example.vhkdemo",
            "--python-cmd",
            "python3.12",
            "--force",
            "--quiet",
        ],
    )
    assert res.exit_code == 0, res.output

    plan = json.loads((project_dir / "docs" / "VHK_RUNTIME_EMBED_PLAN.json").read_text())
    story = dict(plan["embed_story"])
    assert story["bundle_kind"] == "release-stage"
    assert story["bundle_profile_id"] == "gnome-wayland"
    assert story["app_id"] == "org.example.vhkdemo"
    assert story["python_cmd"] == "python3.12"

    embed_root = project_dir / "build" / "publish" / "proj-gnome-wayland" / "runtime" / "embed"
    manifest = json.loads((embed_root / "vhk_runtime_embed_handoff.json").read_text())
    assert manifest["bundle_profile_id"] == "gnome-wayland"

    refresh = (embed_root / "refresh_runtime_embed_inputs.sh").read_text()
    assert "--bundle-target-profile gnome-wayland" in refresh

    appimage_embed = (embed_root / "embed_appimage_runtime.sh").read_text()
    assert 'distribution/appimage/AppDir/usr/lib/vhk-runtime' in appimage_embed

    flatpak_embed = (embed_root / "embed_flatpak_runtime.sh").read_text()
    assert 'distribution/flatpak/files/lib/vhk-runtime' in flatpak_embed
