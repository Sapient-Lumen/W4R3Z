from __future__ import annotations

from typing import Any, Mapping


def build_startup_handoff_policy(
    *,
    desktop_backend: str,
    service_mode: str,
    autostart_mode: str,
    authority_scope: str,
    session_target_policy: dict[str, Any] | None = None,
    portal_route_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    backend = str(desktop_backend or "unknown").strip().lower() or "unknown"
    service_mode_value = str(service_mode or "environment-only").strip() or "environment-only"
    autostart_mode_value = str(autostart_mode or "none").strip() or "none"
    authority_scope_value = str(authority_scope or "user-session-owned").strip() or "user-session-owned"
    session_target = dict(session_target_policy or {})
    portal_route = dict(portal_route_contract or {})

    target_unit = str(session_target.get("target_unit") or "graphical-session.target")
    binds_to_graphical_session = bool(session_target.get("binds_to_graphical_session"))
    current_desktop = str(portal_route.get("xdg_current_desktop") or "").strip()

    if service_mode_value != "environment-only" and binds_to_graphical_session:
        mode = "graphical-target-primary-autostart-fallback"
        primary_owner = target_unit
        fallback_owner = "xdg-autostart"
        default_install_autostart_bridge = False
        default_enable_user_unit = True
        summary = (
            "Use the systemd user target as the primary startup owner for the VHK-owned service lane and keep the XDG autostart desktop entry as an explicit fallback instead of installing both by default. "
            "That keeps startup ownership reviewable and lowers the chance of duplicate starts or session-manager-specific ordering loops."
        )
    elif autostart_mode_value != "none":
        mode = "xdg-autostart-primary"
        primary_owner = "xdg-autostart"
        fallback_owner = None
        default_install_autostart_bridge = True
        default_enable_user_unit = False
        summary = (
            "Use the XDG autostart bridge as the primary startup owner because this handoff does not have a strong first-party graphical-session-bound unit lane to enable."
        )
    else:
        mode = "manual-or-external-owner"
        primary_owner = "manual"
        fallback_owner = None
        default_install_autostart_bridge = False
        default_enable_user_unit = service_mode_value != "environment-only"
        summary = (
            "Keep startup ownership manual or external because this handoff does not export a stable autostart bridge."
        )

    guardrails = [
        "Pick one primary startup owner at install time. Do not enable the graphical-session target path and the XDG autostart bridge by default for the same VHK-owned service lane.",
        "Treat XDG autostart as a desktop/session startup contract, not as proof that every session manager starts things the same way or at the same point in the graphical lifecycle.",
        "Keep startup ownership separate from authority ownership: starting a user unit at login does not grant portal consent, compositor privileges, or helper-daemon control.",
    ]
    if backend == "wayland":
        guardrails.append(
            "Wayland sessions vary more in how login, compositor, autostart, and user targets are connected, so keep the autostart bridge available as an explicit fallback rather than a hard-wired second owner."
        )
    if current_desktop:
        guardrails.append(
            f"Review startup behavior on the observed desktop (`{current_desktop}`) before enabling fallback owners together; desktop matching and session-manager behavior still decide when an autostart entry actually runs."
        )

    install_toggles = {
        "autostart_bridge_env": "VHK_INSTALL_AUTOSTART_BRIDGE",
        "enable_user_unit_env": "VHK_ENABLE_USER_UNIT",
        "default_install_autostart_bridge": default_install_autostart_bridge,
        "default_enable_user_unit": default_enable_user_unit,
    }
    verification_commands = [
        f"systemctl --user is-enabled {target_unit}",
        f"systemctl --user show {target_unit} -p Id -p ActiveState",
        "test -f \"${XDG_CONFIG_HOME:-$HOME/.config}/autostart/<unit>.desktop\" && printf '%s\\n' 'autostart bridge installed' || printf '%s\\n' 'autostart bridge absent'",
    ]
    if current_desktop:
        verification_commands.append("printf '%s\n' \"${XDG_CURRENT_DESKTOP:-unknown}\"")

    return {
        "mode": mode,
        "summary": summary,
        "primary_owner": primary_owner,
        "fallback_owner": fallback_owner,
        "authority_scope": authority_scope_value,
        "service_mode": service_mode_value,
        "autostart_mode": autostart_mode_value,
        "current_desktop": current_desktop or None,
        "install_toggles": install_toggles,
        "guardrails": guardrails,
        "verification_commands": verification_commands,
    }


def summarize_startup_handoff_policy(policy: Mapping[str, Any] | None) -> dict[str, Any]:
    payload = dict(policy or {})
    toggles = dict(payload.get("install_toggles") or {})
    return {
        "mode": str(payload.get("mode") or "unknown"),
        "primary_owner": str(payload.get("primary_owner") or "manual"),
        "fallback_owner": str(payload.get("fallback_owner") or "") or None,
        "default_install_autostart_bridge": bool(toggles.get("default_install_autostart_bridge")),
        "default_enable_user_unit": bool(toggles.get("default_enable_user_unit")),
    }
