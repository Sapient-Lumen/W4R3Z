from __future__ import annotations

import base64
import json
import re
import shutil
from pathlib import Path
from typing import Any

import yaml

from vhk.project.desktop_entry import desktop_exec_join
from vhk.project.publish_pack import build_publish_plan, write_publish_pack


_ONE_PIXEL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9WnXl9sAAAAASUVORK5CYII="
)


def _write_if_allowed(path: Path, content: bytes | str, *, force: bool) -> None:
    if path.exists() and not force:
        raise ValueError(f"Refusing to overwrite existing file: {path}. Use --force.")
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content)


def _slugify(text: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", str(text or "").strip()).strip("-").lower()
    return slug or "project"


def _sanitize_app_id(value: str | None, *, project_name: str) -> str:
    if value and str(value).strip():
        text = str(value).strip()
    else:
        text = f"io.visualhotkey.{_slugify(project_name).replace('-', '')}"
    parts = [part for part in re.split(r"[^A-Za-z0-9_]+", text) if part]
    if not parts:
        parts = ["io", "visualhotkey", _slugify(project_name).replace("-", "") or "project"]
    cleaned: list[str] = []
    for idx, part in enumerate(parts):
        part = part.lower()
        part = re.sub(r"[^a-z0-9_]", "", part)
        if not part:
            part = "app" if idx else "io"
        if part[0].isdigit():
            part = f"app{part}"
        cleaned.append(part)
    if len(cleaned) < 3:
        cleaned.extend(["visualhotkey", "app"])
        cleaned = cleaned[:2] + [cleaned[2] if len(cleaned) > 2 else _slugify(project_name).replace("-", "")]
    return ".".join(cleaned[:3] + cleaned[3:])


def _appstream_component_id(app_id: str) -> str:
    return app_id.strip() or "io.visualhotkey.project"


def _bundle_command_name(app_id: str) -> str:
    leaf = app_id.split(".")[-1] or "project"
    return f"vhk-{_slugify(leaf)}"


def _default_finish_args(backend: str) -> list[str]:
    backend = str(backend or "").strip().lower()
    finish_args = ["--share=ipc"]
    if backend == "x11":
        finish_args.append("--socket=fallback-x11")
    elif backend == "wayland":
        finish_args.extend(["--socket=wayland", "--socket=fallback-x11", "--device=dri"])
    else:
        finish_args.extend(["--socket=wayland", "--socket=fallback-x11"])
    return finish_args


def _distribution_constraints(plan: dict[str, Any]) -> list[str]:
    project = dict(plan.get("project") or {})
    backend = str(project.get("desktop_backend") or "unknown")
    story = dict(plan.get("bundle_release_story") or {})
    lines = [
        "Treat generated AppImage and Flatpak outputs as packaging skeletons backed by the reviewed publish handoff, not as proof of blanket Linux parity.",
        "Flatpak is best aligned with palette/launcher/portal-friendly workflows; raw-input remappers, host-global hooks, and privileged helper daemons still belong in native install lanes.",
        "Keep AppImage and Flatpak metadata aligned with the same bundle name, public support note, and install quickstart so sandboxed/package variants do not drift from the maintainer-reviewed release story.",
    ]
    if backend == "wayland":
        lines.append("This project targets a Wayland-first backend, so the Flatpak skeleton enables both Wayland and fallback X11 sockets while still leaving host-global automation claims outside the sandboxed package contract.")
    elif backend == "x11":
        lines.append("This project targets X11, so the Flatpak skeleton stays X11-oriented and should not be marketed as a Wayland automation solution without a separate lane audit.")
    if str(story.get("bundle_kind") or "project") == "release-stage":
        profile_id = str(story.get("bundle_profile_id") or "target").strip() or "target"
        lines.append(f"The current distribution handoff is pinned to the `{profile_id}` release-stage lane; regenerate it whenever that lane's staged payload changes.")
    return lines


def _distribution_paths(plan: dict[str, Any]) -> dict[str, str]:
    handoff = dict(plan.get("publish_handoff") or {})
    root = str(handoff.get("root") or "build/publish/project")
    return {
        "distribution_root": f"{root}/distribution",
        "distribution_manifest": f"{root}/distribution/vhk_distribution_handoff.json",
        "distribution_readme": f"{root}/distribution/README.md",
        "distribution_refresh_script": f"{root}/distribution/refresh_distribution_inputs.sh",
        "distribution_appimage_root": f"{root}/distribution/appimage",
        "distribution_flatpak_root": f"{root}/distribution/flatpak",
    }


def build_distribution_plan(
    project_dir: Path,
    *,
    bundle_target_profile: str | None = None,
    app_id: str | None = None,
    runtime: str = "org.freedesktop.Platform",
    runtime_version: str = "24.08",
    sdk: str = "org.freedesktop.Sdk",
) -> dict[str, Any]:
    project_dir = project_dir.expanduser().resolve()
    publish_plan = build_publish_plan(project_dir, bundle_target_profile=bundle_target_profile)
    project = dict(publish_plan.get("project") or {})
    project_name = str(project.get("name") or project_dir.name)
    backend = str(project.get("desktop_backend") or "unknown")
    app_id_value = _sanitize_app_id(app_id, project_name=project_name)
    command_name = _bundle_command_name(app_id_value)
    finish_args = _default_finish_args(backend)
    bundle_story = dict(publish_plan.get("bundle_release_story") or {})
    publish_handoff = dict(publish_plan.get("publish_handoff") or {})
    bundle_name = str(bundle_story.get("bundle_name_hint") or f"{project_name}.zip").strip() or f"{project_name}.zip"
    rel_paths = _distribution_paths(publish_plan)
    appdir_root = f"{rel_paths['distribution_appimage_root']}/AppDir"
    app_icon = f"{appdir_root}/usr/share/icons/hicolor/256x256/apps/{app_id_value}.png"
    app_desktop = f"{appdir_root}/{app_id_value}.desktop"
    app_usr_desktop = f"{appdir_root}/usr/share/applications/{app_id_value}.desktop"
    app_metainfo = f"{appdir_root}/usr/share/metainfo/{app_id_value}.metainfo.xml"
    flatpak_root = rel_paths["distribution_flatpak_root"]
    flatpak_manifest = f"{flatpak_root}/{app_id_value}.yaml"
    flatpak_files_root = f"{flatpak_root}/files"
    flatpak_bundle_dest = f"{flatpak_files_root}/share/vhk/project/{bundle_name}"

    distribution_story = {
        "headline": "Generate reviewable AppImage and Flatpak packaging skeletons from the same publish/release-stage handoff instead of hand-writing distro metadata later.",
        "app_id": app_id_value,
        "command_name": command_name,
        "bundle_name": bundle_name,
        "bundle_kind": str(bundle_story.get("bundle_kind") or "project"),
        "bundle_profile_id": str(bundle_story.get("bundle_profile_id") or "").strip() or None,
        "runtime": runtime,
        "runtime_version": str(runtime_version),
        "sdk": sdk,
        "finish_args": finish_args,
        "constraints": _distribution_constraints(publish_plan),
        "appimage": {
            "root": rel_paths["distribution_appimage_root"],
            "appdir_root": appdir_root,
            "build_script": f"{rel_paths['distribution_appimage_root']}/build_appimage.sh",
            "apprun": f"{appdir_root}/AppRun",
            "launcher": f"{appdir_root}/usr/bin/vhk-launch",
            "desktop_root_entry": app_desktop,
            "desktop_file": app_usr_desktop,
            "icon_file": app_icon,
            "diricon": f"{appdir_root}/.DirIcon",
            "metainfo_file": app_metainfo,
            "bundle_payload_path": f"{appdir_root}/usr/share/vhk/project/{bundle_name}",
            "validation_commands": [
                "desktop-file-validate AppDir/usr/share/applications/<app-id>.desktop",
                "appstreamcli validate --no-net AppDir/usr/share/metainfo/<app-id>.metainfo.xml",
            ],
        },
        "flatpak": {
            "root": flatpak_root,
            "manifest_path": flatpak_manifest,
            "build_script": f"{flatpak_root}/build_flatpak.sh",
            "files_root": flatpak_files_root,
            "launcher": f"{flatpak_files_root}/bin/vhk-launch",
            "desktop_file": f"{flatpak_files_root}/share/applications/{app_id_value}.desktop",
            "icon_file": f"{flatpak_files_root}/share/icons/hicolor/256x256/apps/{app_id_value}.png",
            "metainfo_file": f"{flatpak_files_root}/share/metainfo/{app_id_value}.metainfo.xml",
            "bundle_payload_path": flatpak_bundle_dest,
            "validation_commands": [
                f"desktop-file-validate {Path(flatpak_files_root) / 'share/applications' / (app_id_value + '.desktop')}",
                f"appstreamcli validate --no-net {Path(flatpak_files_root) / 'share/metainfo' / (app_id_value + '.metainfo.xml')}",
                f"flatpak-builder --show-manifest {Path(flatpak_manifest).name}",
            ],
        },
    }

    distribution_commands = [
        "vhk gen-publish-pack . --force",
        "vhk gen-distribution-pack . --force",
        str(bundle_story.get("bundle_command") or ""),
    ]
    distribution_commands = [cmd for cmd in distribution_commands if cmd]

    publish_plan["distribution_paths"] = rel_paths
    publish_plan["distribution_story"] = distribution_story
    publish_plan["distribution_commands"] = distribution_commands
    publish_plan["distribution_summary"] = {
        "app_id": app_id_value,
        "runtime": runtime,
        "runtime_version": str(runtime_version),
        "sdk": sdk,
        "finish_arg_count": len(finish_args),
        "bundle_kind": str(bundle_story.get("bundle_kind") or "project"),
    }
    publish_plan["source_contract"] = "distribution_pack"
    return publish_plan


def _render_metainfo_xml(plan: dict[str, Any]) -> str:
    story = dict(plan.get("distribution_story") or {})
    bundle_story = dict(plan.get("bundle_release_story") or {})
    project = dict(plan.get("project") or {})
    app_id = _appstream_component_id(str(story.get("app_id") or "io.visualhotkey.project"))
    summary = str(project.get("name") or "VHK project")
    bundle_line = str(bundle_story.get("bundle_kind") or "project")
    profile = str(bundle_story.get("bundle_profile_id") or "").strip()
    description = [
        "Planner-backed VisualHotKey distribution skeleton.",
        f"Bundle shape: {bundle_line}.",
    ]
    if profile:
        description.append(f"Pinned release-stage lane: {profile}.")
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<component type="desktop-application">',
        f"  <id>{app_id}</id>",
        f"  <name>{summary}</name>",
        "  <summary>Linux-native VHK packaging skeleton</summary>",
        "  <metadata_license>CC0-1.0</metadata_license>",
        "  <project_license>LicenseRef-proprietary</project_license>",
        '  <description>',
    ]
    for paragraph in description:
        lines.append(f"    <p>{paragraph}</p>")
    lines.extend([
        "  </description>",
        '  <launchable type="desktop-id">' + app_id + '.desktop</launchable>',
        "</component>",
        "",
    ])
    return "\n".join(lines)


def _render_desktop_file(plan: dict[str, Any]) -> str:
    story = dict(plan.get("distribution_story") or {})
    project = dict(plan.get("project") or {})
    app_id = str(story.get("app_id") or "io.visualhotkey.project")
    command_name = str(story.get("command_name") or "vhk-project")
    exec_line = desktop_exec_join([command_name])
    name = str(project.get("name") or "VHK project")
    lines = [
        "[Desktop Entry]",
        "Type=Application",
        f"Name={name}",
        "Comment=Planner-backed VHK distribution skeleton",
        f"Exec={exec_line}",
        f"Icon={app_id}",
        "Categories=Utility;Development;",
        "Terminal=true",
        "StartupNotify=false",
        "",
    ]
    return "\n".join(lines)


def _render_runtime_launcher(plan: dict[str, Any], *, appdir_style: bool) -> str:
    story = dict(plan.get("distribution_story") or {})
    bundle_story = dict(plan.get("bundle_release_story") or {})
    bundle_name = str(story.get("bundle_name") or bundle_story.get("bundle_name_hint") or "project.zip")
    bundle_ref = f'${{APPDIR:-/app}}/usr/share/vhk/project/{bundle_name}' if appdir_style else f"/app/share/vhk/project/{bundle_name}"
    if appdir_style:
        bundle_ref = f'${{APPDIR}}/usr/share/vhk/project/{bundle_name}'
    lines = [
        "#!/usr/bin/env sh",
        "set -eu",
    ]
    if appdir_style:
        lines.extend([
            'APPDIR="${APPDIR:-$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)}"',
            'EMBEDDED_VHK="$APPDIR/usr/lib/vhk-runtime/bin/vhk"',
            f'BUNDLE_PATH="{bundle_ref}"',
        ])
    else:
        lines.extend([
            'EMBEDDED_VHK="/app/lib/vhk-runtime/bin/vhk"',
            f'BUNDLE_PATH="{bundle_ref}"',
        ])
    lines.extend([
        'if [ -x "$EMBEDDED_VHK" ]; then',
        '  exec "$EMBEDDED_VHK" inspect-bundle "$BUNDLE_PATH" "$@"',
        'fi',
        'if command -v vhk >/dev/null 2>&1; then',
        '  exec vhk inspect-bundle "$BUNDLE_PATH" "$@"',
        'fi',
        'printf "%s\n" "This is a VHK distribution skeleton, not a fully embedded runtime."',
        'printf "%s\n" "Bundle payload: $BUNDLE_PATH"',
        'printf "%s\n" "Install or embed the VHK runtime before shipping this package as runnable automation software."',
        'exit 1',
        "",
    ])
    return "\n".join(lines)


def _render_apprun_script() -> str:
    return "\n".join(
        [
            "#!/usr/bin/env sh",
            "set -eu",
            'APPDIR="${APPDIR:-$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)}"',
            'exec "$APPDIR/usr/bin/vhk-launch" "$@"',
            "",
        ]
    )


def _render_appimage_build_script(plan: dict[str, Any], *, distribution_root: Path, project_dir: Path) -> str:
    publish_handoff = dict(plan.get("publish_handoff") or {})
    story = dict(plan.get("distribution_story") or {})
    bundle_name = str(story.get("bundle_name") or "project.zip")
    publish_root_rel = str(publish_handoff.get("root") or "build/publish/project")
    rel = project_dir.relative_to(distribution_root.parent.parent).as_posix() if False else None
    # compute project dir from script location: appimage dir -> distribution -> publish root -> project root
    publish_root_parent = distribution_root.parent.parent
    project_rel = project_dir.relative_to(publish_root_parent.parent.parent) if False else None
    header = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        'SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"',
        'DIST_DIR="$SCRIPT_DIR/../../dist"',
        'APPDIR="$SCRIPT_DIR/AppDir"',
        'PUBLISH_ROOT="$SCRIPT_DIR/../.."',
        'PROJECT_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/../../../.." && pwd)"',
        'cd "$PROJECT_DIR"',
        "",
        'printf "%s\\n" "Refreshing publish bundle for AppImage skeleton..."',
        'sh "$PUBLISH_ROOT/bundle_release.sh"',
        "if [ \"${VHK_EMBED_RUNTIME:-0}\" = \"1\" ] && [ -x \"$PUBLISH_ROOT/runtime/embed/embed_appimage_runtime.sh\" ]; then",
        "  printf \"%s\\n\" \"Embedding VHK runtime into AppDir target...\"",
        "  sh \"$PUBLISH_ROOT/runtime/embed/embed_appimage_runtime.sh\"",
        "fi",
        f'mkdir -p "$APPDIR/usr/share/vhk/project"',
        f'cp "$DIST_DIR/{bundle_name}" "$APPDIR/usr/share/vhk/project/{bundle_name}"',
        'printf "%s\\n" "AppDir payload refreshed."',
        'if command -v linuxdeploy >/dev/null 2>&1 && command -v appimagetool >/dev/null 2>&1; then',
        '  linuxdeploy --appdir "$APPDIR" --output appimage',
        'else',
        '  printf "%s\\n" "Install linuxdeploy and appimagetool to emit the final AppImage."',
        'fi',
        "",
    ]
    return "\n".join(header)


def _render_flatpak_manifest(plan: dict[str, Any]) -> str:
    story = dict(plan.get("distribution_story") or {})
    flatpak = dict(story.get("flatpak") or {})
    app_id = str(story.get("app_id") or "io.visualhotkey.project")
    command_name = str(story.get("command_name") or "vhk-project")
    bundle_name = str(story.get("bundle_name") or "project.zip")
    manifest = {
        "app-id": app_id,
        "runtime": str(story.get("runtime") or "org.freedesktop.Platform"),
        "runtime-version": str(story.get("runtime_version") or "24.08"),
        "sdk": str(story.get("sdk") or "org.freedesktop.Sdk"),
        "command": command_name,
        "finish-args": [str(x) for x in list(story.get("finish_args") or []) if str(x)],
        "modules": [
            {
                "name": _slugify(app_id),
                "buildsystem": "simple",
                "build-commands": [
                    f"install -Dm755 files/bin/vhk-launch /app/bin/{command_name}",
                    f"install -Dm644 files/share/applications/{app_id}.desktop /app/share/applications/{app_id}.desktop",
                    f"install -Dm644 files/share/metainfo/{app_id}.metainfo.xml /app/share/metainfo/{app_id}.metainfo.xml",
                    f"install -Dm644 files/share/icons/hicolor/256x256/apps/{app_id}.png /app/share/icons/hicolor/256x256/apps/{app_id}.png",
                    f"install -Dm644 files/share/vhk/project/{bundle_name} /app/share/vhk/project/{bundle_name}",
                ],
                "sources": [
                    {"type": "dir", "path": "files"},
                ],
            }
        ],
    }
    return yaml.safe_dump(manifest, sort_keys=False)


def _render_flatpak_build_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("distribution_story") or {})
    flatpak = dict(story.get("flatpak") or {})
    bundle_name = str(story.get("bundle_name") or "project.zip")
    manifest_name = Path(str(flatpak.get("manifest_path") or "manifest.yaml")).name
    lines = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        'SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"',
        'FILES_DIR="$SCRIPT_DIR/files"',
        'DIST_DIR="$SCRIPT_DIR/../../dist"',
        'PUBLISH_ROOT="$SCRIPT_DIR/../.."',
        'PROJECT_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/../../../.." && pwd)"',
        'cd "$PROJECT_DIR"',
        "",
        'printf "%s\\n" "Refreshing publish bundle for Flatpak skeleton..."',
        'sh "$PUBLISH_ROOT/bundle_release.sh"',
        "if [ \"${VHK_EMBED_RUNTIME:-0}\" = \"1\" ] && [ -x \"$PUBLISH_ROOT/runtime/embed/embed_flatpak_runtime.sh\" ]; then",
        "  printf \"%s\\n\" \"Embedding VHK runtime into Flatpak files target...\"",
        "  sh \"$PUBLISH_ROOT/runtime/embed/embed_flatpak_runtime.sh\"",
        "fi",
        'mkdir -p "$FILES_DIR/share/vhk/project"',
        f'cp "$DIST_DIR/{bundle_name}" "$FILES_DIR/share/vhk/project/{bundle_name}"',
        'printf "%s\\n" "Flatpak files tree refreshed."',
        'if command -v flatpak-builder >/dev/null 2>&1; then',
        f'  flatpak-builder --force-clean --user build-dir "$SCRIPT_DIR/{manifest_name}"',
        'else',
        '  printf "%s\\n" "Install flatpak-builder to build the Flatpak from this skeleton."',
        'fi',
        "",
    ]
    return "\n".join(lines)


def render_distribution_handoff_readme(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    story = dict(plan.get("distribution_story") or {})
    paths = dict(plan.get("distribution_paths") or {})
    lines = [
        f"# VHK distribution handoff for {project.get('name') or 'project'}",
        "",
        "Generated by `vhk gen-distribution-pack`. This tree keeps package metadata, launcher wrappers, and bundle-refresh scripts tied to the same publish handoff.",
        "",
        f"- App id: `{story.get('app_id') or 'io.visualhotkey.project'}`",
        f"- Runtime: `{story.get('runtime') or 'org.freedesktop.Platform'}` / `{story.get('runtime_version') or '24.08'}`",
        f"- SDK: `{story.get('sdk') or 'org.freedesktop.Sdk'}`",
        f"- Bundle kind: `{story.get('bundle_kind') or 'project'}`",
    ]
    if story.get("bundle_profile_id"):
        lines.append(f"- Target profile: `{story.get('bundle_profile_id')}`")
    lines.extend([
        "",
        "## Generated packaging roots",
        "",
        f"- AppImage: `{paths.get('distribution_appimage_root') or 'build/publish/project/distribution/appimage'}`",
        f"- Flatpak: `{paths.get('distribution_flatpak_root') or 'build/publish/project/distribution/flatpak'}`",
        "",
        "## Constraints",
        "",
    ])
    for item in [str(x) for x in list(story.get("constraints") or []) if str(x)]:
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## Refresh/build flow",
        "",
        "1. Refresh publish inputs and release the current bundle via the publish handoff.",
        "2. Refresh the AppImage/Flatpak skeleton payload trees.",
        "3. Optionally set `VHK_EMBED_RUNTIME=1` when running the generated AppImage/Flatpak build scripts so they bootstrap the exact-path runtime before final package assembly.",
        "4. Validate desktop/metadata files, then decide whether the target lane really belongs in a sandboxed package or should stay native.",
        "",
    ])
    return "\n".join(lines)


def render_distribution_doc(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    story = dict(plan.get("distribution_story") or {})
    bundle_story = dict(plan.get("bundle_release_story") or {})
    paths = dict(plan.get("distribution_paths") or {})
    lines = [
        f"# VHK distribution pack for {project.get('name') or 'project'}",
        "",
        "Generated by `vhk gen-distribution-pack`. Use it to turn the publish handoff into reviewable package metadata rather than inventing AppImage/Flatpak inputs at release time.",
        "",
        "## Distribution posture",
        "",
        f"- App id: `{story.get('app_id') or 'io.visualhotkey.project'}`",
        f"- Runtime: `{story.get('runtime') or 'org.freedesktop.Platform'}` `{story.get('runtime_version') or '24.08'}`",
        f"- SDK: `{story.get('sdk') or 'org.freedesktop.Sdk'}`",
        f"- Bundle kind: `{bundle_story.get('bundle_kind') or 'project'}`",
        f"- Bundle name: `{story.get('bundle_name') or bundle_story.get('bundle_name_hint') or 'project.zip'}`",
    ]
    if bundle_story.get("bundle_profile_id"):
        lines.append(f"- Target profile: `{bundle_story.get('bundle_profile_id')}` ({bundle_story.get('bundle_profile_title') or bundle_story.get('bundle_profile_id')})")
    lines.extend([
        "",
        "## Flatpak finish args",
        "",
    ])
    for arg in [str(x) for x in list(story.get("finish_args") or []) if str(x)]:
        lines.append(f"- `{arg}`")
    lines.extend([
        "",
        "## Packaging constraints",
        "",
    ])
    for item in [str(x) for x in list(story.get("constraints") or []) if str(x)]:
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## Generated paths",
        "",
        f"- Distribution root: `{paths.get('distribution_root')}`",
        f"- AppImage root: `{paths.get('distribution_appimage_root')}`",
        f"- Flatpak root: `{paths.get('distribution_flatpak_root')}`",
        "",
        "## Review commands",
        "",
    ])
    for cmd in [str(x) for x in list(plan.get("distribution_commands") or []) if str(x)]:
        lines.append(f"- `{cmd}`")
    lines.extend([
        "- `VHK_EMBED_RUNTIME=1 sh build/publish/<bundle-name>/distribution/appimage/build_appimage.sh`",
        "- `VHK_EMBED_RUNTIME=1 sh build/publish/<bundle-name>/distribution/flatpak/build_flatpak.sh`",
    ])
    lines.append("")
    return "\n".join(lines)


def render_distribution_refresh_script(plan: dict[str, Any], *, distribution_root: Path, project_dir: Path) -> str:
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
        'printf "%s\\n" "Refreshing VHK distribution pack inputs..."',
    ]
    publish_cmd = 'vhk gen-publish-pack . --force --quiet'
    dist_cmd = 'vhk gen-distribution-pack . --force --quiet'
    if profile:
        publish_cmd += f' --bundle-target-profile {profile}'
        dist_cmd += f' --bundle-target-profile {profile}'
    lines.extend([
        f'printf "+ %s\\n" {publish_cmd!r}',
        f'sh -lc {publish_cmd!r} || true',
        f'printf "+ %s\\n" {dist_cmd!r}',
        f'sh -lc {dist_cmd!r} || true',
        'printf "%s\\n" "Distribution pack refresh complete."',
        "",
    ])
    return "\n".join(lines)


def _copy_if_present(src: Path, dest: Path) -> bool:
    if not src.is_file():
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return True


def _materialize_distribution_handoff(project_dir: Path, plan: dict[str, Any], *, build_dir: Path, force: bool) -> dict[str, Path]:
    publish_handoff = dict(plan.get("publish_handoff") or {})
    if not publish_handoff:
        return {}
    paths = dict(plan.get("distribution_paths") or {})
    root = build_dir / "distribution"
    appimage_root = root / "appimage"
    appdir_root = appimage_root / "AppDir"
    flatpak_root = root / "flatpak"
    files_root = flatpak_root / "files"
    story = dict(plan.get("distribution_story") or {})
    appimage = dict(story.get("appimage") or {})
    flatpak = dict(story.get("flatpak") or {})
    app_id = str(story.get("app_id") or "io.visualhotkey.project")

    root.mkdir(parents=True, exist_ok=True)
    (appdir_root / "usr/bin").mkdir(parents=True, exist_ok=True)
    (appdir_root / "usr/share/applications").mkdir(parents=True, exist_ok=True)
    (appdir_root / "usr/share/metainfo").mkdir(parents=True, exist_ok=True)
    (appdir_root / "usr/share/icons/hicolor/256x256/apps").mkdir(parents=True, exist_ok=True)
    (appdir_root / "usr/share/vhk/project").mkdir(parents=True, exist_ok=True)
    (files_root / "bin").mkdir(parents=True, exist_ok=True)
    (files_root / "share/applications").mkdir(parents=True, exist_ok=True)
    (files_root / "share/metainfo").mkdir(parents=True, exist_ok=True)
    (files_root / "share/icons/hicolor/256x256/apps").mkdir(parents=True, exist_ok=True)
    (files_root / "share/vhk/project").mkdir(parents=True, exist_ok=True)

    desktop = _render_desktop_file(plan)
    metainfo = _render_metainfo_xml(plan)
    appimage_launcher = _render_runtime_launcher(plan, appdir_style=True)
    flatpak_launcher = _render_runtime_launcher(plan, appdir_style=False)

    _write_if_allowed(root / "README.md", render_distribution_handoff_readme(plan), force=force)
    manifest_payload = {
        "project_root": str(project_dir),
        **paths,
        **{k: v for k, v in story.items() if k not in {"appimage", "flatpak"}},
        "appimage": appimage,
        "flatpak": flatpak,
    }
    _write_if_allowed(root / "vhk_distribution_handoff.json", json.dumps(manifest_payload, indent=2, sort_keys=True) + "\n", force=force)
    refresh_script = root / "refresh_distribution_inputs.sh"
    _write_if_allowed(refresh_script, render_distribution_refresh_script(plan, distribution_root=root, project_dir=project_dir), force=force)
    refresh_script.chmod(0o755)

    app_run = appdir_root / "AppRun"
    app_launcher = appdir_root / "usr/bin/vhk-launch"
    app_root_desktop = appdir_root / f"{app_id}.desktop"
    app_usr_desktop = appdir_root / "usr/share/applications" / f"{app_id}.desktop"
    app_metainfo = appdir_root / "usr/share/metainfo" / f"{app_id}.metainfo.xml"
    app_icon = appdir_root / "usr/share/icons/hicolor/256x256/apps" / f"{app_id}.png"
    app_diricon = appdir_root / ".DirIcon"

    _write_if_allowed(app_run, _render_apprun_script(), force=force)
    _write_if_allowed(app_launcher, appimage_launcher, force=force)
    _write_if_allowed(app_root_desktop, desktop, force=force)
    _write_if_allowed(app_usr_desktop, desktop, force=force)
    _write_if_allowed(app_metainfo, metainfo, force=force)
    _write_if_allowed(app_icon, _ONE_PIXEL_PNG, force=force)
    _write_if_allowed(app_diricon, _ONE_PIXEL_PNG, force=force)
    app_run.chmod(0o755)
    app_launcher.chmod(0o755)

    appimage_script = appimage_root / "build_appimage.sh"
    _write_if_allowed(appimage_script, _render_appimage_build_script(plan, distribution_root=root, project_dir=project_dir), force=force)
    appimage_script.chmod(0o755)

    flatpak_launcher_path = files_root / "bin/vhk-launch"
    flatpak_desktop = files_root / "share/applications" / f"{app_id}.desktop"
    flatpak_metainfo = files_root / "share/metainfo" / f"{app_id}.metainfo.xml"
    flatpak_icon = files_root / "share/icons/hicolor/256x256/apps" / f"{app_id}.png"
    flatpak_manifest = flatpak_root / f"{app_id}.yaml"
    flatpak_script = flatpak_root / "build_flatpak.sh"
    _write_if_allowed(flatpak_launcher_path, flatpak_launcher, force=force)
    _write_if_allowed(flatpak_desktop, desktop, force=force)
    _write_if_allowed(flatpak_metainfo, metainfo, force=force)
    _write_if_allowed(flatpak_icon, _ONE_PIXEL_PNG, force=force)
    _write_if_allowed(flatpak_manifest, _render_flatpak_manifest(plan), force=force)
    _write_if_allowed(flatpak_script, _render_flatpak_build_script(plan), force=force)
    flatpak_launcher_path.chmod(0o755)
    flatpak_script.chmod(0o755)

    copied_publish_docs: list[str] = []
    payload_docs_root = root / "payload/docs"
    for rel in [
        "docs/VHK_PUBLIC_SUPPORT.md",
        "docs/VHK_INSTALL_QUICKSTART.md",
        "docs/VHK_PUBLISH_PLAN.json",
        "docs/VHK_DISTRIBUTION.md",
        "docs/VHK_DISTRIBUTION_PLAN.json",
    ]:
        if _copy_if_present(project_dir / rel, payload_docs_root / Path(rel).name):
            copied_publish_docs.append(rel)

    return {
        "distribution_root": root,
        "distribution_manifest": root / "vhk_distribution_handoff.json",
        "distribution_readme": root / "README.md",
        "distribution_refresh_script": refresh_script,
        "distribution_appimage_script": appimage_script,
        "distribution_flatpak_manifest": flatpak_manifest,
        "distribution_flatpak_script": flatpak_script,
    }


def write_distribution_pack(
    project_dir: Path,
    *,
    out_dir: Path | None = None,
    script_dir: Path | None = None,
    bundle_target_profile: str | None = None,
    app_id: str | None = None,
    runtime: str = "org.freedesktop.Platform",
    runtime_version: str = "24.08",
    sdk: str = "org.freedesktop.Sdk",
    force: bool = False,
    distribution_doc: bool = True,
    plan_json: bool = True,
    script: bool = True,
) -> dict[str, Path]:
    project_dir = project_dir.expanduser().resolve()
    out_dir = (out_dir or (project_dir / "docs")).expanduser().resolve()
    script_dir = (script_dir or (project_dir / "scripts")).expanduser().resolve()

    write_publish_pack(
        project_dir,
        bundle_target_profile=bundle_target_profile,
        force=force,
        support_doc=True,
        quickstart=True,
        plan_json=True,
        script=True,
    )
    plan = build_distribution_plan(
        project_dir,
        bundle_target_profile=bundle_target_profile,
        app_id=app_id,
        runtime=runtime,
        runtime_version=runtime_version,
        sdk=sdk,
    )
    written: dict[str, Path] = {}
    if distribution_doc:
        path = out_dir / "VHK_DISTRIBUTION.md"
        _write_if_allowed(path, render_distribution_doc(plan), force=force)
        written["distribution_doc"] = path
    if plan_json:
        path = out_dir / "VHK_DISTRIBUTION_PLAN.json"
        _write_if_allowed(path, json.dumps(plan, indent=2, sort_keys=True) + "\n", force=force)
        written["plan_json"] = path
    if script:
        path = script_dir / "vhk_refresh_distribution_pack.sh"
        script_text = render_distribution_refresh_script(plan, distribution_root=project_dir / "build" / "publish" / Path(str((plan.get("publish_handoff") or {}).get("slug") or "project")) / "distribution", project_dir=project_dir)
        _write_if_allowed(path, script_text, force=force)
        path.chmod(0o755)
        written["script"] = path

    publish_root = project_dir / str((plan.get("publish_handoff") or {}).get("root") or "build/publish/project")
    written.update(_materialize_distribution_handoff(project_dir, plan, build_dir=publish_root, force=force))
    return written
