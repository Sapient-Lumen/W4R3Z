from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from vhk.project.loader import load_project
from vhk.project.strategy import summarize_project_strategy


def _write_if_allowed(path: Path, content: bytes | str, *, force: bool) -> None:
    if path.exists() and not force:
        raise ValueError(f"Refusing to overwrite existing file: {path}. Use --force.")
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content)


def _trim_items(items: list[dict[str, Any]] | None, limit: int = 5) -> list[dict[str, Any]]:
    return [dict(item) for item in list(items or [])[:limit] if isinstance(item, dict)]


def _first_text(item: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def build_support_plan(
    project_dir: Path,
    *,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
) -> dict[str, Any]:
    """Load a VHK project and emit a planner-backed support/triage payload."""

    project = load_project(project_dir)
    plan = summarize_project_strategy(
        project,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
    )

    log_dir = str(project.settings.log_dir or "logs")
    support_artifacts = [
        {
            "id": "doctor-report",
            "title": "Doctor capability snapshot",
            "path_hint": "reports/doctor.json",
            "summary": "Capture the current session/backend/helper capability facts before debugging anything else.",
            "producer_commands": ["vhk doctor --json"],
            "attach_when": ["always"],
        },
        {
            "id": "validate-report",
            "title": "Validation report",
            "path_hint": "reports/validate.json",
            "summary": "Show structural project issues separately from desktop/session capability problems.",
            "producer_commands": ["vhk validate . --json"],
            "attach_when": ["always"],
        },
        {
            "id": "project-strategy",
            "title": "Strategy snapshot",
            "path_hint": "reports/plan-project.json",
            "summary": "Preserve the planner's view of deployable surfaces, setup recipes, and release gates for the failing project state.",
            "producer_commands": ["vhk plan-project . --json"],
            "attach_when": ["always"],
        },
        {
            "id": "latest-run-report",
            "title": "Latest run summary",
            "path_hint": "reports/latest_report.json",
            "summary": "Summarize the most recent event log so triage starts from slow waits, retries, and failing steps instead of raw JSONL only.",
            "producer_commands": ["vhk report --project . --latest --json"],
            "attach_when": ["when event logs exist"],
        },
        {
            "id": "latest-run-trace",
            "title": "Latest run trace",
            "path_hint": "reports/latest.trace.json",
            "summary": "Export the latest run into a trace-viewer-friendly format so support can inspect timing and sequencing offline.",
            "producer_commands": ["vhk trace --project . --latest --out ./support/latest.trace.json"],
            "attach_when": ["when event logs exist"],
        },
        {
            "id": "recent-log-artifacts",
            "title": "Recent event/error artifacts",
            "path_hint": f"logs/ (copied from {log_dir}/)",
            "summary": "Collect recent run logs, watcher logs, screenshots, JSON failure contexts, and diff images from the project's log directory.",
            "producer_commands": ["copy recent files from project logs"],
            "attach_when": ["when logs or screenshots exist"],
        },
        {
            "id": "generated-handoff-docs",
            "title": "Deployment and verification packs",
            "path_hint": "docs/",
            "summary": "Regenerate operator and verification artifacts so the bug report includes the install/release expectations for this project revision.",
            "producer_commands": ["vhk gen-operator-pack . --force", "vhk gen-verification-pack . --force"],
            "attach_when": ["recommended"],
        },
        {
            "id": "capability-audit-pack",
            "title": "Capability audit and fallback pack",
            "path_hint": "docs/VHK_CAPABILITY_AUDIT.md",
            "summary": "Capture the current desktop/session/helper boundary story so triage can distinguish packaging bugs from real Linux capability limits.",
            "producer_commands": ["vhk gen-capability-audit-pack . --force"],
            "attach_when": ["recommended for cross-session or Wayland issues"],
        },
        {
            "id": "installed-host-dossier-pack",
            "title": "Installed host dossier pack",
            "path_hint": "build/publish/<bundle>/dossier/ and ${XDG_STATE_HOME}/vhk/dossier/<command>/",
            "summary": "Collect one installed-host dossier when the bug lives in native install, service composition, launcher discoverability, or user-session drift instead of pure project logic.",
            "producer_commands": ["vhk gen-host-dossier-pack . --force", "sh build/publish/<bundle>/dossier/collect_host_dossier.sh", "sh build/publish/<bundle>/dossier/redact_host_dossier.sh", "sh build/publish/<bundle>/dossier/archive_share_dossier.sh"],
            "attach_when": ["recommended for install/service/desktop-shell issues"],
        },
        {
            "id": "deterministic-project-bundle",
            "title": "Optional reproducible project bundle",
            "path_hint": "project_bundle.zip",
            "summary": "Capture a deterministic project archive when maintainers need to reproduce the exact macros/assets/configs offline.",
            "producer_commands": ["vhk bundle . ./support/project_bundle.zip --deterministic", "vhk verify-bundle ./support/project_bundle.zip"],
            "attach_when": ["only after privacy review / opt-in"],
        },
    ]
    privacy_review = [
        "Event logs, prompt answers, and clipboard-related artifacts may contain typed text or copied content; review them before sharing outside your team.",
        "Failure screenshots, diff PNGs, and visual baselines may expose app content, personal data, or secrets on screen; scrub or remove them when needed.",
        "Installed host dossiers may include home/XDG paths, session identifiers, and user-service logs; prefer the share-safe dossier archive and still review its redaction report before external sharing.",
        "A full project bundle may include macros, assets, prompt defaults, and environment-specific paths; only attach it when the recipient truly needs reproducibility.",
    ]
    support_commands = [
        "vhk doctor --json",
        "vhk validate . --json",
        "vhk plan-project . --json",
        "vhk gen-operator-pack . --force",
        "vhk gen-verification-pack . --force",
        "vhk gen-capability-audit-pack . --force",
        "vhk gen-host-dossier-pack . --force",
        "sh build/publish/<bundle>/dossier/redact_host_dossier.sh",
        "sh build/publish/<bundle>/dossier/archive_share_dossier.sh",
        "vhk report --project . --latest --json",
        "vhk trace --project . --latest --out ./support/latest.trace.json",
    ]

    plan["support_paths"] = {
        "project_root": str(Path(project.root_dir)),
        "log_dir": log_dir,
        "docs_dir": "docs",
        "scripts_dir": "scripts",
        "support_dir": "support",
    }
    plan["support_artifacts"] = support_artifacts
    plan["privacy_review"] = privacy_review
    plan["support_commands"] = support_commands
    return plan



def render_support_guide(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    overview = dict(plan.get("overview") or {})
    deployable_surfaces = _trim_items(plan.get("deployable_surfaces"), limit=6)
    verification_gates = _trim_items(plan.get("verification_gates"), limit=6)
    support_artifacts = _trim_items(plan.get("support_artifacts"), limit=8)
    support_paths = dict(plan.get("support_paths") or {})
    session_capabilities = dict(plan.get("session_capabilities") or {})
    session_issues = list(plan.get("session_issues") or [])
    privacy_review = [str(item).strip() for item in list(plan.get("privacy_review") or []) if str(item).strip()]
    support_commands = [str(item).strip() for item in list(plan.get("support_commands") or []) if str(item).strip()]

    lines: list[str] = []
    lines.append(f"# VHK support guide for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-support-pack`. Use it when a project works on one Linux session, fails on another, or needs a reproducible bug report.")
    if session_capabilities:
        lines.append("This guide is session-aware: it includes the current capability matrix so triage starts from a real desktop instead of a hypothetical target.")
    else:
        lines.append("This guide is capability-agnostic: rerun it with session checks on the failing machine so the support pack matches the real desktop state.")
    lines.append("")

    lines.append("## Project snapshot")
    lines.append("")
    lines.append(f"- Root: `{project.get('root_dir') or '.'}`")
    lines.append(f"- Desktop backend: `{project.get('desktop_backend') or 'unknown'}`")
    lines.append(f"- Macros: {overview.get('macros', 0)}")
    lines.append(f"- Bindings: {overview.get('bindings', 0)}")
    lines.append(f"- Hotstrings: {overview.get('hotstrings', 0)}")
    lines.append(f"- Clipboard watchers: {overview.get('clipboard_watchers', 0)}")
    lines.append(f"- Bus watchers: {overview.get('bus_watchers', 0)}")
    lines.append(f"- Window watchers: {overview.get('window_watchers', 0)}")
    if support_paths:
        lines.append(f"- Log dir: `{support_paths.get('log_dir') or 'logs'}`")
        lines.append(f"- Generated support dir: `{support_paths.get('support_dir') or 'support'}`")
    lines.append("")

    lines.append("## Triage loop")
    lines.append("")
    lines.append("1. Capture current desktop facts with `vhk doctor --json`.")
    lines.append("2. Capture project facts with `vhk validate . --json` and `vhk plan-project . --json`.")
    lines.append("3. If event logs exist, export the latest run summary and trace so timing/failure sequencing survives outside the original machine.")
    lines.append("4. Attach operator/release artifacts so the bug report includes install expectations, rollback paths, and release gates.")
    lines.append("5. Review privacy-sensitive evidence before sharing anything externally.")
    lines.append("")

    if support_artifacts:
        lines.append("## Evidence to attach")
        lines.append("")
        for item in support_artifacts:
            title = item.get("title") or item.get("id") or "artifact"
            lines.append(f"### {title}")
            summary = _first_text(item, "summary", "why", "description", "notes")
            if summary:
                lines.append(summary)
            path_hint = str(item.get("path_hint") or "").strip()
            if path_hint:
                lines.append("")
                lines.append(f"Expected path: `{path_hint}`")
            attach_when = list(item.get("attach_when") or [])
            if attach_when:
                lines.append("")
                lines.append(f"Attach when: {', '.join(str(x) for x in attach_when[:4])}")
            producer_commands = list(item.get("producer_commands") or [])
            if producer_commands:
                lines.append("")
                lines.append("Producer commands:")
                for cmd in producer_commands[:4]:
                    lines.append(f"- `{cmd}`")
            lines.append("")

    if deployable_surfaces:
        lines.append("## Surfaces worth naming in the bug report")
        lines.append("")
        for item in deployable_surfaces:
            title = item.get("title") or item.get("id") or "surface"
            summary = _first_text(item, "summary", "why", "description", "notes")
            if summary:
                lines.append(f"- **{title}** — {summary}")
            else:
                lines.append(f"- **{title}**")
        lines.append("")

    if verification_gates:
        lines.append("## Claims to test while reproducing")
        lines.append("")
        for item in verification_gates:
            title = item.get("title") or item.get("id") or "gate"
            summary = _first_text(item, "summary", "why", "description", "notes")
            if summary:
                lines.append(f"- **{title}** — {summary}")
            else:
                lines.append(f"- **{title}**")
        lines.append("")

    if session_capabilities:
        lines.append("## Current session fit")
        lines.append("")
        for capability in [
            "screen_capture",
            "text_injection",
            "pointer_injection",
            "global_hotkeys",
            "window_introspection",
            "input_capture",
        ]:
            item = session_capabilities.get(capability)
            if not isinstance(item, dict):
                continue
            status = str(item.get("status") or "unknown")
            recommended = str(item.get("recommended") or "")
            mechanisms = ", ".join(str(x) for x in (item.get("mechanisms") or [])[:4])
            lines.append(f"- **{capability}** — `{status}`; recommended: `{recommended or 'n/a'}`; mechanisms: {mechanisms or 'n/a'}")
        lines.append("")

    if session_issues:
        lines.append("## Current session warnings")
        lines.append("")
        for item in session_issues[:8]:
            message = _first_text(item, "message", "summary", "why", "description")
            suggestion = _first_text(item, "suggestion", "response", "notes")
            if suggestion:
                lines.append(f"- **{message}** — {suggestion}")
            else:
                lines.append(f"- **{message}**")
        lines.append("")

    if privacy_review:
        lines.append("## Privacy review before sharing")
        lines.append("")
        for item in privacy_review:
            lines.append(f"- {item}")
        lines.append("")

    if support_commands:
        lines.append("## Suggested capture commands")
        lines.append("")
        lines.append("```bash")
        for cmd in support_commands:
            lines.append(cmd)
        lines.append("sh scripts/vhk_capture_support.sh")
        lines.append("```")
        lines.append("")

    return "\n".join(line.rstrip() for line in lines).rstrip() + "\n"



def render_support_checklist(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    support_artifacts = _trim_items(plan.get("support_artifacts"), limit=8)
    privacy_review = [str(item).strip() for item in list(plan.get("privacy_review") or []) if str(item).strip()]
    session_issues = list(plan.get("session_issues") or [])

    lines: list[str] = []
    lines.append(f"# VHK support checklist for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-support-pack`. Use this when collecting a bug report, cross-session repro bundle, or maintainer handoff.")
    lines.append("")
    lines.append("## Baseline refresh")
    lines.append("")
    lines.append("- [ ] Reproduce the issue once with event logging enabled if possible.")
    lines.append("- [ ] Run `vhk doctor --json` on the failing session.")
    lines.append("- [ ] Run `vhk validate . --json` in the project root.")
    lines.append("- [ ] Run `vhk plan-project . --json` and note which surfaces/gates appear relevant to the failure.")
    lines.append("- [ ] Regenerate `docs/VHK_SUPPORT_PLAN.json` and `scripts/vhk_capture_support.sh`.")
    if session_issues:
        lines.append(f"- [ ] Review {min(len(session_issues), 8)} session issue(s) captured in `docs/VHK_SUPPORT_PLAN.json`.")
    lines.append("")

    if support_artifacts:
        lines.append("## Evidence to collect")
        lines.append("")
        for item in support_artifacts:
            title = item.get("title") or item.get("id") or "artifact"
            summary = _first_text(item, "summary", "why", "description", "notes")
            if summary:
                lines.append(f"- [ ] {title} — {summary}")
            else:
                lines.append(f"- [ ] {title}")
        lines.append("")

    if privacy_review:
        lines.append("## Privacy review")
        lines.append("")
        for item in privacy_review:
            lines.append(f"- [ ] {item}")
        lines.append("")

    lines.append("## Handoff")
    lines.append("")
    lines.append("- [ ] Mention the failing desktop/session (X11, GNOME Wayland, KDE Wayland, sway/wlroots, Hyprland, etc.).")
    lines.append("- [ ] Mention whether the failure is in capture, hotkeys, text injection, pointer injection, window scoping, or deployment/install.")
    lines.append("- [ ] Attach `support/` output from `scripts/vhk_capture_support.sh` or explain why some artifacts were intentionally omitted.")
    lines.append("")

    return "\n".join(line.rstrip() for line in lines).rstrip() + "\n"



def render_capture_script(plan: dict[str, Any]) -> str:
    support_paths = dict(plan.get("support_paths") or {})
    log_dir = str(support_paths.get("log_dir") or "logs")

    lines: list[str] = []
    lines.append("#!/usr/bin/env sh")
    lines.append("set -eu")
    lines.append("")
    lines.append('DEST_ROOT="${1:-./support}"')
    lines.append('STAMP="$(date +%Y%m%d_%H%M%S 2>/dev/null || printf unknown)"')
    lines.append('DEST="$DEST_ROOT/capture_$STAMP"')
    lines.append('MAX_LOG_FILES="${SUPPORT_MAX_LOG_FILES:-8}"')
    lines.append('INCLUDE_PROJECT_BUNDLE="${SUPPORT_INCLUDE_PROJECT_BUNDLE:-0}"')
    lines.append("")
    lines.append('mkdir -p "$DEST/reports" "$DEST/logs" "$DEST/docs" "$DEST/scripts" "$DEST/meta"')
    lines.append("")
    lines.append('run_json() {')
    lines.append('  label="$1"')
    lines.append('  shift')
    lines.append('  echo "> $label"')
    lines.append('  if "$@" > "$DEST/reports/$label" 2> "$DEST/reports/$label.stderr"; then')
    lines.append('    :')
    lines.append('  else')
    lines.append('    echo "command failed: $*" >> "$DEST/reports/FAILURES.txt"')
    lines.append('  fi')
    lines.append('}')
    lines.append("")
    lines.append('copy_recent() {')
    lines.append('  pattern="$1"')
    lines.append('  limit="$2"')
    lines.append('  if [ ! -d "' + log_dir.replace('"', '\\"') + '" ]; then')
    lines.append('    return 0')
    lines.append('  fi')
    lines.append("  find \"" + log_dir.replace('"', '\\"') + "\" -maxdepth 1 -type f -name \"$pattern\" -printf '%T@ %p\\n' 2>/dev/null | sort -nr | head -n \"$limit\" | cut -d' ' -f2- | while IFS= read -r src; do")
    lines.append('    [ -n "$src" ] || continue')
    lines.append('    cp -f "$src" "$DEST/logs/$(basename "$src")"')
    lines.append('  done')
    lines.append('}')
    lines.append("")
    lines.append('echo "[1/5] Capturing environment metadata"')
    lines.append('{')
    lines.append('  printf "pwd=%s\\n" "$PWD"')
    lines.append('  printf "uname="; uname -a 2>/dev/null || true')
    lines.append('  printf "desktop_backend=%s\\n" "${XDG_SESSION_TYPE:-unknown}"')
    lines.append('  printf "XDG_CURRENT_DESKTOP=%s\\n" "${XDG_CURRENT_DESKTOP:-}"')
    lines.append('  printf "DESKTOP_SESSION=%s\\n" "${DESKTOP_SESSION:-}"')
    lines.append('  printf "DISPLAY=%s\\n" "${DISPLAY:-}"')
    lines.append('  printf "WAYLAND_DISPLAY=%s\\n" "${WAYLAND_DISPLAY:-}"')
    lines.append('  printf "SWAYSOCK=%s\\n" "${SWAYSOCK:-}"')
    lines.append('  printf "HYPRLAND_INSTANCE_SIGNATURE=%s\\n" "${HYPRLAND_INSTANCE_SIGNATURE:-}"')
    lines.append('} > "$DEST/meta/session_env.txt"')
    lines.append("")
    lines.append('echo "[2/5] Capturing core JSON reports"')
    lines.append('run_json doctor.json vhk doctor --json')
    lines.append('run_json validate.json vhk validate . --json')
    lines.append('run_json plan-project.json vhk plan-project . --json')
    lines.append("")
    lines.append('echo "[3/5] Regenerating planner-backed handoff docs"')
    lines.append('if vhk gen-operator-pack . --out-dir "$DEST/docs" --force --quiet --no-session-check; then :; else echo "gen-operator-pack failed" >> "$DEST/reports/FAILURES.txt"; fi')
    lines.append('if vhk gen-verification-pack . --out-dir "$DEST/docs" --script-dir "$DEST/scripts" --force --quiet --no-session-check; then :; else echo "gen-verification-pack failed" >> "$DEST/reports/FAILURES.txt"; fi')
    lines.append('if vhk gen-support-pack . --out-dir "$DEST/docs" --script-dir "$DEST/scripts" --force --quiet --no-session-check; then :; else echo "gen-support-pack failed" >> "$DEST/reports/FAILURES.txt"; fi')
    lines.append('if vhk gen-capability-audit-pack . --out-dir "$DEST/docs" --script-dir "$DEST/scripts" --build-root "$DEST/build/capability-audit" --force --quiet --no-audit-check; then :; else echo "gen-capability-audit-pack failed" >> "$DEST/reports/FAILURES.txt"; fi')
    lines.append("")
    lines.append('echo "[4/5] Capturing recent logs and traces"')
    lines.append('copy_recent "run_*.jsonl" "$MAX_LOG_FILES"')
    lines.append('copy_recent "clipboard_watcher_*.jsonl" "$MAX_LOG_FILES"')
    lines.append('copy_recent "bus_watcher_*.jsonl" "$MAX_LOG_FILES"')
    lines.append('copy_recent "window_watcher_*.jsonl" "$MAX_LOG_FILES"')
    lines.append('copy_recent "error_*.json" "$MAX_LOG_FILES"')
    lines.append('copy_recent "error_*.png" "$MAX_LOG_FILES"')
    lines.append('copy_recent "*.diff.png" "$MAX_LOG_FILES"')
    lines.append('if vhk report --project . --latest --json > "$DEST/reports/latest_report.json" 2> "$DEST/reports/latest_report.stderr"; then :; else echo "latest report unavailable" >> "$DEST/reports/FAILURES.txt"; fi')
    lines.append('if vhk trace --project . --latest --out "$DEST/reports/latest.trace.json" > "$DEST/reports/latest_trace.stdout" 2> "$DEST/reports/latest_trace.stderr"; then :; else echo "latest trace unavailable" >> "$DEST/reports/FAILURES.txt"; fi')
    lines.append("")
    lines.append('echo "[5/5] Optional deterministic project bundle"')
    lines.append('if [ "$INCLUDE_PROJECT_BUNDLE" = "1" ]; then')
    lines.append('  if vhk bundle . "$DEST/project_bundle.zip" --deterministic > "$DEST/reports/bundle.stdout" 2> "$DEST/reports/bundle.stderr"; then')
    lines.append('    vhk verify-bundle "$DEST/project_bundle.zip" > "$DEST/reports/bundle_verify.txt" 2>&1 || true')
    lines.append('  else')
    lines.append('    echo "project bundle generation failed" >> "$DEST/reports/FAILURES.txt"')
    lines.append('  fi')
    lines.append('else')
    lines.append('  echo "Skipped project bundle (set SUPPORT_INCLUDE_PROJECT_BUNDLE=1 to include it)." > "$DEST/reports/bundle_skip.txt"')
    lines.append('fi')
    lines.append("")
    lines.append('cat > "$DEST/README.txt" <<EOF')
    lines.append('VHK support capture complete.')
    lines.append('')
    lines.append('Review privacy-sensitive files before sharing: screenshots, diff images, event logs, and optional project bundles may contain secrets or personal data.')
    lines.append('')
    lines.append('Key files:')
    lines.append('- reports/doctor.json')
    lines.append('- reports/validate.json')
    lines.append('- reports/plan-project.json')
    lines.append('- reports/latest_report.json (if logs existed)')
    lines.append('- reports/latest.trace.json (if logs existed)')
    lines.append('- docs/VHK_OPERATOR_PLAN.json')
    lines.append('- docs/VHK_VERIFICATION_PLAN.json')
    lines.append('- docs/VHK_SUPPORT_PLAN.json')
    lines.append('- logs/')
    lines.append('EOF')
    lines.append("")
    lines.append('echo "Support capture complete: $DEST"')
    lines.append("")
    return "\n".join(lines)



def write_support_pack(
    project_dir: Path,
    *,
    out_dir: Path | None = None,
    script_dir: Path | None = None,
    force: bool,
    guide: bool = True,
    checklist: bool = True,
    plan_json: bool = True,
    script: bool = True,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
) -> dict[str, Path]:
    """Write planner-backed support/triage artifacts for an existing project."""

    out_dir = (out_dir or (project_dir / "docs")).expanduser().resolve()
    script_dir = (script_dir or (project_dir / "scripts")).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    script_dir.mkdir(parents=True, exist_ok=True)

    plan = build_support_plan(
        project_dir,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
    )

    written: dict[str, Path] = {}
    if plan_json:
        path = out_dir / "VHK_SUPPORT_PLAN.json"
        _write_if_allowed(path, json.dumps(plan, ensure_ascii=False, indent=2) + "\n", force=force)
        written["plan_json"] = path
    if guide:
        path = out_dir / "VHK_SUPPORT_GUIDE.md"
        _write_if_allowed(path, render_support_guide(plan), force=force)
        written["guide"] = path
    if checklist:
        path = out_dir / "VHK_SUPPORT_CHECKLIST.md"
        _write_if_allowed(path, render_support_checklist(plan), force=force)
        written["checklist"] = path
    if script:
        path = script_dir / "vhk_capture_support.sh"
        _write_if_allowed(path, render_capture_script(plan), force=force)
        try:
            path.chmod(0o755)
        except Exception:
            pass
        written["script"] = path
    return written
