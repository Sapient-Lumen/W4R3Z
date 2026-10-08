from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "proj"
    (project_dir / "macros").mkdir(parents=True)

    (project_dir / "macros" / "reply.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "reply",
                "presets": [{"name": "support", "vars": {"team": "support"}}],
                "steps": [
                    {
                        "type": "PromptForm",
                        "title": "Reply",
                        "fields": [{"name": "name", "label": "Name"}],
                    },
                    {"type": "TypeText", "text": "Hello ${reply.name}"},
                    {"type": "Return", "value": "ok"},
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
                "bus_watchers": [{"name": "refresh", "event": "proj.refresh", "macro": "vision"}],
            },
            sort_keys=False,
        )
    )
    return project_dir



def test_gen_claim_pack_writes_expected_artifacts(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = project_dir / "docs"
    scripts_dir = project_dir / "scripts"

    res = runner.invoke(app, ["gen-claim-pack", str(project_dir), "--no-session-check", "--quiet"])
    assert res.exit_code == 0, res.output

    guide = (docs_dir / "VHK_CLAIM_GUIDE.md").read_text()
    claims = yaml.safe_load((docs_dir / "VHK_TARGET_CLAIMS.yaml").read_text())
    plan = json.loads((docs_dir / "VHK_CLAIM_AUDIT_PLAN.json").read_text())
    script = (scripts_dir / "vhk_audit_claims.sh").read_text()

    assert "# VHK claim guide for proj" in guide
    assert "## Claim level glossary" in guide
    assert "## Recommended target claims" in guide
    assert "## Claim audit commands" in guide
    assert "capability-agnostic" in guide

    assert claims["schema"] == "vhk.target_claims.v1"
    assert claims["project"]["name"] == "proj"
    assert claims["target_claims"]
    assert any(item["target"] == "x11-i3" for item in claims["target_claims"])

    assert plan["project"]["name"] == "proj"
    assert plan["recommended_claims"]
    assert plan["claim_commands"]
    assert plan["claim_levels"]["supported"]

    assert script.startswith("#!/usr/bin/env sh\n")
    assert "vhk gen-claim-pack . --out-dir" in script
    assert "vhk audit-target-claims ." in script



def test_gen_claim_pack_can_select_outputs(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = tmp_path / "claim-docs"
    scripts_dir = tmp_path / "claim-scripts"

    res = runner.invoke(
        app,
        [
            "gen-claim-pack",
            str(project_dir),
            "--out-dir",
            str(docs_dir),
            "--script-dir",
            str(scripts_dir),
            "--no-session-check",
            "--no-guide",
            "--no-script",
            "--force",
            "--quiet",
        ],
    )
    assert res.exit_code == 0, res.output

    assert not (docs_dir / "VHK_CLAIM_GUIDE.md").exists()
    assert (docs_dir / "VHK_TARGET_CLAIMS.yaml").exists()
    assert (docs_dir / "VHK_CLAIM_AUDIT_PLAN.json").exists()
    assert not (scripts_dir / "vhk_audit_claims.sh").exists()



def test_audit_target_claims_reports_failures_for_overclaims(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    for cmd in ["gen-operator-pack", "gen-verification-pack", "gen-portability-pack", "gen-claim-pack"]:
        res = runner.invoke(app, [cmd, str(project_dir), "--no-session-check", "--force", "--quiet"])
        assert res.exit_code == 0, res.output

    claims_file = project_dir / "docs" / "VHK_TARGET_CLAIMS.yaml"
    payload = yaml.safe_load(claims_file.read_text())
    for item in payload["target_claims"]:
        if item["target"] == "portable-text":
            item["claim_level"] = "reference"
            item["maintainer_notes"] = "Pretend this is fully supported everywhere."
            item["evidence_status"] = "verified"
            break
    claims_file.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True))

    res = runner.invoke(app, ["audit-target-claims", str(project_dir), "--no-session-check", "--json"])
    assert res.exit_code == 1, res.output
    payload = json.loads(res.output)
    overclaim = next(item for item in payload["results"] if item["target"] == "portable-text")
    assert overclaim["status"] == "fail"
    assert any("stronger than the current recommendation" in text for text in overclaim["issues"])



def test_audit_target_claims_passes_with_generated_claims(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    for cmd in ["gen-operator-pack", "gen-verification-pack", "gen-portability-pack", "gen-claim-pack"]:
        res = runner.invoke(app, [cmd, str(project_dir), "--no-session-check", "--force", "--quiet"])
        assert res.exit_code == 0, res.output

    res = runner.invoke(app, ["audit-target-claims", str(project_dir), "--no-session-check", "--json"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.output)
    assert payload["summary"]["claims"] >= 1
    assert payload["summary"]["fail"] == 0
    assert any(item["status"] in {"pass", "warning"} for item in payload["results"])
