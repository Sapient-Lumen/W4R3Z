from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

import vhk.cli as cli_mod
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


def test_gen_claim_pack_surfaces_current_host_review_when_session_check_is_enabled(tmp_path: Path, monkeypatch) -> None:
    project_dir = _make_project(tmp_path)
    capability_matrix = {
        "screen_capture": {"status": "ok", "recommended": "portal:Screenshot", "mechanisms": ["portal:Screenshot"], "notes": [], "portal_backends": ["gnome"]},
        "text_injection": {"status": "limited", "recommended": None, "mechanisms": ["portal:RemoteDesktop(keyboard)"], "notes": ["interactive path"], "portal_backends": ["gnome"]},
        "pointer_injection": {"status": "ok", "recommended": "dotoolc", "mechanisms": ["dotoolc"], "notes": [], "portal_backends": ["gnome"]},
        "global_hotkeys": {"status": "ok", "recommended": "portal:GlobalShortcuts", "mechanisms": ["portal:GlobalShortcuts"], "notes": [], "portal_backends": ["gnome"]},
        "input_capture": {"status": "limited", "recommended": None, "mechanisms": ["portal:InputCapture"], "notes": ["trigger-based"], "portal_backends": ["gnome"]},
    }
    host_snapshot = {
        "helpers": {"espanso": "/usr/bin/espanso", "dotool": "/usr/bin/dotool", "dotoolc": "/usr/bin/dotoolc", "dotoold": "/usr/bin/dotoold", "ydotool": None},
        "uinput": {"can_write": False, "status": "permission_denied"},
        "ydotool_socket": {"status": "missing"},
        "xdg_portal_screenshot": {"status": "ok"},
        "xdg_portal_screencast": {"status": "ok"},
        "xdg_portal_global_shortcuts": {"status": "interface_missing"},
        "xdg_portal_remote_desktop": {"status": "interface_missing"},
        "xdg_portal_input_capture": {"status": "interface_missing"},
        "xdg_portal_backend_config": {"status": "config_missing"},
        "xdg_portal_backend_manifests": {"status": "ok_with_warnings", "xdg_current_desktop": "sway", "backends": []},
    }
    monkeypatch.setattr(cli_mod, "_validation_session_capability_matrix", lambda: capability_matrix)
    monkeypatch.setattr(cli_mod, "_validation_live_readiness_snapshot", lambda requirements=None: host_snapshot)

    res = runner.invoke(app, ["gen-claim-pack", str(project_dir), "--force", "--quiet"])
    assert res.exit_code == 0, res.output

    guide = (project_dir / "docs" / "VHK_CLAIM_GUIDE.md").read_text()
    plan = json.loads((project_dir / "docs" / "VHK_CLAIM_AUDIT_PLAN.json").read_text())

    assert "## Current host review" in guide
    assert "XDG_CURRENT_DESKTOP: `sway`" in guide
    gnome = next(item for item in plan["recommended_claims"] if item["target"] == "gnome-wayland")
    assert gnome["current_host_fit"]["status"] == "drifted"
    assert plan["claim_host_review"]["drifted_count"] >= 1


def test_audit_target_claims_fails_verified_reference_when_current_host_drifts(tmp_path: Path, monkeypatch) -> None:
    project_dir = _make_project(tmp_path)
    capability_matrix = {
        "screen_capture": {"status": "ok", "recommended": "portal:Screenshot", "mechanisms": ["portal:Screenshot"], "notes": [], "portal_backends": ["gnome"]},
        "text_injection": {"status": "limited", "recommended": None, "mechanisms": ["portal:RemoteDesktop(keyboard)"], "notes": ["interactive path"], "portal_backends": ["gnome"]},
        "pointer_injection": {"status": "ok", "recommended": "dotoolc", "mechanisms": ["dotoolc"], "notes": [], "portal_backends": ["gnome"]},
        "global_hotkeys": {"status": "ok", "recommended": "portal:GlobalShortcuts", "mechanisms": ["portal:GlobalShortcuts"], "notes": [], "portal_backends": ["gnome"]},
        "input_capture": {"status": "limited", "recommended": None, "mechanisms": ["portal:InputCapture"], "notes": ["trigger-based"], "portal_backends": ["gnome"]},
    }
    host_snapshot = {
        "helpers": {"espanso": "/usr/bin/espanso", "dotool": "/usr/bin/dotool", "dotoolc": "/usr/bin/dotoolc", "dotoold": "/usr/bin/dotoold", "ydotool": None},
        "uinput": {"can_write": False, "status": "permission_denied"},
        "ydotool_socket": {"status": "missing"},
        "xdg_portal_screenshot": {"status": "ok"},
        "xdg_portal_screencast": {"status": "ok"},
        "xdg_portal_global_shortcuts": {"status": "interface_missing"},
        "xdg_portal_remote_desktop": {"status": "interface_missing"},
        "xdg_portal_input_capture": {"status": "interface_missing"},
        "xdg_portal_backend_config": {"status": "config_missing"},
        "xdg_portal_backend_manifests": {"status": "ok_with_warnings", "xdg_current_desktop": "sway", "backends": []},
    }
    monkeypatch.setattr(cli_mod, "_validation_session_capability_matrix", lambda: capability_matrix)
    monkeypatch.setattr(cli_mod, "_validation_live_readiness_snapshot", lambda requirements=None: host_snapshot)

    for cmd in ["gen-operator-pack", "gen-verification-pack", "gen-portability-pack", "gen-claim-pack"]:
        res = runner.invoke(app, [cmd, str(project_dir), "--force", "--quiet"])
        assert res.exit_code == 0, res.output

    claims_file = project_dir / "docs" / "VHK_TARGET_CLAIMS.yaml"
    payload = yaml.safe_load(claims_file.read_text())
    for item in payload["target_claims"]:
        if item["target"] == "gnome-wayland":
            item["claim_level"] = "reference"
            item["maintainer_notes"] = "Treat this host run as verified GNOME proof."
            item["evidence_status"] = "verified"
            break
    claims_file.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True))

    res = runner.invoke(app, ["audit-target-claims", str(project_dir), "--json"])
    assert res.exit_code == 1, res.output
    payload = json.loads(res.output)
    gnome = next(item for item in payload["results"] if item["target"] == "gnome-wayland")
    assert gnome["status"] == "fail"
    assert gnome["current_host_fit"]["status"] == "drifted"
    assert any("Current host drifts from this target claim" in text for text in gnome["issues"])


def test_gen_claim_pack_can_pin_explicit_evidence_lane(tmp_path: Path, monkeypatch) -> None:
    project_dir = _make_project(tmp_path)
    capability_matrix = {
        "screen_capture": {"status": "ok", "recommended": "portal:Screenshot", "mechanisms": ["portal:Screenshot"], "notes": [], "portal_backends": ["gnome"]},
        "text_injection": {"status": "limited", "recommended": None, "mechanisms": ["portal:RemoteDesktop(keyboard)"], "notes": ["interactive path"], "portal_backends": ["gnome"]},
        "pointer_injection": {"status": "ok", "recommended": "dotoolc", "mechanisms": ["dotoolc"], "notes": [], "portal_backends": ["gnome"]},
        "global_hotkeys": {"status": "ok", "recommended": "portal:GlobalShortcuts", "mechanisms": ["portal:GlobalShortcuts"], "notes": [], "portal_backends": ["gnome"]},
        "input_capture": {"status": "limited", "recommended": None, "mechanisms": ["portal:InputCapture"], "notes": ["trigger-based"], "portal_backends": ["gnome"]},
    }
    host_snapshot = {
        "helpers": {"espanso": "/usr/bin/espanso", "dotool": "/usr/bin/dotool", "dotoolc": "/usr/bin/dotoolc", "dotoold": "/usr/bin/dotoold", "ydotool": None},
        "uinput": {"can_write": False, "status": "permission_denied"},
        "ydotool_socket": {"status": "missing"},
        "xdg_portal_screenshot": {"status": "ok"},
        "xdg_portal_screencast": {"status": "ok"},
        "xdg_portal_global_shortcuts": {"status": "interface_missing"},
        "xdg_portal_remote_desktop": {"status": "interface_missing"},
        "xdg_portal_input_capture": {"status": "interface_missing"},
        "xdg_portal_backend_config": {"status": "config_missing"},
        "xdg_portal_backend_manifests": {"status": "ok_with_warnings", "xdg_current_desktop": "sway", "backends": []},
    }
    monkeypatch.setattr(cli_mod, "_validation_session_capability_matrix", lambda: capability_matrix)
    monkeypatch.setattr(cli_mod, "_validation_live_readiness_snapshot", lambda requirements=None: host_snapshot)

    res = runner.invoke(app, ["gen-claim-pack", str(project_dir), "--force", "--quiet", "--evidence-lane", "gnome-wayland"])
    assert res.exit_code == 0, res.output

    guide = (project_dir / "docs" / "VHK_CLAIM_GUIDE.md").read_text()
    plan = json.loads((project_dir / "docs" / "VHK_CLAIM_AUDIT_PLAN.json").read_text())
    script = (project_dir / "scripts" / "vhk_audit_claims.sh").read_text()

    assert plan["selected_evidence_lane"]["profile_id"] == "gnome-wayland"
    assert plan["evidence_lane_fit"]["status"] == "drifted"
    assert plan["evidence_lane_fit"]["selection_source"] == "explicit"
    assert "Selected evidence lane: `gnome-wayland`" in guide
    assert "--evidence-lane gnome-wayland" in script
