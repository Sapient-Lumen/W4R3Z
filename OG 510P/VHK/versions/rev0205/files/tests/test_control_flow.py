from __future__ import annotations

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


def test_while_continue_break_and_return_from_child_macro(tmp_path: Path):
    proj = _write_project(
        tmp_path,
        {
            "name": "p",
            "settings": {"event_log": False},
            "macros": {"parent": "macros/parent.yaml", "child": "macros/child.yaml"},
        },
        {
            "child": {
                "name": "child",
                "steps": [
                    {"type": "SetVar", "name": "seen", "value": "before"},
                    {"type": "Return", "value_expr": "'done:' + who", "out_var": "rv"},
                    {"type": "SetVar", "name": "seen", "value": "after"},
                ],
            },
            "parent": {
                "name": "parent",
                "steps": [
                    {"type": "SetVar", "name": "i", "value": 0},
                    {"type": "WriteFile", "path": "data/seen.txt", "text": ""},
                    {
                        "type": "While",
                        "condition": "i < 6",
                        "steps": [
                            {
                                "type": "If",
                                "condition": "i == 1",
                                "then_steps": [
                                    {"type": "SetVar", "name": "i", "value": "i + 1"},
                                    {"type": "Continue"},
                                ],
                            },
                            {
                                "type": "If",
                                "condition": "i == 4",
                                "then_steps": [{"type": "Break"}],
                            },
                            {"type": "AppendFile", "path": "data/seen.txt", "text": "${i},"},
                            {"type": "SetVar", "name": "i", "value": "i + 1"},
                        ],
                    },
                    {
                        "type": "CallMacro",
                        "macro": "child",
                        "args": {"who": "bob"},
                        "returns": {"rv": "child_rv", "seen": "child_seen"},
                    },
                ],
            },
        },
    )

    res = Runner(load_project(proj)).run("parent")
    assert res.ok
    assert (proj / "data" / "seen.txt").read_text() == "0,2,3,"
    assert res.vars["while_iterations"] == 5
    assert res.vars["child_rv"] == "done:bob"
    assert res.vars["child_seen"] == "before"


def test_try_catch_finally_and_while_iteration_limit(tmp_path: Path):
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml", "bad": "macros/bad.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {
                        "type": "Try",
                        "steps": [
                            {"type": "RunShell", "command": "python -c \"import sys; sys.exit(3)\""},
                        ],
                        "catch_steps": [
                            {"type": "SetVar", "name": "caught", "value": "${last_error.error_type}:${last_error.error}"},
                        ],
                        "finally_steps": [
                            {"type": "SetVar", "name": "cleanup", "value": "done"},
                        ],
                    }
                ],
            },
            "bad": {
                "name": "bad",
                "steps": [
                    {"type": "SetVar", "name": "i", "value": 0},
                    {
                        "type": "While",
                        "condition": "True",
                        "max_iterations": 3,
                        "steps": [
                            {"type": "SetVar", "name": "i", "value": "i + 1"},
                        ],
                    },
                ],
            },
        },
    )

    ok = Runner(load_project(proj)).run("m")
    assert ok.ok
    assert ok.vars["cleanup"] == "done"
    assert "RuntimeError:Command failed" in ok.vars["caught"]

    bad = Runner(load_project(proj)).run("bad")
    assert not bad.ok
    assert "max_iterations=3" in (bad.error or "")


def test_wait_until_succeeds_and_times_out(tmp_path: Path):
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"ok": "macros/ok.yaml", "bad": "macros/bad.yaml"}},
        {
            "ok": {
                "name": "ok",
                "steps": [
                    {"type": "SetVar", "name": "start", "value": "monotonic_ms()"},
                    {
                        "type": "WaitUntil",
                        "condition": "monotonic_ms() - start >= 15",
                        "timeout_ms": 500,
                        "poll_ms": 1,
                        "max_poll_ms": 5,
                        "jitter_ms": 0,
                        "out_value": "delta",
                        "out_attempts": "tries",
                    },
                ],
            },
            "bad": {
                "name": "bad",
                "steps": [
                    {
                        "type": "WaitUntil",
                        "condition": "False",
                        "timeout_ms": 20,
                        "poll_ms": 0,
                        "jitter_ms": 0,
                        "max_attempts": 2,
                    }
                ],
            },
        },
    )

    ok = Runner(load_project(proj)).run("ok")
    assert ok.ok
    assert ok.vars["delta"] is True
    assert ok.vars["tries"] >= 1

    bad = Runner(load_project(proj)).run("bad")
    assert not bad.ok
    assert "WaitUntil timed out" in (bad.error or "")
