from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.project.kitty_pack import render_kitty_routes_yaml, write_kitty_pack
from vhk.project.loader import load_project


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "kitty-proj"
    (project_dir / "macros").mkdir(parents=True)

    (project_dir / "macros" / "send_to_kitty.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "send_to_kitty",
                "description": "Send text to a kitty work terminal",
                "steps": [
                    {"type": "WaitForWindow", "selector": {"class": "kitty", "title": "Work"}, "timeout_ms": 1000},
                    {"type": "TypeText", "text": "pytest -q"},
                    {"type": "Return", "value": "ok"},
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    (project_dir / "macros" / "kitty_without_title.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "kitty_without_title",
                "description": "Targets kitty but does not have enough title evidence yet",
                "steps": [
                    {"type": "WaitForWindow", "selector": {"class": "kitty"}, "timeout_ms": 1000},
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
                "name": "kitty-proj",
                "settings": {"desktop_backend": "wayland", "event_log": False},
                "bindings": [
                    {"keys": "Mod4+Return", "macro": "send_to_kitty", "when": {"class": "kitty", "title": "Work"}},
                    {"keys": "Mod4+E", "macro": "kitty_without_title", "when": {"class": "kitty"}},
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return project_dir


def test_render_kitty_routes_yaml_mentions_send_text_and_match(tmp_path: Path) -> None:
    project = load_project(_make_project(tmp_path))
    manifest = write_kitty_pack(project, out_dir=tmp_path / "kitty")
    text = render_kitty_routes_yaml(project, routes=list(manifest.routes), skipped=list(manifest.skipped))
    assert "vhk gen-kitty-pack" in text
    assert "kitten @ send-text --match 'title:^Work$' --stdin" in text
    assert "allow_remote_control" in text
    assert "missing_match_hint" in text


def test_write_kitty_pack_writes_routes_manifest_and_helper_script(tmp_path: Path) -> None:
    project = load_project(_make_project(tmp_path))
    out_dir = tmp_path / "kitty"
    manifest = write_kitty_pack(project, out_dir=out_dir)
    assert manifest.routes_path.exists()
    assert manifest.commands_path.exists()
    assert manifest.readme_path.exists()
    assert len(manifest.routes) == 1
    assert len(manifest.skipped) == 1
    helper_text = manifest.helper_paths[0].read_text(encoding="utf-8")
    assert 'KITTY_MATCH=${KITTY_MATCH:-title:^Work$}' in helper_text
    assert 'KITTY_TO=${KITTY_TO:-}' in helper_text
    assert 'pytest -q' in helper_text
    payload = json.loads(manifest.commands_path.read_text(encoding="utf-8"))
    assert payload["project"] == "kitty-proj"
    assert payload["route_count"] == 1
    assert payload["routes"][0]["match_expr"] == "title:^Work$"
    assert payload["skipped"][0]["reason"] == "missing_match_hint"
    readme = manifest.readme_path.read_text(encoding="utf-8")
    assert "allow_remote_control" in readme
    assert "title/title_regex" in readme


def test_gen_kitty_pack_cli_json_writes_pack(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    out_dir = tmp_path / "pack"
    res = runner.invoke(app, ["gen-kitty-pack", str(project_dir), str(out_dir), "--json"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.output)
    assert payload["project"] == "kitty-proj"
    assert payload["route_count"] == 1
    assert len(payload["helper_paths"]) == 1
    assert len(payload["skipped"]) == 1
    assert (out_dir / "vhk.kitty.routes.yml").exists()
    assert (out_dir / "vhk.kitty.commands.json").exists()
    helper_text = Path(payload["helper_paths"][0]).read_text(encoding="utf-8")
    assert 'send-text --match "$KITTY_MATCH" --stdin' in helper_text
