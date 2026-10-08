from __future__ import annotations

from typing import Any, Mapping


def build_session_target_policy(
    *,
    desktop_backend: str,
    service_mode: str,
    autostart_mode: str,
    authority_scope: str,
    has_bus_watchers: bool,
    unit_base: str,
) -> dict[str, Any]:
    backend = str(desktop_backend or "unknown").strip().lower() or "unknown"
    service_mode_value = str(service_mode or "environment-only").strip() or "environment-only"
    autostart_mode_value = str(autostart_mode or "none").strip() or "none"
    target_unit = "graphical-session.target"
    pre_target = "graphical-session-pre.target"
    default_target = "default.target"

    binds = service_mode_value != "environment-only"
    if binds:
        mode = "graphical-session-bound"
        summary = (
            "This service lane should follow graphical-session lifetime rather than pretend that a generic user login is the same thing. "
            "VHK keeps a default.target install fallback for portability, but the owned watcher/runtime lane is expected to start and stop with the graphical session when that target exists."
        )
    else:
        mode = "environment-export-only"
        summary = (
            "This handoff does not ship a first-party long-lived user unit, so target binding stays documentary: VHK exports environment and bridge guidance without claiming session-lifetime ownership."
        )

    guardrails = [
        "Keep graphical-session binding explicit for session-specific automation; services that need live display/session context should not be documented as generic always-on user daemons.",
        "Retain default.target as a fallback install lane because not every desktop/session publishes the same graphical-session target behavior.",
        "Do not use session-target prose to blur authority boundaries: portal sessions and privileged helper daemons are still separate ownership stories.",
    ]
    if backend == "wayland":
        guardrails.append(
            "For Wayland-first projects, prefer graphical-session lifetime for user-owned watcher services and keep compositor/helper boundaries explicit instead of stretching default.target into a universal answer."
        )
    elif backend == "x11":
        guardrails.append(
            "For X11-first projects, session lifetime still matters because DISPLAY/XAUTHORITY-style context is tied to the graphical session, not just to the user account."
        )

    verification_commands: list[str] = []
    if binds:
        verification_commands = [
            f"systemctl --user show {unit_base}.service -p PartOf -p BindsTo -p After",
            f"systemctl --user show {unit_base}.socket -p PartOf -p BindsTo",
            f"systemctl --user list-dependencies {target_unit}",
            f"systemctl --user is-active {target_unit}",
        ]

    return {
        "mode": mode,
        "target_unit": target_unit,
        "pre_target_unit": pre_target,
        "fallback_target_unit": default_target,
        "binds_to_graphical_session": binds,
        "wants_graphical_session": binds,
        "service_mode": service_mode_value,
        "autostart_mode": autostart_mode_value,
        "authority_scope": authority_scope,
        "has_bus_watchers": bool(has_bus_watchers),
        "summary": summary,
        "guardrails": guardrails,
        "verification_commands": verification_commands,
    }


def summarize_session_target_policy(policy: Mapping[str, Any] | None) -> dict[str, Any]:
    payload = dict(policy or {})
    verification_commands = [str(x) for x in list(payload.get("verification_commands") or []) if str(x)]
    return {
        "mode": str(payload.get("mode") or "unknown"),
        "binds_to_graphical_session": bool(payload.get("binds_to_graphical_session")),
        "verification_command_count": len(verification_commands),
        "target_unit": str(payload.get("target_unit") or "graphical-session.target"),
    }
