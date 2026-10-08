from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

from vhk.project.desktop_entry import desktop_exec_join
from vhk.project.distribution_pack import _ONE_PIXEL_PNG, _render_metainfo_xml
from vhk.project.loader import load_project
from vhk.project.palette import build_palette_entries
from vhk.project.runtime_embed_pack import build_runtime_embed_plan, write_runtime_embed_pack
from vhk.project.support_posture import render_support_about_text, summarize_support_posture


def _write_if_allowed(path: Path, content: bytes | str, *, force: bool) -> None:
    if path.exists() and not force:
        raise ValueError(f"Refusing to overwrite existing file: {path}. Use --force.")
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content)


def _copy_if_present(src: Path, dest: Path) -> bool:
    if not src.is_file():
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return True


def _desktop_escape_value(value: str) -> str:
    return str(value).replace("\\", "\\\\").replace("\n", "\\n")


def _slug(text: str) -> str:
    cleaned = "".join(ch if ch.isalnum() else "-" for ch in str(text or "").strip())
    parts = [p for p in cleaned.split("-") if p]
    return "-".join(parts) or "project"


def _native_action_id(seed: str, seen: set[str]) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9-]+", "-", str(seed or "").strip()).strip("-") or "Action"
    if cleaned[:1].isdigit():
        cleaned = f"A-{cleaned}"
    base = cleaned[:48] or "Action"
    candidate = base
    idx = 2
    while candidate in seen:
        suffix = f"-{idx}"
        candidate = (base[: max(1, 48 - len(suffix))] + suffix).strip("-")
        idx += 1
    seen.add(candidate)
    return candidate


def _native_quick_actions(project_dir: Path, *, max_actions: int = 4) -> list[dict[str, str | None]]:
    project = load_project(project_dir)
    entries = build_palette_entries(
        project,
        include_hidden=False,
        include_presets=True,
        include_profile_actions=True,
        include_profile_management_actions=False,
        recent_first=True,
        history_limit=50,
    )
    seen: set[str] = set()
    actions: list[dict[str, str | None]] = []
    for entry in entries:
        if entry.action != "run":
            continue
        target = entry.macro
        if entry.preset:
            target += f" [{entry.preset}]"
        if entry.prompt_profile:
            target += f" ‹{entry.prompt_profile}›"
        actions.append(
            {
                "id": _native_action_id(entry.entry_id.replace("@", "-").replace("#", "-").replace("!", "-"), seen),
                "name": f"Run {target}",
                "exec": desktop_exec_join(["__VHK_LAUNCHER_EXEC__", "--entry-id", entry.entry_id]),
                "icon": entry.icon or None,
            }
        )
        if max_actions and len(actions) >= max_actions:
            break
    return actions


def _native_doc_specs() -> list[tuple[str, str, str]]:
    return [
        ("home", "VHK_APP_HOME.md", "App home"),
        ("support", "VHK_PUBLIC_SUPPORT.md", "Support guide"),
        ("install", "VHK_INSTALL_QUICKSTART.md", "Install quickstart"),
        ("native", "VHK_NATIVE_INSTALL.md", "Native install notes"),
        ("distribution", "VHK_DISTRIBUTION.md", "Distribution handoff"),
        ("runtime", "VHK_RUNTIME.md", "Runtime handoff"),
        ("runtime-embed", "VHK_RUNTIME_EMBED.md", "Runtime embedding notes"),
        ("service", "VHK_SERVICE_COMPOSE.md", "Session service notes"),
        ("rehearsal", "VHK_HOST_REHEARSAL.md", "Host rehearsal guide"),
    ]


def _native_doc_filename(kind: str) -> str | None:
    wanted = str(kind or '').strip().lower()
    if wanted == 'home-json':
        return 'VHK_APP_HOME.json'
    for key, filename, _title in _native_doc_specs():
        if key == wanted:
            return filename
    return None


def _native_service_hints(project_dir: Path) -> dict[str, Any]:
    project = load_project(project_dir)
    watchers = [str(w.name) for w in list(project.bus_watchers or []) if str(w.name)]
    unit_base = f"vhk-busd-{_slug(project.name)}"
    expected_units: list[str] = []
    if watchers:
        expected_units = [f"{unit_base}.socket", f"{unit_base}.service"]
    return {
        'mode': 'socket-activated-busd' if watchers else 'environment-only',
        'watchers': watchers,
        'unit_base': unit_base,
        'expected_units': expected_units,
        'guide_doc_kind': 'service',
        'rehearsal_doc_kind': 'rehearsal',
    }


def _native_home_payload(project_dir: Path, plan: dict[str, Any], *, max_entries: int = 8) -> dict[str, Any]:
    story = dict(plan.get('native_install_story') or {})
    support_posture = summarize_support_posture(project_dir)
    support_about = render_support_about_text(support_posture)
    project = load_project(project_dir)
    service_hints = dict(story.get('service_hints') or _native_service_hints(project_dir))
    entries = build_palette_entries(
        project,
        include_hidden=False,
        include_presets=True,
        include_profile_actions=True,
        include_profile_management_actions=False,
        recent_first=True,
        history_limit=50,
    )
    top_entries: list[dict[str, Any]] = []
    for entry in entries:
        if entry.action != 'run':
            continue
        top_entries.append(
            {
                'entry_id': entry.entry_id,
                'label': entry.label,
                'group': entry.group,
                'icon': entry.icon,
                'recent_runs': entry.recent_runs,
                'needs_prompt': entry.needs_prompt,
                'hotkeys': list(entry.hotkeys),
                'hotstrings': list(entry.hotstrings),
                'tags': list(entry.tags),
            }
        )
        if max_entries and len(top_entries) >= max_entries:
            break
    xdg_defaults = dict(story.get('xdg_defaults') or {})
    doc_specs = [
        {'kind': kind, 'file': filename, 'title': title}
        for kind, filename, title in _native_doc_specs()
    ]
    return {
        'project': {
            'name': str((plan.get('project') or {}).get('name') or project.name),
            'root_dir': str(project.root_dir),
            'desktop_backend': str((plan.get('project') or {}).get('desktop_backend') or project.settings.desktop_backend or 'unknown'),
        },
        'native_install': {
            'app_id': str(story.get('app_id') or 'io.visualhotkey.project'),
            'command_name': str(story.get('command_name') or 'vhk-project'),
            'bundle_name': str(story.get('bundle_name') or 'project.zip'),
            'bundle_kind': str(story.get('bundle_kind') or 'project'),
            'bundle_profile_id': str(story.get('bundle_profile_id') or '').strip() or None,
            'default_entrypoint': str(story.get('default_entrypoint') or 'palette'),
            'launcher_link': str(xdg_defaults.get('launcher_link') or '${VHK_BIN_HOME:-$HOME/.local/bin}/vhk-project'),
            'install_root': str(xdg_defaults.get('install_root') or '${XDG_DATA_HOME}/vhk/apps/vhk-project'),
            'bundle_cache_root': str(xdg_defaults.get('bundle_cache_root') or '${XDG_CACHE_HOME:-$HOME/.cache}/vhk/apps/vhk-project'),
            'state_root': str(xdg_defaults.get('state_root') or '${XDG_STATE_HOME:-$HOME/.local/state}/vhk/apps/vhk-project'),
            'desktop_actions': [str(x) for x in list(story.get('desktop_actions') or []) if str(x)],
        },
        'support': {
            'headline': str(support_posture.get('headline') or 'Support posture unavailable'),
            'claim_source': str(support_posture.get('claim_source') or 'planner_recommendations'),
            'reference_targets': [str(x) for x in list(support_posture.get('reference_targets') or []) if str(x)],
            'supported_targets': [str(x) for x in list(support_posture.get('supported_targets') or []) if str(x)],
            'caveated_targets': [str(x) for x in list(support_posture.get('caveated_targets') or []) if str(x)],
            'experimental_targets': [str(x) for x in list(support_posture.get('experimental_targets') or []) if str(x)],
            'docs': [str(x) for x in list(support_posture.get('docs') or []) if str(x)],
            'about_text': support_about,
            'flagship_lane_title': str(support_posture.get('flagship_lane_title') or ''),
            'flagship_release_level': str(support_posture.get('flagship_release_level') or ''),
            'flagship_deploy_style': str(support_posture.get('flagship_deploy_style') or ''),
        },
        'service': {
            'mode': str(service_hints.get('mode') or 'environment-only'),
            'watchers': [str(x) for x in list(service_hints.get('watchers') or []) if str(x)],
            'unit_base': str(service_hints.get('unit_base') or ''),
            'expected_units': [str(x) for x in list(service_hints.get('expected_units') or []) if str(x)],
            'guide_doc_kind': str(service_hints.get('guide_doc_kind') or 'service'),
            'rehearsal_doc_kind': str(service_hints.get('rehearsal_doc_kind') or 'rehearsal'),
        },
        'bundled_docs': doc_specs,
        'top_entries': top_entries,
        'commands': [
            {'argv': [str(story.get('command_name') or 'vhk-project')], 'summary': 'Open the reviewed project palette.'},
            {'argv': [str(story.get('command_name') or 'vhk-project'), '--open-doc', 'home'], 'summary': 'Open the packaged app-home guide in the default desktop viewer.'},
            {'argv': [str(story.get('command_name') or 'vhk-project'), '--open-doc', 'support'], 'summary': 'Open the packaged support guide.'},
            {'argv': [str(story.get('command_name') or 'vhk-project'), '--open-doc', 'service'], 'summary': 'Open the packaged session-service guide when this lane ships one.'},
            {'argv': [str(story.get('command_name') or 'vhk-project'), '--open-status-report'], 'summary': 'Generate and open a live status report for the installed lane.'},
            {'argv': [str(story.get('command_name') or 'vhk-project'), '--status-json'], 'summary': 'Print a machine-readable live status snapshot for the installed lane.'},
            {'argv': [str(story.get('command_name') or 'vhk-project'), '--inspect-bundle'], 'summary': 'Inspect the shipped reviewed bundle manifest.'},
            {'argv': [str(story.get('command_name') or 'vhk-project'), '--refresh-bundle'], 'summary': 'Refresh the cached materialized bundle before launching.'},
            {'argv': [str(story.get('command_name') or 'vhk-project'), '--status'], 'summary': 'Print bundle/runtime/doc/status paths for the installed lane.'},
            {'argv': [str(story.get('command_name') or 'vhk-project'), '--refresh-desktop-actions'], 'summary': 'Rewrite the installed desktop entry so launcher quick actions follow pinned and recent entries from this installed lane.'},
            {'argv': [str(story.get('command_name') or 'vhk-project'), '--pin-entry', '<entry-id>'], 'summary': 'Pin one palette entry into the stateful launcher quick-action set.'},
            {'argv': [str(story.get('command_name') or 'vhk-project'), '--list-pinned-entries'], 'summary': 'List pinned launcher entries with their current labels.'},
        ],
    }


def _render_native_home_doc(payload: dict[str, Any]) -> str:
    project = dict(payload.get('project') or {})
    native = dict(payload.get('native_install') or {})
    support = dict(payload.get('support') or {})
    service = dict(payload.get('service') or {})
    lines = [
        f"# VHK app home for {project.get('name') or 'project'}",
        '',
        'This file ships inside the native VHK app tree so launcher actions and operators have one packaged place to start: what this installed lane is, which reviewed bundle it carries, which docs came with it, and which palette entries are most relevant.',
        '',
        '## Installed lane',
        '',
        f"- Command: `{native.get('command_name') or 'vhk-project'}`",
        f"- App id: `{native.get('app_id') or 'io.visualhotkey.project'}`",
        f"- Bundle kind: `{native.get('bundle_kind') or 'project'}`",
        f"- Bundle name: `{native.get('bundle_name') or 'project.zip'}`",
        f"- Default entrypoint: `{native.get('default_entrypoint') or 'palette'}`",
        f"- Launcher link: `{native.get('launcher_link') or '${VHK_BIN_HOME:-$HOME/.local/bin}/vhk-project'}`",
        f"- Install root: `{native.get('install_root') or '${XDG_DATA_HOME}/vhk/apps/vhk-project'}`",
        f"- Bundle cache root: `{native.get('bundle_cache_root') or '${XDG_CACHE_HOME:-$HOME/.cache}/vhk/apps/vhk-project'}`",
        f"- Launcher state root: `{native.get('state_root') or '${XDG_STATE_HOME:-$HOME/.local/state}/vhk/apps/vhk-project'}`",
        '',
        '## Support posture',
        '',
        str(support.get('headline') or 'Support posture unavailable'),
        '',
    ]
    for label, key in [('Reference', 'reference_targets'), ('Supported', 'supported_targets'), ('Caveated', 'caveated_targets'), ('Experimental', 'experimental_targets')]:
        values = [str(x) for x in list(support.get(key) or []) if str(x)]
        if values:
            lines.append(f"- {label}: " + ', '.join(values[:5]))
    flagship = str(support.get('flagship_lane_title') or '').strip()
    if flagship:
        lines.append(f"- Flagship lane: {flagship}")
    deploy_style = str(support.get('flagship_deploy_style') or '').strip()
    if deploy_style:
        lines.append(f"- Flagship deploy style: {deploy_style}")
    lines.extend([
        '',
        '## Service and session hints',
        '',
        f"- Mode: `{service.get('mode') or 'environment-only'}`",
    ])
    unit_base = str(service.get('unit_base') or '').strip()
    if unit_base:
        lines.append(f"- Expected unit base: `{unit_base}`")
    watchers = [str(x) for x in list(service.get('watchers') or []) if str(x)]
    if watchers:
        lines.append('- Watchers: ' + ', '.join(watchers[:6]))
    expected_units = [str(x) for x in list(service.get('expected_units') or []) if str(x)]
    if expected_units:
        lines.append('- Expected user units: ' + ', '.join(expected_units))
    lines.extend([
        '- Live status/report surface: `--status`, `--status-json`, `--open-status-report`',
        '',
        '## Packaged docs',
        '',
    ])
    for item in [dict(x) for x in list(payload.get('bundled_docs') or []) if isinstance(x, dict)]:
        lines.append(f"- `{item.get('file')}` — {item.get('title') or item.get('kind') or 'doc'}")
    lines.extend([
        '',
        '## Top palette entries',
        '',
    ])
    top_entries = [dict(x) for x in list(payload.get('top_entries') or []) if isinstance(x, dict)]
    if not top_entries:
        lines.append('- No palette-visible entries were available when this app home was generated.')
    else:
        for item in top_entries[:8]:
            extras: list[str] = []
            if item.get('hotkeys'):
                extras.append('keys: ' + ', '.join([str(x) for x in list(item.get('hotkeys') or [])[:2]]))
            if item.get('hotstrings'):
                extras.append('triggers: ' + ', '.join([str(x) for x in list(item.get('hotstrings') or [])[:2]]))
            if item.get('recent_runs'):
                extras.append(f"recent: {int(item.get('recent_runs') or 0)}")
            lines.append(f"- `{item.get('entry_id')}` — {item.get('label') or item.get('entry_id') or 'entry'}" + (f" ({' · '.join(extras)})" if extras else ''))
    lines.extend([
        '',
        '## Useful commands',
        '',
    ])
    for item in [dict(x) for x in list(payload.get('commands') or []) if isinstance(x, dict)]:
        argv = [str(x) for x in list(item.get('argv') or []) if str(x)]
        if argv:
            lines.append(f"- `{' '.join(argv)}` — {item.get('summary') or ''}".rstrip())
    lines.append('')
    return "\n".join(lines)


def _render_native_desktop_file(project_dir: Path, plan: dict[str, Any]) -> str:
    story = dict(plan.get("native_install_story") or {})
    project = dict(plan.get("project") or {})
    app_id = str(story.get("app_id") or "io.visualhotkey.project")
    bundle_kind = str(story.get("bundle_kind") or "project")
    bundle_profile = str(story.get("bundle_profile_id") or "").strip()
    name = str(project.get("name") or "VHK project")
    comment = f"Open the reviewed VHK palette for {name}"
    if bundle_kind == "release-stage" and bundle_profile:
        comment += f" ({bundle_profile})"
    actions = [
        {"id": "OpenPalette", "name": "Open palette", "exec": desktop_exec_join(["__VHK_LAUNCHER_EXEC__"]), "icon": None},
        {"id": "OpenHomeDoc", "name": "Open app home", "exec": desktop_exec_join(["__VHK_LAUNCHER_EXEC__", "--open-doc", "home"]), "icon": None},
        {"id": "OpenSupportGuide", "name": "Open support guide", "exec": desktop_exec_join(["__VHK_LAUNCHER_EXEC__", "--open-doc", "support"]), "icon": None},
        {"id": "OpenServiceGuide", "name": "Open service guide", "exec": desktop_exec_join(["__VHK_LAUNCHER_EXEC__", "--open-doc", "service"]), "icon": None},
        {"id": "OpenStatusReport", "name": "Open live status report", "exec": desktop_exec_join(["__VHK_LAUNCHER_EXEC__", "--open-status-report"]), "icon": None},
        {"id": "InspectBundle", "name": "Inspect reviewed bundle", "exec": desktop_exec_join(["__VHK_LAUNCHER_EXEC__", "--inspect-bundle"]), "icon": None},
        {"id": "RefreshBundle", "name": "Refresh cached bundle", "exec": desktop_exec_join(["__VHK_LAUNCHER_EXEC__", "--refresh-bundle"]), "icon": None},
        {"id": "RefreshLauncherActions", "name": "Refresh launcher actions", "exec": desktop_exec_join(["__VHK_LAUNCHER_EXEC__", "--refresh-desktop-actions"]), "icon": None},
        *_native_quick_actions(project_dir),
    ]
    lines = [
        "[Desktop Entry]",
        "Version=1.5",
        "Type=Application",
        f"Name={_desktop_escape_value(name)}",
        f"Comment={_desktop_escape_value(comment)}",
        f"Exec={desktop_exec_join(['__VHK_LAUNCHER_EXEC__'])}",
        "TryExec=__VHK_LAUNCHER_TRYEXEC__",
        f"Icon={_desktop_escape_value(app_id)}",
        "Categories=Utility;Development;",
        "Keywords=automation;macro;hotkey;launcher;palette;",
        "Terminal=false",
        "StartupNotify=false",
        f"X-VHK-BundleKind={_desktop_escape_value(bundle_kind)}",
        f"X-VHK-DefaultEntry=palette",
        f"X-VHK-CacheRoot=${{XDG_CACHE_HOME:-$HOME/.cache}}/vhk/apps/{_desktop_escape_value(str(story.get('command_name') or 'vhk-project'))}",
        f"Actions={';'.join([str(item['id']) for item in actions])};",
        "",
    ]
    if bundle_profile:
        lines.insert(-2, f"X-VHK-BundleProfile={_desktop_escape_value(bundle_profile)}")
    for action in actions:
        lines.extend([
            f"[Desktop Action {action['id']}]",
            f"Name={_desktop_escape_value(str(action['name']))}",
            f"Exec={str(action['exec'])}",
        ])
        if action.get("icon"):
            lines.append(f"Icon={_desktop_escape_value(str(action['icon']))}")
        lines.append("")
    return "\n".join(lines)


def _native_install_paths(plan: dict[str, Any]) -> dict[str, str]:
    handoff = dict(plan.get("publish_handoff") or {})
    root = str(handoff.get("root") or "build/publish/project")
    distribution_story = dict(plan.get("distribution_story") or {})
    app_id = str(distribution_story.get("app_id") or "io.visualhotkey.project")
    command_name = str(distribution_story.get("command_name") or "vhk-project")
    bundle_name = str(distribution_story.get("bundle_name") or "project.zip")
    native_root = f"{root}/native"
    app_root = f"{native_root}/app"
    return {
        "native_root": native_root,
        "native_manifest": f"{native_root}/vhk_native_install_handoff.json",
        "native_readme": f"{native_root}/README.md",
        "native_refresh_script": f"{native_root}/refresh_native_install_inputs.sh",
        "native_assemble_script": f"{native_root}/assemble_native_app.sh",
        "native_smoke_script": f"{native_root}/smoke_test_native_install.sh",
        "native_refresh_actions_script": f"{native_root}/refresh_desktop_actions.sh",
        "native_install_script": f"{native_root}/install_xdg_local_app.sh",
        "native_uninstall_script": f"{native_root}/uninstall_xdg_local_app.sh",
        "native_app_root": app_root,
        "native_launcher": f"{app_root}/bin/{command_name}",
        "native_bundle_path": f"{app_root}/share/vhk/project/{bundle_name}",
        "native_runtime_root": f"{app_root}/lib/vhk-runtime",
        "native_desktop_file": f"{app_root}/share/applications/{app_id}.desktop",
        "native_metainfo_file": f"{app_root}/share/metainfo/{app_id}.metainfo.xml",
        "native_icon_file": f"{app_root}/share/icons/hicolor/256x256/apps/{app_id}.png",
        "native_doc_root": f"{app_root}/share/doc/vhk",
    }


def _native_install_constraints(plan: dict[str, Any]) -> list[str]:
    project = dict(plan.get("project") or {})
    backend = str(project.get("desktop_backend") or "unknown")
    story = dict(plan.get("embed_story") or {})
    bundle_story = dict(plan.get("bundle_release_story") or {})
    items = [
        "Model the local install after the Linux/XDG + pipx pattern: one isolated environment per app tree plus one command exposed from ~/.local/bin.",
        "Treat the generated native tree as the conservative runnable lane: it can carry a reviewed bundle, docs, and optionally an embedded runtime without pretending sandboxed packaging or host-global helpers are already solved.",
        "The installed launcher should default to the reviewed project palette, not to bundle inspection, so the first-launch experience feels like a real Linux app entrypoint instead of a maintainer diagnostic.",
        "Materialize the reviewed bundle into XDG cache/state owned by the user and reuse it until the shipped bundle changes, instead of unzipping the payload on every launch.",
        "Keep the install reversible: the generated uninstall script removes only the app root, launcher link, and desktop metadata created by this handoff.",
        "Do not claim this native install lane proves compositor-global remapping parity; helper daemons, raw-input permissions, and portal/compositor seams remain outside the Python app tree.",
    ]
    if backend == "wayland":
        items.append("For Wayland-first projects, market the native install lane as the place where helper daemons, portal setup, and compositor-specific routing can be documented honestly alongside the app tree.")
    if str(bundle_story.get("bundle_kind") or "project") == "release-stage" and bundle_story.get("bundle_profile_id"):
        items.append(f"This native install handoff is pinned to the `{bundle_story.get('bundle_profile_id')}` release-stage lane; refresh the local app tree whenever that lane's staged payload changes.")
    if story.get("python_cmd"):
        items.append(f"The embed helpers still assume a target-side Python command (`{story.get('python_cmd')}` by default); use a matching interpreter when building the local runtime tree.")
    return items


def build_native_install_plan(
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
    plan = build_runtime_embed_plan(
        project_dir,
        bundle_target_profile=bundle_target_profile,
        app_id=app_id,
        runtime=runtime,
        runtime_version=runtime_version,
        sdk=sdk,
        python_cmd=python_cmd,
    )
    distribution_story = dict(plan.get("distribution_story") or {})
    runtime_story = dict(plan.get("runtime_story") or {})
    embed_story = dict(plan.get("embed_story") or {})
    bundle_story = dict(plan.get("bundle_release_story") or {})
    paths = _native_install_paths(plan)
    app_id_value = str(distribution_story.get("app_id") or "io.visualhotkey.project")
    command_name = str(distribution_story.get("command_name") or "vhk-project")
    package_name = str(runtime_story.get("package_name") or embed_story.get("package_name") or "vhk")
    bundle_name = str(distribution_story.get("bundle_name") or embed_story.get("bundle_name") or "project.zip")
    service_hints = _native_service_hints(project_dir)
    desktop_actions = ["OpenPalette", "OpenHomeDoc", "OpenSupportGuide", "OpenServiceGuide", "OpenStatusReport", "InspectBundle", "RefreshBundle", "RefreshLauncherActions", "TopPaletteEntries"]
    native_story = {
        "headline": "Generate a conservative, XDG-local native install handoff so a reviewed VHK bundle can become one runnable app tree with an isolated runtime, launcher link, desktop actions, and a palette-first entrypoint.",
        "app_id": app_id_value,
        "command_name": command_name,
        "package_name": package_name,
        "bundle_name": bundle_name,
        "bundle_kind": str(bundle_story.get("bundle_kind") or "project"),
        "bundle_profile_id": str(bundle_story.get("bundle_profile_id") or "").strip() or None,
        "python_cmd": python_cmd,
        "desktop_actions": list(desktop_actions),
        "xdg_defaults": {
            "data_home": "~/.local/share",
            "bin_home": "~/.local/bin",
            "cache_home": "~/.cache",
            "state_home": "~/.local/state",
            "applications_dir": "${XDG_DATA_HOME}/applications",
            "metainfo_dir": "${XDG_DATA_HOME}/metainfo",
            "icons_dir": "${XDG_DATA_HOME}/icons/hicolor/256x256/apps",
            "install_root": f"${{XDG_DATA_HOME}}/vhk/apps/{command_name}",
            "launcher_link": f"${{VHK_BIN_HOME:-$HOME/.local/bin}}/{command_name}",
            "bundle_cache_root": f"${{XDG_CACHE_HOME:-$HOME/.cache}}/vhk/apps/{command_name}",
            "state_root": f"${{XDG_STATE_HOME:-$HOME/.local/state}}/vhk/apps/{command_name}",
        },
        "default_entrypoint": "palette",
        "app_tree": {
            "root": paths["native_app_root"],
            "launcher": paths["native_launcher"],
            "bundle_payload": paths["native_bundle_path"],
            "runtime_root": paths["native_runtime_root"],
            "desktop_file": paths["native_desktop_file"],
            "metainfo_file": paths["native_metainfo_file"],
            "icon_file": paths["native_icon_file"],
        },
        "service_hints": service_hints,
        "constraints": _native_install_constraints(plan),
    }
    native_commands = [
        "vhk gen-runtime-pack . --force",
        "vhk gen-runtime-embed-pack . --force",
        "vhk gen-native-install-pack . --force",
        str(bundle_story.get("bundle_command") or ""),
        f"sh {paths['native_assemble_script']}",
        f"sh {paths['native_smoke_script']}",
    ]
    plan["native_install_paths"] = paths
    plan["native_install_story"] = native_story
    plan["native_install_commands"] = [cmd for cmd in native_commands if str(cmd).strip()]
    plan["native_install_summary"] = {
        "app_id": app_id_value,
        "command_name": command_name,
        "bundle_kind": native_story["bundle_kind"],
        "python_cmd": python_cmd,
        "desktop_actions": list(desktop_actions),
    }
    plan["source_contract"] = "native_install_pack"
    return plan


def render_native_install_doc(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    story = dict(plan.get("native_install_story") or {})
    paths = dict(plan.get("native_install_paths") or {})
    lines = [
        f"# VHK native install pack for {project.get('name') or 'project'}",
        "",
        "Generated by `vhk gen-native-install-pack`. Use it to turn the reviewed bundle/runtime handoff into one conservative XDG-local app tree with a launcher, desktop metadata, packaged support/home docs, a live installed-lane status surface, and optional embedded runtime.",
        "",
        "## Native install posture",
        "",
        f"- App id: `{story.get('app_id') or 'io.visualhotkey.project'}`",
        f"- Command: `{story.get('command_name') or 'vhk-project'}`",
        f"- Bundle kind: `{story.get('bundle_kind') or 'project'}`",
        f"- Bundle name: `{story.get('bundle_name') or 'project.zip'}`",
        f"- Python command: `{story.get('python_cmd') or 'python'}`",
        "",
        "## XDG-local install defaults",
        "",
        f"- Data home: `{((story.get('xdg_defaults') or {}).get('data_home')) or '~/.local/share'}`",
        f"- Bin home: `{((story.get('xdg_defaults') or {}).get('bin_home')) or '~/.local/bin'}`",
        f"- Cache home: `{((story.get('xdg_defaults') or {}).get('cache_home')) or '~/.cache'}`",
        f"- State home: `{((story.get('xdg_defaults') or {}).get('state_home')) or '~/.local/state'}`",
        f"- Install root: `{((story.get('xdg_defaults') or {}).get('install_root')) or '${XDG_DATA_HOME}/vhk/apps/project'}`",
        f"- Launcher link: `{((story.get('xdg_defaults') or {}).get('launcher_link')) or '${VHK_BIN_HOME:-$HOME/.local/bin}/vhk-project'}`",
        f"- Bundle cache root: `{((story.get('xdg_defaults') or {}).get('bundle_cache_root')) or '${XDG_CACHE_HOME:-$HOME/.cache}/vhk/apps/vhk-project'}`",
        f"- State root: `{((story.get('xdg_defaults') or {}).get('state_root')) or '${XDG_STATE_HOME:-$HOME/.local/state}/vhk/apps/vhk-project'}`",
        "",
        "## App tree",
        "",
        f"- Native app root: `{paths.get('native_app_root')}`",
        f"- Runtime root: `{paths.get('native_runtime_root')}`",
        f"- Bundle payload: `{paths.get('native_bundle_path')}`",
        f"- Desktop file: `{paths.get('native_desktop_file')}`",
        f"- Default entrypoint: `{story.get('default_entrypoint') or 'palette'}`",
        f"- Packaged docs root: `{paths.get('native_doc_root')}`",
        "",
        "## Constraints",
        "",
    ]
    for item in [str(x) for x in list(story.get("constraints") or []) if str(x)]:
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## Review commands",
        "",
    ])
    for cmd in [str(x) for x in list(plan.get("native_install_commands") or []) if str(x)]:
        lines.append(f"- `{cmd}`")
    lines.append("")
    return "\n".join(lines)


def render_native_install_handoff_readme(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    story = dict(plan.get("native_install_story") or {})
    paths = dict(plan.get("native_install_paths") or {})
    return "\n".join(
        [
            f"# VHK native install handoff for {project.get('name') or 'project'}",
            "",
            "Generated by `vhk gen-native-install-pack`. This tree packages one conservative local-install story: assemble the app tree, optionally embed the runtime at its final install path, install/uninstall it under XDG-local directories, ship packaged home/support docs, generate a live installed-lane status report, and launch the reviewed palette from a cached materialized bundle instead of a mutable checkout.",
            "",
            f"- Bundle kind: `{story.get('bundle_kind') or 'project'}`",
            f"- Bundle name: `{story.get('bundle_name') or 'project.zip'}`",
            f"- Command name: `{story.get('command_name') or 'vhk-project'}`",
            "",
            "## Generated scripts",
            "",
            f"- Assemble: `{paths.get('native_assemble_script')}`",
            f"- Install: `{paths.get('native_install_script')}`",
            f"- Uninstall: `{paths.get('native_uninstall_script')}`",
            f"- Smoke test: `{paths.get('native_smoke_script')}`",
            f"- Refresh launcher actions: `{paths.get('native_refresh_actions_script')}`",
            "",
            "## Flow",
            "",
            "1. Refresh the lower-level publish/runtime/embed handoffs.",
            "2. Assemble the local app tree so the reviewed bundle and docs land under one native root.",
            "3. Install it into XDG-local directories and optionally embed the runtime at the final install path.",
            "4. Use launcher quick actions or `--open-doc` to reach packaged home/support docs without digging through the project tree.",
            "5. Launch the installed command to materialize the reviewed bundle into XDG cache and open the project palette by default.",
            "6. Use the uninstall script to remove only what this handoff created.",
            "",
        ]
    )


def render_native_install_refresh_script(plan: dict[str, Any]) -> str:
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
        'printf "%s\\n" "Refreshing VHK native install pack inputs..."',
    ]
    runtime = 'vhk gen-runtime-embed-pack . --force --quiet'
    native = 'vhk gen-native-install-pack . --force --quiet'
    if profile:
        runtime += f' --bundle-target-profile {profile}'
        native += f' --bundle-target-profile {profile}'
    for cmd in [runtime, native]:
        lines.append(f'printf "+ %s\\n" {cmd!r}')
        lines.append(f'sh -lc {cmd!r} || true')
    lines.extend([
        'printf "%s\\n" "Native install pack refresh complete."',
        "",
    ])
    return "\n".join(lines)


def _render_native_launcher(plan: dict[str, Any]) -> str:
    story = dict(plan.get("native_install_story") or {})
    command_name = str(story.get("command_name") or "vhk-project")
    bundle_name = str(story.get("bundle_name") or "project.zip")
    app_id = str(story.get("app_id") or "io.visualhotkey.project")
    service_hints = dict(story.get("service_hints") or {})
    service_mode = str(service_hints.get("mode") or "environment-only")
    service_unit_base = str(service_hints.get("unit_base") or "")
    service_units = ":".join([str(x) for x in list(service_hints.get("expected_units") or []) if str(x)])
    script = """#!/usr/bin/env sh
set -eu

resolve_self_path() {
  if command -v readlink >/dev/null 2>&1; then
    resolved="$(readlink -f -- "$0" 2>/dev/null || true)"
    if [ -n "$resolved" ]; then
      printf '%s\n' "$resolved"
      return 0
    fi
  fi
  if command -v python3 >/dev/null 2>&1; then
    python3 - "$0" <<'PY'
import os
import sys
print(os.path.realpath(sys.argv[1]))
PY
    return 0
  fi
  if command -v python >/dev/null 2>&1; then
    python - "$0" <<'PY'
import os
import sys
print(os.path.realpath(sys.argv[1]))
PY
    return 0
  fi
  printf '%s\n' "$0"
}

SELF_PATH="$(resolve_self_path)"
APP_ROOT="${APP_ROOT:-$(CDPATH= cd -- "$(dirname -- "$SELF_PATH")/.." && pwd)}"
EMBEDDED_VHK="$APP_ROOT/lib/vhk-runtime/bin/vhk"
EMBEDDED_PYTHON="$APP_ROOT/lib/vhk-runtime/bin/python"
BUNDLE_PATH="$APP_ROOT/share/vhk/project/__VHK_BUNDLE_NAME__"
DOC_ROOT="$APP_ROOT/share/doc/vhk"
APP_HOME_DOC="$DOC_ROOT/VHK_APP_HOME.md"
APP_HOME_JSON="$DOC_ROOT/VHK_APP_HOME.json"
STATUS_ROOT="$STATE_ROOT/status"
STATUS_JSON="$STATUS_ROOT/VHK_APP_STATUS.json"
STATUS_MD="$STATUS_ROOT/VHK_APP_STATUS.md"
XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
XDG_CACHE_HOME="${XDG_CACHE_HOME:-$HOME/.cache}"
XDG_STATE_HOME="${XDG_STATE_HOME:-$HOME/.local/state}"
VHK_BIN_HOME="${VHK_BIN_HOME:-$HOME/.local/bin}"
CACHE_ROOT="${VHK_CACHE_ROOT:-$XDG_CACHE_HOME/vhk/apps/__VHK_COMMAND_NAME__}"
STATE_ROOT="${VHK_STATE_ROOT:-$XDG_STATE_HOME/vhk/apps/__VHK_COMMAND_NAME__}"
MATERIALIZED_ROOT="$CACHE_ROOT/materialized"
STAMP_FILE="$CACHE_ROOT/bundle.stamp"
RECENTS_FILE="$STATE_ROOT/recent_entries.json"
PINS_FILE="$STATE_ROOT/pinned_entries.json"
DESKTOP_TEMPLATE="$APP_ROOT/share/applications/__VHK_APP_ID__.desktop"
DESKTOP_DEST="${VHK_DESKTOP_FILE:-$XDG_DATA_HOME/applications/__VHK_APP_ID__.desktop}"
LAUNCHER_EXEC="${VHK_LAUNCHER_EXEC_PATH:-$VHK_BIN_HOME/__VHK_COMMAND_NAME__}"
SERVICE_MODE="__VHK_SERVICE_MODE__"
SERVICE_UNIT_BASE="__VHK_SERVICE_UNIT_BASE__"
SERVICE_UNITS_RAW="__VHK_SERVICE_UNITS__"
FORCE_REFRESH=0
MODE="palette"
ENTRY_ID=""
DOC_KIND=""
PIN_ENTRY_ID=""
PASS_ARGS=""
NO_RUN=0

resolve_vhk_cmd() {
  if [ -x "$EMBEDDED_VHK" ]; then
    printf '%s\n' "$EMBEDDED_VHK"
    return 0
  fi
  if command -v vhk >/dev/null 2>&1; then
    command -v vhk
    return 0
  fi
  return 1
}

resolve_python_cmd() {
  if [ -x "$EMBEDDED_PYTHON" ]; then
    printf '%s\n' "$EMBEDDED_PYTHON"
    return 0
  fi
  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return 0
  fi
  if command -v python >/dev/null 2>&1; then
    command -v python
    return 0
  fi
  return 1
}

runtime_source() {
  if [ -x "$EMBEDDED_VHK" ]; then
    printf '%s\n' 'embedded'
    return 0
  fi
  if command -v vhk >/dev/null 2>&1; then
    printf '%s\n' 'system'
    return 0
  fi
  printf '%s\n' 'missing'
  return 1
}

fail_runtime() {
  printf '%s\n' 'No embedded or system VHK runtime is available for this native app tree.' >&2
  printf '%s\n' "Bundle payload: $BUNDLE_PATH" >&2
  printf '%s\n' 'Run install_xdg_local_app.sh with VHK_EMBED_RUNTIME=1, or install vhk system-wide before launching this app.' >&2
  exit 1
}

doc_path() {
  case "$1" in
    home) printf '%s\n' "$APP_HOME_DOC" ;;
    home-json) printf '%s\n' "$APP_HOME_JSON" ;;
    status) printf '%s\n' "$STATUS_MD" ;;
    status-json) printf '%s\n' "$STATUS_JSON" ;;
    support) printf '%s\n' "$DOC_ROOT/VHK_PUBLIC_SUPPORT.md" ;;
    install) printf '%s\n' "$DOC_ROOT/VHK_INSTALL_QUICKSTART.md" ;;
    native) printf '%s\n' "$DOC_ROOT/VHK_NATIVE_INSTALL.md" ;;
    distribution) printf '%s\n' "$DOC_ROOT/VHK_DISTRIBUTION.md" ;;
    runtime) printf '%s\n' "$DOC_ROOT/VHK_RUNTIME.md" ;;
    runtime-embed) printf '%s\n' "$DOC_ROOT/VHK_RUNTIME_EMBED.md" ;;
    service) printf '%s\n' "$DOC_ROOT/VHK_SERVICE_COMPOSE.md" ;;
    rehearsal) printf '%s\n' "$DOC_ROOT/VHK_HOST_REHEARSAL.md" ;;
    *) return 1 ;;
  esac
}

open_doc() {
  target="$(doc_path "$1")" || {
    printf '%s\n' "Unknown doc kind: $1" >&2
    exit 2
  }
  if [ ! -f "$target" ]; then
    case "$1" in
      status|status-json) refresh_status_report >/dev/null 2>&1 || true ;;
    esac
  fi
  if [ ! -f "$target" ]; then
    case "$1" in
      status|status-json) refresh_status_report >/dev/null 2>&1 || true ;;
    esac
  fi
  if [ ! -f "$target" ]; then
    printf '%s\n' "Packaged doc is missing: $target" >&2
    exit 1
  fi
  if command -v gio >/dev/null 2>&1; then
    exec gio open "$target"
  fi
  if command -v xdg-open >/dev/null 2>&1; then
    exec xdg-open "$target"
  fi
  printf '%s\n' "$target"
}

print_doc() {
  target="$(doc_path "$1")" || {
    printf '%s\n' "Unknown doc kind: $1" >&2
    exit 2
  }
  if [ ! -f "$target" ]; then
    printf '%s\n' "Packaged doc is missing: $target" >&2
    exit 1
  fi
  cat "$target"
}

list_docs() {
  for kind in home home-json status status-json support install native distribution runtime runtime-embed service rehearsal; do
    target="$(doc_path "$kind" 2>/dev/null || true)"
    if [ -n "$target" ] && [ -f "$target" ]; then
      printf '%s\t%s\n' "$kind" "$target"
    fi
  done
}

bundle_stamp() {
  PYTHON_CMD="$(resolve_python_cmd)" || fail_runtime
  "$PYTHON_CMD" - "$BUNDLE_PATH" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
st = p.stat()
print(f"{st.st_size}:{st.st_mtime_ns}")
PY
}

project_root_from_metadata() {
  PYTHON_CMD="$(resolve_python_cmd)" || fail_runtime
  "$PYTHON_CMD" - "$MATERIALIZED_ROOT/.vhk_bundle_materialized.json" <<'PY'
import json
import sys
from pathlib import Path
meta = json.loads(Path(sys.argv[1]).read_text())
print(meta.get('project_root') or '')
PY
}

ensure_materialized() {
  VHK_CMD="$(resolve_vhk_cmd)" || fail_runtime
  CURRENT_STAMP="$(bundle_stamp)"
  STORED_STAMP=""
  if [ -f "$STAMP_FILE" ]; then
    STORED_STAMP="$(cat "$STAMP_FILE" 2>/dev/null || true)"
  fi
  if [ "$FORCE_REFRESH" = "1" ] || [ ! -d "$MATERIALIZED_ROOT" ] || [ ! -f "$MATERIALIZED_ROOT/.vhk_bundle_materialized.json" ] || [ "$CURRENT_STAMP" != "$STORED_STAMP" ]; then
    mkdir -p "$CACHE_ROOT"
    rm -rf "$MATERIALIZED_ROOT"
    "$VHK_CMD" materialize-bundle "$BUNDLE_PATH" "$MATERIALIZED_ROOT" >/dev/null
    printf '%s\n' "$CURRENT_STAMP" > "$STAMP_FILE"
  fi
  PROJECT_ROOT="$(project_root_from_metadata)"
  if [ -z "$PROJECT_ROOT" ] || [ ! -d "$PROJECT_ROOT" ]; then
    printf '%s\n' 'Materialized bundle is missing a readable project root.' >&2
    exit 1
  fi
}

append_pass_arg() {
  if [ -z "$PASS_ARGS" ]; then
    PASS_ARGS=$(printf '%s' "$1" | sed "s/'/'\\''/g")
  else
    PASS_ARGS="$PASS_ARGS $(printf '%s' "$1" | sed "s/'/'\\''/g")"
  fi
}

palette_cmd() {
  set -- "$VHK_CMD" palette "$PROJECT_ROOT"
  if [ -n "$PASS_ARGS" ]; then
    eval "set -- \"\\$@\" $PASS_ARGS"
  fi
  "$@"
}

palette_entry_json_path() {
  TMP_DIR="$STATE_ROOT/tmp"
  mkdir -p "$TMP_DIR"
  tmp_json="$TMP_DIR/palette.json"
  palette_cmd --json > "$tmp_json"
  printf '%s\n' "$tmp_json"
}

mutate_entry_list() {
  mode="$1"
  entry_id="$2"
  target="$3"
  max_items="$4"
  PYTHON_CMD="$(resolve_python_cmd)" || fail_runtime
  mkdir -p "$STATE_ROOT"
  "$PYTHON_CMD" - "$mode" "$entry_id" "$target" "$max_items" <<'PY'
import json
import sys
from pathlib import Path
mode, entry_id, target, max_items = sys.argv[1], sys.argv[2], Path(sys.argv[3]), int(sys.argv[4])
items = []
if target.exists():
    try:
        payload = json.loads(target.read_text())
        if isinstance(payload, list):
            items = [str(x) for x in payload if str(x)]
    except Exception:
        items = []
if mode == 'recent':
    items = [entry_id, *[x for x in items if x != entry_id]]
    if max_items > 0:
        items = items[:max_items]
elif mode == 'pin':
    if entry_id not in items:
        items.append(entry_id)
elif mode == 'unpin':
    items = [x for x in items if x != entry_id]
else:
    raise SystemExit(f'unknown mutation mode: {mode}')
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(items, indent=2) + "\n")
PY
}

record_recent_entry() {
  [ -n "$1" ] || return 0
  mutate_entry_list recent "$1" "$RECENTS_FILE" 12
}

pin_entry() {
  [ -n "$1" ] || return 0
  mutate_entry_list pin "$1" "$PINS_FILE" 24
}

unpin_entry() {
  [ -n "$1" ] || return 0
  mutate_entry_list unpin "$1" "$PINS_FILE" 24
}

list_entry_state() {
  target="$1"
  ensure_materialized
  palette_json="$(palette_entry_json_path)"
  PYTHON_CMD="$(resolve_python_cmd)" || fail_runtime
  "$PYTHON_CMD" - "$target" "$palette_json" <<'PY'
import json
import sys
from pathlib import Path
state_path = Path(sys.argv[1])
palette_path = Path(sys.argv[2])
items = []
if state_path.exists():
    try:
        payload = json.loads(state_path.read_text())
        if isinstance(payload, list):
            items = [str(x) for x in payload if str(x)]
    except Exception:
        items = []
entries = {}
try:
    palette = json.loads(palette_path.read_text())
    for entry in palette.get('entries') or []:
        if isinstance(entry, dict):
            entries[str(entry.get('entry_id') or '')] = entry
except Exception:
    pass
for entry_id in items:
    row = entries.get(entry_id) or {}
    label = str(row.get('label') or entry_id)
    print(f"{entry_id}\t{label}")
PY
}

refresh_desktop_actions() {
  ensure_materialized
  PYTHON_CMD="$(resolve_python_cmd)" || fail_runtime
  mkdir -p "$STATE_ROOT"
  palette_json="$(palette_entry_json_path)"
  "$PYTHON_CMD" - "$DESKTOP_TEMPLATE" "$DESKTOP_DEST" "$LAUNCHER_EXEC" "$RECENTS_FILE" "$PINS_FILE" "$palette_json" <<'PY'
import json
import re
import sys
from pathlib import Path

def quote(arg: str) -> str:
    value = str(arg).replace('%', '%%')
    reserved = set(" \t\n\"'\\><~|&;$*?#()`")
    if value and not any(ch in reserved for ch in value):
        return value
    escaped = value.replace('\\', '\\\\').replace('"', '\\"').replace('`', '\\`').replace('$', '\\$')
    return f'"{escaped}"'

def load_list(path: Path) -> list[str]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text())
    except Exception:
        return []
    if not isinstance(payload, list):
        return []
    return [str(x) for x in payload if str(x)]

def action_seed(entry_id: str, idx: int) -> str:
    seed = re.sub(r'[^A-Za-z0-9-]+', '-', entry_id.replace('@', '-').replace('#', '-').replace('!', '-')).strip('-')
    seed = seed or f'Quick-{idx}'
    return f'Quick-{idx}-{seed}'[:48]

template_path = Path(sys.argv[1])
dest_path = Path(sys.argv[2])
launcher = sys.argv[3]
recents_path = Path(sys.argv[4])
pins_path = Path(sys.argv[5])
palette_path = Path(sys.argv[6])
palette = json.loads(palette_path.read_text())
entries = [entry for entry in palette.get('entries') or [] if isinstance(entry, dict) and str(entry.get('action') or 'run') == 'run']
by_id = {str(entry.get('entry_id') or ''): entry for entry in entries if str(entry.get('entry_id') or '')}
pins = [entry_id for entry_id in load_list(pins_path) if entry_id in by_id]
recents = [entry_id for entry_id in load_list(recents_path) if entry_id in by_id and entry_id not in pins]
order = []
for entry_id in [*pins, *recents]:
    if entry_id not in order:
        order.append(entry_id)
if not order:
    order = [str(entry.get('entry_id') or '') for entry in entries[:4] if str(entry.get('entry_id') or '')]
dynamic_ids = []
actions = []
for idx, entry_id in enumerate(order[:4], start=1):
    entry = by_id.get(entry_id) or {}
    action_id = action_seed(entry_id, idx)
    dynamic_ids.append(action_id)
    label = str(entry.get('label') or entry_id)
    if entry_id in pins:
        label = f'Pinned: {label}'
    elif entry_id in recents:
        label = f'Recent: {label}'
    actions.append((action_id, label, [launcher, '--entry-id', entry_id], str(entry.get('icon') or '').strip() or None))
text = template_path.read_text()
text = text.replace('__VHK_LAUNCHER_EXEC__', quote(launcher))
text = text.replace('__VHK_LAUNCHER_TRYEXEC__', launcher)
lines = text.splitlines()
for idx, line in enumerate(lines):
    if line.startswith('Actions='):
        existing = [item for item in line[len('Actions='):].split(';') if item]
        existing = [item for item in existing if not item.startswith('Quick-')]
        lines[idx] = 'Actions=' + ';'.join([*existing, *dynamic_ids]) + ';'
        break
rendered = '\n'.join(lines).rstrip() + '\n\n'
for action_id, name, argv, icon in actions:
    rendered += f'[Desktop Action {action_id}]\n'
    rendered += f'Name={name.replace(chr(10), " ")}\n'
    rendered += 'Exec=' + ' '.join(quote(part) for part in argv) + '\n'
    if icon:
        rendered += f'Icon={icon}\n'
    rendered += '\n'
dest_path.parent.mkdir(parents=True, exist_ok=True)
dest_path.write_text(rendered)
print(dest_path)
PY
}

refresh_status_report() {
  ensure_materialized
  palette_json="$(palette_entry_json_path)"
  PYTHON_CMD="$(resolve_python_cmd)" || fail_runtime
  mkdir -p "$STATUS_ROOT"
  runtime="$(runtime_source 2>/dev/null || printf '%s' missing)"
  "$PYTHON_CMD" - "$STATUS_JSON" "$STATUS_MD" "$APP_HOME_JSON" "$DOC_ROOT" "$DESKTOP_DEST" "$APP_ROOT" "$BUNDLE_PATH" "$CACHE_ROOT" "$STATE_ROOT" "$MATERIALIZED_ROOT" "$PROJECT_ROOT" "$RECENTS_FILE" "$PINS_FILE" "$palette_json" "$runtime" "$LAUNCHER_EXEC" "$SERVICE_MODE" "$SERVICE_UNIT_BASE" "$SERVICE_UNITS_RAW" <<'PY'
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

status_json = Path(sys.argv[1])
status_md = Path(sys.argv[2])
app_home_json = Path(sys.argv[3])
doc_root = Path(sys.argv[4])
desktop_dest = Path(sys.argv[5])
app_root = Path(sys.argv[6])
bundle_path = Path(sys.argv[7])
cache_root = Path(sys.argv[8])
state_root = Path(sys.argv[9])
materialized_root = Path(sys.argv[10])
project_root = Path(sys.argv[11])
recents_path = Path(sys.argv[12])
pins_path = Path(sys.argv[13])
palette_path = Path(sys.argv[14])
runtime_source = sys.argv[15]
launcher_exec = sys.argv[16]
service_mode = sys.argv[17]
service_unit_base = sys.argv[18]
service_units_raw = sys.argv[19]

def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except Exception:
        return default

app_home = load_json(app_home_json, {}) if app_home_json.exists() else {}
palette_payload = load_json(palette_path, {})
entry_rows = {}
for row in palette_payload.get('entries') or []:
    if isinstance(row, dict):
        entry_id = str(row.get('entry_id') or '')
        if entry_id:
            entry_rows[entry_id] = row

def resolve_entries(path: Path) -> list[dict[str, str]]:
    payload = load_json(path, [])
    out = []
    if not isinstance(payload, list):
        return out
    for entry_id in payload:
        entry_id = str(entry_id)
        row = entry_rows.get(entry_id) or {}
        out.append({'entry_id': entry_id, 'label': str(row.get('label') or entry_id)})
    return out

recent_entries = resolve_entries(recents_path)
pinned_entries = resolve_entries(pins_path)
packaged_docs = sorted([p.name for p in doc_root.iterdir() if p.is_file()]) if doc_root.exists() else []
service_units = [item for item in service_units_raw.split(':') if item]
service_payload = {
    'mode': service_mode,
    'unit_base': service_unit_base or None,
    'expected_units': service_units,
    'systemctl_available': bool(shutil.which('systemctl')),
    'journalctl_available': bool(shutil.which('journalctl')),
    'units': [],
}
if service_payload['systemctl_available'] and service_units:
    for unit in service_units:
        proc = subprocess.run(
            ['systemctl', '--user', 'show', '--property=LoadState,ActiveState,SubState,UnitFileState,FragmentPath', unit],
            capture_output=True,
            text=True,
        )
        fields = {'unit': unit}
        for line in (proc.stdout or '').splitlines():
            if '=' not in line:
                continue
            key, value = line.split('=', 1)
            fields[key] = value
        service_payload['units'].append(
            {
                'unit': unit,
                'load_state': str(fields.get('LoadState') or ('not-found' if proc.returncode else 'unknown')),
                'active_state': str(fields.get('ActiveState') or ('inactive' if proc.returncode else 'unknown')),
                'sub_state': str(fields.get('SubState') or ''),
                'unit_file_state': str(fields.get('UnitFileState') or ''),
                'fragment_path': str(fields.get('FragmentPath') or ''),
                'query_ok': proc.returncode == 0,
            }
        )
payload = {
    'generated_at_epoch': time.time(),
    'generated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'app': {
        'name': str((app_home.get('project') or {}).get('name') or app_root.name),
        'command_name': str((app_home.get('native_install') or {}).get('command_name') or launcher_exec),
        'app_id': str((app_home.get('native_install') or {}).get('app_id') or ''),
        'bundle_kind': str((app_home.get('native_install') or {}).get('bundle_kind') or 'project'),
        'bundle_profile_id': (app_home.get('native_install') or {}).get('bundle_profile_id'),
        'runtime_source': runtime_source,
    },
    'paths': {
        'launcher_exec': launcher_exec,
        'desktop_file': str(desktop_dest),
        'app_root': str(app_root),
        'bundle_path': str(bundle_path),
        'cache_root': str(cache_root),
        'state_root': str(state_root),
        'materialized_root': str(materialized_root),
        'project_root': str(project_root),
        'status_json': str(status_json),
        'status_markdown': str(status_md),
    },
    'docs': {'packaged': packaged_docs, 'doc_root': str(doc_root)},
    'launcher_state': {'pinned_entries': pinned_entries, 'recent_entries': recent_entries},
    'service': service_payload,
}
status_json.parent.mkdir(parents=True, exist_ok=True)
status_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')
lines = [
    f"# VHK live status for {payload['app']['name']}",
    '',
    f"- Generated at: `{payload['generated_at']}`",
    f"- Runtime source: `{payload['app']['runtime_source']}`",
    f"- Bundle kind: `{payload['app']['bundle_kind']}`",
    f"- Launcher exec: `{payload['paths']['launcher_exec']}`",
    f"- Desktop file: `{payload['paths']['desktop_file']}`",
    f"- Project root: `{payload['paths']['project_root']}`",
    f"- Materialized root: `{payload['paths']['materialized_root']}`",
    '',
    '## Packaged docs',
    '',
]
for name in packaged_docs:
    lines.append(f"- `{name}`")
lines.extend(['', '## Launcher state', ''])
if pinned_entries:
    lines.append('- Pinned entries:')
    for row in pinned_entries[:8]:
        lines.append(f"  - `{row['entry_id']}` — {row['label']}")
else:
    lines.append('- Pinned entries: none yet')
if recent_entries:
    lines.append('- Recent entries:')
    for row in recent_entries[:8]:
        lines.append(f"  - `{row['entry_id']}` — {row['label']}")
else:
    lines.append('- Recent entries: none yet')
lines.extend(['', '## Service/session hints', ''])
lines.append(f"- Mode: `{service_mode}`")
if service_unit_base:
    lines.append(f"- Unit base: `{service_unit_base}`")
if service_payload['units']:
    for row in service_payload['units']:
        summary = f"load={row['load_state']} active={row['active_state']}"
        if row['sub_state']:
            summary += f" sub={row['sub_state']}"
        if row['unit_file_state']:
            summary += f" enabled={row['unit_file_state']}"
        lines.append(f"- `{row['unit']}` — {summary}")
elif service_units:
    lines.append('- Expected units are known, but `systemctl --user show` did not yield live state.')
else:
    lines.append('- No bundled user-service units are expected for this lane.')
lines.extend(['', '## Machine-readable snapshot', '', f"- `{status_json}`", ''])
status_md.write_text('\n'.join(lines).rstrip() + '\n')
print(status_json)
PY
}

print_status() {
  ensure_materialized
  refresh_status_report >/dev/null 2>&1 || true
  printf '%s\n' 'VHK reviewed lane status'
  printf '%s\n' "runtime-source: $(runtime_source 2>/dev/null || printf '%s' missing)"
  printf '%s\n' "bundle-path: $BUNDLE_PATH"
  printf '%s\n' "cache-root: $CACHE_ROOT"
  printf '%s\n' "state-root: $STATE_ROOT"
  printf '%s\n' "desktop-file: $DESKTOP_DEST"
  printf '%s\n' "materialized-root: $MATERIALIZED_ROOT"
  printf '%s\n' "project-root: $PROJECT_ROOT"
  printf '%s\n' "app-home-doc: $APP_HOME_DOC"
  printf '%s\n' "status-report: $STATUS_MD"
  printf '%s\n' "status-json: $STATUS_JSON"
  if [ -n "$SERVICE_UNIT_BASE" ]; then
    printf '%s\n' "service-unit-base: $SERVICE_UNIT_BASE"
  fi
  if [ -f "$APP_HOME_JSON" ]; then
    printf '%s\n' "app-home-json: $APP_HOME_JSON"
  fi
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --inspect-bundle)
      MODE="inspect"
      shift
      ;;
    --refresh-bundle)
      FORCE_REFRESH=1
      shift
      ;;
    --refresh-desktop-actions)
      MODE="refresh-desktop-actions"
      shift
      ;;
    --print-project-root)
      MODE="print-project-root"
      shift
      ;;
    --refresh-status-report)
      MODE="refresh-status-report"
      shift
      ;;
    --about)
      MODE="about"
      shift
      ;;
    --home-json|--support-json)
      MODE="home-json"
      shift
      ;;
    --status-json)
      MODE="status-json"
      shift
      ;;
    --open-status-report)
      MODE="open-status-report"
      shift
      ;;
    --list-docs)
      MODE="list-docs"
      shift
      ;;
    --list-recent-entries)
      MODE="list-recent"
      shift
      ;;
    --list-pinned-entries)
      MODE="list-pinned"
      shift
      ;;
    --pin-entry)
      PIN_ENTRY_ID="$2"
      MODE="pin-entry"
      shift 2
      ;;
    --unpin-entry)
      PIN_ENTRY_ID="$2"
      MODE="unpin-entry"
      shift 2
      ;;
    --status)
      MODE="status"
      shift
      ;;
    --open-doc)
      DOC_KIND="$2"
      MODE="open-doc"
      shift 2
      ;;
    --print-doc-path)
      DOC_KIND="$2"
      MODE="print-doc-path"
      shift 2
      ;;
    --entry-id)
      ENTRY_ID="$2"
      shift 2
      ;;
    --no-run)
      NO_RUN=1
      shift
      ;;
    --)
      shift
      while [ "$#" -gt 0 ]; do
        append_pass_arg "$1"
        shift
      done
      ;;
    *)
      append_pass_arg "$1"
      shift
      ;;
  esac
done

if [ "$MODE" = "about" ]; then
  print_doc home
  exit 0
fi
if [ "$MODE" = "home-json" ]; then
  print_doc home-json
  exit 0
fi
if [ "$MODE" = "status-json" ]; then
  print_doc status-json
  exit 0
fi
if [ "$MODE" = "open-status-report" ]; then
  open_doc status
fi
if [ "$MODE" = "list-docs" ]; then
  list_docs
  exit 0
fi
if [ "$MODE" = "print-doc-path" ]; then
  doc_path "$DOC_KIND"
  exit 0
fi
if [ "$MODE" = "open-doc" ]; then
  open_doc "$DOC_KIND"
fi
VHK_CMD="$(resolve_vhk_cmd)" || fail_runtime
if [ "$MODE" = "inspect" ]; then
  exec "$VHK_CMD" inspect-bundle "$BUNDLE_PATH"
fi
if [ "$MODE" = "status" ]; then
  print_status
  exit 0
fi
if [ "$MODE" = "refresh-status-report" ]; then
  refresh_status_report
  exit 0
fi
if [ "$MODE" = "refresh-desktop-actions" ]; then
  refresh_desktop_actions
  exit 0
fi
if [ "$MODE" = "list-recent" ]; then
  list_entry_state "$RECENTS_FILE"
  exit 0
fi
if [ "$MODE" = "list-pinned" ]; then
  list_entry_state "$PINS_FILE"
  exit 0
fi
if [ "$MODE" = "pin-entry" ]; then
  ensure_materialized
  pin_entry "$PIN_ENTRY_ID"
  refresh_desktop_actions >/dev/null 2>&1 || true
  refresh_status_report >/dev/null 2>&1 || true
  printf '%s\n' "$PIN_ENTRY_ID"
  exit 0
fi
if [ "$MODE" = "unpin-entry" ]; then
  ensure_materialized
  unpin_entry "$PIN_ENTRY_ID"
  refresh_desktop_actions >/dev/null 2>&1 || true
  printf '%s\n' "$PIN_ENTRY_ID"
  exit 0
fi
ensure_materialized
if [ "$MODE" = "print-project-root" ]; then
  printf '%s\n' "$PROJECT_ROOT"
  exit 0
fi
if [ -z "$ENTRY_ID" ]; then
  resolved_entry="$(palette_cmd --no-run)"
  ENTRY_ID="$(printf '%s' "$resolved_entry" | tr -d '\r' | tail -n 1)"
  if [ -z "$ENTRY_ID" ]; then
    exit 0
  fi
fi
record_recent_entry "$ENTRY_ID"
refresh_desktop_actions >/dev/null 2>&1 || true
refresh_status_report >/dev/null 2>&1 || true
if [ "$NO_RUN" = "1" ]; then
  printf '%s\n' "$ENTRY_ID"
  exit 0
fi
set -- palette "$PROJECT_ROOT" --entry-id "$ENTRY_ID"
if [ -n "$PASS_ARGS" ]; then
  eval "set -- \"\\$@\" $PASS_ARGS"
fi
exec "$VHK_CMD" "$@"
"""
    return (script
        .replace('__VHK_BUNDLE_NAME__', bundle_name)
        .replace('__VHK_COMMAND_NAME__', command_name)
        .replace('__VHK_APP_ID__', app_id)
        .replace('__VHK_SERVICE_MODE__', service_mode)
        .replace('__VHK_SERVICE_UNIT_BASE__', service_unit_base)
        .replace('__VHK_SERVICE_UNITS__', service_units)
    )


def _render_native_assemble_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("native_install_story") or {})
    bundle_name = str(story.get("bundle_name") or "project.zip")
    return "\n".join(
        [
            "#!/usr/bin/env sh",
            "set -eu",
            "",
            'SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"',
            'NATIVE_ROOT="$SCRIPT_DIR"',
            'APP_ROOT="$SCRIPT_DIR/app"',
            'DIST_DIR="$SCRIPT_DIR/../dist"',
            'PUBLISH_ROOT="$SCRIPT_DIR/.."',
            'PROJECT_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/../../.." && pwd)"',
            'PYTHON_CMD="${PYTHON_CMD:-python}"',
            'cd "$PROJECT_DIR"',
            'printf "%s\n" "Refreshing publish bundle for native app tree..."',
            'sh "$PUBLISH_ROOT/bundle_release.sh"',
            'mkdir -p "$APP_ROOT/share/vhk/project"',
            f'cp "$DIST_DIR/{bundle_name}" "$APP_ROOT/share/vhk/project/{bundle_name}"',
            'if [ "${VHK_EMBED_RUNTIME:-0}" = "1" ] && [ -x "$PUBLISH_ROOT/runtime/embed/bootstrap_runtime_at_target.sh" ]; then',
            '  printf "%s\n" "Embedding VHK runtime into native app tree..."',
            '  sh "$PUBLISH_ROOT/runtime/embed/bootstrap_runtime_at_target.sh" "$APP_ROOT/lib/vhk-runtime" "$PYTHON_CMD"',
            'fi',
            'printf "%s\n" "Native app tree assembled under $APP_ROOT"',
            "",
        ]
    )


def _render_refresh_actions_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("native_install_story") or {})
    command_name = str(story.get("command_name") or "vhk-project")
    return "\n".join(
        [
            "#!/usr/bin/env sh",
            "set -eu",
            "",
            'SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"',
            f'exec "$SCRIPT_DIR/app/bin/{command_name}" --refresh-desktop-actions "$@"',
            "",
        ]
    )


def _render_install_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("native_install_story") or {})
    app_id = str(story.get("app_id") or "io.visualhotkey.project")
    command_name = str(story.get("command_name") or "vhk-project")
    script = """#!/usr/bin/env sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
APP_TEMPLATE="$SCRIPT_DIR/app"
PUBLISH_ROOT="$SCRIPT_DIR/.."
XDG_DATA_HOME="${{XDG_DATA_HOME:-$HOME/.local/share}}"
VHK_BIN_HOME="${{VHK_BIN_HOME:-$HOME/.local/bin}}"
APP_DEST="$XDG_DATA_HOME/vhk/apps/{command_name}"
DESKTOP_DEST="$XDG_DATA_HOME/applications/{app_id}.desktop"
METAINFO_DEST="$XDG_DATA_HOME/metainfo/{app_id}.metainfo.xml"
ICON_DEST="$XDG_DATA_HOME/icons/hicolor/256x256/apps/{app_id}.png"
PYTHON_CMD="${{PYTHON_CMD:-python}}"
mkdir -p "$XDG_DATA_HOME/applications" "$XDG_DATA_HOME/metainfo" "$XDG_DATA_HOME/icons/hicolor/256x256/apps" "$VHK_BIN_HOME"
rm -rf "$APP_DEST"
mkdir -p "$(dirname -- "$APP_DEST")"
cp -R "$APP_TEMPLATE" "$APP_DEST"
if [ "${{VHK_EMBED_RUNTIME:-0}}" = "1" ] && [ -x "$PUBLISH_ROOT/runtime/embed/bootstrap_runtime_at_target.sh" ]; then
  printf '%s\n' 'Embedding VHK runtime at final install path...'
  sh "$PUBLISH_ROOT/runtime/embed/bootstrap_runtime_at_target.sh" "$APP_DEST/lib/vhk-runtime" "$PYTHON_CMD"
fi
LAUNCHER_PATH="$VHK_BIN_HOME/{command_name}"
ln -sfn "$APP_DEST/bin/{command_name}" "$LAUNCHER_PATH"
PYTHON_CMD_RESOLVED="$PYTHON_CMD"
if ! command -v "$PYTHON_CMD_RESOLVED" >/dev/null 2>&1; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD_RESOLVED="$(command -v python3)"
  elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD_RESOLVED="$(command -v python)"
  else
    printf '%s\n' 'A Python interpreter is required to finalize the desktop entry template.' >&2
    exit 1
  fi
fi
VHK_DESKTOP_TEMPLATE="$APP_DEST/share/applications/{app_id}.desktop" \
VHK_DESKTOP_DEST="$DESKTOP_DEST" \
VHK_LAUNCHER_PATH="$LAUNCHER_PATH" \
"$PYTHON_CMD_RESOLVED" - <<'PY'
import os
from pathlib import Path

def quote(arg: str) -> str:
    value = str(arg).replace('%', '%%')
    reserved = set(" \t\n\"'\\><~|&;$*?#()`")
    if value and not any(ch in reserved for ch in value):
        return value
    escaped = value.replace('\\', '\\\\').replace('\"', '\\\\"').replace('`', '\\`').replace('$', '\\$')
    return f'"{{escaped}}"'

text = Path(os.environ['VHK_DESKTOP_TEMPLATE']).read_text()
launcher = os.environ['VHK_LAUNCHER_PATH']
text = text.replace('__VHK_LAUNCHER_EXEC__', quote(launcher))
text = text.replace('__VHK_LAUNCHER_TRYEXEC__', launcher)
Path(os.environ['VHK_DESKTOP_DEST']).write_text(text)
PY
if "$LAUNCHER_PATH" --refresh-desktop-actions >/dev/null 2>&1; then
  printf '%s\n' 'Refreshed launcher actions for installed desktop entry.'
fi
cp "$APP_DEST/share/metainfo/{app_id}.metainfo.xml" "$METAINFO_DEST"
cp "$APP_DEST/share/icons/hicolor/256x256/apps/{app_id}.png" "$ICON_DEST"
printf '%s\n' "Installed VHK native app under $APP_DEST"
printf '%s\n' "Launcher link: $LAUNCHER_PATH"
"""
    return script.format(app_id=app_id, command_name=command_name)


def _render_uninstall_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("native_install_story") or {})
    app_id = str(story.get("app_id") or "io.visualhotkey.project")
    command_name = str(story.get("command_name") or "vhk-project")
    return "\n".join(
        [
            "#!/usr/bin/env sh",
            "set -eu",
            "",
            'XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"',
            'VHK_BIN_HOME="${VHK_BIN_HOME:-$HOME/.local/bin}"',
            f'rm -rf "$XDG_DATA_HOME/vhk/apps/{command_name}"',
            f'rm -f "$VHK_BIN_HOME/{command_name}"',
            f'rm -f "$XDG_DATA_HOME/applications/{app_id}.desktop"',
            f'rm -f "$XDG_DATA_HOME/metainfo/{app_id}.metainfo.xml"',
            f'rm -f "$XDG_DATA_HOME/icons/hicolor/256x256/apps/{app_id}.png"',
            'printf "%s\\n" "Removed VHK native app install artifacts."',
            "",
        ]
    )


def _render_smoke_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("native_install_story") or {})
    app_id = str(story.get("app_id") or "io.visualhotkey.project")
    command_name = str(story.get("command_name") or "vhk-project")
    bundle_name = str(story.get("bundle_name") or "project.zip")
    return "\n".join(
        [
            "#!/usr/bin/env sh",
            "set -eu",
            "",
            'SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"',
            'SMOKE_ROOT="$SCRIPT_DIR/.smoke-root"',
            'rm -rf "$SMOKE_ROOT"',
            'mkdir -p "$SMOKE_ROOT/data" "$SMOKE_ROOT/bin"',
            'sh "$SCRIPT_DIR/assemble_native_app.sh"',
            'XDG_DATA_HOME="$SMOKE_ROOT/data" VHK_BIN_HOME="$SMOKE_ROOT/bin" sh "$SCRIPT_DIR/install_xdg_local_app.sh"',
            f'test -x "$SMOKE_ROOT/bin/{command_name}"',
            f'test -x "$SCRIPT_DIR/refresh_desktop_actions.sh"',
            f'test -f "$SMOKE_ROOT/data/applications/{app_id}.desktop"',
            f'test -f "$SMOKE_ROOT/data/vhk/apps/{command_name}/share/vhk/project/{bundle_name}"',
            f'grep -q "Actions=OpenPalette;OpenHomeDoc;OpenSupportGuide;OpenServiceGuide;OpenStatusReport;InspectBundle;RefreshBundle;RefreshLauncherActions;" "$SMOKE_ROOT/data/applications/{app_id}.desktop"',
            f'test -f "$SMOKE_ROOT/data/vhk/apps/{command_name}/share/doc/vhk/VHK_APP_HOME.md"',
            f'test -f "$SMOKE_ROOT/data/vhk/apps/{command_name}/share/doc/vhk/VHK_APP_HOME.json"',
            f'grep -q "Exec=$SMOKE_ROOT/bin/{command_name}" "$SMOKE_ROOT/data/applications/{app_id}.desktop"',
            'printf "%s\n" "Native install smoke test completed."',
            "",
        ]
    )


def _materialize_native_install_handoff(project_dir: Path, plan: dict[str, Any], *, build_dir: Path, force: bool) -> dict[str, Path]:
    root = build_dir / "native"
    app_root = root / "app"
    story = dict(plan.get("native_install_story") or {})
    paths = dict(plan.get("native_install_paths") or {})
    app_id = str(story.get("app_id") or "io.visualhotkey.project")
    command_name = str(story.get("command_name") or "vhk-project")

    (app_root / "bin").mkdir(parents=True, exist_ok=True)
    (app_root / "share/applications").mkdir(parents=True, exist_ok=True)
    (app_root / "share/metainfo").mkdir(parents=True, exist_ok=True)
    (app_root / "share/icons/hicolor/256x256/apps").mkdir(parents=True, exist_ok=True)
    (app_root / "share/vhk/project").mkdir(parents=True, exist_ok=True)
    (app_root / "share/doc/vhk").mkdir(parents=True, exist_ok=True)

    _write_if_allowed(root / "README.md", render_native_install_handoff_readme(plan), force=force)
    manifest_payload = {
        "project_root": str(project_dir),
        **paths,
        **story,
    }
    _write_if_allowed(root / "vhk_native_install_handoff.json", json.dumps(manifest_payload, indent=2, sort_keys=True) + "\n", force=force)

    refresh_script = root / "refresh_native_install_inputs.sh"
    refresh_actions_script = root / "refresh_desktop_actions.sh"
    assemble_script = root / "assemble_native_app.sh"
    install_script = root / "install_xdg_local_app.sh"
    uninstall_script = root / "uninstall_xdg_local_app.sh"
    smoke_script = root / "smoke_test_native_install.sh"
    launcher_path = app_root / "bin" / command_name
    desktop_path = app_root / "share/applications" / f"{app_id}.desktop"
    metainfo_path = app_root / "share/metainfo" / f"{app_id}.metainfo.xml"
    icon_path = app_root / "share/icons/hicolor/256x256/apps" / f"{app_id}.png"

    _write_if_allowed(refresh_script, render_native_install_refresh_script(plan), force=force)
    _write_if_allowed(assemble_script, _render_native_assemble_script(plan), force=force)
    _write_if_allowed(refresh_actions_script, _render_refresh_actions_script(plan), force=force)
    _write_if_allowed(install_script, _render_install_script(plan), force=force)
    _write_if_allowed(uninstall_script, _render_uninstall_script(plan), force=force)
    _write_if_allowed(smoke_script, _render_smoke_script(plan), force=force)
    _write_if_allowed(launcher_path, _render_native_launcher(plan), force=force)
    _write_if_allowed(desktop_path, _render_native_desktop_file(project_dir, plan), force=force)
    _write_if_allowed(metainfo_path, _render_metainfo_xml(plan), force=force)
    _write_if_allowed(icon_path, _ONE_PIXEL_PNG, force=force)

    for path in [refresh_script, refresh_actions_script, assemble_script, install_script, uninstall_script, smoke_script, launcher_path]:
        path.chmod(0o755)

    payload_docs_root = app_root / "share/doc/vhk"
    home_payload = _native_home_payload(project_dir, plan)
    _write_if_allowed(payload_docs_root / "VHK_APP_HOME.md", _render_native_home_doc(home_payload), force=force)
    _write_if_allowed(payload_docs_root / "VHK_APP_HOME.json", json.dumps(home_payload, indent=2, sort_keys=True) + "\n", force=force)
    for rel in [
        "docs/VHK_PUBLIC_SUPPORT.md",
        "docs/VHK_INSTALL_QUICKSTART.md",
        "docs/VHK_DISTRIBUTION.md",
        "docs/VHK_RUNTIME.md",
        "docs/VHK_RUNTIME_EMBED.md",
        "docs/VHK_NATIVE_INSTALL.md",
        "docs/VHK_SERVICE_COMPOSE.md",
        "docs/VHK_HOST_REHEARSAL.md",
    ]:
        _copy_if_present(project_dir / rel, payload_docs_root / Path(rel).name)

    return {
        "native_root": root,
        "native_manifest": root / "vhk_native_install_handoff.json",
        "native_readme": root / "README.md",
        "native_refresh_script": refresh_script,
        "native_assemble_script": assemble_script,
        "native_refresh_actions_script": refresh_actions_script,
        "native_install_script": install_script,
        "native_uninstall_script": uninstall_script,
        "native_smoke_script": smoke_script,
        "native_launcher": launcher_path,
        "native_desktop_file": desktop_path,
    }


def write_native_install_pack(
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
    native_doc: bool = True,
    plan_json: bool = True,
    script: bool = True,
) -> dict[str, Path]:
    project_dir = project_dir.expanduser().resolve()
    out_dir = (out_dir or (project_dir / "docs")).expanduser().resolve()
    script_dir = (script_dir or (project_dir / "scripts")).expanduser().resolve()

    write_runtime_embed_pack(
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
        embed_doc=True,
        plan_json=True,
        script=True,
    )
    plan = build_native_install_plan(
        project_dir,
        bundle_target_profile=bundle_target_profile,
        app_id=app_id,
        runtime=runtime,
        runtime_version=runtime_version,
        sdk=sdk,
        python_cmd=python_cmd,
    )
    written: dict[str, Path] = {}
    if native_doc:
        path = out_dir / "VHK_NATIVE_INSTALL.md"
        _write_if_allowed(path, render_native_install_doc(plan), force=force)
        written["native_doc"] = path
    if plan_json:
        path = out_dir / "VHK_NATIVE_INSTALL_PLAN.json"
        _write_if_allowed(path, json.dumps(plan, indent=2, sort_keys=True) + "\n", force=force)
        written["plan_json"] = path
    if script:
        path = script_dir / "vhk_refresh_native_install_pack.sh"
        _write_if_allowed(path, render_native_install_refresh_script(plan), force=force)
        path.chmod(0o755)
        written["script"] = path

    publish_root = project_dir / str((plan.get("publish_handoff") or {}).get("root") or "build/publish/project")
    written.update(_materialize_native_install_handoff(project_dir, plan, build_dir=publish_root, force=force))
    return written
