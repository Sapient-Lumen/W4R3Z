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
                "bus_watchers": [{"name": "refresh", "event": "proj.refresh", "macro": "vision"}],
            },
            sort_keys=False,
        )
    )
    (project_dir / "docs").mkdir(exist_ok=True)
    (project_dir / "docs" / "VHK_TARGET_CLAIMS.yaml").write_text(
        yaml.safe_dump(
            {
                "target_claims": [
                    {
                        "target": "gnome-wayland",
                        "title": "GNOME Wayland",
                        "claim_level": "caveated",
                        "maintainer_notes": "Reviewed lane only.",
                        "evidence_status": "planned",
                    }
                ]
            },
            sort_keys=False,
        )
    )
    return project_dir


def test_gen_capability_audit_pack_writes_expected_artifacts(tmp_path: Path, monkeypatch) -> None:
    project_dir = _make_project(tmp_path)
    capability_matrix = {
        "screen_capture": {"status": "ok", "recommended": "portal:Screenshot", "mechanisms": ["portal:Screenshot"], "notes": [], "portal_backends": ["gnome"]},
        "text_injection": {"status": "limited", "recommended": None, "mechanisms": ["portal:RemoteDesktop(keyboard)"], "notes": ["interactive path"], "portal_backends": ["gnome"]},
        "pointer_injection": {"status": "limited", "recommended": "ydotool", "mechanisms": ["ydotool", "portal:RemoteDesktop(pointer)"], "notes": ["helper-backed"], "portal_backends": ["gnome"]},
        "global_hotkeys": {"status": "ok", "recommended": "portal:GlobalShortcuts", "mechanisms": ["portal:GlobalShortcuts"], "notes": [], "portal_backends": ["gnome"]},
        "input_capture": {"status": "limited", "recommended": None, "mechanisms": ["portal:InputCapture"], "notes": ["trigger-based"], "portal_backends": ["gnome"]},
    }
    host_snapshot = {
        "helpers": {
            "espanso": "/usr/bin/espanso",
            "ydotool": "/usr/bin/ydotool",
            "keyd": "/usr/bin/keyd",
            "kanata": None,
            "kmonad": None,
            "xremap": None,
        },
        "uinput": {"can_write": False, "status": "permission_denied"},
        "input_event_access": {"status": "permission_denied", "device_count": 2, "readable_count": 0, "readable_paths": []},
        "user_groups": {"status": "partial", "group_names": ["input"]},
        "ydotool_socket": {"status": "missing"},
        "xdg_portal_backend_config": {"status": "config_missing"},
        "service_units": {
            "user:espanso.service": {"unit": "espanso.service", "scope": "user", "status": "ok", "active_state": "active", "load_state": "loaded"},
            "system:keyd.service": {"unit": "keyd.service", "scope": "system", "status": "ok", "active_state": "active", "load_state": "loaded"},
        },
    }
    monkeypatch.setattr(cli_mod, "_validation_session_capability_matrix", lambda: capability_matrix)
    monkeypatch.setattr(cli_mod, "_validation_live_readiness_snapshot", lambda requirements=None: host_snapshot)

    res = runner.invoke(app, ["gen-capability-audit-pack", str(project_dir), "--quiet", "--force"])
    assert res.exit_code == 0, res.output

    audit_doc = (project_dir / "docs" / "VHK_CAPABILITY_AUDIT.md").read_text()
    fixups_doc = (project_dir / "docs" / "VHK_CAPABILITY_FIXUPS.md").read_text()
    plan = json.loads((project_dir / "docs" / "VHK_CAPABILITY_AUDIT_PLAN.json").read_text())
    refresh = (project_dir / "scripts" / "vhk_refresh_capability_audit_pack.sh").read_text()

    assert "# VHK capability audit for proj" in audit_doc
    assert "## Input lane dossier" in audit_doc
    assert "## Promotion lane plan" in audit_doc
    assert "## Promotion startup routes" in audit_doc
    assert "## Promotion operator controls" in audit_doc
    assert "## Promotion recovery lanes" in audit_doc
    assert "## Promotion performance envelopes" in audit_doc
    assert "## Promotion dispatch budgets" in audit_doc
    assert "## Capability lanes" in audit_doc
    assert "## Portal and session routing audit" in audit_doc
    assert "## Fallback routes" in audit_doc
    assert "## Claim posture" in audit_doc

    assert "# VHK capability fixups for proj" in fixups_doc
    assert "## Blocked queue" in fixups_doc
    assert "## Degraded queue" in fixups_doc
    assert "## Fallback route reminders" in fixups_doc

    assert plan["source_contract"] == "capability_audit_pack"
    assert plan["input_lane_dossier"]["lanes"]
    assert plan["promotion_input_lane_plan"]
    assert plan["promotion_activation_route_plan"]
    assert plan["promotion_operator_control_plan"]
    assert plan["promotion_recovery_plan"]
    assert plan["promotion_verification_plan"]
    assert plan["promotion_performance_plan"]
    assert plan["promotion_dispatch_budget_plan"]
    assert plan["promotion_authority_envelope_plan"]
    assert plan["project"]["name"] == "proj"
    assert plan["capability_audit_summary"]["overall_status"] in {"blocked", "degraded"}
    assert any(item["capability"] == "pointer_injection" for item in plan["capability_lanes"])
    assert any(item["title"] in {"Persistent ydotool daemon", "uinput / raw-input permissions", "Remapper lifecycle and placement"} for item in plan["helper_boundaries"])
    assert plan["claim_audit"]["summary"]["claims"] == 1
    assert "Current-host fit" in audit_doc
    assert any(item.get("current_host_fit") for item in plan["claim_audit"]["results"])

    assert refresh.startswith("#!/usr/bin/env sh\n")
    assert "vhk gen-capability-audit-pack" in refresh

    root = project_dir / "build" / "capability-audit" / "proj"
    assert (root / "README.md").exists()
    assert (root / "vhk_capability_audit_handoff.json").exists()
    assert (root / "collect_capability_audit.sh").exists()

    handoff = json.loads((root / "vhk_capability_audit_handoff.json").read_text())
    assert handoff["summary"]["overall_status"] in {"blocked", "degraded"}
    assert handoff["paths"]["doctor_json"] == "build/capability-audit/proj/reports/latest/reports/doctor.json"

    collect = (root / "collect_capability_audit.sh").read_text()
    assert 'vhk doctor --json > "$REPORTS_DIR/doctor.json" || true' in collect
    assert 'vhk gen-host-contract-pack "$PROJECT_DIR" --out-dir "$DOCS_DIR" --script-dir "$SCRIPTS_DIR" --force --quiet || true' in collect
    assert 'vhk gen-capability-audit-pack "$PROJECT_DIR" --out-dir "$DOCS_DIR" --script-dir "$SCRIPTS_DIR" --build-root "$REPORT_ROOT/build" --force --quiet || true' in collect


def test_gen_capability_audit_pack_can_select_outputs(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = tmp_path / "audit-docs"
    scripts_dir = tmp_path / "audit-scripts"
    build_dir = tmp_path / "audit-build"

    res = runner.invoke(
        app,
        [
            "gen-capability-audit-pack",
            str(project_dir),
            "--out-dir",
            str(docs_dir),
            "--script-dir",
            str(scripts_dir),
            "--build-root",
            str(build_dir),
            "--no-audit-check",
            "--no-fixups-doc",
            "--force",
            "--quiet",
        ],
    )
    assert res.exit_code == 0, res.output

    assert (docs_dir / "VHK_CAPABILITY_AUDIT.md").exists()
    assert (docs_dir / "VHK_CAPABILITY_AUDIT_PLAN.json").exists()
    assert not (docs_dir / "VHK_CAPABILITY_FIXUPS.md").exists()
    assert (scripts_dir / "vhk_refresh_capability_audit_pack.sh").exists()
    assert (build_dir / "README.md").exists()
    assert (build_dir / "collect_capability_audit.sh").exists()


def test_gen_capability_audit_pack_can_pin_explicit_evidence_lane(tmp_path: Path, monkeypatch) -> None:
    project_dir = _make_project(tmp_path)
    capability_matrix = {
        "screen_capture": {"status": "ok", "recommended": "portal:Screenshot", "mechanisms": ["portal:Screenshot"], "notes": [], "portal_backends": ["gnome"]},
        "text_injection": {"status": "limited", "recommended": None, "mechanisms": ["portal:RemoteDesktop(keyboard)"], "notes": ["interactive path"], "portal_backends": ["gnome"]},
        "pointer_injection": {"status": "limited", "recommended": "ydotool", "mechanisms": ["ydotool", "portal:RemoteDesktop(pointer)"], "notes": ["helper-backed"], "portal_backends": ["gnome"]},
        "global_hotkeys": {"status": "ok", "recommended": "portal:GlobalShortcuts", "mechanisms": ["portal:GlobalShortcuts"], "notes": [], "portal_backends": ["gnome"]},
        "input_capture": {"status": "limited", "recommended": None, "mechanisms": ["portal:InputCapture"], "notes": ["trigger-based"], "portal_backends": ["gnome"]},
    }
    host_snapshot = {
        "helpers": {
            "espanso": "/usr/bin/espanso",
            "ydotool": "/usr/bin/ydotool",
            "keyd": "/usr/bin/keyd",
            "kanata": None,
            "kmonad": None,
            "xremap": None,
        },
        "uinput": {"can_write": False, "status": "permission_denied"},
        "input_event_access": {"status": "permission_denied", "device_count": 2, "readable_count": 0, "readable_paths": []},
        "user_groups": {"status": "partial", "group_names": ["input"]},
        "ydotool_socket": {"status": "missing"},
        "xdg_portal_backend_config": {"status": "config_missing"},
        "xdg_portal_backend_manifests": {"status": "ok_with_warnings", "xdg_current_desktop": "sway", "backends": []},
        "service_units": {
            "user:espanso.service": {"unit": "espanso.service", "scope": "user", "status": "ok", "active_state": "active", "load_state": "loaded"},
            "system:keyd.service": {"unit": "keyd.service", "scope": "system", "status": "ok", "active_state": "active", "load_state": "loaded"},
        },
    }
    monkeypatch.setattr(cli_mod, "_validation_session_capability_matrix", lambda: capability_matrix)
    monkeypatch.setattr(cli_mod, "_validation_live_readiness_snapshot", lambda requirements=None: host_snapshot)

    res = runner.invoke(app, ["gen-capability-audit-pack", str(project_dir), "--quiet", "--force", "--evidence-lane", "gnome-wayland"])
    assert res.exit_code == 0, res.output

    plan = json.loads((project_dir / "docs" / "VHK_CAPABILITY_AUDIT_PLAN.json").read_text())
    assert plan["claim_audit"]["selected_evidence_lane"]["profile_id"] == "gnome-wayland"
    assert plan["claim_audit"]["evidence_lane_fit"]["status"] == "drifted"
