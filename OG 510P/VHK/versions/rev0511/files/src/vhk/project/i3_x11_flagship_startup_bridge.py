from __future__ import annotations

from typing import Any, Mapping

from vhk.project.session_activation_policy import build_session_activation_policy
from vhk.project.session_target_policy import build_session_target_policy, summarize_session_target_policy
from vhk.project.session_readiness_policy import build_session_readiness_policy, summarize_session_readiness_policy
from vhk.project.startup_handoff_policy import build_startup_handoff_policy, summarize_startup_handoff_policy


FLAGSHIP_RUNTIME_KIND = "vhk.i3_x11.flagship_startup_bridge"


def build_i3_x11_flagship_startup_bridge_contract(
    *,
    unit_base: str,
    project_root: str,
    bus_event: str = "hotkey",
    service_mode: str = "socket-activated-busd",
    autostart_mode: str = "systemctl-bridge",
    authority_scope: str = "user-session-owned",
    has_bus_watchers: bool = True,
) -> dict[str, Any]:
    resolved_unit_base = str(unit_base or "vhk-busd").strip() or "vhk-busd"
    resolved_project_root = str(project_root or ".").strip() or "."
    resolved_bus_event = str(bus_event or "hotkey").strip() or "hotkey"
    resolved_service_mode = str(service_mode or "socket-activated-busd").strip() or "socket-activated-busd"
    resolved_autostart_mode = str(autostart_mode or "systemctl-bridge").strip() or "systemctl-bridge"
    resolved_authority_scope = str(authority_scope or "user-session-owned").strip() or "user-session-owned"

    session_activation_policy = build_session_activation_policy(
        desktop_backend="x11",
        service_mode=resolved_service_mode,
        authority_scope=resolved_authority_scope,
        has_bus_watchers=has_bus_watchers,
        portal_route_contract={"live_route": "x11", "declared_route": "x11-first", "xdg_current_desktop": "i3"},
        authority_policy={},
    )
    session_target_policy = build_session_target_policy(
        desktop_backend="x11",
        service_mode=resolved_service_mode,
        autostart_mode=resolved_autostart_mode,
        authority_scope=resolved_authority_scope,
        has_bus_watchers=has_bus_watchers,
        unit_base=resolved_unit_base,
    )
    session_readiness_policy = build_session_readiness_policy(
        desktop_backend="x11",
        service_mode=resolved_service_mode,
        authority_scope=resolved_authority_scope,
        session_target_policy=session_target_policy,
        session_activation_policy=session_activation_policy,
        authority_policy={},
    )
    startup_handoff_policy = build_startup_handoff_policy(
        desktop_backend="x11",
        service_mode=resolved_service_mode,
        autostart_mode=resolved_autostart_mode,
        authority_scope=resolved_authority_scope,
        session_target_policy=session_target_policy,
        portal_route_contract={"live_route": "x11", "declared_route": "x11-first", "xdg_current_desktop": "i3"},
    )

    helper_paths = {
        "sync_session_activation_env": "bin/sync_session_activation_env.sh",
        "verify_session_readiness": "bin/verify_session_readiness.sh",
        "start_user_session": "bin/start_user_session.sh",
        "install_user_session": "install_user_session.sh",
        "uninstall_user_session": "uninstall_user_session.sh",
        "smoke_install": "smoke_install.sh",
        "verify_user_session_json": "verify_user_session_json.sh",
        "verify_user_session": "verify_user_session.sh",
        "repair_user_session": "repair_user_session.sh",
        "autostart_desktop": f"autostart/{resolved_unit_base}.desktop",
        "socket_unit": f"systemd-user/{resolved_unit_base}.socket",
        "service_unit": f"systemd-user/{resolved_unit_base}.service",
        "i3_snippet": "i3/vhk-busd.conf",
        "control_manifest": "control-plane.json",
    }

    install_contract = {
        "primary_startup_owner": str(startup_handoff_policy.get("primary_owner") or "graphical-session.target"),
        "fallback_startup_owner": str(startup_handoff_policy.get("fallback_owner") or "") or None,
        "default_enable_user_unit": bool(((startup_handoff_policy.get("install_toggles") or {}).get("default_enable_user_unit"))),
        "default_install_autostart_bridge": bool(((startup_handoff_policy.get("install_toggles") or {}).get("default_install_autostart_bridge"))),
        "recommended_steps": [
            f"run {helper_paths['smoke_install']} before touching the live desktop",
            f"run {helper_paths['install_user_session']} to copy units, wrappers, the control manifest, and the i3 include into XDG config",
            f"run {helper_paths['verify_user_session_json']} to confirm the installed lane still has the required files and live-session probes",
            f"use {helper_paths['repair_user_session']} when the installed lane drifted and needs a bounded reinstall + session-start bridge",
            f"systemctl --user enable --now {resolved_unit_base}.socket",
            f"include the installed copy of {helper_paths['i3_snippet']} from your i3 config and reload i3",
            f"install {helper_paths['autostart_desktop']} only when the session needs an explicit desktop-login fallback bridge",
        ],
        "guardrails": [
            "Prefer one startup owner. The graphical-session-bound user unit is primary; the autostart bridge is a fallback, not a co-equal default owner.",
            "Keep the warm lane thin: hotkeys emit into the resident bus lane; recorder, cleanup, replay, and direct-run stay explicit wrappers.",
            "Do not widen this contract to generic Linux-native or portal-first stories unless the X11/i3 warm lane gets measurably better.",
        ],
    }

    llm_contract = {
        "preferred_triage_entrypoints": [
            "bin/stack_state_json.sh",
            "bin/next_action_json.sh",
            "bin/warm_runtime_ticket_json.sh",
            "bin/check_runtime_json.sh",
        ],
        "preferred_edit_entrypoint": "bin/macro_source_json.sh <macro>",
        "preferred_dispatch_entrypoint": "bin/dispatch_macro_checked.sh <macro>",
        "runtime_repair_entrypoints": [
            helper_paths["verify_user_session_json"],
            helper_paths["repair_user_session"],
            helper_paths["verify_session_readiness"],
            helper_paths["sync_session_activation_env"],
            "bin/reload_runtime_json.sh",
            "bin/restart_runtime_json.sh",
        ],
    }

    return {
        "runtime_kind": FLAGSHIP_RUNTIME_KIND,
        "project_root": resolved_project_root,
        "bus_event": resolved_bus_event,
        "desktop_backend": "x11",
        "window_manager": "i3",
        "service_mode": resolved_service_mode,
        "autostart_mode": resolved_autostart_mode,
        "authority_scope": resolved_authority_scope,
        "has_bus_watchers": bool(has_bus_watchers),
        "unit_base": resolved_unit_base,
        "helper_paths": helper_paths,
        "session_activation_policy": session_activation_policy,
        "session_target_policy": session_target_policy,
        "session_readiness_policy": session_readiness_policy,
        "startup_handoff_policy": startup_handoff_policy,
        "install_contract": install_contract,
        "llm_contract": llm_contract,
    }


def summarize_i3_x11_flagship_startup_bridge_contract(contract: Mapping[str, Any] | None) -> dict[str, Any]:
    payload = dict(contract or {})
    install_contract = dict(payload.get("install_contract") or {})
    helper_paths = dict(payload.get("helper_paths") or {})
    activation_policy = dict(payload.get("session_activation_policy") or {})
    return {
        "runtime_kind": str(payload.get("runtime_kind") or FLAGSHIP_RUNTIME_KIND),
        "window_manager": str(payload.get("window_manager") or "i3"),
        "desktop_backend": str(payload.get("desktop_backend") or "x11"),
        "primary_startup_owner": str(install_contract.get("primary_startup_owner") or "graphical-session.target"),
        "fallback_startup_owner": str(install_contract.get("fallback_startup_owner") or "") or None,
        "helper_count": len([str(x) for x in helper_paths.values() if str(x)]),
        "session_activation_policy": {
            "mode": str(activation_policy.get("mode") or "unknown"),
            "required": bool(activation_policy),
            "bridge_variable_count": len([str(x) for x in list(activation_policy.get("bridge_variables") or []) if str(x)]),
        },
        "session_target_policy": summarize_session_target_policy(payload.get("session_target_policy")),
        "session_readiness_policy": summarize_session_readiness_policy(payload.get("session_readiness_policy")),
        "startup_handoff_policy": summarize_startup_handoff_policy(payload.get("startup_handoff_policy")),
    }
