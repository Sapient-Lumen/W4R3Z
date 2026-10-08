from __future__ import annotations

import json
import subprocess
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
                    {"type": "TypeText", "text": "Hello there, this is a Linux-native reply snippet with enough text to trigger planner promotion guidance."},
                ],
            },
            sort_keys=False,
        )
    )

    (project_dir / "macros" / "remap.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "remap",
                "steps": [
                    {"type": "Key", "keys": "ctrl+c"},
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

    (project_dir / "macros" / "sync.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "sync",
                "steps": [
                    {"type": "WaitForBusEvent", "event": "proj.sync", "timeout_ms": 1000},
                    {"type": "TypeText", "text": "synced"},
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
                "bindings": [
                    {"keys": "Mod4+R", "macro": "remap"},
                    {"keys": "Mod4+V", "macro": "vision"},
                ],
                "hotstrings": [{"trigger": ":reply", "macro": "reply"}],
                "bus_watchers": [{"name": "refresh", "event": "proj.sync", "macro": "sync"}],
            },
            sort_keys=False,
        )
    )
    return project_dir


def test_gen_promotion_pack_writes_expected_artifacts(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = project_dir / "docs"
    scripts_dir = project_dir / "scripts"

    res = runner.invoke(app, ["gen-promotion-pack", str(project_dir), "--no-session-check", "--quiet"])
    assert res.exit_code == 0, res.output

    promotion_doc = (docs_dir / "VHK_PROMOTION_PLAN.md").read_text()
    fixups_doc = (docs_dir / "VHK_PROMOTION_FIXUPS.md").read_text()
    backlog_doc = (docs_dir / "VHK_PROMOTION_BACKLOG.md").read_text()
    evidence_doc = (docs_dir / "VHK_PROMOTION_EVIDENCE.md").read_text()
    plan = json.loads((docs_dir / "VHK_PROMOTION_PLAN.json").read_text())
    refresh_script = (scripts_dir / "vhk_review_promotion_plan.sh").read_text()

    assert "# VHK promotion plan for proj" in promotion_doc
    assert "## Promotion shipping lanes" in promotion_doc
    assert "## Promotion startup routes" in promotion_doc
    assert "Text surface shipping lane" in promotion_doc
    assert "Text surface startup route" in promotion_doc
    assert "Shipping posture: `flagship`" in promotion_doc
    assert "Primary input lane: `clipboard-text-lane`" in promotion_doc
    assert "## Promotion waves" in promotion_doc
    assert "Wave 1 — promote specialist export lanes" in promotion_doc
    assert "## Promotion readiness" in promotion_doc
    assert "## Promotion gates" in promotion_doc
    assert "## Promotion backlog" in promotion_doc
    assert "Specialist surface gate" in promotion_doc
    assert "Text package candidate" in promotion_doc
    assert "Watcher service candidate" in promotion_doc

    assert "# VHK promotion fixups for proj" in fixups_doc
    assert "## High-priority promotions" in fixups_doc
    assert "## Promotion readiness reviews" in fixups_doc
    assert "## Promotion gates needing attention" in fixups_doc
    assert "## Backlog tasks to run now" in fixups_doc
    assert "`text-package-export`" in fixups_doc
    assert "## Helper-boundary surfaces" in fixups_doc

    assert "# VHK promotion backlog for proj" in backlog_doc
    assert "## Queue summary" in backlog_doc
    assert "## Tasks" in backlog_doc
    assert "surface:text-package-export" in backlog_doc
    assert "gate:claim-discipline-gate" in backlog_doc

    assert "# VHK promotion evidence for proj" in evidence_doc
    assert "## Evidence summary" in evidence_doc
    assert "## Evidence entries" in evidence_doc
    assert "## Promotion operator controls" in promotion_doc
    assert "## Promotion recovery lanes" in promotion_doc
    assert "## Promotion verification lanes" in promotion_doc
    assert "## Promotion performance envelopes" in promotion_doc
    assert "## Promotion dispatch budgets" in promotion_doc
    assert "## Promotion authority envelopes" in promotion_doc
    assert "surface:text-package-export" in evidence_doc
    assert "gate:claim-discipline-gate" in evidence_doc

    assert plan["project"]["name"] == "proj"
    assert plan["source_contract"] == "promotion_pack"
    assert plan["promotion_summary"]["high_priority_surface_count"] >= 2
    assert plan["promotion_summary"]["shipping_lane_count"] >= 3
    assert plan["promotion_summary"]["flagship_shipping_lane_count"] >= 1
    assert plan["promotion_summary"]["activation_route_count"] >= 3
    assert plan["promotion_summary"]["resident_activation_route_count"] >= 1
    assert "clipboard-text-lane" in plan["promotion_summary"]["primary_shipping_lane_ids"]
    assert plan["promotion_summary"]["review_surface_count"] >= 1
    assert plan["promotion_summary"]["gate_count"] >= 3
    assert plan["promotion_summary"]["review_gate_count"] + plan["promotion_summary"]["failing_gate_count"] >= 1
    assert plan["promotion_summary"]["backlog_task_count"] >= 4
    assert plan["promotion_summary"]["evidence_entry_count"] >= 4
    assert plan["promotion_summary"]["partial_evidence_count"] + plan["promotion_summary"]["missing_evidence_count"] >= 1
    assert any(item["priority"] == "high" and "text-package-export" in item["export_surface_ids"] for item in plan["promotion_waves"])
    assert any(item["export_surface_id"] == "helper-route-dossier" for item in plan["export_promotion_plan"])
    assert any(item["export_surface_id"] == "text-package-export" and item["primary_input_lane_id"] == "clipboard-text-lane" for item in plan["promotion_input_lane_plan"])
    assert any(item["export_surface_id"] == "text-package-export" and item["primary_activation_route_id"] == "text-surface-route" for item in plan["promotion_activation_route_plan"])
    assert any(item["export_surface_id"] == "text-package-export" and item["primary_control_lane_id"] == "text-service-control" for item in plan["promotion_operator_control_plan"])
    assert any(item["export_surface_id"] == "text-package-export" and item["primary_recovery_lane_id"] == "text-service-recovery" for item in plan["promotion_recovery_plan"])
    assert any(item["export_surface_id"] == "text-package-export" and item["primary_verification_lane_id"] == "text-surface-verification" for item in plan["promotion_verification_plan"])
    assert any(item["export_surface_id"] == "text-package-export" and item["primary_performance_lane_id"] == "clipboard-text-throughput" for item in plan["promotion_performance_plan"])
    assert any(item["export_surface_id"] == "text-package-export" and item["primary_dispatch_lane_id"] == "resident-text-service" for item in plan["promotion_dispatch_budget_plan"])
    assert any(item["export_surface_id"] == "text-package-export" and item["primary_authority_lane_id"] == "session-text-service-authority" for item in plan["promotion_authority_envelope_plan"])
    assert plan["promotion_input_lane_summary"]["flagship_count"] >= 1
    assert plan["promotion_activation_route_summary"]["resident_count"] >= 1
    assert plan["promotion_operator_control_summary"]["service_managed_count"] >= 1
    assert plan["promotion_recovery_summary"]["service_restart_count"] >= 1
    assert plan["promotion_verification_summary"]["service_smoke_count"] >= 1
    assert plan["promotion_performance_summary"]["throughput_first_count"] >= 1
    assert plan["promotion_summary"]["dispatch_budget_count"] >= 4
    assert plan["promotion_summary"]["authority_envelope_count"] >= 4
    assert plan["promotion_summary"]["service_resident_dispatch_count"] >= 1
    assert "resident-text-service" in plan["promotion_summary"]["primary_dispatch_budget_lane_ids"]
    assert "session-text-service-authority" in plan["promotion_summary"]["primary_authority_lane_ids"]
    assert "text-service-control" in plan["promotion_summary"]["primary_operator_control_lane_ids"]
    assert "text-service-recovery" in plan["promotion_summary"]["primary_recovery_lane_ids"]
    assert "text-surface-verification" in plan["promotion_summary"]["primary_verification_lane_ids"]
    assert "clipboard-text-throughput" in plan["promotion_summary"]["primary_performance_lane_ids"]
    assert any(item["export_surface_id"] == "text-package-export" for item in plan["promotion_readiness"])
    assert any(item["gate_id"] == "claim-discipline-gate" for item in plan["promotion_gates"])
    assert any(item["task_id"] == "surface:text-package-export" for item in plan["promotion_backlog"])
    assert any(item["task_id"] == "gate:claim-discipline-gate" for item in plan["promotion_backlog"])

    assert refresh_script.startswith("#!/usr/bin/env sh\n")
    assert "Collecting VHK promotion evidence" in refresh_script
    assert "vhk gen-promotion-pack . --force --quiet" in refresh_script


def test_gen_promotion_pack_can_select_outputs_and_refresh_script_runs(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = tmp_path / "promotion-docs"
    scripts_dir = tmp_path / "promotion-scripts"

    res = runner.invoke(
        app,
        [
            "gen-promotion-pack",
            str(project_dir),
            "--out-dir",
            str(docs_dir),
            "--script-dir",
            str(scripts_dir),
            "--no-session-check",
            "--no-fixups-doc",
            "--force",
            "--quiet",
        ],
    )
    assert res.exit_code == 0, res.output

    assert (docs_dir / "VHK_PROMOTION_PLAN.md").exists()
    assert not (docs_dir / "VHK_PROMOTION_FIXUPS.md").exists()
    assert (docs_dir / "VHK_PROMOTION_BACKLOG.md").exists()
    assert (docs_dir / "VHK_PROMOTION_EVIDENCE.md").exists()
    assert (docs_dir / "VHK_PROMOTION_PLAN.json").exists()
    assert (scripts_dir / "vhk_review_promotion_plan.sh").exists()

    proc = subprocess.run(
        ["sh", str(scripts_dir / "vhk_review_promotion_plan.sh")],
        cwd=project_dir,
        env={"PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "Collecting VHK promotion evidence" in proc.stdout
    assert "Promotion review refresh complete." in proc.stdout


def test_gen_promotion_pack_surfaces_current_host_claim_witness(tmp_path: Path, monkeypatch) -> None:
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

    res = runner.invoke(app, ["gen-promotion-pack", str(project_dir), "--force", "--quiet"])
    assert res.exit_code == 0, res.output

    promotion_doc = (project_dir / "docs" / "VHK_PROMOTION_PLAN.md").read_text()
    fixups_doc = (project_dir / "docs" / "VHK_PROMOTION_FIXUPS.md").read_text()
    backlog_doc = (project_dir / "docs" / "VHK_PROMOTION_BACKLOG.md").read_text()
    evidence_doc = (project_dir / "docs" / "VHK_PROMOTION_EVIDENCE.md").read_text()
    plan = json.loads((project_dir / "docs" / "VHK_PROMOTION_PLAN.json").read_text())
    refresh_script = (project_dir / "scripts" / "vhk_review_promotion_plan.sh").read_text()

    assert "## Promotion shipping lanes" in promotion_doc
    assert "## Current host claim witness" in promotion_doc
    assert "XDG_CURRENT_DESKTOP: `sway`" in promotion_doc
    assert plan["promotion_claim_witness"]["status"] == "review"
    assert plan["promotion_summary"]["current_host_proof_status"] == "review"
    assert any(item["gate_id"] == "current-host-proof-gate" and item["status"] == "review" for item in plan["promotion_gates"])
    assert any(item["task_id"] == "gate:current-host-proof-gate" for item in plan["promotion_backlog"])
    assert any(item["evidence_id"] == "gate:current-host-proof-gate" for item in plan["promotion_evidence"])
    assert "## Current-host proof drift" in fixups_doc
    assert "Resolve current-host proof posture" in backlog_doc
    assert "Current-host proof gate evidence" in evidence_doc
    assert "vhk gen-claim-pack . --force --quiet" in refresh_script


def test_gen_promotion_pack_can_pin_explicit_evidence_lane(tmp_path: Path, monkeypatch) -> None:
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

    res = runner.invoke(app, ["gen-promotion-pack", str(project_dir), "--force", "--quiet", "--evidence-lane", "gnome-wayland"])
    assert res.exit_code == 0, res.output

    plan = json.loads((project_dir / "docs" / "VHK_PROMOTION_PLAN.json").read_text())
    doc = (project_dir / "docs" / "VHK_PROMOTION_PLAN.md").read_text()
    refresh = (project_dir / "scripts" / "vhk_review_promotion_plan.sh").read_text()

    assert plan["selected_evidence_lane"]["profile_id"] == "gnome-wayland"
    assert plan["evidence_lane_fit"]["status"] == "drifted"
    assert plan["promotion_summary"]["selected_evidence_lane_id"] == "gnome-wayland"
    assert "Selected evidence lane: `gnome-wayland`" in doc
    assert "--evidence-lane gnome-wayland" in refresh
