from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from vhk.project.loader import load_project
from vhk.project.setup_pack import _build_toolchain_package_plan, _lane_filter_id
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


def _alternative_order(value: Mapping[str, Any]) -> int:
    try:
        return int(value.get("alternative_order"))
    except (TypeError, ValueError):
        return 999


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


def _service_probe(snapshot: Mapping[str, Any] | None, unit: str, scope: str) -> Mapping[str, Any] | None:
    if not isinstance(snapshot, Mapping):
        return None
    service_units = snapshot.get("service_units")
    if not isinstance(service_units, Mapping):
        return None
    item = service_units.get(f"{str(scope or 'system').strip().lower()}:{str(unit or '').strip()}")
    return item if isinstance(item, Mapping) else None


_PORTAL_INTERFACES: list[tuple[str, str, str]] = [
    ("org.freedesktop.impl.portal.Screenshot", "Screenshot", "xdg_portal_screenshot"),
    ("org.freedesktop.impl.portal.ScreenCast", "ScreenCast", "xdg_portal_screencast"),
    ("org.freedesktop.impl.portal.RemoteDesktop", "RemoteDesktop", "xdg_portal_remote_desktop"),
    ("org.freedesktop.impl.portal.InputCapture", "InputCapture", "xdg_portal_input_capture"),
    ("org.freedesktop.impl.portal.GlobalShortcuts", "GlobalShortcuts", "xdg_portal_global_shortcuts"),
]


def _portal_live_status(snapshot: Mapping[str, Any] | None, probe_key: str) -> str:
    if not isinstance(snapshot, Mapping):
        return "unknown"
    probe = snapshot.get(probe_key)
    if not isinstance(probe, Mapping):
        return "unknown"
    return str(probe.get("status") or "unknown")


def _manifest_backend_catalog(snapshot: Mapping[str, Any] | None) -> tuple[dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]], list[dict[str, Any]], list[dict[str, Any]], str, str | None]:
    manifests = snapshot.get("xdg_portal_backend_manifests") if isinstance(snapshot, Mapping) else None
    manifest_status = str((manifests or {}).get("status") or "unknown") if isinstance(manifests, Mapping) else "unknown"
    xdg_current_desktop = str((manifests or {}).get("xdg_current_desktop") or (snapshot or {}).get("xdg_current_desktop") or "").strip() or None
    backend_entries = [dict(item) for item in list((manifests or {}).get("backends") or []) if isinstance(item, Mapping)] if isinstance(manifests, Mapping) else []
    parse_errors = [dict(item) for item in list((manifests or {}).get("parse_errors") or []) if isinstance(item, Mapping)] if isinstance(manifests, Mapping) else []
    by_backend: dict[str, dict[str, Any]] = {}
    by_interface: dict[str, list[dict[str, Any]]] = {}
    for item in backend_entries:
        backend = str(item.get("backend") or "").strip()
        if not backend:
            continue
        normalized = dict(item)
        normalized["interfaces"] = [str(x) for x in list(item.get("interfaces") or []) if str(x)]
        normalized["use_in"] = [str(x) for x in list(item.get("use_in") or []) if str(x)]
        normalized["matching_desktops"] = [str(x) for x in list(item.get("matching_desktops") or []) if str(x)]
        by_backend[backend] = normalized
        for interface_name in normalized["interfaces"]:
            by_interface.setdefault(interface_name, []).append(normalized)
    for entries in by_interface.values():
        entries.sort(key=lambda item: (0 if bool(item.get("usable_on_current_desktop")) else 1, str(item.get("backend") or "")))
    return by_backend, by_interface, backend_entries, parse_errors, manifest_status, xdg_current_desktop


def build_portal_route_contract(
    requirements: list[dict[str, Any]] | None,
    *,
    capability_matrix: Mapping[str, Any] | None = None,
    host_snapshot: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    host_snapshot = host_snapshot or {}
    cfg = host_snapshot.get("xdg_portal_backend_config") if isinstance(host_snapshot, Mapping) else None
    cfg = dict(cfg) if isinstance(cfg, Mapping) else {}
    cfg_status = str(cfg.get("status") or "unknown")
    preferred_default = [str(x) for x in list(cfg.get("preferred_default") or []) if str(x)]
    preferred_interfaces = {
        str(key): [str(x) for x in list(value or []) if str(x)]
        for key, value in dict(cfg.get("preferred_interfaces") or {}).items()
        if str(key)
    }
    manifest_by_backend, manifest_by_interface, manifest_backends, parse_errors, manifest_status, xdg_current_desktop = _manifest_backend_catalog(host_snapshot)

    requested_interfaces: list[str] = []
    for item in list(requirements or []):
        if not isinstance(item, Mapping):
            continue
        for interface_name in list(item.get("portal_interfaces") or []):
            interface_text = str(interface_name or "").strip()
            if interface_text and interface_text not in requested_interfaces:
                requested_interfaces.append(interface_text)
    for interface_name, _short_name, _probe_key in _PORTAL_INTERFACES:
        if interface_name not in requested_interfaces:
            requested_interfaces.append(interface_name)

    configured_backends_all: list[str] = []
    for backend_name in preferred_default:
        if backend_name not in configured_backends_all:
            configured_backends_all.append(backend_name)
    for entries in preferred_interfaces.values():
        for backend_name in entries:
            if backend_name not in configured_backends_all:
                configured_backends_all.append(backend_name)

    live_interfaces: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    installed_usable_backends: list[str] = []
    installed_all_backends: list[str] = []
    for interface_name, short_name, probe_key in _PORTAL_INTERFACES:
        configured_backends = [str(x) for x in list(preferred_interfaces.get(interface_name) or preferred_default) if str(x)]
        installed_entries = [dict(item) for item in list(manifest_by_interface.get(interface_name) or []) if isinstance(item, Mapping)]
        installed_backend_names = [str(item.get("backend") or "") for item in installed_entries if str(item.get("backend") or "")]
        usable_entries = [item for item in installed_entries if bool(item.get("usable_on_current_desktop"))]
        usable_backend_names = [str(item.get("backend") or "") for item in usable_entries if str(item.get("backend") or "")]
        for backend_name in installed_backend_names:
            if backend_name and backend_name not in installed_all_backends:
                installed_all_backends.append(backend_name)
        for backend_name in usable_backend_names:
            if backend_name and backend_name not in installed_usable_backends:
                installed_usable_backends.append(backend_name)
        missing_configured = [name for name in configured_backends if name not in {"*", "none"} and name not in installed_backend_names]
        desktop_mismatch = [name for name in configured_backends if name not in {"*", "none"} and name in installed_backend_names and name not in usable_backend_names]
        live_status = _portal_live_status(host_snapshot, probe_key)
        live_item = {
            "interface": interface_name,
            "short_name": short_name,
            "probe_key": probe_key,
            "live_status": live_status,
            "configured_backends": configured_backends,
            "installed_backends": installed_backend_names,
            "usable_backends": usable_backend_names,
            "missing_configured_backends": missing_configured,
            "desktop_mismatch_backends": desktop_mismatch,
            "live_recommended": str(((capability_matrix or {}).get({
                "org.freedesktop.impl.portal.Screenshot": "screen_capture",
                "org.freedesktop.impl.portal.ScreenCast": "screen_capture",
                "org.freedesktop.impl.portal.RemoteDesktop": "text_injection",
                "org.freedesktop.impl.portal.InputCapture": "input_capture",
                "org.freedesktop.impl.portal.GlobalShortcuts": "global_hotkeys",
            }.get(interface_name, "")) or {}).get("recommended") or "").strip() or None,
            "requested_by_project": interface_name in requested_interfaces,
            "installed_entries": [
                {
                    "backend": str(item.get("backend") or ""),
                    "manifest_path": item.get("manifest_path"),
                    "usable_on_current_desktop": bool(item.get("usable_on_current_desktop")),
                    "use_in": [str(x) for x in list(item.get("use_in") or []) if str(x)],
                    "matching_desktops": [str(x) for x in list(item.get("matching_desktops") or []) if str(x)],
                }
                for item in installed_entries
            ],
        }
        live_interfaces.append(live_item)
        if missing_configured:
            issues.append({
                "severity": "warning",
                "kind": "configured_backend_missing",
                "interface": interface_name,
                "summary": f"{short_name} is configured to use backend ids that are not installed: {', '.join(missing_configured)}.",
            })
        if desktop_mismatch:
            issues.append({
                "severity": "warning",
                "kind": "configured_backend_desktop_mismatch",
                "interface": interface_name,
                "summary": f"{short_name} is configured to prefer installed backends that do not match the current desktop: {', '.join(desktop_mismatch)}.",
            })
        if live_status in {"service_missing", "interface_missing"} and usable_backend_names:
            issues.append({
                "severity": "warning",
                "kind": "installed_backend_not_live",
                "interface": interface_name,
                "summary": f"{short_name} has installed backend candidates ({', '.join(usable_backend_names)}) but the live portal interface is still missing; check D-Bus activation environment, backend startup, and routing.",
            })

    if cfg_status == "config_missing":
        issues.append({
            "severity": "info",
            "kind": "config_missing",
            "summary": "No portals.conf was found, so routing depends on distro/session defaults instead of an explicit per-interface contract.",
        })
    elif cfg_status == "missing_preferred_section":
        issues.append({
            "severity": "warning",
            "kind": "config_incomplete",
            "summary": "A portals.conf file was found but it does not contain a [preferred] section.",
        })
    elif cfg_status == "parse_failed":
        issues.append({
            "severity": "warning",
            "kind": "config_parse_failed",
            "summary": "The active portals.conf file could not be parsed cleanly.",
        })

    if parse_errors:
        bad_paths = [str(item.get("path") or "").strip() for item in parse_errors if str(item.get("path") or "").strip()]
        issues.append({
            "severity": "warning",
            "kind": "manifest_parse_errors",
            "summary": "Some installed .portal manifests could not be parsed: " + ", ".join(bad_paths[:3]) + ("." if len(bad_paths) <= 3 else " ..."),
        })

    route_status = "ready"
    if any(str(item.get("severity") or "") == "warning" for item in issues):
        route_status = "degraded"
    if cfg_status in {"parse_failed"} or manifest_status == "parse_failed":
        route_status = "blocked"
    if cfg_status == "unknown" and manifest_status in {"unknown", "manifest_dir_missing", "manifest_missing"}:
        route_status = "unknown"

    return {
        "status": route_status,
        "xdg_current_desktop": xdg_current_desktop,
        "config_status": cfg_status,
        "config_path": cfg.get("config_path"),
        "preferred_default": preferred_default,
        "preferred_interfaces": preferred_interfaces,
        "manifest_status": manifest_status,
        "manifest_backend_count": len(manifest_backends),
        "usable_backend_count": len(installed_usable_backends),
        "installed_backends": installed_all_backends,
        "usable_backends": installed_usable_backends,
        "backends": [
            {
                "backend": str(item.get("backend") or ""),
                "manifest_path": item.get("manifest_path"),
                "interfaces": [str(x) for x in list(item.get("interfaces") or []) if str(x)],
                "use_in": [str(x) for x in list(item.get("use_in") or []) if str(x)],
                "matching_desktops": [str(x) for x in list(item.get("matching_desktops") or []) if str(x)],
                "usable_on_current_desktop": bool(item.get("usable_on_current_desktop")),
            }
            for item in manifest_backends
        ],
        "parse_errors": parse_errors,
        "interfaces": live_interfaces,
        "issues": issues,
    }


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

    if req_id == "dotool-daemon":
        user_probe = _service_probe(host_snapshot, "dotoold.service", "user")
        system_probe = _service_probe(host_snapshot, "dotoold.service", "system")
        probes = [probe for probe in (user_probe, system_probe) if isinstance(probe, Mapping)]
        statuses = {str(probe.get("status") or "unknown") for probe in probes}
        if "ok" in statuses:
            return "ready", "dotoold service was detected."
        if statuses.intersection({"inactive", "activating", "deactivating", "loaded"}):
            return "degraded", "dotoold is installed, but no active service was confirmed."
        if statuses.intersection({"failed", "unit_missing"}):
            return "blocked", "dotoold service was not installed or failed to start."
        present = _helper_present(host_snapshot, "dotool", "dotoolc", "dotoold")
        if present is False:
            return "blocked", "dotool / dotoolc helper binaries were not found on PATH."
        if present is True:
            return "unknown", "dotool helpers are installed, but dotoold lifecycle was not confirmed in this snapshot."
        return "unknown", "dotoold presence was not confirmed in this snapshot."

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

    if req_id in {"keyd-remapper-service", "kanata-remapper-service", "xremap-remapper-service", "kmonad-remapper-service"}:
        helper_map = {
            "keyd-remapper-service": ("keyd", "keyd", [("keyd.service", "system")]),
            "kanata-remapper-service": ("kanata", "Kanata", [("kanata.service", "user"), ("kanata.service", "system")]),
            "xremap-remapper-service": ("xremap", "xremap", [("xremap.service", "user"), ("xremap.service", "system")]),
            "kmonad-remapper-service": ("kmonad", "KMonad", [("kmonad.service", "user"), ("kmonad.service", "system")]),
        }
        helper_name, label, unit_specs = helper_map[req_id]
        probes = [_service_probe(host_snapshot, unit, scope) for unit, scope in unit_specs]
        statuses = {str(probe.get("status") or "unknown") for probe in probes if isinstance(probe, Mapping)}
        if "ok" in statuses:
            return "ready", f"{label} service was detected."
        if statuses.intersection({"inactive", "activating", "deactivating", "loaded"}):
            return "degraded", f"{label} is installed, but no active service was confirmed."
        present = _helper_present(host_snapshot, helper_name)
        if present is False:
            return "blocked", f"{label} binary was not found on PATH."
        if statuses.intersection({"failed", "unit_missing"}):
            return "blocked", f"{label} service was not installed or failed to start."
        if present is True:
            return "unknown", f"{label} is installed, but service lifecycle was not confirmed in this snapshot."
        return "unknown", f"{label} presence was not confirmed in this snapshot."

    if req_id == "watcher-user-service":
        return "unknown", "VHK can generate user units, but current service enablement was not probed."

    if req_type == "service":
        helper_names = [str(x) for x in list(item.get("services") or []) if str(x)]
        present = _helper_present(host_snapshot, *helper_names)
        if present is False:
            return "blocked", "Required helper binary was not found on PATH."
        return "unknown", None

    return "unknown", None


def _status_for_all_of(statuses: list[str]) -> str:
    tracks = {str(item or "unknown") for item in statuses}
    if not tracks:
        return "unknown"
    if "blocked" in tracks:
        return "blocked"
    if "degraded" in tracks:
        return "degraded"
    if tracks == {"ready"}:
        return "ready"
    return "unknown"


def _status_for_one_of(statuses: list[str]) -> str:
    tracks = {str(item or "unknown") for item in statuses}
    if not tracks:
        return "unknown"
    if "ready" in tracks:
        return "ready"
    if "degraded" in tracks:
        return "degraded"
    if tracks == {"blocked"}:
        return "blocked"
    return "unknown"


def _status_for_policy(statuses: list[str], policy: str) -> str:
    if str(policy or "").strip().lower() == "one_of":
        return _status_for_one_of(statuses)
    return _status_for_all_of(statuses)


def summarize_requirement_alternative_groups(
    requirements: list[dict[str, Any]] | None,
    *,
    status_key: str,
    effective_key: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    items = [dict(item) for item in list(requirements or []) if isinstance(item, dict)]
    grouped: dict[str, dict[str, Any]] = {}
    for item in items:
        group_id = str(item.get("alternative_group") or "").strip()
        if not group_id:
            continue
        group = grouped.setdefault(
            group_id,
            {
                "id": group_id,
                "title": str(item.get("alternative_title") or group_id).strip() or group_id,
                "policy": str(item.get("alternative_policy") or "one_of").strip() or "one_of",
                "capability": str(item.get("capability") or "").strip() or None,
                "members": [],
            },
        )
        if not group.get("capability") and str(item.get("capability") or "").strip():
            group["capability"] = str(item.get("capability") or "").strip()
        group["members"].append(item)

    summaries: list[dict[str, Any]] = []
    summary_by_id: dict[str, dict[str, Any]] = {}
    for group_id, raw_group in grouped.items():
        members = [dict(item) for item in list(raw_group.get("members") or []) if isinstance(item, dict)]
        if not members:
            continue
        members.sort(
            key=lambda item: (
                _alternative_order(item),
                _priority_rank(str(item.get("priority") or "conditional")),
                str(item.get("title") or item.get("id") or ""),
            )
        )
        policy = str(raw_group.get("policy") or "one_of")
        ready_members = [str(item.get("id") or "") for item in members if str(item.get(status_key) or "") == "ready"]
        degraded_members = [str(item.get("id") or "") for item in members if str(item.get(status_key) or "") == "degraded"]
        blocked_members = [str(item.get("id") or "") for item in members if str(item.get(status_key) or "") == "blocked"]
        unknown_members = [str(item.get("id") or "") for item in members if str(item.get(status_key) or "unknown") == "unknown"]
        effective_status = _status_for_policy([str(item.get(status_key) or "unknown") for item in members], policy)

        active_member_ids: list[str] = []
        if str(policy).lower() == "one_of":
            if ready_members:
                active_member_ids = ready_members
            elif degraded_members:
                active_member_ids = degraded_members

        preferred_member: dict[str, Any] | None = None
        if str(policy).lower() == "one_of":
            for bucket in (ready_members, degraded_members, unknown_members, blocked_members):
                if not bucket:
                    continue
                preferred_member = next((member for member in members if str(member.get("id") or "") == bucket[0]), None)
                if preferred_member is not None:
                    break
        preferred_member_id = str(preferred_member.get("id") or "") if preferred_member else ""
        preferred_member_title = str(preferred_member.get("title") or preferred_member_id).strip() if preferred_member else ""

        note = ""
        if str(policy).lower() == "one_of":
            if effective_status == "ready" and active_member_ids:
                note = "Alternative lane satisfied by " + ", ".join(f"`{item}`" for item in active_member_ids) + "."
            elif effective_status == "degraded" and active_member_ids:
                note = "Alternative lane is only partially ready; the current best member is " + ", ".join(f"`{item}`" for item in active_member_ids) + "."
            elif effective_status == "blocked":
                note = "All members of this alternative lane are currently blocked."
            else:
                note = "No member of this alternative lane was fully confirmed yet."
            if preferred_member_id:
                note = (note + f" Preferred member: `{preferred_member_id}`.").strip()

        summary = {
            "id": group_id,
            "title": str(raw_group.get("title") or group_id),
            "policy": policy,
            "capability": raw_group.get("capability"),
            "effective_status": effective_status,
            "active_member_ids": active_member_ids,
            "preferred_member_id": preferred_member_id or None,
            "preferred_member_title": preferred_member_title or None,
            "ready_members": ready_members,
            "degraded_members": degraded_members,
            "blocked_members": blocked_members,
            "unknown_members": unknown_members,
            "note": note,
            "members": members,
        }
        summaries.append(summary)
        summary_by_id[group_id] = summary

    annotated: list[dict[str, Any]] = []
    for item in items:
        group_id = str(item.get("alternative_group") or "").strip()
        enriched = dict(item)
        if group_id and group_id in summary_by_id:
            summary = summary_by_id[group_id]
            active_member_ids = {str(x) for x in list(summary.get("active_member_ids") or []) if str(x)}
            member_id = str(item.get("id") or "")
            suppressed = bool(active_member_ids) and member_id not in active_member_ids
            enriched["alternative_group_status"] = summary.get("effective_status")
            enriched["alternative_group_title"] = summary.get("title")
            enriched["alternative_group_note"] = summary.get("note")
            enriched["alternative_group_active_member_ids"] = list(summary.get("active_member_ids") or [])
            enriched["alternative_group_preferred_member_id"] = summary.get("preferred_member_id")
            enriched["alternative_group_preferred_member_title"] = summary.get("preferred_member_title")
            enriched["suppressed_by_alternative"] = suppressed
            enriched[effective_key] = "covered" if suppressed else enriched.get(status_key)
        else:
            enriched["suppressed_by_alternative"] = False
            enriched[effective_key] = enriched.get(status_key)
        annotated.append(enriched)

    summaries.sort(key=lambda item: (str(item.get("capability") or ""), str(item.get("title") or item.get("id") or "")))
    return annotated, summaries


def attach_alternative_package_context(
    alternative_groups: list[dict[str, Any]] | None,
    package_group_by_capability: Mapping[str, Mapping[str, Any]] | None,
) -> list[dict[str, Any]]:
    package_group_by_capability = package_group_by_capability or {}
    enriched_groups: list[dict[str, Any]] = []
    for raw_group in list(alternative_groups or []):
        if not isinstance(raw_group, Mapping):
            continue
        group = dict(raw_group)
        capability = str(group.get("capability") or "").strip()
        package_group = dict(package_group_by_capability.get(capability) or {})
        package_group_id = str(package_group.get("id") or capability or "packages").strip() or "packages"
        alt_package_group: dict[str, Any] = {}
        for candidate in [dict(item) for item in list(package_group.get("alternative_package_groups") or []) if isinstance(item, dict)]:
            if str(candidate.get("id") or "").strip() == str(group.get("id") or "").strip():
                alt_package_group = candidate
                break
        members_by_id = {
            str(item.get("id") or "").strip(): dict(item)
            for item in list(alt_package_group.get("members") or [])
            if isinstance(item, dict) and str(item.get("id") or "").strip()
        }
        preferred_member_id = str(group.get("preferred_member_id") or "").strip()
        enriched_members: list[dict[str, Any]] = []
        for raw_member in list(group.get("members") or []):
            if not isinstance(raw_member, Mapping):
                continue
            member = dict(raw_member)
            member_id = str(member.get("id") or "").strip()
            package_member = dict(members_by_id.get(member_id) or {})
            member["bootstrap_filter_id"] = str(package_member.get("filter_id") or _lane_filter_id(package_group_id, member_id)) if member_id else None
            member["selected_by_default"] = bool(package_member.get("selected_by_default"))
            member["effective_packages"] = [str(x) for x in list(package_member.get("effective_packages") or []) if str(x)]
            enriched_members.append(member)
        group["members"] = enriched_members
        group["package_group_id"] = package_group_id
        group["default_bootstrap_filter_id"] = str(alt_package_group.get("selected_filter_id") or "").strip() or None
        group["bootstrap_filter_options"] = [str(item.get("bootstrap_filter_id") or "") for item in enriched_members if str(item.get("bootstrap_filter_id") or "")]
        preferred_filter = str((members_by_id.get(preferred_member_id) or {}).get("filter_id") or "").strip() if preferred_member_id else ""
        group["bootstrap_filter_id"] = preferred_filter or group.get("default_bootstrap_filter_id")
        enriched_groups.append(group)
    return enriched_groups


def build_host_contract_plan(
    project_dir: Path,
    *,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
    host_snapshot: dict[str, object] | None = None,
    evidence_lane_profile: str | None = None,
) -> dict[str, Any]:
    project_dir = project_dir.expanduser().resolve()
    project = load_project(project_dir)
    strategy = summarize_project_strategy(
        project,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
        evidence_lane_profile=evidence_lane_profile,
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

    enriched_requirements, alternative_groups = summarize_requirement_alternative_groups(
        enriched_requirements,
        status_key="observed_status",
        effective_key="effective_observed_status",
    )
    alternative_groups = attach_alternative_package_context(alternative_groups, package_group_by_capability)

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

    standalone_effective_units: list[dict[str, Any]] = [
        {"id": str(item.get("id") or ""), "capability": item.get("capability"), "status": str(item.get("observed_status") or "unknown")}
        for item in enriched_requirements
        if not str(item.get("alternative_group") or "").strip()
    ]
    alternative_effective_units: list[dict[str, Any]] = [
        {
            "id": str(item.get("id") or ""),
            "capability": item.get("capability"),
            "status": str(item.get("effective_status") or "unknown"),
            "title": item.get("title"),
            "active_member_ids": list(item.get("active_member_ids") or []),
        }
        for item in alternative_groups
    ]
    effective_units = [*standalone_effective_units, *alternative_effective_units]

    capability_lanes: list[dict[str, Any]] = []
    for capability in relevant_capabilities:
        items = [dict(item) for item in enriched_requirements if str(item.get("capability") or "") == capability]
        capability_alternative_groups = [dict(item) for item in alternative_groups if str(item.get("capability") or "") == capability]
        unit_statuses = [
            str(item.get("observed_status") or "unknown")
            for item in items
            if not str(item.get("alternative_group") or "").strip()
        ]
        unit_statuses.extend(str(item.get("effective_status") or "unknown") for item in capability_alternative_groups)
        lane_status = _status_for_all_of(unit_statuses)
        package_group = dict(package_group_by_capability.get(capability) or {})
        capability_lanes.append(
            {
                "capability": capability,
                "status": lane_status,
                "requirements": items,
                "alternative_groups": capability_alternative_groups,
                "package_group": package_group,
                "observed_statuses": sorted({str(item.get("observed_status") or "unknown") for item in items}),
                "effective_unit_statuses": unit_statuses,
            }
        )

    helper_snapshot = {
        key: value
        for key, value in dict(host_snapshot.get("helpers") or {}).items()
        if isinstance(key, str)
    }
    portal_route_contract = build_portal_route_contract(
        requirements,
        capability_matrix=capability_matrix,
        host_snapshot=host_snapshot,
    )

    blocked = [item.get("id") for item in enriched_requirements if item.get("observed_status") == "blocked"]
    degraded = [item.get("id") for item in enriched_requirements if item.get("observed_status") == "degraded"]
    unknown = [item.get("id") for item in enriched_requirements if item.get("observed_status") == "unknown"]
    ready = [item.get("id") for item in enriched_requirements if item.get("observed_status") == "ready"]

    effective_blocked = [str(item.get("id") or "") for item in effective_units if str(item.get("status") or "") == "blocked"]
    effective_degraded = [str(item.get("id") or "") for item in effective_units if str(item.get("status") or "") == "degraded"]
    effective_unknown = [str(item.get("id") or "") for item in effective_units if str(item.get("status") or "") == "unknown"]
    effective_ready = [str(item.get("id") or "") for item in effective_units if str(item.get("status") or "") == "ready"]
    overall_status = "blocked" if effective_blocked else ("degraded" if effective_degraded else ("ready" if effective_units and not effective_unknown else "unknown"))

    from vhk.project.target_fit_contract import build_target_fit_contract_from_lane, select_target_lane

    selected_evidence_lane = dict(strategy.get("planner_evidence_lane") or {})
    evidence_lane_fit = dict(strategy.get("planner_evidence_lane_fit") or {})
    if not selected_evidence_lane:
        try:
            selected = select_target_lane(
                project_dir,
                bundle_target_profile=evidence_lane_profile,
                capability_usage=capability_usage,
            )
        except Exception:
            selected = {}
        if selected:
            selected_evidence_lane = {
                "profile_id": str(selected.get("profile_id") or ""),
                "title": str(selected.get("title") or selected.get("profile_id") or "target"),
                "release_level": str(selected.get("release_level") or ""),
                "backend": str(selected.get("backend") or ""),
                "desktop_family": str(selected.get("desktop_family") or ""),
                "trigger_route_id": str(selected.get("trigger_route_id") or ""),
                "overall_status": str(selected.get("overall_status") or ""),
                "selection_source": "explicit" if evidence_lane_profile else "flagship-default",
                "requested_profile_id": str(evidence_lane_profile or "").strip() or None,
            }
            evidence_lane_fit = build_target_fit_contract_from_lane(
                selected,
                host_truth={"overall_status": overall_status},
                host_requirements=enriched_requirements,
                portal_route_contract=portal_route_contract,
            )
            if evidence_lane_fit:
                evidence_lane_fit["selection_source"] = "explicit" if evidence_lane_profile else "flagship-default"
                evidence_lane_fit["requested_profile_id"] = str(evidence_lane_profile or "").strip() or None
    elif selected_evidence_lane and not evidence_lane_fit:
        try:
            selected = select_target_lane(
                project_dir,
                bundle_target_profile=str(selected_evidence_lane.get("profile_id") or "").strip() or evidence_lane_profile,
                capability_usage=capability_usage,
            )
        except Exception:
            selected = {}
        if selected:
            evidence_lane_fit = build_target_fit_contract_from_lane(
                selected,
                host_truth={"overall_status": overall_status},
                host_requirements=enriched_requirements,
                portal_route_contract=portal_route_contract,
            )
            if evidence_lane_fit:
                evidence_lane_fit["selection_source"] = str(selected_evidence_lane.get("selection_source") or ("explicit" if evidence_lane_profile else "flagship-default"))
                evidence_lane_fit["requested_profile_id"] = str(evidence_lane_profile or "").strip() or None

    evidence_flag = f" --evidence-lane {evidence_lane_profile}" if str(evidence_lane_profile or "").strip() else ""

    review_commands = _dedupe_keep_order(
        [
            "vhk doctor --json",
            f"vhk validate {project_dir.as_posix()} --json",
            f"vhk plan-project {project_dir.as_posix()} --json{evidence_flag}",
            f"vhk gen-host-contract-pack {project_dir.as_posix()} --force --quiet{evidence_flag}",
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
        "selected_evidence_lane": selected_evidence_lane,
        "evidence_lane_fit": evidence_lane_fit,
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
            "effective_blockers": effective_blocked,
            "effective_degraded": effective_degraded,
            "effective_unknown": effective_unknown,
            "effective_ready": effective_ready,
            "service_count": len(grouped_requirements["service"]),
            "permission_count": len(grouped_requirements["permission"]),
            "portal_count": len(grouped_requirements["portal"]),
            "alternative_group_count": len(alternative_groups),
            "satisfied_alternative_groups": [str(item.get("id") or "") for item in alternative_groups if str(item.get("effective_status") or "") in {"ready", "degraded"}],
        },
        "helper_snapshot": helper_snapshot,
        "package_plan": package_plan,
        "relevant_package_groups": relevant_package_groups,
        "host_requirements": enriched_requirements,
        "alternative_requirement_groups": alternative_groups,
        "grouped_requirements": grouped_requirements,
        "capability_lanes": capability_lanes,
        "review_commands": review_commands,
        "stack_profiles": list(strategy.get("stack_profiles") or strategy.get("deployment_profiles") or []),
        "runtime_seams": list(strategy.get("runtime_seams") or []),
        "session_capabilities": dict(capability_matrix or {}),
        "session_issues": [dict(item) for item in list(capability_issues or []) if isinstance(item, dict)],
        "portal_route_contract": portal_route_contract,
        "host_snapshot": dict(host_snapshot or {}),
    }


def render_host_requirements_doc(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    overview = dict(plan.get("overview") or {})
    summary = dict(plan.get("host_summary") or {})
    helper_snapshot = dict(plan.get("helper_snapshot") or {})
    portal_route_contract = dict(plan.get("portal_route_contract") or {})
    package_groups = _trim_items(plan.get("relevant_package_groups"), limit=8)
    alternative_groups = _trim_items(plan.get("alternative_requirement_groups"), limit=8)
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
    selected_lane = dict(plan.get("selected_evidence_lane") or {})
    lane_fit = dict(plan.get("evidence_lane_fit") or {})
    if selected_lane:
        lines.append(f"- Evidence lane: `{selected_lane.get('profile_id') or 'unknown'}` ({selected_lane.get('selection_source') or 'flagship-default'})")
    if lane_fit:
        lines.append(f"- Evidence lane fit: `{lane_fit.get('status') or 'unknown'}`")
    lines.append(f"- Live host snapshot attached: `{str(bool(summary.get('host_snapshot_attached'))).lower()}`")
    lines.append(f"- Alternative requirement groups: {summary.get('alternative_group_count') or 0}")
    lines.append("")

    if helper_snapshot:
        lines.append("## Helper visibility on this host")
        lines.append("")
        for name, value in sorted(helper_snapshot.items()):
            lines.append(f"- `{name}`: `{value or 'missing'}`")
        lines.append("")

    if portal_route_contract:
        lines.append("## Portal route contract")
        lines.append("")
        lines.append("This section compares three truths VHK now keeps separate: configured routing (`portals.conf`), installed backend manifests (`*.portal`), and the live frontend interfaces visible on D-Bus.")
        lines.append("")
        lines.append(f"- Route status: `{portal_route_contract.get('status') or 'unknown'}`")
        lines.append(f"- XDG_CURRENT_DESKTOP: `{portal_route_contract.get('xdg_current_desktop') or 'unknown'}`")
        lines.append(f"- Config status: `{portal_route_contract.get('config_status') or 'unknown'}`")
        lines.append(f"- Manifest status: `{portal_route_contract.get('manifest_status') or 'unknown'}`")
        lines.append(f"- Installed backends: `{', '.join([str(x) for x in list(portal_route_contract.get('installed_backends') or []) if str(x)]) or '(none reported)'}`")
        lines.append(f"- Usable backends: `{', '.join([str(x) for x in list(portal_route_contract.get('usable_backends') or []) if str(x)]) or '(none reported)'}`")
        issues = [dict(item) for item in list(portal_route_contract.get('issues') or []) if isinstance(item, dict)]
        if issues:
            lines.append("- Route issues:")
            for item in issues[:5]:
                lines.append(f"  - {item.get('summary') or item.get('kind') or 'portal issue'}")
        lines.append("")
        lines.append("### Per-interface route view")
        lines.append("")
        for item in [dict(x) for x in list(portal_route_contract.get('interfaces') or []) if isinstance(x, dict)][:8]:
            lines.append(f"- `{item.get('short_name') or item.get('interface') or ''}` → live `{item.get('live_status') or 'unknown'}`; configured `{', '.join([str(x) for x in list(item.get('configured_backends') or []) if str(x)]) or '(default)'}`; usable `{', '.join([str(x) for x in list(item.get('usable_backends') or []) if str(x)]) or '(none)'}`")
        lines.append("")

    if package_groups:
        lines.append("## Package bundles")
        lines.append("")
        lines.append("These remain bootstrap hints, but they are now shown next to the non-package host requirements they usually travel with.")
        lines.append("")
        for group in package_groups:
            lines.append(f"### {group.get('title') or group.get('id') or 'Package bundle'}")
            lines.append("")

    if alternative_groups:
        lines.append("## Alternative requirement groups")
        lines.append("")
        lines.append("These groups model choose-one host lanes. A blocked helper inside a satisfied group stays visible for review, but it does not block the whole capability by itself.")
        lines.append("")
        for group in alternative_groups:
            lines.append(f"### {group.get('title') or group.get('id') or 'Alternative group'}")
            lines.append("")
            lines.append(f"- Group id: `{group.get('id') or ''}`")
            lines.append(f"- Policy: `{group.get('policy') or 'one_of'}`")
            lines.append(f"- Effective status: `{group.get('effective_status') or 'unknown'}`")
            capability = str(group.get("capability") or "").strip()
            if capability:
                lines.append(f"- Capability: `{capability}`")
            note = _first_text(group, "note")
            if note:
                lines.append(f"- Note: {note}")
            for member in [dict(item) for item in list(group.get("members") or []) if isinstance(item, dict)]:
                lines.append(f"- `{member.get('id') or ''}` → `{member.get('observed_status') or 'unknown'}`")
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
            group_id = str(item.get("alternative_group") or "").strip()
            if group_id:
                lines.append(f"- Alternative group: `{group_id}` (`{item.get('alternative_group_status') or 'unknown'}`)")
                active = [str(x) for x in list(item.get("alternative_group_active_member_ids") or []) if str(x)]
                if active:
                    lines.append(f"- Active lane member(s): `{', '.join(active)}`")
                preferred = str(item.get("alternative_group_preferred_member_id") or "").strip()
                if preferred:
                    lines.append(f"- Preferred lane member: `{preferred}`")
                if item.get("suppressed_by_alternative"):
                    lines.append("- Effective blocker status: `covered`")
                group_note = _first_text(item, "alternative_group_note")
                if group_note:
                    lines.append(f"- Alternative note: {group_note}")
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
    alternative_groups = _trim_items(plan.get("alternative_requirement_groups"), limit=8)
    portal_route_contract = dict(plan.get("portal_route_contract") or {})
    session_issues = _trim_items(plan.get("session_issues"), limit=10)

    lines: list[str] = []
    lines.append(f"# VHK host fixups for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-host-contract-pack`. Use this when package installation was only the first step and the host still needs lifecycle, permission, or portal-routing review.")
    lines.append("")
    lines.append("## Priority summary")
    lines.append("")
    lines.append(f"- Overall host status: `{summary.get('overall_status') or 'unknown'}`")
    selected_lane = dict(plan.get("selected_evidence_lane") or {})
    lane_fit = dict(plan.get("evidence_lane_fit") or {})
    if selected_lane:
        lines.append(f"- Evidence lane: `{selected_lane.get('profile_id') or 'unknown'}` ({selected_lane.get('selection_source') or 'flagship-default'})")
    if lane_fit:
        lines.append(f"- Evidence lane fit: `{lane_fit.get('status') or 'unknown'}`")
    lines.append(f"- Effective blockers: {len(list(summary.get('effective_blockers') or []))}")
    lines.append(f"- Effective degraded units: {len(list(summary.get('effective_degraded') or []))}")
    lines.append(f"- Effective unknown units: {len(list(summary.get('effective_unknown') or []))}")
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
            alternative_lane_groups = [dict(item) for item in list(lane.get("alternative_groups") or []) if isinstance(item, dict)]
            if alternative_lane_groups:
                lines.append("- Alternative lane groups:")
                for alt_group in alternative_lane_groups:
                    active = [str(x) for x in list(alt_group.get("active_member_ids") or []) if str(x)]
                    line = f"  - `{alt_group.get('id') or ''}` → `{alt_group.get('effective_status') or 'unknown'}`"
                    if active:
                        line += f" via `{', '.join(active)}`"
                    preferred = str(alt_group.get('preferred_member_id') or '').strip()
                    if preferred and preferred not in active:
                        line += f" (preferred: `{preferred}`)"
                    bootstrap_filter = str(alt_group.get('bootstrap_filter_id') or '').strip()
                    if bootstrap_filter:
                        line += f" [bootstrap: `{bootstrap_filter}`]"
                    lines.append(line)
            for item in [dict(x) for x in list(lane.get("requirements") or []) if isinstance(x, dict)]:
                if item.get("suppressed_by_alternative"):
                    continue
                lines.append(f"- `{item.get('observed_status') or 'unknown'}` {item.get('title') or item.get('id')}")
                note = _first_text(item, "observed_note")
                if note:
                    lines.append(f"  - {note}")
                for hint in [str(x) for x in list(item.get("fixup_hints") or []) if str(x)][:3]:
                    lines.append(f"  - {hint}")
            lines.append("")

    if portal_route_contract:
        lines.append("## Portal routing review")
        lines.append("")
        lines.append(f"- Route status: `{portal_route_contract.get('status') or 'unknown'}`")
        lines.append(f"- Config status: `{portal_route_contract.get('config_status') or 'unknown'}`")
        lines.append(f"- Manifest status: `{portal_route_contract.get('manifest_status') or 'unknown'}`")
        for item in [dict(x) for x in list(portal_route_contract.get('issues') or []) if isinstance(x, dict)][:6]:
            lines.append(f"- `{item.get('severity') or 'info'}` {item.get('summary') or item.get('kind') or 'portal issue'}")
        lines.append("")

    if alternative_groups:
        lines.append("## Alternative lane review")
        lines.append("")
        for group in alternative_groups:
            lines.append(f"### {group.get('title') or group.get('id')}")
            lines.append("")
            lines.append(f"- Effective status: `{group.get('effective_status') or 'unknown'}`")
            preferred = str(group.get('preferred_member_id') or '').strip()
            if preferred:
                lines.append(f"- Preferred member: `{preferred}`")
            bootstrap_filter = str(group.get('bootstrap_filter_id') or '').strip()
            if bootstrap_filter:
                lines.append(f"- Preferred bootstrap filter: `{bootstrap_filter}`")
            note = _first_text(group, "note")
            if note:
                lines.append(f"- Note: {note}")
            for member in [dict(item) for item in list(group.get("members") or []) if isinstance(item, dict)]:
                line = f"- `{member.get('id') or ''}` → `{member.get('observed_status') or 'unknown'}`"
                member_filter = str(member.get('bootstrap_filter_id') or '').strip()
                if member_filter:
                    line += f" (`{member_filter}`)"
                lines.append(line)
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
    selected_lane = dict(plan.get("selected_evidence_lane") or {})
    profile_id = str(selected_lane.get("profile_id") or "").strip()
    lane_flag = f" --evidence-lane {profile_id}" if profile_id and str(selected_lane.get("selection_source") or "") == "explicit" else ""
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
        f'run_json plan-project.json "vhk plan-project . --json{lane_flag}"',
        'printf "+ %s\\n" "vhk gen-host-contract-pack . --force --quiet"',
        f'sh -lc "vhk gen-host-contract-pack . --force --quiet{lane_flag}" || true',
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
    evidence_lane_profile: str | None = None,
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
        evidence_lane_profile=evidence_lane_profile,
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
