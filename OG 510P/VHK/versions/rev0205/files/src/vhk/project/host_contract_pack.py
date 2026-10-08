from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from vhk.project.loader import load_project
from vhk.project.setup_pack import _build_toolchain_package_plan
from vhk.project.strategy import summarize_project_strategy


def _write_if_allowed(path: Path, content: bytes | str, *, force: bool) -> None:
    if path.exists() and not force:
        raise ValueError(f"Refusing to overwrite existing file: {path}. Use --force.")
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


def _trim_items(items: list[dict[str, Any]] | None, limit: int = 8) -> list[dict[str, Any]]:
    return [dict(item) for item in list(items or [])[:limit] if isinstance(item, dict)]


def _dedupe_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in values:
        text = str(item or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _first_text(item: Mapping[str, Any], *keys: str) -> str:
    for key in keys:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _status_rank(value: str) -> int:
    return {"blocked": 0, "degraded": 1, "unknown": 2, "ready": 3}.get(str(value or "unknown"), 2)


def _priority_rank(value: str) -> int:
    return {"required": 0, "recommended": 1, "conditional": 2}.get(str(value or "conditional"), 2)


def _track_status(value: str | None) -> str:
    lowered = str(value or "unknown").strip().lower()
    if lowered == "ok":
        return "ready"
    if lowered == "limited":
        return "degraded"
    if lowered in {"missing", "permission_denied", "service_missing", "interface_missing", "backend_missing"}:
        return "blocked"
    return "unknown"


def _helper_present(snapshot: Mapping[str, Any] | None, *names: str) -> bool | None:
    if not isinstance(snapshot, Mapping):
        return None
    helpers = snapshot.get("helpers")
    if not isinstance(helpers, Mapping):
        return None
    results = [bool(helpers.get(name)) for name in names if name]
    if not results:
        return None
    return any(results)


def _requirement_status(
    item: Mapping[str, Any],
    *,
    capability_matrix: Mapping[str, Any] | None = None,
    host_snapshot: Mapping[str, Any] | None = None,
) -> tuple[str, str | None]:
    req_id = str(item.get("id") or "")
    req_type = str(item.get("requirement_type") or "")
    capability = str(item.get("capability") or "")
    matrix_item = capability_matrix.get(capability) if isinstance(capability_matrix, Mapping) and capability else None
    matrix_status = str(matrix_item.get("status") or "unknown") if isinstance(matrix_item, Mapping) else "unknown"

    if req_id == "uinput-permissions":
        uinput = host_snapshot.get("uinput") if isinstance(host_snapshot, Mapping) else None
        if isinstance(uinput, Mapping):
            if uinput.get("can_write") is True:
                return "ready", "`/dev/uinput` is writable on this host."
            if uinput.get("can_write") is False:
                return "blocked", "`/dev/uinput` is present but not writable for the current user/service."
        return "unknown", "uinput access was not confirmed in this snapshot."

    if req_id == "ydotool-daemon":
        socket_info = host_snapshot.get("ydotool_socket") if isinstance(host_snapshot, Mapping) else None
        if isinstance(socket_info, Mapping):
            status = str(socket_info.get("status") or "unknown")
            if status == "ok":
                return "ready", "ydotoold socket was detected."
            if status in {"missing", "not_found", "socket_missing", "permission_denied"}:
                return "blocked", "ydotoold socket was not detected."
        return "unknown", "ydotoold presence was not confirmed in this snapshot."

    if req_id == "portal-backend-config":
        cfg = host_snapshot.get("xdg_portal_backend_config") if isinstance(host_snapshot, Mapping) else None
        if isinstance(cfg, Mapping):
            status = str(cfg.get("status") or "unknown")
            if status == "ok":
                return "ready", "A portal routing config with a `[preferred]` section was found."
            if status in {"config_missing", "missing_preferred_section"}:
                return "degraded", "Portal routing config was incomplete or missing."
            if status == "parse_failed":
                return "blocked", "Portal routing config could not be parsed."
        return "unknown", "Portal backend routing was not inspected."

    if req_type == "portal":
        mapped = _track_status(matrix_status)
        note = None
        if isinstance(matrix_item, Mapping):
            recommended = str(matrix_item.get("recommended") or "").strip()
            if recommended:
                note = f"Current session recommendation: `{recommended}`."
        return mapped, note

    if req_id == "text-surface-service":
        present = _helper_present(host_snapshot, "espanso")
        if present is True:
            return "unknown", "Espanso binary is present, but service registration/start still needs review."
        if present is False:
            return "blocked", "Espanso binary was not found on PATH."
        return "unknown", "Text-surface helper availability was not checked."

    if req_id == "remapper-lifecycle":
        present = _helper_present(host_snapshot, "keyd", "kanata", "kmonad", "xremap")
        if present is True:
            return "unknown", "At least one remapper helper is installed, but placement/restart policy still needs review."
        if present is False:
            return "blocked", "No known remapper helper binary was found on PATH."
        return "unknown", "Remapper helper availability was not checked."

    if req_id == "watcher-user-service":
        return "unknown", "VHK can generate user units, but current service enablement was not probed."

    if req_type == "service":
        helper_names = [str(x) for x in list(item.get("services") or []) if str(x)]
        present = _helper_present(host_snapshot, *helper_names)
        if present is False:
            return "blocked", "Required helper binary was not found on PATH."
        return "unknown", None

    return "unknown", None


def build_host_contract_plan(
    project_dir: Path,
    *,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
    host_snapshot: dict[str, object] | None = None,
) -> dict[str, Any]:
    project_dir = project_dir.expanduser().resolve()
    project = load_project(project_dir)
    strategy = summarize_project_strategy(
        project,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
    )
    package_plan = _build_toolchain_package_plan(strategy)
    requirements = [dict(item) for item in list(strategy.get("host_requirements") or []) if isinstance(item, dict)]
    capability_matrix = capability_matrix or {}
    host_snapshot = host_snapshot or {}

    package_group_by_capability = {
        str(item.get("capability") or ""): dict(item)
        for item in list(package_plan.get("package_groups") or [])
        if isinstance(item, dict) and str(item.get("capability") or "")
    }

    enriched_requirements: list[dict[str, Any]] = []
    for item in requirements:
        status, note = _requirement_status(item, capability_matrix=capability_matrix, host_snapshot=host_snapshot)
        capability = str(item.get("capability") or "")
        package_group = dict(package_group_by_capability.get(capability) or {})
        enriched = dict(item)
        enriched["observed_status"] = status
        if note:
            enriched["observed_note"] = note
        if package_group:
            enriched["package_group"] = package_group
        enriched_requirements.append(enriched)

    enriched_requirements.sort(
        key=lambda item: (
            _status_rank(str(item.get("observed_status") or "unknown")),
            _priority_rank(str(item.get("priority") or "conditional")),
            str(item.get("title") or ""),
        )
    )

    grouped_requirements = {
        kind: [dict(item) for item in enriched_requirements if str(item.get("requirement_type") or "") == kind]
        for kind in ["service", "permission", "portal"]
    }

    relevant_capabilities = _dedupe_keep_order([str(item.get("capability") or "") for item in enriched_requirements if str(item.get("capability") or "")])
    relevant_package_groups = [dict(package_group_by_capability[cap]) for cap in relevant_capabilities if cap in package_group_by_capability]

    capability_lanes: list[dict[str, Any]] = []
    for capability in relevant_capabilities:
        items = [dict(item) for item in enriched_requirements if str(item.get("capability") or "") == capability]
        statuses = {str(item.get("observed_status") or "unknown") for item in items}
        lane_status = "blocked" if "blocked" in statuses else ("degraded" if "degraded" in statuses else ("ready" if statuses == {"ready"} else "unknown"))
        package_group = dict(package_group_by_capability.get(capability) or {})
        capability_lanes.append(
            {
                "capability": capability,
                "status": lane_status,
                "requirements": items,
                "package_group": package_group,
                "observed_statuses": sorted(statuses),
            }
        )

    helper_snapshot = {
        key: value
        for key, value in dict(host_snapshot.get("helpers") or {}).items()
        if isinstance(key, str)
    }

    blocked = [item.get("id") for item in enriched_requirements if item.get("observed_status") == "blocked"]
    degraded = [item.get("id") for item in enriched_requirements if item.get("observed_status") == "degraded"]
    unknown = [item.get("id") for item in enriched_requirements if item.get("observed_status") == "unknown"]
    ready = [item.get("id") for item in enriched_requirements if item.get("observed_status") == "ready"]
    overall_status = "blocked" if blocked else ("degraded" if degraded else ("ready" if enriched_requirements and not unknown else "unknown"))

    review_commands = _dedupe_keep_order(
        [
            "vhk doctor --json",
            f"vhk validate {project_dir.as_posix()} --json",
            f"vhk plan-project {project_dir.as_posix()} --json",
            f"vhk gen-host-contract-pack {project_dir.as_posix()} --force --quiet",
            *[
                str(cmd)
                for item in enriched_requirements
                for cmd in list(item.get("verify_commands") or [])
                if str(cmd)
            ],
        ]
    )

    return {
        "source_contract": "host_contract",
        "project": dict(strategy.get("project") or {}),
        "overview": dict(strategy.get("overview") or {}),
        "project_tags": list(strategy.get("project_tags") or []),
        "host_summary": {
            "overall_status": overall_status,
            "host_snapshot_attached": bool(host_snapshot),
            "requirement_count": len(enriched_requirements),
            "blocked_requirements": blocked,
            "degraded_requirements": degraded,
            "unknown_requirements": unknown,
            "ready_requirements": ready,
            "service_count": len(grouped_requirements["service"]),
            "permission_count": len(grouped_requirements["permission"]),
            "portal_count": len(grouped_requirements["portal"]),
        },
        "helper_snapshot": helper_snapshot,
        "package_plan": package_plan,
        "relevant_package_groups": relevant_package_groups,
        "host_requirements": enriched_requirements,
        "grouped_requirements": grouped_requirements,
        "capability_lanes": capability_lanes,
        "review_commands": review_commands,
        "stack_profiles": list(strategy.get("stack_profiles") or strategy.get("deployment_profiles") or []),
        "runtime_seams": list(strategy.get("runtime_seams") or []),
        "session_capabilities": dict(capability_matrix or {}),
        "session_issues": [dict(item) for item in list(capability_issues or []) if isinstance(item, dict)],
        "host_snapshot": dict(host_snapshot or {}),
    }


def render_host_requirements_doc(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    overview = dict(plan.get("overview") or {})
    summary = dict(plan.get("host_summary") or {})
    helper_snapshot = dict(plan.get("helper_snapshot") or {})
    package_groups = _trim_items(plan.get("relevant_package_groups"), limit=8)
    grouped = {key: _trim_items(value, limit=8) for key, value in dict(plan.get("grouped_requirements") or {}).items()}
    review_commands = [str(x) for x in list(plan.get("review_commands") or []) if str(x)]

    lines: list[str] = []
    lines.append(f"# VHK host requirements for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-host-contract-pack`. This is the host-side contract between planner output and Linux-native deployment work: packages, service lifecycle, permissions, and portal routing.")
    lines.append("")
    lines.append("## Snapshot")
    lines.append("")
    lines.append(f"- Root: `{project.get('root_dir') or '.'}`")
    lines.append(f"- Declared desktop backend: `{project.get('desktop_backend') or 'unknown'}`")
    lines.append(f"- Macros: {overview.get('macros', 0)}")
    lines.append(f"- Bindings: {overview.get('bindings', 0)}")
    lines.append(f"- Hotstrings: {overview.get('hotstrings', 0)}")
    lines.append(f"- Overall host status: `{summary.get('overall_status') or 'unknown'}`")
    lines.append(f"- Live host snapshot attached: `{str(bool(summary.get('host_snapshot_attached'))).lower()}`")
    lines.append("")

    if helper_snapshot:
        lines.append("## Helper visibility on this host")
        lines.append("")
        for name, value in sorted(helper_snapshot.items()):
            lines.append(f"- `{name}`: `{value or 'missing'}`")
        lines.append("")

    if package_groups:
        lines.append("## Package bundles")
        lines.append("")
        lines.append("These remain bootstrap hints, but they are now shown next to the non-package host requirements they usually travel with.")
        lines.append("")
        for group in package_groups:
            lines.append(f"### {group.get('title') or group.get('id') or 'Package bundle'}")
            lines.append("")
            lines.append(f"- Capability: `{group.get('capability') or 'unknown'}`")
            packages = [str(x) for x in list(group.get("packages") or []) if str(x)]
            if packages:
                lines.append(f"- Packages: `{', '.join(packages)}`")
            commands = dict(group.get("install_commands") or {})
            if commands:
                lines.append("- Example install commands:")
                for manager in ["apt", "dnf", "pacman", "zypper"]:
                    cmd = str(commands.get(manager) or "").strip()
                    if cmd:
                        lines.append(f"  - `{cmd}`")
            lines.append("")

    section_meta = [
        ("service", "## Service lifecycle requirements"),
        ("permission", "## Permission requirements"),
        ("portal", "## Portal and session requirements"),
    ]
    for key, heading in section_meta:
        items = grouped.get(key) or []
        if not items:
            continue
        lines.append(heading)
        lines.append("")
        for item in items:
            lines.append(f"### {item.get('title') or item.get('id') or 'Requirement'}")
            lines.append("")
            lines.append(f"- Priority: `{item.get('priority') or 'conditional'}`")
            lines.append(f"- Observed status: `{item.get('observed_status') or 'unknown'}`")
            capability = str(item.get("capability") or "").strip()
            if capability:
                lines.append(f"- Capability: `{capability}`")
            applies = _first_text(item, "applies_when")
            if applies:
                lines.append(f"- Applies when: {applies}")
            why = _first_text(item, "why")
            if why:
                lines.append(f"- Why it exists: {why}")
            note = _first_text(item, "observed_note")
            if note:
                lines.append(f"- Current host note: {note}")
            services = [str(x) for x in list(item.get("services") or []) if str(x)]
            if services:
                scope = str(item.get("service_scope") or "").strip()
                lines.append(f"- Services: `{', '.join(services)}`" + (f" (`{scope}`)" if scope else ""))
            groups_ = [str(x) for x in list(item.get("groups") or []) if str(x)]
            if groups_:
                lines.append(f"- Groups: `{', '.join(groups_)}`")
            paths = [str(x) for x in list(item.get("paths") or []) if str(x)]
            if paths:
                lines.append(f"- Paths: `{', '.join(paths)}`")
            portals = [str(x) for x in list(item.get("portal_interfaces") or []) if str(x)]
            if portals:
                lines.append(f"- Portal interfaces: `{', '.join(portals)}`")
            backend_hints = [str(x) for x in list(item.get("portal_backend_hints") or []) if str(x)]
            if backend_hints:
                lines.append(f"- Backend hints: `{', '.join(backend_hints)}`")
            fixups = [str(x) for x in list(item.get("fixup_hints") or []) if str(x)]
            if fixups:
                lines.append("- Review / fixup hints:")
                for hint in fixups[:4]:
                    lines.append(f"  - {hint}")
            lines.append("")

    if review_commands:
        lines.append("## Review loop")
        lines.append("")
        for cmd in review_commands[:8]:
            lines.append(f"- `{cmd}`")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_host_fixups_doc(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    summary = dict(plan.get("host_summary") or {})
    lanes = _trim_items(plan.get("capability_lanes"), limit=10)
    session_issues = _trim_items(plan.get("session_issues"), limit=10)

    lines: list[str] = []
    lines.append(f"# VHK host fixups for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-host-contract-pack`. Use this when package installation was only the first step and the host still needs lifecycle, permission, or portal-routing review.")
    lines.append("")
    lines.append("## Priority summary")
    lines.append("")
    lines.append(f"- Overall host status: `{summary.get('overall_status') or 'unknown'}`")
    lines.append(f"- Blocked requirements: {len(list(summary.get('blocked_requirements') or []))}")
    lines.append(f"- Degraded requirements: {len(list(summary.get('degraded_requirements') or []))}")
    lines.append(f"- Unknown requirements: {len(list(summary.get('unknown_requirements') or []))}")
    lines.append("")

    if lanes:
        lines.append("## Capability lanes")
        lines.append("")
        for lane in lanes:
            lines.append(f"### {lane.get('capability') or 'capability'}")
            lines.append("")
            lines.append(f"- Lane status: `{lane.get('status') or 'unknown'}`")
            package_group = dict(lane.get("package_group") or {})
            packages = [str(x) for x in list(package_group.get("packages") or []) if str(x)]
            if packages:
                lines.append(f"- Related packages: `{', '.join(packages)}`")
            for item in [dict(x) for x in list(lane.get("requirements") or []) if isinstance(x, dict)]:
                lines.append(f"- `{item.get('observed_status') or 'unknown'}` {item.get('title') or item.get('id')}")
                note = _first_text(item, "observed_note")
                if note:
                    lines.append(f"  - {note}")
                for hint in [str(x) for x in list(item.get("fixup_hints") or []) if str(x)][:3]:
                    lines.append(f"  - {hint}")
            lines.append("")

    if session_issues:
        lines.append("## Session-fit warnings carried into this pack")
        lines.append("")
        for item in session_issues:
            message = _first_text(item, "message", "summary")
            suggestion = _first_text(item, "suggestion", "notes")
            capability = str(item.get("capability") or "").strip()
            prefix = f"- `{capability}` — " if capability else "- "
            if suggestion:
                lines.append(f"{prefix}{message} — {suggestion}")
            else:
                lines.append(f"{prefix}{message}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_host_review_script(plan: Mapping[str, Any]) -> str:
    lines: list[str] = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        'DEST="${DEST:-./build/host-contract}"',
        'mkdir -p "$DEST"',
        "",
        "run_json() {",
        '  name="$1"',
        '  shift',
        '  printf "+ %s\\n" "$*"',
        '  sh -lc "$*" > "$DEST/$name" 2> "$DEST/${name%.json}.stderr" || true',
        "}",
        "",
        'echo "Collecting VHK host-contract evidence into $DEST"',
        'run_json doctor.json "vhk doctor --json"',
        'run_json validate.json "vhk validate . --json"',
        'run_json plan-project.json "vhk plan-project . --json"',
        'printf "+ %s\\n" "vhk gen-host-contract-pack . --force --quiet"',
        'sh -lc "vhk gen-host-contract-pack . --force --quiet" || true',
        'echo "Host-contract refresh complete."',
        'echo "Review: $DEST/doctor.json, $DEST/validate.json, and $DEST/plan-project.json"',
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"


def write_host_contract_pack(
    project_dir: Path,
    *,
    out_dir: Path | None = None,
    script_dir: Path | None = None,
    force: bool = False,
    requirements_doc: bool = True,
    fixups_doc: bool = True,
    plan_json: bool = True,
    review_script: bool = True,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
    host_snapshot: dict[str, object] | None = None,
) -> dict[str, Path]:
    project_dir = project_dir.expanduser().resolve()
    out_dir = (out_dir or (project_dir / "docs")).expanduser().resolve()
    script_dir = (script_dir or (project_dir / "scripts")).expanduser().resolve()

    plan = build_host_contract_plan(
        project_dir,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
        host_snapshot=host_snapshot,
    )

    written: dict[str, Path] = {}
    if requirements_doc:
        path = out_dir / "VHK_HOST_REQUIREMENTS.md"
        _write_if_allowed(path, render_host_requirements_doc(plan), force=force)
        written["requirements_doc"] = path
    if fixups_doc:
        path = out_dir / "VHK_HOST_FIXUPS.md"
        _write_if_allowed(path, render_host_fixups_doc(plan), force=force)
        written["fixups_doc"] = path
    if plan_json:
        path = out_dir / "VHK_HOST_PLAN.json"
        _write_if_allowed(path, json.dumps(plan, indent=2, sort_keys=False) + "\n", force=force)
        written["plan_json"] = path
    if review_script:
        path = script_dir / "vhk_review_host_contract.sh"
        _write_if_allowed(path, render_host_review_script(plan), force=force)
        path.chmod(path.stat().st_mode | 0o111)
        written["review_script"] = path
    return written
