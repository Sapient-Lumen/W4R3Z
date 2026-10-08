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

    vision = next(item for item in data["macro_profiles"] if item["macro"] == "vision")
    assert "vision-heavy" in vision["tags"]
    assert set(vision["triggers"]) == {"hotkey", "bus-watcher"}
    assert vision["smells"]["long_delay"] == 1
    assert vision["smells"]["coord_click"] == 1

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
    assert "vhk-palette-launcher" in surface_ids
    assert "wm-native-dispatch" in surface_ids
    assert "portal-global-shortcuts" in surface_ids
    assert "keyd-remap" in surface_ids
    assert "kanata-remap" in surface_ids
    assert "watcher-services" in surface_ids
    espanso = next(item for item in data["surface_choices"] if item["id"] == "espanso-text-package")
    assert espanso["fit"] in {"good", "strong"}
    assert any("gen-espanso" in cmd for cmd in espanso["commands"])

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

    portability_playbook_ids = {item["id"] for item in data["portability_playbooks"]}
    assert "hyprland-conservative" in portability_playbook_ids
    helper_playbook = next(item for item in data["portability_playbooks"] if item["id"] == "hyprland-conservative")
    assert helper_playbook["priority"] in {"high", "medium"}
    assert any("doctor --json" in cmd for cmd in helper_playbook["commands"])
    assert helper_playbook["artifacts"]

    toolchain_ids = {item["id"] for item in data["toolchain_choices"]}
    assert "text-injection" in toolchain_ids
    assert "pointer-injection" in toolchain_ids
    assert "screen-capture" in toolchain_ids
    assert "global-hotkeys" in toolchain_ids
    assert "window-introspection" in toolchain_ids
    text_toolchain = next(item for item in data["toolchain_choices"] if item["id"] == "text-injection")
    assert text_toolchain["recommended_toolchain"]
    assert text_toolchain["category"] == "input"
    assert text_toolchain["fallback_toolchains"]

    coverage_ids = {item["id"] for item in data["capability_coverage"]}
    assert "text-injection" in coverage_ids
    assert "pointer-injection" in coverage_ids
    assert "global-hotkeys" in coverage_ids
    text_coverage = next(item for item in data["capability_coverage"] if item["id"] == "text-injection")
    assert text_coverage["coverage_class"] in {"portable", "conditional", "broad"}
    assert text_coverage["usage_count"] >= 1
    assert text_coverage["best_environments"]
    pointer_coverage = next(item for item in data["capability_coverage"] if item["id"] == "pointer-injection")
    assert pointer_coverage["coverage_class"] in {"helper-boundary", "conditional", "x11-first"}
    assert pointer_coverage["blocking_environments"]
    assert pointer_coverage["offload_paths"]

    gate_ids = {item["id"] for item in data["verification_gates"]}
    assert "text-injection" in gate_ids
    assert "pointer-injection" in gate_ids
    assert "global-hotkeys" in gate_ids
    text_gate = next(item for item in data["verification_gates"] if item["id"] == "text-injection")
    assert text_gate["priority"] in {"high", "medium"}
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
    helper_pattern = next(item for item in data["reference_patterns"] if item["id"] == "portal-helper-boundary")
    assert helper_pattern["fit"] in {"good", "strong"}
    assert any("doctor --json" in cmd for cmd in helper_pattern["commands"])

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
    assert "autokey-session-honesty" in lesson_ids
    assert "xremap-app-context-bridge" in lesson_ids
    assert "keyd-thin-trigger-boundary" in lesson_ids
    assert "portal-stable-action-catalog" in lesson_ids
    assert "libei-helper-seam" in lesson_ids
    portal_lesson = next(item for item in data["ecosystem_lessons"] if item["id"] == "portal-stable-action-catalog")
    assert portal_lesson["source_tools"]
    assert portal_lesson["product_implication"]

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
