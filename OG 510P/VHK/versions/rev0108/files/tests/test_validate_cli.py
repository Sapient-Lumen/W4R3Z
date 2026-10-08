from __future__ import annotations

import yaml
from pathlib import Path

from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def _write_project(tmp_path: Path, *, bad_expr: bool = False, missing_call_target: bool = False) -> Path:
    proj = tmp_path / "p"
    (proj / "macros").mkdir(parents=True)

    steps = []
    if bad_expr:
        steps.append({"type": "If", "condition": "1 +", "then_steps": []})
    if missing_call_target:
        steps.append({"type": "CallMacro", "macro": "nope", "args": {}})
    steps.append({"type": "Return", "value_expr": "'OK'", "out_var": "return_value"})

    (proj / "macros" / "main.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "main",
                "steps": steps,
            }
        )
    )

    (proj / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "p",
                "macros": {"main": "macros/main.yaml"},
                "bindings": [{"keys": "Mod4+M", "macro": "main"}],
            }
        )
    )

    return proj


def test_validate_ok(tmp_path: Path):
    proj = _write_project(tmp_path)
    result = runner.invoke(app, ["validate", str(proj)])
    assert result.exit_code == 0, result.output


def test_validate_catches_bad_expression(tmp_path: Path):
    proj = _write_project(tmp_path, bad_expr=True)
    result = runner.invoke(app, ["validate", str(proj)])
    assert result.exit_code == 1
    assert "invalid expression" in result.output


def test_validate_catches_missing_callmacro_target(tmp_path: Path):
    proj = _write_project(tmp_path, missing_call_target=True)
    result = runner.invoke(app, ["validate", str(proj)])
    assert result.exit_code == 1
    assert "CallMacro references unknown macro" in result.output


_PNG_1X1_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/wwAAgMBAp1RXr8AAAAASUVORK5CYII="
)


def _write_png(path: Path) -> None:
    import base64

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(base64.b64decode(_PNG_1X1_B64))


def test_validate_catches_missing_visual_asset_file(tmp_path: Path):
    proj = tmp_path / "p"
    (proj / "macros").mkdir(parents=True)

    (proj / "macros" / "main.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "main",
                "steps": [
                    {"type": "ImageSearch", "needle_path": "assets/missing.png"},
                    {"type": "Return", "value_expr": "'OK'", "out_var": "return_value"},
                ],
            }
        )
    )

    (proj / "project.yaml").write_text(
        yaml.safe_dump({"name": "p", "macros": {"main": "macros/main.yaml"}})
    )

    result = runner.invoke(app, ["validate", str(proj)])
    assert result.exit_code == 1
    assert "missing required asset file" in result.output


def test_validate_ignores_missing_visual_assets_for_disabled_steps(tmp_path: Path):
    proj = tmp_path / "p"
    (proj / "macros").mkdir(parents=True)

    (proj / "macros" / "main.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "main",
                "steps": [
                    {"type": "ImageSearch", "needle_path": "assets/missing.png", "enabled": False},
                    {"type": "Return", "value_expr": "'OK'", "out_var": "return_value"},
                ],
            }
        )
    )

    (proj / "project.yaml").write_text(
        yaml.safe_dump({"name": "p", "macros": {"main": "macros/main.yaml"}})
    )

    result = runner.invoke(app, ["validate", str(proj)])
    assert result.exit_code == 0, result.output


def test_validate_allows_valid_visual_assets(tmp_path: Path):
    proj = tmp_path / "p"
    (proj / "macros").mkdir(parents=True)

    _write_png(proj / "assets" / "ok.png")

    (proj / "macros" / "main.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "main",
                "steps": [
                    {"type": "VisualAssert", "baseline_path": "assets/ok.png"},
                    {"type": "Return", "value_expr": "'OK'", "out_var": "return_value"},
                ],
            }
        )
    )

    (proj / "project.yaml").write_text(
        yaml.safe_dump({"name": "p", "macros": {"main": "macros/main.yaml"}})
    )

    result = runner.invoke(app, ["validate", str(proj)])
    assert result.exit_code == 0, result.output


def test_validate_warns_on_invalid_asset_metadata(tmp_path: Path):
    proj = tmp_path / "p"
    (proj / "macros").mkdir(parents=True)

    png = proj / "assets" / "ok.png"
    _write_png(png)
    (proj / "assets" / "ok.json").write_text("{ not json }")

    (proj / "macros" / "main.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "main",
                "steps": [
                    {"type": "VisualVerify", "baseline_path": "assets/ok.png"},
                    {"type": "Return", "value_expr": "'OK'", "out_var": "return_value"},
                ],
            }
        )
    )

    (proj / "project.yaml").write_text(
        yaml.safe_dump({"name": "p", "macros": {"main": "macros/main.yaml"}})
    )

    result = runner.invoke(app, ["validate", str(proj)])
    assert result.exit_code == 0, result.output
    assert "invalid asset metadata json" in result.output
