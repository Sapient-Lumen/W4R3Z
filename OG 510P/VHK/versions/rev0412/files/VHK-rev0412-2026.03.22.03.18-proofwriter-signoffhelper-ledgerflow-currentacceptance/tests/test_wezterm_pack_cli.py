from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.project.loader import load_project
from vhk.project.wezterm_pack import render_wezterm_routes_yaml, write_wezterm_pack


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "wezterm-proj"
    (project_dir / "macros").mkdir(parents=True)

    (project_dir / "macros" / "send_to_wezterm.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "send_to_wezterm",
                "description": "Send text to a WezTerm work pane",
                "steps": [
                    {"type": "WaitForWindow", "selector": {"class": "org.wezfurlong.wezterm", "title": "Work Pane"}, "timeout_ms": 1000},
                    {"type": "TypeText", "text": "cargo test --quiet"},
                    {"type": "Return", "value": "ok"},
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    (project_dir / "macros" / "wezterm_without_title.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "wezterm_without_title",
                "description": "Targets WezTerm but needs a better pane hint",
                "steps": [
                    {"type": "WaitForWindow", "selector": {"class": "wezterm"}, "timeout_ms": 1000},
                    {"type": "TypeText", "text": "echo missing-title"},
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "wezterm-proj",
                "settings": {"desktop_backend": "wayland", "event_log": False},
                "bindings": [
                    {"keys": "Mod4+Return", "macro": "send_to_wezterm", "when": {"class": "org.wezfurlong.wezterm", "title": "Work Pane"}},
                    {"keys": "Mod4+W", "macro": "wezterm_without_title", "when": {"class": "wezterm"}},
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return project_dir


def test_render_wezterm_routes_yaml_mentions_send_and_capture_commands(tmp_path: Path) -> None:
    project = load_project(_make_project(tmp_path))
    manifest = write_wezterm_pack(project, out_dir=tmp_path / "wezterm")
    text = render_wezterm_routes_yaml(project, routes=list(manifest.routes), skipped=list(manifest.skipped))
    assert "vhk gen-wezterm-pack" in text
    assert "wezterm cli send-text --pane-id <pane-id> 'cargo test --quiet'" in text
    assert "wezterm cli get-text --pane-id <pane-id>" in text
    assert "missing_pane_hint" in text


def test_write_wezterm_pack_writes_routes_manifest_and_helper_script(tmp_path: Path) -> None:
    project = load_project(_make_project(tmp_path))
    out_dir = tmp_path / "wezterm"
    manifest = write_wezterm_pack(project, out_dir=out_dir)
    assert manifest.routes_path.exists()
    assert manifest.commands_path.exists()
    assert manifest.readme_path.exists()
    assert len(manifest.routes) == 1
    assert len(manifest.skipped) == 1
    helper_text = manifest.helper_paths[0].read_text(encoding="utf-8")
    assert 'WEZTERM_MATCH_TITLE=${WEZTERM_MATCH_TITLE:-Work Pane}' in helper_text
    assert 'WEZTERM_SEND_MODE=${WEZTERM_SEND_MODE:-paste}' in helper_text
    assert 'cli list --format json' in helper_text
    assert 'cli get-text --pane-id "$WEZTERM_PANE_ID" > "$WEZTERM_CAPTURE_FILE"' in helper_text
    payload = json.loads(manifest.commands_path.read_text(encoding="utf-8"))
    assert payload["project"] == "wezterm-proj"
    assert payload["route_count"] == 1
    assert payload["routes"][0]["title_pattern"] == "Work Pane"
    assert payload["routes"][0]["title_match_mode"] == "exact"
    assert payload["skipped"][0]["reason"] == "missing_pane_hint"
    readme = manifest.readme_path.read_text(encoding="utf-8")
    assert "title/title_regex" in readme
    assert "WEZTERM_PANE_ID" in readme


def test_gen_wezterm_pack_cli_json_writes_pack(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    out_dir = tmp_path / "pack"
    res = runner.invoke(app, ["gen-wezterm-pack", str(project_dir), str(out_dir), "--json"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.output)
    assert payload["project"] == "wezterm-proj"
    assert payload["route_count"] == 1
    assert len(payload["helper_paths"]) == 1
    assert len(payload["skipped"]) == 1
    assert (out_dir / "vhk.wezterm.routes.yml").exists()
    assert (out_dir / "vhk.wezterm.commands.json").exists()
    helper_text = Path(payload["helper_paths"][0]).read_text(encoding="utf-8")
    assert 'cli send-text --pane-id "$WEZTERM_PANE_ID"' in helper_text
