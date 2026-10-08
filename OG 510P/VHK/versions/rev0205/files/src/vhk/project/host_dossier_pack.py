from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from vhk.project.host_rehearsal_pack import build_host_rehearsal_plan, write_host_rehearsal_pack


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


def _dossier_paths(plan: dict[str, Any]) -> dict[str, str]:
    handoff = dict(plan.get("publish_handoff") or {})
    root = str(handoff.get("root") or "build/publish/project")
    story = dict(plan.get("host_rehearsal_story") or {})
    command_name = str(story.get("command_name") or "vhk-project")
    dossier_root = f"{root}/dossier"
    xdg_state = "${XDG_STATE_HOME:-$HOME/.local/state}"
    state_root = f"{xdg_state}/vhk/dossier/{command_name}"
    share_root = f"{state_root}/share-safe"
    return {
        "dossier_root": dossier_root,
        "dossier_manifest": f"{dossier_root}/vhk_host_dossier_handoff.json",
        "dossier_readme": f"{dossier_root}/README.md",
        "dossier_refresh_script": f"{dossier_root}/refresh_host_dossier_inputs.sh",
        "dossier_collect_script": f"{dossier_root}/collect_host_dossier.sh",
        "dossier_redact_script": f"{dossier_root}/redact_host_dossier.sh",
        "dossier_archive_script": f"{dossier_root}/archive_host_dossier.sh",
        "dossier_share_archive_script": f"{dossier_root}/archive_share_dossier.sh",
        "dossier_smoke_script": f"{dossier_root}/smoke_test_host_dossier.sh",
        "dossier_docs_root": f"{dossier_root}/docs",
        "state_root": state_root,
        "json": f"{state_root}/VHK_HOST_DOSSIER.json",
        "markdown": f"{state_root}/VHK_HOST_DOSSIER.md",
        "archive": f"{state_root}/VHK_HOST_DOSSIER.zip",
        "captures_root": f"{state_root}/captures",
        "app_home_capture": f"{state_root}/captures/app_home.json",
        "status_capture": f"{state_root}/captures/status.json",
        "docs_capture": f"{state_root}/captures/docs.tsv",
        "session_env_capture": f"{state_root}/captures/session_env.txt",
        "loginctl_capture": f"{state_root}/captures/loginctl_session.txt",
        "unit_path_capture": f"{state_root}/captures/systemd_unit_path.txt",
        "unit_show_capture": f"{state_root}/captures/systemd_units.txt",
        "journal_capture": f"{state_root}/captures/systemd_journal.txt",
        "rehearsal_report_capture": f"{state_root}/captures/rehearsal_report.json",
        "rehearsal_markdown_capture": f"{state_root}/captures/rehearsal_report.md",
        "notes_capture": f"{state_root}/captures/notes.txt",
        "share_root": share_root,
        "share_json": f"{share_root}/VHK_HOST_DOSSIER.share.json",
        "share_markdown": f"{share_root}/VHK_HOST_DOSSIER.share.md",
        "share_archive": f"{state_root}/VHK_HOST_DOSSIER.share.zip",
        "share_report": f"{share_root}/VHK_HOST_DOSSIER_REDACTION.json",
        "share_captures_root": f"{share_root}/captures",
    }


def _host_dossier_constraints(plan: dict[str, Any]) -> list[str]:
    project = dict(plan.get("project") or {})
    story = dict(plan.get("host_rehearsal_story") or {})
    constraints = [
        "Treat the host dossier as a support packet for one installed reviewed lane: it should collect launcher state, rehearsal output, and best-effort session/service probes without mutating the shipped bundle.",
        "Keep collection best-effort and additive: missing loginctl, unavailable per-user journals, or skipped systemctl checks should be reported as gaps in the dossier rather than treated as proof that the lane is healthy.",
        "Prefer state-root evidence over copy/pasted stdout so bug reports can be reviewed offline and attached to support threads without rerunning commands from memory.",
        "Preserve privacy review: launcher state, session variables, and journal excerpts may contain sensitive names, paths, or recent activity and should be scrubbed before external sharing.",
    ]
    if str(project.get("desktop_backend") or "").strip().lower() == "wayland":
        constraints.append("For Wayland-first projects, treat this dossier as evidence for one conservative installed lane only; it does not erase compositor policy, portal consent, or helper-daemon requirements outside that lane.")
    if str(story.get("service_mode") or "environment-only") == "environment-only":
        constraints.append("This project does not ship a first-party long-lived watcher unit, so the dossier will still capture launcher/session facts but may legitimately have no VHK-owned unit logs.")
    else:
        constraints.append("When the lane ships VHK-owned user units, collect both static unit metadata and recent journal excerpts so support can distinguish packaging drift from runtime failures.")
    return constraints


def build_host_dossier_plan(
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
    plan = build_host_rehearsal_plan(
        project_dir,
        bundle_target_profile=bundle_target_profile,
        app_id=app_id,
        runtime=runtime,
        runtime_version=runtime_version,
        sdk=sdk,
        python_cmd=python_cmd,
    )
    rehearse = dict(plan.get("host_rehearsal_story") or {})
    paths = _dossier_paths(plan)
    tools = [
        {"tool": "loginctl show-session", "purpose": "Capture the live desktop/session contract when logind is available so host triage can name the real session type instead of guessing from screenshots."},
        {"tool": "systemctl --user show", "purpose": "Record live unit visibility, search paths, and expected VHK-owned unit state when the lane ships user services."},
        {"tool": "journalctl --user", "purpose": "Attach recent user-unit logs when per-user journals are available instead of relying on ephemeral terminal output."},
        {"tool": "installed launcher --home-json / --status-json", "purpose": "Capture the installed lane's own packaged-doc and live-status view, not just project-root planner output."},
        {"tool": "redact_host_dossier.sh", "purpose": "Create a share-safe dossier copy with path, email, and secret-like token redaction plus a redaction report that flags suspicious leftovers for review."},
        {"tool": "archive_share_dossier.sh", "purpose": "Zip the redacted share-safe dossier after privacy review instead of sending the raw state-root capture."},
    ]
    story = {
        "headline": "Generate one installed-host dossier handoff that collects launcher state, rehearsal output, session facts, and best-effort systemd visibility into a shareable support packet for a reviewed lane.",
        "app_id": str(rehearse.get("app_id") or "io.visualhotkey.project"),
        "command_name": str(rehearse.get("command_name") or "vhk-project"),
        "bundle_name": str(rehearse.get("bundle_name") or "project.zip"),
        "bundle_kind": str(rehearse.get("bundle_kind") or "project"),
        "bundle_profile_id": str(rehearse.get("bundle_profile_id") or "").strip() or None,
        "desktop_backend": str(rehearse.get("desktop_backend") or "unknown"),
        "service_mode": str(rehearse.get("service_mode") or "environment-only"),
        "unit_base": str(rehearse.get("unit_base") or ""),
        "launcher_link": str(rehearse.get("launcher_link") or "${VHK_BIN_HOME:-$HOME/.local/bin}/vhk-project"),
        "report_json": str(rehearse.get("report_json") or ""),
        "report_markdown": str(rehearse.get("report_markdown") or ""),
        "dossier_root": paths["state_root"],
        "dossier_json": paths["json"],
        "dossier_markdown": paths["markdown"],
        "archive_path": paths["archive"],
        "share_safe_root": paths["share_root"],
        "share_safe_json": paths["share_json"],
        "share_safe_markdown": paths["share_markdown"],
        "share_safe_archive": paths["share_archive"],
        "share_safe_report": paths["share_report"],
        "capture_tools": tools,
        "constraints": _host_dossier_constraints(plan),
    }
    plan["host_dossier_paths"] = paths
    plan["host_dossier_story"] = story
    plan["host_dossier_commands"] = [
        "vhk gen-host-rehearsal-pack . --force",
        f"sh {paths['dossier_collect_script']}",
        f"sh {paths['dossier_redact_script']}",
        f"sh {paths['dossier_share_archive_script']}",
        f"sh {paths['dossier_archive_script']}",
        f"sh {paths['dossier_smoke_script']}",
    ]
    plan["host_dossier_summary"] = {
        "app_id": story["app_id"],
        "command_name": story["command_name"],
        "bundle_kind": story["bundle_kind"],
        "service_mode": story["service_mode"],
    }
    plan["source_contract"] = "host_dossier_pack"
    return plan


def render_host_dossier_doc(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    story = dict(plan.get("host_dossier_story") or {})
    paths = dict(plan.get("host_dossier_paths") or {})
    lines = [
        f"# VHK host dossier pack for {project.get('name') or 'project'}",
        "",
        "Generated by `vhk gen-host-dossier-pack`. Use it when one reviewed installed lane needs a shareable support packet: launcher state, live status, rehearsal output, session facts, and best-effort service visibility collected under XDG state instead of scattered terminal history.",
        "",
        "## Dossier posture",
        "",
        str(story.get("headline") or "Host dossier posture unavailable."),
        "",
        f"- Bundle kind: `{story.get('bundle_kind') or 'project'}`",
        f"- Command name: `{story.get('command_name') or 'vhk-project'}`",
        f"- Launcher link: `{story.get('launcher_link') or '${VHK_BIN_HOME:-$HOME/.local/bin}/vhk-project'}`",
        f"- Dossier root: `{paths.get('state_root') or '${XDG_STATE_HOME:-$HOME/.local/state}/vhk/dossier/vhk-project'}`",
        f"- Dossier JSON: `{paths.get('json') or ''}`",
        f"- Dossier archive: `{paths.get('archive') or ''}`",
        f"- Share-safe root: `{paths.get('share_root') or ''}`",
        f"- Share-safe archive: `{paths.get('share_archive') or ''}`",
        "",
        "## What gets captured",
        "",
    ]
    for tool in list(story.get("capture_tools") or []):
        if not isinstance(tool, dict):
            continue
        lines.append(f"- **{tool.get('tool') or 'tool'}** — {tool.get('purpose') or ''}".rstrip())
    lines.extend([
        "",
        "## Constraints",
        "",
    ])
    for item in list(story.get("constraints") or []):
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## Commands",
        "",
    ])
    for cmd in [str(x) for x in list(plan.get("host_dossier_commands") or []) if str(x)]:
        lines.append(f"- `{cmd}`")
    lines.append("")
    return "\n".join(lines)


def render_host_dossier_handoff_readme(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    story = dict(plan.get("host_dossier_story") or {})
    paths = dict(plan.get("host_dossier_paths") or {})
    return "\n".join(
        [
            f"# VHK host dossier handoff for {project.get('name') or 'project'}",
            "",
            "Generated by `vhk gen-host-dossier-pack`. This tree creates one shareable installed-host packet from the reviewed lane: collect launcher/home/status state, fold in the host rehearsal report, add best-effort session + systemd facts, then archive the result after privacy review.",
            "",
            f"- Bundle kind: `{story.get('bundle_kind') or 'project'}`",
            f"- Bundle name: `{story.get('bundle_name') or 'project.zip'}`",
            f"- Command name: `{story.get('command_name') or 'vhk-project'}`",
            f"- Service mode: `{story.get('service_mode') or 'environment-only'}`",
            "",
            "## Generated scripts",
            "",
            f"- Collect: `{paths.get('dossier_collect_script')}`",
            f"- Redact: `{paths.get('dossier_redact_script')}`",
            f"- Archive raw: `{paths.get('dossier_archive_script')}`",
            f"- Archive share-safe: `{paths.get('dossier_share_archive_script')}`",
            f"- Smoke: `{paths.get('dossier_smoke_script')}`",
            "",
            "## Flow",
            "",
            "1. Refresh the host-rehearsal inputs so the reviewed lane and its report path stay aligned.",
            "2. Install/rehearse the reviewed lane when needed.",
            "3. Run collect_host_dossier.sh to capture launcher + session + service facts under XDG state.",
            "4. Run redact_host_dossier.sh to generate a share-safe copy plus a redaction report that flags suspicious leftovers.",
            "5. Review the share-safe dossier and its redaction report for anything project-specific that should still be scrubbed.",
            "6. Run archive_share_dossier.sh for external handoff, or archive_host_dossier.sh only when raw evidence is explicitly needed.",
            "",
        ]
    )


def render_host_dossier_refresh_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("host_dossier_story") or {})
    profile = str(story.get("bundle_profile_id") or "").strip()
    lines = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        'SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"',
        'PROJECT_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/../../../.." && pwd)"',
        'cd "$PROJECT_DIR"',
        "",
        'printf "%s\\n" "Refreshing VHK host dossier pack inputs..."',
    ]
    rehearsal = 'vhk gen-host-rehearsal-pack . --force --quiet'
    dossier = 'vhk gen-host-dossier-pack . --force --quiet'
    if profile:
        rehearsal += f' --bundle-target-profile {profile}'
        dossier += f' --bundle-target-profile {profile}'
    for cmd in [rehearsal, dossier]:
        lines.append(f'printf "+ %s\\n" {cmd!r}')
        lines.append(f'sh -lc {cmd!r} || true')
    lines.extend([
        'printf "%s\\n" "Host dossier pack refresh complete."',
        "",
    ])
    return "\n".join(lines)


def _render_collect_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("host_dossier_story") or {})
    app_id = str(story.get("app_id") or "io.visualhotkey.project")
    command_name = str(story.get("command_name") or "vhk-project")
    service_mode = str(story.get("service_mode") or "environment-only")
    unit_base = str(story.get("unit_base") or "")
    units: list[str] = []
    if unit_base and service_mode != "environment-only":
        if service_mode == "socket-activated-busd":
            units.append(f"{unit_base}.socket")
        units.append(f"{unit_base}.service")
    unit_args = " ".join(units)
    script = '''#!/usr/bin/env sh
set -eu

XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
XDG_STATE_HOME="${XDG_STATE_HOME:-$HOME/.local/state}"
VHK_BIN_HOME="${VHK_BIN_HOME:-$HOME/.local/bin}"
DOSSIER_LINES="${VHK_DOSSIER_LINES:-120}"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PUBLISH_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
APP_ROOT="$XDG_DATA_HOME/vhk/apps/__COMMAND_NAME__"
LAUNCHER_LINK="$VHK_BIN_HOME/__COMMAND_NAME__"
DOSSIER_ROOT="$XDG_STATE_HOME/vhk/dossier/__COMMAND_NAME__"
DOSSIER_JSON="$DOSSIER_ROOT/VHK_HOST_DOSSIER.json"
DOSSIER_MD="$DOSSIER_ROOT/VHK_HOST_DOSSIER.md"
APP_HOME_CAPTURE="$DOSSIER_ROOT/captures/app_home.json"
STATUS_CAPTURE="$DOSSIER_ROOT/captures/status.json"
DOCS_CAPTURE="$DOSSIER_ROOT/captures/docs.tsv"
SESSION_ENV_CAPTURE="$DOSSIER_ROOT/captures/session_env.txt"
LOGINCTL_CAPTURE="$DOSSIER_ROOT/captures/loginctl_session.txt"
UNIT_PATH_CAPTURE="$DOSSIER_ROOT/captures/systemd_unit_path.txt"
UNIT_SHOW_CAPTURE="$DOSSIER_ROOT/captures/systemd_units.txt"
JOURNAL_CAPTURE="$DOSSIER_ROOT/captures/systemd_journal.txt"
REHEARSAL_CAPTURE="$DOSSIER_ROOT/captures/rehearsal_report.json"
REHEARSAL_CAPTURE_MD="$DOSSIER_ROOT/captures/rehearsal_report.md"
NOTES_CAPTURE="$DOSSIER_ROOT/captures/notes.txt"
REHEARSAL_ROOT="$XDG_STATE_HOME/vhk/rehearsal/__COMMAND_NAME__"
REHEARSAL_REPORT_JSON="$REHEARSAL_ROOT/VHK_HOST_REHEARSAL_REPORT.json"
REHEARSAL_REPORT_MD="$REHEARSAL_ROOT/VHK_HOST_REHEARSAL_REPORT.md"
JOURNAL_UNITS_RAW="__JOURNAL_UNITS__"
mkdir -p "$DOSSIER_ROOT/captures"
: > "$NOTES_CAPTURE"

{
  printf 'XDG_SESSION_ID=%s\n' "${XDG_SESSION_ID:-}"
  printf 'XDG_SESSION_TYPE=%s\n' "${XDG_SESSION_TYPE:-}"
  printf 'XDG_CURRENT_DESKTOP=%s\n' "${XDG_CURRENT_DESKTOP:-}"
  printf 'DESKTOP_SESSION=%s\n' "${DESKTOP_SESSION:-}"
  printf 'DISPLAY=%s\n' "${DISPLAY:-}"
  printf 'WAYLAND_DISPLAY=%s\n' "${WAYLAND_DISPLAY:-}"
  printf 'SWAYSOCK=%s\n' "${SWAYSOCK:-}"
  printf 'HYPRLAND_INSTANCE_SIGNATURE=%s\n' "${HYPRLAND_INSTANCE_SIGNATURE:-}"
} > "$SESSION_ENV_CAPTURE"

if [ -x "$LAUNCHER_LINK" ]; then
  "$LAUNCHER_LINK" --refresh-status-report >/dev/null 2>&1 || true
  "$LAUNCHER_LINK" --home-json > "$APP_HOME_CAPTURE" 2> "$APP_HOME_CAPTURE.stderr" || true
  "$LAUNCHER_LINK" --status-json > "$STATUS_CAPTURE" 2> "$STATUS_CAPTURE.stderr" || true
  "$LAUNCHER_LINK" --list-docs > "$DOCS_CAPTURE" 2> "$DOCS_CAPTURE.stderr" || true
else
  printf '%s\n' "launcher missing: $LAUNCHER_LINK" >> "$NOTES_CAPTURE"
fi

if [ -x "$PUBLISH_ROOT/rehearsal/report_reviewed_lane.sh" ]; then
  VHK_SKIP_SYSTEMCTL="${VHK_SKIP_SYSTEMCTL:-0}" sh "$PUBLISH_ROOT/rehearsal/report_reviewed_lane.sh" > "$DOSSIER_ROOT/captures/rehearsal.stdout" 2> "$DOSSIER_ROOT/captures/rehearsal.stderr" || true
fi
if [ -f "$REHEARSAL_REPORT_JSON" ]; then cp -f "$REHEARSAL_REPORT_JSON" "$REHEARSAL_CAPTURE"; fi
if [ -f "$REHEARSAL_REPORT_MD" ]; then cp -f "$REHEARSAL_REPORT_MD" "$REHEARSAL_CAPTURE_MD"; fi

if [ "${VHK_SKIP_LOGINCTL:-0}" != "1" ] && command -v loginctl >/dev/null 2>&1 && [ -n "${XDG_SESSION_ID:-}" ]; then
  loginctl show-session "$XDG_SESSION_ID" -p Id -p Name -p Type -p Class -p State -p Desktop -p Active -p Remote -p Display > "$LOGINCTL_CAPTURE" 2> "$LOGINCTL_CAPTURE.stderr" || true
else
  printf '%s\n' 'loginctl probe skipped' > "$LOGINCTL_CAPTURE"
fi

if [ "${VHK_SKIP_SYSTEMCTL:-0}" != "1" ] && command -v systemctl >/dev/null 2>&1; then
  systemctl --user show -p UnitPath --value > "$UNIT_PATH_CAPTURE" 2> "$UNIT_PATH_CAPTURE.stderr" || true
  if [ -n "$JOURNAL_UNITS_RAW" ]; then
    systemctl --user show -p LoadState -p ActiveState -p SubState -p UnitFileState -p FragmentPath $JOURNAL_UNITS_RAW > "$UNIT_SHOW_CAPTURE" 2> "$UNIT_SHOW_CAPTURE.stderr" || true
  else
    printf '%s\n' 'no VHK-owned user units declared for this lane' > "$UNIT_SHOW_CAPTURE"
  fi
else
  printf '%s\n' 'systemctl --user probe skipped' > "$UNIT_PATH_CAPTURE"
  printf '%s\n' 'systemctl --user probe skipped' > "$UNIT_SHOW_CAPTURE"
fi

if [ "${VHK_SKIP_SYSTEMCTL:-0}" != "1" ] && command -v journalctl >/dev/null 2>&1 && [ -n "$JOURNAL_UNITS_RAW" ]; then
  journalctl --user --no-pager -n "$DOSSIER_LINES" $(printf '%s' "$JOURNAL_UNITS_RAW" | sed 's/[^ ][^ ]*/-u &/g') > "$JOURNAL_CAPTURE" 2> "$JOURNAL_CAPTURE.stderr" || true
else
  printf '%s\n' 'journalctl --user probe skipped' > "$JOURNAL_CAPTURE"
fi

PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then PYTHON_BIN="$(command -v python3)"; elif command -v python >/dev/null 2>&1; then PYTHON_BIN="$(command -v python)"; fi
if [ -z "$PYTHON_BIN" ]; then
  printf '%s\n' 'python is required to assemble the host dossier summary' >&2
  exit 1
fi
"$PYTHON_BIN" - "$DOSSIER_JSON" "$DOSSIER_MD" "$APP_HOME_CAPTURE" "$STATUS_CAPTURE" "$DOCS_CAPTURE" "$SESSION_ENV_CAPTURE" "$LOGINCTL_CAPTURE" "$UNIT_PATH_CAPTURE" "$UNIT_SHOW_CAPTURE" "$JOURNAL_CAPTURE" "$REHEARSAL_CAPTURE" "$REHEARSAL_CAPTURE_MD" "$LAUNCHER_LINK" "$APP_ROOT" "$NOTES_CAPTURE" <<'PY'
import json
import sys
from pathlib import Path

def load_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None

def load_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text()
    except Exception:
        return ""

def parse_kv(text: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in text.splitlines():
        if '=' not in line:
            continue
        key, value = line.split('=', 1)
        data[key.strip()] = value.strip()
    return data

dossier_json = Path(sys.argv[1])
dossier_md = Path(sys.argv[2])
app_home_path = Path(sys.argv[3])
status_path = Path(sys.argv[4])
docs_path = Path(sys.argv[5])
session_env_path = Path(sys.argv[6])
loginctl_path = Path(sys.argv[7])
unit_path_path = Path(sys.argv[8])
unit_show_path = Path(sys.argv[9])
journal_path = Path(sys.argv[10])
rehearsal_path = Path(sys.argv[11])
rehearsal_md_path = Path(sys.argv[12])
launcher_link = sys.argv[13]
app_root = sys.argv[14]
notes_path = Path(sys.argv[15])
app_home = load_json(app_home_path) or {}
status = load_json(status_path) or {}
rehearsal = load_json(rehearsal_path) or {}
docs = []
for line in load_text(docs_path).splitlines():
    if not line.strip():
        continue
    parts = line.split('\t', 1)
    docs.append({'kind': parts[0], 'path': parts[1] if len(parts) > 1 else ''})
session_env = parse_kv(load_text(session_env_path))
loginctl = parse_kv(load_text(loginctl_path))
unit_show = load_text(unit_show_path)
units: list[dict[str, str]] = []
current: dict[str, str] = {}
for line in unit_show.splitlines():
    if not line.strip():
        if current:
            units.append(current)
            current = {}
        continue
    if '=' not in line:
        continue
    key, value = line.split('=', 1)
    current[key] = value
if current:
    units.append(current)
payload = {
    'launcher': {
        'link': launcher_link,
        'present': Path(launcher_link).exists(),
    },
    'app_root': app_root,
    'app_home': app_home,
    'status': status,
    'packaged_docs': docs,
    'session_env': session_env,
    'loginctl': loginctl,
    'systemd': {
        'unit_path': load_text(unit_path_path).strip(),
        'unit_show_text': unit_show,
        'units': units,
        'journal_excerpt_path': str(journal_path),
    },
    'rehearsal': rehearsal,
    'captures': {
        'app_home_json': str(app_home_path),
        'status_json': str(status_path),
        'docs_tsv': str(docs_path),
        'session_env': str(session_env_path),
        'loginctl': str(loginctl_path),
        'systemd_unit_path': str(unit_path_path),
        'systemd_units': str(unit_show_path),
        'systemd_journal': str(journal_path),
        'rehearsal_json': str(rehearsal_path),
        'rehearsal_markdown': str(rehearsal_md_path),
        'notes': str(notes_path),
    },
    'notes': load_text(notes_path).splitlines(),
}
dossier_json.parent.mkdir(parents=True, exist_ok=True)
dossier_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')
project_name = str(((app_home.get('project') or {}).get('name')) or ((status.get('app') or {}).get('name')) or 'project')
lines = [
    f"# VHK host dossier for {project_name}",
    '',
    f"- Launcher link: `{launcher_link}`",
    f"- App root: `{app_root}`",
    f"- Dossier JSON: `{dossier_json}`",
    f"- Rehearsal report captured: `{'yes' if rehearsal else 'no'}`",
    '',
    '## Session facts',
    '',
]
if session_env:
    for key, value in sorted(session_env.items()):
        lines.append(f"- `{key}` = `{value}`")
else:
    lines.append('- Session environment capture unavailable')
lines.extend(['', '## User-service visibility', ''])
if units:
    for row in units:
        summary = []
        for key in ['LoadState', 'ActiveState', 'SubState', 'UnitFileState']:
            value = row.get(key)
            if value:
                summary.append(f"{key}={value}")
        label = row.get('FragmentPath') or row.get('LoadState') or 'unit'
        lines.append(f"- `{label}` — {' '.join(summary)}")
else:
    lines.append('- No parsed user-unit state was captured for this lane.')
lines.extend(['', '## Packaged docs', ''])
if docs:
    for row in docs:
        lines.append(f"- `{row['kind']}` — `{row['path']}`")
else:
    lines.append('- No packaged doc inventory was captured from the launcher.')
lines.extend(['', '## Notes', ''])
notes = load_text(notes_path).splitlines()
if notes:
    for note in notes:
        lines.append(f'- {note}')
else:
    lines.append('- Review the JSON captures and journal excerpt before sharing externally.')
dossier_md.write_text('\n'.join(lines).rstrip() + '\n')
print(dossier_json)
PY
printf '%s\n' "$DOSSIER_JSON"
'''
    return (
        script.replace("__APP_ID__", app_id)
        .replace("__COMMAND_NAME__", command_name)
        .replace("__SERVICE_MODE__", service_mode)
        .replace("__JOURNAL_UNITS__", unit_args)
    )

def _render_redact_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("host_dossier_story") or {})
    command_name = str(story.get("command_name") or "vhk-project")
    script = r'''#!/usr/bin/env sh
set -eu

XDG_STATE_HOME="${XDG_STATE_HOME:-$HOME/.local/state}"
XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
VHK_BIN_HOME="${VHK_BIN_HOME:-$HOME/.local/bin}"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
DOSSIER_ROOT="$XDG_STATE_HOME/vhk/dossier/__COMMAND_NAME__"
SHARE_ROOT="$DOSSIER_ROOT/share-safe"
RAW_JSON="$DOSSIER_ROOT/VHK_HOST_DOSSIER.json"
RAW_MD="$DOSSIER_ROOT/VHK_HOST_DOSSIER.md"
SHARE_JSON="$SHARE_ROOT/VHK_HOST_DOSSIER.share.json"
SHARE_MD="$SHARE_ROOT/VHK_HOST_DOSSIER.share.md"
SHARE_REPORT="$SHARE_ROOT/VHK_HOST_DOSSIER_REDACTION.json"
mkdir -p "$SHARE_ROOT/captures"
sh "$SCRIPT_DIR/collect_host_dossier.sh" >/dev/null
PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then PYTHON_BIN="$(command -v python3)"; elif command -v python >/dev/null 2>&1; then PYTHON_BIN="$(command -v python)"; fi
if [ -z "$PYTHON_BIN" ]; then
  printf '%s\n' 'python is required to redact the host dossier' >&2
  exit 1
fi
"$PYTHON_BIN" - "$DOSSIER_ROOT" "$SHARE_ROOT" "$RAW_JSON" "$RAW_MD" "$SHARE_JSON" "$SHARE_MD" "$SHARE_REPORT" <<'PY'
import json
import os
import re
import sys
from pathlib import Path

raw_root = Path(sys.argv[1])
share_root = Path(sys.argv[2])
raw_json = Path(sys.argv[3])
raw_md = Path(sys.argv[4])
share_json = Path(sys.argv[5])
share_md = Path(sys.argv[6])
share_report = Path(sys.argv[7])
share_root.mkdir(parents=True, exist_ok=True)
(share_root / 'captures').mkdir(parents=True, exist_ok=True)

counts = {
    'path_replacements': 0,
    'email_replacements': 0,
    'secret_replacements': 0,
    'token_replacements': 0,
}

path_map = []
for name, placeholder in [
    ('HOME', '$HOME'),
    ('XDG_DATA_HOME', '$XDG_DATA_HOME'),
    ('XDG_CONFIG_HOME', '$XDG_CONFIG_HOME'),
    ('XDG_STATE_HOME', '$XDG_STATE_HOME'),
    ('VHK_BIN_HOME', '$VHK_BIN_HOME'),
]:
    value = os.environ.get(name, '').strip()
    if value:
        path_map.append((value, placeholder))
path_map.sort(key=lambda item: len(item[0]), reverse=True)

secret_line = re.compile(r'(?im)^([A-Za-z0-9_./-]*(?:SECRET|TOKEN|PASSWORD|PASSWD|API[_-]?KEY|ACCESS[_-]?KEY|AUTH(?:ORIZATION)?|COOKIE|PRIVATE[_-]?KEY)[A-Za-z0-9_./-]*=).+$')
secret_json = re.compile(r'(?i)("[^"\n]*(?:secret|token|password|passwd|api[_-]?key|access[_-]?key|auth(?:orization)?|cookie|private[_-]?key)[^"\n]*"\s*:\s*")([^"]*)(")')
email_re = re.compile(r'(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b')
bearer_re = re.compile(r'\bBearer\s+[A-Za-z0-9._~+/=-]{8,}\b')
provider_token_re = re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9]+|xox[baprs]-[A-Za-z0-9-]+|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{20,}|eyJ[A-Za-z0-9._-]{20,})\b')
private_key_re = re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----')
secret_scan = [
    ('provider_token', provider_token_re),
    ('bearer_token', re.compile(r'\bBearer\s+[A-Za-z0-9._~+/=-]{8,}\b')),
    ('private_key', private_key_re),
    ('secret_assignment', re.compile(r'(?i)(?:secret|token|password|passwd|api[_-]?key|access[_-]?key|auth(?:orization)?|cookie|private[_-]?key)\s*[:=]\s*\S+')),
]

def scrub(text: str) -> str:
    out = text
    for actual, placeholder in path_map:
        if actual and actual in out:
            counts['path_replacements'] += out.count(actual)
            out = out.replace(actual, placeholder)
    out, n = email_re.subn('[REDACTED_EMAIL]', out)
    counts['email_replacements'] += n
    out, n = secret_line.subn(r'\1[REDACTED_SECRET]', out)
    counts['secret_replacements'] += n
    out, n = secret_json.subn(r'\1[REDACTED_SECRET]\3', out)
    counts['secret_replacements'] += n
    out, n = bearer_re.subn('Bearer [REDACTED_TOKEN]', out)
    counts['token_replacements'] += n
    out, n = provider_token_re.subn('[REDACTED_TOKEN]', out)
    counts['token_replacements'] += n
    out, n = private_key_re.subn('-----BEGIN [REDACTED_PRIVATE_KEY]-----', out)
    counts['secret_replacements'] += n
    return out


def scrub_value(value):
    if isinstance(value, str):
        return scrub(value)
    if isinstance(value, list):
        return [scrub_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): scrub_value(item) for key, item in value.items()}
    return value


def load_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None

suspicious = []
for path in sorted(raw_root.rglob('*')):
    if path.is_dir() or share_root in path.parents or path == share_root:
        continue
    rel = path.relative_to(raw_root)
    target = share_root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        if path.suffix.lower() == '.json':
            data = load_json(path)
            if data is None:
                target.write_text(scrub(path.read_text()))
            else:
                target.write_text(json.dumps(scrub_value(data), indent=2, sort_keys=True) + '\n')
        else:
            target.write_text(scrub(path.read_text()))
    except UnicodeDecodeError:
        target.write_bytes(path.read_bytes())

if raw_json.exists():
    raw_payload = load_json(raw_json) or {}
    share_json.write_text(json.dumps(scrub_value(raw_payload), indent=2, sort_keys=True) + '\n')
if raw_md.exists():
    share_md.write_text(scrub(raw_md.read_text()))

scan_targets = [share_json, share_md] + sorted((share_root / 'captures').glob('*'))
for path in scan_targets:
    if not path.exists() or path.is_dir():
        continue
    try:
        text = path.read_text()
    except Exception:
        continue
    for label, pattern in secret_scan:
        match = pattern.search(text)
        if match:
            suspicious.append({
                'file': str(path.relative_to(share_root)),
                'pattern': label,
                'snippet': scrub(match.group(0))[:160],
            })

report = {
    'raw_root': str(raw_root),
    'share_root': str(share_root),
    'share_json': str(share_json),
    'share_markdown': str(share_md),
    'counts': counts,
    'suspicious_findings': suspicious,
    'review_required': bool(suspicious),
    'notes': [
        'The share-safe dossier replaces common home/XDG paths with placeholders and redacts email addresses, secret-like assignments, bearer tokens, and a small set of provider-token patterns.',
        'It cannot know every project-specific secret format, so review_required remains the final gate before external sharing.',
    ],
}
share_report.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(share_json)
PY
printf '%s\n' "$SHARE_JSON"
'''
    return script.replace("__COMMAND_NAME__", command_name)


def _render_share_archive_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("host_dossier_story") or {})
    command_name = str(story.get("command_name") or "vhk-project")
    script = r'''#!/usr/bin/env sh
set -eu

XDG_STATE_HOME="${XDG_STATE_HOME:-$HOME/.local/state}"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
DOSSIER_ROOT="$XDG_STATE_HOME/vhk/dossier/__COMMAND_NAME__"
SHARE_ROOT="$DOSSIER_ROOT/share-safe"
OUTPUT="${1:-$DOSSIER_ROOT/VHK_HOST_DOSSIER.share.zip}"
sh "$SCRIPT_DIR/redact_host_dossier.sh" >/dev/null
PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then PYTHON_BIN="$(command -v python3)"; elif command -v python >/dev/null 2>&1; then PYTHON_BIN="$(command -v python)"; fi
if [ -z "$PYTHON_BIN" ]; then
  printf '%s\n' 'python is required to archive the share-safe host dossier' >&2
  exit 1
fi
"$PYTHON_BIN" - "$SHARE_ROOT" "$OUTPUT" <<'PY'
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
root = Path(sys.argv[1])
out = Path(sys.argv[2])
out.parent.mkdir(parents=True, exist_ok=True)
with ZipFile(out, 'w', compression=ZIP_DEFLATED) as zf:
    for path in sorted(root.rglob('*')):
        if path.is_dir() or path.resolve() == out.resolve():
            continue
        zf.write(path, path.relative_to(root))
print(out)
PY
'''
    return script.replace("__COMMAND_NAME__", command_name)


def _render_archive_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("host_dossier_story") or {})
    command_name = str(story.get("command_name") or "vhk-project")
    return f'''#!/usr/bin/env sh
set -eu

XDG_STATE_HOME="${{XDG_STATE_HOME:-$HOME/.local/state}}"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
DOSSIER_ROOT="$XDG_STATE_HOME/vhk/dossier/{command_name}"
OUTPUT="${{1:-$DOSSIER_ROOT/VHK_HOST_DOSSIER.zip}}"
sh "$SCRIPT_DIR/collect_host_dossier.sh" >/dev/null
PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then PYTHON_BIN="$(command -v python3)"; elif command -v python >/dev/null 2>&1; then PYTHON_BIN="$(command -v python)"; fi
if [ -z "$PYTHON_BIN" ]; then
  printf '%s\n' 'python is required to archive the host dossier' >&2
  exit 1
fi
"$PYTHON_BIN" - "$DOSSIER_ROOT" "$OUTPUT" <<'PY'
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
root = Path(sys.argv[1])
out = Path(sys.argv[2])
out.parent.mkdir(parents=True, exist_ok=True)
with ZipFile(out, 'w', compression=ZIP_DEFLATED) as zf:
    for path in sorted(root.rglob('*')):
        if path.is_dir() or path.resolve() == out.resolve():
            continue
        zf.write(path, path.relative_to(root))
print(out)
PY
'''


def _render_smoke_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("host_dossier_story") or {})
    command_name = str(story.get("command_name") or "vhk-project")
    return f'''#!/usr/bin/env sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PUBLISH_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
SMOKE_ROOT="$(mktemp -d "${{TMPDIR:-/tmp}}/vhk-host-dossier-XXXXXX")"
cleanup() {{ rm -rf "$SMOKE_ROOT"; }}
trap cleanup EXIT INT TERM
mkdir -p "$SMOKE_ROOT/share" "$SMOKE_ROOT/config" "$SMOKE_ROOT/state" "$SMOKE_ROOT/bin"
XDG_DATA_HOME="$SMOKE_ROOT/share" XDG_CONFIG_HOME="$SMOKE_ROOT/config" XDG_STATE_HOME="$SMOKE_ROOT/state" VHK_BIN_HOME="$SMOKE_ROOT/bin" VHK_SKIP_SYSTEMCTL=1 sh "$PUBLISH_ROOT/rehearsal/install_reviewed_lane.sh"
XDG_DATA_HOME="$SMOKE_ROOT/share" XDG_CONFIG_HOME="$SMOKE_ROOT/config" XDG_STATE_HOME="$SMOKE_ROOT/state" VHK_BIN_HOME="$SMOKE_ROOT/bin" VHK_SKIP_SYSTEMCTL=1 VHK_SKIP_LOGINCTL=1 sh "$SCRIPT_DIR/collect_host_dossier.sh"
XDG_DATA_HOME="$SMOKE_ROOT/share" XDG_CONFIG_HOME="$SMOKE_ROOT/config" XDG_STATE_HOME="$SMOKE_ROOT/state" VHK_BIN_HOME="$SMOKE_ROOT/bin" VHK_SKIP_SYSTEMCTL=1 VHK_SKIP_LOGINCTL=1 sh "$SCRIPT_DIR/redact_host_dossier.sh"
XDG_DATA_HOME="$SMOKE_ROOT/share" XDG_CONFIG_HOME="$SMOKE_ROOT/config" XDG_STATE_HOME="$SMOKE_ROOT/state" VHK_BIN_HOME="$SMOKE_ROOT/bin" VHK_SKIP_SYSTEMCTL=1 VHK_SKIP_LOGINCTL=1 sh "$SCRIPT_DIR/archive_share_dossier.sh"
XDG_DATA_HOME="$SMOKE_ROOT/share" XDG_CONFIG_HOME="$SMOKE_ROOT/config" XDG_STATE_HOME="$SMOKE_ROOT/state" VHK_BIN_HOME="$SMOKE_ROOT/bin" VHK_SKIP_SYSTEMCTL=1 VHK_SKIP_LOGINCTL=1 sh "$SCRIPT_DIR/archive_host_dossier.sh"
test -f "$SMOKE_ROOT/state/vhk/dossier/{command_name}/VHK_HOST_DOSSIER.json"
test -f "$SMOKE_ROOT/state/vhk/dossier/{command_name}/VHK_HOST_DOSSIER.md"
test -f "$SMOKE_ROOT/state/vhk/dossier/{command_name}/share-safe/VHK_HOST_DOSSIER.share.json"
test -f "$SMOKE_ROOT/state/vhk/dossier/{command_name}/share-safe/VHK_HOST_DOSSIER_REDACTION.json"
test -f "$SMOKE_ROOT/state/vhk/dossier/{command_name}/VHK_HOST_DOSSIER.share.zip"
test -f "$SMOKE_ROOT/state/vhk/dossier/{command_name}/VHK_HOST_DOSSIER.zip"
test -x "$SMOKE_ROOT/bin/{command_name}"
XDG_DATA_HOME="$SMOKE_ROOT/share" XDG_CONFIG_HOME="$SMOKE_ROOT/config" XDG_STATE_HOME="$SMOKE_ROOT/state" VHK_BIN_HOME="$SMOKE_ROOT/bin" VHK_SKIP_SYSTEMCTL=1 sh "$PUBLISH_ROOT/rehearsal/uninstall_reviewed_lane.sh" >/dev/null 2>&1 || true
printf '%s\n' "Host dossier smoke test passed: $SMOKE_ROOT"
'''


def write_host_dossier_pack(
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
    force: bool,
    dossier_doc: bool = True,
    plan_json: bool = True,
    script: bool = True,
) -> dict[str, Path]:
    project_dir = project_dir.expanduser().resolve()
    write_host_rehearsal_pack(
        project_dir,
        bundle_target_profile=bundle_target_profile,
        app_id=app_id,
        runtime=runtime,
        runtime_version=runtime_version,
        sdk=sdk,
        python_cmd=python_cmd,
        force=force,
        rehearsal_doc=True,
        plan_json=True,
        script=True,
    )
    plan = build_host_dossier_plan(
        project_dir,
        bundle_target_profile=bundle_target_profile,
        app_id=app_id,
        runtime=runtime,
        runtime_version=runtime_version,
        sdk=sdk,
        python_cmd=python_cmd,
    )
    docs_dir = (out_dir.expanduser().resolve() if out_dir else project_dir / "docs")
    scripts_dir = (script_dir.expanduser().resolve() if script_dir else project_dir / "scripts")
    paths = dict(plan.get("host_dossier_paths") or {})
    root = project_dir / str(paths.get("dossier_root") or "build/publish/project/dossier")

    doc_path = docs_dir / "VHK_HOST_DOSSIER.md"
    plan_path = docs_dir / "VHK_HOST_DOSSIER_PLAN.json"
    script_path = scripts_dir / "vhk_refresh_host_dossier_pack.sh"
    collect_path = root / "collect_host_dossier.sh"
    redact_path = root / "redact_host_dossier.sh"
    archive_path = root / "archive_host_dossier.sh"
    share_archive_path = root / "archive_share_dossier.sh"
    smoke_path = root / "smoke_test_host_dossier.sh"
    readme_path = root / "README.md"
    manifest_path = root / "vhk_host_dossier_handoff.json"
    refresh_path = root / "refresh_host_dossier_inputs.sh"
    docs_root = root / "docs"

    written: dict[str, Path] = {}
    if dossier_doc:
        _write_if_allowed(doc_path, render_host_dossier_doc(plan), force=force)
        written["dossier_doc"] = doc_path
    if plan_json:
        _write_if_allowed(plan_path, json.dumps(plan, indent=2, sort_keys=True) + "\n", force=force)
        written["plan_json"] = plan_path
    if script:
        _write_if_allowed(script_path, render_host_dossier_refresh_script(plan), force=force)
        script_path.chmod(0o755)
        written["script"] = script_path

    _write_if_allowed(readme_path, render_host_dossier_handoff_readme(plan), force=force)
    _write_if_allowed(manifest_path, json.dumps(dict(plan.get("host_dossier_story") or {}), indent=2, sort_keys=True) + "\n", force=force)
    _write_if_allowed(refresh_path, render_host_dossier_refresh_script(plan), force=force)
    _write_if_allowed(collect_path, _render_collect_script(plan), force=force)
    _write_if_allowed(redact_path, _render_redact_script(plan), force=force)
    _write_if_allowed(archive_path, _render_archive_script(plan), force=force)
    _write_if_allowed(share_archive_path, _render_share_archive_script(plan), force=force)
    _write_if_allowed(smoke_path, _render_smoke_script(plan), force=force)
    for path in [refresh_path, collect_path, redact_path, archive_path, share_archive_path, smoke_path]:
        path.chmod(0o755)

    for src_name in [
        "VHK_HOST_REHEARSAL.md",
        "VHK_NATIVE_INSTALL.md",
        "VHK_SERVICE_COMPOSE.md",
        "VHK_CAPABILITY_AUDIT.md",
        "VHK_PUBLIC_SUPPORT.md",
    ]:
        src = project_dir / "docs" / src_name
        if src.exists():
            _copy_if_present(src, docs_root / src_name)

    written.update(
        {
            "dossier_root": root,
            "dossier_collect_script": collect_path,
            "dossier_redact_script": redact_path,
            "dossier_archive_script": archive_path,
            "dossier_share_archive_script": share_archive_path,
            "dossier_smoke_script": smoke_path,
        }
    )
    return written
