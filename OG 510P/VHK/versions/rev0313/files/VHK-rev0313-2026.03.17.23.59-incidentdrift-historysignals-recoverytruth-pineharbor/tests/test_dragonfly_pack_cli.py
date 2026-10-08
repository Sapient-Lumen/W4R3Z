from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.project.dragonfly_pack import build_dragonfly_entries, find_voice_phrase_collisions, render_dragonfly_module, write_dragonfly_pack
from vhk.project.loader import load_project


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



def test_build_dragonfly_entries_uses_voice_phrases_contexts_and_skips_unsupported(tmp_path: Path) -> None:
    project = load_project(_make_project(tmp_path))
    commands, skipped = build_dragonfly_entries(project, command="python -m vhk.cli")
    assert [(item.macro, item.preset) for item in commands] == [
        ("capture", None),
        ("deploy", None),
        ("deploy", "prod"),
    ]
    deploy = next(item for item in commands if item.macro == "deploy" and item.preset is None)
    assert deploy.spoken_forms[:2] == ("ship build", "deploy build")
    assert deploy.argv[:3] == ("python", "-m", "vhk.cli")
    assert project.root_dir in deploy.argv
    assert "deploy" in deploy.argv
    assert deploy.argv[-1] == "--quiet"
    assert deploy.voice_context == {"cls": "Firefox", "title": "CI Dashboard"}
    prod = next(item for item in commands if item.preset == "prod")
    assert prod.voice_context == {"cls": "Firefox", "title": "Production"}
    assert {item.preset or item.macro: item.skip_reason for item in skipped} == {
        "staging": "preset prompt overlay requires interactive input",
        "review": "voice context uses unsupported Dragonfly selector fields: workspace",
    }



def test_render_dragonfly_module_contains_contextual_grammars(tmp_path: Path) -> None:
    project = load_project(_make_project(tmp_path))
    commands, _ = build_dragonfly_entries(project)
    text = render_dragonfly_module(project, commands=commands)
    assert 'from dragonfly import AppContext, Function, Grammar, MappingRule' in text
    assert 'GRAMMAR_SPECS =' in text
    assert '"cls": "Firefox"' in text
    assert '"title": "CI Dashboard"' in text
    assert '"title": "Production"' in text
    assert 'Grammar(_spec[\'name\'], context=_context)' in text
    assert 'Function(_run_vhk, command=COMMANDS[item[\'command_id\']])' in text



def test_write_dragonfly_pack_writes_module_manifest_and_readme(tmp_path: Path) -> None:
    project = load_project(_make_project(tmp_path))
    out_dir = tmp_path / "dragonfly"
    manifest = write_dragonfly_pack(project, out_dir=out_dir)
    assert manifest.module_path.exists()
    assert manifest.commands_path.exists()
    assert manifest.readme_path.exists()
    payload = json.loads(manifest.commands_path.read_text(encoding="utf-8"))
    assert payload["project"] == "proj"
    assert payload["command_count"] == 3
    assert payload["skipped_count"] == 2
    assert any(item["voice_context"] == {"cls": "Firefox", "title": "Production"} for item in payload["commands"])
    readme = manifest.readme_path.read_text(encoding="utf-8")
    assert "`voice_when` is only exported when it can be mapped honestly" in readme
    assert "context: class=Firefox, title=Production" in readme



def test_voice_phrase_dedup_is_context_scoped_for_dragonfly(tmp_path: Path) -> None:
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
    commands, skipped = build_dragonfly_entries(project)
    assert not skipped
    assert [item.command_id for item in commands] == ["alpha-class-firefox-title-dashboard-a", "beta-class-firefox-title-dashboard-b"]
    assert [item.spoken_forms for item in commands] == [("open dashboard", "alpha"), ("open dashboard", "beta")]
    assert not find_voice_phrase_collisions(project, backend="dragonfly")


def test_voice_phrase_collisions_are_reported_within_same_dragonfly_scope(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj_collision"
    (project_dir / "macros").mkdir(parents=True)
    for name in ["alpha", "beta"]:
        (project_dir / "macros" / f"{name}.yaml").write_text(
            yaml.safe_dump(
                {
                    "name": name,
                    "voice_phrases": ["open dashboard"],
                    "steps": [{"type": "Return", "value": "ok"}],
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj_collision",
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
    collisions = find_voice_phrase_collisions(project, backend="dragonfly")
    assert [item.to_dict() for item in collisions] == [
        {
            "backend": "dragonfly",
            "phrase": "open dashboard",
            "context_label": None,
            "targets": ["alpha", "beta"],
        }
    ]


def test_gen_dragonfly_pack_cli_json_and_include_prompt_entries(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    out_dir = tmp_path / "pack"
    res = runner.invoke(
        app,
        [
            "gen-dragonfly-pack",
            str(project_dir),
            str(out_dir),
            "--command",
            "python -m vhk.cli",
            "--include-prompt-entries",
            "--json",
        ],
    )
    assert res.exit_code == 0, res.output
    payload = json.loads(res.output)
    assert payload["command_count"] == 4
    assert payload["skipped_count"] == 1
    assert (out_dir / payload["module_name"]).exists()
    module_text = (out_dir / payload["module_name"]).read_text(encoding="utf-8")
    assert '"deploy staging"' in module_text
    assert '"CI Dashboard"' in module_text
