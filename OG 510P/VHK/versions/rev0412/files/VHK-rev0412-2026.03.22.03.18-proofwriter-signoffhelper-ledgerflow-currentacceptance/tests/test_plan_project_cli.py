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

    (project_dir / "macros" / "snippet.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "snippet",
                "description": "Insert a structured reply",
                "presets": [{"name": "support", "vars": {"team": "support"}}],
                "steps": [
                    {
                        "type": "PromptForm",
                        "title": "Reply",
                        "fields": [{"name": "name", "label": "Name"}],
                    },
                    {"type": "TypeText", "text": "Hello ${reply.name}"},
                    {
                        "type": "TypeText",
                        "backend": "native",
                        "text": "Email:	person@example.com\nCompany:	Very Long Company Name",
                    },
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
                "description": "Click through a visual workflow",
                "steps": [
                    {"type": "Delay", "ms": 2000},
                    {"type": "WaitForImage", "needle_path": "assets/button.png", "timeout_ms": 5000},
                    {"type": "MouseClickAt", "x": 100, "y": 200},
                    {"type": "ClickNeedle", "needle_path": "assets/ok.png"},
                ],
            },
            sort_keys=False,
        )
    )

    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj",
                "settings": {"desktop_backend": "wayland", "event_log": False},
                "bindings": [{"keys": "Mod4+V", "macro": "vision"}],
                "hotstrings": [{"trigger": ":reply", "macro": "snippet"}],
                "bus_watchers": [{"name": "refresh", "event": "proj.refresh", "macro": "vision"}],
            },
            sort_keys=False,
        )
    )
    return project_dir


def _make_x11_project(tmp_path: Path) -> Path:
    project_dir = _make_project(tmp_path)
    project_data = yaml.safe_load((project_dir / "project.yaml").read_text())
    project_data.setdefault("settings", {})["desktop_backend"] = "x11"
    (project_dir / "project.yaml").write_text(yaml.safe_dump(project_data, sort_keys=False))
    return project_dir


def _make_accessibility_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "a11y-proj"
    (project_dir / "macros").mkdir(parents=True)

    (project_dir / "macros" / "focus_terminal.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "focus_terminal",
                "description": "Focus and inspect a terminal window",
                "steps": [
                    {"type": "WaitForWindow", "selector": {"title": "Terminal"}, "timeout_ms": 2000},
                    {"type": "GetActiveWindow", "var": "active", "include_geometry": True},
                    {"type": "Return", "value": "${active.title}"},
                ],
            },
            sort_keys=False,
        )
    )

    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "a11y-proj",
                "settings": {"desktop_backend": "wayland", "event_log": False},
                "bindings": [{"keys": "Mod4+T", "macro": "focus_terminal"}],
                "window_watchers": [{"name": "terminal-ready", "selector": {"title": "Terminal"}, "macro": "focus_terminal"}],
            },
            sort_keys=False,
        )
    )
    return project_dir


def _make_picker_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "picker-proj"
    (project_dir / "macros").mkdir(parents=True)

    (project_dir / "macros" / "deploy.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "deploy",
                "description": "Choose a target and deploy",
                "presets": [{"name": "prod", "vars": {"env": "prod"}}],
                "steps": [
                    {
                        "type": "PromptForm",
                        "title": "Deploy",
                        "fields": [{"name": "ticket", "label": "Ticket"}],
                    },
                    {"type": "SetVar", "name": "regions", "value": ["us-east-1", "eu-west-1"]},
                    {
                        "type": "ChooseFromList",
                        "text": "Choose region",
                        "items_expr": "regions",
                        "out_var": "region",
                    },
                    {"type": "Return", "value": "${region}"},
                ],
            },
            sort_keys=False,
        )
    )

    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "picker-proj",
                "settings": {"desktop_backend": "wayland", "event_log": False},
            },
            sort_keys=False,
        )
    )
    return project_dir


def _make_app_protocol_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "app-protocol-proj"
    (project_dir / "macros").mkdir(parents=True)

    (project_dir / "macros" / "send_to_kitty.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "send_to_kitty",
                "description": "Send text to a kitty-backed terminal workflow",
                "steps": [
                    {"type": "WaitForWindow", "selector": {"class": "kitty", "title": "Work"}, "timeout_ms": 2000},
                    {"type": "TypeText", "text": "pytest -q"},
                    {"type": "Return", "value": "kitty"},
                ],
            },
            sort_keys=False,
        )
    )

    (project_dir / "macros" / "pause_mpv.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "pause_mpv",
                "description": "Find the mpv player window",
                "steps": [
                    {"type": "WaitForWindow", "selector": {"class": "mpv"}, "timeout_ms": 2000},
                    {"type": "Return", "value": "mpv"},
                ],
            },
            sort_keys=False,
        )
    )

    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "app-protocol-proj",
                "settings": {"desktop_backend": "wayland", "event_log": False},
                "bindings": [
                    {"keys": "Mod4+Return", "macro": "send_to_kitty", "when": {"class": "kitty"}},
                    {"keys": "Mod4+P", "macro": "pause_mpv", "when": {"class": "mpv"}},
                ],
            },
            sort_keys=False,
        )
    )
    return project_dir

def _make_qutebrowser_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "qutebrowser-plan-proj"
    (project_dir / "macros").mkdir(parents=True)

    (project_dir / "macros" / "browser_action.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "browser_action",
                "description": "Run a qutebrowser userscript-backed workflow",
                "steps": [
                    {"type": "WaitForWindow", "selector": {"class": "qutebrowser", "title": "Docs"}, "timeout_ms": 2000},
                    {"type": "Return", "value": "browser"},
                ],
            },
            sort_keys=False,
        )
    )

    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "qutebrowser-plan-proj",
                "settings": {"desktop_backend": "wayland", "event_log": False},
                "bindings": [
                    {"keys": ",b", "macro": "browser_action", "when": {"class": "qutebrowser", "title": "Docs"}},
                ],
            },
            sort_keys=False,
        )
    )
    return project_dir


def _make_wezterm_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "wezterm-plan-proj"
    (project_dir / "macros").mkdir(parents=True)

    (project_dir / "macros" / "send_to_wezterm.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "send_to_wezterm",
                "description": "Send text to a WezTerm work pane",
                "steps": [
                    {"type": "WaitForWindow", "selector": {"class": "org.wezfurlong.wezterm", "title": "Work Pane"}, "timeout_ms": 2000},
                    {"type": "TypeText", "text": "cargo test --quiet"},
                    {"type": "Return", "value": "wezterm"},
                ],
            },
            sort_keys=False,
        )
    )

    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "wezterm-plan-proj",
                "settings": {"desktop_backend": "wayland", "event_log": False},
                "bindings": [
                    {"keys": "Mod4+Return", "macro": "send_to_wezterm", "when": {"class": "org.wezfurlong.wezterm", "title": "Work Pane"}},
                ],
            },
            sort_keys=False,
        )
    )
    return project_dir


def _make_voice_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "voice-proj"
    (project_dir / "macros").mkdir(parents=True)

    (project_dir / "macros" / "open_terminal.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "open_terminal",
                "description": "Open a terminal command palette",
                "voice_phrases": ["terminal palette", "open terminal palette"],
                "voice_when": {"class": "kitty", "title": "Work"},
                "steps": [
                    {"type": "ShowMessage", "title": "Voice", "text": "terminal"},
                    {"type": "Return", "value": "terminal"},
                ],
            },
            sort_keys=False,
        )
    )

    (project_dir / "macros" / "deploy.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "deploy",
                "description": "Deploy through a spoken preset",
                "presets": [
                    {
                        "name": "prod",
                        "vars": {"env": "prod"},
                        "voice_phrases": ["deploy production"],
                        "voice_when": {"title": "Dashboard"},
                    }
                ],
                "steps": [
                    {"type": "Return", "value": "deploy"},
                ],
            },
            sort_keys=False,
        )
    )

    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "voice-proj",
                "settings": {"desktop_backend": "wayland", "event_log": False},
            },
            sort_keys=False,
        )
    )
    return project_dir


def _make_mpris_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "mpris-proj"
    (project_dir / "macros").mkdir(parents=True)

    (project_dir / "macros" / "wait_for_track.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "wait_for_track",
                "description": "React to the next media-player track change",
                "steps": [
                    {
                        "type": "WaitForDbusSignal",
                        "bus": "session",
                        "sender": "org.mpris.MediaPlayer2.spotify",
                        "path": "/org/mpris/MediaPlayer2",
                        "interface": "org.freedesktop.DBus.Properties",
                        "member": "PropertiesChanged",
                        "timeout_ms": 2000,
                    },
                    {"type": "Return", "value": "mpris"},
                ],
            },
            sort_keys=False,
        )
    )

    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "mpris-proj",
                "settings": {"desktop_backend": "wayland", "event_log": False},
                "bindings": [{"keys": "XF86AudioPlay", "macro": "wait_for_track"}],
            },
            sort_keys=False,
        )
    )
    return project_dir



def _make_notification_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "notification-proj"
    (project_dir / "macros").mkdir(parents=True)

    (project_dir / "macros" / "sync_status.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "sync_status",
                "description": "Report sync progress through desktop notifications",
                "steps": [
                    {
                        "type": "Notify",
                        "summary": "Sync started",
                        "body": "Uploading logs",
                        "urgency": "normal",
                        "progress": 10,
                        "actions": [{"id": "open_logs", "label": "Open logs"}],
                        "out_action": "notification_action",
                    },
                    {
                        "type": "WaitForDbusSignal",
                        "bus": "session",
                        "sender": "org.freedesktop.Notifications",
                        "path": "/org/freedesktop/Notifications",
                        "interface": "org.freedesktop.Notifications",
                        "member": "ActionInvoked",
                        "timeout_ms": 1500,
                    },
                    {"type": "Return", "value": "notifications"},
                ],
            },
            sort_keys=False,
        )
    )

    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "notification-proj",
                "settings": {"desktop_backend": "wayland", "event_log": False},
                "bindings": [{"keys": "Mod4+N", "macro": "sync_status"}],
            },
            sort_keys=False,
        )
    )
    return project_dir


def _make_x11_mode_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "x11-mode-proj"
    (project_dir / "macros").mkdir(parents=True)

    for idx in range(1, 6):
        (project_dir / "macros" / f"m{idx}.yaml").write_text(
            yaml.safe_dump(
                {
                    "name": f"m{idx}",
                    "description": f"Macro {idx}",
                    "steps": [{"type": "Return", "value": f"m{idx}"}],
                },
                sort_keys=False,
            )
        )

    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "i3-proj",
                "settings": {"desktop_backend": "x11", "event_log": False},
                "bindings": [
                    {"keys": "Mod4+R", "macro": "m1", "description": "Resize mode action"},
                    {"keys": "Mod4+M", "macro": "m2", "description": "Management action"},
                    {"keys": "Mod4+Shift+P", "macro": "m3", "description": "Project action"},
                    {"keys": "Mod4+Shift+L", "macro": "m4", "description": "Layout action"},
                    {"keys": "Mod4+Shift+O", "macro": "m5", "description": "Ops action"},
                ],
            },
            sort_keys=False,
        )
    )
    return project_dir



def test_plan_project_json_reports_shape_and_recommendations(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(app, ["plan-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)

    assert data["overview"]["macros"] == 2
    assert data["overview"]["bindings"] == 1
    assert data["overview"]["hotstrings"] == 1
    assert "wm-integrated" in data["project_tags"]
    assert "text-expander-integration" in data["project_tags"]
    assert "selector-asset-heavy" in data["project_tags"]
    assert "parameterized" in data["project_tags"]

    snippet = next(item for item in data["macro_profiles"] if item["macro"] == "snippet")
    assert "text-expander" in snippet["tags"]
    assert "parameterized" in snippet["tags"]
    assert snippet["triggers"] == ["hotstring"]
    assert "text-throughput" in snippet["performance"]["tags"]
    assert "structured-text" in snippet["performance"]["tags"]
    assert snippet["performance"]["structured_literal_type_steps"] == 1
    assert snippet["performance"]["long_literal_type_steps"] == 0

    vision = next(item for item in data["macro_profiles"] if item["macro"] == "vision")
    assert "vision-heavy" in vision["tags"]
    assert set(vision["triggers"]) == {"hotkey", "bus-watcher"}
    assert vision["smells"]["long_delay"] == 1
    assert vision["smells"]["coord_click"] == 1
    assert "capture-heavy" in vision["performance"]["tags"]
    assert "unscoped-vision" in vision["performance"]["tags"]
    assert vision["performance"]["risk_level"] in {"high", "medium"}
    assert vision["performance"]["live_capture_steps"] >= 2

    perf = data["performance_profile"]
    assert perf["priority"] in {"high", "medium"}
    assert perf["budget"]["unscoped_live_capture_steps"] >= 1
    assert perf["budget"]["ocr_steps"] == 0
    assert perf["budget"]["structured_literal_type_steps"] == 1
    hotspot_ids = {item["id"] for item in perf["hotspots"]}
    assert "unscoped-live-capture" in hotspot_ids
    assert "fixed-delay-budget" in hotspot_ids
    assert "typed-text-throughput" in hotspot_ids
    assert "direct-hotkey-heavy-macros" in hotspot_ids
    snippet_runtime = next(item for item in perf["macro_runtime_profiles"] if item["macro"] == "snippet")
    assert snippet_runtime["structured_literal_type_steps"] == 1
    runtime_profile = next(item for item in perf["macro_runtime_profiles"] if item["macro"] == "vision")
    assert runtime_profile["risk_level"] in {"high", "medium"}
    assert runtime_profile["live_capture_steps"] >= 2
    assert runtime_profile["declared_delay_ms"] == 2000

    rec_ids = {item["id"] for item in data["recommendations"]}
    assert "dispatch-plane" in rec_ids
    assert "text-tier" in rec_ids
    assert "selector-assets" in rec_ids
    assert "cleanup-loop" in rec_ids

    lane_ids = {item["id"] for item in data["product_lanes"]}
    assert "trigger-plane" in lane_ids
    assert "text-tier" in lane_ids
    assert "visual-lane" in lane_ids
    assert "event-bridge" in lane_ids
    assert "remap-surface" in lane_ids
    assert next(item for item in data["product_lanes"] if item["id"] == "text-tier")["score"] > 0

    architecture = data["architecture_map"]
    assert architecture["stance"]
    component_ids = {item["id"] for item in architecture["components"]}
    assert "runner-core" in component_ids
    assert "dispatch-plane" in component_ids
    assert "text-tier" in component_ids
    assert "selector-pack" in component_ids

    target_ids = {item["id"] for item in data["integration_targets"]}
    assert "trigger-plane" in target_ids
    assert "text-tier" in target_ids
    assert "selector-pack" in target_ids
    assert "event-bridge" in target_ids

    playbook_ids = {item["id"] for item in data["playbooks"]}
    assert "deployment-audit" in playbook_ids
    assert "text-export-loop" in playbook_ids
    assert "selector-debug-loop" in playbook_ids
    assert "remap-export-loop" in playbook_ids
    assert "dispatch-daemon-loop" in playbook_ids
    text_export = next(item for item in data["playbooks"] if item["id"] == "text-export-loop")
    assert any("gen-espanso" in cmd for cmd in text_export["commands"])

    profile_ids = {item["id"] for item in data["deployment_profiles"]}
    assert "text-first-export" in profile_ids
    assert "selector-runner" in profile_ids
    assert "watcher-daemon" in profile_ids
    assert "remap-integrated" in profile_ids
    assert any("gen-espanso" in cmd for item in data["deployment_profiles"] if item["id"] == "text-first-export" for cmd in item["commands"])

    stack_profile_ids = {item["id"] for item in data["stack_profiles"]}
    assert "text-first-export" in stack_profile_ids
    assert "selector-runner" in stack_profile_ids
    assert "watcher-daemon" in stack_profile_ids
    assert "remap-integrated" in stack_profile_ids
    text_stack = next(item for item in data["stack_profiles"] if item["id"] == "text-first-export")
    assert text_stack["product_shape"] == "export-first"
    assert text_stack["thin_layers"]
    assert text_stack["stateful_layers"]

    desktop_target_ids = {item["id"] for item in data["desktop_targets"]}
    assert "portable-text-export" in desktop_target_ids
    assert "portal-wayland" in desktop_target_ids
    assert "helper-boundary-wayland" in desktop_target_ids
    helper_target = next(item for item in data["desktop_targets"] if item["id"] == "helper-boundary-wayland")
    assert helper_target["learn_from"]
    assert any("gen-keyd-config" in cmd for cmd in helper_target["commands"])

    surface_ids = {item["id"] for item in data["surface_choices"]}
    assert "espanso-text-package" in surface_ids
    assert "wtype-wayland-text" in surface_ids
    assert "uinput-helper-daemon" in surface_ids
    assert "vhk-palette-launcher" in surface_ids
    assert "launcher-hub-surface" in surface_ids
    assert "wm-native-dispatch" in surface_ids
    assert "portal-global-shortcuts" in surface_ids
    assert "keyd-remap" in surface_ids
    assert "kanata-remap" in surface_ids
    assert "xremap-remap" in surface_ids
    wtype_surface = next(item for item in data["surface_choices"] if item["id"] == "wtype-wayland-text")
    assert wtype_surface["category"] == "text"
    assert wtype_surface["fit"] in {"conditional", "good", "strong"}
    assert any("gen-espanso" in cmd for cmd in wtype_surface["commands"])
    helper_daemon_surface = next(item for item in data["surface_choices"] if item["id"] == "uinput-helper-daemon")
    assert helper_daemon_surface["category"] == "adapter"
    assert helper_daemon_surface["fit"] in {"conditional", "good", "strong"}
    assert any("gen-dotoold-service" in cmd for cmd in helper_daemon_surface["commands"])
    assert any("gen-udev-uinput" in cmd for cmd in helper_daemon_surface["commands"])
    xremap_surface = next(item for item in data["surface_choices"] if item["id"] == "xremap-remap")
    assert any("gen-xremap-config" in cmd for cmd in xremap_surface["commands"])
    assert "watcher-services" in surface_ids




def test_plan_project_json_includes_input_lane_dossier(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(app, ["plan-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)

    dossier = dict(data["input_lane_dossier"])
    assert dossier["summary"]
    lane_ids = {item["id"] for item in dossier["lanes"]}
    assert "clipboard-text-lane" in lane_ids
    assert "virtual-keyboard-text-fastpath" in lane_ids
    assert "daemon-backed-uinput-playback" in lane_ids
    assert "portal-permissioned-input" in lane_ids

    clipboard_lane = next(item for item in dossier["lanes"] if item["id"] == "clipboard-text-lane")
    assert clipboard_lane["fit"] in {"good", "strong"}
    assert "text-surface-service" in clipboard_lane["host_requirement_ids"]

    daemon_lane = next(item for item in dossier["lanes"] if item["id"] == "daemon-backed-uinput-playback")
    assert daemon_lane["fit"] in {"good", "strong"}
    assert "uinput-permissions" in daemon_lane["host_requirement_ids"]
    assert any(item in daemon_lane["host_requirement_ids"] for item in {"dotool-daemon", "ydotool-daemon"})

    assert "clipboard-text-lane" in dossier["recommended_lane_ids"]
    assert "daemon-backed-uinput-playback" in dossier["recommended_lane_ids"]


def test_plan_project_x11_surfaces_include_autokey_adapter_lane(tmp_path: Path) -> None:
    project_dir = _make_x11_project(tmp_path)

    res = runner.invoke(app, ["plan-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)

    surface_ids = {item["id"] for item in data["surface_choices"]}
    assert "autokey-x11-adapter" in surface_ids
    autokey_surface = next(item for item in data["surface_choices"] if item["id"] == "autokey-x11-adapter")
    assert autokey_surface["category"] == "adapter"
    assert autokey_surface["fit"] in {"good", "strong"}
    assert any("gen-autokey-pack" in cmd for cmd in autokey_surface["commands"])

    reference_ids = {item["id"] for item in data["reference_patterns"]}
    assert "autokey-reviewable-adapter" in reference_ids
    autokey_pattern = next(item for item in data["reference_patterns"] if item["id"] == "autokey-reviewable-adapter")
    assert autokey_pattern["fit"] in {"good", "strong"}
    assert any("gen-autokey-pack" in cmd for cmd in autokey_pattern["commands"])

    snippet_route = next(item for item in data["macro_route_profiles"] if item["macro"] == "snippet")
    assert snippet_route["route_id"] == "text-tier"
    assert any("gen-autokey-pack" in cmd for cmd in snippet_route["commands"])

    text_export = next(
        item for item in data["macro_export_candidates"]
        if item["macro"] == "snippet" and item["export_surface_id"] == "text-package-export"
    )
    assert "AutoKey" in text_export["tool_family"]
    assert any("gen-autokey-pack" in cmd for cmd in text_export["commands"])
    espanso = next(item for item in data["surface_choices"] if item["id"] == "espanso-text-package")
    assert espanso["fit"] in {"good", "strong"}
    assert any("gen-espanso" in cmd for cmd in espanso["commands"])
    launcher_hub = next(item for item in data["surface_choices"] if item["id"] == "launcher-hub-surface")
    assert launcher_hub["commands"]
    assert "Kando menu triggers" in launcher_hub["learn_from"]

    env_ids = {item["id"] for item in data["environment_diffs"]}
    assert "x11-i3" in env_ids
    assert "gnome-wayland" in env_ids
    assert "kde-wayland" in env_ids
    assert "wlroots-sway-conservative" in env_ids
    assert "hyprland-conservative" in env_ids
    x11 = next(item for item in data["environment_diffs"] if item["id"] == "x11-i3")
    assert x11["top_target"]["id"] == "x11-tiling-native"
    hypr = next(item for item in data["environment_diffs"] if item["id"] == "hyprland-conservative")
    assert "pointer_injection" in hypr["blocking_capabilities"]
    assert hypr["preferred_surfaces"]


def test_plan_project_wayland_surfaces_include_accessibility_lane(tmp_path: Path) -> None:
    project_dir = _make_accessibility_project(tmp_path)

    res = runner.invoke(app, ["plan-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)

    surface_ids = {item["id"] for item in data["surface_choices"]}
    assert "atspi-structured-ui" in surface_ids
    a11y_surface = next(item for item in data["surface_choices"] if item["id"] == "atspi-structured-ui")
    assert a11y_surface["category"] == "context"
    assert a11y_surface["fit"] in {"conditional", "good", "strong"}
    assert any("doctor --json" in cmd for cmd in a11y_surface["commands"])
    assert any("gen-session-fit-pack" in cmd for cmd in a11y_surface["commands"])

    reference_ids = {item["id"] for item in data["reference_patterns"]}
    assert "atspi-structured-selector-lane" in reference_ids
    a11y_pattern = next(item for item in data["reference_patterns"] if item["id"] == "atspi-structured-selector-lane")
    assert a11y_pattern["fit"] in {"conditional", "good", "strong"}
    assert "Accerciser" in a11y_pattern["learn_from"]
    assert any("gen-capability-audit-pack" in cmd for cmd in a11y_pattern["commands"])

    lesson_ids = {item["id"] for item in data["ecosystem_lessons"]}
    assert "atspi-separate-bus-structured-automation" in lesson_ids
    lesson = next(item for item in data["ecosystem_lessons"] if item["id"] == "atspi-separate-bus-structured-automation")
    assert lesson["fit"] in {"good", "strong", "conditional"}
    assert "Accerciser" in lesson["source_tools"]
    assert any("doctor --json" in cmd for cmd in lesson["commands"])

    toolchain = next(item for item in data["toolchain_choices"] if item["id"] == "window-introspection")
    assert toolchain["recommended_toolchain"]
    assert any("AT-SPI/Accerciser" == item for item in toolchain["fallback_toolchains"])
    assert any("dogtail structured UI automation" == item for item in toolchain["learn_from"])


def test_plan_project_wayland_surfaces_include_app_native_protocol_lane(tmp_path: Path) -> None:
    project_dir = _make_app_protocol_project(tmp_path)

    res = runner.invoke(app, ["plan-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)

    surface_ids = {item["id"] for item in data["surface_choices"]}
    assert "app-native-control-adapter" in surface_ids
    app_surface = next(item for item in data["surface_choices"] if item["id"] == "app-native-control-adapter")
    assert app_surface["category"] == "adapter"
    assert app_surface["fit"] in {"good", "strong", "conditional"}
    assert "kitty" in " ".join(app_surface["evidence"]).lower()
    assert any("gen-kitty-pack" in cmd for cmd in app_surface["commands"])
    assert any("gen-mpv-pack" in cmd for cmd in app_surface["commands"])
    assert any("gen-target-route-pack" in cmd for cmd in app_surface["commands"])

    reference_ids = {item["id"] for item in data["reference_patterns"]}
    assert "app-native-protocol-lane" in reference_ids
    app_pattern = next(item for item in data["reference_patterns"] if item["id"] == "app-native-protocol-lane")
    assert app_pattern["fit"] in {"good", "strong", "conditional"}
    assert "kitty remote control" in app_pattern["learn_from"]
    assert "mpv JSON IPC" in app_pattern["learn_from"]
    assert any("gen-kitty-pack" in cmd for cmd in app_pattern["commands"])
    assert any("gen-mpv-pack" in cmd for cmd in app_pattern["commands"])
    assert any("gen-target-route-pack" in cmd for cmd in app_pattern["commands"])

    lesson_ids = {item["id"] for item in data["ecosystem_lessons"]}
    assert "native-app-protocols-beat-input-replay" in lesson_ids
    lesson = next(item for item in data["ecosystem_lessons"] if item["id"] == "native-app-protocols-beat-input-replay")
    assert lesson["fit"] in {"good", "strong", "conditional"}
    assert "kitty remote control" in lesson["source_tools"]
    assert "mpv JSON IPC" in lesson["source_tools"]
    assert any("gen-kitty-pack" in cmd for cmd in lesson["commands"])
    assert any("gen-mpv-pack" in cmd for cmd in lesson["commands"])
    assert any("gen-design-pack" in cmd for cmd in lesson["commands"])


def test_plan_project_surfaces_include_wezterm_pack_command(tmp_path: Path) -> None:
    project_dir = _make_wezterm_project(tmp_path)

    res = runner.invoke(app, ["plan-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)

    app_surface = next(item for item in data["surface_choices"] if item["id"] == "app-native-control-adapter")
    assert app_surface["fit"] in {"good", "strong", "conditional"}
    assert any("wezterm" in value.lower() for value in app_surface["evidence"])
    assert any("gen-wezterm-pack" in cmd for cmd in app_surface["commands"])

    app_pattern = next(item for item in data["reference_patterns"] if item["id"] == "app-native-protocol-lane")
    assert "WezTerm CLI" in app_pattern["learn_from"]
    assert any("gen-wezterm-pack" in cmd for cmd in app_pattern["commands"])

    lesson = next(item for item in data["ecosystem_lessons"] if item["id"] == "native-app-protocols-beat-input-replay")
    assert "WezTerm CLI" in lesson["source_tools"]
    assert any("gen-wezterm-pack" in cmd for cmd in lesson["commands"])


def test_plan_project_surfaces_include_qutebrowser_pack_command(tmp_path: Path) -> None:
    project_dir = _make_qutebrowser_project(tmp_path)

    res = runner.invoke(app, ["plan-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)

    app_surface = next(item for item in data["surface_choices"] if item["id"] == "app-native-control-adapter")
    assert app_surface["fit"] in {"good", "strong", "conditional"}
    assert any("qutebrowser" in value.lower() for value in app_surface["evidence"])
    assert any("gen-qutebrowser-pack" in cmd for cmd in app_surface["commands"])

    app_pattern = next(item for item in data["reference_patterns"] if item["id"] == "app-native-protocol-lane")
    assert "qutebrowser userscripts" in app_pattern["learn_from"]
    assert any("gen-qutebrowser-pack" in cmd for cmd in app_pattern["commands"])

    lesson = next(item for item in data["ecosystem_lessons"] if item["id"] == "native-app-protocols-beat-input-replay")
    assert "qutebrowser userscripts" in lesson["source_tools"]
    assert any("gen-qutebrowser-pack" in cmd for cmd in lesson["commands"])


def test_plan_project_surfaces_include_voice_adapter_lane(tmp_path: Path) -> None:
    project_dir = _make_voice_project(tmp_path)

    res = runner.invoke(app, ["plan-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)

    surface_ids = {item["id"] for item in data["surface_choices"]}
    assert "voice-command-adapter" in surface_ids
    voice_surface = next(item for item in data["surface_choices"] if item["id"] == "voice-command-adapter")
    assert voice_surface["category"] == "adapter"
    assert voice_surface["fit"] in {"good", "strong", "conditional"}
    assert any("gen-dragonfly-pack" in cmd for cmd in voice_surface["commands"])
    assert any("gen-talon-pack" in cmd for cmd in voice_surface["commands"])
    assert "voice_phrases=3" in voice_surface["evidence"]

    reference_ids = {item["id"] for item in data["reference_patterns"]}
    assert "voice-context-command-lane" in reference_ids
    voice_pattern = next(item for item in data["reference_patterns"] if item["id"] == "voice-context-command-lane")
    assert voice_pattern["fit"] in {"good", "strong", "conditional"}
    assert "Talon contexts" in voice_pattern["learn_from"]
    assert any("gen-dragonfly-pack" in cmd for cmd in voice_pattern["commands"])

    lesson_ids = {item["id"] for item in data["ecosystem_lessons"]}
    assert "voice-tools-own-recognition-context" in lesson_ids
    lesson = next(item for item in data["ecosystem_lessons"] if item["id"] == "voice-tools-own-recognition-context")
    assert lesson["fit"] in {"good", "strong", "conditional"}
    assert "Talon" in lesson["source_tools"]
    assert "Dragonfly" in lesson["source_tools"]
    assert any("gen-talon-pack" in cmd for cmd in lesson["commands"])


def test_plan_project_surfaces_include_mpris_service_bus_lane(tmp_path: Path) -> None:
    project_dir = _make_mpris_project(tmp_path)

    res = runner.invoke(app, ["plan-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)

    surface_ids = {item["id"] for item in data["surface_choices"]}
    assert "mpris-media-bus-adapter" in surface_ids
    mpris_surface = next(item for item in data["surface_choices"] if item["id"] == "mpris-media-bus-adapter")
    assert mpris_surface["category"] == "adapter"
    assert mpris_surface["fit"] in {"good", "strong", "conditional"}
    assert "mpris_signals=1" in mpris_surface["evidence"]
    assert any("gen-playerctl-pack" in cmd for cmd in mpris_surface["commands"])
    assert any("gen-session-fit-pack" in cmd for cmd in mpris_surface["commands"])

    reference_ids = {item["id"] for item in data["reference_patterns"]}
    assert "mpris-follow-control-lane" in reference_ids
    mpris_pattern = next(item for item in data["reference_patterns"] if item["id"] == "mpris-follow-control-lane")
    assert mpris_pattern["fit"] in {"good", "strong", "conditional"}
    assert "playerctl --follow" in mpris_pattern["learn_from"]
    assert any("gen-playerctl-pack" in cmd for cmd in mpris_pattern["commands"])
    assert any("gen-design-pack" in cmd for cmd in mpris_pattern["commands"])

    lesson_ids = {item["id"] for item in data["ecosystem_lessons"]}
    assert "mpris-standard-media-bus" in lesson_ids
    lesson = next(item for item in data["ecosystem_lessons"] if item["id"] == "mpris-standard-media-bus")
    assert lesson["fit"] in {"good", "strong", "conditional"}
    assert "MPRIS" in lesson["source_tools"]
    assert "playerctl" in lesson["source_tools"]
    assert any("gen-playerctl-pack" in cmd for cmd in lesson["commands"])
    assert any("gen-session-fit-pack" in cmd for cmd in lesson["commands"])



def test_plan_project_surfaces_include_notification_feedback_lane(tmp_path: Path) -> None:
    project_dir = _make_notification_project(tmp_path)

    res = runner.invoke(app, ["plan-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)

    surface_ids = {item["id"] for item in data["surface_choices"]}
    assert "desktop-notification-feedback" in surface_ids
    notification_surface = next(item for item in data["surface_choices"] if item["id"] == "desktop-notification-feedback")
    assert notification_surface["category"] == "feedback"
    assert notification_surface["fit"] in {"good", "strong", "conditional"}
    assert "notify_steps=1" in notification_surface["evidence"]
    assert "notification_signals=1" in notification_surface["evidence"]
    assert "actionable_notifications=1" in notification_surface["evidence"]
    assert "progress_notifications=1" in notification_surface["evidence"]
    assert any("gen-setup-pack" in cmd for cmd in notification_surface["commands"])

    reference_ids = {item["id"] for item in data["reference_patterns"]}
    assert "notification-daemon-feedback-lane" in reference_ids
    notification_pattern = next(item for item in data["reference_patterns"] if item["id"] == "notification-daemon-feedback-lane")
    assert notification_pattern["fit"] in {"good", "strong", "conditional"}
    assert "dunstify" in notification_pattern["learn_from"]
    assert any("gen-design-pack" in cmd for cmd in notification_pattern["commands"])

    lesson_ids = {item["id"] for item in data["ecosystem_lessons"]}
    assert "notifications-are-session-service-contract" in lesson_ids
    lesson = next(item for item in data["ecosystem_lessons"] if item["id"] == "notifications-are-session-service-contract")
    assert lesson["fit"] in {"good", "strong", "conditional"}
    assert "Desktop Notifications spec" in lesson["source_tools"]
    assert "XDG Notification portal" in lesson["source_tools"]
    assert any("gen-setup-pack" in cmd for cmd in lesson["commands"])


def test_plan_project_picker_surfaces_include_native_chooser_lane(tmp_path: Path) -> None:
    project_dir = _make_picker_project(tmp_path)

    res = runner.invoke(app, ["plan-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)

    surface_ids = {item["id"] for item in data["surface_choices"]}
    assert "picker-native-chooser" in surface_ids
    chooser_surface = next(item for item in data["surface_choices"] if item["id"] == "picker-native-chooser")
    assert chooser_surface["category"] == "launcher"
    assert chooser_surface["fit"] in {"good", "strong", "conditional"}
    assert any("export-launcher-script" in cmd for cmd in chooser_surface["commands"])
    assert any("export-rofi-mode" in cmd for cmd in chooser_surface["commands"])

    reference_ids = {item["id"] for item in data["reference_patterns"]}
    assert "script-mode-picker-lane" in reference_ids
    chooser_pattern = next(item for item in data["reference_patterns"] if item["id"] == "script-mode-picker-lane")
    assert chooser_pattern["fit"] in {"good", "strong", "conditional"}
    assert "rofi script mode" in chooser_pattern["learn_from"]
    assert any("export-launcher-script" in cmd for cmd in chooser_pattern["commands"])

    lesson_ids = {item["id"] for item in data["ecosystem_lessons"]}
    assert "picker-protocol-thin-launch-surface" in lesson_ids
    lesson = next(item for item in data["ecosystem_lessons"] if item["id"] == "picker-protocol-thin-launch-surface")
    assert lesson["fit"] in {"good", "strong", "conditional"}
    assert "rofi" in lesson["source_tools"]
    assert any("export-launcher-script" in cmd for cmd in lesson["commands"])


def test_plan_project_x11_surfaces_include_modal_wm_trigger_lane(tmp_path: Path) -> None:
    project_dir = _make_x11_mode_project(tmp_path)

    res = runner.invoke(app, ["plan-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)

    surface_ids = {item["id"] for item in data["surface_choices"]}
    assert "wm-modal-trigger-layer" in surface_ids
    modal_surface = next(item for item in data["surface_choices"] if item["id"] == "wm-modal-trigger-layer")
    assert modal_surface["category"] == "trigger"
    assert modal_surface["fit"] in {"good", "strong"}
    assert any("gen-wm-config" in cmd and "--mode-enter" in cmd for cmd in modal_surface["commands"])

    reference_ids = {item["id"] for item in data["reference_patterns"]}
    assert "wm-modal-submap-lane" in reference_ids
    modal_pattern = next(item for item in data["reference_patterns"] if item["id"] == "wm-modal-submap-lane")
    assert modal_pattern["fit"] in {"good", "strong"}
    assert any("export-wm-bundle" in cmd and "launcher-mode" in cmd for cmd in modal_pattern["commands"])

    lesson_ids = {item["id"] for item in data["ecosystem_lessons"]}
    assert "wm-modes-submaps-grouped-triggers" in lesson_ids
    lesson = next(item for item in data["ecosystem_lessons"] if item["id"] == "wm-modes-submaps-grouped-triggers")
    assert lesson["fit"] in {"good", "strong"}
    assert any("gen-wm-config" in cmd and "--mode-enter" in cmd for cmd in lesson["commands"])


def test_plan_project_json_includes_execution_waves_artifacts_and_setup(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(app, ["plan-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)

    text_gate = next(item for item in data["verification_gates"] if item["id"] == "text-injection")
    assert text_gate["gate_type"] in {"baseline", "capability"}
    assert any("gen-espanso" in cmd for cmd in text_gate["commands"])
    pointer_gate = next(item for item in data["verification_gates"] if item["id"] == "pointer-injection")
    assert pointer_gate["gate_type"] in {"helper-boundary", "capability", "portability"}
    assert any("preview-needle" in cmd for cmd in pointer_gate["commands"])
    assert pointer_gate["acceptance_checks"]

    reference_ids = {item["id"] for item in data["reference_patterns"]}
    assert "ahk-runner-core" in reference_ids
    assert "pulover-visual-studio" in reference_ids
    assert "espanso-forms-text-tier" in reference_ids
    assert "wm-bind-dispatch" in reference_ids
    assert "portal-helper-boundary" in reference_ids
    assert "daemonized-uinput-helper-lane" in reference_ids
    espanso_pattern = next(item for item in data["reference_patterns"] if item["id"] == "espanso-forms-text-tier")
    assert espanso_pattern["fit"] in {"good", "strong"}
    assert any("gen-espanso" in cmd for cmd in espanso_pattern["commands"])

    wave_ids = {item["id"] for item in data["implementation_waves"]}
    assert "foundation-contract" in wave_ids
    assert "text-and-prompt-tier" in wave_ids
    assert "visual-debug-loop" in wave_ids
    assert "dispatch-and-daemons" in wave_ids
    assert "release-gates" in wave_ids
    foundation_wave = next(item for item in data["implementation_waves"] if item["id"] == "foundation-contract")
    assert foundation_wave["order"] == 1
    assert any("plan-project" in cmd for cmd in foundation_wave["commands"])
    text_wave = next(item for item in data["implementation_waves"] if item["id"] == "text-and-prompt-tier")
    assert any("gen-espanso" in cmd for cmd in text_wave["commands"])
    visual_wave = next(item for item in data["implementation_waves"] if item["id"] == "visual-debug-loop")
    assert any("preview-needle" in cmd for cmd in visual_wave["commands"])
    release_wave = next(item for item in data["implementation_waves"] if item["id"] == "release-gates")
    assert release_wave["depends_on"]
    assert release_wave["borrowed_patterns"]

    artifact_ids = {item["id"] for item in data["artifact_blueprint"]}
    assert "espanso-package" in artifact_ids
    assert "selector-assets" in artifact_ids
    assert "desktop-entry" in artifact_ids or "launcher-entry" in artifact_ids
    espanso_artifact = next(item for item in data["artifact_blueprint"] if item["id"] == "espanso-package")
    assert espanso_artifact["category"] == "text-export"
    assert espanso_artifact["first_wave"]["id"] in {"foundation-contract", "text-and-prompt-tier"}
    assert any("gen-espanso" in cmd for cmd in espanso_artifact["generator_commands"])
    selector_artifact = next(item for item in data["artifact_blueprint"] if item["id"] == "selector-assets")
    assert selector_artifact["category"] == "asset-pack"
    assert selector_artifact["validation_commands"]

    deployable_ids = {item["id"] for item in data["deployable_surfaces"]}
    assert "text-automation" in deployable_ids
    assert "launcher-entrypoints" in deployable_ids
    assert "watcher-services" in deployable_ids
    assert "selector-debug-pack" in deployable_ids
    text_surface = next(item for item in data["deployable_surfaces"] if item["id"] == "text-automation")
    assert text_surface["category"] == "text"
    assert text_surface["first_wave"]["id"] in {"foundation-contract", "text-and-prompt-tier"}
    assert any("gen-espanso" in cmd for cmd in text_surface["generator_commands"])
    launcher_surface = next(item for item in data["deployable_surfaces"] if item["id"] == "launcher-entrypoints")
    assert launcher_surface["artifacts"]
    assert launcher_surface["entrypoint"]

    recipe_ids = {item["id"] for item in data["setup_recipes"]}
    assert "text-package-install" in recipe_ids
    assert "launcher-entrypoint-install" in recipe_ids
    assert "wm-trigger-install" in recipe_ids
    assert "watcher-service-install" in recipe_ids
    assert "selector-debug-review" in recipe_ids
    text_recipe = next(item for item in data["setup_recipes"] if item["id"] == "text-package-install")
    assert text_recipe["audience"] == "author/operator"
    assert text_recipe["install_steps"]
    assert any("gen-espanso" in cmd for cmd in text_recipe["generator_commands"])
    service_recipe = next(item for item in data["setup_recipes"] if item["id"] == "watcher-service-install")
    assert service_recipe["verify_steps"]

    step_ids = {item["id"] for item in data["next_steps"]}
    assert "cleanup-drafts" in step_ids
    assert "selector-assets" in step_ids
    assert "expand-presets" in step_ids
    assert "app-scoping" in step_ids





def test_plan_project_input_lane_dossier_uses_session_truth(tmp_path: Path, monkeypatch) -> None:
    project_dir = _make_project(tmp_path)

    import vhk.cli as cli_mod

    monkeypatch.setattr(
        cli_mod,
        "_validation_session_capability_matrix",
        lambda: {
            "screen_capture": {"status": "ok", "mechanisms": ["portal:Screenshot"], "recommended": "portal:Screenshot", "notes": [], "portal_backends": ["gtk"]},
            "text_injection": {"status": "ok", "mechanisms": ["wtype", "clipboard"], "recommended": "wtype", "notes": [], "portal_backends": []},
            "pointer_injection": {"status": "limited", "mechanisms": ["portal:RemoteDesktop(pointer)"], "recommended": None, "notes": ["interactive"], "portal_backends": ["gtk"]},
            "global_hotkeys": {"status": "missing", "mechanisms": [], "recommended": None, "notes": [], "portal_backends": []},
            "window_introspection": {"status": "ok", "mechanisms": ["hyprctl"], "recommended": "hyprctl", "notes": [], "portal_backends": []},
            "input_capture": {"status": "limited", "mechanisms": ["portal:InputCapture"], "recommended": None, "notes": ["trigger-based"], "portal_backends": ["gtk"]},
        },
    )

    res = runner.invoke(app, ["plan-project", str(project_dir), "--json"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)

    dossier = dict(data["input_lane_dossier"])
    portal_lane = next(item for item in dossier["lanes"] if item["id"] == "portal-permissioned-input")
    assert portal_lane["fit"] in {"good", "strong"}
    assert any(entry == "input_capture=limited" for entry in portal_lane["session_capabilities"])
    assert any("mechanism=portal:remotedesktop(pointer)" == entry for entry in portal_lane["evidence"])

    wtype_lane = next(item for item in dossier["lanes"] if item["id"] == "virtual-keyboard-text-fastpath")
    assert wtype_lane["fit"] in {"conditional", "good", "strong"}
    assert any(entry == "recommended=wtype" for entry in wtype_lane["evidence"])

    assert "portal-permissioned-input" in dossier["recommended_lane_ids"]

    promotion_input_lanes = {item["export_surface_id"]: item for item in data["promotion_input_lane_plan"]}
    assert promotion_input_lanes["text-package-export"]["primary_input_lane_id"] == "clipboard-text-lane"
    assert promotion_input_lanes["text-package-export"]["shipping_posture"] == "flagship"


def test_plan_project_includes_session_mismatch_recommendation(tmp_path: Path, monkeypatch) -> None:
    project_dir = _make_project(tmp_path)

    import vhk.cli as cli_mod

    monkeypatch.setattr(
        cli_mod,
        "_validation_session_capability_matrix",
        lambda: {
            "screen_capture": {"status": "ok", "mechanisms": ["portal:Screenshot"], "recommended": "portal:Screenshot", "notes": [], "portal_backends": ["gtk"]},
            "text_injection": {"status": "ok", "mechanisms": ["wtype"], "recommended": "wtype", "notes": [], "portal_backends": []},
            "pointer_injection": {"status": "limited", "mechanisms": ["portal:RemoteDesktop(pointer)"], "recommended": None, "notes": ["interactive"], "portal_backends": ["gtk"]},
            "global_hotkeys": {"status": "missing", "mechanisms": [], "recommended": None, "notes": [], "portal_backends": []},
            "window_introspection": {"status": "ok", "mechanisms": ["hyprctl"], "recommended": "hyprctl", "notes": [], "portal_backends": []},
            "input_capture": {"status": "missing", "mechanisms": [], "recommended": None, "notes": [], "portal_backends": []},
        },
    )

    res = runner.invoke(app, ["plan-project", str(project_dir), "--json"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)

    assert data["session_capabilities"]["pointer_injection"]["status"] == "limited"
    issues = data["session_issues"]
    assert any(item.get("capability") == "global_hotkeys" for item in issues)
    assert any(item.get("capability") == "pointer_injection" for item in issues)

    rec_ids = {item["id"] for item in data["recommendations"]}
    assert "session-mismatch" in rec_ids
    assert "capture-without-pointer" in rec_ids

    architecture_ids = {item["id"] for item in data["architecture_map"]["components"]}
    assert "wayland-boundary" in architecture_ids

    target_ids = {item["id"] for item in data["integration_targets"]}
    assert "wayland-injection" in target_ids

    playbooks = {item["id"]: item for item in data["playbooks"]}
    assert "deployment-audit" in playbooks
    assert playbooks["deployment-audit"]["priority"] == "high"

    profile_ids = {item["id"] for item in data["deployment_profiles"]}
    assert "wayland-helper-boundary" in profile_ids
    wayland_profile = next(item for item in data["deployment_profiles"] if item["id"] == "wayland-helper-boundary")
    assert "pointer_injection" in wayland_profile["blocking_capabilities"]

    desktop_target_ids = {item["id"] for item in data["desktop_targets"]}
    assert "helper-boundary-wayland" in desktop_target_ids
    helper_target = next(item for item in data["desktop_targets"] if item["id"] == "helper-boundary-wayland")
    assert "pointer_injection" in helper_target["blocking_capabilities"]
    assert helper_target["fit"] in {"good", "strong"}

    portal_choice = next(item for item in data["surface_choices"] if item["id"] == "portal-global-shortcuts")
    assert portal_choice["category"] == "trigger"
    assert portal_choice["fit"] in {"weak", "conditional", "good"}

    env_ids = {item["id"] for item in data["environment_diffs"]}
    assert "gnome-wayland" in env_ids
    helper_env = next(item for item in data["environment_diffs"] if item["id"] == "hyprland-conservative")
    assert "pointer_injection" in helper_env["blocking_capabilities"]

    gap_ids = {item["id"] for item in data["portability_gaps"]}
    assert "hyprland-conservative" in gap_ids
    helper_gap = next(item for item in data["portability_gaps"] if item["id"] == "hyprland-conservative")
    assert "pointer_injection" in helper_gap["newly_blocked_capabilities"] or "pointer_injection" in helper_gap["degraded_capabilities"]

    portability_playbook_ids = {item["id"] for item in data["portability_playbooks"]}
    assert "hyprland-conservative" in portability_playbook_ids
    helper_playbook = next(item for item in data["portability_playbooks"] if item["id"] == "hyprland-conservative")
    artifact_ids = {artifact["id"] for artifact in helper_playbook["artifacts"]}
    assert "pointer-helper-boundary" in artifact_ids
    assert any("validate" in cmd for cmd in helper_playbook["commands"])

    toolchain_ids = {item["id"] for item in data["toolchain_choices"]}
    assert "pointer-injection" in toolchain_ids
    assert "input-capture" in toolchain_ids
    pointer_toolchain = next(item for item in data["toolchain_choices"] if item["id"] == "pointer-injection")
    assert pointer_toolchain["status"] == "limited"
    assert pointer_toolchain["recommended_toolchain"]
    assert pointer_toolchain["fallback_toolchains"]
    assert "dotoolc" in pointer_toolchain["fallback_toolchains"]

    coverage_ids = {item["id"] for item in data["capability_coverage"]}
    assert "pointer-injection" in coverage_ids
    assert "global-hotkeys" in coverage_ids
    pointer_coverage = next(item for item in data["capability_coverage"] if item["id"] == "pointer-injection")
    assert pointer_coverage["current_status"] == "limited"
    assert pointer_coverage["coverage_class"] in {"helper-boundary", "conditional"}
    assert pointer_coverage["commands"]
    hotkey_coverage = next(item for item in data["capability_coverage"] if item["id"] == "global-hotkeys")
    assert hotkey_coverage["current_status"] == "missing"
    assert hotkey_coverage["coverage_class"] in {"desktop-boundary", "conditional"}

    gate_ids = {item["id"] for item in data["verification_gates"]}
    assert "pointer-injection" in gate_ids
    assert "global-hotkeys" in gate_ids
    pointer_gate = next(item for item in data["verification_gates"] if item["id"] == "pointer-injection")
    assert pointer_gate["priority"] == "high"
    assert pointer_gate["gate_type"] in {"helper-boundary", "capability"}
    assert any("doctor --json" in cmd for cmd in pointer_gate["commands"])
    hotkey_gate = next(item for item in data["verification_gates"] if item["id"] == "global-hotkeys")
    assert hotkey_gate["priority"] == "high"
    assert hotkey_gate["gate_type"] in {"desktop-profile", "capability"}
    assert hotkey_gate["commands"]

    reference_ids = {item["id"] for item in data["reference_patterns"]}
    assert "portal-helper-boundary" in reference_ids
    assert "portal-session-catalog-lane" in reference_ids
    assert "launcher-hub-catalog" in reference_ids
    assert "wtype-narrow-wayland-text-lane" in reference_ids
    assert "daemonized-uinput-helper-lane" in reference_ids
    helper_pattern = next(item for item in data["reference_patterns"] if item["id"] == "portal-helper-boundary")
    assert helper_pattern["fit"] in {"good", "strong", "conditional"}
    assert any("doctor --json" in cmd for cmd in helper_pattern["commands"])
    portal_catalog_pattern = next(item for item in data["reference_patterns"] if item["id"] == "portal-session-catalog-lane")
    assert portal_catalog_pattern["fit"] in {"weak", "conditional", "good", "strong"}
    assert any("gen-portal-shortcuts-spec" in cmd for cmd in portal_catalog_pattern["commands"])
    launcher_pattern = next(item for item in data["reference_patterns"] if item["id"] == "launcher-hub-catalog")
    assert launcher_pattern["commands"]
    assert "Kando" in launcher_pattern["learn_from"]
    wtype_pattern = next(item for item in data["reference_patterns"] if item["id"] == "wtype-narrow-wayland-text-lane")
    assert wtype_pattern["fit"] in {"conditional", "good", "strong"}
    assert any("gen-espanso" in cmd for cmd in wtype_pattern["commands"])
    daemon_pattern = next(item for item in data["reference_patterns"] if item["id"] == "daemonized-uinput-helper-lane")
    assert daemon_pattern["fit"] in {"conditional", "good", "strong"}
    assert any("gen-dotoold-service" in cmd for cmd in daemon_pattern["commands"])

    wave_ids = {item["id"] for item in data["implementation_waves"]}
    assert "foundation-contract" in wave_ids
    assert "dispatch-and-daemons" in wave_ids
    foundation_wave = next(item for item in data["implementation_waves"] if item["id"] == "foundation-contract")
    assert foundation_wave["priority"] == "high"
    assert any("doctor --json" in cmd for cmd in foundation_wave["commands"])
    dispatch_wave = next(item for item in data["implementation_waves"] if item["id"] == "dispatch-and-daemons")
    assert any("gen-keyd-config" in cmd or "gen-vhk-busd-service" in cmd for cmd in dispatch_wave["commands"])
    release_wave = next(item for item in data["implementation_waves"] if item["id"] == "release-gates")
    assert release_wave["validation"]
    assert any(pattern["id"] == "portal-helper-boundary" for pattern in release_wave["borrowed_patterns"])

    artifact_ids = {item["id"] for item in data["artifact_blueprint"]}
    assert "pointer-helper-boundary" in artifact_ids
    assert "systemd-user-units" in artifact_ids
    helper_artifact = next(item for item in data["artifact_blueprint"] if item["id"] == "pointer-helper-boundary")
    assert helper_artifact["category"] == "audit"
    assert helper_artifact["generator_commands"]
    service_artifact = next(item for item in data["artifact_blueprint"] if item["id"] == "systemd-user-units")
    assert service_artifact["category"] == "service"
    assert any("gen-vhk-busd-service" in cmd for cmd in service_artifact["generator_commands"])

    deployable_ids = {item["id"] for item in data["deployable_surfaces"]}
    assert "capability-audit-pack" in deployable_ids
    assert "watcher-services" in deployable_ids
    audit_surface = next(item for item in data["deployable_surfaces"] if item["id"] == "capability-audit-pack")
    assert audit_surface["category"] == "audit"
    assert "pointer_injection" in audit_surface["related_capabilities"]
    assert audit_surface["notes"]
    service_surface = next(item for item in data["deployable_surfaces"] if item["id"] == "watcher-services")
    assert any("gen-vhk-busd-service" in cmd for cmd in service_surface["generator_commands"])

    recipe_ids = {item["id"] for item in data["setup_recipes"]}
    assert "capability-audit-review" in recipe_ids
    assert "remap-helper-install" in recipe_ids
    assert "watcher-service-install" in recipe_ids
    audit_recipe = next(item for item in data["setup_recipes"] if item["id"] == "capability-audit-review")
    assert audit_recipe["category"] == "audit"
    assert "pointer_injection" in audit_recipe["related_capabilities"]
    assert audit_recipe["rollback_steps"]
    remap_recipe = next(item for item in data["setup_recipes"] if item["id"] == "remap-helper-install")
    assert remap_recipe["playbooks"]

    seam_ids = {item["id"] for item in data["runtime_seams"]}
    assert "runner-core" in seam_ids
    assert "trigger-surface" in seam_ids
    assert "text-surface" in seam_ids
    assert "selector-asset-pack" in seam_ids
    assert "watcher-service-plane" in seam_ids
    assert "helper-boundary" in seam_ids
    helper_seam = next(item for item in data["runtime_seams"] if item["id"] == "helper-boundary")
    assert helper_seam["contracts"]
    assert helper_seam["commands"]

    lesson_ids = {item["id"] for item in data["ecosystem_lessons"]}
    assert "ahk-runner-diagnostics" in lesson_ids
    assert "pulover-recorder-cleanup" in lesson_ids
    assert "espanso-text-surface" in lesson_ids
    assert "menu-catalog-control-surface" in lesson_ids
    assert "autokey-session-honesty" in lesson_ids
    assert "xremap-app-context-bridge" in lesson_ids
    assert "keyd-thin-trigger-boundary" in lesson_ids
    assert "portal-stable-action-catalog" in lesson_ids
    assert "daemonized-helper-lifecycle" in lesson_ids
    assert "libei-helper-seam" in lesson_ids
    assert "wtype-virtual-keyboard-boundary" in lesson_ids
    portal_lesson = next(item for item in data["ecosystem_lessons"] if item["id"] == "portal-stable-action-catalog")
    assert portal_lesson["source_tools"]
    assert portal_lesson["product_implication"]
    wtype_lesson = next(item for item in data["ecosystem_lessons"] if item["id"] == "wtype-virtual-keyboard-boundary")
    assert wtype_lesson["fit"] in {"good", "strong"}
    helper_lifecycle_lesson = next(item for item in data["ecosystem_lessons"] if item["id"] == "daemonized-helper-lifecycle")
    assert helper_lifecycle_lesson["fit"] in {"good", "strong"}
    assert any("gen-dotoold-service" in cmd for cmd in helper_lifecycle_lesson["commands"])
    menu_lesson = next(item for item in data["ecosystem_lessons"] if item["id"] == "menu-catalog-control-surface")
    assert "Kando" in menu_lesson["source_tools"]

    step_ids = {item["id"] for item in data["next_steps"]}
    assert "desktop-profiles" in step_ids


def test_plan_project_table_includes_lanes_and_playbooks(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(app, ["plan-project", str(project_dir), "--no-session-check"])
    assert res.exit_code == 0, res.output
    assert "Product lanes" in res.output
    assert "Architecture map" in res.output
    assert "Suggested stack profiles" in res.output
    assert "Runtime seams" in res.output
    assert "Ecosystem lessons" in res.output
    assert "Desktop target matrix" in res.output
    assert "Candidate integration surfaces" in res.output
    assert "Environment comparison" in res.output
    assert "Portability gaps" in res.output
    assert "Portability playbooks" in res.output
    assert "Concrete toolchain choices" in res.output
    assert "Capability coverage matrix" in res.output
    assert "Verification gates" in res.output
    assert "Implementation waves" in res.output
    assert "Artifact blueprint" in res.output
    assert "Deployable surfaces" in res.output
    assert "Setup recipes" in res.output
    assert "Reference patterns" in res.output
    assert "Implementation playbooks" in res.output
    assert "Performance hotspots" in res.output
    assert "Macro runtime profile" in res.output
    assert "Promotion authority envelopes" in res.output


def _make_route_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "route_proj"
    (project_dir / "macros").mkdir(parents=True)

    (project_dir / "macros" / "snippet.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "snippet",
                "steps": [
                    {"type": "TypeText", "text": "Thanks for the update.\nNext step:\tShip it."},
                ],
            },
            sort_keys=False,
        )
    )

    (project_dir / "macros" / "launcher.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "launcher",
                "steps": [
                    {"type": "PromptForm", "title": "Open item", "fields": [{"name": "target", "label": "Target"}]},
                    {"type": "RunShell", "command": "echo ${target.target}"},
                ],
            },
            sort_keys=False,
        )
    )

    (project_dir / "macros" / "palette_key.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "palette_key",
                "steps": [
                    {"type": "Key", "keys": "ctrl+shift+p"},
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
                    {"type": "WaitForImage", "needle_path": "assets/button.png", "timeout_ms": 3000},
                    {"type": "MouseClickAt", "x": 20, "y": 40},
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
                    {"type": "RunShell", "command": "echo sync"},
                ],
            },
            sort_keys=False,
        )
    )

    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "route-proj",
                "settings": {"desktop_backend": "wayland", "event_log": False},
                "bindings": [
                    {"keys": "Mod4+P", "macro": "palette_key"},
                    {"keys": "Mod4+V", "macro": "vision"},
                ],
                "hotstrings": [{"trigger": ":ty", "macro": "snippet"}],
                "bus_watchers": [{"name": "sync-watch", "event": "proj.sync", "macro": "sync"}],
            },
            sort_keys=False,
        )
    )
    return project_dir



def test_plan_project_json_includes_macro_route_profiles(tmp_path: Path) -> None:
    project_dir = _make_route_project(tmp_path)

    res = runner.invoke(app, ["plan-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)

    routes = {item["macro"]: item for item in data["macro_route_profiles"]}

    assert routes["snippet"]["route_id"] == "text-tier"
    assert routes["snippet"]["primary_activation_route_id"] == "text-surface-route"
    assert routes["snippet"]["fit"] in {"strong", "good"}
    assert "Espanso" in routes["snippet"]["learn_from"]

    assert routes["palette_key"]["route_id"] == "remapper-tier"
    assert routes["palette_key"]["primary_activation_route_id"] in {"remapper-route", "native-trigger-route"}
    assert "keyd" in routes["palette_key"]["execution_surface"]

    assert routes["vision"]["route_id"] == "helper-boundary-runner"
    assert routes["vision"]["primary_activation_route_id"] in {"portal-shortcuts-route", "native-trigger-route", "remapper-route", "launcher-entrypoint"}
    assert "pointer_injection" in routes["vision"]["capabilities"]
    assert "screen_capture" in routes["vision"]["capabilities"]
    assert routes["vision"]["fit"] in {"conditional", "good"}

    assert routes["sync"]["route_id"] == "watcher-service"
    assert routes["sync"]["primary_activation_route_id"] == "watcher-service-route"
    assert routes["sync"]["fit"] in {"strong", "good"}

    assert routes["launcher"]["route_id"] == "launcher-entry"
    assert routes["launcher"]["primary_activation_route_id"] == "launcher-entrypoint"

    export_candidates = {(item["macro"], item["export_surface_id"]): item for item in data["macro_export_candidates"]}
    assert export_candidates[("snippet", "text-package-export")]["title"] == "Text package candidate"
    assert "Espanso" in export_candidates[("snippet", "text-package-export")]["tool_family"]
    assert export_candidates[("palette_key", "remapper-export")]["primary_activation_route_id"] in {"remapper-route", "native-trigger-route"}
    assert "keyd" in export_candidates[("palette_key", "remapper-export")]["tool_family"]
    assert export_candidates[("vision", "helper-route-dossier")]["fit"] in {"conditional", "good"}
    assert export_candidates[("sync", "watcher-service-export")]["title"] == "Watcher service candidate"

    route_portfolio = {item["route_id"]: item for item in data["route_portfolio"]}
    assert route_portfolio["text-tier"]["macro_count"] == 1
    assert route_portfolio["text-tier"]["dominant_fit"] in {"strong", "good"}
    assert "snippet" in route_portfolio["text-tier"]["example_macros"]
    assert "text-surface-route" in route_portfolio["text-tier"]["top_activation_routes"]
    assert route_portfolio["helper-boundary-runner"]["macro_count"] == 1
    assert "vision" in route_portfolio["helper-boundary-runner"]["example_macros"]

    promotion_plan = {item["export_surface_id"]: item for item in data["export_promotion_plan"]}
    assert promotion_plan["text-package-export"]["priority"] == "high"
    assert "snippet" in promotion_plan["text-package-export"]["macros"]
    assert any("gen-espanso" in cmd for cmd in promotion_plan["text-package-export"]["commands"])
    assert promotion_plan["remapper-export"]["priority"] == "high"
    assert "palette_key" in promotion_plan["remapper-export"]["macros"]
    assert "keyd" in promotion_plan["remapper-export"]["tool_family"]
    assert promotion_plan["helper-route-dossier"]["priority"] == "medium"
    assert "vision" in promotion_plan["helper-route-dossier"]["macros"]

    promotion_input_lanes = {item["export_surface_id"]: item for item in data["promotion_input_lane_plan"]}
    assert promotion_input_lanes["text-package-export"]["shipping_posture"] == "flagship"
    assert promotion_input_lanes["text-package-export"]["primary_input_lane_id"] == "clipboard-text-lane"
    assert "text-surface-service" in promotion_input_lanes["text-package-export"]["host_requirement_ids"]
    assert any("gen-espanso" in cmd for cmd in promotion_input_lanes["text-package-export"]["commands"])
    assert promotion_input_lanes["remapper-export"]["shipping_posture"] in {"specialist", "reviewed"}
    assert promotion_input_lanes["remapper-export"]["primary_input_lane_id"] == "daemon-backed-uinput-playback"
    assert "uinput-permissions" in promotion_input_lanes["remapper-export"]["host_requirement_ids"]
    assert promotion_input_lanes["helper-route-dossier"]["shipping_posture"] == "reviewed"
    assert promotion_input_lanes["helper-route-dossier"]["primary_input_lane_id"] in {"daemon-backed-uinput-playback", "portal-permissioned-input"}
    assert promotion_input_lanes["watcher-service-export"]["shipping_posture"] == "orthogonal"
    assert promotion_input_lanes["watcher-service-export"]["primary_input_lane_id"] is None

    promotion_activation_routes = {item["export_surface_id"]: item for item in data["promotion_activation_route_plan"]}
    assert promotion_activation_routes["text-package-export"]["startup_posture"] == "resident"
    assert promotion_activation_routes["text-package-export"]["primary_activation_route_id"] == "text-surface-route"
    assert promotion_activation_routes["text-package-export"]["primary_activation_kind"] == "user_service"
    assert "text-surface-service" in promotion_activation_routes["text-package-export"]["host_requirement_ids"]
    assert any("gen-espanso" in cmd for cmd in promotion_activation_routes["text-package-export"]["commands"])
    assert promotion_activation_routes["remapper-export"]["primary_activation_route_id"] in {"remapper-route", "native-trigger-route"}
    assert promotion_activation_routes["watcher-service-export"]["primary_activation_route_id"] == "watcher-service-route"
    assert promotion_activation_routes["watcher-service-export"]["startup_posture"] == "resident"
    assert promotion_activation_routes["launcher-surface-export"]["primary_activation_route_id"] == "launcher-entrypoint"
    assert promotion_activation_routes["launcher-surface-export"]["startup_posture"] == "launcher-first"

    promotion_operator_controls = {item["export_surface_id"]: item for item in data["promotion_operator_control_plan"]}
    assert promotion_operator_controls["text-package-export"]["control_posture"] == "service-managed"
    assert promotion_operator_controls["text-package-export"]["primary_control_lane_id"] == "text-service-control"
    assert "text-surface-service" in promotion_operator_controls["text-package-export"]["host_requirement_ids"]
    assert any("espanso status" in cmd for cmd in promotion_operator_controls["text-package-export"]["commands"])
    assert promotion_operator_controls["helper-route-dossier"]["control_posture"] in {"daemon-reviewed", "session-managed"}
    assert promotion_operator_controls["watcher-service-export"]["control_posture"] == "service-managed"
    assert promotion_operator_controls["watcher-service-export"]["primary_control_lane_id"] == "watcher-service-control"
    assert promotion_operator_controls["launcher-surface-export"]["control_posture"] == "manual-entry"

    promotion_recovery = {item["export_surface_id"]: item for item in data["promotion_recovery_plan"]}
    assert promotion_recovery["text-package-export"]["recovery_posture"] == "service-restart"
    assert promotion_recovery["text-package-export"]["primary_recovery_lane_id"] == "text-service-recovery"
    assert any("espanso restart" in cmd for cmd in promotion_recovery["text-package-export"]["commands"])
    assert promotion_recovery["remapper-export"]["recovery_posture"] in {"rollback-first", "reload-and-smoke"}
    assert promotion_recovery["helper-route-dossier"]["recovery_posture"] in {"daemon-reset", "session-recreate"}
    assert promotion_recovery["watcher-service-export"]["recovery_posture"] == "service-restart"
    assert promotion_recovery["launcher-surface-export"]["recovery_posture"] == "manual-smoke"

    promotion_verification = {item["export_surface_id"]: item for item in data["promotion_verification_plan"]}
    assert promotion_verification["text-package-export"]["verification_posture"] == "service-smoke"
    assert promotion_verification["text-package-export"]["primary_verification_lane_id"] == "text-surface-verification"
    assert any("espanso status" in cmd for cmd in promotion_verification["text-package-export"]["commands"])
    assert "text_injection" in promotion_verification["text-package-export"]["verification_gate_ids"]
    assert promotion_verification["remapper-export"]["verification_posture"] == "input-event-smoke"
    assert promotion_verification["helper-route-dossier"]["verification_posture"] in {"portal-proof", "daemon-proof"}
    assert promotion_verification["watcher-service-export"]["verification_posture"] == "event-flow-smoke"
    assert promotion_verification["launcher-surface-export"]["verification_posture"] == "launch-smoke"

    promotion_performance = {item["export_surface_id"]: item for item in data["promotion_performance_plan"]}
    assert promotion_performance["text-package-export"]["performance_posture"] == "throughput-first"
    assert promotion_performance["text-package-export"]["primary_performance_lane_id"] == "clipboard-text-throughput"
    assert "typed-text-throughput" in promotion_performance["text-package-export"]["performance_hotspot_ids"]
    assert any("gen-espanso" in cmd for cmd in promotion_performance["text-package-export"]["commands"])
    assert promotion_performance["remapper-export"]["performance_posture"] == "low-latency-edge"
    assert promotion_performance["helper-route-dossier"]["performance_posture"] in {"warm-daemon", "consent-bound-async"}
    assert promotion_performance["watcher-service-export"]["performance_posture"] == "event-pipeline"
    assert promotion_performance["launcher-surface-export"]["performance_posture"] == "launch-to-dispatch"
    assert data["promotion_performance_summary"]["throughput_first_count"] >= 1

    promotion_dispatch_budgets = {item["export_surface_id"]: item for item in data["promotion_dispatch_budget_plan"]}
    assert promotion_dispatch_budgets["text-package-export"]["dispatch_posture"] == "service-resident"
    assert promotion_dispatch_budgets["text-package-export"]["primary_dispatch_lane_id"] == "resident-text-service"
    assert "resident text/package surface" in promotion_dispatch_budgets["text-package-export"]["steady_state_path"].lower()
    assert promotion_dispatch_budgets["remapper-export"]["dispatch_posture"] == "edge-resident"
    assert promotion_dispatch_budgets["remapper-export"]["primary_dispatch_lane_id"] == "resident-remapper-edge"
    assert promotion_dispatch_budgets["helper-route-dossier"]["dispatch_posture"] in {"daemon-warm", "session-resume"}
    assert promotion_dispatch_budgets["watcher-service-export"]["dispatch_posture"] == "service-resident"
    assert promotion_dispatch_budgets["launcher-surface-export"]["dispatch_posture"] == "launch-cold"
    assert data["promotion_dispatch_budget_summary"]["entry_count"] >= 4
    assert data["promotion_dispatch_budget_summary"]["service_resident_count"] >= 1

    promotion_authority = {item["export_surface_id"]: item for item in data["promotion_authority_envelope_plan"]}
    assert promotion_authority["text-package-export"]["authority_posture"] == "session-userland"
    assert promotion_authority["text-package-export"]["primary_authority_lane_id"] == "session-text-service-authority"
    assert "user-session text service" in promotion_authority["text-package-export"]["authority_owner"].lower()
    assert promotion_authority["remapper-export"]["authority_posture"] == "input-edge-privileged"
    assert promotion_authority["remapper-export"]["primary_authority_lane_id"] == "evdev-uinput-edge-authority"
    assert promotion_authority["helper-route-dossier"]["authority_posture"] in {"desktop-mediated", "helper-daemon-privileged"}
    assert promotion_authority["watcher-service-export"]["authority_posture"] == "session-userland"
    assert promotion_authority["launcher-surface-export"]["authority_posture"] == "launch-userland"
    assert data["promotion_authority_envelope_summary"]["entry_count"] >= 4
    assert data["promotion_authority_envelope_summary"]["session_userland_count"] >= 1

    promotion_waves = {item["priority"]: item for item in data["promotion_waves"]}
    assert promotion_waves["high"]["order"] == 1
    assert "text-package-export" in promotion_waves["high"]["export_surface_ids"]
    assert "remapper-export" in promotion_waves["high"]["export_surface_ids"]
    assert "text-tier" in promotion_waves["high"]["route_ids"]
    assert "remapper-tier" in promotion_waves["high"]["route_ids"]
    assert any("gen-espanso" in cmd for cmd in promotion_waves["high"]["commands"])
    assert promotion_waves["medium"]["order"] == 2
    assert "helper-route-dossier" in promotion_waves["medium"]["export_surface_ids"]

    promotion_readiness = {item["export_surface_id"]: item for item in data["promotion_readiness"]}
    assert promotion_readiness["text-package-export"]["readiness_status"] == "review"
    assert "text_injection" in promotion_readiness["text-package-export"]["required_capabilities"]
    assert promotion_readiness["remapper-export"]["readiness_status"] == "review"
    assert promotion_readiness["watcher-service-export"]["readiness_status"] == "ready"
    assert promotion_readiness["helper-route-dossier"]["readiness_status"] in {"review", "blocked"}
    assert "pointer_injection" in promotion_readiness["helper-route-dossier"]["required_capabilities"]

    readiness_summary = data["promotion_readiness_summary"]
    assert readiness_summary["surface_count"] >= 4
    assert readiness_summary["review_count"] >= 2
    assert readiness_summary["ready_count"] >= 1

    promotion_gates = {item["gate_id"]: item for item in data["promotion_gates"]}
    assert promotion_gates["specialist-surface-gate"]["status"] in {"review", "fail"}
    assert "text-package-export" in promotion_gates["specialist-surface-gate"]["affected_surfaces"]
    assert promotion_gates["helper-boundary-gate"]["status"] in {"review", "fail"}
    assert "helper-route-dossier" in promotion_gates["helper-boundary-gate"]["affected_surfaces"]
    assert promotion_gates["claim-discipline-gate"]["status"] in {"review", "fail"}

    gate_summary = data["promotion_gate_summary"]
    assert gate_summary["gate_count"] >= 3
    assert gate_summary["review_count"] + gate_summary["fail_count"] >= 1

    promotion_backlog = {item["task_id"]: item for item in data["promotion_backlog"]}
    assert "surface:text-package-export" in promotion_backlog
    assert "surface:watcher-service-export" in promotion_backlog
    assert "surface:helper-route-dossier" in promotion_backlog
    assert "gate:claim-discipline-gate" in promotion_backlog
    assert promotion_backlog["surface:text-package-export"]["kind"] in {"promote", "review"}
    assert promotion_backlog["surface:text-package-export"]["commands"]
    assert promotion_backlog["surface:helper-route-dossier"]["queue_state"] in {"blocked", "review"}
    assert promotion_backlog["gate:claim-discipline-gate"]["kind"] == "gate"
    assert promotion_backlog["gate:claim-discipline-gate"]["queue_state"] in {"blocked", "review"}

    backlog_summary = data["promotion_backlog_summary"]
    assert backlog_summary["task_count"] >= 4
    assert backlog_summary["review_count"] + backlog_summary["blocked_count"] >= 1

    promotion_evidence = {item["evidence_id"]: item for item in data["promotion_evidence"]}
    assert "surface:text-package-export" in promotion_evidence
    assert promotion_evidence["surface:text-package-export"]["subject_kind"] == "surface"
    assert promotion_evidence["surface:text-package-export"]["evidence_status"] in {"missing", "partial"}
    assert "docs/VHK_SETUP_GUIDE.md" in promotion_evidence["surface:text-package-export"]["required_artifacts"]
    assert "gate:claim-discipline-gate" in promotion_evidence
    assert promotion_evidence["gate:claim-discipline-gate"]["subject_kind"] == "gate"
    assert "docs/VHK_TARGET_CLAIMS.yaml" in promotion_evidence["gate:claim-discipline-gate"]["required_artifacts"]

    evidence_summary = data["promotion_evidence_summary"]
    assert evidence_summary["entry_count"] >= 4
    assert evidence_summary["partial_count"] + evidence_summary["missing_count"] >= 1


def test_plan_project_surfaces_planner_claim_witness_when_session_check_is_enabled(tmp_path: Path, monkeypatch) -> None:
    project_dir = _make_project(tmp_path)

    import vhk.cli as cli_mod

    capability_matrix = {
        "screen_capture": {"status": "ok", "recommended": "portal:Screenshot", "mechanisms": ["portal:Screenshot"], "notes": [], "portal_backends": ["gnome"]},
        "text_injection": {"status": "limited", "recommended": None, "mechanisms": ["portal:RemoteDesktop(keyboard)"], "notes": ["interactive path"], "portal_backends": ["gnome"]},
        "pointer_injection": {"status": "ok", "recommended": "dotoolc", "mechanisms": ["dotoolc"], "notes": [], "portal_backends": ["gnome"]},
        "global_hotkeys": {"status": "ok", "recommended": "portal:GlobalShortcuts", "mechanisms": ["portal:GlobalShortcuts"], "notes": [], "portal_backends": ["gnome"]},
        "window_introspection": {"status": "ok", "recommended": "hyprctl", "mechanisms": ["hyprctl"], "notes": [], "portal_backends": []},
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

    res = runner.invoke(app, ["plan-project", str(project_dir), "--json"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)

    assert data["planner_claim_witness"]["status"] == "drifted"
    assert data["host_truth"]["overall_status"] == "blocked"
    assert data["portal_route_contract"]["xdg_current_desktop"] == "sway"
    gnome = next(item for item in data["planner_target_claims"] if item["target"] == "gnome-wayland")
    assert gnome["current_host_fit"]["status"] == "drifted"

    table_res = runner.invoke(app, ["plan-project", str(project_dir)])
    assert table_res.exit_code == 0, table_res.output
    assert "Current host proof posture" in table_res.output
    assert "Planner target claims" in table_res.output
    assert "Promotion recovery lanes" in table_res.output


def test_plan_project_can_pin_explicit_evidence_lane(tmp_path: Path, monkeypatch) -> None:
    project_dir = _make_project(tmp_path)

    import vhk.cli as cli_mod

    capability_matrix = {
        "screen_capture": {"status": "ok", "recommended": "portal:Screenshot", "mechanisms": ["portal:Screenshot"], "notes": [], "portal_backends": ["gnome"]},
        "text_injection": {"status": "limited", "recommended": None, "mechanisms": ["portal:RemoteDesktop(keyboard)"], "notes": ["interactive path"], "portal_backends": ["gnome"]},
        "pointer_injection": {"status": "ok", "recommended": "dotoolc", "mechanisms": ["dotoolc"], "notes": [], "portal_backends": ["gnome"]},
        "global_hotkeys": {"status": "ok", "recommended": "portal:GlobalShortcuts", "mechanisms": ["portal:GlobalShortcuts"], "notes": [], "portal_backends": ["gnome"]},
        "window_introspection": {"status": "ok", "recommended": "hyprctl", "mechanisms": ["hyprctl"], "notes": [], "portal_backends": []},
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

    res = runner.invoke(app, ["plan-project", str(project_dir), "--json", "--evidence-lane", "gnome-wayland"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)

    assert data["planner_evidence_lane"]["profile_id"] == "gnome-wayland"
    assert data["planner_evidence_lane_fit"]["status"] == "drifted"
    assert data["planner_evidence_lane_fit"]["selection_source"] == "explicit"

    table_res = runner.invoke(app, ["plan-project", str(project_dir), "--evidence-lane", "gnome-wayland"])
    assert table_res.exit_code == 0, table_res.output
    assert "Evidence lane" in table_res.output
    assert "Evidence fit" in table_res.output


def test_plan_project_wayland_portal_catalog_signals_stable_vs_dynamic_hotkeys(tmp_path: Path) -> None:
    dynamic_project = _make_project(tmp_path / "dynamic")

    dynamic_res = runner.invoke(app, ["plan-project", str(dynamic_project), "--json", "--no-session-check"])
    assert dynamic_res.exit_code == 0, dynamic_res.output
    dynamic_data = json.loads(dynamic_res.output)

    dynamic_surface = next(item for item in dynamic_data["surface_choices"] if item["id"] == "portal-global-shortcuts")
    assert "stable_shortcut_candidates=0" in dynamic_surface["evidence"]
    assert "dynamic_shortcut_candidates=1" in dynamic_surface["evidence"]

    stable_project = tmp_path / "stable" / "proj"
    (stable_project / "macros").mkdir(parents=True)
    (stable_project / "macros" / "simple.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "simple",
                "steps": [{"type": "TypeText", "text": "Hello world"}],
            },
            sort_keys=False,
        )
    )
    (stable_project / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "stable-proj",
                "settings": {"desktop_backend": "wayland"},
                "bindings": [{"keys": "Mod4+H", "macro": "simple"}],
            },
            sort_keys=False,
        )
    )

    stable_res = runner.invoke(app, ["plan-project", str(stable_project), "--json", "--no-session-check"])
    assert stable_res.exit_code == 0, stable_res.output
    stable_data = json.loads(stable_res.output)

    stable_surface = next(item for item in stable_data["surface_choices"] if item["id"] == "portal-global-shortcuts")
    assert stable_surface["fit"] in {"good", "strong"}
    assert "stable_shortcut_candidates=1" in stable_surface["evidence"]
    assert "dynamic_shortcut_candidates=0" in stable_surface["evidence"]
    stable_macro = next(item for item in stable_data["macro_route_profiles"] if item["macro"] == "simple")
    assert stable_macro["primary_activation_route_id"] == "portal-shortcuts-route"


def test_plan_project_wayland_helper_sensitive_hotkeys_do_not_default_to_portal_route(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "macros" / "clicker.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "clicker",
                "steps": [
                    {"type": "WaitForImage", "needle_path": "assets/button.png", "timeout_ms": 1500},
                    {"type": "ClickNeedle", "needle_path": "assets/ok.png"},
                ],
            },
            sort_keys=False,
        )
    )
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "portal-hotkey-shape",
                "settings": {"desktop_backend": "wayland"},
                "bindings": [{"keys": "Mod4+K", "macro": "clicker"}],
            },
            sort_keys=False,
        )
    )

    res = runner.invoke(app, ["plan-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)

    clicker = next(item for item in data["macro_route_profiles"] if item["macro"] == "clicker")
    assert clicker["route_id"] == "helper-boundary-runner"
    assert clicker["primary_activation_route_id"] == "native-trigger-route"
    portal_surface = next(item for item in data["surface_choices"] if item["id"] == "portal-global-shortcuts")
    assert "stable_shortcut_candidates=0" in portal_surface["evidence"]
    assert "dynamic_shortcut_candidates=1" in portal_surface["evidence"]
