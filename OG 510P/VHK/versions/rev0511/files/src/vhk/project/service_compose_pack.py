from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any

from vhk.project.host_contract_pack import build_host_contract_plan
from vhk.project.loader import load_project
from vhk.project.native_install_pack import build_native_install_plan, write_native_install_pack
from vhk.project.readiness_pack import derive_service_unit_hints
from vhk.project.session_activation_policy import build_session_activation_policy
from vhk.project.session_target_policy import build_session_target_policy, summarize_session_target_policy
from vhk.project.session_readiness_policy import build_session_readiness_policy, summarize_session_readiness_policy
from vhk.project.startup_handoff_policy import build_startup_handoff_policy, summarize_startup_handoff_policy
from vhk.system.event_bus import get_bus_socket_path


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


def _slug(text: str) -> str:
    cleaned = "".join(ch if ch.isalnum() else "-" for ch in str(text or "").strip())
    parts = [p for p in cleaned.split("-") if p]
    return "-".join(parts) or "project"


def _compose_paths(plan: dict[str, Any]) -> dict[str, str]:
    handoff = dict(plan.get("publish_handoff") or {})
    root = str(handoff.get("root") or "build/publish/project")
    story = dict(plan.get("native_install_story") or {})
    command_name = str(story.get("command_name") or "vhk-project")
    bundle_name = str(story.get("bundle_name") or "project.zip")
    service_root = f"{root}/service"
    config_rel = f"vhk/{command_name}/session-service"
    return {
        "service_root": service_root,
        "service_manifest": f"{service_root}/vhk_service_compose_handoff.json",
        "service_readme": f"{service_root}/README.md",
        "service_refresh_script": f"{service_root}/refresh_service_compose_inputs.sh",
        "service_install_script": f"{service_root}/install_user_session.sh",
        "service_uninstall_script": f"{service_root}/uninstall_user_session.sh",
        "service_smoke_script": f"{service_root}/smoke_test_service_compose.sh",
        "service_materialize_script": f"{service_root}/materialize_bundle_root.sh",
        "service_run_script": f"{service_root}/run_bundle_busd.sh",
        "service_systemd_root": f"{service_root}/systemd-user",
        "service_autostart_root": f"{service_root}/autostart",
        "service_environment_root": f"{service_root}/environment.d",
        "service_session_activation_script": f"{service_root}/sync_session_activation_env.sh",
        "service_payload_doc_root": f"{service_root}/docs",
        "service_session_targets_doc": f"{service_root}/docs/VHK_SESSION_TARGETS.md",
        "service_target_probe_script": f"{service_root}/verify_session_targets.sh",
        "service_session_readiness_doc": f"{service_root}/docs/VHK_SESSION_READINESS.md",
        "service_readiness_probe_script": f"{service_root}/verify_session_readiness.sh",
        "service_startup_doc": f"{service_root}/docs/VHK_STARTUP_HANDOFF.md",
        "service_startup_probe_script": f"{service_root}/verify_startup_handoff.sh",
        "service_native_hint": f"${{XDG_DATA_HOME:-$HOME/.local/share}}/vhk/apps/{command_name}",
        "service_publish_bundle": f"{root}/dist/{bundle_name}",
        "service_installed_bundle": f"${{XDG_DATA_HOME:-$HOME/.local/share}}/vhk/apps/{command_name}/share/vhk/project/{bundle_name}",
        "service_config_payload_root": f"${{XDG_CONFIG_HOME:-$HOME/.config}}/{config_rel}",
        "service_systemd_configuration_directory": config_rel,
        "service_systemd_state_directory": config_rel,
        "service_systemd_cache_directory": config_rel,
    }


def _compose_constraints(
    plan: dict[str, Any],
    *,
    has_bus_watchers: bool,
    external_service_hints: list[dict[str, str]],
) -> list[str]:
    project = dict(plan.get("project") or {})
    bundle_story = dict(plan.get("bundle_release_story") or {})
    items = [
        "Treat user-service startup as a composition problem: user units, XDG autostart, service-specific environment files, and bundle materialization each solve a different part of the login/session story.",
        "Keep the generated VHK-owned service narrow: it manages the watcher/event plane and a reviewed-bundle runner, not every helper daemon or privilege boundary the desktop might still require.",
        "Do not assume graphical-session.target or xdg-desktop-autostart.target make login behavior universal; the generated autostart entry is a bridge, not proof that every desktop delegates startup the same way.",
        "Keep PATH and VHK-specific variables in environment.d for user services instead of relying on interactive-shell startup files.",
        "Run long-lived watchers from a verified bundle payload extracted into user state/cache roots rather than directly from the mutable project checkout.",
    ]
    if has_bus_watchers:
        items.append("This handoff includes a socket-activated busd lane so event-driven projects can wake the runner on demand instead of requiring a manually started terminal process.")
    else:
        items.append("This project does not declare bus watchers, so the pack focuses on environment/export scaffolding and documents the missing first-party long-lived service lane explicitly.")
    if external_service_hints:
        items.append("External helpers like ydotoold, espanso, or remappers remain adjacent services to review separately; this pack surfaces those units in docs but does not pretend VHK owns their lifecycle.")
    if str(bundle_story.get("bundle_kind") or "project") == "release-stage" and bundle_story.get("bundle_profile_id"):
        items.append(f"The session-service handoff is pinned to the `{bundle_story.get('bundle_profile_id')}` release-stage lane; refresh it whenever that staged payload or deployment story changes.")
    if str(project.get("desktop_backend") or "").strip().lower() == "wayland":
        items.append("For Wayland-first projects, keep the service pack honest about compositor/helper boundaries: user units can start helpers and watchers, but they do not erase portal consent, app-scoped shortcuts, or uinput permissions.")
    return items


def build_service_compose_plan(
    project_dir: Path,
    *,
    bundle_target_profile: str | None = None,
    app_id: str | None = None,
    runtime: str = "org.freedesktop.Platform",
    runtime_version: str = "24.08",
    sdk: str = "org.freedesktop.Sdk",
    python_cmd: str = "python",
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
    host_snapshot: dict[str, object] | None = None,
) -> dict[str, Any]:
    project_dir = project_dir.expanduser().resolve()
    plan = build_native_install_plan(
        project_dir,
        bundle_target_profile=bundle_target_profile,
        app_id=app_id,
        runtime=runtime,
        runtime_version=runtime_version,
        sdk=sdk,
        python_cmd=python_cmd,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
        host_snapshot=host_snapshot,
    )
    host_plan = build_host_contract_plan(
        project_dir,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
        host_snapshot=host_snapshot,
    )
    project_model = load_project(project_dir)
    native_story = dict(plan.get("native_install_story") or {})
    authority_policy = dict(native_story.get("authority_policy") or {})
    bundle_story = dict(plan.get("bundle_release_story") or {})
    paths = _compose_paths(plan)
    project_slug = _slug(project_model.name)
    unit_base = f"vhk-busd-{project_slug}"
    watcher_names = [str(w.name) for w in list(project_model.bus_watchers or []) if str(w.name)]
    has_bus_watchers = bool(watcher_names)
    raw_socket_path = get_bus_socket_path(Path(project_model.root_dir), configured=project_model.settings.bus_socket)
    listen_path = str(raw_socket_path)
    xdg_runtime_dir = os.environ.get("XDG_RUNTIME_DIR")
    if xdg_runtime_dir:
        xdg_runtime_dir = str(Path(xdg_runtime_dir).expanduser().resolve())
        resolved_socket = str(raw_socket_path.resolve()) if raw_socket_path.exists() else str(raw_socket_path)
        if resolved_socket.startswith(xdg_runtime_dir + os.sep):
            listen_path = "%t" + resolved_socket[len(xdg_runtime_dir) :]
    host_requirements = [dict(item) for item in list(host_plan.get("host_requirements") or []) if isinstance(item, dict)]
    external_service_hints = [
        dict(item)
        for item in derive_service_unit_hints(host_requirements)
        if str(item.get("requirement_id") or "") != "watcher-user-service"
    ]
    command_name = str(native_story.get("command_name") or "vhk-project")
    app_id_value = str(native_story.get("app_id") or "io.visualhotkey.project")
    bundle_name = str(native_story.get("bundle_name") or "project.zip")
    session_service_surface_ids = [
        surface_id
        for surface_id in [str(x) for x in list(authority_policy.get("service_candidate_surface_ids") or []) if str(x)]
        if surface_id in {"watcher-service-export", "text-package-export"}
    ]
    desktop_mediated_surface_ids = [str(x) for x in list(authority_policy.get("desktop_mediated_surface_ids") or []) if str(x)]
    adjacent_privileged_surface_ids = [str(x) for x in list(authority_policy.get("adjacent_privileged_surface_ids") or []) if str(x)]
    if adjacent_privileged_surface_ids and desktop_mediated_surface_ids:
        authority_scope = "user-session-owned-with-portal-and-adjacent-privileged-review"
    elif adjacent_privileged_surface_ids:
        authority_scope = "user-session-owned-with-adjacent-privileged-review"
    elif desktop_mediated_surface_ids:
        authority_scope = "user-session-owned-with-portal-review"
    else:
        authority_scope = "user-session-owned"

    resolved_service_mode = "socket-activated-busd" if has_bus_watchers else "environment-only"
    resolved_autostart_mode = "systemctl-bridge" if has_bus_watchers else "none"
    session_activation_policy = build_session_activation_policy(
        desktop_backend=str(plan.get("project", {}).get("desktop_backend") or "unknown"),
        service_mode=resolved_service_mode,
        authority_scope=authority_scope,
        has_bus_watchers=has_bus_watchers,
        portal_route_contract=dict(host_plan.get("portal_route_contract") or {}),
        authority_policy=authority_policy,
    )
    session_target_policy = build_session_target_policy(
        desktop_backend=str(plan.get("project", {}).get("desktop_backend") or "unknown"),
        service_mode=resolved_service_mode,
        autostart_mode=resolved_autostart_mode,
        authority_scope=authority_scope,
        has_bus_watchers=has_bus_watchers,
        unit_base=unit_base,
    )
    startup_handoff_policy = build_startup_handoff_policy(
        desktop_backend=str(plan.get("project", {}).get("desktop_backend") or "unknown"),
        service_mode=resolved_service_mode,
        autostart_mode=resolved_autostart_mode,
        authority_scope=authority_scope,
        session_target_policy=session_target_policy,
        portal_route_contract=dict(host_plan.get("portal_route_contract") or {}),
    )
    session_readiness_policy = build_session_readiness_policy(
        desktop_backend=str(plan.get("project", {}).get("desktop_backend") or "unknown"),
        service_mode=resolved_service_mode,
        authority_scope=authority_scope,
        session_target_policy=session_target_policy,
        session_activation_policy=session_activation_policy,
        authority_policy=authority_policy,
    )

    service_story = {
        "headline": "Generate a Linux-native session-service handoff that composes one VHK-owned watcher service lane with XDG autostart, environment.d scaffolding, and a reviewed-bundle runner instead of leaving login-time startup as tribal knowledge.",
        "app_id": app_id_value,
        "command_name": command_name,
        "bundle_name": bundle_name,
        "bundle_kind": str(bundle_story.get("bundle_kind") or "project"),
        "bundle_profile_id": str(bundle_story.get("bundle_profile_id") or "").strip() or None,
        "project_root": str(project_dir),
        "desktop_backend": str(plan.get("project", {}).get("desktop_backend") or "unknown"),
        "python_cmd": python_cmd,
        "service_mode": resolved_service_mode,
        "autostart_mode": resolved_autostart_mode,
        "runner_mode": "bundle-state",
        "authority_scope": authority_scope,
        "authority_policy": authority_policy,
        "session_service_surface_ids": session_service_surface_ids,
        "desktop_mediated_surface_ids": desktop_mediated_surface_ids,
        "adjacent_privileged_surface_ids": adjacent_privileged_surface_ids,
        "unit_base": unit_base,
        "watchers": watcher_names,
        "bus_socket_path": listen_path,
        "native_install_hint": paths["service_native_hint"],
        "bundle_publish_path": paths["service_publish_bundle"],
        "bundle_install_hint": paths["service_installed_bundle"],
        "systemd_directories": {
            "configuration": paths["service_systemd_configuration_directory"],
            "state": paths["service_systemd_state_directory"],
            "cache": paths["service_systemd_cache_directory"],
        },
        "environment_exports": {
            "PATH": "${HOME}/.local/bin:$PATH",
            "VHK_PROJECT_ROOT": str(project_dir),
            "VHK_NATIVE_APP_ROOT": paths["service_native_hint"],
            "VHK_BUNDLE_KIND": str(bundle_story.get("bundle_kind") or "project"),
            "VHK_BUNDLE_PROFILE": str(bundle_story.get("bundle_profile_id") or "").strip(),
            "VHK_SERVICE_RUNNER_MODE": "bundle-state",
            "VHK_SERVICE_BUNDLE_NAME": bundle_name,
            "VHK_BUNDLE_PATH": paths["service_installed_bundle"],
            "VHK_BUSD_UNIT": f"{unit_base}.{'socket' if has_bus_watchers else 'service'}",
        },
        "install_targets": {
            "systemd_user_dir": "${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user",
            "autostart_dir": "${XDG_CONFIG_HOME:-$HOME/.config}/autostart",
            "environment_dir": "${XDG_CONFIG_HOME:-$HOME/.config}/environment.d",
            "service_payload_dir": paths["service_config_payload_root"],
        },
        "external_service_hints": external_service_hints,
        "session_activation_policy": session_activation_policy,
        "session_target_policy": session_target_policy,
        "session_readiness_policy": session_readiness_policy,
        "startup_handoff_policy": startup_handoff_policy,
    }
    service_story["constraints"] = _compose_constraints(
        plan,
        has_bus_watchers=has_bus_watchers,
        external_service_hints=external_service_hints,
    )
    commands = [
        "vhk gen-native-install-pack . --force",
        "vhk gen-service-compose-pack . --force",
        f"sh {paths['service_install_script']}",
        "systemctl --user daemon-reload",
    ]
    if has_bus_watchers:
        commands.append(f"systemctl --user enable --now {unit_base}.socket")
    plan["service_compose_paths"] = paths
    plan["service_compose_story"] = service_story
    plan["service_compose_commands"] = [cmd for cmd in commands if str(cmd).strip()]
    plan["service_compose_summary"] = {
        "service_mode": service_story["service_mode"],
        "authority_scope": service_story["authority_scope"],
        "watcher_count": len(watcher_names),
        "external_service_count": len(external_service_hints),
        "activation_variable_count": len(list(session_activation_policy.get("bridge_variables") or [])),
        "session_target_policy": summarize_session_target_policy(session_target_policy),
        "session_readiness_policy": summarize_session_readiness_policy(session_readiness_policy),
        "startup_handoff_policy": summarize_startup_handoff_policy(startup_handoff_policy),
        "bundle_kind": service_story["bundle_kind"],
    }
    plan["host_truth"] = dict(host_plan.get("host_summary") or {})
    plan["portal_route_contract"] = dict(host_plan.get("portal_route_contract") or {})
    plan["service_compose_host_requirements"] = host_requirements
    plan["source_contract"] = "service_compose_pack"
    return plan


def render_service_compose_doc(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    story = dict(plan.get("service_compose_story") or {})
    paths = dict(plan.get("service_compose_paths") or {})
    host_truth = dict(plan.get("host_truth") or {})
    portal_route_contract = dict(plan.get("portal_route_contract") or {})
    host_requirements = [dict(item) for item in list(plan.get("service_compose_host_requirements") or []) if isinstance(item, dict)]
    lines = [
        f"# VHK service composition pack for {project.get('name') or 'project'}",
        "",
        "Generated by `vhk gen-service-compose-pack`. Use it to turn the reviewed native/install story into one explicit session-service handoff: user units, environment.d exports, a reviewed-bundle runner, and an XDG autostart bridge where that still helps.",
        "",
        "## Service posture",
        "",
        f"- Service mode: `{story.get('service_mode') or 'environment-only'}`",
        f"- Autostart mode: `{story.get('autostart_mode') or 'none'}`",
        f"- Runner mode: `{story.get('runner_mode') or 'bundle-state'}`",
        f"- Bundle kind: `{story.get('bundle_kind') or 'project'}`",
        f"- Command: `{story.get('command_name') or 'vhk-project'}`",
        f"- Unit base: `{story.get('unit_base') or 'vhk-busd-project'}`",
        f"- Authority scope: `{story.get('authority_scope') or 'user-session-owned'}`",
        "",
        "## Generated roots",
        "",
        f"- Service root: `{paths.get('service_root')}`",
        f"- systemd user units: `{paths.get('service_systemd_root')}`",
        f"- environment.d: `{paths.get('service_environment_root')}`",
        f"- activation sync script: `{paths.get('service_session_activation_script')}`",
        f"- session-target probe: `{paths.get('service_target_probe_script')}`",
        f"- session-readiness guide: `{paths.get('service_session_readiness_doc')}`",
        f"- session-readiness probe: `{paths.get('service_readiness_probe_script')}`",
        f"- startup handoff guide: `{paths.get('service_startup_doc')}`",
        f"- startup handoff probe: `{paths.get('service_startup_probe_script')}`",
        f"- materializer: `{paths.get('service_materialize_script')}`",
        f"- runner: `{paths.get('service_run_script')}`",
        f"- autostart: `{paths.get('service_autostart_root')}`",
        "",
    ]
    authority_policy = dict(story.get("authority_policy") or {})
    if authority_policy:
        lines.extend([
            "## Authority ownership and service scope",
            "",
            str(authority_policy.get("summary") or "Authority posture unavailable"),
            f"- Service scope: `{story.get('authority_scope') or 'user-session-owned'}`",
        ])
        for label, key in [
            ("Session-owned surfaces", "session_service_surface_ids"),
            ("Desktop-mediated surfaces", "desktop_mediated_surface_ids"),
            ("Adjacent privileged surfaces", "adjacent_privileged_surface_ids"),
            ("Review-only surfaces", "review_surface_ids"),
        ]:
            source = story if key in {"session_service_surface_ids", "desktop_mediated_surface_ids", "adjacent_privileged_surface_ids"} else authority_policy
            values = [str(x) for x in list(source.get(key) or []) if str(x)]
            if values:
                lines.append(f"- {label}: " + ', '.join(values[:8]))
        for item in [str(x) for x in list(authority_policy.get("guardrails") or []) if str(x)][:4]:
            lines.append(f"- Guardrail: {item}")
        lines.append("")
    target_policy = dict(story.get("session_target_policy") or {})
    if target_policy:
        lines.extend([
            "## Graphical session lifetime binding",
            "",
            str(target_policy.get("summary") or "Target binding policy unavailable."),
            f"- Mode: `{target_policy.get('mode') or 'unknown'}`",
            f"- Target unit: `{target_policy.get('target_unit') or 'graphical-session.target'}`",
            f"- Fallback target: `{target_policy.get('fallback_target_unit') or 'default.target'}`",
            f"- Binds to graphical session: `{str(bool(target_policy.get('binds_to_graphical_session'))).lower()}`",
        ])
        for item in [str(x) for x in list(target_policy.get("guardrails") or []) if str(x)][:4]:
            lines.append(f"- Guardrail: {item}")
        lines.append("")
    startup_policy = dict(story.get("startup_handoff_policy") or {})
    if startup_policy:
        lines.extend([
            "## Startup ownership and duplicate-start guards",
            "",
            str(startup_policy.get("summary") or "Startup handoff policy unavailable."),
            f"- Mode: `{startup_policy.get('mode') or 'unknown'}`",
            f"- Primary owner: `{startup_policy.get('primary_owner') or 'manual'}`",
        ])
        if startup_policy.get("fallback_owner"):
            lines.append(f"- Fallback owner: `{startup_policy.get('fallback_owner')}`")
        toggles = dict(startup_policy.get("install_toggles") or {})
        lines.append(f"- Default installs autostart bridge: `{str(bool(toggles.get('default_install_autostart_bridge'))).lower()}`")
        lines.append(f"- Default enables user unit: `{str(bool(toggles.get('default_enable_user_unit'))).lower()}`")
        for item in [str(x) for x in list(startup_policy.get("guardrails") or []) if str(x)][:4]:
            lines.append(f"- Guardrail: {item}")
        lines.append("")

    activation_policy = dict(story.get("session_activation_policy") or {})
    if activation_policy:
        lines.extend([
            "## Session activation environment",
            "",
            str(activation_policy.get("summary") or "Activation sync policy unavailable."),
            f"- Sync mode: `{activation_policy.get('mode') or 'unknown'}`",
            f"- Bridge variables: `{', '.join(str(x) for x in list(activation_policy.get('bridge_variables') or []) if str(x)) or 'none'}`",
            f"- Preferred command: `{activation_policy.get('preferred_command') or ''}`",
            f"- Fallback command: `{activation_policy.get('fallback_command') or ''}`",
        ])
        for item in [str(x) for x in list(activation_policy.get("guardrails") or []) if str(x)][:4]:
            lines.append(f"- Guardrail: {item}")
        lines.append("")

    readiness_policy = dict(story.get("session_readiness_policy") or {})
    if readiness_policy:
        lines.extend([
            "## Session readiness guards",
            "",
            str(readiness_policy.get("summary") or "Session readiness policy unavailable."),
            f"- Guard mode: `{readiness_policy.get('mode') or 'unknown'}`",
            f"- Required variables: `{', '.join(str(x) for x in list(readiness_policy.get('required_variables') or []) if str(x)) or 'none'}`",
            f"- Display requirement: `{readiness_policy.get('display_requirement') or 'none'}`",
            f"- Display variables: `{', '.join(str(x) for x in list(readiness_policy.get('display_any_of') or []) if str(x)) or 'none'}`",
            f"- Requires graphical-session target: `{str(bool(readiness_policy.get('require_graphical_session_target'))).lower()}`",
        ])
        for item in [str(x) for x in list(readiness_policy.get("guardrails") or []) if str(x)][:4]:
            lines.append(f"- Guardrail: {item}")
        lines.append("")

    if host_truth or portal_route_contract:
        lines.extend([
            "## Current host truth",
            "",
            f"- Host truth status: `{host_truth.get('status') or 'unknown'}`",
            f"- Observed host requirements: {host_truth.get('requirement_count') or len(host_requirements)}",
        ])
        if portal_route_contract:
            lines.append(f"- Portal route status: `{portal_route_contract.get('status') or 'unknown'}`")
            lines.append(f"- Portal manifest status: `{portal_route_contract.get('manifest_status') or 'unknown'}`")
        blockers = [item for item in host_requirements if str(item.get('observed_status') or '') not in {'ready', 'ok', 'pass'}]
        for item in blockers[:5]:
            lines.append(f"- `{item.get('id') or ''}` — `{item.get('observed_status') or 'unknown'}` — {item.get('observed_note') or item.get('why') or item.get('title') or 'review host boundary'}")
        lines.append("")
    lines.extend([
        "## Watcher plane",
        "",
    ])
    watchers = [str(x) for x in list(story.get("watchers") or []) if str(x)]
    if watchers:
        for watcher in watchers:
            lines.append(f"- `bus_watcher`: `{watcher}`")
    else:
        lines.append("- No bus watchers declared; the pack stays in environment/export mode.")
    lines.extend([
        "",
        "## Constraints",
        "",
    ])
    for item in [str(x) for x in list(story.get("constraints") or []) if str(x)]:
        lines.append(f"- {item}")
    external = [dict(x) for x in list(story.get("external_service_hints") or []) if isinstance(x, dict)]
    if external:
        lines.extend(["", "## Adjacent helper services to review", ""])
        for item in external:
            scope = str(item.get("scope") or "system")
            unit = str(item.get("unit") or "")
            title = str(item.get("title") or unit)
            lines.append(f"- `{scope}:{unit}` — {title}")
    lines.extend(["", "## Review commands", ""])
    for cmd in [str(x) for x in list(plan.get("service_compose_commands") or []) if str(x)]:
        lines.append(f"- `{cmd}`")
    lines.append("")
    return "\n".join(lines)


def render_service_compose_handoff_readme(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    story = dict(plan.get("service_compose_story") or {})
    paths = dict(plan.get("service_compose_paths") or {})
    return "\n".join(
        [
            f"# VHK service composition handoff for {project.get('name') or 'project'}",
            "",
            "Generated by `vhk gen-service-compose-pack`. This tree keeps one VHK-owned watcher service lane, one environment.d export file, one reviewed-bundle materializer/runner, and one XDG autostart bridge together so startup policy is reviewable instead of hidden in a wiki or shell history.",
            "",
            f"- Service mode: `{story.get('service_mode') or 'environment-only'}`",
            f"- Autostart mode: `{story.get('autostart_mode') or 'none'}`",
            f"- Runner mode: `{story.get('runner_mode') or 'bundle-state'}`",
            f"- Unit base: `{story.get('unit_base') or 'vhk-busd-project'}`",
            f"- Authority scope: `{story.get('authority_scope') or 'user-session-owned'}`",
            "",
            "## Generated assets",
            "",
            f"- Install script: `{paths.get('service_install_script')}`",
            f"- Uninstall script: `{paths.get('service_uninstall_script')}`",
            f"- Smoke script: `{paths.get('service_smoke_script')}`",
            f"- User units: `{paths.get('service_systemd_root')}`",
            f"- environment.d exports: `{paths.get('service_environment_root')}`",
            f"- activation sync script: `{paths.get('service_session_activation_script')}`",
            f"- session-target guide: `{paths.get('service_session_targets_doc')}`",
            f"- session-target probe: `{paths.get('service_target_probe_script')}`",
            f"- session-readiness guide: `{paths.get('service_session_readiness_doc')}`",
            f"- session-readiness probe: `{paths.get('service_readiness_probe_script')}`",
            f"- startup handoff guide: `{paths.get('service_startup_doc')}`",
            f"- startup handoff probe: `{paths.get('service_startup_probe_script')}`",
            f"- bundle materializer: `{paths.get('service_materialize_script')}`",
            f"- bundle runner: `{paths.get('service_run_script')}`",
            f"- autostart entries: `{paths.get('service_autostart_root')}`",
            "",
            "## Flow",
            "",
            "1. Refresh the lower-level native/runtime handoffs.",
            "2. Install the generated environment.d, activation-sync script, and systemd user files into XDG config roots.",
            "3. Keep one primary startup owner by default: enable the graphical-session-bound unit lane first and install the XDG autostart bridge only as an explicit fallback.",
            "4. Let the optional XDG autostart bridge sync session activation variables before it starts the user unit on desktop login.",
            "5. Use the session-readiness probe to confirm live runtime/session prerequisites before blaming restart behavior on the unit itself.",
            "6. Use the session-target and startup-handoff guides/probes to verify the lane is tied to graphical-session lifetime without duplicate startup owners.",
            "7. Review external helper daemons separately instead of pretending the VHK-owned unit is the whole Linux automation story.",
            "",
        ]
    )


def render_session_targets_doc(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    story = dict(plan.get("service_compose_story") or {})
    policy = dict(story.get("session_target_policy") or {})
    lines = [
        f"# VHK session target guide for {project.get('name') or 'project'}",
        "",
        "Generated by `vhk gen-service-compose-pack`. Use it to keep VHK-owned user units honest about whether they should follow graphical-session lifetime or merely exist as generic user services.",
        "",
        f"- Mode: `{policy.get('mode') or 'unknown'}`",
        f"- Target unit: `{policy.get('target_unit') or 'graphical-session.target'}`",
        f"- Pre-target unit: `{policy.get('pre_target_unit') or 'graphical-session-pre.target'}`",
        f"- Fallback target: `{policy.get('fallback_target_unit') or 'default.target'}`",
        f"- Binds to graphical session: `{str(bool(policy.get('binds_to_graphical_session'))).lower()}`",
        "",
    ]
    summary = str(policy.get("summary") or "").strip()
    if summary:
        lines.extend(["## Why this exists", "", summary, ""])
    guardrails = [str(x) for x in list(policy.get("guardrails") or []) if str(x)]
    if guardrails:
        lines.extend(["## Guardrails", ""])
        for item in guardrails:
            lines.append(f"- {item}")
        lines.append("")
    verification = [str(x) for x in list(policy.get("verification_commands") or []) if str(x)]
    if verification:
        lines.extend(["## Verification commands", ""])
        for item in verification:
            lines.append(f"- `{item}`")
        lines.append("")
    lines.extend([
        "## Recommended flow",
        "",
        "1. Install the generated session-service handoff.",
        "2. Let the generated autostart bridge sync session activation variables before it starts the user-owned unit/socket.",
        "3. Run the session-target probe after login to verify the lane still follows graphical-session lifetime on the target desktop.",
        "",
    ])
    return "\n".join(lines)


def render_session_readiness_doc(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    story = dict(plan.get("service_compose_story") or {})
    policy = dict(story.get("session_readiness_policy") or {})
    lines = [
        f"# VHK session readiness guide for {project.get('name') or 'project'}",
        "",
        "Generated by `vhk gen-service-compose-pack`. Use it to keep VHK-owned user units from pretending a generic login is always the same thing as a live graphical session with the variables and targets the lane actually needs.",
        "",
        f"- Guard mode: `{policy.get('mode') or 'unknown'}`",
        f"- Target unit: `{policy.get('target_unit') or 'graphical-session.target'}`",
        f"- Requires graphical-session target: `{str(bool(policy.get('require_graphical_session_target'))).lower()}`",
        f"- Required variables: `{', '.join(str(x) for x in list(policy.get('required_variables') or []) if str(x)) or 'none'}`",
        f"- Display requirement: `{policy.get('display_requirement') or 'none'}`",
        f"- Display variables: `{', '.join(str(x) for x in list(policy.get('display_any_of') or []) if str(x)) or 'none'}`",
        "",
    ]
    summary = str(policy.get("summary") or "").strip()
    if summary:
        lines.extend(["## Why this exists", "", summary, ""])
    optional_vars = [str(x) for x in list(policy.get("optional_variables") or []) if str(x)]
    if optional_vars:
        lines.extend(["## Optional variables to observe", ""])
        for item in optional_vars:
            lines.append(f"- `{item}`")
        lines.append("")
    guardrails = [str(x) for x in list(policy.get("guardrails") or []) if str(x)]
    if guardrails:
        lines.extend(["## Guardrails", ""])
        for item in guardrails:
            lines.append(f"- {item}")
        lines.append("")
    verification = [str(x) for x in list(policy.get("verification_commands") or []) if str(x)]
    if verification:
        lines.extend(["## Verification commands", ""])
        for item in verification:
            lines.append(f"- `{item}`")
        lines.append("")
    lines.extend([
        "## Recommended flow",
        "",
        "1. Install the generated session-service handoff.",
        "2. Sync session activation variables before starting the VHK-owned unit from desktop/session hooks.",
        "3. Run the readiness probe first when the service appears to start in the wrong context or churns after login.",
        "4. Treat a readiness failure as session evidence, not as proof that authority, helper privileges, or portal consent are solved.",
        "",
    ])
    return "\n".join(lines)


def render_startup_handoff_doc(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    story = dict(plan.get("service_compose_story") or {})
    policy = dict(story.get("startup_handoff_policy") or {})
    lines = [
        f"# VHK startup handoff guide for {project.get('name') or 'project'}",
        "",
        "Generated by `vhk gen-service-compose-pack`. Use it to keep exactly one primary startup owner for the VHK-owned service lane and to treat the XDG autostart bridge as an explicit fallback instead of a silent second owner.",
        "",
        f"- Mode: `{policy.get('mode') or 'unknown'}`",
        f"- Primary owner: `{policy.get('primary_owner') or 'manual'}`",
        f"- Fallback owner: `{policy.get('fallback_owner') or 'none'}`",
        f"- Current desktop: `{policy.get('current_desktop') or 'unknown'}`",
        "",
    ]
    summary = str(policy.get("summary") or "").strip()
    if summary:
        lines.extend(["## Why this exists", "", summary, ""])
    toggles = dict(policy.get("install_toggles") or {})
    if toggles:
        lines.extend([
            "## Install defaults",
            "",
            f"- Default autostart bridge install: `{str(bool(toggles.get('default_install_autostart_bridge'))).lower()}` via `{toggles.get('autostart_bridge_env') or 'VHK_INSTALL_AUTOSTART_BRIDGE'}`",
            f"- Default user-unit enable: `{str(bool(toggles.get('default_enable_user_unit'))).lower()}` via `{toggles.get('enable_user_unit_env') or 'VHK_ENABLE_USER_UNIT'}`",
            "",
        ])
    guardrails = [str(x) for x in list(policy.get("guardrails") or []) if str(x)]
    if guardrails:
        lines.extend(["## Guardrails", ""])
        for item in guardrails:
            lines.append(f"- {item}")
        lines.append("")
    verification = [str(x) for x in list(policy.get("verification_commands") or []) if str(x)]
    if verification:
        lines.extend(["## Verification commands", ""])
        for item in verification:
            lines.append(f"- `{item}`")
        lines.append("")
    lines.extend([
        "## Recommended flow",
        "",
        "1. Install the generated session-service handoff.",
        "2. Leave the graphical-session-bound systemd user unit as the default startup owner when the pack says it is primary.",
        "3. Install the XDG autostart bridge only when the target desktop/session still needs that fallback.",
        "4. Run the startup-handoff probe to catch duplicate owners before calling the lane production-ready.",
        "",
    ])
    return "\n".join(lines)


def render_session_activation_doc(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    story = dict(plan.get("service_compose_story") or {})
    policy = dict(story.get("session_activation_policy") or {})
    lines = [
        f"# VHK session activation guide for {project.get('name') or 'project'}",
        "",
        "Generated by `vhk gen-service-compose-pack`. Use it to keep the D-Bus/session-service activation environment aligned with the live graphical session before VHK-owned units start.",
        "",
        f"- Sync mode: `{policy.get('mode') or 'unknown'}`",
        f"- Authority scope: `{story.get('authority_scope') or 'user-session-owned'}`",
        f"- Service mode: `{story.get('service_mode') or 'environment-only'}`",
        f"- Preferred command: `{policy.get('preferred_command') or ''}`",
        f"- Fallback command: `{policy.get('fallback_command') or ''}`",
        "",
    ]
    summary = str(policy.get("summary") or "").strip()
    if summary:
        lines.extend(["## Why this exists", "", summary, ""])
    bridge_vars = [str(x) for x in list(policy.get("bridge_variables") or []) if str(x)]
    if bridge_vars:
        lines.extend(["## Variables to sync", ""])
        for item in bridge_vars:
            lines.append(f"- `{item}`")
        lines.append("")
    guardrails = [str(x) for x in list(policy.get("guardrails") or []) if str(x)]
    if guardrails:
        lines.extend(["## Guardrails", ""])
        for item in guardrails:
            lines.append(f"- {item}")
        lines.append("")
    lines.extend([
        "## Recommended flow",
        "",
        "1. Install the generated session-service handoff.",
        "2. Run the activation sync script from a desktop/session hook or let the generated autostart bridge call it.",
        "3. Start or restart the VHK-owned user unit after activation variables are synced.",
        "",
    ])
    return "\n".join(lines)


def render_service_compose_refresh_script(plan: dict[str, Any]) -> str:
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
        'printf "%s\\n" "Refreshing VHK service composition inputs..."',
    ]
    native = 'vhk gen-native-install-pack . --force --quiet'
    service = 'vhk gen-service-compose-pack . --force --quiet'
    if profile:
        native += f' --bundle-target-profile {profile}'
        service += f' --bundle-target-profile {profile}'
    for cmd in [native, service]:
        lines.append(f'printf "+ %s\\n" {cmd!r}')
        lines.append(f'sh -lc {cmd!r} || true')
    lines.extend([
        'printf "%s\\n" "Service composition refresh complete."',
        "",
    ])
    return "\n".join(lines)


def _shell_resolve_vhk(story: dict[str, Any]) -> list[str]:
    command_name = str(story.get("command_name") or "vhk-project")
    return [
        f'NATIVE_APP_ROOT="${{VHK_NATIVE_APP_ROOT:-${{XDG_DATA_HOME:-$HOME/.local/share}}/vhk/apps/{command_name}}}"',
        'EMBEDDED_VHK="$NATIVE_APP_ROOT/lib/vhk-runtime/bin/vhk"',
        'if [ -x "$EMBEDDED_VHK" ]; then',
        '  VHK_CMD="$EMBEDDED_VHK"',
        'elif command -v vhk >/dev/null 2>&1; then',
        '  VHK_CMD="$(command -v vhk)"',
        'else',
        '  printf "%s\n" "No embedded or system VHK runtime is available for the session-service lane." >&2',
        '  printf "%s\n" "Expected native app root: $NATIVE_APP_ROOT" >&2',
        '  exit 1',
        'fi',
    ]


def _shell_resolve_bundle(story: dict[str, Any]) -> list[str]:
    bundle_name = str(story.get("bundle_name") or "project.zip")
    command_name = str(story.get("command_name") or "vhk-project")
    publish_bundle = str(story.get("bundle_publish_path") or f"build/publish/{command_name}/dist/{bundle_name}")
    return [
        f'BUNDLE_NAME="{bundle_name}"',
        'if [ -n "${VHK_BUNDLE_PATH:-}" ] && [ -f "$VHK_BUNDLE_PATH" ]; then',
        '  BUNDLE_PATH="$VHK_BUNDLE_PATH"',
        f'elif [ -f "${{VHK_NATIVE_APP_ROOT:-${{XDG_DATA_HOME:-$HOME/.local/share}}/vhk/apps/{command_name}}}/share/vhk/project/{bundle_name}" ]; then',
        f'  BUNDLE_PATH="${{VHK_NATIVE_APP_ROOT:-${{XDG_DATA_HOME:-$HOME/.local/share}}/vhk/apps/{command_name}}}/share/vhk/project/{bundle_name}"',
        f'elif [ -f "{publish_bundle}" ]; then',
        f'  BUNDLE_PATH="{publish_bundle}"',
        'else',
        '  printf "%s\n" "Unable to locate the reviewed VHK bundle for the session-service lane." >&2',
        '  printf "%s\n" "Set VHK_BUNDLE_PATH or install the native app tree first." >&2',
        '  exit 1',
        'fi',
    ]


def _render_materialize_bundle_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("service_compose_story") or {})
    state_rel = str((story.get("systemd_directories") or {}).get("state") or "vhk/project/session-service")
    lines = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        'PYTHON_CMD="${PYTHON_CMD:-python}"',
    ]
    lines.extend(_shell_resolve_vhk(story))
    lines.extend(_shell_resolve_bundle(story))
    lines.extend([
        f'STATE_DIRECTORY="${{STATE_DIRECTORY:-${{XDG_STATE_HOME:-$HOME/.local/state}}/{state_rel}}}"',
        'TARGET_ROOT="$STATE_DIRECTORY/project"',
        'mkdir -p "$TARGET_ROOT"',
        'JSON_PAYLOAD="$($VHK_CMD materialize-bundle "$BUNDLE_PATH" "$TARGET_ROOT" --json)"',
        'printf "%s" "$JSON_PAYLOAD" > "$TARGET_ROOT/.vhk_bundle_materialized.json"',
        "PROJECT_ROOT=\"$(printf \"%s\" \"$JSON_PAYLOAD\" | \"$PYTHON_CMD\" -c 'import json,sys; print(json.load(sys.stdin)[\"project_root\"])')\"",
        'printf "%s\n" "$PROJECT_ROOT"',
        "",
    ])
    return "\n".join(lines)


def _render_run_bundle_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("service_compose_story") or {})
    lines = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        'CONFIGURATION_DIRECTORY="${CONFIGURATION_DIRECTORY:-$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)}"',
        'PROJECT_ROOT="$($CONFIGURATION_DIRECTORY/materialize_bundle_root.sh)"',
    ]
    lines.extend(_shell_resolve_vhk(story))
    args = ["$VHK_CMD", "busd", '"$PROJECT_ROOT"']
    for watcher in [str(x) for x in list(story.get("watchers") or []) if str(x)]:
        args.extend(["--watcher", watcher])
    exec_cmd = " ".join(args)
    lines.extend([
        f'exec {exec_cmd}',
        "",
    ])
    return "\n".join(lines)


def _render_busd_service(plan: dict[str, Any]) -> str:
    story = dict(plan.get("service_compose_story") or {})
    project_root = str(story.get("project_root") or ".")
    unit_base = str(story.get("unit_base") or "vhk-busd-project")
    dirs = dict(story.get("systemd_directories") or {})
    exec_cmd = "/usr/bin/env sh -lc '$CONFIGURATION_DIRECTORY/run_bundle_busd.sh'"
    target_policy = dict(story.get("session_target_policy") or {})
    lines = [
        "[Unit]",
        f"Description=VHK bus daemon ({Path(project_root).name})",
        "PartOf=graphical-session.target",
        "After=graphical-session-pre.target",
    ]
    if target_policy.get("binds_to_graphical_session"):
        lines.append("BindsTo=graphical-session.target")
    if story.get("service_mode") == "socket-activated-busd":
        lines.extend([
            f"Requires={unit_base}.socket",
            f"After={unit_base}.socket",
        ])
    lines.extend([
        "",
        "[Service]",
        "Type=simple",
        f"ConfigurationDirectory={str(dirs.get('configuration') or 'vhk/project/session-service')}",
        f"StateDirectory={str(dirs.get('state') or 'vhk/project/session-service')}",
        f"CacheDirectory={str(dirs.get('cache') or 'vhk/project/session-service')}",
        'Environment=PYTHON_CMD=${PYTHON_CMD:-python}',
        "ExecCondition=/usr/bin/env sh -lc '$CONFIGURATION_DIRECTORY/verify_session_readiness.sh'",
        f"ExecStart={exec_cmd}",
        "Restart=on-failure",
        "RestartSec=1",
        "",
        "[Install]",
        "WantedBy=default.target",
        "WantedBy=graphical-session.target",
        "",
    ])
    return "\n".join(lines)


def _render_busd_socket(plan: dict[str, Any]) -> str:
    story = dict(plan.get("service_compose_story") or {})
    target_policy = dict(story.get("session_target_policy") or {})
    unit_base = str(story.get("unit_base") or "vhk-busd-project")
    listen = str(story.get("bus_socket_path") or "%t/vhk-bus.sock")
    unit_lines = [
        "[Unit]",
        f"Description=VHK bus socket ({Path(str(story.get('project_root') or '.')).name})",
        "PartOf=graphical-session.target",
    ]
    if target_policy.get("binds_to_graphical_session"):
        unit_lines.append("BindsTo=graphical-session.target")
    unit_lines.append("")
    return "\n".join(
        unit_lines + [
            "[Socket]",
            f"ListenDatagram={listen}",
            "SocketMode=0600",
            "RemoveOnStop=yes",
            "FlushPending=yes",
            "",
            "[Install]",
            "WantedBy=sockets.target",
            "WantedBy=graphical-session.target",
            f"Also={unit_base}.service",
            "",
        ]
    )


def _render_session_activation_sync_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("service_compose_story") or {})
    policy = dict(story.get("session_activation_policy") or {})
    vars_list = [str(x) for x in list(policy.get("bridge_variables") or []) if str(x)]
    vars_joined = " ".join(vars_list)
    lines = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        "# Generated by `vhk gen-service-compose-pack`.",
        "# Keep D-Bus and systemd --user activation environments aligned with the live session.",
        f'VARS="{vars_joined}"',
        'if [ -z "$VARS" ]; then',
        '  exit 0',
        'fi',
        'if command -v dbus-update-activation-environment >/dev/null 2>&1; then',
        '  dbus-update-activation-environment --systemd $VARS >/dev/null 2>&1 || true',
        'fi',
        'if command -v systemctl >/dev/null 2>&1; then',
        '  systemctl --user import-environment $VARS >/dev/null 2>&1 || true',
        '  systemctl --user daemon-reload >/dev/null 2>&1 || true',
        'fi',
        'printf "%s\n" "Synced VHK session activation environment."',
        "",
    ]
    return "\n".join(lines)


def _render_session_target_probe_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("service_compose_story") or {})
    policy = dict(story.get("session_target_policy") or {})
    unit_base = str(story.get("unit_base") or "vhk-busd-project")
    target = str(policy.get("target_unit") or "graphical-session.target")
    lines = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        f'TARGET_UNIT="{target}"',
        f'SERVICE_UNIT="{unit_base}.service"',
        f'SOCKET_UNIT="{unit_base}.socket"',
        'if ! command -v systemctl >/dev/null 2>&1; then',
        '  printf "%s\n" "systemctl is unavailable; session-target probe skipped."',
        '  exit 0',
        'fi',
        'printf "%s\n" "== VHK session target probe =="',
        'systemctl --user is-active "$TARGET_UNIT" >/dev/null 2>&1 && printf "%s\n" "graphical-session target: active" || printf "%s\n" "graphical-session target: inactive or unknown"',
        'systemctl --user show "$SERVICE_UNIT" -p LoadState -p ActiveState -p PartOf -p BindsTo -p After 2>/dev/null || true',
        'systemctl --user show "$SOCKET_UNIT" -p LoadState -p ActiveState -p PartOf -p BindsTo 2>/dev/null || true',
        'systemctl --user list-dependencies "$TARGET_UNIT" 2>/dev/null || true',
        "",
    ]
    return "\n".join(lines)


def _render_session_readiness_probe_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("service_compose_story") or {})
    policy = dict(story.get("session_readiness_policy") or {})
    required_vars = [str(x) for x in list(policy.get("required_variables") or []) if str(x)]
    display_any_of = [str(x) for x in list(policy.get("display_any_of") or []) if str(x)]
    optional_vars = [str(x) for x in list(policy.get("optional_variables") or []) if str(x)]
    target_unit = str(policy.get("target_unit") or "graphical-session.target")
    require_target = bool(policy.get("require_graphical_session_target"))
    lines = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        "# Generated by `vhk gen-service-compose-pack`.",
        "# Probe live session/runtime prerequisites before starting the VHK-owned unit lane.",
        f'TARGET_UNIT="{target_unit}"',
        f'REQUIRE_GRAPHICAL_TARGET="{"1" if require_target else "0"}"',
        f'REQUIRED_VARS="{" ".join(required_vars)}"',
        f'DISPLAY_VARS="{" ".join(display_any_of)}"',
        f'OPTIONAL_VARS="{" ".join(optional_vars)}"',
        'get_var() { eval "printf \'%s\' \\\"\\${$1-}\\\""; }',
        'printf "%s\n" "== VHK session readiness probe =="',
        f'printf "%s\n" "mode: {policy.get("mode") or "unknown"}"',
        'if [ "$REQUIRE_GRAPHICAL_TARGET" = "1" ] && command -v systemctl >/dev/null 2>&1; then',
        '  if systemctl --user is-active "$TARGET_UNIT" >/dev/null 2>&1; then',
        '    printf "%s\n" "graphical-session target: active"',
        '  else',
        '    printf "%s\n" "graphical-session target: inactive" >&2',
        '    exit 1',
        '  fi',
        'fi',
        'for name in $REQUIRED_VARS; do',
        '  value="$(get_var "$name")"',
        '  if [ -z "$value" ]; then',
        '    printf "%s\n" "missing required session variable: $name" >&2',
        '    exit 1',
        '  fi',
        '  printf "%s\n" "$name=$value"',
        'done',
        'if [ -n "${XDG_RUNTIME_DIR:-}" ] && [ ! -d "$XDG_RUNTIME_DIR" ]; then',
        '  printf "%s\n" "XDG_RUNTIME_DIR is set but does not exist: $XDG_RUNTIME_DIR" >&2',
        '  exit 1',
        'fi',
        'if [ -n "$DISPLAY_VARS" ]; then',
        '  found_display=0',
        '  for name in $DISPLAY_VARS; do',
        '    value="$(get_var "$name")"',
        '    if [ -n "$value" ]; then',
        '      printf "%s\n" "$name=$value"',
        '      found_display=1',
        '      break',
        '    fi',
        '  done',
        '  if [ "$found_display" != "1" ]; then',
        '    printf "%s\n" "missing required display identity; checked: $DISPLAY_VARS" >&2',
        '    exit 1',
        '  fi',
        'fi',
        'for name in $OPTIONAL_VARS; do',
        '  value="$(get_var "$name")"',
        '  if [ -n "$value" ]; then',
        '    printf "%s\n" "$name=$value"',
        '  fi',
        'done',
        'printf "%s\n" "session readiness: ready"',
        "",
    ]
    return "\n".join(lines)


def _render_startup_handoff_probe_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("service_compose_story") or {})
    policy = dict(story.get("startup_handoff_policy") or {})
    unit_base = str(story.get("unit_base") or "vhk-busd-project")
    service_unit = f"{unit_base}.service"
    socket_unit = f"{unit_base}.socket"
    autostart_desktop = f"${{XDG_CONFIG_HOME:-$HOME/.config}}/autostart/{unit_base}.desktop"
    target_unit = str((story.get("session_target_policy") or {}).get("target_unit") or "graphical-session.target")
    lines = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        "# Generated by `vhk gen-service-compose-pack`.",
        "# Check whether the VHK service lane has one clear startup owner or multiple startup hooks.",
        f'TARGET_UNIT="{target_unit}"',
        f'SERVICE_UNIT="{service_unit}"',
        f'SOCKET_UNIT="{socket_unit}"',
        f'AUTOSTART_DESKTOP="{autostart_desktop}"',
        'printf "%s\n" "== VHK startup handoff probe =="',
        f'printf "%s\n" "expected mode: {policy.get("mode") or "unknown"}"',
        f'printf "%s\n" "primary owner: {policy.get("primary_owner") or "manual"}"',
        'if command -v systemctl >/dev/null 2>&1; then',
        '  systemctl --user show "$TARGET_UNIT" -p Id -p ActiveState 2>/dev/null || true',
        '  systemctl --user is-enabled "$SERVICE_UNIT" 2>/dev/null || true',
        '  systemctl --user is-enabled "$SOCKET_UNIT" 2>/dev/null || true',
        'else',
        '  printf "%s\n" "systemctl unavailable; target/unit checks skipped."',
        'fi',
        'if [ -f "$AUTOSTART_DESKTOP" ]; then',
        '  printf "%s\n" "autostart bridge: present"',
        'else',
        '  printf "%s\n" "autostart bridge: absent"',
        'fi',
        'if [ -f "$AUTOSTART_DESKTOP" ] && command -v systemctl >/dev/null 2>&1; then',
        '  if systemctl --user is-enabled "$SERVICE_UNIT" >/dev/null 2>&1 || systemctl --user is-enabled "$SOCKET_UNIT" >/dev/null 2>&1; then',
        '    printf "%s\n" "warning: both an autostart bridge and an enabled user unit are present; review duplicate-start risk."',
        '  fi',
        'fi',
        "",
    ]
    return "\n".join(lines)


def _render_env_conf(plan: dict[str, Any]) -> str:
    story = dict(plan.get("service_compose_story") or {})
    exports = dict(story.get("environment_exports") or {})
    lines = [
        "# Generated by `vhk gen-service-compose-pack`.",
        "# Passed to services started by the systemd user instance.",
    ]
    for key, value in exports.items():
        if str(value).strip() == "":
            continue
        lines.append(f"{key}={value}")
    lines.append("")
    return "\n".join(lines)


def _render_autostart_desktop(plan: dict[str, Any]) -> str:
    story = dict(plan.get("service_compose_story") or {})
    unit_base = str(story.get("unit_base") or "vhk-busd-project")
    unit_name = f"{unit_base}.socket" if story.get("service_mode") == "socket-activated-busd" else f"{unit_base}.service"
    name = f"VHK session services for {Path(str(story.get('project_root') or '.')).name}"
    config_rel = str((story.get("systemd_directories") or {}).get("configuration") or f"vhk/{story.get('command_name') or 'vhk-project'}/session-service")
    exec_line = (
        "/usr/bin/env sh -lc '"
        "XDG_CONFIG_HOME=\"${XDG_CONFIG_HOME:-$HOME/.config}\"; "
        f"SERVICE_PAYLOAD_DIR=\"$XDG_CONFIG_HOME/{config_rel}\"; "
        "if [ -x \"$SERVICE_PAYLOAD_DIR/sync_session_activation_env.sh\" ]; then \"$SERVICE_PAYLOAD_DIR/sync_session_activation_env.sh\" >/dev/null 2>&1 || true; fi; "
        "if [ -x \"$SERVICE_PAYLOAD_DIR/verify_session_readiness.sh\" ]; then \"$SERVICE_PAYLOAD_DIR/verify_session_readiness.sh\" >/dev/null 2>&1 || exit 0; fi; "
        f"systemctl --user start {unit_name} >/dev/null 2>&1 || true'"
    )
    return "\n".join(
        [
            "[Desktop Entry]",
            "Type=Application",
            "Version=1.0",
            f"Name={name}",
            "Comment=Start VHK-owned session services through the user service manager",
            f"Exec={exec_line}",
            "TryExec=systemctl",
            "Terminal=false",
            "NoDisplay=true",
            "X-GNOME-Autostart-enabled=true",
            "",
        ]
    )


def _render_install_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("service_compose_story") or {})
    startup_policy = dict(story.get("startup_handoff_policy") or {})
    toggles = dict(startup_policy.get("install_toggles") or {})
    unit_base = str(story.get("unit_base") or "vhk-busd-project")
    command_name = str(story.get("command_name") or "vhk-project")
    service_mode = str(story.get("service_mode") or "environment-only")
    autostart_mode = str(story.get("autostart_mode") or "none")
    config_rel = str((story.get("systemd_directories") or {}).get("configuration") or f"vhk/{command_name}/session-service")
    default_install_autostart = "1" if bool(toggles.get("default_install_autostart_bridge")) else "0"
    default_enable_user_unit = "1" if bool(toggles.get("default_enable_user_unit")) else "0"
    lines = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        'SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"',
        'XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"',
        'SYSTEMD_USER_DIR="$XDG_CONFIG_HOME/systemd/user"',
        'AUTOSTART_DIR="$XDG_CONFIG_HOME/autostart"',
        'ENV_DIR="$XDG_CONFIG_HOME/environment.d"',
        f'SERVICE_PAYLOAD_DIR="$XDG_CONFIG_HOME/{config_rel}"',
        f'INSTALL_AUTOSTART_BRIDGE="${{{toggles.get("autostart_bridge_env") or "VHK_INSTALL_AUTOSTART_BRIDGE"}:-{default_install_autostart}}}"',
        f'ENABLE_USER_UNIT="${{{toggles.get("enable_user_unit_env") or "VHK_ENABLE_USER_UNIT"}:-{default_enable_user_unit}}}"',
        'mkdir -p "$SYSTEMD_USER_DIR" "$AUTOSTART_DIR" "$ENV_DIR" "$SERVICE_PAYLOAD_DIR"',
        f'cp "$SCRIPT_DIR/environment.d/80-vhk-{command_name}.conf" "$ENV_DIR/80-vhk-{command_name}.conf"',
        'cp "$SCRIPT_DIR/materialize_bundle_root.sh" "$SERVICE_PAYLOAD_DIR/materialize_bundle_root.sh"',
        'cp "$SCRIPT_DIR/run_bundle_busd.sh" "$SERVICE_PAYLOAD_DIR/run_bundle_busd.sh"',
        'cp "$SCRIPT_DIR/sync_session_activation_env.sh" "$SERVICE_PAYLOAD_DIR/sync_session_activation_env.sh"',
        'cp "$SCRIPT_DIR/verify_session_readiness.sh" "$SERVICE_PAYLOAD_DIR/verify_session_readiness.sh"',
        'cp "$SCRIPT_DIR/verify_session_targets.sh" "$SERVICE_PAYLOAD_DIR/verify_session_targets.sh"',
        'cp "$SCRIPT_DIR/verify_startup_handoff.sh" "$SERVICE_PAYLOAD_DIR/verify_startup_handoff.sh"',
        'chmod 755 "$SERVICE_PAYLOAD_DIR/materialize_bundle_root.sh" "$SERVICE_PAYLOAD_DIR/run_bundle_busd.sh" "$SERVICE_PAYLOAD_DIR/sync_session_activation_env.sh" "$SERVICE_PAYLOAD_DIR/verify_session_readiness.sh" "$SERVICE_PAYLOAD_DIR/verify_session_targets.sh" "$SERVICE_PAYLOAD_DIR/verify_startup_handoff.sh"',
    ]
    if service_mode == "socket-activated-busd":
        lines.extend([
            f'cp "$SCRIPT_DIR/systemd-user/{unit_base}.service" "$SYSTEMD_USER_DIR/{unit_base}.service"',
            f'cp "$SCRIPT_DIR/systemd-user/{unit_base}.socket" "$SYSTEMD_USER_DIR/{unit_base}.socket"',
        ])
    elif service_mode != "environment-only":
        lines.append(f'cp "$SCRIPT_DIR/systemd-user/{unit_base}.service" "$SYSTEMD_USER_DIR/{unit_base}.service"')
    if autostart_mode != "none":
        lines.extend([
            'if [ "$INSTALL_AUTOSTART_BRIDGE" = "1" ]; then',
            f'  cp "$SCRIPT_DIR/autostart/{unit_base}.desktop" "$AUTOSTART_DIR/{unit_base}.desktop"',
            'else',
            f'  rm -f "$AUTOSTART_DIR/{unit_base}.desktop"',
            'fi',
        ])
    lines.extend([
        'if [ "${VHK_SKIP_SYSTEMCTL:-0}" != "1" ] && command -v systemctl >/dev/null 2>&1; then',
        '  systemctl --user daemon-reload || true',
    ])
    if service_mode == "socket-activated-busd":
        lines.extend([
            '  if [ "$ENABLE_USER_UNIT" = "1" ]; then',
            f'    systemctl --user enable --now {unit_base}.socket || true',
            '  fi',
        ])
    elif service_mode != "environment-only":
        lines.extend([
            '  if [ "$ENABLE_USER_UNIT" = "1" ]; then',
            f'    systemctl --user enable --now {unit_base}.service || true',
            '  fi',
        ])
    lines.extend([
        'fi',
        'printf "%s\n" "Installed VHK session-service composition artifacts."',
        'printf "%s\n" "Config root: $XDG_CONFIG_HOME"',
        'printf "%s\n" "Service payload dir: $SERVICE_PAYLOAD_DIR"',
        'printf "%s\n" "Autostart bridge installed: $INSTALL_AUTOSTART_BRIDGE"',
        'printf "%s\n" "User unit enabled: $ENABLE_USER_UNIT"',
        "",
    ])
    return "\n".join(lines)


def _render_uninstall_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("service_compose_story") or {})
    unit_base = str(story.get("unit_base") or "vhk-busd-project")
    command_name = str(story.get("command_name") or "vhk-project")
    service_mode = str(story.get("service_mode") or "environment-only")
    autostart_mode = str(story.get("autostart_mode") or "none")
    config_rel = str((story.get("systemd_directories") or {}).get("configuration") or f"vhk/{command_name}/session-service")
    lines = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        'XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"',
        'SYSTEMD_USER_DIR="$XDG_CONFIG_HOME/systemd/user"',
        'AUTOSTART_DIR="$XDG_CONFIG_HOME/autostart"',
        'ENV_DIR="$XDG_CONFIG_HOME/environment.d"',
        f'SERVICE_PAYLOAD_DIR="$XDG_CONFIG_HOME/{config_rel}"',
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
        '  systemctl --user daemon-reload || true',
        'fi',
        f'rm -f "$ENV_DIR/80-vhk-{command_name}.conf"',
        'rm -rf "$SERVICE_PAYLOAD_DIR"',
    ])
    if service_mode == "socket-activated-busd":
        lines.extend([
            f'rm -f "$SYSTEMD_USER_DIR/{unit_base}.service"',
            f'rm -f "$SYSTEMD_USER_DIR/{unit_base}.socket"',
        ])
    elif service_mode != "environment-only":
        lines.append(f'rm -f "$SYSTEMD_USER_DIR/{unit_base}.service"')
    if autostart_mode != "none":
        lines.append(f'rm -f "$AUTOSTART_DIR/{unit_base}.desktop"')
    lines.extend([
        'printf "%s\n" "Removed VHK session-service composition artifacts."',
        "",
    ])
    return "\n".join(lines)


def _render_smoke_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("service_compose_story") or {})
    startup_policy = dict(story.get("startup_handoff_policy") or {})
    toggles = dict(startup_policy.get("install_toggles") or {})
    unit_base = str(story.get("unit_base") or "vhk-busd-project")
    command_name = str(story.get("command_name") or "vhk-project")
    service_mode = str(story.get("service_mode") or "environment-only")
    autostart_mode = str(story.get("autostart_mode") or "none")
    config_rel = str((story.get("systemd_directories") or {}).get("configuration") or f"vhk/{command_name}/session-service")
    default_install_autostart = "1" if bool(toggles.get("default_install_autostart_bridge")) else "0"
    env_name = str(toggles.get("autostart_bridge_env") or "VHK_INSTALL_AUTOSTART_BRIDGE")
    lines = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        'SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"',
        'SMOKE_ROOT="$SCRIPT_DIR/.smoke-root"',
        'rm -rf "$SMOKE_ROOT"',
        'mkdir -p "$SMOKE_ROOT/home" "$SMOKE_ROOT/config" "$SMOKE_ROOT/data"',
        'HOME="$SMOKE_ROOT/home" XDG_CONFIG_HOME="$SMOKE_ROOT/config" XDG_DATA_HOME="$SMOKE_ROOT/data" VHK_SKIP_SYSTEMCTL=1 sh "$SCRIPT_DIR/install_user_session.sh"',
        f'test -f "$SMOKE_ROOT/config/environment.d/80-vhk-{command_name}.conf"',
        f'test -x "$SMOKE_ROOT/config/{config_rel}/materialize_bundle_root.sh"',
        f'test -x "$SMOKE_ROOT/config/{config_rel}/run_bundle_busd.sh"',
        f'test -x "$SMOKE_ROOT/config/{config_rel}/sync_session_activation_env.sh"',
        f'test -x "$SMOKE_ROOT/config/{config_rel}/verify_session_readiness.sh"',
        f'test -x "$SMOKE_ROOT/config/{config_rel}/verify_session_targets.sh"',
        f'test -x "$SMOKE_ROOT/config/{config_rel}/verify_startup_handoff.sh"',
    ]
    if service_mode == "socket-activated-busd":
        lines.extend([
            f'test -f "$SMOKE_ROOT/config/systemd/user/{unit_base}.service"',
            f'test -f "$SMOKE_ROOT/config/systemd/user/{unit_base}.socket"',
            f'grep -q "ConfigurationDirectory=" "$SMOKE_ROOT/config/systemd/user/{unit_base}.service"',
            f'grep -q "ExecCondition=/usr/bin/env sh -lc \'$CONFIGURATION_DIRECTORY/verify_session_readiness.sh\'" "$SMOKE_ROOT/config/systemd/user/{unit_base}.service"',
            f'grep -q "BindsTo=graphical-session.target" "$SMOKE_ROOT/config/systemd/user/{unit_base}.service"',
            f'grep -q "StateDirectory=" "$SMOKE_ROOT/config/systemd/user/{unit_base}.service"',
            f'grep -q "run_bundle_busd.sh" "$SMOKE_ROOT/config/systemd/user/{unit_base}.service"',
            f'grep -q "ListenDatagram=" "$SMOKE_ROOT/config/systemd/user/{unit_base}.socket"',
            f'grep -q "BindsTo=graphical-session.target" "$SMOKE_ROOT/config/systemd/user/{unit_base}.socket"',
        ])
    if autostart_mode != "none":
        if default_install_autostart == "1":
            lines.extend([
                f'test -f "$SMOKE_ROOT/config/autostart/{unit_base}.desktop"',
                f'grep -q "sync_session_activation_env.sh" "$SMOKE_ROOT/config/autostart/{unit_base}.desktop"',
                f'grep -q "verify_session_readiness.sh" "$SMOKE_ROOT/config/autostart/{unit_base}.desktop"',
                f'grep -q "systemctl --user start {unit_base}.socket" "$SMOKE_ROOT/config/autostart/{unit_base}.desktop"',
            ])
        else:
            lines.append(f'test ! -e "$SMOKE_ROOT/config/autostart/{unit_base}.desktop"')
            lines.append(f'HOME="$SMOKE_ROOT/home" XDG_CONFIG_HOME="$SMOKE_ROOT/config" XDG_DATA_HOME="$SMOKE_ROOT/data" VHK_SKIP_SYSTEMCTL=1 {env_name}=1 sh "$SCRIPT_DIR/install_user_session.sh"')
            lines.extend([
                f'test -f "$SMOKE_ROOT/config/autostart/{unit_base}.desktop"',
                f'grep -q "sync_session_activation_env.sh" "$SMOKE_ROOT/config/autostart/{unit_base}.desktop"',
                f'grep -q "verify_session_readiness.sh" "$SMOKE_ROOT/config/autostart/{unit_base}.desktop"',
                f'grep -q "systemctl --user start {unit_base}.socket" "$SMOKE_ROOT/config/autostart/{unit_base}.desktop"',
            ])
    lines.extend([
        'HOME="$SMOKE_ROOT/home" XDG_CONFIG_HOME="$SMOKE_ROOT/config" XDG_DATA_HOME="$SMOKE_ROOT/data" VHK_SKIP_SYSTEMCTL=1 sh "$SCRIPT_DIR/uninstall_user_session.sh"',
        f'test ! -e "$SMOKE_ROOT/config/environment.d/80-vhk-{command_name}.conf"',
        f'test ! -e "$SMOKE_ROOT/config/{config_rel}"',
        'printf "%s\n" "Service composition smoke test completed."',
        "",
    ])
    return "\n".join(lines)


def _materialize_service_compose_handoff(project_dir: Path, plan: dict[str, Any], *, build_dir: Path, force: bool) -> dict[str, Path]:
    root = build_dir / "service"
    paths = dict(plan.get("service_compose_paths") or {})
    story = dict(plan.get("service_compose_story") or {})
    command_name = str(story.get("command_name") or "vhk-project")
    unit_base = str(story.get("unit_base") or "vhk-busd-project")
    service_mode = str(story.get("service_mode") or "environment-only")
    autostart_mode = str(story.get("autostart_mode") or "none")

    systemd_root = root / "systemd-user"
    autostart_root = root / "autostart"
    env_root = root / "environment.d"
    docs_root = root / "docs"
    systemd_root.mkdir(parents=True, exist_ok=True)
    autostart_root.mkdir(parents=True, exist_ok=True)
    env_root.mkdir(parents=True, exist_ok=True)
    docs_root.mkdir(parents=True, exist_ok=True)

    _write_if_allowed(root / "README.md", render_service_compose_handoff_readme(plan), force=force)
    manifest_payload = {
        "project_root": str(project_dir),
        **paths,
        **story,
    }
    _write_if_allowed(root / "vhk_service_compose_handoff.json", json.dumps(manifest_payload, indent=2, sort_keys=True) + "\n", force=force)

    refresh_script = root / "refresh_service_compose_inputs.sh"
    install_script = root / "install_user_session.sh"
    uninstall_script = root / "uninstall_user_session.sh"
    smoke_script = root / "smoke_test_service_compose.sh"
    materialize_script = root / "materialize_bundle_root.sh"
    run_script = root / "run_bundle_busd.sh"
    sync_script = root / "sync_session_activation_env.sh"
    readiness_probe_script = root / "verify_session_readiness.sh"
    target_probe_script = root / "verify_session_targets.sh"
    startup_probe_script = root / "verify_startup_handoff.sh"
    env_path = env_root / f"80-vhk-{command_name}.conf"

    _write_if_allowed(refresh_script, render_service_compose_refresh_script(plan), force=force)
    _write_if_allowed(install_script, _render_install_script(plan), force=force)
    _write_if_allowed(uninstall_script, _render_uninstall_script(plan), force=force)
    _write_if_allowed(smoke_script, _render_smoke_script(plan), force=force)
    _write_if_allowed(materialize_script, _render_materialize_bundle_script(plan), force=force)
    _write_if_allowed(run_script, _render_run_bundle_script(plan), force=force)
    _write_if_allowed(sync_script, _render_session_activation_sync_script(plan), force=force)
    _write_if_allowed(readiness_probe_script, _render_session_readiness_probe_script(plan), force=force)
    _write_if_allowed(target_probe_script, _render_session_target_probe_script(plan), force=force)
    _write_if_allowed(startup_probe_script, _render_startup_handoff_probe_script(plan), force=force)
    _write_if_allowed(env_path, _render_env_conf(plan), force=force)

    busd_service_path: Path | None = None
    busd_socket_path: Path | None = None
    autostart_path: Path | None = None
    if service_mode == "socket-activated-busd":
        busd_service_path = systemd_root / f"{unit_base}.service"
        busd_socket_path = systemd_root / f"{unit_base}.socket"
        _write_if_allowed(busd_service_path, _render_busd_service(plan), force=force)
        _write_if_allowed(busd_socket_path, _render_busd_socket(plan), force=force)
    if autostart_mode != "none":
        autostart_path = autostart_root / f"{unit_base}.desktop"
        _write_if_allowed(autostart_path, _render_autostart_desktop(plan), force=force)

    for path in [refresh_script, install_script, uninstall_script, smoke_script, materialize_script, run_script, sync_script, readiness_probe_script, target_probe_script, startup_probe_script]:
        path.chmod(0o755)

    copied_docs: list[str] = []
    for rel in [
        "docs/VHK_AUTHORITY_OVERVIEW.md",
        "docs/VHK_PUBLIC_SUPPORT.md",
        "docs/VHK_INSTALL_QUICKSTART.md",
        "docs/VHK_DISTRIBUTION.md",
        "docs/VHK_RUNTIME.md",
        "docs/VHK_RUNTIME_EMBED.md",
        "docs/VHK_NATIVE_INSTALL.md",
        "docs/VHK_SERVICE_COMPOSE.md",
        "docs/VHK_SESSION_ACTIVATION.md",
        "docs/VHK_SESSION_READINESS.md",
        "docs/VHK_SESSION_TARGETS.md",
        "docs/VHK_STARTUP_HANDOFF.md",
        "docs/VHK_HOST_REQUIREMENTS.md",
        "docs/VHK_HOST_FIXUPS.md",
    ]:
        if _copy_if_present(project_dir / rel, docs_root / Path(rel).name):
            copied_docs.append(rel)

    out = {
        "service_root": root,
        "service_manifest": root / "vhk_service_compose_handoff.json",
        "service_readme": root / "README.md",
        "service_refresh_script": refresh_script,
        "service_install_script": install_script,
        "service_uninstall_script": uninstall_script,
        "service_smoke_script": smoke_script,
        "service_materialize_script": materialize_script,
        "service_run_script": run_script,
        "service_sync_script": sync_script,
        "service_readiness_probe_script": readiness_probe_script,
        "service_target_probe_script": target_probe_script,
        "service_startup_probe_script": startup_probe_script,
        "service_env_file": env_path,
    }
    if busd_service_path:
        out["service_busd_service"] = busd_service_path
    if busd_socket_path:
        out["service_busd_socket"] = busd_socket_path
    if autostart_path:
        out["service_autostart"] = autostart_path
    return out


def write_service_compose_pack(
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
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
    host_snapshot: dict[str, object] | None = None,
    force: bool = False,
    service_doc: bool = True,
    plan_json: bool = True,
    script: bool = True,
) -> dict[str, Path]:
    project_dir = project_dir.expanduser().resolve()
    out_dir = (out_dir or (project_dir / "docs")).expanduser().resolve()
    script_dir = (script_dir or (project_dir / "scripts")).expanduser().resolve()

    write_native_install_pack(
        project_dir,
        out_dir=out_dir,
        script_dir=script_dir,
        bundle_target_profile=bundle_target_profile,
        app_id=app_id,
        runtime=runtime,
        runtime_version=runtime_version,
        sdk=sdk,
        python_cmd=python_cmd,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
        host_snapshot=host_snapshot,
        force=force,
        native_doc=True,
        plan_json=True,
        script=True,
    )
    plan = build_service_compose_plan(
        project_dir,
        bundle_target_profile=bundle_target_profile,
        app_id=app_id,
        runtime=runtime,
        runtime_version=runtime_version,
        sdk=sdk,
        python_cmd=python_cmd,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
        host_snapshot=host_snapshot,
    )
    written: dict[str, Path] = {}
    if service_doc:
        path = out_dir / "VHK_SERVICE_COMPOSE.md"
        _write_if_allowed(path, render_service_compose_doc(plan), force=force)
        written["service_doc"] = path
        activation_doc = out_dir / "VHK_SESSION_ACTIVATION.md"
        _write_if_allowed(activation_doc, render_session_activation_doc(plan), force=force)
        written["session_activation_doc"] = activation_doc
        readiness_doc = out_dir / "VHK_SESSION_READINESS.md"
        _write_if_allowed(readiness_doc, render_session_readiness_doc(plan), force=force)
        written["session_readiness_doc"] = readiness_doc
        target_doc = out_dir / "VHK_SESSION_TARGETS.md"
        _write_if_allowed(target_doc, render_session_targets_doc(plan), force=force)
        written["session_targets_doc"] = target_doc
        startup_doc = out_dir / "VHK_STARTUP_HANDOFF.md"
        _write_if_allowed(startup_doc, render_startup_handoff_doc(plan), force=force)
        written["startup_handoff_doc"] = startup_doc
    if plan_json:
        path = out_dir / "VHK_SERVICE_COMPOSE_PLAN.json"
        _write_if_allowed(path, json.dumps(plan, indent=2, sort_keys=True) + "\n", force=force)
        written["plan_json"] = path
    if script:
        path = script_dir / "vhk_refresh_service_compose_pack.sh"
        _write_if_allowed(path, render_service_compose_refresh_script(plan), force=force)
        path.chmod(0o755)
        written["script"] = path

    publish_root = project_dir / str((plan.get("publish_handoff") or {}).get("root") or "build/publish/project")
    written.update(_materialize_service_compose_handoff(project_dir, plan, build_dir=publish_root, force=force))
    return written
