from __future__ import annotations

from typing import Any


def _dedupe(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def build_session_activation_policy(
    *,
    desktop_backend: str,
    service_mode: str,
    authority_scope: str,
    has_bus_watchers: bool,
    portal_route_contract: dict[str, Any] | None = None,
    authority_policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    desktop_backend = str(desktop_backend or "unknown").strip().lower() or "unknown"
    service_mode = str(service_mode or "environment-only").strip() or "environment-only"
    authority_scope = str(authority_scope or "user-session-owned").strip() or "user-session-owned"
    portal_route_contract = dict(portal_route_contract or {})
    authority_policy = dict(authority_policy or {})

    live_route = str(portal_route_contract.get("live_route") or "").strip().lower()
    declared_route = str(portal_route_contract.get("declared_route") or "").strip().lower()
    route_text = " ".join(part for part in [live_route, declared_route] if part)
    has_wayland = desktop_backend == "wayland" or "wayland" in route_text
    has_x11 = desktop_backend == "x11" or "x11" in route_text or not has_wayland

    base_vars = [
        "DBUS_SESSION_BUS_ADDRESS",
        "XDG_RUNTIME_DIR",
        "XDG_CURRENT_DESKTOP",
        "XDG_SESSION_TYPE",
    ]
    display_vars: list[str] = []
    if has_wayland:
        display_vars.extend(["WAYLAND_DISPLAY", "DISPLAY"])
    if has_x11:
        display_vars.extend(["DISPLAY", "XAUTHORITY"])

    portal_surface_ids = [str(x) for x in list(authority_policy.get("desktop_mediated_surface_ids") or []) if str(x)]
    adjacent_surface_ids = [str(x) for x in list(authority_policy.get("adjacent_privileged_surface_ids") or []) if str(x)]
    bridge_vars = _dedupe(base_vars + display_vars)

    sync_mode = "dbus-and-systemd-activation-sync"
    if service_mode == "environment-only" and not portal_surface_ids:
        sync_mode = "systemd-activation-sync"

    summary_parts = [
        "Keep the user-manager and D-Bus activation environments aligned with the live graphical session before starting VHK-owned services.",
    ]
    if has_wayland:
        summary_parts.append("Treat Wayland display state as first-class so user services and portal-facing helpers inherit the same session identifiers the desktop exported.")
    if has_x11:
        summary_parts.append("Carry X11 display/auth hints forward explicitly instead of assuming they survive the login path automatically.")
    if portal_surface_ids:
        summary_parts.append("Desktop-mediated surfaces stay session-scoped, so activation sync should happen before portal-routed helpers or shortcuts are expected to wake correctly.")
    if adjacent_surface_ids:
        summary_parts.append("Adjacent privileged helpers still need their own review; syncing activation variables does not collapse evdev/uinput ownership into the VHK user service.")
    if has_bus_watchers:
        summary_parts.append("Because this project has long-lived watcher traffic, the autostart bridge should sync activation variables before it asks systemd --user to start the socket/service lane.")

    preferred_command = "dbus-update-activation-environment --systemd " + " ".join(bridge_vars)
    fallback_command = "systemctl --user import-environment " + " ".join(bridge_vars)

    return {
        "mode": sync_mode,
        "summary": " ".join(summary_parts),
        "bridge_variables": bridge_vars,
        "display_variables": _dedupe(display_vars),
        "portal_surface_ids": portal_surface_ids,
        "adjacent_privileged_surface_ids": adjacent_surface_ids,
        "authority_scope": authority_scope,
        "preferred_command": preferred_command,
        "fallback_command": fallback_command,
        "autostart_sync_required": bool(has_bus_watchers or portal_surface_ids),
        "guardrails": [
            "Keep the activation variable list explicit instead of using --all, so service startup stays reviewable and avoids dragging unrelated shell/session state into user services.",
            "Sync activation variables before starting VHK-owned user units from autostart or session hooks; environment.d covers static exports, but live display/session variables may still need import/update at login time.",
            "Treat the sync step as user-session glue only; it does not grant portal permissions or privileged helper access on its own.",
        ],
    }
