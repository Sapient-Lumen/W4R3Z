from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.project.loader import load_project
from vhk.project.playerctl_pack import render_playerctl_routes_yaml, write_playerctl_pack


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "mpris-proj"
    (project_dir / "macros").mkdir(parents=True)

    (project_dir / "macros" / "wait_for_track.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "wait_for_track",
                "description": "React to the next media-player track change",
                "steps": [
                    {
                        "type": "WaitForDbusSignal",
                        "bus": "session",
                        "sender": "org.mpris.MediaPlayer2.spotify",
                        "path": "/org/mpris/MediaPlayer2",
                        "interface": "org.freedesktop.DBus.Properties",
                        "member": "PropertiesChanged",
                        "timeout_ms": 2000,
                    },
                    {"type": "Return", "value": "mpris"},
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "mpris-proj",
                "settings": {"desktop_backend": "wayland", "event_log": False},
                "bindings": [{"keys": "XF86AudioPlay", "macro": "wait_for_track"}],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return project_dir



def test_render_playerctl_routes_yaml_mentions_playerctl_follow_and_vhk_run(tmp_path: Path) -> None:
    project = load_project(_make_project(tmp_path))
    manifest = write_playerctl_pack(project, out_dir=tmp_path / "playerctl")
    text = render_playerctl_routes_yaml(project, routes=list(manifest.routes))
    assert "vhk gen-playerctl-pack" in text
    assert "playerctl --follow --player spotify metadata" in text
    assert "vhk run" in text
    assert "PropertiesChanged" in text



def test_write_playerctl_pack_writes_route_catalog_manifest_and_helper_script(tmp_path: Path) -> None:
    project = load_project(_make_project(tmp_path))
    out_dir = tmp_path / "playerctl"
    manifest = write_playerctl_pack(project, out_dir=out_dir, command="python -m vhk.cli")
    assert manifest.routes_path.exists()
    assert manifest.commands_path.exists()
    assert manifest.readme_path.exists()
    assert len(manifest.helper_paths) == 1
    assert manifest.helper_paths[0].exists()
    helper_text = manifest.helper_paths[0].read_text(encoding="utf-8")
    assert 'VHK_RUN_MODE=${VHK_RUN_MODE:-print}' in helper_text
    assert 'playerctl' in helper_text
    assert 'python -m vhk.cli run' in helper_text
    payload = json.loads(manifest.commands_path.read_text(encoding="utf-8"))
    assert payload["project"] == "mpris-proj"
    assert payload["route_count"] == 1
    assert payload["routes"][0]["player_selector"] == "spotify"
    readme = manifest.readme_path.read_text(encoding="utf-8")
    assert "playerctld" in readme
    assert "MPRIS" in readme



def test_gen_playerctl_pack_cli_json_writes_pack(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    out_dir = tmp_path / "pack"
    res = runner.invoke(
        app,
        [
            "gen-playerctl-pack",
            str(project_dir),
            str(out_dir),
            "--command",
            "python -m vhk.cli",
            "--json",
        ],
    )
    assert res.exit_code == 0, res.output
    payload = json.loads(res.output)
    assert payload["project"] == "mpris-proj"
    assert payload["route_count"] == 1
    assert len(payload["helper_paths"]) == 1
    assert (out_dir / "vhk.playerctl.routes.yml").exists()
    assert (out_dir / "vhk.playerctl.commands.json").exists()
    helper_text = Path(payload["helper_paths"][0]).read_text(encoding="utf-8")
    assert 'PLAYER=${PLAYER:-spotify}' in helper_text
    assert 'VHK_RUN_MODE=${VHK_RUN_MODE:-print}' in helper_text
