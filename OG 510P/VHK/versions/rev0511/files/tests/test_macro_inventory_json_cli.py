from __future__ import annotations
from pathlib import Path
import json
import os
import yaml
from typer.testing import CliRunner
from vhk.cli import app
runner = CliRunner()

def _make_project(tmp_path: Path) -> Path:
    proj = tmp_path / "inv"
    (proj / "macros").mkdir(parents=True)
    (proj / "macros" / "alpha.yaml").write_text(yaml.safe_dump({"name": "alpha", "group": "editing", "tags": ["text"], "presets": [{"name": "quick", "tags": ["fast"], "vars": {"mode": "quick"}}], "steps": [{"type": "TypeText", "text": "hello"}, {"type": "I3Command", "command": "workspace next"}]}))
    (proj / "macros" / "beta.yaml").write_text(yaml.safe_dump({"name": "beta", "hidden": True, "tags": ["vision"], "steps": [{"type": "If", "condition": "True", "then_steps": [{"type": "CaptureScreenshot", "out_path": "shot.png"}], "else_steps": [{"type": "Return", "value_expr": '"noop"'}]}]}))
    (proj / "project.yaml").write_text(yaml.safe_dump({"name": "inv", "macros": {"alpha": "macros/alpha.yaml", "beta": "macros/beta.yaml"}}))
    return proj

def test_macro_inventory_json_reports_macro_metadata(tmp_path: Path):
    proj = _make_project(tmp_path)
    res = runner.invoke(app, ["macro-inventory-json", str(proj)])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["stack_kind"] == "vhk.project.macro_inventory"
    assert payload["project"]["macro_count"] == 2
    assert payload["project"]["hidden_macro_count"] == 1
    assert payload["project"]["preset_total"] == 1
    alpha = next(item for item in payload["macros"] if item["name"] == "alpha")
    assert alpha["preset_count"] == 1
    assert set(alpha["hints"]["capability_tags"]) >= {"text", "i3"}
    beta = next(item for item in payload["macros"] if item["name"] == "beta")
    assert beta["steps"]["total_count"] == 3
    assert "vision" in beta["hints"]["capability_tags"]


def test_macro_inventory_json_rolls_up_recording_drift_and_brittleness(tmp_path: Path):
    proj = _make_project(tmp_path)
    alpha_sidecar = proj / "macros" / "alpha.window-context.yaml"
    alpha_sidecar.write_text(yaml.safe_dump({
        "suggested": {"stable": {"class": "Alacritty"}},
        "segments": [
            {"selector_kind": "stable", "transition_reason": "focus", "relative_mouse_anchor": {"mode": "window"}},
            {"selector_kind": "exact", "transition_reason": "title"},
        ],
    }, sort_keys=False))
    beta_sidecar = proj / "macros" / "beta.window-context.yaml"
    beta_sidecar.write_text(yaml.safe_dump({"segments": [{"selector_kind": "stable", "transition_reason": "focus"}]}, sort_keys=False))
    os.utime(alpha_sidecar, (1000, 1000))
    os.utime(proj / "macros" / "alpha.yaml", (2000, 2000))
    os.utime(beta_sidecar, (3000, 3000))
    os.utime(proj / "macros" / "beta.yaml", (2000, 2000))

    res = runner.invoke(app, ["macro-inventory-json", str(proj)])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    project = payload["project"]
    assert project["recording_sidecar_count"] == 2
    assert project["recording_sidecar_missing_count"] == 0
    assert project["recording_sidecar_stale_count"] == 1
    assert project["recording_sidecar_newer_than_source_count"] == 1
    assert project["macros_with_exact_recording_segments"] == 1
    assert project["macros_with_title_recording_segments"] == 1
    assert project["window_relative_recording_macro_count"] == 1
    alpha = next(item for item in payload["macros"] if item["name"] == "alpha")
    assert alpha["source"]["recording_sidecar"]["freshness"]["status"] == "source_newer_than_recording"
    assert alpha["source"]["recording_sidecar"]["exact_segment_count"] == 1
    beta = next(item for item in payload["macros"] if item["name"] == "beta")
    assert beta["source"]["recording_sidecar"]["freshness"]["status"] == "recording_newer_than_source"
