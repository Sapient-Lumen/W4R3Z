from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.project.loader import load_project
from vhk.project.mpv_pack import render_mpv_routes_yaml, write_mpv_pack


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "mpv-proj"
    (project_dir / "macros").mkdir(parents=True)

    (project_dir / "macros" / "pause_mpv.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "pause_mpv",
                "description": "Toggle mpv playback pause",
                "steps": [
                    {"type": "WaitForWindow", "selector": {"class": "mpv", "title": "Player"}, "timeout_ms": 1000},
                    {"type": "Return", "value": "paused"},
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    (project_dir / "macros" / "focus_mpv.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "focus_mpv",
                "description": "Focus the mpv player window",
                "steps": [
                    {"type": "WaitForWindow", "selector": {"class": "mpv", "title": "Player"}, "timeout_ms": 1000},
                    {"type": "Return", "value": "focused"},
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "mpv-proj",
                "settings": {"desktop_backend": "wayland", "event_log": False},
                "bindings": [
                    {"keys": "XF86AudioPlay", "macro": "pause_mpv", "when": {"class": "mpv"}},
                    {"keys": "Mod4+M", "macro": "focus_mpv", "when": {"class": "mpv"}},
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return project_dir



def test_render_mpv_routes_yaml_mentions_input_ipc_and_pause_command(tmp_path: Path) -> None:
    project = load_project(_make_project(tmp_path))
    manifest = write_mpv_pack(project, out_dir=tmp_path / "mpv")
    text = render_mpv_routes_yaml(project, routes=list(manifest.routes), skipped=list(manifest.skipped))
    assert "vhk gen-mpv-pack" in text
    assert "input-ipc-server" in text
    assert "cycle pause" in text
    assert "socat - \"$MPV_SOCKET\"" in text



def test_write_mpv_pack_writes_route_catalog_manifest_and_helper_script(tmp_path: Path) -> None:
    project = load_project(_make_project(tmp_path))
    out_dir = tmp_path / "mpv"
    manifest = write_mpv_pack(project, out_dir=out_dir)
    assert manifest.routes_path.exists()
    assert manifest.commands_path.exists()
    assert manifest.readme_path.exists()
    assert len(manifest.routes) == 1
    assert len(manifest.skipped) == 1
    assert len(manifest.helper_paths) == 1
    helper_text = manifest.helper_paths[0].read_text(encoding="utf-8")
    assert "MPV_SOCKET=${MPV_SOCKET:-${XDG_RUNTIME_DIR:-/tmp}/mpv.socket}" in helper_text
    assert '"command": ["cycle", "pause"]' in helper_text
    payload = json.loads(manifest.commands_path.read_text(encoding="utf-8"))
    assert payload["project"] == "mpv-proj"
    assert payload["route_count"] == 1
    assert payload["routes"][0]["action_id"] == "toggle-pause"
    assert payload["skipped"][0]["reason"] == "no_command_hint"
    readme = manifest.readme_path.read_text(encoding="utf-8")
    assert "JSON IPC" in readme
    assert "focus-sensitive key replay" in readme



def test_gen_mpv_pack_cli_json_writes_pack(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    out_dir = tmp_path / "pack"
    res = runner.invoke(
        app,
        [
            "gen-mpv-pack",
            str(project_dir),
            str(out_dir),
            "--json",
        ],
    )
    assert res.exit_code == 0, res.output
    payload = json.loads(res.output)
    assert payload["project"] == "mpv-proj"
    assert payload["route_count"] == 1
    assert len(payload["helper_paths"]) == 1
    assert (out_dir / "vhk.mpv.routes.yml").exists()
    assert (out_dir / "vhk.mpv.commands.json").exists()
    helper_text = Path(payload["helper_paths"][0]).read_text(encoding="utf-8")
    assert "nc -U" in helper_text
