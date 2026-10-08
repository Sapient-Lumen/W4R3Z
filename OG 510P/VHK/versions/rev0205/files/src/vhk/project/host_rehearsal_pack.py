from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from vhk.project.service_compose_pack import build_service_compose_plan, write_service_compose_pack


def _write_if_allowed(path: Path, content: bytes | str, *, force: bool) -> None:
    if path.exists() and not force:
        raise ValueError(f"Refusing to overwrite existing file: {path}. Use --force.")
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


def _copy_if_present(src: Path, dest: Path) -> bool:
    if not src.is_file():
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return True


def _rehearsal_paths(plan: dict[str, Any]) -> dict[str, str]:
    handoff = dict(plan.get("publish_handoff") or {})
    root = str(handoff.get("root") or "build/publish/project")
    native_story = dict(plan.get("native_install_story") or {})
    service_story = dict(plan.get("service_compose_story") or {})
    app_id = str(native_story.get("app_id") or service_story.get("app_id") or "io.visualhotkey.project")
    command_name = str(native_story.get("command_name") or service_story.get("command_name") or "vhk-project")
    bundle_name = str(native_story.get("bundle_name") or service_story.get("bundle_name") or "project.zip")
    rehearsal_root = f"{root}/rehearsal"
    xdg_data = "${XDG_DATA_HOME:-$HOME/.local/share}"
    xdg_config = "${XDG_CONFIG_HOME:-$HOME/.config}"
    xdg_state = "${XDG_STATE_HOME:-$HOME/.local/state}"
    bin_home = "${VHK_BIN_HOME:-$HOME/.local/bin}"
    install_root = f"{xdg_data}/vhk/apps/{command_name}"
    report_root = f"{xdg_state}/vhk/rehearsal/{command_name}"
    return {
        "rehearsal_root": rehearsal_root,
        "rehearsal_manifest": f"{rehearsal_root}/vhk_host_rehearsal_handoff.json",
        "rehearsal_readme": f"{rehearsal_root}/README.md",
        "rehearsal_refresh_script": f"{rehearsal_root}/refresh_host_rehearsal_inputs.sh",
        "rehearsal_install_script": f"{rehearsal_root}/install_reviewed_lane.sh",
        "rehearsal_status_script": f"{rehearsal_root}/status_reviewed_lane.sh",
        "rehearsal_report_script": f"{rehearsal_root}/report_reviewed_lane.sh",
        "rehearsal_logs_script": f"{rehearsal_root}/logs_reviewed_lane.sh",
        "rehearsal_uninstall_script": f"{rehearsal_root}/uninstall_reviewed_lane.sh",
        "rehearsal_smoke_script": f"{rehearsal_root}/rehearse_reviewed_lane.sh",
        "rehearsal_docs_root": f"{rehearsal_root}/docs",
        "rehearsal_report_root": report_root,
        "rehearsal_report_json": f"{report_root}/VHK_HOST_REHEARSAL_REPORT.json",
        "rehearsal_report_markdown": f"{report_root}/VHK_HOST_REHEARSAL_REPORT.md",
        "installed_app_root": install_root,
        "installed_bundle": f"{install_root}/share/vhk/project/{bundle_name}",
        "installed_launcher": f"{bin_home}/{command_name}",
        "installed_desktop_file": f"{xdg_data}/applications/{app_id}.desktop",
        "installed_metainfo": f"{xdg_data}/metainfo/{app_id}.metainfo.xml",
        "installed_icon": f"{xdg_data}/icons/hicolor/256x256/apps/{app_id}.png",
        "installed_env_file": f"{xdg_config}/environment.d/80-vhk-{command_name}.conf",
    }


def _host_rehearsal_constraints(plan: dict[str, Any]) -> list[str]:
    project = dict(plan.get("project") or {})
    native_story = dict(plan.get("native_install_story") or {})
    service_story = dict(plan.get("service_compose_story") or {})
    constraints = [
        "Treat host rehearsal as a layered proof: bundle creation, native app assembly, desktop-entry discoverability, and user-service status/log inspection each validate a different Linux-facing seam.",
        "Keep desktop-shell checks honest: validating a desktop file and naming a gtk-launch id is useful, but menu indexing and shell discoverability still vary by desktop environment and user session.",
        "Use systemctl/journalctl when available because long-lived watcher lanes live or die on user-service status and logs, not just whether files landed on disk.",
        "Keep the reviewed bundle as the source of truth; install/rehearsal flows should always assemble from the published bundle and never silently fall back to the mutable project checkout.",
    ]
    if str(service_story.get("service_mode") or "environment-only") == "socket-activated-busd":
        constraints.append("This rehearsal lane assumes one socket-activated VHK-owned busd watcher plane; if the project depends on adjacent helpers, review those helper services separately.")
    else:
        constraints.append("This project does not declare a first-party long-lived watcher service, so the rehearsal pack focuses on native install, environment scaffolding, and desktop discoverability instead of pretending a daemon exists.")
    if str(native_story.get("bundle_kind") or "project") == "release-stage" and native_story.get("bundle_profile_id"):
        constraints.append(f"This rehearsal pack is pinned to the `{native_story.get('bundle_profile_id')}` release-stage lane; refresh the handoff whenever that staged payload changes.")
    if str(project.get("desktop_backend") or "").strip().lower() == "wayland":
        constraints.append("For Wayland-first projects, treat a green rehearsal as proof of one conservative user-local lane only; it does not erase portal consent, compositor policy, or raw-input helper requirements.")
    return constraints


def build_host_rehearsal_plan(
    project_dir: Path,
    *,
    bundle_target_profile: str | None = None,
    app_id: str | None = None,
    runtime: str = "org.freedesktop.Platform",
    runtime_version: str = "24.08",
    sdk: str = "org.freedesktop.Sdk",
    python_cmd: str = "python",
) -> dict[str, Any]:
    project_dir = project_dir.expanduser().resolve()
    plan = build_service_compose_plan(
        project_dir,
        bundle_target_profile=bundle_target_profile,
        app_id=app_id,
        runtime=runtime,
        runtime_version=runtime_version,
        sdk=sdk,
        python_cmd=python_cmd,
    )
    native_story = dict(plan.get("native_install_story") or {})
    service_story = dict(plan.get("service_compose_story") or {})
    paths = _rehearsal_paths(plan)
    app_id_value = str(native_story.get("app_id") or service_story.get("app_id") or "io.visualhotkey.project")
    command_name = str(native_story.get("command_name") or service_story.get("command_name") or "vhk-project")
    bundle_name = str(native_story.get("bundle_name") or service_story.get("bundle_name") or "project.zip")
    unit_base = str(service_story.get("unit_base") or f"vhk-busd-{command_name}")
    service_mode = str(service_story.get("service_mode") or "environment-only")
    host_story = {
        "headline": "Generate an end-to-end host rehearsal handoff that installs one reviewed VHK bundle as a local app, validates desktop-entry discoverability, and inspects the user-service lane with status/log helpers instead of leaving the proving path in shell history.",
        "app_id": app_id_value,
        "command_name": command_name,
        "bundle_name": bundle_name,
        "bundle_kind": str(native_story.get("bundle_kind") or "project"),
        "bundle_profile_id": str(native_story.get("bundle_profile_id") or "").strip() or None,
        "desktop_backend": str(plan.get("project", {}).get("desktop_backend") or "unknown"),
        "python_cmd": python_cmd,
        "service_mode": service_mode,
        "runner_mode": str(service_story.get("runner_mode") or "bundle-state"),
        "launcher_link": paths["installed_launcher"],
        "install_root": paths["installed_app_root"],
        "desktop_file": paths["installed_desktop_file"],
        "bundle_path": paths["installed_bundle"],
        "env_file": paths["installed_env_file"],
        "report_root": paths["rehearsal_report_root"],
        "report_json": paths["rehearsal_report_json"],
        "report_markdown": paths["rehearsal_report_markdown"],
        "unit_base": unit_base,
        "service_units": {
            "service": f"{unit_base}.service" if service_mode != "environment-only" else None,
            "socket": f"{unit_base}.socket" if service_mode == "socket-activated-busd" else None,
        },
        "validation_tools": [
            {"tool": "desktop-file-validate", "purpose": "Validate the installed desktop entry against the spec when desktop-file-utils is available."},
            {"tool": "gtk-launch", "purpose": "Probe launcher id alignment with the installed desktop file when GTK tooling is available."},
            {"tool": "systemctl --user", "purpose": "Inspect enablement, active state, and unit search paths for the VHK-owned session-service lane."},
            {"tool": "systemd-analyze --user verify", "purpose": "Best-effort static verification for installed VHK user-unit files without depending on a successful start."},
            {"tool": "journalctl --user", "purpose": "Read recent logs for the VHK-owned service/socket lane without guessing where output landed."},
        ],
        "constraints": _host_rehearsal_constraints(plan),
    }
    plan["host_rehearsal_paths"] = paths
    plan["host_rehearsal_story"] = host_story
    plan["host_rehearsal_commands"] = [
        "vhk gen-service-compose-pack . --force",
        f"sh {paths['rehearsal_install_script']}",
        f"sh {paths['rehearsal_status_script']}",
        f"sh {paths['rehearsal_report_script']}",
        f"sh {paths['rehearsal_logs_script']}",
        f"sh {paths['rehearsal_uninstall_script']}",
        f"sh {paths['rehearsal_smoke_script']}",
    ]
    plan["host_rehearsal_summary"] = {
        "app_id": app_id_value,
        "command_name": command_name,
        "bundle_kind": host_story["bundle_kind"],
        "service_mode": service_mode,
        "runner_mode": host_story["runner_mode"],
    }
    plan["source_contract"] = "host_rehearsal_pack"
    return plan


def render_host_rehearsal_doc(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    story = dict(plan.get("host_rehearsal_story") or {})
    paths = dict(plan.get("host_rehearsal_paths") or {})
    lines = [
        f"# VHK host rehearsal pack for {project.get('name') or 'project'}",
        "",
        "Generated by `vhk gen-host-rehearsal-pack`. Use it to prove one conservative reviewed-bundle lane end to end: assemble/install the native app, validate desktop-entry discoverability, inspect user-service status/logs, and roll the whole thing back cleanly.",
        "",
        "## Rehearsal posture",
        "",
        f"- App id: `{story.get('app_id') or 'io.visualhotkey.project'}`",
        f"- Command: `{story.get('command_name') or 'vhk-project'}`",
        f"- Bundle kind: `{story.get('bundle_kind') or 'project'}`",
        f"- Bundle name: `{story.get('bundle_name') or 'project.zip'}`",
        f"- Service mode: `{story.get('service_mode') or 'environment-only'}`",
        f"- Runner mode: `{story.get('runner_mode') or 'bundle-state'}`",
        "",
        "## Installed targets",
        "",
        f"- App root: `{paths.get('installed_app_root')}`",
        f"- Launcher link: `{paths.get('installed_launcher')}`",
        f"- Desktop file: `{paths.get('installed_desktop_file')}`",
        f"- Reviewed bundle path: `{paths.get('installed_bundle')}`",
        f"- Environment file: `{paths.get('installed_env_file')}`",
        f"- Rehearsal report root: `{paths.get('rehearsal_report_root')}`",
        f"- Rehearsal report JSON: `{paths.get('rehearsal_report_json')}`",
        "",
        "## Validation tools",
        "",
    ]
    for item in [x for x in list(story.get("validation_tools") or []) if isinstance(x, dict)]:
        lines.append(f"- `{item.get('tool')}` — {item.get('purpose')}")
    lines.extend([
        "",
        "## Constraints",
        "",
    ])
    for item in [str(x) for x in list(story.get("constraints") or []) if str(x)]:
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## Review commands",
        "",
    ])
    for cmd in [str(x) for x in list(plan.get("host_rehearsal_commands") or []) if str(x)]:
        lines.append(f"- `{cmd}`")
    lines.append("")
    return "\n".join(lines)


def render_host_rehearsal_handoff_readme(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    story = dict(plan.get("host_rehearsal_story") or {})
    paths = dict(plan.get("host_rehearsal_paths") or {})
    unit_base = str(story.get("unit_base") or "vhk-busd-project")
    return "\n".join(
        [
            f"# VHK host rehearsal handoff for {project.get('name') or 'project'}",
            "",
            "Generated by `vhk gen-host-rehearsal-pack`. This tree turns the reviewed bundle/native/service packs into one operable proving lane: install it, inspect status, read logs, then uninstall it without guessing which generated scripts matter.",
            "",
            f"- Bundle kind: `{story.get('bundle_kind') or 'project'}`",
            f"- Bundle name: `{story.get('bundle_name') or 'project.zip'}`",
            f"- Command name: `{story.get('command_name') or 'vhk-project'}`",
            f"- Service mode: `{story.get('service_mode') or 'environment-only'}`",
            f"- Unit base: `{unit_base}`",
            "",
            "## Generated scripts",
            "",
            f"- Install: `{paths.get('rehearsal_install_script')}`",
            f"- Status: `{paths.get('rehearsal_status_script')}`",
            f"- Logs: `{paths.get('rehearsal_logs_script')}`",
            f"- Report: `{paths.get('rehearsal_report_script')}`",
            f"- Uninstall: `{paths.get('rehearsal_uninstall_script')}`",
            f"- Rehearsal smoke: `{paths.get('rehearsal_smoke_script')}`",
            "",
            "## Flow",
            "",
            "1. Refresh the lower-level native/service handoffs.",
            "2. Assemble and install the reviewed native bundle lane.",
            "3. Validate desktop-entry alignment and inspect service status/logs.",
            "4. Collect one live rehearsal report from the installed launcher and best-effort systemd validation.",
            "5. Uninstall the lane or rerun the rehearsal smoke path under temporary XDG roots.",
            "",
        ]
    )


def render_host_rehearsal_refresh_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("bundle_release_story") or {})
    profile = str(story.get("bundle_profile_id") or "").strip()
    lines = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        'SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"',
        'PROJECT_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/../../../.." && pwd)"',
        'cd "$PROJECT_DIR"',
        "",
        'printf "%s\\n" "Refreshing VHK host rehearsal pack inputs..."',
    ]
    service = 'vhk gen-service-compose-pack . --force --quiet'
    rehearsal = 'vhk gen-host-rehearsal-pack . --force --quiet'
    if profile:
        service += f' --bundle-target-profile {profile}'
        rehearsal += f' --bundle-target-profile {profile}'
    for cmd in [service, rehearsal]:
        lines.append(f'printf "+ %s\\n" {cmd!r}')
        lines.append(f'sh -lc {cmd!r} || true')
    lines.extend([
        'printf "%s\\n" "Host rehearsal pack refresh complete."',
        "",
    ])
    return "\n".join(lines)


def _render_install_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("host_rehearsal_story") or {})
    app_id = str(story.get("app_id") or "io.visualhotkey.project")
    service_mode = str(story.get("service_mode") or "environment-only")
    lines = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        'SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"',
        'PUBLISH_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"',
        'printf "%s\\n" "Assembling reviewed VHK native lane..."',
        'sh "$PUBLISH_ROOT/native/assemble_native_app.sh"',
        'printf "%s\\n" "Installing reviewed VHK native lane..."',
        'sh "$PUBLISH_ROOT/native/install_xdg_local_app.sh"',
        'if [ -x "$PUBLISH_ROOT/service/install_user_session.sh" ]; then',
        '  printf "%s\\n" "Installing VHK session-service composition..."',
        '  sh "$PUBLISH_ROOT/service/install_user_session.sh"',
        'fi',
        f'printf "%s\\n" "Desktop launch probe: gtk-launch {app_id}"',
    ]
    if service_mode == "socket-activated-busd":
        unit_base = str(story.get("unit_base") or "vhk-busd-project")
        lines.append(f'printf "%s\\n" "User service probe: systemctl --user status {unit_base}.socket {unit_base}.service"')
    lines.extend([
        'printf "%s\\n" "Run status_reviewed_lane.sh next to inspect launcher/service health."',
        'printf "%s\\n" "Run report_reviewed_lane.sh next to capture one machine-readable rehearsal report."',
        "",
    ])
    return "\n".join(lines)


def _render_status_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("host_rehearsal_story") or {})
    app_id = str(story.get("app_id") or "io.visualhotkey.project")
    command_name = str(story.get("command_name") or "vhk-project")
    bundle_name = str(story.get("bundle_name") or "project.zip")
    service_mode = str(story.get("service_mode") or "environment-only")
    unit_base = str(story.get("unit_base") or "vhk-busd-project")
    lines = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        'XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"',
        'XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"',
        'VHK_BIN_HOME="${VHK_BIN_HOME:-$HOME/.local/bin}"',
        'ok=1',
        f'APP_ROOT="$XDG_DATA_HOME/vhk/apps/{command_name}"',
        f'BUNDLE_PATH="$APP_ROOT/share/vhk/project/{bundle_name}"',
        f'DESKTOP_FILE="$XDG_DATA_HOME/applications/{app_id}.desktop"',
        f'LAUNCHER_LINK="$VHK_BIN_HOME/{command_name}"',
        f'ENV_FILE="$XDG_CONFIG_HOME/environment.d/80-vhk-{command_name}.conf"',
        'printf "%s\\n" "VHK reviewed-lane status"',
        'printf "%s\\n" "========================="',
        'if [ -x "$LAUNCHER_LINK" ]; then printf "%s\\n" "launcher: ok ($LAUNCHER_LINK)"; else printf "%s\\n" "launcher: missing ($LAUNCHER_LINK)" >&2; ok=0; fi',
        'if [ -f "$BUNDLE_PATH" ]; then printf "%s\\n" "bundle: ok ($BUNDLE_PATH)"; else printf "%s\\n" "bundle: missing ($BUNDLE_PATH)" >&2; ok=0; fi',
        'if [ -f "$DESKTOP_FILE" ]; then printf "%s\\n" "desktop-file: ok ($DESKTOP_FILE)"; else printf "%s\\n" "desktop-file: missing ($DESKTOP_FILE)" >&2; ok=0; fi',
        'if [ -f "$ENV_FILE" ]; then printf "%s\\n" "environment: present ($ENV_FILE)"; else printf "%s\\n" "environment: missing ($ENV_FILE)"; fi',
        'if command -v desktop-file-validate >/dev/null 2>&1 && [ -f "$DESKTOP_FILE" ]; then',
        '  if desktop-file-validate "$DESKTOP_FILE"; then',
        '    printf "%s\\n" "desktop-file-validate: ok"',
        '  else',
        '    printf "%s\\n" "desktop-file-validate: failed" >&2',
        '    ok=0',
        '  fi',
        'else',
        '  printf "%s\\n" "desktop-file-validate: skipped (desktop-file-utils not installed)"',
        'fi',
        'if command -v gtk-launch >/dev/null 2>&1; then',
        f'  printf "%s\\n" "gtk-launch probe id: {app_id}"',
        'else',
        '  printf "%s\\n" "gtk-launch: skipped (GTK launcher tool not installed)"',
        'fi',
    ]
    if service_mode == "socket-activated-busd":
        lines.extend([
            'if [ "${VHK_SKIP_SYSTEMCTL:-0}" != "1" ] && command -v systemctl >/dev/null 2>&1; then',
            f'  printf "%s\\n" "systemctl --user is-enabled {unit_base}.socket"',
            f'  systemctl --user is-enabled {unit_base}.socket || true',
            f'  printf "%s\\n" "systemctl --user is-active {unit_base}.socket"',
            f'  systemctl --user is-active {unit_base}.socket || true',
            f'  printf "%s\\n" "systemctl --user is-active {unit_base}.service"',
            f'  systemctl --user is-active {unit_base}.service || true',
            f'  systemctl --user show -p FragmentPath -p ActiveState -p SubState {unit_base}.socket {unit_base}.service || true',
            'else',
            '  printf "%s\\n" "systemctl --user: skipped"',
            'fi',
            'if command -v journalctl >/dev/null 2>&1; then',
            '  printf "%s\\n" "logs: sh ./logs_reviewed_lane.sh"',
            'else',
            '  printf "%s\\n" "journalctl: skipped"',
            'fi',
        ])
    else:
        lines.extend([
            'printf "%s\\n" "service-mode: environment-only (no VHK-owned daemon expected)"',
            'if [ "${VHK_SKIP_SYSTEMCTL:-0}" != "1" ] && command -v systemctl >/dev/null 2>&1; then',
            f'  systemctl --user show -p UnitPath --value >/dev/null 2>&1 || true',
            'fi',
        ])
    lines.extend([
        'printf "%s\n" "report: sh ./report_reviewed_lane.sh"',
        'if [ "$ok" -ne 1 ]; then exit 1; fi',
        'printf "%s\\n" "Host rehearsal status checks passed."',
        "",
    ])
    return "\n".join(lines)


def _render_report_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("host_rehearsal_story") or {})
    app_id = str(story.get("app_id") or "io.visualhotkey.project")
    command_name = str(story.get("command_name") or "vhk-project")
    bundle_name = str(story.get("bundle_name") or "project.zip")
    service_mode = str(story.get("service_mode") or "environment-only")
    unit_base = str(story.get("unit_base") or "vhk-busd-project")
    script = """#!/usr/bin/env sh
set -eu

XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
XDG_STATE_HOME="${XDG_STATE_HOME:-$HOME/.local/state}"
VHK_BIN_HOME="${VHK_BIN_HOME:-$HOME/.local/bin}"
APP_ROOT="$XDG_DATA_HOME/vhk/apps/__COMMAND_NAME__"
BUNDLE_PATH="$APP_ROOT/share/vhk/project/__BUNDLE_NAME__"
DESKTOP_FILE="$XDG_DATA_HOME/applications/__APP_ID__.desktop"
LAUNCHER_LINK="$VHK_BIN_HOME/__COMMAND_NAME__"
SYSTEMD_USER_DIR="$XDG_CONFIG_HOME/systemd/user"
REPORT_ROOT="$XDG_STATE_HOME/vhk/rehearsal/__COMMAND_NAME__"
REPORT_JSON="$REPORT_ROOT/VHK_HOST_REHEARSAL_REPORT.json"
REPORT_MD="$REPORT_ROOT/VHK_HOST_REHEARSAL_REPORT.md"
STATUS_CAPTURE="$REPORT_ROOT/status.txt"
STATUS_JSON_CAPTURE="$REPORT_ROOT/launcher-status.json"
HOME_JSON_CAPTURE="$REPORT_ROOT/app-home.json"
DESKTOP_VALIDATE_TXT="$REPORT_ROOT/desktop-validate.txt"
UNIT_PATHS_TXT="$REPORT_ROOT/unit-paths.txt"
UNIT_VERIFY_TXT="$REPORT_ROOT/unit-verify.txt"
mkdir -p "$REPORT_ROOT"

if [ -x "$LAUNCHER_LINK" ]; then
  "$LAUNCHER_LINK" --refresh-status-report >/dev/null 2>&1 || true
  "$LAUNCHER_LINK" --status-json > "$STATUS_JSON_CAPTURE" || true
  "$LAUNCHER_LINK" --home-json > "$HOME_JSON_CAPTURE" || true
  "$LAUNCHER_LINK" --status > "$STATUS_CAPTURE" || true
else
  printf '%s\n' "Launcher is missing: $LAUNCHER_LINK" > "$STATUS_CAPTURE"
  rm -f "$STATUS_JSON_CAPTURE" "$HOME_JSON_CAPTURE"
fi

if command -v desktop-file-validate >/dev/null 2>&1 && [ -f "$DESKTOP_FILE" ]; then
  desktop-file-validate "$DESKTOP_FILE" > "$DESKTOP_VALIDATE_TXT" 2>&1 || true
else
  printf '%s\n' 'desktop-file-validate skipped' > "$DESKTOP_VALIDATE_TXT"
fi

if [ "${VHK_SKIP_SYSTEMCTL:-0}" != "1" ] && command -v systemctl >/dev/null 2>&1; then
  systemctl --user show -p UnitPath --value > "$UNIT_PATHS_TXT" 2>/dev/null || true
  if [ ! -s "$UNIT_PATHS_TXT" ]; then
    printf '%s\n' 'systemctl unit-path lookup returned no data' > "$UNIT_PATHS_TXT"
  fi
else
  printf '%s\n' 'systemctl --user skipped' > "$UNIT_PATHS_TXT"
fi

__UNIT_VERIFY_BLOCK__

if command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD="$(command -v python)"
else
  printf '%s\n' 'python is required to assemble the host rehearsal report.' >&2
  exit 1
fi

"$PYTHON_CMD" - "$REPORT_JSON" "$REPORT_MD" "$STATUS_JSON_CAPTURE" "$HOME_JSON_CAPTURE" "$STATUS_CAPTURE" "$DESKTOP_VALIDATE_TXT" "$UNIT_PATHS_TXT" "$UNIT_VERIFY_TXT" "$LAUNCHER_LINK" "$BUNDLE_PATH" "$DESKTOP_FILE" "$REPORT_ROOT" "$APP_ROOT" <<'PY'
import json
import sys
import time
from pathlib import Path

report_json = Path(sys.argv[1])
report_md = Path(sys.argv[2])
status_json_path = Path(sys.argv[3])
home_json_path = Path(sys.argv[4])
status_capture_path = Path(sys.argv[5])
desktop_validate_path = Path(sys.argv[6])
unit_paths_path = Path(sys.argv[7])
unit_verify_path = Path(sys.argv[8])
launcher_link = Path(sys.argv[9])
bundle_path = Path(sys.argv[10])
desktop_file = Path(sys.argv[11])
report_root = Path(sys.argv[12])
app_root = Path(sys.argv[13])

def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text())
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}

def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text()
    except Exception:
        return ""

launcher_status = load_json(status_json_path)
app_home = load_json(home_json_path)
desktop_validate = read_text(desktop_validate_path).strip()
unit_paths = [line for line in read_text(unit_paths_path).splitlines() if line.strip()]
unit_verify = read_text(unit_verify_path).strip()
status_stdout = read_text(status_capture_path).strip()
service_units = []
service = launcher_status.get("service") if isinstance(launcher_status, dict) else {}
if isinstance(service, dict):
    service_units = [dict(x) for x in list(service.get("units") or []) if isinstance(x, dict)]
app_meta = launcher_status.get("app") if isinstance(launcher_status, dict) else {}
healthy = launcher_link.exists() and bundle_path.exists() and desktop_file.exists() and bool(launcher_status)
report = {
    "generated_at_epoch": time.time(),
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "healthy": bool(healthy),
    "app": app_meta if isinstance(app_meta, dict) else {},
    "host_rehearsal": {
        "report_root": str(report_root),
        "launcher_link": str(launcher_link),
        "bundle_path": str(bundle_path),
        "desktop_file": str(desktop_file),
        "app_root": str(app_root),
        "launcher_exists": launcher_link.exists(),
        "bundle_exists": bundle_path.exists(),
        "desktop_file_exists": desktop_file.exists(),
        "desktop_validate": desktop_validate,
        "unit_paths": unit_paths,
        "unit_verify": unit_verify,
        "status_stdout_path": str(status_capture_path),
    },
    "launcher_status": launcher_status,
    "launcher_home": app_home,
}
report_json.parent.mkdir(parents=True, exist_ok=True)
report_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
lines = [
    f"# VHK host rehearsal report for {(app_meta or {}).get('name') or app_root.name}",
    "",
    f"- Generated at: `{report['generated_at']}`",
    f"- Healthy: `{str(report['healthy']).lower()}`",
    f"- Launcher: `{launcher_link}`",
    f"- Bundle: `{bundle_path}`",
    f"- Desktop file: `{desktop_file}`",
    "",
    "## Installed-lane report bridge",
    "",
    f"- App root: `{app_root}`",
    f"- Runtime source: `{((app_meta or {}).get('runtime_source') or 'unknown')}`",
    f"- Launcher status JSON present: `{str(bool(launcher_status)).lower()}`",
    "",
    "## Desktop validation",
    "",
]
if desktop_validate:
    for line in desktop_validate.splitlines()[:16]:
        lines.append(f"- {line}")
else:
    lines.append("- desktop-file-validate returned no output (this usually means success).")
lines.extend(["", "## User-service visibility", ""])
if unit_paths:
    lines.append("- Unit search paths:")
    for line in unit_paths[:8]:
        lines.append(f"  - `{line}`")
else:
    lines.append("- Unit search paths unavailable.")
if unit_verify:
    lines.append("- Unit verification:")
    for line in unit_verify.splitlines()[:20]:
        lines.append(f"  - {line}")
else:
    lines.append("- Unit verification output unavailable.")
if service_units:
    lines.append("- Live unit state:")
    for row in service_units[:6]:
        summary = f"load={row.get('load_state') or 'unknown'} active={row.get('active_state') or 'unknown'}"
        if row.get('sub_state'):
            summary += f" sub={row.get('sub_state')}"
        if row.get('unit_file_state'):
            summary += f" enabled={row.get('unit_file_state')}"
        lines.append(f"  - `{row.get('unit') or 'unit'}` — {summary}")
else:
    lines.append("- No live unit rows were captured from the installed lane.")
lines.extend(["", "## Captured launcher status", ""])
if status_stdout:
    for line in status_stdout.splitlines()[:20]:
        lines.append(f"- {line}")
else:
    lines.append("- Launcher status output unavailable.")
lines.extend(["", "## Machine-readable report", "", f"- `{report_json}`", ""])
report_md.write_text("\n".join(lines).rstrip() + "\n")
print(report_json)
PY

printf '%s\n' "$REPORT_JSON"
if [ -f "$REPORT_MD" ]; then
  printf '%s\n' "$REPORT_MD"
fi
if [ ! -x "$LAUNCHER_LINK" ] || [ ! -f "$BUNDLE_PATH" ] || [ ! -f "$DESKTOP_FILE" ]; then
  exit 1
fi
"""
    if service_mode == "socket-activated-busd":
        verify_block = f"""if command -v systemd-analyze >/dev/null 2>&1 && [ -f \"$SYSTEMD_USER_DIR/{unit_base}.socket\" ] && [ -f \"$SYSTEMD_USER_DIR/{unit_base}.service\" ]; then
  systemd-analyze --user --man=no verify \"$SYSTEMD_USER_DIR/{unit_base}.socket\" \"$SYSTEMD_USER_DIR/{unit_base}.service\" > \"$UNIT_VERIFY_TXT\" 2>&1 || true
else
  printf '%s\\n' 'systemd-analyze verify skipped' > \"$UNIT_VERIFY_TXT\"
fi"""
    elif service_mode != "environment-only":
        verify_block = f"""if command -v systemd-analyze >/dev/null 2>&1 && [ -f \"$SYSTEMD_USER_DIR/{unit_base}.service\" ]; then
  systemd-analyze --user --man=no verify \"$SYSTEMD_USER_DIR/{unit_base}.service\" > \"$UNIT_VERIFY_TXT\" 2>&1 || true
else
  printf '%s\\n' 'systemd-analyze verify skipped' > \"$UNIT_VERIFY_TXT\"
fi"""
    else:
        verify_block = "printf '%s\\n' 'no VHK-owned user units expected' > \"$UNIT_VERIFY_TXT\""
    return (script
        .replace("__APP_ID__", app_id)
        .replace("__COMMAND_NAME__", command_name)
        .replace("__BUNDLE_NAME__", bundle_name)
        .replace("__UNIT_VERIFY_BLOCK__", verify_block)
    )


def _render_logs_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("host_rehearsal_story") or {})
    service_mode = str(story.get("service_mode") or "environment-only")
    unit_base = str(story.get("unit_base") or "vhk-busd-project")
    lines = [
        "#!/usr/bin/env sh",
        "set -eu",
        'LINES="${LINES:-100}"',
    ]
    if service_mode == "socket-activated-busd":
        lines.extend([
            'if command -v journalctl >/dev/null 2>&1; then',
            f'  exec journalctl --user --no-pager -n "$LINES" -u {unit_base}.socket -u {unit_base}.service "$@"',
            'fi',
            'printf "%s\\n" "journalctl is not available; cannot show VHK user-service logs." >&2',
            'exit 1',
            "",
        ])
    else:
        lines.extend([
            'printf "%s\\n" "This rehearsal lane does not declare a VHK-owned user service, so there are no first-party logs to show."',
            "",
        ])
    return "\n".join(lines)


def _render_uninstall_script(plan: dict[str, Any]) -> str:
    lines = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        'SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"',
        'PUBLISH_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"',
        'if [ -x "$PUBLISH_ROOT/service/uninstall_user_session.sh" ]; then',
        '  sh "$PUBLISH_ROOT/service/uninstall_user_session.sh"',
        'fi',
        'sh "$PUBLISH_ROOT/native/uninstall_xdg_local_app.sh"',
        'printf "%s\\n" "Removed reviewed VHK host rehearsal lane."',
        "",
    ]
    return "\n".join(lines)


def _render_smoke_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("host_rehearsal_story") or {})
    command_name = str(story.get("command_name") or "vhk-project")
    app_id = str(story.get("app_id") or "io.visualhotkey.project")
    service_mode = str(story.get("service_mode") or "environment-only")
    config_rel = str((plan.get("service_compose_story") or {}).get("systemd_directories", {}).get("configuration") or f"vhk/{command_name}/session-service")
    lines = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        'SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"',
        'PUBLISH_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"',
        'SMOKE_ROOT="$SCRIPT_DIR/.smoke-root"',
        'rm -rf "$SMOKE_ROOT"',
        'mkdir -p "$SMOKE_ROOT/home" "$SMOKE_ROOT/data" "$SMOKE_ROOT/config" "$SMOKE_ROOT/bin"',
        'sh "$PUBLISH_ROOT/native/smoke_test_native_install.sh"',
        'if [ -x "$PUBLISH_ROOT/service/smoke_test_service_compose.sh" ]; then',
        '  sh "$PUBLISH_ROOT/service/smoke_test_service_compose.sh"',
        'fi',
        'HOME="$SMOKE_ROOT/home" XDG_DATA_HOME="$SMOKE_ROOT/data" XDG_CONFIG_HOME="$SMOKE_ROOT/config" VHK_BIN_HOME="$SMOKE_ROOT/bin" VHK_SKIP_SYSTEMCTL=1 sh "$SCRIPT_DIR/install_reviewed_lane.sh"',
        'HOME="$SMOKE_ROOT/home" XDG_DATA_HOME="$SMOKE_ROOT/data" XDG_CONFIG_HOME="$SMOKE_ROOT/config" XDG_STATE_HOME="$SMOKE_ROOT/state" VHK_BIN_HOME="$SMOKE_ROOT/bin" VHK_SKIP_SYSTEMCTL=1 sh "$SCRIPT_DIR/status_reviewed_lane.sh"',
        'HOME="$SMOKE_ROOT/home" XDG_DATA_HOME="$SMOKE_ROOT/data" XDG_CONFIG_HOME="$SMOKE_ROOT/config" XDG_STATE_HOME="$SMOKE_ROOT/state" VHK_BIN_HOME="$SMOKE_ROOT/bin" VHK_SKIP_SYSTEMCTL=1 sh "$SCRIPT_DIR/report_reviewed_lane.sh"',
        f'test -x "$SMOKE_ROOT/bin/{command_name}"',
        f'test -f "$SMOKE_ROOT/data/applications/{app_id}.desktop"',
        f'test -f "$SMOKE_ROOT/data/vhk/apps/{command_name}/share/vhk/project/{str(story.get("bundle_name") or "project.zip")}"',
        f'test -f "$SMOKE_ROOT/state/vhk/rehearsal/{command_name}/VHK_HOST_REHEARSAL_REPORT.json"',
        f'test -f "$SMOKE_ROOT/state/vhk/rehearsal/{command_name}/VHK_HOST_REHEARSAL_REPORT.md"',
    ]
    if service_mode == "socket-activated-busd":
        lines.append(f'test -e "$SMOKE_ROOT/config/{config_rel}"')
    lines.extend([
        'HOME="$SMOKE_ROOT/home" XDG_DATA_HOME="$SMOKE_ROOT/data" XDG_CONFIG_HOME="$SMOKE_ROOT/config" VHK_BIN_HOME="$SMOKE_ROOT/bin" VHK_SKIP_SYSTEMCTL=1 sh "$SCRIPT_DIR/uninstall_reviewed_lane.sh"',
        f'test ! -e "$SMOKE_ROOT/bin/{command_name}"',
        f'test ! -e "$SMOKE_ROOT/data/applications/{app_id}.desktop"',
        'printf "%s\\n" "Host rehearsal smoke test completed."',
        "",
    ])
    return "\n".join(lines)


def _materialize_host_rehearsal_handoff(project_dir: Path, plan: dict[str, Any], *, build_dir: Path, force: bool) -> dict[str, Path]:
    root = build_dir / "rehearsal"
    docs_root = root / "docs"

    manifest_path = root / "vhk_host_rehearsal_handoff.json"
    readme_path = root / "README.md"
    refresh_script = root / "refresh_host_rehearsal_inputs.sh"
    install_script = root / "install_reviewed_lane.sh"
    status_script = root / "status_reviewed_lane.sh"
    logs_script = root / "logs_reviewed_lane.sh"
    report_script = root / "report_reviewed_lane.sh"
    uninstall_script = root / "uninstall_reviewed_lane.sh"
    smoke_script = root / "rehearse_reviewed_lane.sh"

    _write_if_allowed(readme_path, render_host_rehearsal_handoff_readme(plan), force=force)
    _write_if_allowed(manifest_path, json.dumps(plan.get("host_rehearsal_story") or {}, indent=2, sort_keys=True) + "\n", force=force)
    _write_if_allowed(refresh_script, render_host_rehearsal_refresh_script(plan), force=force)
    _write_if_allowed(install_script, _render_install_script(plan), force=force)
    _write_if_allowed(status_script, _render_status_script(plan), force=force)
    _write_if_allowed(report_script, _render_report_script(plan), force=force)
    _write_if_allowed(logs_script, _render_logs_script(plan), force=force)
    _write_if_allowed(uninstall_script, _render_uninstall_script(plan), force=force)
    _write_if_allowed(smoke_script, _render_smoke_script(plan), force=force)

    for path in [refresh_script, install_script, status_script, report_script, logs_script, uninstall_script, smoke_script]:
        path.chmod(0o755)

    copied_docs: list[str] = []
    for rel in [
        "docs/VHK_PUBLIC_SUPPORT.md",
        "docs/VHK_INSTALL_QUICKSTART.md",
        "docs/VHK_NATIVE_INSTALL.md",
        "docs/VHK_SERVICE_COMPOSE.md",
        "docs/VHK_HOST_REHEARSAL.md",
        "docs/VHK_READINESS_REPORT.md",
        "docs/VHK_HOST_FIXUPS.md",
    ]:
        if _copy_if_present(project_dir / rel, docs_root / Path(rel).name):
            copied_docs.append(rel)
    if copied_docs:
        _write_if_allowed(docs_root / ".vhk_docs_manifest.json", json.dumps({"copied_docs": copied_docs}, indent=2, sort_keys=True) + "\n", force=force)

    return {
        "rehearsal_root": root,
        "rehearsal_manifest": manifest_path,
        "rehearsal_readme": readme_path,
        "rehearsal_refresh_script": refresh_script,
        "rehearsal_install_script": install_script,
        "rehearsal_status_script": status_script,
        "rehearsal_report_script": report_script,
        "rehearsal_logs_script": logs_script,
        "rehearsal_uninstall_script": uninstall_script,
        "rehearsal_smoke_script": smoke_script,
    }


def write_host_rehearsal_pack(
    project_dir: Path,
    *,
    out_dir: Path | None = None,
    script_dir: Path | None = None,
    bundle_target_profile: str | None = None,
    app_id: str | None = None,
    runtime: str = "org.freedesktop.Platform",
    runtime_version: str = "24.08",
    sdk: str = "org.freedesktop.Sdk",
    python_cmd: str = "python",
    force: bool = False,
    rehearsal_doc: bool = True,
    plan_json: bool = True,
    script: bool = True,
) -> dict[str, Path]:
    project_dir = project_dir.expanduser().resolve()
    out_dir = (out_dir or (project_dir / "docs")).expanduser().resolve()
    script_dir = (script_dir or (project_dir / "scripts")).expanduser().resolve()

    write_service_compose_pack(
        project_dir,
        out_dir=out_dir,
        script_dir=script_dir,
        bundle_target_profile=bundle_target_profile,
        app_id=app_id,
        runtime=runtime,
        runtime_version=runtime_version,
        sdk=sdk,
        python_cmd=python_cmd,
        force=force,
        service_doc=True,
        plan_json=True,
        script=True,
    )
    plan = build_host_rehearsal_plan(
        project_dir,
        bundle_target_profile=bundle_target_profile,
        app_id=app_id,
        runtime=runtime,
        runtime_version=runtime_version,
        sdk=sdk,
        python_cmd=python_cmd,
    )

    written: dict[str, Path] = {}
    if rehearsal_doc:
        path = out_dir / "VHK_HOST_REHEARSAL.md"
        _write_if_allowed(path, render_host_rehearsal_doc(plan), force=force)
        written["rehearsal_doc"] = path
    if plan_json:
        path = out_dir / "VHK_HOST_REHEARSAL_PLAN.json"
        _write_if_allowed(path, json.dumps(plan, indent=2, sort_keys=True) + "\n", force=force)
        written["plan_json"] = path
    if script:
        path = script_dir / "vhk_refresh_host_rehearsal_pack.sh"
        _write_if_allowed(path, render_host_rehearsal_refresh_script(plan), force=force)
        path.chmod(0o755)
        written["script"] = path

    publish_root = project_dir / str((plan.get("publish_handoff") or {}).get("root") or "build/publish/project")
    written.update(_materialize_host_rehearsal_handoff(project_dir, plan, build_dir=publish_root, force=force))
    return written
