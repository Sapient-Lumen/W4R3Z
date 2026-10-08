from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.project.loader import load_project
from vhk.project.talon_pack import render_talon_commands_file, render_talon_python_module, write_talon_pack


runner = CliRunner()



def _make_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "proj"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "macros" / "deploy.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "deploy",
                "group": "Release",
                "description": "Ship the current build",
                "voice_phrases": ["ship build", "deploy build"],
                "voice_when": {"class": "Firefox", "title": "CI Dashboard"},
                "presets": [
                    {
                        "name": "prod",
                        "description": "Deploy to prod",
                        "voice_phrases": ["deploy production"],
                        "voice_when": {"class": "Firefox", "title": "Production"},
                        "vars": {"env": "prod"},
                    },
                    {
                        "name": "staging",
                        "description": "Deploy to staging",
                        "vars": {"env": "staging"},
                        "prompt_form": {
                            "fields": [{"name": "version", "label": "Version"}],
                        },
                    },
                ],
                "steps": [{"type": "Return", "value": "ok"}],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (project_dir / "macros" / "capture.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "capture",
                "description": "Take screenshot",
                "steps": [{"type": "Return", "value": "ok"}],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (project_dir / "macros" / "review.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "review",
                "description": "Review current ticket",
                "voice_when": {"workspace": "2:web"},
                "steps": [{"type": "Return", "value": "ok"}],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj",
                "settings": {"event_log": False},
                "macros": {
                    "capture": "macros/capture.yaml",
                    "deploy": "macros/deploy.yaml",
                    "review": "macros/review.yaml",
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return project_dir



def test_render_talon_python_module_contains_vhk_command_map(tmp_path: Path) -> None:
    project = load_project(_make_project(tmp_path))
    manifest = write_talon_pack(project, out_dir=tmp_path / "talon", command="python -m vhk.cli")
    text = render_talon_python_module(project, commands=list(manifest.commands), base_name=manifest.base_name)
    assert 'from talon import Module, app' in text
    assert 'subprocess.Popen(command)' in text
    assert '"run"' in text
    assert '"--preset"' in text and '"prod"' in text
    assert 'def vhk_run_generated_voice(command_id: str) -> None:' in text



def test_render_talon_commands_file_contains_literal_spoken_forms_and_context_header(tmp_path: Path) -> None:
    project = load_project(_make_project(tmp_path))
    manifest = write_talon_pack(project, out_dir=tmp_path / "talon")
    deploy_entry = next(item for item in manifest.commands if item.macro == "deploy" and item.preset is None)
    text = render_talon_commands_file(project, commands=[deploy_entry], base_name=manifest.base_name, context_label=deploy_entry.voice_context_label)
    assert 'os: linux' in text
    assert 'app: Firefox' in text
    assert 'title: /CI\\ Dashboard/' in text
    assert 'ship build:' in text
    assert f'user.vhk_run_generated_voice("{deploy_entry.command_id}")' in text



def test_talon_python_module_uses_stable_command_ids(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj_ctx"
    (project_dir / "macros").mkdir(parents=True)
    for name, title in [("alpha", "Dashboard A"), ("beta", "Dashboard B")]:
        (project_dir / "macros" / f"{name}.yaml").write_text(
            yaml.safe_dump(
                {
                    "name": name,
                    "voice_phrases": ["open dashboard"],
                    "voice_when": {"class": "Firefox", "title": title},
                    "steps": [{"type": "Return", "value": "ok"}],
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj_ctx",
                "macros": {
                    "alpha": "macros/alpha.yaml",
                    "beta": "macros/beta.yaml",
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    project = load_project(project_dir)
    manifest = write_talon_pack(project, out_dir=tmp_path / "talon")
    text = render_talon_python_module(project, commands=list(manifest.commands), base_name=manifest.base_name)
    assert '"alpha-app-firefox-title-dashboard-a"' in text
    assert '"beta-app-firefox-title-dashboard-b"' in text
    assert '"open dashboard"' not in text.split("COMMANDS =", 1)[1].split("@mod.action_class", 1)[0]
    contextual = [path.read_text(encoding="utf-8") for path in manifest.context_paths]
    assert any('user.vhk_run_generated_voice("alpha-app-firefox-title-dashboard-a")' in item for item in contextual)
    assert any('user.vhk_run_generated_voice("beta-app-firefox-title-dashboard-b")' in item for item in contextual)


def test_write_talon_pack_writes_python_talon_manifest_and_context_files(tmp_path: Path) -> None:
    project = load_project(_make_project(tmp_path))
    out_dir = tmp_path / "talon"
    manifest = write_talon_pack(project, out_dir=out_dir)
    assert manifest.python_path.exists()
    assert manifest.talon_path.exists()
    assert manifest.commands_path.exists()
    assert manifest.readme_path.exists()
    assert len(manifest.context_paths) == 2
    assert all(path.exists() for path in manifest.context_paths)
    payload = json.loads(manifest.commands_path.read_text(encoding="utf-8"))
    assert payload["project"] == "proj"
    assert payload["command_count"] == 3
    assert payload["skipped_count"] == 2
    assert payload["base_name"] == manifest.base_name
    assert len(payload["context_paths"]) == 2
    root_text = manifest.talon_path.read_text(encoding="utf-8")
    assert 'capture:' in root_text
    readme = manifest.readme_path.read_text(encoding="utf-8")
    assert "optional extra `.talon` files" in readme
    assert "context: app=Firefox, title=Production" in readme



def test_gen_talon_pack_cli_json_and_include_prompt_entries(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    out_dir = tmp_path / "pack"
    res = runner.invoke(
        app,
        [
            "gen-talon-pack",
            str(project_dir),
            str(out_dir),
            "--command",
            "python -m vhk.cli",
            "--include-prompt-entries",
            "--base-name",
            "voice_proj",
            "--json",
        ],
    )
    assert res.exit_code == 0, res.output
    payload = json.loads(res.output)
    assert payload["command_count"] == 4
    assert payload["skipped_count"] == 1
    assert payload["base_name"] == "voice_proj"
    assert (out_dir / "voice_proj.py").exists()
    assert (out_dir / "voice_proj.talon").exists()
    assert len(payload["context_paths"]) == 2
    contextual_text = Path(payload["context_paths"][0]).read_text(encoding="utf-8")
    assert 'app: Firefox' in contextual_text
    assert 'user.vhk_run_generated_voice(' in contextual_text
