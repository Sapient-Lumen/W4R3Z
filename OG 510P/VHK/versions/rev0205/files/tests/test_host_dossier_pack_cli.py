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
                    {"type": "TypeText", "text": "Hello"},
                ],
            },
            sort_keys=False,
        )
    )

    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj",
                "settings": {"desktop_backend": "wayland", "bus_socket": "bus.sock"},
                "bindings": [{"keys": "Mod4+V", "macro": "reply"}],
                "bus_watchers": [{"name": "hotkeys", "event": "hotkey", "dispatch": True}],
            },
            sort_keys=False,
        )
    )
    return project_dir


def test_gen_host_dossier_pack_writes_docs_and_support_scripts(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(app, ["gen-host-dossier-pack", str(project_dir), "--force", "--quiet"])
    assert res.exit_code == 0, res.output

    doc = (project_dir / "docs" / "VHK_HOST_DOSSIER.md").read_text()
    plan = json.loads((project_dir / "docs" / "VHK_HOST_DOSSIER_PLAN.json").read_text())
    script = (project_dir / "scripts" / "vhk_refresh_host_dossier_pack.sh").read_text()

    assert "# VHK host dossier pack for proj" in doc
    assert "## Dossier posture" in doc
    assert "## What gets captured" in doc
    assert "loginctl show-session" in doc
    assert "redact_host_dossier.sh" in doc
    assert "archive_share_dossier.sh" in doc

    story = dict(plan["host_dossier_story"])
    assert story["app_id"] == "io.visualhotkey.proj"
    assert story["command_name"] == "vhk-proj"
    assert story["bundle_kind"] == "project"
    assert story["service_mode"] == "socket-activated-busd"
    assert story["dossier_root"] == "${XDG_STATE_HOME:-$HOME/.local/state}/vhk/dossier/vhk-proj"
    assert story["dossier_json"] == "${XDG_STATE_HOME:-$HOME/.local/state}/vhk/dossier/vhk-proj/VHK_HOST_DOSSIER.json"
    assert story["archive_path"] == "${XDG_STATE_HOME:-$HOME/.local/state}/vhk/dossier/vhk-proj/VHK_HOST_DOSSIER.zip"
    assert story["share_safe_archive"] == "${XDG_STATE_HOME:-$HOME/.local/state}/vhk/dossier/vhk-proj/VHK_HOST_DOSSIER.share.zip"
    assert story["share_safe_root"] == "${XDG_STATE_HOME:-$HOME/.local/state}/vhk/dossier/vhk-proj/share-safe"

    assert "vhk gen-host-rehearsal-pack . --force --quiet" in script
    assert "vhk gen-host-dossier-pack . --force --quiet" in script

    root = project_dir / "build" / "publish" / "proj" / "dossier"
    assert (root / "README.md").exists()
    assert (root / "vhk_host_dossier_handoff.json").exists()
    assert (root / "collect_host_dossier.sh").exists()
    assert (root / "redact_host_dossier.sh").exists()
    assert (root / "archive_host_dossier.sh").exists()
    assert (root / "archive_share_dossier.sh").exists()
    assert (root / "smoke_test_host_dossier.sh").exists()

    collect_script = (root / "collect_host_dossier.sh").read_text()
    redact_script = (root / "redact_host_dossier.sh").read_text()
    archive_script = (root / "archive_host_dossier.sh").read_text()
    share_archive_script = (root / "archive_share_dossier.sh").read_text()
    smoke_script = (root / "smoke_test_host_dossier.sh").read_text()

    assert '"$LAUNCHER_LINK" --home-json > "$APP_HOME_CAPTURE"' in collect_script
    assert '"$LAUNCHER_LINK" --status-json > "$STATUS_CAPTURE"' in collect_script
    assert 'sh "$PUBLISH_ROOT/rehearsal/report_reviewed_lane.sh"' in collect_script
    assert 'loginctl show-session "$XDG_SESSION_ID" -p Id -p Name -p Type -p Class -p State -p Desktop -p Active -p Remote -p Display' in collect_script
    assert 'systemctl --user show -p UnitPath --value > "$UNIT_PATH_CAPTURE"' in collect_script
    assert 'journalctl --user --no-pager -n "$DOSSIER_LINES"' in collect_script
    assert 'VHK_HOST_DOSSIER.json' in collect_script
    assert 'VHK_HOST_DOSSIER.md' in collect_script

    assert 'sh "$SCRIPT_DIR/collect_host_dossier.sh" >/dev/null' in archive_script
    assert 'VHK_HOST_DOSSIER.zip' in archive_script
    assert 'ZipFile(out, ' in archive_script

    assert 'sh "$SCRIPT_DIR/collect_host_dossier.sh" >/dev/null' in redact_script
    assert 'VHK_HOST_DOSSIER.share.json' in redact_script
    assert 'VHK_HOST_DOSSIER_REDACTION.json' in redact_script
    assert 'review_required' in redact_script
    assert '[REDACTED_SECRET]' in redact_script

    assert 'sh "$SCRIPT_DIR/redact_host_dossier.sh" >/dev/null' in share_archive_script
    assert 'VHK_HOST_DOSSIER.share.zip' in share_archive_script
    assert 'ZipFile(out, ' in share_archive_script

    assert 'sh "$PUBLISH_ROOT/rehearsal/install_reviewed_lane.sh"' in smoke_script
    assert 'VHK_SKIP_LOGINCTL=1 sh "$SCRIPT_DIR/collect_host_dossier.sh"' in smoke_script
    assert 'VHK_SKIP_LOGINCTL=1 sh "$SCRIPT_DIR/redact_host_dossier.sh"' in smoke_script
    assert 'VHK_SKIP_LOGINCTL=1 sh "$SCRIPT_DIR/archive_share_dossier.sh"' in smoke_script
    assert 'VHK_SKIP_LOGINCTL=1 sh "$SCRIPT_DIR/archive_host_dossier.sh"' in smoke_script
    assert 'test -f "$SMOKE_ROOT/state/vhk/dossier/vhk-proj/VHK_HOST_DOSSIER.json"' in smoke_script
    assert 'test -f "$SMOKE_ROOT/state/vhk/dossier/vhk-proj/share-safe/VHK_HOST_DOSSIER.share.json"' in smoke_script
    assert 'test -f "$SMOKE_ROOT/state/vhk/dossier/vhk-proj/VHK_HOST_DOSSIER.share.zip"' in smoke_script
    assert 'test -f "$SMOKE_ROOT/state/vhk/dossier/vhk-proj/VHK_HOST_DOSSIER.zip"' in smoke_script


def test_gen_host_dossier_pack_stage_target_keeps_profile_context(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(
        app,
        [
            "gen-host-dossier-pack",
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

    plan = json.loads((project_dir / "docs" / "VHK_HOST_DOSSIER_PLAN.json").read_text())
    story = dict(plan["host_dossier_story"])
    assert story["bundle_kind"] == "release-stage"
    assert story["bundle_profile_id"] == "gnome-wayland"
    assert story["app_id"] == "org.example.vhkdemo"

    root = project_dir / "build" / "publish" / "proj-gnome-wayland" / "dossier"
    manifest = json.loads((root / "vhk_host_dossier_handoff.json").read_text())
    assert manifest["bundle_profile_id"] == "gnome-wayland"
    assert manifest["command_name"] == "vhk-vhkdemo"
    assert manifest["dossier_json"] == "${XDG_STATE_HOME:-$HOME/.local/state}/vhk/dossier/vhk-vhkdemo/VHK_HOST_DOSSIER.json"

    refresh = (root / "refresh_host_dossier_inputs.sh").read_text()
    assert "--bundle-target-profile gnome-wayland" in refresh

    collect_script = (root / "collect_host_dossier.sh").read_text()
    assert 'LAUNCHER_LINK="$VHK_BIN_HOME/vhk-vhkdemo"' in collect_script
