from __future__ import annotations

from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def _write_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "proj"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "project.yaml").write_text("name: proj\n")

    (project_dir / "macros" / "a.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "a",
                "steps": [
                    {"type": "Delay", "ms": 10},
                    {"type": "Delay", "ms": 20},
                    {"type": "MouseMove", "x": 1, "y": 2},
                    {"type": "MouseMove", "x": 3, "y": 4},
                    {"type": "MouseMove", "x": 3, "y": 4},
                    {"type": "KeyDown", "key": "ctrl"},
                    {"type": "KeyDown", "key": "l"},
                    {"type": "KeyUp", "key": "l"},
                    {"type": "KeyUp", "key": "ctrl"},
                ],
            }
        )
    )

    (project_dir / "macros" / "b.yaml").write_text(
        yaml.safe_dump({"name": "b", "steps": [{"type": "Log", "message": "hi"}]})
    )

    return project_dir


def test_optimize_project_writes_out_dir(tmp_path: Path) -> None:
    project_dir = _write_project(tmp_path)
    out_dir = tmp_path / "out"

    res = runner.invoke(app, ["optimize-project", str(project_dir), "--out-dir", str(out_dir), "--quiet"])
    assert res.exit_code == 0, res.output

    a_out = yaml.safe_load((out_dir / "a.yaml").read_text())
    assert a_out["steps"][0] == {"type": "Delay", "ms": 30}
    assert a_out["steps"][1] == {"type": "MouseMove", "x": 3, "y": 4}
    assert {"type": "Key", "keys": "ctrl+l"} in a_out["steps"]

    # Original file should remain unchanged.
    a_in = yaml.safe_load((project_dir / "macros" / "a.yaml").read_text())
    assert a_in["steps"][0] == {"type": "Delay", "ms": 10}


def test_optimize_project_in_place(tmp_path: Path) -> None:
    project_dir = _write_project(tmp_path)

    res = runner.invoke(app, ["optimize-project", str(project_dir), "--in-place", "--quiet"])
    assert res.exit_code == 0, res.output

    a_in = yaml.safe_load((project_dir / "macros" / "a.yaml").read_text())
    assert a_in["steps"][0] == {"type": "Delay", "ms": 30}


def test_optimize_project_can_segment_structured_text(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj_segment"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "project.yaml").write_text("name: proj_segment\n")
    (project_dir / "macros" / "form.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "form",
                "steps": [
                    {
                        "type": "TypeText",
                        "text": "Email:\tperson@example.com\nCompany:\tVery Long Company Name",
                        "backend": "native",
                    }
                ],
            }
        )
    )

    out_dir = tmp_path / "out_segment"
    res = runner.invoke(
        app,
        [
            "optimize-project",
            str(project_dir),
            "--out-dir",
            str(out_dir),
            "--segment-paste-text",
            "--segment-paste-min-chars",
            "12",
            "--quiet",
        ],
    )
    assert res.exit_code == 0, res.output

    out = yaml.safe_load((out_dir / "form.yaml").read_text())
    assert out["steps"][0]["comment"] == "optimized into hybrid text/paste lanes"
    assert out["steps"][1] == {"type": "Key", "keys": "tab"}
    assert out["steps"][2]["backend"] == "clipboard"
    assert out["steps"][3] == {"type": "Key", "keys": "enter"}
    assert out["steps"][-1]["backend"] == "clipboard"
