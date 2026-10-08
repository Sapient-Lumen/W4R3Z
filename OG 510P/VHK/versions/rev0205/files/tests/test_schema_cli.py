from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def test_schema_command_outputs_draft7_json():
    res = runner.invoke(app, ["schema", "--kind", "macro"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.output)
    assert payload.get("$schema") == "http://json-schema.org/draft-07/schema#"
    assert "definitions" in payload


def test_schemas_writes_files_and_can_patch_modelines(tmp_path: Path):
    proj = tmp_path / "p"
    runner.invoke(app, ["init", str(proj), "--no-schemas"])  # create without schemas

    res = runner.invoke(app, ["schemas", str(proj), "--patch-modelines"])
    assert res.exit_code == 0, res.output

    assert (proj / "schemas" / "vhk_project.schema.json").exists()
    assert (proj / "schemas" / "vhk_macro.schema.json").exists()

    # Modelines are inserted.
    assert (proj / "project.yaml").read_text().startswith(
        "# yaml-language-server: $schema=schemas/vhk_project.schema.json"
    )
    macro_text = (proj / "macros" / "main.yaml").read_text()
    assert macro_text.startswith("# yaml-language-server: $schema=")

    # YAML still parses.
    yaml.safe_load((proj / "project.yaml").read_text())
