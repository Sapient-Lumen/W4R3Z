from __future__ import annotations

from pathlib import Path
from typing import Any


FLAGSHIP_STACK_INSTALL_KIND = "vhk.i3_x11.flagship_stack_install_pack"


def build_i3_x11_flagship_stack_install_pack(
    *,
    project_dir: Path,
    stack_bridge_pack: dict[str, Any],
) -> dict[str, Any]:
    project_root = project_dir.expanduser().resolve()
    startup_bridge_contract = dict((stack_bridge_pack or {}).get("startup_bridge_contract") or {})
    service_story = dict((stack_bridge_pack or {}).get("service_compose_story") or {})
    unit_base = str(service_story.get("unit_base") or startup_bridge_contract.get("unit_base") or "vhk-busd-project").strip() or "vhk-busd-project"
    command_name = str(service_story.get("command_name") or unit_base).strip() or unit_base
    startup_handoff_policy = dict(startup_bridge_contract.get("startup_handoff_policy") or {})
    install_toggles = dict(startup_handoff_policy.get("install_toggles") or {})
    payload_rel = str((service_story.get("systemd_directories") or {}).get("configuration") or f"vhk/{command_name}/session-service")
    i3_include_rel = f"i3/vhk/{unit_base}.conf"
    install_story = {
        "project_root": str(project_root),
        "project_name": project_root.name,
        "unit_base": unit_base,
        "command_name": command_name,
        "service_mode": str(service_story.get("service_mode") or startup_bridge_contract.get("service_mode") or "socket-activated-busd"),
        "autostart_mode": str(service_story.get("autostart_mode") or startup_bridge_contract.get("autostart_mode") or "systemctl-bridge"),
        "payload_rel": payload_rel,
        "i3_include_rel": i3_include_rel,
        "default_enable_user_unit": bool(install_toggles.get("default_enable_user_unit", True)),
        "default_install_autostart_bridge": bool(install_toggles.get("default_install_autostart_bridge", False)),
        "default_install_i3_include": True,
        "env_toggles": {
            "enable_user_unit_env": str(install_toggles.get("enable_user_unit_env") or "VHK_ENABLE_USER_UNIT"),
            "autostart_bridge_env": str(install_toggles.get("autostart_bridge_env") or "VHK_INSTALL_AUTOSTART_BRIDGE"),
            "install_i3_include_env": "VHK_INSTALL_I3_INCLUDE",
        },
    }
    install_summary = {
        "unit_base": unit_base,
        "payload_rel": payload_rel,
        "i3_include_rel": i3_include_rel,
        "default_enable_user_unit": install_story["default_enable_user_unit"],
        "default_install_autostart_bridge": install_story["default_install_autostart_bridge"],
        "default_install_i3_include": True,
        "post_install_helpers": {
            "verify_user_session_json": "verify_user_session_json.sh",
            "verify_user_session": "verify_user_session.sh",
            "repair_user_session": "repair_user_session.sh",
        },
    }
    return {
        "pack_kind": FLAGSHIP_STACK_INSTALL_KIND,
        "startup_bridge_contract": startup_bridge_contract,
        "service_compose_story": service_story,
        "install_story": install_story,
        "install_summary": install_summary,
    }


def render_i3_x11_flagship_stack_install_user_session(pack: dict[str, Any]) -> str:
    install_story = dict(pack.get("install_story") or {})
    env_toggles = dict(install_story.get("env_toggles") or {})
    unit_base = str(install_story.get("unit_base") or "vhk-busd-project")
    command_name = str(install_story.get("command_name") or unit_base)
    service_mode = str(install_story.get("service_mode") or "socket-activated-busd")
    autostart_mode = str(install_story.get("autostart_mode") or "systemctl-bridge")
    payload_rel = str(install_story.get("payload_rel") or f"vhk/{command_name}/session-service")
    i3_include_rel = str(install_story.get("i3_include_rel") or f"i3/vhk/{unit_base}.conf")
    unit_name = f"{unit_base}.socket" if service_mode == "socket-activated-busd" else f"{unit_base}.service"
    default_enable_user_unit = "1" if bool(install_story.get("default_enable_user_unit", True)) else "0"
    default_install_autostart = "1" if bool(install_story.get("default_install_autostart_bridge", False)) else "0"
    default_install_i3_include = "1" if bool(install_story.get("default_install_i3_include", True)) else "0"
    lines = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        'SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"',
        'XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"',
        'SYSTEMD_USER_DIR="$XDG_CONFIG_HOME/systemd/user"',
        'AUTOSTART_DIR="$XDG_CONFIG_HOME/autostart"',
        f'PAYLOAD_DIR="$XDG_CONFIG_HOME/{payload_rel}"',
        f'I3_INCLUDE_PATH="$XDG_CONFIG_HOME/{i3_include_rel}"',
        f'ENABLE_USER_UNIT="${{{env_toggles.get("enable_user_unit_env") or "VHK_ENABLE_USER_UNIT"}:-{default_enable_user_unit}}}"',
        f'INSTALL_AUTOSTART_BRIDGE="${{{env_toggles.get("autostart_bridge_env") or "VHK_INSTALL_AUTOSTART_BRIDGE"}:-{default_install_autostart}}}"',
        f'INSTALL_I3_INCLUDE="${{{env_toggles.get("install_i3_include_env") or "VHK_INSTALL_I3_INCLUDE"}:-{default_install_i3_include}}}"',
        'mkdir -p "$SYSTEMD_USER_DIR" "$AUTOSTART_DIR" "$PAYLOAD_DIR" "$(dirname -- "$I3_INCLUDE_PATH")"',
        'cp "$SCRIPT_DIR/control-plane.json" "$PAYLOAD_DIR/control-plane.json"',
        'cp "$SCRIPT_DIR/README.md" "$PAYLOAD_DIR/stack-README.md"',
        'cp "$SCRIPT_DIR/bin/"*.sh "$PAYLOAD_DIR/"',
        'chmod 755 "$PAYLOAD_DIR/"*.sh',
    ]
    if service_mode == "socket-activated-busd":
        lines.extend([
            f'cp "$SCRIPT_DIR/systemd-user/{unit_base}.service" "$SYSTEMD_USER_DIR/{unit_base}.service"',
            f'cp "$SCRIPT_DIR/systemd-user/{unit_base}.socket" "$SYSTEMD_USER_DIR/{unit_base}.socket"',
        ])
    elif service_mode != "environment-only":
        lines.append(f'cp "$SCRIPT_DIR/systemd-user/{unit_base}.service" "$SYSTEMD_USER_DIR/{unit_base}.service"')
    lines.extend([
        'if [ "$INSTALL_I3_INCLUDE" = "1" ]; then',
        '  cp "$SCRIPT_DIR/i3/vhk-busd.conf" "$I3_INCLUDE_PATH"',
        'else',
        '  rm -f "$I3_INCLUDE_PATH"',
        'fi',
    ])
    if autostart_mode != "none":
        lines.extend([
            'if [ "$INSTALL_AUTOSTART_BRIDGE" = "1" ]; then',
            f'  cp "$SCRIPT_DIR/autostart/{unit_base}.desktop" "$AUTOSTART_DIR/{unit_base}.desktop"',
            'else',
            f'  rm -f "$AUTOSTART_DIR/{unit_base}.desktop"',
            'fi',
        ])
    lines.append('if [ "${VHK_SKIP_SYSTEMCTL:-0}" != "1" ] && command -v systemctl >/dev/null 2>&1; then')
    lines.append('  systemctl --user daemon-reload || true')
    if service_mode != "environment-only":
        lines.extend([
            '  if [ "$ENABLE_USER_UNIT" = "1" ]; then',
            f'    systemctl --user enable --now {unit_name} || true',
            '  fi',
        ])
    lines.extend([
        'fi',
        'printf "%s\n" "Installed flagship VHK i3/X11 warm-runtime stack."',
        'printf "%s\n" "Payload dir: $PAYLOAD_DIR"',
        'printf "%s\n" "i3 include: $I3_INCLUDE_PATH"',
        'printf "%s\n" "User unit enabled: $ENABLE_USER_UNIT"',
        'printf "%s\n" "Autostart bridge installed: $INSTALL_AUTOSTART_BRIDGE"',
        'printf "%s\n" "i3 include installed: $INSTALL_I3_INCLUDE"',
        '',
    ])
    return "\n".join(lines)


def render_i3_x11_flagship_stack_uninstall_user_session(pack: dict[str, Any]) -> str:
    install_story = dict(pack.get("install_story") or {})
    unit_base = str(install_story.get("unit_base") or "vhk-busd-project")
    command_name = str(install_story.get("command_name") or unit_base)
    service_mode = str(install_story.get("service_mode") or "socket-activated-busd")
    autostart_mode = str(install_story.get("autostart_mode") or "systemctl-bridge")
    payload_rel = str(install_story.get("payload_rel") or f"vhk/{command_name}/session-service")
    i3_include_rel = str(install_story.get("i3_include_rel") or f"i3/vhk/{unit_base}.conf")
    lines = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        'XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"',
        'SYSTEMD_USER_DIR="$XDG_CONFIG_HOME/systemd/user"',
        'AUTOSTART_DIR="$XDG_CONFIG_HOME/autostart"',
        f'PAYLOAD_DIR="$XDG_CONFIG_HOME/{payload_rel}"',
        f'I3_INCLUDE_PATH="$XDG_CONFIG_HOME/{i3_include_rel}"',
        'if [ "${VHK_SKIP_SYSTEMCTL:-0}" != "1" ] && command -v systemctl >/dev/null 2>&1; then',
    ]
    if service_mode == "socket-activated-busd":
        lines.extend([
            f'  systemctl --user disable --now {unit_base}.socket || true',
            f'  systemctl --user stop {unit_base}.service || true',
        ])
    elif service_mode != "environment-only":
        lines.append(f'  systemctl --user disable --now {unit_base}.service || true')
    lines.extend([
        'fi',
        f'rm -f "$SYSTEMD_USER_DIR/{unit_base}.service"',
    ])
    if service_mode == "socket-activated-busd":
        lines.append(f'rm -f "$SYSTEMD_USER_DIR/{unit_base}.socket"')
    if autostart_mode != "none":
        lines.append(f'rm -f "$AUTOSTART_DIR/{unit_base}.desktop"')
    lines.extend([
        'rm -f "$I3_INCLUDE_PATH"',
        'rm -rf "$PAYLOAD_DIR"',
        'if [ "${VHK_SKIP_SYSTEMCTL:-0}" != "1" ] && command -v systemctl >/dev/null 2>&1; then',
        '  systemctl --user daemon-reload || true',
        'fi',
        'printf "%s\n" "Removed flagship VHK i3/X11 warm-runtime stack."',
        '',
    ])
    return "\n".join(lines)


def render_i3_x11_flagship_stack_smoke_install(pack: dict[str, Any]) -> str:
    install_story = dict(pack.get("install_story") or {})
    env_toggles = dict(install_story.get("env_toggles") or {})
    unit_base = str(install_story.get("unit_base") or "vhk-busd-project")
    command_name = str(install_story.get("command_name") or unit_base)
    service_mode = str(install_story.get("service_mode") or "socket-activated-busd")
    autostart_mode = str(install_story.get("autostart_mode") or "systemctl-bridge")
    payload_rel = str(install_story.get("payload_rel") or f"vhk/{command_name}/session-service")
    i3_include_rel = str(install_story.get("i3_include_rel") or f"i3/vhk/{unit_base}.conf")
    autostart_env = str(env_toggles.get("autostart_bridge_env") or "VHK_INSTALL_AUTOSTART_BRIDGE")
    lines = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        'SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"',
        'SMOKE_ROOT="$SCRIPT_DIR/.smoke-root"',
        'rm -rf "$SMOKE_ROOT"',
        'mkdir -p "$SMOKE_ROOT/home" "$SMOKE_ROOT/config" "$SMOKE_ROOT/data"',
        'HOME="$SMOKE_ROOT/home" XDG_CONFIG_HOME="$SMOKE_ROOT/config" XDG_DATA_HOME="$SMOKE_ROOT/data" VHK_SKIP_SYSTEMCTL=1 sh "$SCRIPT_DIR/install_user_session.sh"',
        f'test -f "$SMOKE_ROOT/config/{payload_rel}/control-plane.json"',
        f'test -x "$SMOKE_ROOT/config/{payload_rel}/start_user_session.sh"',
        f'test -x "$SMOKE_ROOT/config/{payload_rel}/dispatch_macro_checked.sh"',
        f'test -f "$SMOKE_ROOT/config/{i3_include_rel}"',
        f'grep -q "vhk-emit" "$SMOKE_ROOT/config/{i3_include_rel}"',
        f'test -f "$SMOKE_ROOT/config/systemd/user/{unit_base}.service"',
    ]
    if service_mode == "socket-activated-busd":
        lines.extend([
            f'test -f "$SMOKE_ROOT/config/systemd/user/{unit_base}.socket"',
            f'grep -q "ListenDatagram=" "$SMOKE_ROOT/config/systemd/user/{unit_base}.socket"',
        ])
    lines.extend([
        f'grep -q "start_user_session.sh" "$SMOKE_ROOT/config/{payload_rel}/stack-README.md"',
        'HOME="$SMOKE_ROOT/home" XDG_CONFIG_HOME="$SMOKE_ROOT/config" XDG_DATA_HOME="$SMOKE_ROOT/data" VHK_SKIP_SYSTEMCTL=1 sh "$SCRIPT_DIR/verify_user_session_json.sh" > "$SMOKE_ROOT/verify-before-repair.json"',
        'grep -q \'"install_complete": true\' "$SMOKE_ROOT/verify-before-repair.json"',
        'HOME="$SMOKE_ROOT/home" XDG_CONFIG_HOME="$SMOKE_ROOT/config" XDG_DATA_HOME="$SMOKE_ROOT/data" VHK_SKIP_SYSTEMCTL=1 sh "$SCRIPT_DIR/repair_user_session.sh"',
        'HOME="$SMOKE_ROOT/home" XDG_CONFIG_HOME="$SMOKE_ROOT/config" XDG_DATA_HOME="$SMOKE_ROOT/data" VHK_SKIP_SYSTEMCTL=1 sh "$SCRIPT_DIR/verify_user_session_json.sh" > "$SMOKE_ROOT/verify-after-repair.json"',
        'grep -q \'"install_complete": true\' "$SMOKE_ROOT/verify-after-repair.json"',
    ])
    if autostart_mode != "none":
        lines.extend([
            f'test ! -e "$SMOKE_ROOT/config/autostart/{unit_base}.desktop"',
            f'HOME="$SMOKE_ROOT/home" XDG_CONFIG_HOME="$SMOKE_ROOT/config" XDG_DATA_HOME="$SMOKE_ROOT/data" VHK_SKIP_SYSTEMCTL=1 {autostart_env}=1 sh "$SCRIPT_DIR/install_user_session.sh"',
            f'test -f "$SMOKE_ROOT/config/autostart/{unit_base}.desktop"',
            f'grep -q "sync_session_activation_env.sh" "$SMOKE_ROOT/config/autostart/{unit_base}.desktop"',
            f'grep -q "verify_session_readiness.sh" "$SMOKE_ROOT/config/autostart/{unit_base}.desktop"',
        ])
    lines.extend([
        'HOME="$SMOKE_ROOT/home" XDG_CONFIG_HOME="$SMOKE_ROOT/config" XDG_DATA_HOME="$SMOKE_ROOT/data" VHK_SKIP_SYSTEMCTL=1 sh "$SCRIPT_DIR/uninstall_user_session.sh"',
        f'test ! -e "$SMOKE_ROOT/config/{payload_rel}"',
        f'test ! -e "$SMOKE_ROOT/config/{i3_include_rel}"',
        f'test ! -e "$SMOKE_ROOT/config/systemd/user/{unit_base}.service"',
        'printf "%s\n" "Flagship stack install smoke test completed."',
        '',
    ])
    return "\n".join(lines)


def render_i3_x11_flagship_stack_verify_user_session_json(pack: dict[str, Any]) -> str:
    install_story = dict(pack.get("install_story") or {})
    unit_base = str(install_story.get("unit_base") or "vhk-busd-project")
    command_name = str(install_story.get("command_name") or unit_base)
    service_mode = str(install_story.get("service_mode") or "socket-activated-busd")
    autostart_mode = str(install_story.get("autostart_mode") or "systemctl-bridge")
    payload_rel = str(install_story.get("payload_rel") or f"vhk/{command_name}/session-service")
    i3_include_rel = str(install_story.get("i3_include_rel") or f"i3/vhk/{unit_base}.conf")
    unit_name = f"{unit_base}.socket" if service_mode == "socket-activated-busd" else f"{unit_base}.service"
    lines = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        'XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"',
        'SYSTEMD_USER_DIR="$XDG_CONFIG_HOME/systemd/user"',
        'AUTOSTART_DIR="$XDG_CONFIG_HOME/autostart"',
        f'PAYLOAD_DIR="$XDG_CONFIG_HOME/{payload_rel}"',
        f'I3_INCLUDE_PATH="$XDG_CONFIG_HOME/{i3_include_rel}"',
        f'SERVICE_PATH="$SYSTEMD_USER_DIR/{unit_base}.service"',
        f'SOCKET_PATH="$SYSTEMD_USER_DIR/{unit_base}.socket"',
        f'AUTOSTART_PATH="$AUTOSTART_DIR/{unit_base}.desktop"',
        f'UNIT_NAME="{unit_name}"',
        'INSTALL_COMPLETE=1',
        'PAYLOAD_PRESENT=0',
        'SERVICE_PRESENT=0',
        'SOCKET_PRESENT=0',
        'I3_INCLUDE_PRESENT=0',
        'AUTOSTART_PRESENT=0',
        'SYNC_HELPER_PRESENT=0',
        'START_HELPER_PRESENT=0',
        'READINESS_HELPER_PRESENT=0',
        'TARGETS_HELPER_PRESENT=0',
        'HANDOFF_HELPER_PRESENT=0',
        'SESSION_READINESS_OK="unknown"',
        'SESSION_TARGETS_OK="unknown"',
        'STARTUP_HANDOFF_OK="unknown"',
        'SYSTEMCTL_AVAILABLE=0',
        'UNIT_ENABLED_STATE="unknown"',
        'UNIT_ACTIVE_STATE="unknown"',
        'WARNINGS=""',
        'if [ -d "$PAYLOAD_DIR" ]; then PAYLOAD_PRESENT=1; else INSTALL_COMPLETE=0; WARNINGS="$WARNINGS missing_payload"; fi',
        'if [ -f "$SERVICE_PATH" ]; then SERVICE_PRESENT=1; else INSTALL_COMPLETE=0; WARNINGS="$WARNINGS missing_service_unit"; fi',
    ]
    if service_mode == "socket-activated-busd":
        lines.append('if [ -f "$SOCKET_PATH" ]; then SOCKET_PRESENT=1; else INSTALL_COMPLETE=0; WARNINGS="$WARNINGS missing_socket_unit"; fi')
    else:
        lines.append('SOCKET_PRESENT="not_applicable"')
    lines.append('if [ -f "$I3_INCLUDE_PATH" ]; then I3_INCLUDE_PRESENT=1; else INSTALL_COMPLETE=0; WARNINGS="$WARNINGS missing_i3_include"; fi')
    if autostart_mode != "none":
        lines.append('if [ -f "$AUTOSTART_PATH" ]; then AUTOSTART_PRESENT=1; fi')
    else:
        lines.append('AUTOSTART_PRESENT="not_applicable"')
    lines.extend([
        'if [ -x "$PAYLOAD_DIR/sync_session_activation_env.sh" ]; then SYNC_HELPER_PRESENT=1; else INSTALL_COMPLETE=0; WARNINGS="$WARNINGS missing_sync_helper"; fi',
        'if [ -x "$PAYLOAD_DIR/start_user_session.sh" ]; then START_HELPER_PRESENT=1; else INSTALL_COMPLETE=0; WARNINGS="$WARNINGS missing_start_helper"; fi',
        'if [ -x "$PAYLOAD_DIR/verify_session_readiness.sh" ]; then READINESS_HELPER_PRESENT=1; if "$PAYLOAD_DIR/verify_session_readiness.sh" >/dev/null 2>&1; then SESSION_READINESS_OK=true; else SESSION_READINESS_OK=false; WARNINGS="$WARNINGS session_not_ready"; fi; else INSTALL_COMPLETE=0; SESSION_READINESS_OK="missing"; WARNINGS="$WARNINGS missing_readiness_helper"; fi',
        'if [ -x "$PAYLOAD_DIR/verify_session_targets.sh" ]; then TARGETS_HELPER_PRESENT=1; if "$PAYLOAD_DIR/verify_session_targets.sh" >/dev/null 2>&1; then SESSION_TARGETS_OK=true; else SESSION_TARGETS_OK=false; WARNINGS="$WARNINGS session_targets_unhealthy"; fi; else INSTALL_COMPLETE=0; SESSION_TARGETS_OK="missing"; WARNINGS="$WARNINGS missing_target_helper"; fi',
        'if [ -x "$PAYLOAD_DIR/verify_startup_handoff.sh" ]; then HANDOFF_HELPER_PRESENT=1; if "$PAYLOAD_DIR/verify_startup_handoff.sh" >/dev/null 2>&1; then STARTUP_HANDOFF_OK=true; else STARTUP_HANDOFF_OK=false; WARNINGS="$WARNINGS startup_owner_drift"; fi; else INSTALL_COMPLETE=0; STARTUP_HANDOFF_OK="missing"; WARNINGS="$WARNINGS missing_handoff_helper"; fi',
        'if [ "${VHK_SKIP_SYSTEMCTL:-0}" != "1" ] && command -v systemctl >/dev/null 2>&1; then',
        '  SYSTEMCTL_AVAILABLE=1',
        '  UNIT_ENABLED_STATE="$(systemctl --user is-enabled "$UNIT_NAME" 2>/dev/null || printf "%s" "unknown")"',
        '  UNIT_ACTIVE_STATE="$(systemctl --user is-active "$UNIT_NAME" 2>/dev/null || printf "%s" "inactive")"',
        'fi',
        'export WARNINGS INSTALL_COMPLETE SESSION_READINESS_OK SESSION_TARGETS_OK STARTUP_HANDOFF_OK UNIT_ACTIVE_STATE UNIT_NAME PAYLOAD_DIR SERVICE_PATH SOCKET_PATH I3_INCLUDE_PATH AUTOSTART_PATH PAYLOAD_PRESENT SERVICE_PRESENT SOCKET_PRESENT I3_INCLUDE_PRESENT AUTOSTART_PRESENT SYNC_HELPER_PRESENT START_HELPER_PRESENT READINESS_HELPER_PRESENT TARGETS_HELPER_PRESENT HANDOFF_HELPER_PRESENT SYSTEMCTL_AVAILABLE UNIT_ENABLED_STATE',
        "python3 - <<'PY'",
        'import json, os',
        'warnings = [item for item in os.environ.get("WARNINGS", "").split() if item]',
        'install_complete = os.environ.get("INSTALL_COMPLETE", "0") == "1"',
        'session_readiness = os.environ.get("SESSION_READINESS_OK", "unknown")',
        'session_targets = os.environ.get("SESSION_TARGETS_OK", "unknown")',
        'startup_handoff = os.environ.get("STARTUP_HANDOFF_OK", "unknown")',
        'unit_active_state = os.environ.get("UNIT_ACTIVE_STATE", "unknown")',
        'runtime_startable_now = install_complete and session_readiness == "true" and session_targets == "true" and startup_handoff == "true"',
        'runtime_active_now = unit_active_state == "active"',
        'payload = {',
        '    "schema_version": 1,',
        '    "stack_kind": "vhk.i3_x11.flagship_user_session_install_verdict",',
        '    "install_complete": install_complete,',
        '    "runtime_startable_now": runtime_startable_now,',
        '    "runtime_active_now": runtime_active_now,',
        '    "unit_name": os.environ.get("UNIT_NAME", ""),',
        '    "paths": {',
        '        "payload_dir": os.environ.get("PAYLOAD_DIR", ""),',
        '        "service_unit": os.environ.get("SERVICE_PATH", ""),',
        '        "socket_unit": os.environ.get("SOCKET_PATH", ""),',
        '        "i3_include": os.environ.get("I3_INCLUDE_PATH", ""),',
        '        "autostart_desktop": os.environ.get("AUTOSTART_PATH", ""),',
        '    },',
        '    "artifacts": {',
        '        "payload_present": os.environ.get("PAYLOAD_PRESENT", "0") == "1",',
        '        "service_present": os.environ.get("SERVICE_PRESENT", "0") == "1",',
        '        "socket_present": os.environ.get("SOCKET_PRESENT", ""),',
        '        "i3_include_present": os.environ.get("I3_INCLUDE_PRESENT", "0") == "1",',
        '        "autostart_present": os.environ.get("AUTOSTART_PRESENT", ""),',
        '        "sync_helper_present": os.environ.get("SYNC_HELPER_PRESENT", "0") == "1",',
        '        "start_helper_present": os.environ.get("START_HELPER_PRESENT", "0") == "1",',
        '        "readiness_helper_present": os.environ.get("READINESS_HELPER_PRESENT", "0") == "1",',
        '        "targets_helper_present": os.environ.get("TARGETS_HELPER_PRESENT", "0") == "1",',
        '        "handoff_helper_present": os.environ.get("HANDOFF_HELPER_PRESENT", "0") == "1",',
        '    },',
        '    "session": {',
        '        "readiness_ok": session_readiness,',
        '        "targets_ok": session_targets,',
        '        "startup_handoff_ok": startup_handoff,',
        '    },',
        '    "systemd_user": {',
        '        "available": os.environ.get("SYSTEMCTL_AVAILABLE", "0") == "1",',
        '        "enabled_state": os.environ.get("UNIT_ENABLED_STATE", "unknown"),',
        '        "active_state": unit_active_state,',
        '    },',
        '    "warnings": warnings,',
        '    "summary": (',
        '        "Installed warm-lane artifacts are present and the live X11/i3 session looks startable."',
        '        if runtime_startable_now else',
        '        "Inspect warnings; the installed warm-lane bridge still has missing artifacts or live-session blockers."',
        '    ),',
        '}',
        'print(json.dumps(payload, indent=2, sort_keys=False))',
        'PY',
        '',
    ])
    return "\n".join(lines)


def render_i3_x11_flagship_stack_verify_user_session(pack: dict[str, Any]) -> str:
    lines = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        'SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"',
        'VERIFY_JSON="$SCRIPT_DIR/verify_user_session_json.sh"',
        'if [ ! -x "$VERIFY_JSON" ]; then',
        '  echo "verify_user_session_json.sh is missing or not executable" >&2',
        '  exit 1',
        'fi',
        'TMP_JSON="$(mktemp "${TMPDIR:-/tmp}/vhk-verify-user-session.XXXXXX.json")"',
        "trap 'rm -f \"$TMP_JSON\"' EXIT HUP INT TERM",
        'sh "$VERIFY_JSON" > "$TMP_JSON"',
        "python3 - \"$TMP_JSON\" <<'PY'",
        'import json, pathlib, sys',
        'payload = json.loads(pathlib.Path(sys.argv[1]).read_text())',
        'print("Install complete:", payload.get("install_complete"))',
        'print("Runtime startable now:", payload.get("runtime_startable_now"))',
        'print("Runtime active now:", payload.get("runtime_active_now"))',
        'session = dict(payload.get("session") or {})',
        'print("Session readiness:", session.get("readiness_ok"))',
        'print("Session targets:", session.get("targets_ok"))',
        'print("Startup handoff:", session.get("startup_handoff_ok"))',
        'systemd_user = dict(payload.get("systemd_user") or {})',
        'print("Unit active state:", systemd_user.get("active_state"))',
        'warnings = list(payload.get("warnings") or [])',
        'if warnings:',
        '    print("Warnings: " + ", ".join(warnings))',
        'else:',
        '    print("Warnings: none")',
        'print(payload.get("summary") or "")',
        'PY',
        '',
    ]
    return "\n".join(lines)


def render_i3_x11_flagship_stack_repair_user_session(pack: dict[str, Any]) -> str:
    install_story = dict(pack.get("install_story") or {})
    command_name = str(install_story.get("command_name") or install_story.get("unit_base") or "vhk-busd-project")
    lines = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        'SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"',
        'VERIFY_JSON="$SCRIPT_DIR/verify_user_session_json.sh"',
        'INSTALL_SCRIPT="$SCRIPT_DIR/install_user_session.sh"',
        'if [ ! -x "$INSTALL_SCRIPT" ]; then',
        '  echo "install_user_session.sh is missing or not executable" >&2',
        '  exit 1',
        'fi',
        'sh "$INSTALL_SCRIPT"',
        'XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"',
        f'PAYLOAD_DIR="$XDG_CONFIG_HOME/vhk/{command_name}/session-service"',
        'if [ -x "$PAYLOAD_DIR/sync_session_activation_env.sh" ]; then',
        '  "$PAYLOAD_DIR/sync_session_activation_env.sh" >/dev/null 2>&1 || true',
        'fi',
        'REPAIR_INSTALL_ONLY="${VHK_REPAIR_INSTALL_ONLY:-${VHK_SKIP_SYSTEMCTL:-0}}"',
        'if [ "$REPAIR_INSTALL_ONLY" != "1" ] && [ -x "$PAYLOAD_DIR/start_user_session.sh" ]; then',
        '  "$PAYLOAD_DIR/start_user_session.sh" >/dev/null 2>&1 || true',
        'fi',
        'if [ -x "$VERIFY_JSON" ]; then',
        '  TMP_JSON="$(mktemp "${TMPDIR:-/tmp}/vhk-repair-user-session.XXXXXX.json")"',
        "  trap 'rm -f \"$TMP_JSON\"' EXIT HUP INT TERM",
        '  sh "$VERIFY_JSON" > "$TMP_JSON"',
        "  python3 - \"$TMP_JSON\" <<'PY'",
        'import json, pathlib, sys',
        'payload = json.loads(pathlib.Path(sys.argv[1]).read_text())',
        'import os',
        'install_only = os.environ.get("VHK_REPAIR_INSTALL_ONLY", os.environ.get("VHK_SKIP_SYSTEMCTL", "0")) == "1"',
        'if payload.get("install_complete") and (payload.get("runtime_startable_now") or install_only):',
        '    print("Repaired flagship VHK i3/X11 user session lane." if not install_only else "Rehearsed flagship VHK i3/X11 user session install lane.")',
        '    sys.exit(0)',
        'print(payload.get("summary") or "Repair left unresolved blockers.", file=sys.stderr)',
        'warnings = list(payload.get("warnings") or [])',
        'if warnings:',
        '    print("Warnings: " + ", ".join(warnings), file=sys.stderr)',
        'sys.exit(1)',
        'PY',
        'fi',
        'printf "%s\n" "Repaired flagship VHK i3/X11 user session lane."',
        '',
    ]
    return "\n".join(lines)
