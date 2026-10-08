from __future__ import annotations

from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def test_optimize_check_exit_codes(tmp_path: Path) -> None:
    macro = tmp_path / "m.yaml"
    macro.write_text(
        yaml.safe_dump(
            {
                "name": "m",
                "steps": [
                    {"type": "Delay", "ms": 10},
                    {"type": "Delay", "ms": 20},
                ],
            }
        )
    )

    res = runner.invoke(app, ["optimize", str(macro), "--check", "--quiet"])
    assert res.exit_code == 1

    # Ensure check mode does not rewrite the file.
    out = yaml.safe_load(macro.read_text())
    assert out["steps"][0] == {"type": "Delay", "ms": 10}

    # A macro that is already optimized should exit 0.
    macro.write_text(
        yaml.safe_dump(
            {
                "name": "m",
                "steps": [
                    {"type": "Delay", "ms": 30},
                ],
            },
            sort_keys=False,
        )
    )
    res2 = runner.invoke(app, ["optimize", str(macro), "--check", "--quiet"])
    assert res2.exit_code == 0


def test_optimize_diff_is_diff_only(tmp_path: Path) -> None:
    macro = tmp_path / "m.yaml"
    macro.write_text(
        yaml.safe_dump(
            {
                "name": "m",
                "steps": [
                    {"type": "Delay", "ms": 10},
                    {"type": "Delay", "ms": 20},
                ],
            }
        )
    )

    res = runner.invoke(app, ["optimize", str(macro), "--diff", "--quiet"])
    assert res.exit_code == 0
    assert res.output.startswith("--- ")
    assert "+++" in res.output


def test_optimize_project_check_and_diff(tmp_path: Path) -> None:
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
                ],
            }
        )
    )

    res = runner.invoke(app, ["optimize-project", str(project_dir), "--check", "--quiet"])
    assert res.exit_code == 1

    # Diff review mode should output a unified diff.
    res2 = runner.invoke(app, ["optimize-project", str(project_dir), "--diff", "--quiet"])
    assert res2.exit_code == 0
    assert res2.output.startswith("--- ")
    assert "+++" in res2.output
