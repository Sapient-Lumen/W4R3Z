from __future__ import annotations

import json
import zipfile
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.project.bundle import bundle_project, inspect_bundle


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "proj"
    (project_dir / "macros").mkdir(parents=True)

    (project_dir / "macros" / "reply.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "reply",
                "steps": [
                    {"type": "PromptForm", "title": "Reply", "fields": [{"name": "name", "label": "Name"}]},
                    {"type": "TypeText", "text": "Hello ${reply.name}"},
                ],
            },
            sort_keys=False,
        )
    )

    (project_dir / "macros" / "vision.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "vision",
                "steps": [
                    {"type": "WaitForImage", "needle_path": "assets/button.png", "timeout_ms": 5000},
                    {"type": "MouseClickAt", "x": 100, "y": 200},
                ],
            },
            sort_keys=False,
        )
    )

    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj",
                "settings": {"desktop_backend": "wayland"},
                "bindings": [{"keys": "Mod4+V", "macro": "vision"}],
                "hotstrings": [{"trigger": ":reply", "macro": "reply"}],
            },
            sort_keys=False,
        )
    )
    return project_dir



def test_bundle_manifest_embeds_claim_snapshot_when_claims_exist(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    for cmd in ["gen-operator-pack", "gen-verification-pack", "gen-portability-pack", "gen-claim-pack"]:
        res = runner.invoke(app, [cmd, str(project_dir), "--no-session-check", "--force", "--quiet"])
        assert res.exit_code == 0, res.output

    out = tmp_path / "proj.zip"
    bundle_project(project_dir, out)

    with zipfile.ZipFile(out, "r") as z:
        manifest = json.loads(z.read("vhk_bundle_manifest.json").decode("utf-8"))

    support = manifest["bundle_support_metadata"]
    assert support["claim_source"] == "claims_file"
    assert support["claims_file_present"] is True
    assert support["target_count"] >= 1
    assert any(item["target"] == "x11-i3" for item in support["targets"])
    assert any(item["status"] in {"pass", "warning"} for item in support["targets"])
    assert support["release_lane_overview"]["lane_count"] >= 1
    assert support["release_lane_pack_present"] in {True, False}
    assert support["release_deploy_overview"]["lane_count"] >= 1
    assert support["release_deploy_pack_present"] in {True, False}



def test_inspect_bundle_json_reports_support_snapshot(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    out = tmp_path / "proj.zip"
    bundle_project(project_dir, out)

    payload = inspect_bundle(out)
    assert payload["project_dir_name"] == "proj"
    assert payload["support"]["claim_source"] == "planner_recommendations"
    assert payload["support"]["target_count"] >= 1
    assert payload["support"]["release_lane_overview"]["lane_count"] >= 1
    assert payload["support"]["release_deploy_overview"]["lane_count"] >= 1

    res = runner.invoke(app, ["inspect-bundle", str(out), "--json"])
    assert res.exit_code == 0, res.output
    cli_payload = json.loads(res.output)
    assert cli_payload["support"]["claim_source"] == "planner_recommendations"
    assert any(item["claim_level"] for item in cli_payload["support"]["targets"])
    assert cli_payload["support"]["release_lane_overview"]["flagship_lane_id"]
    assert cli_payload["support"]["release_deploy_overview"]["flagship_lane_id"]


def test_bundle_stage_cli_reports_release_stage_snapshot(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    out = tmp_path / "stage.zip"

    res = runner.invoke(
        app,
        [
            "bundle-stage",
            str(project_dir),
            str(out),
            "--target-profile",
            "gnome-wayland",
        ],
    )
    assert res.exit_code == 0, res.output

    res = runner.invoke(app, ["inspect-bundle", str(out), "--json"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.output)
    assert payload["bundle_kind"] == "release-stage"
    assert payload["bundle_root_name"] == "gnome-wayland"
    assert payload["release_stage"]["profile_id"] == "gnome-wayland"
    assert payload["release_stage"]["release_level"] in {"reference", "supported", "caveated", "experimental"}
