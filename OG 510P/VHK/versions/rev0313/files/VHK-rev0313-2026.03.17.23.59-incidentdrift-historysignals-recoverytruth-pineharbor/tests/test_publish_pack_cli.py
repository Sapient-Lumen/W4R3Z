from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.project.bundle import bundle_project, inspect_bundle


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "proj"
    (project_dir / "macros").mkdir(parents=True)

    (project_dir / "macros" / "reply.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "reply",
                "presets": [{"name": "support", "vars": {"team": "support"}}],
                "steps": [
                    {
                        "type": "PromptForm",
                        "title": "Reply",
                        "fields": [{"name": "name", "label": "Name"}],
                    },
                    {"type": "TypeText", "text": "Hello ${reply.name}"},
                    {"type": "Return", "value": "ok"},
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
                "bus_watchers": [{"name": "refresh", "event": "proj.refresh", "macro": "vision"}],
            },
            sort_keys=False,
        )
    )
    return project_dir



def test_gen_publish_pack_writes_expected_artifacts(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = project_dir / "docs"
    scripts_dir = project_dir / "scripts"

    for cmd in ["gen-operator-pack", "gen-verification-pack", "gen-portability-pack", "gen-claim-pack"]:
        res = runner.invoke(app, [cmd, str(project_dir), "--no-session-check", "--force", "--quiet"])
        assert res.exit_code == 0, res.output

    res = runner.invoke(app, ["gen-publish-pack", str(project_dir), "--no-session-check", "--quiet"])
    assert res.exit_code == 0, res.output

    support = (docs_dir / "VHK_PUBLIC_SUPPORT.md").read_text()
    quickstart = (docs_dir / "VHK_INSTALL_QUICKSTART.md").read_text()
    plan = json.loads((docs_dir / "VHK_PUBLISH_PLAN.json").read_text())
    script = (scripts_dir / "vhk_refresh_publish_pack.sh").read_text()

    assert "# VHK public support for proj" in support
    assert "## Release posture" in support
    assert "## Public support matrix" in support
    assert "## Language guardrails" in support

    assert "# VHK install quickstart for proj" in quickstart
    assert "## Recommended rollout order" in quickstart
    assert "## Install surfaces" in quickstart
    assert "## Bundle review commands" in quickstart

    assert plan["project"]["name"] == "proj"
    assert plan["public_support_matrix"]
    assert plan["language_guardrails"]
    assert plan["publish_commands"]
    assert plan["publish_summary"]["target_count"] >= 1

    assert script.startswith("#!/usr/bin/env sh\n")
    assert "vhk gen-publish-pack . --out-dir" in script
    assert 'BUNDLE_NAME="${BUNDLE_NAME:-proj.zip}"' in script
    assert 'vhk bundle . "$DIST_DIR/$BUNDLE_NAME" --deterministic' in script



def test_gen_publish_pack_can_select_outputs(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = tmp_path / "publish-docs"
    scripts_dir = tmp_path / "publish-scripts"

    res = runner.invoke(
        app,
        [
            "gen-publish-pack",
            str(project_dir),
            "--out-dir",
            str(docs_dir),
            "--script-dir",
            str(scripts_dir),
            "--no-session-check",
            "--no-support-doc",
            "--no-script",
            "--force",
            "--quiet",
        ],
    )
    assert res.exit_code == 0, res.output

    assert not (docs_dir / "VHK_PUBLIC_SUPPORT.md").exists()
    assert (docs_dir / "VHK_INSTALL_QUICKSTART.md").exists()
    assert (docs_dir / "VHK_PUBLISH_PLAN.json").exists()
    assert not (scripts_dir / "vhk_refresh_publish_pack.sh").exists()


def test_gen_publish_pack_can_target_release_stage_bundle(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = project_dir / "docs"
    scripts_dir = project_dir / "scripts"

    for cmd in ["gen-operator-pack", "gen-verification-pack", "gen-portability-pack", "gen-claim-pack"]:
        res = runner.invoke(app, [cmd, str(project_dir), "--no-session-check", "--force", "--quiet"])
        assert res.exit_code == 0, res.output

    res = runner.invoke(
        app,
        [
            "gen-publish-pack",
            str(project_dir),
            "--bundle-target-profile",
            "gnome-wayland",
            "--no-session-check",
            "--quiet",
        ],
    )
    assert res.exit_code == 0, res.output

    support = (docs_dir / "VHK_PUBLIC_SUPPORT.md").read_text()
    quickstart = (docs_dir / "VHK_INSTALL_QUICKSTART.md").read_text()
    plan = json.loads((docs_dir / "VHK_PUBLISH_PLAN.json").read_text())
    script = (scripts_dir / "vhk_refresh_publish_pack.sh").read_text()

    assert "Bundle kind: `release-stage`" in support
    assert "Bundle target profile: `gnome-wayland`" in support
    assert "Bundle shape: `release-stage`" in quickstart
    assert "Target profile: `gnome-wayland`" in quickstart

    story = dict(plan["bundle_release_story"])
    assert story["bundle_kind"] == "release-stage"
    assert story["bundle_profile_id"] == "gnome-wayland"
    assert story["bundle_name_hint"] == "proj-gnome-wayland.zip"
    assert story["bundle_command"] == "vhk bundle-stage . ./dist/proj-gnome-wayland.zip --target-profile gnome-wayland --deterministic"
    assert plan["publish_summary"]["bundle_kind"] == "release-stage"
    assert "vhk gen-release-stage-pack . --target-profile gnome-wayland --force" in plan["publish_commands"]
    assert "vhk bundle-stage . ./dist/proj-gnome-wayland.zip --target-profile gnome-wayland --deterministic" in plan["publish_commands"]

    assert 'BUNDLE_NAME="${BUNDLE_NAME:-proj-gnome-wayland.zip}"' in script
    assert 'VHK_STAGE_PROFILE="${VHK_STAGE_PROFILE:-gnome-wayland}"' in script
    assert 'vhk gen-publish-pack . --out-dir ' in script
    assert '--bundle-target-profile gnome-wayland' in script
    assert 'vhk gen-release-stage-pack . --target-profile "$VHK_STAGE_PROFILE" --force --quiet' in script
    assert 'vhk bundle-stage . "$DIST_DIR/$BUNDLE_NAME" --target-profile "$VHK_STAGE_PROFILE" --deterministic' in script



def test_bundle_manifest_reports_publish_docs_when_present(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    for cmd in ["gen-operator-pack", "gen-verification-pack", "gen-portability-pack", "gen-claim-pack", "gen-publish-pack"]:
        res = runner.invoke(app, [cmd, str(project_dir), "--no-session-check", "--force", "--quiet"])
        assert res.exit_code == 0, res.output

    out = tmp_path / "proj.zip"
    bundle_project(project_dir, out)

    payload = inspect_bundle(out)
    support = payload["support"]
    assert support["publish_pack_present"] is True
    assert "docs/VHK_PUBLIC_SUPPORT.md" in support["publish_docs_present"]
    assert "docs/VHK_INSTALL_QUICKSTART.md" in support["publish_docs_present"]

    res = runner.invoke(app, ["inspect-bundle", str(out), "--json"])
    assert res.exit_code == 0, res.output
    cli_payload = json.loads(res.output)
    assert cli_payload["support"]["publish_pack_present"] is True


def test_gen_publish_pack_materializes_handoff_tree(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(app, ["gen-publish-pack", str(project_dir), "--no-session-check", "--force", "--quiet"])
    assert res.exit_code == 0, res.output

    handoff_root = project_dir / "build" / "publish" / "proj"
    assert (handoff_root / "README.md").exists()
    assert (handoff_root / "vhk_publish_handoff.json").exists()
    assert (handoff_root / "refresh_publish_inputs.sh").exists()
    assert (handoff_root / "bundle_release.sh").exists()
    assert (handoff_root / "payload" / "docs" / "VHK_PUBLIC_SUPPORT.md").exists()
    assert (handoff_root / "payload" / "docs" / "VHK_INSTALL_QUICKSTART.md").exists()

    manifest = json.loads((handoff_root / "vhk_publish_handoff.json").read_text())
    assert manifest["bundle_kind"] == "project"
    assert manifest["copied_docs"] == [
        "docs/VHK_PUBLIC_SUPPORT.md",
        "docs/VHK_INSTALL_QUICKSTART.md",
        "docs/VHK_PUBLISH_PLAN.json",
    ]

    bundle_script = (handoff_root / "bundle_release.sh").read_text()
    assert 'BUNDLE_NAME="${BUNDLE_NAME:-proj.zip}"' in bundle_script
    assert 'vhk bundle . "$DIST_DIR/$BUNDLE_NAME" --deterministic' in bundle_script


def test_gen_publish_pack_stage_handoff_includes_stage_refs(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(
        app,
        [
            "gen-publish-pack",
            str(project_dir),
            "--bundle-target-profile",
            "gnome-wayland",
            "--no-session-check",
            "--force",
            "--quiet",
        ],
    )
    assert res.exit_code == 0, res.output

    handoff_root = project_dir / "build" / "publish" / "proj-gnome-wayland"
    manifest = json.loads((handoff_root / "vhk_publish_handoff.json").read_text())
    assert manifest["bundle_kind"] == "release-stage"
    assert manifest["bundle_profile_id"] == "gnome-wayland"
    assert "build/release-stage/gnome-wayland/README.md" in manifest["copied_stage_refs"]
    assert "build/release-stage/gnome-wayland/vhk_release_stage.json" in manifest["copied_stage_refs"]
    assert (handoff_root / "payload" / "release-stage" / "README.md").exists()
    assert (handoff_root / "payload" / "release-stage" / "vhk_release_stage.json").exists()

    bundle_script = (handoff_root / "bundle_release.sh").read_text()
    assert 'VHK_STAGE_PROFILE="${VHK_STAGE_PROFILE:-gnome-wayland}"' in bundle_script
    assert 'vhk bundle-stage . "$DIST_DIR/$BUNDLE_NAME" --target-profile "$VHK_STAGE_PROFILE" --deterministic' in bundle_script
