from __future__ import annotations

from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def test_init_creates_project(tmp_path: Path):
    proj = tmp_path / "myproj"

    result = runner.invoke(app, ["init", str(proj), "--name", "My Project", "--template", "vision"])
    assert result.exit_code == 0, result.output

    assert (proj / "project.yaml").exists()
    assert (proj / "macros" / "main.yaml").exists()
    assert (proj / "assets" / "needles").exists()
    assert (proj / "assets" / "baselines").exists()
    assert (proj / "assets" / "TODO.png").exists()
    assert (proj / "schemas" / "vhk_project.schema.json").exists()
    assert (proj / "schemas" / "vhk_macro.schema.json").exists()
    assert (proj / ".vscode" / "settings.json").exists()

    # Placeholder needle metadata is real JSON (even though YAML could parse it).
    import json

    json.loads((proj / "assets" / "TODO.json").read_text())

    manifest = yaml.safe_load((proj / "project.yaml").read_text())
    assert manifest["name"] == "My Project"
    assert "main" in (manifest.get("macros") or {})


def test_init_refuses_nonempty_without_force(tmp_path: Path):
    proj = tmp_path / "myproj"
    proj.mkdir(parents=True)
    (proj / "somefile.txt").write_text("hi")

    result = runner.invoke(app, ["init", str(proj)])
    assert result.exit_code != 0
    assert "not empty" in result.output.lower()


def test_new_macro_registers_in_manifest(tmp_path: Path):
    proj = tmp_path / "p"
    runner.invoke(app, ["init", str(proj)])

    result = runner.invoke(app, ["new-macro", str(proj), "hello", "--template", "minimal"])
    assert result.exit_code == 0, result.output

    mp = proj / "macros" / "hello.yaml"
    assert mp.exists()

    manifest = yaml.safe_load((proj / "project.yaml").read_text())
    macros = manifest.get("macros") or {}
    assert macros.get("hello") == "macros/hello.yaml"


def test_new_macro_can_skip_registration(tmp_path: Path):
    proj = tmp_path / "p"
    runner.invoke(app, ["init", str(proj)])

    result = runner.invoke(app, ["new-macro", str(proj), "unregistered", "--no-register"])
    assert result.exit_code == 0, result.output

    manifest = yaml.safe_load((proj / "project.yaml").read_text())
    macros = manifest.get("macros") or {}
    assert "unregistered" not in macros
