from __future__ import annotations

from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.core.models import Macro, Project, Region
from vhk.core.runner import Runner


runner = CliRunner()


def test_runner_resolves_named_region():
    proj = Project(
        name="p",
        root_dir="/tmp/p",
        macros={"m": Macro(name="m", steps=[])},
        regions={"toolbar": Region(x=1, y=2, w=3, h=4)},
    )
    r = Runner(proj)
    out = r._resolve_region_spec("@toolbar", {})
    assert isinstance(out, Region)
    assert out.x == 1 and out.y == 2 and out.w == 3 and out.h == 4

    # Shorthand: raw name if present in project regions.
    out2 = r._resolve_region_spec("toolbar", {})
    assert out2.x == 1 and out2.y == 2 and out2.w == 3 and out2.h == 4


def test_runner_parses_geometry_string():
    proj = Project(name="p", root_dir="/tmp/p", macros={"m": Macro(name="m", steps=[])})
    r = Runner(proj)
    out = r._resolve_region_spec("640x480+10+20", {})
    assert isinstance(out, Region)
    assert out.x == 10 and out.y == 20 and out.w == 640 and out.h == 480


def test_select_region_writes_project_yaml(monkeypatch, tmp_path: Path):
    # Create a tiny project.yaml.
    project_dir = tmp_path / "proj"
    project_dir.mkdir(parents=True)
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump({"name": "p", "macros": {"m": "macros/m.yaml"}, "regions": {}}, sort_keys=False)
    )

    # Stub interactive selection.
    import vhk.cli as cli_mod

    monkeypatch.setattr(cli_mod, "select_region", lambda: Region(x=7, y=8, w=9, h=10))

    result = runner.invoke(app, ["select-region", "--project", str(project_dir), "--name", "toolbar", "--json"])
    assert result.exit_code == 0, result.output

    doc = yaml.safe_load((project_dir / "project.yaml").read_text())
    regions = doc.get("regions") or {}
    assert regions["toolbar"]["x"] == 7
    assert regions["toolbar"]["y"] == 8
    assert regions["toolbar"]["w"] == 9
    assert regions["toolbar"]["h"] == 10
