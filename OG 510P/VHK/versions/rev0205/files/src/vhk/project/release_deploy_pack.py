from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

from vhk.project.loader import load_project
from vhk.project.release_lane_pack import build_release_lane_plan
from vhk.project.setup_pack import build_setup_pack_plan
from vhk.project.support_posture import summarize_support_posture
from vhk.project.target_route_pack import build_target_route_plan


def _write_if_allowed(path: Path, content: bytes | str, *, force: bool) -> None:
    if path.exists() and not force:
        raise ValueError(f"Refusing to overwrite existing file: {path}. Use --force.")
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


def _trim_items(items: list[dict[str, Any]] | None, limit: int = 10) -> list[dict[str, Any]]:
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


def _slugify(text: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", str(text or "").strip()).strip("-").lower()
    return slug or "project"


def _group_by_id(rows: list[dict[str, Any]], group_id: str) -> dict[str, Any]:
    for item in rows:
        if str(item.get("selection_group") or "") == group_id:
            return dict(item)
    return {}


def _route_by_id(rows: list[dict[str, Any]], route_id: str) -> dict[str, Any]:
    for item in rows:
        if str(item.get("id") or "") == route_id:
            return dict(item)
    return {}


def _profile_by_id(rows: list[dict[str, Any]], profile_id: str) -> dict[str, Any]:
    for item in rows:
        profile = dict(item.get("profile") or {}) if isinstance(item, Mapping) else {}
        if str(profile.get("id") or "") == profile_id:
            return dict(item)
    return {}


def _package_group_caps_for_route(route_id: str) -> set[str]:
    mapping = {
        "portal-shortcuts-route": {"global_hotkeys", "input_capture"},
        "native-trigger-route": {"global_hotkeys", "window_introspection"},
        "remapper-route": {"global_hotkeys", "pointer_injection", "text_injection"},
        "helper-input-route": {"pointer_injection", "text_injection"},
        "text-surface-route": {"text_injection"},
        "watcher-service-route": set(),
        "launcher-entrypoint": set(),
    }
    return set(mapping.get(route_id, set()))


def _lane_priority_package_groups(
    package_groups: list[dict[str, Any]],
    *,
    route_ids: list[str],
) -> list[dict[str, Any]]:
    wanted_caps: set[str] = set()
    for route_id in route_ids:
        wanted_caps.update(_package_group_caps_for_route(route_id))
    if not wanted_caps:
        return []
    return [
        dict(item)
        for item in package_groups
        if str(item.get("capability") or "") in wanted_caps
    ]


def _lane_delivery_style(trigger_route_id: str) -> str:
    if trigger_route_id == "portal-shortcuts-route":
        return "desktop-autostart"
    if trigger_route_id == "native-trigger-route":
        return "wm-bundle"
    if trigger_route_id in {"remapper-route", "helper-input-route"}:
        return "remapper-service"
    return "launcher-fallback"


def _lane_delivery_headline(title: str, deploy_style: str, trigger_route_id: str) -> str:
    family = {
        "portal-shortcuts-route": "portal-session",
        "native-trigger-route": "native-binding",
        "remapper-route": "remapper",
        "helper-input-route": "helper-daemon",
        "launcher-entrypoint": "launcher",
    }.get(trigger_route_id, trigger_route_id or "route")
    style_head = {
        "desktop-autostart": "desktop entry + XDG autostart",
        "wm-bundle": "WM bundle include",
        "remapper-service": "remapper/helper service",
        "launcher-fallback": "launcher fallback",
    }.get(deploy_style, deploy_style)
    return f"{title} ships best as `{style_head}` with a `{family}` trigger edge."


def _lane_build_root(profile_id: str) -> str:
    return f"./build/release-lanes/{profile_id}"


def _lane_launcher_id(project_name: str, profile_id: str) -> str:
    return f"vhk-{_slugify(project_name)}-{_slugify(profile_id)}-palette"


def _lane_desktop_id(project_name: str, profile_id: str) -> str:
    return f"vhk-{_slugify(project_name)}-{_slugify(profile_id)}"


def _lane_wm(profile_id: str, backend: str, desktop_family: str) -> str:
    if profile_id == "x11-desktop":
        return "i3"
    if desktop_family == "wlroots":
        return "sway"
    if backend == "wayland":
        return "sway"
    return "i3"


def _lane_artifact_subset(
    *,
    project_name: str,
    lane: Mapping[str, Any],
    deploy_style: str,
    include_text_package: bool,
) -> list[dict[str, Any]]:
    profile_id = str(lane.get("profile_id") or "target")
    backend = str(lane.get("backend") or "")
    desktop_family = str(lane.get("desktop_family") or "")
    build_root = _lane_build_root(profile_id)
    desktop_id = _lane_desktop_id(project_name, profile_id)
    launcher_id = _lane_launcher_id(project_name, profile_id)
    items: list[dict[str, Any]] = [
        {"path": "docs/VHK_PUBLIC_SUPPORT.md", "kind": "doc", "reason": "public support posture"},
        {"path": "docs/VHK_INSTALL_QUICKSTART.md", "kind": "doc", "reason": "operator quickstart"},
        {"path": "docs/VHK_RELEASE_LANES.md", "kind": "doc", "reason": "release lane classification"},
        {"path": "docs/VHK_RELEASE_DEPLOYMENT.md", "kind": "doc", "reason": "lane-native deployment guide"},
        {"path": "docs/VHK_RELEASE_INSTALL_SNIPPETS.md", "kind": "doc", "reason": "copy-ready install snippets"},
        {"path": "docs/VHK_RELEASE_DEPLOY_PLAN.json", "kind": "doc", "reason": "machine-readable deploy plan"},
        {
            "path": f"{build_root}/bin/{launcher_id}",
            "kind": "generated",
            "reason": "launcher fallback helper",
            "generator_command": f"vhk export-launcher-script . {build_root}/bin/{launcher_id} --force",
        },
    ]
    if deploy_style == "desktop-autostart":
        items.extend(
            [
                {
                    "path": f"{build_root}/applications/{desktop_id}.desktop",
                    "kind": "generated",
                    "reason": "desktop launcher entry",
                    "generator_command": f"vhk export-desktop-entry . {build_root}/applications/{desktop_id}.desktop --desktop-id {desktop_id} --force",
                },
                {
                    "path": f"{build_root}/autostart/{desktop_id}.desktop",
                    "kind": "generated",
                    "reason": "XDG autostart copy of the desktop entry",
                },
            ]
        )
    elif deploy_style == "wm-bundle":
        wm = _lane_wm(profile_id, backend, desktop_family)
        items.extend(
            [
                {
                    "path": f"{build_root}/wm-bundle/",
                    "kind": "generated",
                    "reason": f"self-contained {wm} bundle with include snippet + bootstrap note",
                    "generator_command": f"vhk export-wm-bundle . {build_root}/wm-bundle --wm {wm} --kind binding --launcher rofi-mode --force",
                },
                {
                    "path": f"{build_root}/wm-bundle/vhk-wm-bundle.json",
                    "kind": "generated",
                    "reason": f"{wm} bundle manifest",
                },
            ]
        )
    elif deploy_style == "remapper-service":
        unit_name = f"ydotoold-vhk-{_slugify(profile_id)}"
        items.extend(
            [
                {
                    "path": f"{build_root}/trigger-pack/",
                    "kind": "generated",
                    "reason": "trigger/remapper export pack",
                    "generator_command": f"vhk gen-trigger-pack . --out-dir {build_root}/trigger-pack --force --quiet",
                },
                {
                    "path": f"{build_root}/systemd/user/{unit_name}.service",
                    "kind": "generated",
                    "reason": "user service for helper daemon route",
                    "generator_command": f"vhk gen-ydotoold-service --out-dir {build_root}/systemd/user --name {unit_name}",
                },
            ]
        )
    if include_text_package:
        items.append(
            {
                "path": f"{build_root}/espanso_package/",
                "kind": "generated",
                "reason": "text-surface export package",
                "generator_command": f"vhk gen-espanso . --package-dir {build_root}/espanso_package",
            }
        )
    required_artifacts = [str(x) for x in list(lane.get("required_artifacts") or []) if str(x)]
    for path in required_artifacts:
        items.append({"path": path, "kind": "doc", "reason": "release-lane requirement"})
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for item in items:
        path = str(item.get("path") or "").strip()
        if not path or path in seen:
            continue
        seen.add(path)
        out.append(dict(item))
    return out


def _desktop_autostart_commands(project_name: str, profile_id: str) -> tuple[list[str], list[str]]:
    build_root = _lane_build_root(profile_id)
    desktop_id = _lane_desktop_id(project_name, profile_id)
    launcher_id = _lane_launcher_id(project_name, profile_id)
    commands = [
        f"mkdir -p {build_root}/bin {build_root}/applications {build_root}/autostart",
        f"vhk export-launcher-script . {build_root}/bin/{launcher_id} --force",
        f"vhk export-desktop-entry . {build_root}/applications/{desktop_id}.desktop --desktop-id {desktop_id} --force",
        f"install -Dm755 {build_root}/bin/{launcher_id} \"${{XDG_BIN_HOME:-$HOME/.local/bin}}/{launcher_id}\"",
        f"install -Dm644 {build_root}/applications/{desktop_id}.desktop \"${{XDG_DATA_HOME:-$HOME/.local/share}}/applications/{desktop_id}.desktop\"",
        f"install -Dm644 {build_root}/applications/{desktop_id}.desktop \"${{XDG_CONFIG_HOME:-$HOME/.config}}/autostart/{desktop_id}.desktop\"",
    ]
    notes = [
        "Portal shortcuts are session-bound. Launch via the desktop entry first, then bind or confirm portal shortcuts inside the running session.",
        "Keep the launcher script installed even when the portal route is the flagship path; it is the honest fallback when the shortcut session is missing.",
    ]
    return commands, notes


def _wm_bundle_commands(project_name: str, profile_id: str, backend: str, desktop_family: str) -> tuple[list[str], list[str]]:
    build_root = _lane_build_root(profile_id)
    wm = _lane_wm(profile_id, backend, desktop_family)
    launcher_id = _lane_launcher_id(project_name, profile_id)
    commands = [
        f"mkdir -p {build_root}",
        f"vhk export-launcher-script . {build_root}/bin/{launcher_id} --force",
        f"vhk export-wm-bundle . {build_root}/wm-bundle --wm {wm} --kind binding --launcher rofi-mode --force",
    ]
    notes = [
        f"Add the generated bootstrap/include line to your {wm} config instead of hand-copying snippets between releases.",
        "Treat the launcher script as the universal escape hatch even when the WM bundle is the reference trigger route.",
    ]
    return commands, notes


def _remapper_service_commands(project_name: str, profile_id: str) -> tuple[list[str], list[str]]:
    build_root = _lane_build_root(profile_id)
    unit_name = f"ydotoold-vhk-{_slugify(profile_id)}"
    launcher_id = _lane_launcher_id(project_name, profile_id)
    commands = [
        f"mkdir -p {build_root}/systemd/user {build_root}/trigger-pack {build_root}/bin",
        f"vhk export-launcher-script . {build_root}/bin/{launcher_id} --force",
        f"vhk gen-trigger-pack . --out-dir {build_root}/trigger-pack --force --quiet",
        f"vhk gen-ydotoold-service --out-dir {build_root}/systemd/user --name {unit_name}",
        f"install -Dm644 {build_root}/systemd/user/{unit_name}.service \"${{XDG_CONFIG_HOME:-$HOME/.config}}/systemd/user/{unit_name}.service\"",
        "systemctl --user daemon-reload",
        f"systemctl --user enable --now {unit_name}.service",
    ]
    notes = [
        "This lane assumes uinput permissions and a helper daemon lifecycle, so keep host-contract/readiness docs in the release artifact set.",
        "Treat remapper exports as the fast edge and the launcher script as the fallback/manual route.",
    ]
    return commands, notes


def _launcher_fallback_commands(project_name: str, profile_id: str) -> tuple[list[str], list[str]]:
    build_root = _lane_build_root(profile_id)
    launcher_id = _lane_launcher_id(project_name, profile_id)
    commands = [
        f"mkdir -p {build_root}/bin",
        f"vhk export-launcher-script . {build_root}/bin/{launcher_id} --force",
        f"install -Dm755 {build_root}/bin/{launcher_id} \"${{XDG_BIN_HOME:-$HOME/.local/bin}}/{launcher_id}\"",
    ]
    notes = [
        "Use this when the desktop/session-specific trigger route is not ready enough to be the default install story.",
    ]
    return commands, notes


def _text_surface_commands(profile_id: str) -> tuple[list[str], list[str]]:
    build_root = _lane_build_root(profile_id)
    commands = [
        f"vhk gen-espanso . --package-dir {build_root}/espanso_package",
        "espanso service register",
        "espanso start",
    ]
    notes = [
        "This follows Espanso's documented Linux service flow: package/install first, then register the service once and start it.",
    ]
    return commands, notes


def build_release_deploy_plan(
    project_dir: Path,
    *,
    target_profiles: list[str] | None = None,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
) -> dict[str, Any]:
    project_dir = project_dir.expanduser().resolve()
    project = load_project(project_dir)
    release_plan = build_release_lane_plan(
        project_dir,
        target_profiles=target_profiles,
        capability_usage=capability_usage,
    )
    target_plan = build_target_route_plan(
        project_dir,
        target_profiles=target_profiles,
        capability_usage=capability_usage,
    )
    setup_plan = build_setup_pack_plan(
        project_dir,
        capability_usage=capability_usage,
    )
    support_posture = summarize_support_posture(
        project_dir,
        prefer_cached=False,
        capability_usage=capability_usage,
        include_release_deploy=False,
    )

    package_groups = [dict(item) for item in list((setup_plan.get("toolchain_packages") or {}).get("package_groups") or []) if isinstance(item, dict)]
    lanes: list[dict[str, Any]] = []
    for lane in list(release_plan.get("release_lanes") or []):
        if not isinstance(lane, Mapping):
            continue
        lane_dict = dict(lane)
        profile_id = str(lane_dict.get("profile_id") or "")
        target_profile = _profile_by_id(list(target_plan.get("target_profiles") or []), profile_id)
        selected_groups = [dict(item) for item in list(target_profile.get("selected_groups") or []) if isinstance(item, dict)]
        activation_routes = [dict(item) for item in list(target_profile.get("activation_routes") or []) if isinstance(item, dict)]
        trigger_group = _group_by_id(selected_groups, "trigger-entry")
        text_group = _group_by_id(selected_groups, "text-entry")
        event_group = _group_by_id(selected_groups, "event-plane")
        trigger_route_id = str(trigger_group.get("primary_route_id") or "")
        text_route_id = str(text_group.get("primary_route_id") or "")
        event_route_id = str(event_group.get("primary_route_id") or "")
        deploy_style = _lane_delivery_style(trigger_route_id)
        include_text_package = text_route_id == "text-surface-route" and int((release_plan.get("target_summary") or {}).get("profile_count") or 0) >= 0 and bool(getattr(project, "hotstrings", None))
        route_ids = [route_id for route_id in [trigger_route_id, text_route_id, event_route_id] if route_id]
        priority_groups = _lane_priority_package_groups(package_groups, route_ids=route_ids)
        priority_group_ids = [str(item.get("id") or "") for item in priority_groups if str(item.get("id") or "")]
        artifact_subset = _lane_artifact_subset(
            project_name=project.name,
            lane=lane_dict,
            deploy_style=deploy_style,
            include_text_package=include_text_package,
        )
        if deploy_style == "desktop-autostart":
            install_commands, operator_notes = _desktop_autostart_commands(project.name, profile_id)
        elif deploy_style == "wm-bundle":
            install_commands, operator_notes = _wm_bundle_commands(project.name, profile_id, str(lane_dict.get("backend") or ""), str(lane_dict.get("desktop_family") or ""))
        elif deploy_style == "remapper-service":
            install_commands, operator_notes = _remapper_service_commands(project.name, profile_id)
        else:
            install_commands, operator_notes = _launcher_fallback_commands(project.name, profile_id)
        if include_text_package:
            extra_commands, extra_notes = _text_surface_commands(profile_id)
            install_commands.extend(extra_commands)
            operator_notes.extend(extra_notes)
        verify_commands = _dedupe_keep_order(
            [
                "vhk doctor --json",
                "vhk validate . --json",
                *[str(cmd) for cmd in list(lane_dict.get("operator_commands") or []) if str(cmd)],
                *[str(cmd) for route_id in route_ids for cmd in list(_route_by_id(activation_routes, route_id).get("verification_commands") or []) if str(cmd)],
            ]
        )
        deploy_lane = {
            "profile_id": profile_id,
            "title": str(lane_dict.get("title") or profile_id or "target"),
            "release_level": str(lane_dict.get("release_level") or "experimental"),
            "overall_status": str(lane_dict.get("overall_status") or "unknown"),
            "backend": str(lane_dict.get("backend") or ""),
            "desktop_family": str(lane_dict.get("desktop_family") or ""),
            "deploy_style": deploy_style,
            "delivery_headline": _lane_delivery_headline(str(lane_dict.get("title") or profile_id or "target"), deploy_style, trigger_route_id),
            "trigger_route_id": trigger_route_id,
            "text_route_id": text_route_id,
            "event_route_id": event_route_id,
            "priority_package_group_ids": priority_group_ids,
            "priority_package_groups": [
                {
                    "id": str(item.get("id") or ""),
                    "title": str(item.get("title") or item.get("id") or "group"),
                    "capability": str(item.get("capability") or ""),
                    "recommended_toolchain": str(item.get("recommended_toolchain") or ""),
                    "packages": [str(x) for x in list(item.get("packages") or []) if str(x)],
                    "install_commands": dict(item.get("install_commands") or {}),
                }
                for item in priority_groups
            ],
            "artifact_subset": artifact_subset,
            "install_commands": _dedupe_keep_order(install_commands),
            "operator_notes": _dedupe_keep_order(operator_notes),
            "verify_commands": verify_commands,
        }
        lanes.append(deploy_lane)

    lanes.sort(
        key=lambda item: (
            {"reference": 0, "supported": 1, "caveated": 2, "experimental": 3}.get(str(item.get("release_level") or "experimental"), 9),
            str(item.get("title") or ""),
        )
    )
    flagship = dict(lanes[0]) if lanes else {}
    review_commands = _dedupe_keep_order(
        [
            f"vhk gen-setup-pack {project_dir.as_posix()} --force --quiet",
            f"vhk gen-target-route-pack {project_dir.as_posix()} --force --quiet",
            f"vhk gen-release-lane-pack {project_dir.as_posix()} --force --quiet",
            f"vhk gen-release-deploy-pack {project_dir.as_posix()} --force --quiet",
        ]
    )
    return {
        "source_contract": "release_deploy_pack",
        "project": dict(release_plan.get("project") or {}),
        "support_posture": {
            "headline": str(support_posture.get("headline") or "Support posture unavailable"),
            "docs": [str(x) for x in list(support_posture.get("docs") or []) if str(x)],
        },
        "release_summary": dict(release_plan.get("release_summary") or {}),
        "deploy_summary": {
            "lane_count": len(lanes),
            "flagship_lane_id": str(flagship.get("profile_id") or ""),
            "flagship_lane_title": str(flagship.get("title") or flagship.get("profile_id") or ""),
            "flagship_release_level": str(flagship.get("release_level") or ""),
            "flagship_deploy_style": str(flagship.get("deploy_style") or ""),
            "flagship_delivery_headline": str(flagship.get("delivery_headline") or ""),
        },
        "package_bootstrap": {
            "package_count": int((setup_plan.get("toolchain_packages") or {}).get("package_count") or 0),
            "group_count": len(package_groups),
            "aggregate_install_commands": dict((setup_plan.get("toolchain_packages") or {}).get("install_commands") or {}),
        },
        "deploy_lanes": lanes,
        "review_commands": review_commands,
    }


def render_release_deployment(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    summary = dict(plan.get("deploy_summary") or {})
    support_posture = dict(plan.get("support_posture") or {})
    lanes = _trim_items(plan.get("deploy_lanes"), limit=8)
    package_bootstrap = dict(plan.get("package_bootstrap") or {})

    lines: list[str] = []
    lines.append(f"# VHK release deployment guide for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-release-deploy-pack`. This pack turns release lanes into lane-native install/autostart output: artifact subsets, copy-ready generator commands, and the host-side delivery style each desktop family should actually ship.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Release lanes modeled: {summary.get('lane_count') or 0}")
    lines.append(f"- Flagship lane: `{summary.get('flagship_lane_id') or 'none'}`")
    lines.append(f"- Flagship deploy style: `{summary.get('flagship_deploy_style') or 'unknown'}`")
    lines.append(f"- Bootstrap package groups available: {package_bootstrap.get('group_count') or 0}")
    lines.append("")
    headline = str(support_posture.get("headline") or "").strip()
    if headline:
        lines.append("## Public support posture")
        lines.append("")
        lines.append(headline)
        lines.append("")
    if lanes:
        lines.append("## Release-lane deployment choices")
        lines.append("")
        for lane in lanes:
            lines.append(f"### {lane.get('title') or lane.get('profile_id')}")
            lines.append("")
            lines.append(f"- Profile id: `{lane.get('profile_id') or ''}`")
            lines.append(f"- Release level: `{lane.get('release_level') or 'experimental'}`")
            lines.append(f"- Deploy style: `{lane.get('deploy_style') or 'unknown'}`")
            lines.append(f"- Trigger route: `{lane.get('trigger_route_id') or 'unknown'}`")
            lines.append(f"- Text route: `{lane.get('text_route_id') or 'unknown'}`")
            lines.append(f"- Event route: `{lane.get('event_route_id') or 'unknown'}`")
            lines.append(f"- Delivery headline: {lane.get('delivery_headline') or ''}")
            groups = [dict(item) for item in list(lane.get("priority_package_groups") or []) if isinstance(item, dict)]
            if groups:
                lines.append("- Priority package groups:")
                for group in groups:
                    pkgs = [str(x) for x in list(group.get("packages") or []) if str(x)]
                    lines.append(f"  - `{group.get('id') or ''}` → `{group.get('capability') or ''}` ({', '.join(pkgs) or 'no package hints'})")
            subset = [dict(item) for item in list(lane.get("artifact_subset") or []) if isinstance(item, dict)]
            if subset:
                lines.append("- Artifact subset:")
                for item in subset[:8]:
                    note = f" — {item.get('reason') or ''}" if str(item.get("reason") or "") else ""
                    lines.append(f"  - `{item.get('path') or ''}`{note}")
            notes = [str(x) for x in list(lane.get("operator_notes") or []) if str(x)]
            if notes:
                lines.append("- Notes:")
                for note in notes[:4]:
                    lines.append(f"  - {note}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_release_install_snippets(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    lanes = _trim_items(plan.get("deploy_lanes"), limit=8)

    lines: list[str] = []
    lines.append(f"# VHK release install snippets for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-release-deploy-pack`. Copy from here when you need per-desktop install/autostart snippets that match the chosen release lanes instead of freehand Linux setup notes.")
    lines.append("")
    for lane in lanes:
        lines.append(f"## {lane.get('title') or lane.get('profile_id')}")
        lines.append("")
        lines.append(f"- Deploy style: `{lane.get('deploy_style') or 'unknown'}`")
        lines.append(f"- Release level: `{lane.get('release_level') or 'experimental'}`")
        lines.append("")
        lines.append("### Install / activation snippet")
        lines.append("")
        lines.append("```sh")
        for cmd in list(lane.get("install_commands") or []):
            if str(cmd):
                lines.append(str(cmd))
        lines.append("```")
        lines.append("")
        groups = [dict(item) for item in list(lane.get("priority_package_groups") or []) if isinstance(item, dict)]
        if groups:
            lines.append("### Priority package bootstrap hints")
            lines.append("")
            for group in groups:
                lines.append(f"- `{group.get('title') or group.get('id')}`")
                for manager in ["apt", "dnf", "pacman", "zypper"]:
                    cmd = str((group.get("install_commands") or {}).get(manager) or "").strip()
                    if cmd:
                        lines.append(f"  - `{manager}`: `{cmd}`")
            lines.append("")
        lines.append("### Verification")
        lines.append("")
        for cmd in list(lane.get("verify_commands") or [])[:8]:
            lines.append(f"- `{cmd}`")
        notes = [str(x) for x in list(lane.get("operator_notes") or []) if str(x)]
        if notes:
            lines.append("")
            lines.append("### Notes")
            lines.append("")
            for note in notes[:5]:
                lines.append(f"- {note}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_release_deploy_refresh_script(plan: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("#!/usr/bin/env sh")
    lines.append("set -eu")
    lines.append("")
    lines.append('printf "%s\\n" "Collecting VHK release-deploy evidence..."')
    lines.append('printf "+ %s\\n" "vhk gen-setup-pack . --force --quiet"')
    lines.append('sh -lc "vhk gen-setup-pack . --force --quiet" || true')
    lines.append('printf "+ %s\\n" "vhk gen-target-route-pack . --force --quiet"')
    lines.append('sh -lc "vhk gen-target-route-pack . --force --quiet" || true')
    lines.append('printf "+ %s\\n" "vhk gen-release-lane-pack . --force --quiet"')
    lines.append('sh -lc "vhk gen-release-lane-pack . --force --quiet" || true')
    lines.append('printf "+ %s\\n" "vhk gen-release-deploy-pack . --force --quiet"')
    lines.append('sh -lc "vhk gen-release-deploy-pack . --force --quiet" || true')
    lines.append('printf "%s\\n" "Release-deploy refresh complete."')
    lines.append("")
    return "\n".join(lines)


def write_release_deploy_pack(
    project_dir: Path,
    *,
    out_dir: Path | None = None,
    script_dir: Path | None = None,
    force: bool = False,
    deploy_doc: bool = True,
    snippets_doc: bool = True,
    plan_json: bool = True,
    refresh_script: bool = True,
    target_profiles: list[str] | None = None,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
) -> dict[str, Path]:
    project_dir = project_dir.expanduser().resolve()
    out_dir = (out_dir or (project_dir / "docs")).expanduser().resolve()
    script_dir = (script_dir or (project_dir / "scripts")).expanduser().resolve()

    plan = build_release_deploy_plan(
        project_dir,
        target_profiles=target_profiles,
        capability_usage=capability_usage,
    )

    written: dict[str, Path] = {}
    if deploy_doc:
        path = out_dir / "VHK_RELEASE_DEPLOYMENT.md"
        _write_if_allowed(path, render_release_deployment(plan), force=force)
        written["deploy_doc"] = path
    if snippets_doc:
        path = out_dir / "VHK_RELEASE_INSTALL_SNIPPETS.md"
        _write_if_allowed(path, render_release_install_snippets(plan), force=force)
        written["snippets_doc"] = path
    if plan_json:
        path = out_dir / "VHK_RELEASE_DEPLOY_PLAN.json"
        _write_if_allowed(path, json.dumps(plan, indent=2, sort_keys=True) + "\n", force=force)
        written["plan_json"] = path
    if refresh_script:
        path = script_dir / "vhk_refresh_release_deploy.sh"
        _write_if_allowed(path, render_release_deploy_refresh_script(plan), force=force)
        path.chmod(0o755)
        written["refresh_script"] = path
    return written
