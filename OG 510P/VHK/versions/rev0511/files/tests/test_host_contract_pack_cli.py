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
    return project_dir



def test_plan_project_includes_host_requirements(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(app, ["plan-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)

    requirement_ids = {item["id"] for item in data["host_requirements"]}
    assert "text-surface-service" in requirement_ids
    assert "watcher-user-service" in requirement_ids
    assert "dotool-daemon" in requirement_ids
    assert "uinput-permissions" in requirement_ids
    assert "portal-global-shortcuts" in requirement_ids
    assert "portal-backend-config" in requirement_ids
    assert "keyd-remapper-service" in requirement_ids
    assert "xremap-remapper-service" in requirement_ids

    dotool_req = next(item for item in data["host_requirements"] if item["id"] == "dotool-daemon")
    ydotool_req = next(item for item in data["host_requirements"] if item["id"] == "ydotool-daemon")
    assert dotool_req["alternative_group"] == "wayland-uinput-helper-daemon"
    assert ydotool_req["alternative_group"] == "wayland-uinput-helper-daemon"
    assert dotool_req["alternative_policy"] == "one_of"
    assert ydotool_req["alternative_policy"] == "one_of"



def test_gen_host_contract_pack_writes_expected_artifacts(tmp_path: Path, monkeypatch) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = project_dir / "docs"
    scripts_dir = project_dir / "scripts"

    capability_matrix = {
        "screen_capture": {"status": "ok", "recommended": "portal:Screenshot", "mechanisms": ["portal:Screenshot"], "notes": [], "portal_backends": ["gnome"]},
        "text_injection": {"status": "limited", "recommended": None, "mechanisms": ["portal:RemoteDesktop(keyboard)"], "notes": ["interactive path"], "portal_backends": ["gnome"]},
        "pointer_injection": {"status": "ok", "recommended": "dotoolc", "mechanisms": ["dotoolc"], "notes": [], "portal_backends": ["gnome"]},
        "global_hotkeys": {"status": "ok", "recommended": "portal:GlobalShortcuts", "mechanisms": ["portal:GlobalShortcuts"], "notes": [], "portal_backends": ["gnome"]},
        "input_capture": {"status": "limited", "recommended": None, "mechanisms": ["portal:InputCapture"], "notes": ["trigger-based"], "portal_backends": ["gnome"]},
    }
    host_snapshot = {
        "helpers": {
            "espanso": "/usr/bin/espanso",
            "ydotool": None,
            "dotool": "/usr/bin/dotool",
            "dotoolc": "/usr/bin/dotoolc",
            "dotoold": "/usr/bin/dotoold",
            "keyd": None,
            "kanata": None,
            "kmonad": None,
            "xremap": None,
        },
        "uinput": {"can_write": False, "status": "permission_denied"},
        "ydotool_socket": {"status": "missing"},
        "xdg_portal_screenshot": {"status": "ok"},
        "xdg_portal_screencast": {"status": "ok"},
        "xdg_portal_global_shortcuts": {"status": "interface_missing"},
        "xdg_portal_remote_desktop": {"status": "interface_missing"},
        "xdg_portal_input_capture": {"status": "interface_missing"},
        "xdg_portal_backend_config": {"status": "config_missing"},
        "xdg_portal_backend_manifests": {
            "status": "ok_with_warnings",
            "xdg_current_desktop": "sway",
            "backends": [
                {
                    "backend": "gtk",
                    "manifest_path": "/usr/share/xdg-desktop-portal/portals/gtk.portal",
                    "interfaces": ["org.freedesktop.impl.portal.RemoteDesktop"],
                    "use_in": [],
                    "matching_desktops": [],
                    "usable_on_current_desktop": True,
                },
                {
                    "backend": "luminous",
                    "manifest_path": "/usr/share/xdg-desktop-portal/portals/luminous.portal",
                    "interfaces": [
                        "org.freedesktop.impl.portal.Screenshot",
                        "org.freedesktop.impl.portal.ScreenCast",
                        "org.freedesktop.impl.portal.InputCapture",
                    ],
                    "use_in": ["sway"],
                    "matching_desktops": ["sway"],
                    "usable_on_current_desktop": True,
                },
                {
                    "backend": "kde",
                    "manifest_path": "/usr/share/xdg-desktop-portal/portals/kde.portal",
                    "interfaces": ["org.freedesktop.impl.portal.GlobalShortcuts"],
                    "use_in": ["kde"],
                    "matching_desktops": [],
                    "usable_on_current_desktop": False,
                },
            ],
            "parse_errors": [{"path": "/usr/share/xdg-desktop-portal/portals/broken.portal", "status": "parse_failed", "error": "boom"}],
        },
        "service_units": {
            "user:dotoold.service": {"unit": "dotoold.service", "scope": "user", "status": "ok", "active_state": "active", "load_state": "loaded"},
        },
    }
    monkeypatch.setattr(cli_mod, "_validation_session_capability_matrix", lambda: capability_matrix)
    monkeypatch.setattr(cli_mod, "_validation_host_contract_snapshot", lambda: host_snapshot)

    res = runner.invoke(app, ["gen-host-contract-pack", str(project_dir), "--quiet"])
    assert res.exit_code == 0, res.output

    req_doc = (docs_dir / "VHK_HOST_REQUIREMENTS.md").read_text()
    fix_doc = (docs_dir / "VHK_HOST_FIXUPS.md").read_text()
    plan = json.loads((docs_dir / "VHK_HOST_PLAN.json").read_text())
    review_script = (scripts_dir / "vhk_review_host_contract.sh").read_text()

    assert "# VHK host requirements for proj" in req_doc
    assert "## Service lifecycle requirements" in req_doc
    assert "## Permission requirements" in req_doc
    assert "## Portal and session requirements" in req_doc
    assert "## Portal route contract" in req_doc
    assert "`RemoteDesktop` → live `interface_missing`" in req_doc

    assert "# VHK host fixups for proj" in fix_doc
    assert "## Capability lanes" in fix_doc
    assert "## Portal routing review" in fix_doc
    assert "pointer_injection" in fix_doc

    assert plan["project"]["name"] == "proj"
    assert plan["source_contract"] == "host_contract"
    assert plan["host_summary"]["overall_status"] == "blocked"
    assert "uinput-permissions" in plan["host_summary"]["blocked_requirements"]
    assert any(item["id"] == "portal-backend-config" and item["observed_status"] == "degraded" for item in plan["host_requirements"])
    assert any(item["id"] == "dotool-daemon" and item["observed_status"] == "ready" for item in plan["host_requirements"])
    assert any(item["id"] == "ydotool-daemon" and item["observed_status"] == "blocked" for item in plan["host_requirements"])
    assert plan["portal_route_contract"]["manifest_status"] == "ok_with_warnings"
    assert plan["portal_route_contract"]["status"] == "degraded"
    assert "luminous" in plan["portal_route_contract"]["installed_backends"]
    remote_route = next(item for item in plan["portal_route_contract"]["interfaces"] if item["short_name"] == "RemoteDesktop")
    assert remote_route["live_status"] == "interface_missing"
    assert remote_route["usable_backends"] == ["gtk"]

    alt_group = next(item for item in plan["alternative_requirement_groups"] if item["id"] == "wayland-uinput-helper-daemon")
    assert alt_group["effective_status"] == "ready"
    assert "dotool-daemon" in alt_group["active_member_ids"]
    assert alt_group["preferred_member_id"] == "dotool-daemon"
    assert alt_group["bootstrap_filter_id"] == "pointer-injection__dotool-daemon"
    dotool_member = next(item for item in alt_group["members"] if item["id"] == "dotool-daemon")
    assert dotool_member["bootstrap_filter_id"] == "pointer-injection__dotool-daemon"

    ydotool_req = next(item for item in plan["host_requirements"] if item["id"] == "ydotool-daemon")
    assert ydotool_req["suppressed_by_alternative"] is True
    assert ydotool_req["effective_observed_status"] == "covered"

    assert review_script.startswith("#!/usr/bin/env sh\n")
    assert "Collecting VHK host-contract evidence" in review_script
    assert "vhk doctor --json" in review_script



def test_gen_host_contract_pack_preserves_explicit_evidence_lane(tmp_path: Path, monkeypatch) -> None:
    project_dir = _make_project(tmp_path)

    capability_matrix = {
        "screen_capture": {"status": "ok", "recommended": "portal:Screenshot", "mechanisms": ["portal:Screenshot"], "notes": [], "portal_backends": ["gnome"]},
        "text_injection": {"status": "limited", "recommended": None, "mechanisms": ["portal:RemoteDesktop(keyboard)"], "notes": ["interactive path"], "portal_backends": ["gnome"]},
        "pointer_injection": {"status": "ok", "recommended": "dotoolc", "mechanisms": ["dotoolc"], "notes": [], "portal_backends": ["gnome"]},
        "global_hotkeys": {"status": "ok", "recommended": "portal:GlobalShortcuts", "mechanisms": ["portal:GlobalShortcuts"], "notes": [], "portal_backends": ["gnome"]},
        "input_capture": {"status": "limited", "recommended": None, "mechanisms": ["portal:InputCapture"], "notes": ["trigger-based"], "portal_backends": ["gnome"]},
    }
    host_snapshot = {
        "helpers": {"dotool": "/usr/bin/dotool", "dotoolc": "/usr/bin/dotoolc", "dotoold": "/usr/bin/dotoold"},
        "uinput": {"can_write": True, "status": "ok"},
        "xdg_portal_backend_config": {"status": "ok"},
        "service_units": {"user:dotoold.service": {"unit": "dotoold.service", "scope": "user", "status": "ok", "active_state": "active", "load_state": "loaded"}},
    }
    monkeypatch.setattr(cli_mod, "_validation_session_capability_matrix", lambda: capability_matrix)
    monkeypatch.setattr(cli_mod, "_validation_host_contract_snapshot", lambda: host_snapshot)

    res = runner.invoke(app, ["gen-host-contract-pack", str(project_dir), "--evidence-lane", "gnome-wayland", "--quiet"])
    assert res.exit_code == 0, res.output

    plan = json.loads((project_dir / "docs" / "VHK_HOST_PLAN.json").read_text())
    req_doc = (project_dir / "docs" / "VHK_HOST_REQUIREMENTS.md").read_text()
    fix_doc = (project_dir / "docs" / "VHK_HOST_FIXUPS.md").read_text()
    review_script = (project_dir / "scripts" / "vhk_review_host_contract.sh").read_text()

    assert plan["selected_evidence_lane"]["profile_id"] == "gnome-wayland"
    assert plan["selected_evidence_lane"]["selection_source"] == "explicit"
    assert plan["evidence_lane_fit"]["selection_source"] == "explicit"
    assert "Evidence lane: `gnome-wayland` (explicit)" in req_doc
    assert "Evidence lane fit:" in req_doc
    assert "Evidence lane: `gnome-wayland` (explicit)" in fix_doc
    assert "--evidence-lane gnome-wayland" in review_script


def test_host_contract_alternative_lane_does_not_block_when_one_helper_is_ready(tmp_path: Path, monkeypatch) -> None:
    project_dir = _make_project(tmp_path)

    capability_matrix = {
        "screen_capture": {"status": "ok", "recommended": "portal:Screenshot", "mechanisms": ["portal:Screenshot"], "notes": [], "portal_backends": ["gnome"]},
        "text_injection": {"status": "limited", "recommended": None, "mechanisms": ["portal:RemoteDesktop(keyboard)"], "notes": ["interactive path"], "portal_backends": ["gnome"]},
        "pointer_injection": {"status": "ok", "recommended": "dotoolc", "mechanisms": ["dotoolc"], "notes": [], "portal_backends": ["gnome"]},
        "global_hotkeys": {"status": "ok", "recommended": "portal:GlobalShortcuts", "mechanisms": ["portal:GlobalShortcuts"], "notes": [], "portal_backends": ["gnome"]},
        "input_capture": {"status": "limited", "recommended": None, "mechanisms": ["portal:InputCapture"], "notes": ["trigger-based"], "portal_backends": ["gnome"]},
    }
    host_snapshot = {
        "helpers": {
            "espanso": "/usr/bin/espanso",
            "ydotool": None,
            "dotool": "/usr/bin/dotool",
            "dotoolc": "/usr/bin/dotoolc",
            "dotoold": "/usr/bin/dotoold",
            "keyd": None,
            "kanata": None,
            "kmonad": None,
            "xremap": None,
        },
        "uinput": {"can_write": True, "status": "ok"},
        "xdg_portal_backend_config": {"status": "ok"},
        "service_units": {
            "user:espanso.service": {"unit": "espanso.service", "scope": "user", "status": "ok", "active_state": "active", "load_state": "loaded"},
            "user:vhk-busd.service": {"unit": "vhk-busd.service", "scope": "user", "status": "ok", "active_state": "active", "load_state": "loaded"},
            "user:dotoold.service": {"unit": "dotoold.service", "scope": "user", "status": "ok", "active_state": "active", "load_state": "loaded"},
        },
        "ydotool_socket": {"status": "missing"},
    }
    monkeypatch.setattr(cli_mod, "_validation_session_capability_matrix", lambda: capability_matrix)
    monkeypatch.setattr(cli_mod, "_validation_host_contract_snapshot", lambda: host_snapshot)

    res = runner.invoke(app, ["gen-host-contract-pack", str(project_dir), "--quiet"])
    assert res.exit_code == 0, res.output

    plan = json.loads((project_dir / "docs" / "VHK_HOST_PLAN.json").read_text())
    pointer_lane = next(item for item in plan["capability_lanes"] if item["capability"] == "pointer_injection")
    alt_group = next(item for item in plan["alternative_requirement_groups"] if item["id"] == "wayland-uinput-helper-daemon")

    assert alt_group["effective_status"] == "ready"
    assert alt_group["preferred_member_id"] == "dotool-daemon"
    assert alt_group["bootstrap_filter_id"] == "pointer-injection__dotool-daemon"
    assert pointer_lane["status"] == "ready"
    assert "wayland-uinput-helper-daemon" in plan["host_summary"]["effective_ready"]



def test_gen_host_contract_pack_can_select_outputs_and_review_script_runs(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = tmp_path / "host-docs"
    scripts_dir = tmp_path / "host-scripts"

    res = runner.invoke(
        app,
        [
            "gen-host-contract-pack",
            str(project_dir),
            "--out-dir",
            str(docs_dir),
            "--script-dir",
            str(scripts_dir),
            "--no-host-check",
            "--no-fixups-doc",
            "--force",
            "--quiet",
        ],
    )
    assert res.exit_code == 0, res.output

    assert (docs_dir / "VHK_HOST_REQUIREMENTS.md").exists()
    assert not (docs_dir / "VHK_HOST_FIXUPS.md").exists()
    assert (docs_dir / "VHK_HOST_PLAN.json").exists()
    assert (scripts_dir / "vhk_review_host_contract.sh").exists()

    proc = subprocess.run(
        ["sh", str(scripts_dir / "vhk_review_host_contract.sh")],
        cwd=project_dir,
        env={"PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "Collecting VHK host-contract evidence" in proc.stdout
    assert "Host-contract refresh complete." in proc.stdout


def test_host_contract_prefers_keyd_when_remapper_lane_is_ready(tmp_path: Path, monkeypatch) -> None:
    project_dir = _make_project(tmp_path)

    capability_matrix = {
        "screen_capture": {"status": "ok", "recommended": "portal:Screenshot", "mechanisms": ["portal:Screenshot"], "notes": [], "portal_backends": ["gnome"]},
        "text_injection": {"status": "limited", "recommended": None, "mechanisms": ["portal:RemoteDesktop(keyboard)"], "notes": ["interactive path"], "portal_backends": ["gnome"]},
        "pointer_injection": {"status": "ok", "recommended": "dotoolc", "mechanisms": ["dotoolc"], "notes": [], "portal_backends": ["gnome"]},
        "global_hotkeys": {"status": "limited", "recommended": None, "mechanisms": ["remapper"], "notes": [], "portal_backends": ["gnome"]},
        "input_capture": {"status": "limited", "recommended": None, "mechanisms": ["portal:InputCapture"], "notes": ["trigger-based"], "portal_backends": ["gnome"]},
    }
    host_snapshot = {
        "helpers": {
            "espanso": "/usr/bin/espanso",
            "ydotool": None,
            "dotool": "/usr/bin/dotool",
            "dotoolc": "/usr/bin/dotoolc",
            "dotoold": "/usr/bin/dotoold",
            "keyd": "/usr/bin/keyd",
            "kanata": None,
            "kmonad": None,
            "xremap": None,
        },
        "uinput": {"can_write": True, "status": "ok"},
        "xdg_portal_backend_config": {"status": "ok"},
        "service_units": {
            "user:espanso.service": {"unit": "espanso.service", "scope": "user", "status": "ok", "active_state": "active", "load_state": "loaded"},
            "user:vhk-busd.service": {"unit": "vhk-busd.service", "scope": "user", "status": "ok", "active_state": "active", "load_state": "loaded"},
            "user:dotoold.service": {"unit": "dotoold.service", "scope": "user", "status": "ok", "active_state": "active", "load_state": "loaded"},
            "system:keyd.service": {"unit": "keyd.service", "scope": "system", "status": "ok", "active_state": "active", "load_state": "loaded"},
            "user:kanata.service": {"unit": "kanata.service", "scope": "user", "status": "unit_missing", "active_state": None, "load_state": "not-found"},
            "system:kanata.service": {"unit": "kanata.service", "scope": "system", "status": "unit_missing", "active_state": None, "load_state": "not-found"},
            "user:xremap.service": {"unit": "xremap.service", "scope": "user", "status": "unit_missing", "active_state": None, "load_state": "not-found"},
            "system:xremap.service": {"unit": "xremap.service", "scope": "system", "status": "unit_missing", "active_state": None, "load_state": "not-found"},
            "user:kmonad.service": {"unit": "kmonad.service", "scope": "user", "status": "unit_missing", "active_state": None, "load_state": "not-found"},
            "system:kmonad.service": {"unit": "kmonad.service", "scope": "system", "status": "unit_missing", "active_state": None, "load_state": "not-found"},
        },
        "ydotool_socket": {"status": "missing"},
    }
    monkeypatch.setattr(cli_mod, "_validation_session_capability_matrix", lambda: capability_matrix)
    monkeypatch.setattr(cli_mod, "_validation_host_contract_snapshot", lambda: host_snapshot)

    res = runner.invoke(app, ["gen-host-contract-pack", str(project_dir), "--quiet", "--force"])
    assert res.exit_code == 0, res.output

    plan = json.loads((project_dir / "docs" / "VHK_HOST_PLAN.json").read_text())
    alt_group = next(item for item in plan["alternative_requirement_groups"] if item["id"] == "remapper-trigger-lane")
    keyd_req = next(item for item in plan["host_requirements"] if item["id"] == "keyd-remapper-service")
    xremap_req = next(item for item in plan["host_requirements"] if item["id"] == "xremap-remapper-service")

    assert alt_group["effective_status"] == "ready"
    assert alt_group["preferred_member_id"] == "keyd-remapper-service"
    assert alt_group["bootstrap_filter_id"] == "global-hotkeys__keyd-remapper-service"
    assert keyd_req["effective_observed_status"] == "ready"
    assert xremap_req["suppressed_by_alternative"] is True
    assert xremap_req["effective_observed_status"] == "covered"
