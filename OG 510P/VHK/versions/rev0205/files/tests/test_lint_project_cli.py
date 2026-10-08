from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def test_lint_project_check_and_json(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "project.yaml").write_text("name: proj\n")

    (project_dir / "macros" / "a.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "a",
                "steps": [
                    {"type": "Delay", "ms": 2000},
                    {"type": "MouseClickAt", "x": 1, "y": 2},
                ],
            },
            sort_keys=False,
        )
    )

    res = runner.invoke(app, ["lint-project", str(project_dir), "--check", "--json"])
    assert res.exit_code == 1
    data = json.loads(res.output)
    assert data["issue_count"] >= 2
    assert any(i.get("macro") == "macros/a.yaml" for i in data["issues"])


def test_lint_project_warns_on_missing_session_capabilities(tmp_path: Path, monkeypatch) -> None:
    project_dir = tmp_path / "proj"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj",
                "macros": {"main": "macros/main.yaml"},
                "bindings": [{"keys": "Mod4+M", "macro": "main"}],
            },
            sort_keys=False,
        )
    )
    (project_dir / "macros" / "main.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "main",
                "steps": [{"type": "TypeText", "text": "hello"}],
            },
            sort_keys=False,
        )
    )

    import vhk.cli as cli_mod

    monkeypatch.setattr(
        cli_mod,
        "_validation_session_capability_matrix",
        lambda: {
            "global_hotkeys": {"status": "missing", "mechanisms": [], "recommended": None, "notes": [], "portal_backends": []},
            "text_injection": {"status": "limited", "mechanisms": ["portal:RemoteDesktop(keyboard)"], "recommended": None, "notes": ["interactive"], "portal_backends": ["gnome"]},
            "screen_capture": {"status": "ok", "mechanisms": ["portal:Screenshot"], "recommended": "portal:Screenshot", "notes": [], "portal_backends": ["gtk"]},
            "pointer_injection": {"status": "ok", "mechanisms": [], "recommended": None, "notes": [], "portal_backends": []},
            "window_introspection": {"status": "ok", "mechanisms": [], "recommended": None, "notes": [], "portal_backends": []},
        },
    )

    res = runner.invoke(app, ["lint-project", str(project_dir), "--json", "--check"])
    assert res.exit_code == 1, res.output
    data = json.loads(res.output)
    assert data["session_capabilities"]["text_injection"]["status"] == "limited"
    sess = [i for i in data["issues"] if i.get("macro") == "<project>"]
    assert any(i.get("capability") == "global_hotkeys" for i in sess)
    assert any(i.get("capability") == "text_injection" for i in sess)
    assert data["capability_usage"]["global_hotkeys"]
    assert data["capability_usage"]["text_injection"]


def test_lint_project_can_disable_session_capability_check(tmp_path: Path, monkeypatch) -> None:
    project_dir = tmp_path / "proj"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj",
                "macros": {"main": "macros/main.yaml"},
            },
            sort_keys=False,
        )
    )
    (project_dir / "macros" / "main.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "main",
                "steps": [{"type": "TypeText", "text": "hello"}],
            },
            sort_keys=False,
        )
    )

    import vhk.cli as cli_mod

    monkeypatch.setattr(
        cli_mod,
        "_validation_session_capability_matrix",
        lambda: (_ for _ in ()).throw(AssertionError("should not be called")),
    )

    res = runner.invoke(app, ["lint-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)
    assert data["session_capabilities"] is None
    assert all(i.get("macro") != "<project>" for i in data["issues"])
