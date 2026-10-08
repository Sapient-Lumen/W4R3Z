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
