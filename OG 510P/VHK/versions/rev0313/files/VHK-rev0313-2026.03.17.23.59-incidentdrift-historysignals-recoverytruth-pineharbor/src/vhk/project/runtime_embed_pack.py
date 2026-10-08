from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from vhk.project.runtime_pack import write_runtime_pack, build_runtime_plan


def _write_if_allowed(path: Path, content: bytes | str, *, force: bool) -> None:
    if path.exists() and not force:
        raise ValueError(f"Refusing to overwrite existing file: {path}. Use --force.")
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content)


def _embed_paths(plan: dict[str, Any]) -> dict[str, str]:
    runtime_paths = dict(plan.get("runtime_paths") or {})
    runtime_root = str(runtime_paths.get("runtime_root") or "build/publish/project/runtime")
    return {
        "embed_root": f"{runtime_root}/embed",
        "embed_manifest": f"{runtime_root}/embed/vhk_runtime_embed_handoff.json",
        "embed_readme": f"{runtime_root}/embed/README.md",
        "embed_refresh_script": f"{runtime_root}/embed/refresh_runtime_embed_inputs.sh",
        "embed_bootstrap_script": f"{runtime_root}/embed/bootstrap_runtime_at_target.sh",
        "embed_native_script": f"{runtime_root}/embed/embed_native_runtime.sh",
        "embed_appimage_script": f"{runtime_root}/embed/embed_appimage_runtime.sh",
        "embed_flatpak_script": f"{runtime_root}/embed/embed_flatpak_runtime.sh",
        "embed_smoke_script": f"{runtime_root}/embed/smoke_test_embedded_runtime.sh",
        "embed_native_root": f"{runtime_root}/embed/native-runtime",
        "embed_appimage_target": f"{runtime_root}/../distribution/appimage/AppDir/usr/lib/vhk-runtime",
        "embed_flatpak_target": f"{runtime_root}/../distribution/flatpak/files/lib/vhk-runtime",
    }


def _embed_constraints(plan: dict[str, Any]) -> list[str]:
    project = dict(plan.get("project") or {})
    backend = str(project.get("desktop_backend") or "unknown")
    runtime_story = dict(plan.get("runtime_story") or {})
    bundle_story = dict(plan.get("bundle_release_story") or {})
    items = [
        "Create the virtual environment at its final target path; Python's stdlib venv docs explicitly say environments are not considered movable or copyable.",
        "Treat the embed scripts as builder-aware installers tied to one ABI/architecture class, not as proof that a wheelhouse can be copied arbitrarily between hosts.",
        "Use the native embed target first when validating a lane; AppImage and Flatpak launchers can consume the same exact-path runtime afterward, but privileged helpers and compositor bridges still need lane-specific review.",
    ]
    if backend == "wayland":
        items.append("Wayland-first lanes should keep helper/portal/compositor seams explicit even after embedding the Python runtime; the embed scripts only solve the Python/app layer.")
    if str(bundle_story.get("bundle_kind") or "project") == "release-stage" and bundle_story.get("bundle_profile_id"):
        items.append(f"This embed handoff is pinned to the `{bundle_story.get('bundle_profile_id')}` release-stage lane; rebuild the target-path runtime whenever that lane's staged payload or support posture changes.")
    optional = [str(x) for x in list(runtime_story.get("optional_dependency_groups") or []) if str(x)]
    if optional:
        items.append("Optional dependency groups remain outside the base embed flow unless you deliberately add them to the wheelhouse and rerun the target-path bootstrap scripts.")
    return items


def build_runtime_embed_plan(
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
    plan = build_runtime_plan(
        project_dir,
        bundle_target_profile=bundle_target_profile,
        app_id=app_id,
        runtime=runtime,
        runtime_version=runtime_version,
        sdk=sdk,
    )
    story = dict(plan.get("runtime_story") or {})
    dist_story = dict(plan.get("distribution_story") or {})
    bundle_story = dict(plan.get("bundle_release_story") or {})
    paths = _embed_paths(plan)
    package_name = str(story.get("package_name") or "vhk")
    exe_name = package_name if package_name != "vhk" else "vhk"
    embed_story = {
        "headline": "Generate exact-target runtime embedding helpers so native/AppImage/Flatpak lanes can bootstrap a Python environment at the path where it will actually run instead of pretending wheelhouses or venv directories are inherently portable.",
        "package_name": package_name,
        "executable_name": exe_name,
        "python_cmd": python_cmd,
        "bundle_name": str(story.get("bundle_name") or bundle_story.get("bundle_name_hint") or "project.zip"),
        "bundle_kind": str(bundle_story.get("bundle_kind") or "project"),
        "bundle_profile_id": str(bundle_story.get("bundle_profile_id") or "").strip() or None,
        "app_id": str(dist_story.get("app_id") or "io.visualhotkey.project"),
        "command_name": str(dist_story.get("command_name") or "vhk-project"),
        "targets": {
            "native": paths["embed_native_root"],
            "appimage": paths["embed_appimage_target"],
            "flatpak": paths["embed_flatpak_target"],
        },
        "constraints": _embed_constraints(plan),
        "bootstrap_contract": {
            "wheelhouse_root": str((plan.get("runtime_paths") or {}).get("runtime_wheelhouse_root") or "build/publish/project/runtime/wheelhouse"),
            "requirements_file": str((plan.get("runtime_paths") or {}).get("runtime_requirements") or "build/publish/project/runtime/requirements.runtime.txt"),
            "target_build_rule": "Build the runtime directly at its final target path; do not move or rename the created venv afterward.",
        },
    }
    plan["embed_paths"] = paths
    plan["embed_story"] = embed_story
    plan["embed_commands"] = [
        "vhk gen-runtime-pack . --force",
        "vhk gen-runtime-embed-pack . --force",
        str(bundle_story.get("bundle_command") or ""),
        f"sh {str((plan.get('runtime_paths') or {}).get('runtime_build_wheelhouse_script') or 'build/publish/project/runtime/build_wheelhouse.sh')}",
        f"sh {paths['embed_native_script']}",
        f"sh {paths['embed_smoke_script']}",
    ]
    plan["embed_commands"] = [cmd for cmd in list(plan.get("embed_commands") or []) if str(cmd).strip()]
    plan["embed_summary"] = {
        "bundle_kind": embed_story["bundle_kind"],
        "python_cmd": python_cmd,
        "target_count": len(dict(embed_story.get("targets") or {})),
        "package_name": package_name,
    }
    plan["source_contract"] = "runtime_embed_pack"
    return plan


def render_runtime_embed_doc(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    story = dict(plan.get("embed_story") or {})
    paths = dict(plan.get("embed_paths") or {})
    lines = [
        f"# VHK runtime embed pack for {project.get('name') or 'project'}",
        "",
        "Generated by `vhk gen-runtime-embed-pack`. Use it to bootstrap a VHK Python runtime at the exact path where a native/AppImage/Flatpak lane will run instead of treating virtual environments as movable artifacts.",
        "",
        "## Embed posture",
        "",
        f"- Package: `{story.get('package_name') or 'vhk'}`",
        f"- Executable: `{story.get('executable_name') or 'vhk'}`",
        f"- Bundle kind: `{story.get('bundle_kind') or 'project'}`",
        f"- Bundle name: `{story.get('bundle_name') or 'project.zip'}`",
        f"- Python command: `{story.get('python_cmd') or 'python'}`",
        "",
        "## Embed targets",
        "",
        f"- Native: `{paths.get('embed_native_root')}`",
        f"- AppImage: `{paths.get('embed_appimage_target')}`",
        f"- Flatpak: `{paths.get('embed_flatpak_target')}`",
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
    for cmd in [str(x) for x in list(plan.get("embed_commands") or []) if str(x)]:
        lines.append(f"- `{cmd}`")
    lines.append("")
    return "\n".join(lines)


def render_runtime_embed_handoff_readme(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    story = dict(plan.get("embed_story") or {})
    paths = dict(plan.get("embed_paths") or {})
    lines = [
        f"# VHK runtime embed handoff for {project.get('name') or 'project'}",
        "",
        "Generated by `vhk gen-runtime-embed-pack`. This tree keeps exact-target bootstrap scripts, target roots, and smoke tests tied to the same reviewed runtime/publish/distribution story.",
        "",
        f"- Bundle kind: `{story.get('bundle_kind') or 'project'}`",
        f"- Bundle name: `{story.get('bundle_name') or 'project.zip'}`",
        f"- Python command: `{story.get('python_cmd') or 'python'}`",
        "",
        "## Generated targets",
        "",
        f"- Native runtime root: `{paths.get('embed_native_root')}`",
        f"- AppImage runtime target: `{paths.get('embed_appimage_target')}`",
        f"- Flatpak runtime target: `{paths.get('embed_flatpak_target')}`",
        "",
        "## Flow",
        "",
        "1. Build the wheelhouse on the target ABI/architecture class.",
        "2. Run one of the exact-target embed scripts so the venv is created where it will actually live.",
        "3. Run the embedded-runtime smoke test before calling a lane runnable.",
        "",
    ]
    return "\n".join(lines)


def render_runtime_embed_refresh_script(plan: dict[str, Any]) -> str:
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
        'printf "%s\\n" "Refreshing VHK runtime embed pack inputs..."',
    ]
    runtime = 'vhk gen-runtime-pack . --force --quiet'
    embed = 'vhk gen-runtime-embed-pack . --force --quiet'
    if profile:
        runtime += f' --bundle-target-profile {profile}'
        embed += f' --bundle-target-profile {profile}'
    for cmd in [runtime, embed]:
        lines.append(f'printf "+ %s\\n" {cmd!r}')
        lines.append(f'sh -lc {cmd!r} || true')
    lines.extend([
        'printf "%s\\n" "Runtime embed pack refresh complete."',
        "",
    ])
    return "\n".join(lines)


def _render_bootstrap_runtime_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("embed_story") or {})
    package_name = str(story.get("package_name") or "vhk")
    return "\n".join(
        [
            "#!/usr/bin/env sh",
            "set -eu",
            "",
            'SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"',
            'RUNTIME_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"',
            'WHEELHOUSE_DIR="$RUNTIME_ROOT/wheelhouse"',
            'TARGET_DIR="${1:?target runtime directory required}"',
            f'PYTHON_CMD="${{2:-{str(story.get("python_cmd") or "python")}}}"',
            'if [ ! -d "$WHEELHOUSE_DIR" ] || [ -z "$(ls -A "$WHEELHOUSE_DIR" 2>/dev/null || true)" ]; then',
            '  printf "%s\\n" "Wheelhouse is empty; run ../build_wheelhouse.sh first." >&2',
            '  exit 1',
            'fi',
            'rm -rf "$TARGET_DIR"',
            'mkdir -p "$(dirname -- "$TARGET_DIR")"',
            '"$PYTHON_CMD" -m venv "$TARGET_DIR"',
            '"$TARGET_DIR/bin/python" -m pip install --upgrade pip',
            f'"$TARGET_DIR/bin/python" -m pip install --no-index --find-links "$WHEELHOUSE_DIR" {package_name}',
            'printf "%s\\n" "$TARGET_DIR" > "$TARGET_DIR/.vhk-target-path"',
            'printf "%s\\n" "Embedded VHK runtime ready at $TARGET_DIR"',
            "",
        ]
    )


def _render_embed_target_script(plan: dict[str, Any], *, mode: str) -> str:
    paths = dict(plan.get("embed_paths") or {})
    target_map = {
        "native": paths.get("embed_native_root"),
        "appimage": paths.get("embed_appimage_target"),
        "flatpak": paths.get("embed_flatpak_target"),
    }
    target = str(target_map.get(mode) or "")
    label = mode.replace("appimage", "AppImage").replace("flatpak", "Flatpak").replace("native", "native")
    return "\n".join(
        [
            "#!/usr/bin/env sh",
            "set -eu",
            "",
            'SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"',
            f'TARGET_DIR="${{1:-$SCRIPT_DIR/../{Path(target).name}}}"' if mode == "native" else f'TARGET_DIR="${{1:-$SCRIPT_DIR/../../distribution/{"appimage/AppDir/usr/lib/vhk-runtime" if mode == "appimage" else "flatpak/files/lib/vhk-runtime"}}}"',
            'PYTHON_CMD="${2:-python}"',
            f'printf "%s\\n" "Embedding VHK runtime into {label} target..."',
            'sh "$SCRIPT_DIR/bootstrap_runtime_at_target.sh" "$TARGET_DIR" "$PYTHON_CMD"',
            "",
        ]
    )


def _render_embed_smoke_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("embed_story") or {})
    paths = dict(plan.get("embed_paths") or {})
    exe = str(story.get("executable_name") or "vhk")
    bundle_name = str(story.get("bundle_name") or "project.zip")
    native = str(paths.get("embed_native_root") or "")
    appimage = str(paths.get("embed_appimage_target") or "")
    flatpak = str(paths.get("embed_flatpak_target") or "")
    return "\n".join(
        [
            "#!/usr/bin/env sh",
            "set -eu",
            "",
            'SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"',
            'MODE="${1:-native}"',
            'BUNDLE_PATH="${2:-$SCRIPT_DIR/../../dist/' + bundle_name + '}"',
            f'case "$MODE" in\n  native) TARGET_DIR="{native}" ;;\n  appimage) TARGET_DIR="$SCRIPT_DIR/../../distribution/appimage/AppDir/usr/lib/vhk-runtime" ;;\n  flatpak) TARGET_DIR="$SCRIPT_DIR/../../distribution/flatpak/files/lib/vhk-runtime" ;;\n  *) printf "%s\\n" "Unknown mode: $MODE" >&2; exit 2 ;;\nesac',
            'if [ ! -x "$TARGET_DIR/bin/' + exe + '" ]; then',
            '  printf "%s\\n" "Embedded runtime missing at $TARGET_DIR; run an embed_*_runtime.sh script first." >&2',
            '  exit 1',
            'fi',
            'exec "$TARGET_DIR/bin/' + exe + '" inspect-bundle "$BUNDLE_PATH"',
            "",
        ]
    )


def _materialize_runtime_embed_handoff(project_dir: Path, plan: dict[str, Any], *, build_dir: Path, force: bool) -> dict[str, Path]:
    runtime_root = build_dir / "runtime"
    root = runtime_root / "embed"
    root.mkdir(parents=True, exist_ok=True)
    (root / "native-runtime").mkdir(parents=True, exist_ok=True)
    story = dict(plan.get("embed_story") or {})
    paths = dict(plan.get("embed_paths") or {})

    _write_if_allowed(root / "README.md", render_runtime_embed_handoff_readme(plan), force=force)
    payload = {"project_root": str(project_dir), **paths, **story}
    _write_if_allowed(root / "vhk_runtime_embed_handoff.json", json.dumps(payload, indent=2, sort_keys=True) + "\n", force=force)

    refresh_script = root / "refresh_runtime_embed_inputs.sh"
    bootstrap_script = root / "bootstrap_runtime_at_target.sh"
    native_script = root / "embed_native_runtime.sh"
    appimage_script = root / "embed_appimage_runtime.sh"
    flatpak_script = root / "embed_flatpak_runtime.sh"
    smoke_script = root / "smoke_test_embedded_runtime.sh"

    _write_if_allowed(refresh_script, render_runtime_embed_refresh_script(plan), force=force)
    _write_if_allowed(bootstrap_script, _render_bootstrap_runtime_script(plan), force=force)
    _write_if_allowed(native_script, _render_embed_target_script(plan, mode="native"), force=force)
    _write_if_allowed(appimage_script, _render_embed_target_script(plan, mode="appimage"), force=force)
    _write_if_allowed(flatpak_script, _render_embed_target_script(plan, mode="flatpak"), force=force)
    _write_if_allowed(smoke_script, _render_embed_smoke_script(plan), force=force)

    for path in [refresh_script, bootstrap_script, native_script, appimage_script, flatpak_script, smoke_script]:
        path.chmod(0o755)

    return {
        "embed_root": root,
        "embed_manifest": root / "vhk_runtime_embed_handoff.json",
        "embed_readme": root / "README.md",
        "embed_refresh_script": refresh_script,
        "embed_bootstrap_script": bootstrap_script,
        "embed_native_script": native_script,
        "embed_appimage_script": appimage_script,
        "embed_flatpak_script": flatpak_script,
        "embed_smoke_script": smoke_script,
        "embed_native_root": root / "native-runtime",
    }


def write_runtime_embed_pack(
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
    embed_doc: bool = True,
    plan_json: bool = True,
    script: bool = True,
) -> dict[str, Path]:
    project_dir = project_dir.expanduser().resolve()
    out_dir = (out_dir or (project_dir / "docs")).expanduser().resolve()
    script_dir = (script_dir or (project_dir / "scripts")).expanduser().resolve()

    write_runtime_pack(
        project_dir,
        out_dir=out_dir,
        script_dir=script_dir,
        bundle_target_profile=bundle_target_profile,
        app_id=app_id,
        runtime=runtime,
        runtime_version=runtime_version,
        sdk=sdk,
        force=force,
        runtime_doc=True,
        plan_json=True,
        script=True,
    )
    plan = build_runtime_embed_plan(
        project_dir,
        bundle_target_profile=bundle_target_profile,
        app_id=app_id,
        runtime=runtime,
        runtime_version=runtime_version,
        sdk=sdk,
        python_cmd=python_cmd,
    )
    written: dict[str, Path] = {}
    if embed_doc:
        path = out_dir / "VHK_RUNTIME_EMBED.md"
        _write_if_allowed(path, render_runtime_embed_doc(plan), force=force)
        written["embed_doc"] = path
    if plan_json:
        path = out_dir / "VHK_RUNTIME_EMBED_PLAN.json"
        _write_if_allowed(path, json.dumps(plan, indent=2, sort_keys=True) + "\n", force=force)
        written["plan_json"] = path
    if script:
        path = script_dir / "vhk_refresh_runtime_embed_pack.sh"
        _write_if_allowed(path, render_runtime_embed_refresh_script(plan), force=force)
        path.chmod(0o755)
        written["script"] = path

    publish_root = project_dir / str((plan.get("publish_handoff") or {}).get("root") or "build/publish/project")
    written.update(_materialize_runtime_embed_handoff(project_dir, plan, build_dir=publish_root, force=force))
    return written
