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



def test_gen_distribution_pack_writes_docs_and_handoff(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(app, ["gen-distribution-pack", str(project_dir), "--force", "--quiet"])
    assert res.exit_code == 0, res.output

    doc = (project_dir / "docs" / "VHK_DISTRIBUTION.md").read_text()
    plan = json.loads((project_dir / "docs" / "VHK_DISTRIBUTION_PLAN.json").read_text())
    script = (project_dir / "scripts" / "vhk_refresh_distribution_pack.sh").read_text()

    assert "# VHK distribution pack for proj" in doc
    assert "## Distribution posture" in doc
    assert "## Flatpak finish args" in doc
    assert "## Packaging constraints" in doc

    story = dict(plan["distribution_story"])
    assert story["app_id"] == "io.visualhotkey.proj"
    assert story["runtime"] == "org.freedesktop.Platform"
    assert story["runtime_version"] == "24.08"
    assert "--socket=wayland" in story["finish_args"]
    assert plan["distribution_summary"]["bundle_kind"] == "project"

    assert script.startswith("#!/usr/bin/env sh\n")
    assert "vhk gen-distribution-pack . --force --quiet" in script
    assert "vhk gen-publish-pack . --force --quiet" in script

    handoff_root = project_dir / "build" / "publish" / "proj" / "distribution"
    assert (handoff_root / "README.md").exists()
    assert (handoff_root / "vhk_distribution_handoff.json").exists()
    assert (handoff_root / "refresh_distribution_inputs.sh").exists()
    assert (handoff_root / "appimage" / "build_appimage.sh").exists()
    assert (handoff_root / "flatpak" / "build_flatpak.sh").exists()

    appdir = handoff_root / "appimage" / "AppDir"
    assert (appdir / "AppRun").exists()
    assert (appdir / ".DirIcon").exists()
    assert (appdir / "io.visualhotkey.proj.desktop").exists()
    assert (appdir / "usr" / "share" / "applications" / "io.visualhotkey.proj.desktop").exists()
    assert (appdir / "usr" / "share" / "metainfo" / "io.visualhotkey.proj.metainfo.xml").exists()

    flatpak_manifest = (handoff_root / "flatpak" / "io.visualhotkey.proj.yaml").read_text()
    assert "app-id: io.visualhotkey.proj" in flatpak_manifest
    assert "runtime-version: '24.08'" in flatpak_manifest or 'runtime-version: "24.08"' in flatpak_manifest or "runtime-version: '24.08'" in flatpak_manifest
    assert "--socket=wayland" in flatpak_manifest



def test_gen_distribution_pack_stage_target_updates_bundle_story(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(
        app,
        [
            "gen-distribution-pack",
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

    plan = json.loads((project_dir / "docs" / "VHK_DISTRIBUTION_PLAN.json").read_text())
    story = dict(plan["distribution_story"])
    assert story["app_id"] == "org.example.vhkdemo"
    assert story["bundle_kind"] == "release-stage"
    assert story["bundle_profile_id"] == "gnome-wayland"

    handoff_root = project_dir / "build" / "publish" / "proj-gnome-wayland" / "distribution"
    manifest = json.loads((handoff_root / "vhk_distribution_handoff.json").read_text())
    assert manifest["bundle_kind"] == "release-stage"
    assert manifest["bundle_profile_id"] == "gnome-wayland"

    refresh = (handoff_root / "refresh_distribution_inputs.sh").read_text()
    assert "--bundle-target-profile gnome-wayland" in refresh

    appimage_script = (handoff_root / "appimage" / "build_appimage.sh").read_text()
    assert 'sh "$PUBLISH_ROOT/bundle_release.sh"' in appimage_script
    assert 'proj-gnome-wayland.zip' in appimage_script

    flatpak_manifest = (handoff_root / "flatpak" / "org.example.vhkdemo.yaml").read_text()
    assert "app-id: org.example.vhkdemo" in flatpak_manifest
    assert "proj-gnome-wayland.zip" in flatpak_manifest
