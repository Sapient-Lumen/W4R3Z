from __future__ import annotations

import json
import subprocess
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.project.setup_pack import build_setup_pack_plan, render_setup_guide


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



def test_gen_setup_pack_writes_docs_and_scripts(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = project_dir / "docs"
    scripts_dir = project_dir / "scripts"

    res = runner.invoke(app, ["gen-setup-pack", str(project_dir), "--no-session-check", "--quiet"])
    assert res.exit_code == 0, res.output

    guide = (docs_dir / "VHK_SETUP_GUIDE.md").read_text()
    matrix = (docs_dir / "VHK_SETUP_MATRIX.md").read_text()
    plan = json.loads((docs_dir / "VHK_SETUP_PLAN.json").read_text())
    apply_script = (scripts_dir / "vhk_apply_setup_recipes.sh").read_text()
    verify_script = (scripts_dir / "vhk_verify_setup_recipes.sh").read_text()
    package_script = (scripts_dir / "vhk_install_toolchain_packages.sh").read_text()

    assert "# VHK setup guide for proj" in guide
    assert "## Toolchain package bootstrap" in guide
    assert "## Setup recipes" in guide
    assert "scripts/vhk_apply_setup_recipes.sh" in guide
    assert "scripts/vhk_install_toolchain_packages.sh" in guide
    assert "## Authority-aware setup boundaries" in guide

    assert "# VHK setup recipe matrix for proj" in matrix
    assert "Runnable generator commands" in matrix
    assert "## Toolchain package groups" in matrix

    assert plan["project"]["name"] == "proj"
    assert plan["source_contract"] == "setup_recipes"
    assert plan["authority_policy"]["primary_mode"].startswith("xdg-local-userland")
    assert plan["setup_summary"]["recipe_count"] >= 1
    assert plan["toolchain_packages"]["package_count"] >= 1
    assert any(item["id"] == "launcher-entrypoint-install" for item in plan["setup_recipes"])
    launcher_recipe = next(item for item in plan["setup_recipes"] if item["id"] == "launcher-entrypoint-install")
    assert any(cmd.startswith("vhk ") for cmd in launcher_recipe["generator_commands"])
    assert all("/tmp/" not in cmd for cmd in launcher_recipe["generator_commands"])

    assert apply_script.startswith("#!/usr/bin/env sh\n")
    assert 'RECIPE_FILTER="${RECIPE_FILTER:-all}"' in apply_script
    assert "launcher-entrypoint-install" in apply_script
    assert "vhk export-desktop-entry . ./build/vhk-project.desktop" in apply_script

    assert verify_script.startswith("#!/usr/bin/env sh\n")
    assert "Running VHK verification recipe commands" in verify_script

    assert package_script.startswith("#!/usr/bin/env sh\n")
    assert "RUN_INSTALL=" in package_script
    assert "Running VHK toolchain package bootstrap" in package_script
    assert "sudo apt-get install -y" in package_script



def test_gen_setup_pack_can_select_outputs_and_scripts_are_runnable(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = tmp_path / "setup-docs"
    scripts_dir = tmp_path / "setup-scripts"

    res = runner.invoke(
        app,
        [
            "gen-setup-pack",
            str(project_dir),
            "--out-dir",
            str(docs_dir),
            "--script-dir",
            str(scripts_dir),
            "--no-session-check",
            "--no-matrix",
            "--force",
            "--quiet",
        ],
    )
    assert res.exit_code == 0, res.output

    assert (docs_dir / "VHK_SETUP_GUIDE.md").exists()
    assert not (docs_dir / "VHK_SETUP_MATRIX.md").exists()
    assert (docs_dir / "VHK_SETUP_PLAN.json").exists()
    assert (scripts_dir / "vhk_apply_setup_recipes.sh").exists()
    assert (scripts_dir / "vhk_verify_setup_recipes.sh").exists()
    assert (scripts_dir / "vhk_install_toolchain_packages.sh").exists()

    proc = subprocess.run(
        ["sh", str(scripts_dir / "vhk_apply_setup_recipes.sh")],
        cwd=project_dir,
        env={"RECIPE_FILTER": "nonexistent"},
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "Running VHK generator recipe commands" in proc.stdout

    pkg_proc = subprocess.run(
        ["sh", str(scripts_dir / "vhk_install_toolchain_packages.sh")],
        cwd=project_dir,
        env={"PACKAGE_FILTER": "text-injection", "PACKAGE_MANAGER": "apt", "RUN_INSTALL": "0"},
        capture_output=True,
        text=True,
        check=False,
    )
    assert pkg_proc.returncode == 0
    assert "Running VHK toolchain package bootstrap" in pkg_proc.stdout
    assert "Detected package manager: apt" in pkg_proc.stdout
    assert "dry-run" in pkg_proc.stdout


def test_setup_pack_keeps_helper_families_as_alternative_package_lanes(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(app, ["gen-setup-pack", str(project_dir), "--no-session-check", "--quiet", "--force"])
    assert res.exit_code == 0, res.output

    plan = json.loads((project_dir / "docs" / "VHK_SETUP_PLAN.json").read_text())
    package_script = (project_dir / "scripts" / "vhk_install_toolchain_packages.sh").read_text()

    text_group = next(item for item in plan["toolchain_packages"]["package_groups"] if item["id"] == "text-injection")
    pointer_group = next(item for item in plan["toolchain_packages"]["package_groups"] if item["id"] == "pointer-injection")

    assert "wtype" in text_group["packages"]
    assert "wl-clipboard" in text_group["packages"]
    assert "ydotool" not in text_group["packages"]

    assert "dotool" in pointer_group["packages"]
    assert "ydotool" not in pointer_group["packages"]
    assert pointer_group["selected_alternative_ids"] == ["dotool-daemon"]

    alt_group = next(item for item in pointer_group["alternative_package_groups"] if item["id"] == "wayland-uinput-helper-daemon")
    dotool_lane = next(item for item in alt_group["members"] if item["id"] == "dotool-daemon")
    ydotool_lane = next(item for item in alt_group["members"] if item["id"] == "ydotool-daemon")

    assert dotool_lane["selected_by_default"] is True
    assert dotool_lane["filter_id"] == "pointer-injection__dotool-daemon"
    assert ydotool_lane["filter_id"] == "pointer-injection__ydotool-daemon"
    assert alt_group["selected_filter_id"] == "pointer-injection__dotool-daemon"
    assert "pointer-injection__dotool-daemon" in pointer_group["selected_filter_ids"]
    assert "dotool" in dotool_lane["effective_packages"]
    assert "ydotool" in ydotool_lane["effective_packages"]
    assert "ydotool" not in plan["toolchain_packages"]["packages"]

    assert "pointer-injection__ydotool-daemon" in package_script
    assert "Alternative lane filters:" in package_script


def test_setup_pack_keeps_remapper_families_as_alternative_trigger_lanes(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(app, ["gen-setup-pack", str(project_dir), "--no-session-check", "--quiet", "--force"])
    assert res.exit_code == 0, res.output

    plan = json.loads((project_dir / "docs" / "VHK_SETUP_PLAN.json").read_text())
    package_script = (project_dir / "scripts" / "vhk_install_toolchain_packages.sh").read_text()

    hotkey_group = next(item for item in plan["toolchain_packages"]["package_groups"] if item["id"] == "global-hotkeys")
    remapper_group = next(item for item in hotkey_group["alternative_package_groups"] if item["id"] == "remapper-trigger-lane")
    keyd_lane = next(item for item in remapper_group["members"] if item["id"] == "keyd-remapper-service")
    xremap_lane = next(item for item in remapper_group["members"] if item["id"] == "xremap-remapper-service")

    assert hotkey_group["selected_alternative_ids"] == ["keyd-remapper-service"]
    assert "keyd" in hotkey_group["packages"]
    assert "kanata" not in hotkey_group["packages"]
    assert remapper_group["selected_filter_id"] == "global-hotkeys__keyd-remapper-service"
    assert keyd_lane["selected_by_default"] is True
    assert keyd_lane["filter_id"] == "global-hotkeys__keyd-remapper-service"
    assert xremap_lane["filter_id"] == "global-hotkeys__xremap-remapper-service"
    assert "global-hotkeys__xremap-remapper-service" in package_script


def test_setup_pack_can_render_observed_deployment_truth(tmp_path: Path) -> None:
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
        "xdg_portal_backend_manifests": {
            "status": "ok_with_warnings",
            "xdg_current_desktop": "sway",
            "backends": [
                {"backend": "gtk", "manifest_path": "/usr/share/xdg-desktop-portal/portals/gtk.portal", "interfaces": ["org.freedesktop.impl.portal.RemoteDesktop"], "use_in": [], "matching_desktops": [], "usable_on_current_desktop": True},
                {"backend": "luminous", "manifest_path": "/usr/share/xdg-desktop-portal/portals/luminous.portal", "interfaces": ["org.freedesktop.impl.portal.Screenshot", "org.freedesktop.impl.portal.ScreenCast", "org.freedesktop.impl.portal.InputCapture"], "use_in": ["sway"], "matching_desktops": ["sway"], "usable_on_current_desktop": True},
            ],
            "parse_errors": [{"path": "/usr/share/xdg-desktop-portal/portals/broken.portal", "status": "parse_failed", "error": "boom"}],
        },
        "service_units": {"user:dotoold.service": {"unit": "dotoold.service", "scope": "user", "status": "ok", "active_state": "active", "load_state": "loaded"}},
    }

    plan = build_setup_pack_plan(
        project_dir,
        capability_matrix=capability_matrix,
        host_snapshot=host_snapshot,
    )
    guide = render_setup_guide(plan)

    assert plan["portal_route_contract"]["status"] == "degraded"
    assert plan["portal_route_contract"]["manifest_status"] == "ok_with_warnings"
    assert plan["host_truth"]["blocked_count"] >= 1
    assert "## Observed deployment truth" in guide
    assert "Portal route status" in guide
