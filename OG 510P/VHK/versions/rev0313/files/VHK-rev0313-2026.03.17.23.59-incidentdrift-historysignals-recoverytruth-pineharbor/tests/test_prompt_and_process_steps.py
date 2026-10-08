from __future__ import annotations

import sys
from pathlib import Path

import yaml

from vhk.core.runner import Runner
from vhk.project.loader import load_project


def _write_project(tmp_path: Path, manifest: dict, macros: dict[str, dict]) -> Path:
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)
    for name, data in macros.items():
        (proj / "macros" / f"{name}.yaml").write_text(yaml.safe_dump(data))
    (proj / "project.yaml").write_text(yaml.safe_dump(manifest))
    return proj


def test_prompt_steps_use_dialog_helpers(tmp_path: Path, monkeypatch):
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {"type": "ShowMessage", "title": "Hi ${name}", "text": "Ready?", "level": "warning"},
                    {"type": "AskYesNo", "text": "Continue ${name}?", "out_var": "go"},
                    {"type": "InputBox", "prompt": "Value for ${name}", "default": "x", "out_var": "answer"},
                    {"type": "ChooseFromList", "items_expr": "choices", "text": "Pick one", "out_var": "pick"},
                ],
            }
        },
    )

    import vhk.core.runner as runner_mod

    calls: list[tuple] = []
    monkeypatch.setattr(runner_mod.dialogs_mod, "show_message", lambda text, **kw: calls.append(("msg", text, kw)))
    monkeypatch.setattr(runner_mod.dialogs_mod, "ask_yes_no", lambda text, **kw: calls.append(("yesno", text, kw)) or True)
    monkeypatch.setattr(runner_mod.dialogs_mod, "input_text", lambda prompt, **kw: calls.append(("input", prompt, kw)) or "typed")
    monkeypatch.setattr(runner_mod.dialogs_mod, "choose_from_list", lambda items, **kw: calls.append(("choose", list(items), kw)) or "b")

    res = Runner(load_project(proj)).run("m", initial_vars={"name": "Ada", "choices": ["a", "b", "c"]})
    assert res.ok
    assert res.vars["go"] is True
    assert res.vars["answer"] == "typed"
    assert res.vars["pick"] == "b"
    assert calls[0] == ("msg", "Ready?", {"title": "Hi Ada", "level": "warning"})
    assert calls[1][0] == "yesno" and calls[1][1] == "Continue Ada?"
    assert calls[2][0] == "input" and calls[2][1] == "Value for Ada"
    assert calls[3] == ("choose", ["a", "b", "c"], {"title": None, "text": "Pick one", "multiple": False})


def test_start_and_wait_for_process_exit_steps(tmp_path: Path):
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {
                        "type": "StartProcess",
                        "command": [sys.executable, "-c", "pass"],
                        "out_pid": "pid",
                    },
                    {
                        "type": "WaitForProcessExit",
                        "pid": "${pid}",
                        "timeout_ms": 3000,
                        "poll_ms": 10,
                        "max_poll_ms": 20,
                        "jitter_ms": 0,
                        "out_returncode": "rc",
                    },
                ],
            }
        },
    )

    res = Runner(load_project(proj)).run("m")
    assert res.ok
    assert isinstance(res.vars["pid"], int)
    assert res.vars["process_exited"] is True
    assert res.vars["rc"] == 0


def test_kill_process_step(tmp_path: Path):
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {
                        "type": "StartProcess",
                        "command": [sys.executable, "-c", "import time; time.sleep(5)"],
                        "out_pid": "pid",
                    },
                    {"type": "KillProcess", "pid": "${pid}", "signal": "TERM", "wait_ms": 300},
                    {
                        "type": "WaitForProcessExit",
                        "pid": "${pid}",
                        "timeout_ms": 3000,
                        "poll_ms": 10,
                        "max_poll_ms": 20,
                        "jitter_ms": 0,
                        "out_returncode": "rc",
                    },
                ],
            }
        },
    )

    res = Runner(load_project(proj)).run("m")
    assert res.ok
    assert res.vars["process_killed"] is True
    assert res.vars["process_exited"] is True
    assert res.vars["rc"] not in (None, 0)


def test_prompt_form_step_uses_dialog_form_helper(tmp_path: Path, monkeypatch):
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {
                        "type": "PromptForm",
                        "title": "Deploy ${app}",
                        "text": "Collect release details",
                        "out_var": "form",
                        "fields": [
                            {"name": "version", "label": "Version", "default": "${default_version}"},
                            {"name": "confirm", "label": "Ship now?", "kind": "bool", "default": True},
                            {"name": "env", "label": "Environment", "kind": "choice", "choices_expr": "envs"},
                        ],
                    }
                ],
            }
        },
    )

    import vhk.core.runner as runner_mod

    calls: list[tuple] = []

    def fake_prompt_form(fields, **kw):
        calls.append(([(f.name, f.label, f.kind, f.default, list(f.choices)) for f in fields], kw))
        return {"version": "2.0.0", "confirm": False, "env": "staging"}

    monkeypatch.setattr(runner_mod.dialogs_mod, "prompt_form", fake_prompt_form)

    res = Runner(load_project(proj)).run(
        "m",
        initial_vars={"app": "pegasus", "default_version": "1.2.3", "envs": ["dev", "staging", "prod"]},
    )
    assert res.ok
    assert res.vars["form"] == {"version": "2.0.0", "confirm": False, "env": "staging"}
    assert calls == [
        (
            [
                ("version", "Version", "text", "1.2.3", []),
                ("confirm", "Ship now?", "bool", True, []),
                ("env", "Environment", "choice", None, ["dev", "staging", "prod"]),
            ],
            {"title": "Deploy pegasus", "text": "Collect release details"},
        )
    ]


def test_prompt_form_step_remembers_last_answers(tmp_path: Path, monkeypatch):
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {
                        "type": "PromptForm",
                        "title": "Deploy",
                        "out_var": "form",
                        "fields": [
                            {"name": "version", "default": "1.2.3"},
                            {"name": "token", "kind": "password", "default": "secret"},
                        ],
                    }
                ],
            }
        },
    )

    import vhk.core.runner as runner_mod

    calls: list[list[tuple]] = []
    answers = iter([
        {"version": "2.0.0", "token": "override"},
        {"version": "3.0.0", "token": "override2"},
    ])

    def fake_prompt_form(fields, **kw):
        calls.append([(f.name, f.default, f.kind) for f in fields])
        return next(answers)

    monkeypatch.setattr(runner_mod.dialogs_mod, "prompt_form", fake_prompt_form)

    runner = Runner(load_project(proj))
    res1 = runner.run("m")
    assert res1.ok
    res2 = Runner(load_project(proj)).run("m")
    assert res2.ok

    assert calls[0] == [("version", "1.2.3", "text"), ("token", "secret", "password")]
    assert calls[1] == [("version", "2.0.0", "text"), ("token", "secret", "password")]
