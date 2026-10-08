from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.core.runner import RunResult


runner = CliRunner()


def _write_jsonl(path: Path, events: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8")


def _make_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "proj"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "macros" / "capture.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "capture",
                "group": "Capture",
                "description": "Take a screenshot",
                "icon": "camera-photo",
                "tags": ["screen", "vision"],
                "steps": [{"type": "Return", "value": "ok"}],
            },
            sort_keys=False,
        )
    )
    (project_dir / "macros" / "deploy.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "deploy",
                "group": "Release",
                "description": "Ship the current build",
                "icon": "system-run",
                "presets": [
                    {
                        "name": "staging",
                        "description": "Deploy to staging",
                        "vars": {"env": "staging", "approve": False},
                        "tags": ["staging"],
                    },
                    {
                        "name": "prod",
                        "description": "Deploy to production",
                        "icon": "cloud-upload",
                        "vars": {"env": "prod", "approve": True},
                        "tags": ["prod"],
                        "prompt_form": {
                            "title": "Deploy ${env}",
                            "text": "Collect release details",
                            "fields": [
                                {"name": "version", "label": "Version", "default": "${default_version}"},
                                {"name": "ticket", "label": "Ticket", "default": "OPS-000"},
                            ],
                        },
                    },
                    {
                        "name": "ops",
                        "description": "Ops-only helper",
                        "vars": {"env": "ops"},
                        "hidden": True,
                    },
                ],
                "steps": [{"type": "Return", "value": "done"}],
            },
            sort_keys=False,
        )
    )
    (project_dir / "macros" / "hidden.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "hidden",
                "description": "Internal helper",
                "hidden": True,
                "steps": [{"type": "Return", "value": "secret"}],
            },
            sort_keys=False,
        )
    )
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj",
                "settings": {"event_log": False},
                "macros": {
                    "capture": "macros/capture.yaml",
                    "deploy": "macros/deploy.yaml",
                    "hidden": "macros/hidden.yaml",
                },
                "bindings": [
                    {"keys": "Ctrl+Shift+S", "macro": "capture", "description": "Capture screen"},
                    {"keys": "Ctrl+Alt+D", "macro": "deploy", "description": "Run deploy"},
                ],
                "hotstrings": [
                    {"trigger": ":cap", "macro": "capture", "enabled": True},
                ],
            },
            sort_keys=False,
        )
    )

    log_dir = project_dir / "logs"
    _write_jsonl(
        log_dir / "run_capture.jsonl",
        [
            {"ts": 10.0, "type": "run_start", "run_id": "r1", "project": "proj", "macro": "capture"},
            {"ts": 11.0, "type": "run_end", "run_id": "r1", "ok": True},
        ],
    )
    _write_jsonl(
        log_dir / "run_deploy.jsonl",
        [
            {"ts": 20.0, "type": "run_start", "run_id": "r2", "project": "proj", "macro": "deploy"},
            {"ts": 21.0, "type": "run_end", "run_id": "r2", "ok": True},
        ],
    )
    return project_dir


def test_palette_json_includes_metadata_and_recent_order(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(app, ["palette", str(project_dir), "--json"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.output)

    assert payload["count"] == 4
    assert [e["entry_id"] for e in payload["entries"]] == ["deploy", "deploy@prod", "deploy@staging", "capture"]
    prod = next(e for e in payload["entries"] if e["entry_id"] == "deploy@prod")
    assert prod["needs_prompt"] is True
    assert prod["prompt_fields"] == ["version", "ticket"]
    capture = next(e for e in payload["entries"] if e["entry_id"] == "capture")
    assert capture["group"] == "Capture"
    assert capture["description"] == "Take a screenshot"
    assert capture["icon"] == "camera-photo"
    assert capture["tags"] == ["screen", "vision"]
    assert capture["hotkeys"] == ["Ctrl+Shift+S"]
    assert capture["hotstrings"] == [":cap"]
    assert "camera-photo" in capture["search_terms"]
    assert capture["recent_runs"] == 1
    assert prod["icon"] == "cloud-upload"
    assert "deploy@prod" in prod["search_terms"]




def test_palette_json_can_disable_preset_expansion(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(app, ["palette", str(project_dir), "--json", "--no-presets"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.output)
    assert payload["count"] == 2
    assert [e["entry_id"] for e in payload["entries"]] == ["deploy", "capture"]


def test_run_rejects_unknown_preset(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(app, ["run", str(project_dir), "deploy", "--preset", "qa"])
    assert res.exit_code != 0
    assert "Unknown preset 'qa'" in res.output
    assert "staging" in res.output and "prod" in res.output

def test_palette_json_can_include_hidden_and_alpha_sort(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(app, ["palette", str(project_dir), "--json", "--alpha", "--include-hidden"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.output)

    assert [e["entry_id"] for e in payload["entries"]] == ["hidden", "capture", "deploy", "deploy@ops", "deploy@prod", "deploy@staging"]
    hidden = next(e for e in payload["entries"] if e["entry_id"] == "hidden")
    assert hidden["hidden"] is True
    prod = next(e for e in payload["entries"] if e["entry_id"] == "deploy@prod")
    assert prod["preset"] == "prod"
    assert prod["vars"] == {"env": "prod", "approve": True}
    assert "prod" in prod["tags"]


def test_palette_can_choose_and_run_selected_macro(tmp_path: Path, monkeypatch) -> None:
    project_dir = _make_project(tmp_path)

    import vhk.cli as cli_mod

    seen: dict[str, object] = {}

    def fake_choose(items, **kwargs):
        seen["items"] = list(items)
        seen["kwargs"] = kwargs
        return next(x for x in items if x.startswith("Release › deploy [prod]"))

    def fake_run(self, macro_name, initial_vars=None):
        seen["macro"] = macro_name
        seen["vars"] = initial_vars
        return RunResult(ok=True, vars={"return_value": "ok"}, event_log=None)

    monkeypatch.setattr(cli_mod, "choose_from_list", fake_choose)
    monkeypatch.setattr(cli_mod.Runner, "run", fake_run)

    res = runner.invoke(app, ["palette", str(project_dir), "--no-preset-prompts", "--vars", '{"ticket":"123"}'])
    assert res.exit_code == 0, res.output
    assert seen["macro"] == "deploy"
    assert seen["vars"] == {"env": "prod", "approve": True, "ticket": "123"}
    assert seen["kwargs"]["title"] == "proj"
    assert seen["kwargs"]["text"] == "Run macro"


def test_palette_no_run_prints_selected_macro_or_preset(tmp_path: Path, monkeypatch) -> None:
    project_dir = _make_project(tmp_path)

    import vhk.cli as cli_mod

    monkeypatch.setattr(cli_mod, "choose_from_list", lambda items, **kwargs: next(x for x in items if x.startswith("Capture › capture")))

    res = runner.invoke(app, ["palette", str(project_dir), "--no-run"])
    assert res.exit_code == 0, res.output
    assert res.output.strip() == "capture"


def test_palette_no_run_prints_preset_entry_id(tmp_path: Path, monkeypatch) -> None:
    project_dir = _make_project(tmp_path)

    import vhk.cli as cli_mod

    monkeypatch.setattr(cli_mod, "choose_from_list", lambda items, **kwargs: next(x for x in items if x.startswith("Release › deploy [staging]")))

    res = runner.invoke(app, ["palette", str(project_dir), "--no-run"])
    assert res.exit_code == 0, res.output
    assert res.output.strip() == "deploy@staging"


def test_run_can_use_macro_preset_and_override_vars(tmp_path: Path, monkeypatch) -> None:
    project_dir = _make_project(tmp_path)

    import vhk.cli as cli_mod

    seen: dict[str, object] = {}

    def fake_run(self, macro_name, initial_vars=None):
        seen["macro"] = macro_name
        seen["vars"] = dict(initial_vars or {})
        return RunResult(ok=True, vars={"return_value": "ok"}, event_log=None)

    monkeypatch.setattr(cli_mod.Runner, "run", fake_run)

    res = runner.invoke(app, ["run", str(project_dir), "deploy", "--preset", "staging", "--vars", '{"ticket":"456","approve":true}'])
    assert res.exit_code == 0, res.output
    assert seen["macro"] == "deploy"
    assert seen["vars"] == {"env": "staging", "approve": True, "ticket": "456"}


def test_run_preset_prompt_overlay_merges_after_cli_vars(tmp_path: Path, monkeypatch) -> None:
    project_dir = _make_project(tmp_path)

    import vhk.cli as cli_mod

    seen: dict[str, object] = {}

    def fake_prompt_overlay(prompt_form, ctx, *, dry_run=False):
        seen["prompt_ctx"] = dict(ctx)
        seen["prompt_dry_run"] = dry_run
        return {"version": "2.0.0", "ticket": "OPS-9"}

    def fake_run(self, macro_name, initial_vars=None):
        seen["macro"] = macro_name
        seen["vars"] = dict(initial_vars or {})
        return RunResult(ok=True, vars={"return_value": "ok"}, event_log=None)

    monkeypatch.setattr(cli_mod, "prompt_preset_overlay", fake_prompt_overlay)
    monkeypatch.setattr(cli_mod.Runner, "run", fake_run)

    res = runner.invoke(
        app,
        [
            "run",
            str(project_dir),
            "deploy",
            "--preset",
            "prod",
            "--vars",
            '{"default_version":"1.2.3","ticket":"CLI-1","approve":false}',
        ],
    )
    assert res.exit_code == 0, res.output
    assert seen["macro"] == "deploy"
    assert seen["prompt_ctx"] == {"env": "prod", "approve": False, "default_version": "1.2.3", "ticket": "CLI-1"}
    assert seen["vars"] == {
        "env": "prod",
        "approve": False,
        "default_version": "1.2.3",
        "ticket": "OPS-9",
        "version": "2.0.0",
    }


def test_run_can_disable_preset_prompt_overlay(tmp_path: Path, monkeypatch) -> None:
    project_dir = _make_project(tmp_path)

    import vhk.cli as cli_mod

    seen: dict[str, object] = {}

    def fake_prompt_overlay(prompt_form, ctx, *, dry_run=False):
        raise AssertionError("prompt overlay should not be called")

    def fake_run(self, macro_name, initial_vars=None):
        seen["vars"] = dict(initial_vars or {})
        return RunResult(ok=True, vars={"return_value": "ok"}, event_log=None)

    monkeypatch.setattr(cli_mod, "prompt_preset_overlay", fake_prompt_overlay)
    monkeypatch.setattr(cli_mod.Runner, "run", fake_run)

    res = runner.invoke(app, ["run", str(project_dir), "deploy", "--preset", "prod", "--no-preset-prompts"])
    assert res.exit_code == 0, res.output
    assert seen["vars"] == {"env": "prod", "approve": True}


def test_palette_can_choose_prompted_preset_and_run_selected_macro(tmp_path: Path, monkeypatch) -> None:
    project_dir = _make_project(tmp_path)

    import vhk.cli as cli_mod

    seen: dict[str, object] = {}

    def fake_choose(items, **kwargs):
        return next(x for x in items if x.startswith("Release › deploy [prod]"))

    def fake_prompt_overlay(prompt_form, ctx, *, dry_run=False):
        seen["prompt_ctx"] = dict(ctx)
        return {"version": "3.1.4", "ticket": "OPS-77"}

    def fake_run(self, macro_name, initial_vars=None):
        seen["macro"] = macro_name
        seen["vars"] = dict(initial_vars or {})
        return RunResult(ok=True, vars={"return_value": "ok"}, event_log=None)

    monkeypatch.setattr(cli_mod, "choose_from_list", fake_choose)
    monkeypatch.setattr(cli_mod, "prompt_preset_overlay", fake_prompt_overlay)
    monkeypatch.setattr(cli_mod.Runner, "run", fake_run)

    res = runner.invoke(app, ["palette", str(project_dir), "--vars", '{"default_version":"9.9.9"}'])
    assert res.exit_code == 0, res.output
    assert seen["macro"] == "deploy"
    assert seen["prompt_ctx"] == {"env": "prod", "approve": True, "default_version": "9.9.9"}
    assert seen["vars"] == {"env": "prod", "approve": True, "default_version": "9.9.9", "version": "3.1.4", "ticket": "OPS-77"}


def test_run_can_save_and_reload_prompt_profile_for_preset(tmp_path: Path, monkeypatch) -> None:
    project_dir = _make_project(tmp_path)

    import vhk.cli as cli_mod

    seen: list[dict[str, object]] = []

    monkeypatch.setattr(cli_mod, "prompt_preset_overlay", lambda prompt_form, ctx, **kw: {"version": "7.7.7", "ticket": "OPS-777"})

    def fake_run(self, macro_name, initial_vars=None):
        seen.append(dict(initial_vars or {}))
        return RunResult(ok=True, vars={"return_value": "ok"}, event_log=None)

    monkeypatch.setattr(cli_mod.Runner, "run", fake_run)

    res = runner.invoke(app, [
        "run", str(project_dir), "deploy", "--preset", "prod", "--save-prompt-profile", "release"
    ])
    assert res.exit_code == 0, res.output
    assert seen[-1] == {"env": "prod", "approve": True, "version": "7.7.7", "ticket": "OPS-777"}

    store_path = project_dir / ".vhk" / "prompt_profiles.json"
    assert store_path.exists()
    payload = json.loads(store_path.read_text(encoding="utf-8"))
    assert payload["profiles"]["macro:deploy:preset:prod"]["release"] == {"version": "7.7.7", "ticket": "OPS-777"}


def test_run_can_load_named_prompt_profile_for_macro_prompt_step(tmp_path: Path, monkeypatch) -> None:
    project_dir = tmp_path / "proj2"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "macros" / "m.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "m",
                "steps": [
                    {
                        "type": "PromptForm",
                        "title": "Deploy",
                        "out_var": "form",
                        "fields": [
                            {"name": "version", "default": "1.0.0"},
                            {"name": "ticket", "default": "OPS-0"},
                        ],
                    },
                    {"type": "Return", "value_expr": "form"},
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump({"name": "proj2", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}}, sort_keys=False),
        encoding="utf-8",
    )
    store_path = project_dir / ".vhk" / "prompt_profiles.json"
    store_path.parent.mkdir(parents=True, exist_ok=True)
    store_path.write_text(json.dumps({
        "version": 1,
        "last": {},
        "profiles": {"macro:m:prompt:form": {"release": {"version": "9.9.9", "ticket": "OPS-9"}}},
    }), encoding="utf-8")

    import vhk.core.runner as runner_mod

    calls: list[list[tuple[str, object]]] = []

    def fake_prompt_form(fields, **kw):
        calls.append([(f.name, f.default) for f in fields])
        return {"version": fields[0].default, "ticket": fields[1].default}

    monkeypatch.setattr(runner_mod.dialogs_mod, "prompt_form", fake_prompt_form)

    res = runner.invoke(app, ["run", str(project_dir), "m", "--prompt-profile", "release", "--print-return"])
    assert res.exit_code == 0, res.output
    assert json.loads(res.output) == {"version": "9.9.9", "ticket": "OPS-9"}
    assert calls == [[("version", "9.9.9"), ("ticket", "OPS-9")]]


def test_palette_json_expands_saved_prompt_profiles_for_prompted_presets(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    from vhk.project.prompt_profiles import make_prompt_profile_store

    store = make_prompt_profile_store(project_dir, ".vhk/prompt_profiles.json")
    store.save_profile("macro:deploy:preset:prod", "release", {"version": "9.9.9", "ticket": "OPS-9"})
    store.save_profile("macro:deploy:preset:prod", "hotfix", {"version": "9.9.8", "ticket": "OPS-8"})

    res = runner.invoke(app, ["palette", str(project_dir), "--json"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.output)

    assert [e["entry_id"] for e in payload["entries"]] == [
        "deploy",
        "deploy@prod",
        "deploy@prod#hotfix",
        "deploy@prod#release",
        "deploy@staging",
        "capture",
    ]
    prod = next(e for e in payload["entries"] if e["entry_id"] == "deploy@prod")
    assert prod["available_prompt_profiles"] == ["hotfix", "release"]
    hotfix = next(e for e in payload["entries"] if e["entry_id"] == "deploy@prod#hotfix")
    assert hotfix["prompt_profile"] == "hotfix"
    assert hotfix["prompt_profile_key"] == "macro:deploy:preset:prod"


def test_palette_can_choose_saved_prompt_profile_action_and_run_with_it(tmp_path: Path, monkeypatch) -> None:
    project_dir = _make_project(tmp_path)

    from vhk.project.prompt_profiles import make_prompt_profile_store
    import vhk.cli as cli_mod

    store = make_prompt_profile_store(project_dir, ".vhk/prompt_profiles.json")
    store.save_profile("macro:deploy:preset:prod", "release", {"version": "9.9.9", "ticket": "OPS-9"})

    seen: dict[str, object] = {}

    monkeypatch.setattr(cli_mod, "choose_from_list", lambda items, **kwargs: next(x for x in items if "‹release›" in x))

    def fake_run(self, macro_name, initial_vars=None):
        seen["macro"] = macro_name
        seen["vars"] = dict(initial_vars or {})
        return RunResult(ok=True, vars={"return_value": "ok"}, event_log=None)

    monkeypatch.setattr(cli_mod.Runner, "run", fake_run)

    res = runner.invoke(app, ["palette", str(project_dir), "--dry-run"])
    assert res.exit_code == 0, res.output
    assert seen["macro"] == "deploy"
    assert seen["vars"] == {"env": "prod", "approve": True, "version": "9.9.9", "ticket": "OPS-9"}


def test_list_and_delete_prompt_profiles_cli(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    from vhk.project.prompt_profiles import make_prompt_profile_store

    store = make_prompt_profile_store(project_dir, ".vhk/prompt_profiles.json")
    store.save_profile("macro:deploy:preset:prod", "release", {"version": "9.9.9"})

    res = runner.invoke(app, ["list-prompt-profiles", str(project_dir), "--json"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.output)
    assert payload["count"] == 1
    assert payload["keys"] == {"macro:deploy:preset:prod": ["release"]}

    res2 = runner.invoke(app, ["delete-prompt-profile", str(project_dir), "macro:deploy:preset:prod", "release", "--yes"])
    assert res2.exit_code == 0, res2.output

    res3 = runner.invoke(app, ["list-prompt-profiles", str(project_dir), "--json"])
    assert res3.exit_code == 0, res3.output
    payload2 = json.loads(res3.output)
    assert payload2["count"] == 0
    assert payload2["keys"] == {}
