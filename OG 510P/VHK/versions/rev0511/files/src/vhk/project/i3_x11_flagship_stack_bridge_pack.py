from __future__ import annotations

from pathlib import Path
from typing import Any

from vhk.project.i3_x11_flagship_startup_bridge import (
    build_i3_x11_flagship_startup_bridge_contract,
    summarize_i3_x11_flagship_startup_bridge_contract,
)
from vhk.project.service_compose_pack import (
    _render_autostart_desktop,
    _render_session_activation_sync_script,
    _render_session_readiness_probe_script,
    _render_session_target_probe_script,
    _render_startup_handoff_probe_script,
)


FLAGSHIP_STACK_BRIDGE_KIND = "vhk.i3_x11.flagship_stack_bridge_pack"


def build_i3_x11_flagship_stack_bridge_pack(
    *,
    project_dir: Path,
    unit_base: str,
    watcher_names: list[str] | None = None,
    bus_socket_path: str,
) -> dict[str, Any]:
    project_root = project_dir.expanduser().resolve()
    resolved_watchers = [str(x) for x in list(watcher_names or []) if str(x)]
    resolved_unit_base = str(unit_base or "vhk-busd").strip() or "vhk-busd"
    command_name = resolved_unit_base
    config_rel = f"vhk/{command_name}/session-service"
    startup_bridge_contract = build_i3_x11_flagship_startup_bridge_contract(
        unit_base=resolved_unit_base,
        project_root=str(project_root),
        has_bus_watchers=bool(resolved_watchers),
    )
    story = {
        "project_root": str(project_root),
        "project_name": project_root.name,
        "command_name": command_name,
        "unit_base": resolved_unit_base,
        "watchers": resolved_watchers,
        "bus_socket_path": str(bus_socket_path),
        "service_mode": "socket-activated-busd" if resolved_watchers else "environment-only",
        "autostart_mode": str(startup_bridge_contract.get("autostart_mode") or "systemctl-bridge"),
        "systemd_directories": {
            "configuration": config_rel,
            "state": config_rel,
            "cache": config_rel,
        },
        "session_activation_policy": dict(startup_bridge_contract.get("session_activation_policy") or {}),
        "session_target_policy": dict(startup_bridge_contract.get("session_target_policy") or {}),
        "session_readiness_policy": dict(startup_bridge_contract.get("session_readiness_policy") or {}),
        "startup_handoff_policy": dict(startup_bridge_contract.get("startup_handoff_policy") or {}),
    }
    return {
        "pack_kind": FLAGSHIP_STACK_BRIDGE_KIND,
        "startup_bridge_contract": startup_bridge_contract,
        "startup_bridge_summary": summarize_i3_x11_flagship_startup_bridge_contract(startup_bridge_contract),
        "service_compose_story": story,
    }


def render_i3_x11_flagship_stack_sync_session_activation_env(pack: dict[str, Any]) -> str:
    return _render_session_activation_sync_script(pack)


def render_i3_x11_flagship_stack_verify_session_readiness(pack: dict[str, Any]) -> str:
    return _render_session_readiness_probe_script(pack)


def render_i3_x11_flagship_stack_verify_session_targets(pack: dict[str, Any]) -> str:
    return _render_session_target_probe_script(pack)


def render_i3_x11_flagship_stack_verify_startup_handoff(pack: dict[str, Any]) -> str:
    return _render_startup_handoff_probe_script(pack)


def render_i3_x11_flagship_stack_autostart_desktop(pack: dict[str, Any]) -> str:
    return _render_autostart_desktop(pack)


def render_i3_x11_flagship_stack_start_user_session(pack: dict[str, Any]) -> str:
    story = dict(pack.get("service_compose_story") or {})
    unit_base = str(story.get("unit_base") or "vhk-busd-project")
    service_mode = str(story.get("service_mode") or "socket-activated-busd")
    unit_name = f"{unit_base}.socket" if service_mode == "socket-activated-busd" else f"{unit_base}.service"
    return "\n".join(
        [
            "#!/usr/bin/env sh",
            "set -eu",
            "",
            'CONFIGURATION_DIRECTORY="${CONFIGURATION_DIRECTORY:-$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)}"',
            f'UNIT_NAME="{unit_name}"',
            'LENIENT_MODE="${VHK_SESSION_BRIDGE_LENIENT:-0}"',
            'if [ -x "$CONFIGURATION_DIRECTORY/sync_session_activation_env.sh" ]; then',
            '  "$CONFIGURATION_DIRECTORY/sync_session_activation_env.sh" >/dev/null 2>&1 || true',
            'fi',
            'if [ -x "$CONFIGURATION_DIRECTORY/verify_session_readiness.sh" ]; then',
            '  if ! "$CONFIGURATION_DIRECTORY/verify_session_readiness.sh"; then',
            '    if [ "$LENIENT_MODE" = "1" ]; then',
            '      printf "%s\n" "Session not ready; skipping VHK session start bridge."',
            '      exit 0',
            '    fi',
            '    exit 1',
            '  fi',
            'fi',
            'if ! command -v systemctl >/dev/null 2>&1; then',
            '  printf "%s\n" "systemctl unavailable; cannot start VHK user session lane." >&2',
            '  exit 1',
            'fi',
            'systemctl --user start "$UNIT_NAME" >/dev/null 2>&1 || true',
            'printf "%s\n" "Started VHK user session lane: $UNIT_NAME"',
            "",
        ]
    )
