from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.project.loader import load_project
from vhk.project.qutebrowser_pack import render_qutebrowser_routes_yaml, write_qutebrowser_pack


runner = CliRunner()



def _make_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "qute-proj"
    (project_dir / "macros").mkdir(parents=True)

    (project_dir / "macros" / "copy_page_info.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "copy_page_info",
                "description": "Capture qutebrowser page context for a VHK macro",
                "steps": [
                    {"type": "WaitForWindow", "selector": {"class": "qutebrowser", "title": "Docs"}, "timeout_ms": 1000},
                    {"type": "Return", "value": "ok"},
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    (project_dir / "macros" / "generic.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "generic",
                "description": "Not qutebrowser specific",
                "steps": [
                    {"type": "ShowMessage", "title": "Generic", "text": "hi"},
                    {"type": "Return", "value": "ok"},
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "qute-proj",
                "settings": {"desktop_backend": "wayland", "event_log": False},
                "bindings": [
                    {"keys": ",y", "macro": "copy_page_info", "when": {"class": "qutebrowser", "title": "Docs"}},
                    {"keys": "Mod4+G", "macro": "generic"},
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return project_dir



def test_render_qutebrowser_routes_yaml_mentions_spawn_hint_and_qute_vars(tmp_path: Path) -> None:
    project = load_project(_make_project(tmp_path))
    manifest = write_qutebrowser_pack(project, out_dir=tmp_path / "qute")
    text = render_qutebrowser_routes_yaml(project, routes=list(manifest.routes), skipped=list(manifest.skipped))
    assert "vhk gen-qutebrowser-pack" in text
    assert ":spawn --userscript copy-page-info-qutebrowser-userscript" in text
    assert ":hint links userscript copy-page-info-qutebrowser-userscript" in text
    assert "qute_selected_text" in text



def test_write_qutebrowser_pack_writes_catalog_manifest_and_userscript(tmp_path: Path) -> None:
    project = load_project(_make_project(tmp_path))
    out_dir = tmp_path / "qute"
    manifest = write_qutebrowser_pack(project, out_dir=out_dir)
    assert manifest.routes_path.exists()
    assert manifest.commands_path.exists()
    assert manifest.readme_path.exists()
    assert len(manifest.routes) == 1
    assert len(manifest.skipped) == 0
    script_text = manifest.userscript_paths[0].read_text(encoding="utf-8")
    assert 'VHK_COMMAND=${VHK_COMMAND:-vhk}' in script_text
    assert 'QUTE_MODE' in script_text
    assert 'QUTE_URL' in script_text
    assert 'QUTE_FIFO' in script_text
    assert 'message-info VHK userscript %s starting' in script_text
    payload = json.loads(manifest.commands_path.read_text(encoding="utf-8"))
    assert payload["project"] == "qute-proj"
    assert payload["route_count"] == 1
    assert payload["routes"][0]["macro"] == "copy_page_info"
    assert payload["routes"][0]["spawn_example"] == ":spawn --userscript copy-page-info-qutebrowser-userscript"
    assert payload["routes"][0]["hint_example"] == ":hint links userscript copy-page-info-qutebrowser-userscript"
    readme = manifest.readme_path.read_text(encoding="utf-8")
    assert "~/.local/share/qutebrowser/userscripts" in readme
    assert "QUTE_MODE" in readme
    assert "message-info" in readme



def test_gen_qutebrowser_pack_cli_json_writes_pack(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    out_dir = tmp_path / "pack"
    res = runner.invoke(app, ["gen-qutebrowser-pack", str(project_dir), str(out_dir), "--json"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.output)
    assert payload["project"] == "qute-proj"
    assert payload["route_count"] == 1
    assert len(payload["userscript_paths"]) == 1
    assert (out_dir / "vhk.qutebrowser.routes.yml").exists()
    assert (out_dir / "vhk.qutebrowser.commands.json").exists()
    script_text = Path(payload["userscript_paths"][0]).read_text(encoding="utf-8")
    assert 'VHK_RUN_MODE:-run' in script_text
    assert '"$VHK_COMMAND" run "$VHK_PROJECT_DIR" "$VHK_MACRO" --vars "$VHK_VARS" --quiet' in script_text
