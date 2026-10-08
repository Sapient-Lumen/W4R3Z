from __future__ import annotations

import json
import shutil
import tomllib
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any

from vhk import __version__ as VHK_VERSION
from vhk.project.distribution_pack import build_distribution_plan, write_distribution_pack


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


def _repo_pyproject() -> Path | None:
    current = Path(__file__).resolve()
    for parent in current.parents:
        candidate = parent / "pyproject.toml"
        if candidate.is_file():
            return candidate
    return None


def _strip_marker(spec: str) -> str:
    return str(spec).split(";", 1)[0].strip()


def _load_runtime_package_metadata() -> dict[str, Any]:
    pyproject = _repo_pyproject()
    if pyproject is not None:
        payload = tomllib.loads(pyproject.read_text())
        project = dict(payload.get("project") or {})
        optional = dict(project.get("optional-dependencies") or {})
        return {
            "package_name": str(project.get("name") or "vhk"),
            "package_version": str(project.get("version") or VHK_VERSION),
            "requires_python": str(project.get("requires-python") or ">=3.10"),
            "dependencies": [_strip_marker(item) for item in list(project.get("dependencies") or []) if str(item).strip()],
            "optional_dependency_groups": sorted(str(key) for key in optional.keys()),
            "build_system_requires": [str(item) for item in list((payload.get("build-system") or {}).get("requires") or []) if str(item).strip()],
            "source": str(pyproject),
        }

    name = "vhk"
    version = VHK_VERSION
    try:
        version = importlib_metadata.version(name)
    except Exception:
        pass
    dependencies = []
    try:
        dependencies = [_strip_marker(item) for item in list(importlib_metadata.requires(name) or []) if str(item).strip() and "extra ==" not in str(item)]
    except Exception:
        dependencies = []
    requires_python = ">=3.10"
    try:
        meta = importlib_metadata.metadata(name)
        requires_python = str(meta.get("Requires-Python") or requires_python)
    except Exception:
        pass
    return {
        "package_name": name,
        "package_version": version,
        "requires_python": requires_python,
        "dependencies": dependencies,
        "optional_dependency_groups": [],
        "build_system_requires": ["setuptools>=68", "wheel"],
        "source": "importlib.metadata",
    }


def _runtime_paths(plan: dict[str, Any]) -> dict[str, str]:
    handoff = dict(plan.get("publish_handoff") or {})
    root = str(handoff.get("root") or "build/publish/project")
    return {
        "runtime_root": f"{root}/runtime",
        "runtime_manifest": f"{root}/runtime/vhk_runtime_handoff.json",
        "runtime_readme": f"{root}/runtime/README.md",
        "runtime_refresh_script": f"{root}/runtime/refresh_runtime_inputs.sh",
        "runtime_requirements": f"{root}/runtime/requirements.runtime.txt",
        "runtime_build_constraints": f"{root}/runtime/build-requirements.txt",
        "runtime_wheelhouse_root": f"{root}/runtime/wheelhouse",
        "runtime_wheelhouse_readme": f"{root}/runtime/wheelhouse/README.md",
        "runtime_build_wheelhouse_script": f"{root}/runtime/build_wheelhouse.sh",
        "runtime_smoke_install_script": f"{root}/runtime/smoke_test_offline_install.sh",
        "runtime_run_bundle_script": f"{root}/runtime/run_bundle_with_runtime.sh",
        "runtime_flatpak_generator_script": f"{root}/runtime/emit_flatpak_python_modules.sh",
    }


def _runtime_constraints(plan: dict[str, Any], runtime_meta: dict[str, Any]) -> list[str]:
    story = dict(plan.get("bundle_release_story") or {})
    project = dict(plan.get("project") or {})
    items = [
        "Treat the generated wheelhouse as a reproducible runtime handoff, not as proof that packaged lanes are already self-contained.",
        "Build the wheelhouse on the same target OS/architecture class you intend to ship, because compiled wheels are typically machine-specific.",
        "Use virtual environments for smoke tests and native installs instead of mutating system Python; the runtime pack is meant to stay reviewable and reversible.",
        "Keep host-global remapper helpers, uinput daemons, and compositor-native integrations outside the Python wheelhouse contract unless that helper is audited separately.",
    ]
    backend = str(project.get("desktop_backend") or "unknown")
    if backend == "wayland":
        items.append("For Wayland-first projects, treat the wheelhouse as the app/runtime layer and keep portal/helper/compositor boundaries explicit in release notes and package manifests.")
    if str(story.get("bundle_kind") or "project") == "release-stage" and story.get("bundle_profile_id"):
        items.append(f"This runtime handoff is pinned to the `{story.get('bundle_profile_id')}` release-stage lane; rebuild it whenever that lane's staged payload or support posture changes.")
    if runtime_meta.get("optional_dependency_groups"):
        groups = ", ".join(str(x) for x in list(runtime_meta.get("optional_dependency_groups") or []))
        items.append(f"Optional dependency groups remain opt-in and are not bundled into the base runtime wheelhouse by default: {groups}.")
    return items


def build_runtime_plan(
    project_dir: Path,
    *,
    bundle_target_profile: str | None = None,
    app_id: str | None = None,
    runtime: str = "org.freedesktop.Platform",
    runtime_version: str = "24.08",
    sdk: str = "org.freedesktop.Sdk",
) -> dict[str, Any]:
    project_dir = project_dir.expanduser().resolve()
    plan = build_distribution_plan(
        project_dir,
        bundle_target_profile=bundle_target_profile,
        app_id=app_id,
        runtime=runtime,
        runtime_version=runtime_version,
        sdk=sdk,
    )
    runtime_meta = _load_runtime_package_metadata()
    paths = _runtime_paths(plan)
    bundle_story = dict(plan.get("bundle_release_story") or {})
    distribution_story = dict(plan.get("distribution_story") or {})
    package_name = str(runtime_meta.get("package_name") or "vhk")
    package_version = str(runtime_meta.get("package_version") or VHK_VERSION)
    dependencies = [str(item) for item in list(runtime_meta.get("dependencies") or []) if str(item).strip()]
    runtime_story = {
        "headline": "Generate a reviewable VHK Python runtime handoff (requirements + wheelhouse scripts + offline smoke tests) so package/native release lanes stop pretending that runtime embedding is somebody else's problem.",
        "package_name": package_name,
        "package_version": package_version,
        "requires_python": str(runtime_meta.get("requires_python") or ">=3.10"),
        "dependencies": dependencies,
        "dependency_count": len(dependencies),
        "optional_dependency_groups": [str(x) for x in list(runtime_meta.get("optional_dependency_groups") or []) if str(x)],
        "build_system_requires": [str(x) for x in list(runtime_meta.get("build_system_requires") or []) if str(x)],
        "metadata_source": str(runtime_meta.get("source") or "pyproject.toml"),
        "bundle_kind": str(bundle_story.get("bundle_kind") or "project"),
        "bundle_profile_id": str(bundle_story.get("bundle_profile_id") or "").strip() or None,
        "bundle_name": str(bundle_story.get("bundle_name_hint") or distribution_story.get("bundle_name") or "project.zip"),
        "app_id": str(distribution_story.get("app_id") or "io.visualhotkey.project"),
        "command_name": str(distribution_story.get("command_name") or "vhk-project"),
        "constraints": _runtime_constraints(plan, runtime_meta),
        "wheelhouse_commands": {
            "build": 'python -m pip wheel --wheel-dir ./wheelhouse .',
            "offline_install": f'python -m pip install --no-index --find-links ./wheelhouse {package_name}',
            "smoke_bundle": f'./.smoke-venv/bin/{package_name if package_name != "vhk" else "vhk"} inspect-bundle ../../dist/{bundle_story.get("bundle_name_hint") or "project.zip"}',
        },
        "flatpak_bridge": {
            "requirements_file": paths["runtime_requirements"],
            "generator_command": f'python3 flatpak-pip-generator --requirements-file={Path(paths["runtime_requirements"]).name}',
        },
    }
    plan["runtime_paths"] = paths
    plan["runtime_story"] = runtime_story
    plan["runtime_commands"] = [
        "vhk gen-publish-pack . --force",
        "vhk gen-distribution-pack . --force",
        "vhk gen-runtime-pack . --force",
        str(bundle_story.get("bundle_command") or ""),
        f"sh {paths['runtime_build_wheelhouse_script']}",
    ]
    plan["runtime_commands"] = [cmd for cmd in list(plan.get("runtime_commands") or []) if str(cmd).strip()]
    plan["runtime_summary"] = {
        "package_name": package_name,
        "package_version": package_version,
        "dependency_count": len(dependencies),
        "bundle_kind": str(bundle_story.get("bundle_kind") or "project"),
        "requires_python": str(runtime_meta.get("requires_python") or ">=3.10"),
    }
    plan["source_contract"] = "runtime_pack"
    return plan


def _render_requirements_file(runtime_story: dict[str, Any]) -> str:
    lines = [str(item) for item in list(runtime_story.get("dependencies") or []) if str(item).strip()]
    return "\n".join(lines) + ("\n" if lines else "")


def _render_build_requirements(runtime_story: dict[str, Any]) -> str:
    lines = [str(item) for item in list(runtime_story.get("build_system_requires") or []) if str(item).strip()]
    return "\n".join(lines) + ("\n" if lines else "")


def render_runtime_handoff_readme(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    story = dict(plan.get("runtime_story") or {})
    paths = dict(plan.get("runtime_paths") or {})
    lines = [
        f"# VHK runtime handoff for {project.get('name') or 'project'}",
        "",
        "Generated by `vhk gen-runtime-pack`. This tree keeps the Python runtime story reviewable: dependency specs, wheelhouse scripts, offline smoke tests, and Flatpak bridge helpers.",
        "",
        f"- Runtime package: `{story.get('package_name') or 'vhk'}` `{story.get('package_version') or ''}`".rstrip(),
        f"- Requires Python: `{story.get('requires_python') or '>=3.10'}`",
        f"- Bundle kind: `{story.get('bundle_kind') or 'project'}`",
        f"- Bundle name: `{story.get('bundle_name') or 'project.zip'}`",
    ]
    if story.get("bundle_profile_id"):
        lines.append(f"- Target profile: `{story.get('bundle_profile_id')}`")
    lines.extend([
        "",
        "## Generated runtime artifacts",
        "",
        f"- Requirements: `{paths.get('runtime_requirements')}`",
        f"- Wheelhouse root: `{paths.get('runtime_wheelhouse_root')}`",
        f"- Wheelhouse script: `{paths.get('runtime_build_wheelhouse_script')}`",
        f"- Offline smoke test: `{paths.get('runtime_smoke_install_script')}`",
        f"- Flatpak bridge helper: `{paths.get('runtime_flatpak_generator_script')}`",
        "",
        "## Practical flow",
        "",
        "1. Refresh publish/distribution/runtime inputs so the runtime handoff stays tied to the reviewed bundle story.",
        "2. Build the wheelhouse on a builder that matches the target ABI/architecture.",
        "3. Run the offline smoke test before claiming the runtime lane is reproducible.",
        "4. Feed the same requirements file into native/package builders rather than retyping dependency lore by hand.",
        "",
    ])
    return "\n".join(lines)


def render_runtime_doc(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    story = dict(plan.get("runtime_story") or {})
    paths = dict(plan.get("runtime_paths") or {})
    lines = [
        f"# VHK runtime pack for {project.get('name') or 'project'}",
        "",
        "Generated by `vhk gen-runtime-pack`. Use it to turn VHK's Python runtime into a reviewable handoff instead of a hidden assumption behind bundle/package scripts.",
        "",
        "## Runtime posture",
        "",
        f"- Package: `{story.get('package_name') or 'vhk'}` `{story.get('package_version') or ''}`".rstrip(),
        f"- Requires Python: `{story.get('requires_python') or '>=3.10'}`",
        f"- Dependency count: `{story.get('dependency_count') or 0}`",
        f"- Bundle kind: `{story.get('bundle_kind') or 'project'}`",
        f"- Bundle name: `{story.get('bundle_name') or 'project.zip'}`",
        f"- App id: `{story.get('app_id') or 'io.visualhotkey.project'}`",
        "",
        "## Runtime dependencies",
        "",
    ]
    for dep in [str(item) for item in list(story.get("dependencies") or []) if str(item).strip()]:
        lines.append(f"- `{dep}`")
    lines.extend([
        "",
        "## Runtime constraints",
        "",
    ])
    for item in [str(x) for x in list(story.get("constraints") or []) if str(x)]:
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## Generated paths",
        "",
        f"- Runtime root: `{paths.get('runtime_root')}`",
        f"- Requirements file: `{paths.get('runtime_requirements')}`",
        f"- Wheelhouse root: `{paths.get('runtime_wheelhouse_root')}`",
        f"- Flatpak bridge helper: `{paths.get('runtime_flatpak_generator_script')}`",
        "",
        "## Review commands",
        "",
    ])
    for cmd in [str(x) for x in list(plan.get("runtime_commands") or []) if str(x)]:
        lines.append(f"- `{cmd}`")
    lines.append("")
    return "\n".join(lines)


def render_runtime_refresh_script(plan: dict[str, Any]) -> str:
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
        'printf "%s\\n" "Refreshing VHK runtime pack inputs..."',
    ]
    pub = 'vhk gen-publish-pack . --force --quiet'
    dist = 'vhk gen-distribution-pack . --force --quiet'
    runtime = 'vhk gen-runtime-pack . --force --quiet'
    if profile:
        pub += f' --bundle-target-profile {profile}'
        dist += f' --bundle-target-profile {profile}'
        runtime += f' --bundle-target-profile {profile}'
    for cmd in [pub, dist, runtime]:
        lines.append(f'printf "+ %s\\n" {cmd!r}')
        lines.append(f'sh -lc {cmd!r} || true')
    lines.extend([
        'printf "%s\\n" "Runtime pack refresh complete."',
        "",
    ])
    return "\n".join(lines)


def _render_wheelhouse_readme(plan: dict[str, Any]) -> str:
    story = dict(plan.get("runtime_story") or {})
    return "\n".join(
        [
            "# Wheelhouse notes",
            "",
            "Populate this directory with `build_wheelhouse.sh`.",
            "It is intentionally empty by default so generated review trees stay deterministic until a maintainer chooses a build host.",
            "",
            f"Target runtime package: `{story.get('package_name') or 'vhk'}` `{story.get('package_version') or ''}`".rstrip(),
            f"Target bundle: `{story.get('bundle_name') or 'project.zip'}`",
            "",
        ]
    )


def _render_build_wheelhouse_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("runtime_story") or {})
    package_name = str(story.get("package_name") or "vhk")
    lines = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        'SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"',
        'PROJECT_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/../../../.." && pwd)"',
        'WHEELHOUSE_DIR="$SCRIPT_DIR/wheelhouse"',
        'REQ_FILE="$SCRIPT_DIR/requirements.runtime.txt"',
        'BUILD_REQ_FILE="$SCRIPT_DIR/build-requirements.txt"',
        'cd "$PROJECT_DIR"',
        'mkdir -p "$WHEELHOUSE_DIR"',
        'printf "%s\\n" "Building VHK runtime wheelhouse..."',
        'python -m pip install --upgrade pip wheel setuptools',
        'if [ -s "$BUILD_REQ_FILE" ]; then',
        '  python -m pip install -r "$BUILD_REQ_FILE"',
        'fi',
        'if [ -s "$REQ_FILE" ]; then',
        '  python -m pip wheel --wheel-dir "$WHEELHOUSE_DIR" -r "$REQ_FILE"',
        'fi',
        'python -m pip wheel --wheel-dir "$WHEELHOUSE_DIR" .',
        f'printf "%s\\n" "Wheelhouse ready for {package_name}."',
        "",
    ]
    return "\n".join(lines)


def _render_smoke_install_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("runtime_story") or {})
    package_name = str(story.get("package_name") or "vhk")
    bundle_name = str(story.get("bundle_name") or "project.zip")
    lines = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        'SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"',
        'PROJECT_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/../../../.." && pwd)"',
        'WHEELHOUSE_DIR="$SCRIPT_DIR/wheelhouse"',
        'VENV_DIR="$SCRIPT_DIR/.smoke-venv"',
        'DIST_DIR="$SCRIPT_DIR/../../dist"',
        'cd "$PROJECT_DIR"',
        'if [ ! -d "$WHEELHOUSE_DIR" ] || [ -z "$(ls -A "$WHEELHOUSE_DIR" 2>/dev/null || true)" ]; then',
        '  printf "%s\\n" "Wheelhouse is empty; run build_wheelhouse.sh first." >&2',
        '  exit 1',
        'fi',
        'python -m venv "$VENV_DIR"',
        '"$VENV_DIR/bin/python" -m pip install --upgrade pip',
        f'"$VENV_DIR/bin/python" -m pip install --no-index --find-links "$WHEELHOUSE_DIR" {package_name}',
        'if [ -f "$DIST_DIR/' + bundle_name + '" ]; then',
        f'  "$VENV_DIR/bin/{package_name if package_name != "vhk" else "vhk"}" inspect-bundle "$DIST_DIR/{bundle_name}" || true',
        'else',
        '  printf "%s\\n" "No bundle artifact yet; smoke test covered offline install only."',
        'fi',
        'printf "%s\\n" "Offline runtime smoke test complete."',
        "",
    ]
    return "\n".join(lines)


def _render_run_bundle_script(plan: dict[str, Any]) -> str:
    story = dict(plan.get("runtime_story") or {})
    package_name = str(story.get("package_name") or "vhk")
    bundle_name = str(story.get("bundle_name") or "project.zip")
    exe = package_name if package_name != "vhk" else "vhk"
    return "\n".join(
        [
            "#!/usr/bin/env sh",
            "set -eu",
            "",
            'SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"',
            'VENV_DIR="$SCRIPT_DIR/.smoke-venv"',
            'BUNDLE_PATH="${1:-$SCRIPT_DIR/../../dist/' + bundle_name + '}"',
            'if [ ! -x "$VENV_DIR/bin/' + exe + '" ]; then',
            '  printf "%s\\n" "Run smoke_test_offline_install.sh first so the local runtime exists." >&2',
            '  exit 1',
            'fi',
            'exec "$VENV_DIR/bin/' + exe + '" inspect-bundle "$BUNDLE_PATH"',
            "",
        ]
    )


def _render_flatpak_generator_script(plan: dict[str, Any]) -> str:
    return "\n".join(
        [
            "#!/usr/bin/env sh",
            "set -eu",
            "",
            'SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"',
            'REQ_FILE="$SCRIPT_DIR/requirements.runtime.txt"',
            'OUT_FILE="$SCRIPT_DIR/python3-vhk-runtime.json"',
            'cd "$SCRIPT_DIR"',
            'if command -v flatpak-pip-generator >/dev/null 2>&1; then',
            '  flatpak-pip-generator --requirements-file="$REQ_FILE"',
            '  GENERATED="$(find . -maxdepth 1 -name "python3-*.json" | head -n 1 || true)"',
            '  if [ -n "$GENERATED" ] && [ "$GENERATED" != "./python3-vhk-runtime.json" ]; then',
            '    mv "$GENERATED" "$OUT_FILE"',
            '  fi',
            '  printf "%s\\n" "Wrote $OUT_FILE"',
            'else',
            '  printf "%s\\n" "Install flatpak-pip-generator to emit Flatpak Python modules from requirements.runtime.txt." >&2',
            '  exit 1',
            'fi',
            "",
        ]
    )


def _materialize_runtime_handoff(project_dir: Path, plan: dict[str, Any], *, build_dir: Path, force: bool) -> dict[str, Path]:
    root = build_dir / "runtime"
    root.mkdir(parents=True, exist_ok=True)
    wheelhouse = root / "wheelhouse"
    wheelhouse.mkdir(parents=True, exist_ok=True)
    story = dict(plan.get("runtime_story") or {})
    paths = dict(plan.get("runtime_paths") or {})

    _write_if_allowed(root / "README.md", render_runtime_handoff_readme(plan), force=force)
    manifest_payload = {
        "project_root": str(project_dir),
        **paths,
        **story,
    }
    _write_if_allowed(root / "vhk_runtime_handoff.json", json.dumps(manifest_payload, indent=2, sort_keys=True) + "\n", force=force)

    refresh_script = root / "refresh_runtime_inputs.sh"
    wheelhouse_readme = wheelhouse / "README.md"
    wheelhouse_script = root / "build_wheelhouse.sh"
    smoke_script = root / "smoke_test_offline_install.sh"
    run_bundle_script = root / "run_bundle_with_runtime.sh"
    flatpak_generator = root / "emit_flatpak_python_modules.sh"
    req_file = root / "requirements.runtime.txt"
    build_req_file = root / "build-requirements.txt"

    _write_if_allowed(refresh_script, render_runtime_refresh_script(plan), force=force)
    _write_if_allowed(wheelhouse_readme, _render_wheelhouse_readme(plan), force=force)
    _write_if_allowed(wheelhouse_script, _render_build_wheelhouse_script(plan), force=force)
    _write_if_allowed(smoke_script, _render_smoke_install_script(plan), force=force)
    _write_if_allowed(run_bundle_script, _render_run_bundle_script(plan), force=force)
    _write_if_allowed(flatpak_generator, _render_flatpak_generator_script(plan), force=force)
    _write_if_allowed(req_file, _render_requirements_file(story), force=force)
    _write_if_allowed(build_req_file, _render_build_requirements(story), force=force)

    for path in [refresh_script, wheelhouse_script, smoke_script, run_bundle_script, flatpak_generator]:
        path.chmod(0o755)

    copied_docs: list[str] = []
    payload_docs_root = root / "payload/docs"
    for rel in [
        "docs/VHK_PUBLIC_SUPPORT.md",
        "docs/VHK_INSTALL_QUICKSTART.md",
        "docs/VHK_DISTRIBUTION.md",
        "docs/VHK_DISTRIBUTION_PLAN.json",
        "docs/VHK_RUNTIME.md",
        "docs/VHK_RUNTIME_PLAN.json",
    ]:
        if _copy_if_present(project_dir / rel, payload_docs_root / Path(rel).name):
            copied_docs.append(rel)

    return {
        "runtime_root": root,
        "runtime_manifest": root / "vhk_runtime_handoff.json",
        "runtime_readme": root / "README.md",
        "runtime_refresh_script": refresh_script,
        "runtime_requirements": req_file,
        "runtime_wheelhouse_root": wheelhouse,
        "runtime_build_wheelhouse_script": wheelhouse_script,
        "runtime_smoke_install_script": smoke_script,
        "runtime_run_bundle_script": run_bundle_script,
        "runtime_flatpak_generator_script": flatpak_generator,
    }


def write_runtime_pack(
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
    runtime_doc: bool = True,
    plan_json: bool = True,
    script: bool = True,
) -> dict[str, Path]:
    project_dir = project_dir.expanduser().resolve()
    out_dir = (out_dir or (project_dir / "docs")).expanduser().resolve()
    script_dir = (script_dir or (project_dir / "scripts")).expanduser().resolve()

    write_distribution_pack(
        project_dir,
        bundle_target_profile=bundle_target_profile,
        app_id=app_id,
        runtime=runtime,
        runtime_version=runtime_version,
        sdk=sdk,
        force=force,
        distribution_doc=True,
        plan_json=True,
        script=True,
    )
    plan = build_runtime_plan(
        project_dir,
        bundle_target_profile=bundle_target_profile,
        app_id=app_id,
        runtime=runtime,
        runtime_version=runtime_version,
        sdk=sdk,
    )
    written: dict[str, Path] = {}
    if runtime_doc:
        path = out_dir / "VHK_RUNTIME.md"
        _write_if_allowed(path, render_runtime_doc(plan), force=force)
        written["runtime_doc"] = path
    if plan_json:
        path = out_dir / "VHK_RUNTIME_PLAN.json"
        _write_if_allowed(path, json.dumps(plan, indent=2, sort_keys=True) + "\n", force=force)
        written["plan_json"] = path
    if script:
        path = script_dir / "vhk_refresh_runtime_pack.sh"
        _write_if_allowed(path, render_runtime_refresh_script(plan), force=force)
        path.chmod(0o755)
        written["script"] = path

    publish_root = project_dir / str((plan.get("publish_handoff") or {}).get("root") or "build/publish/project")
    written.update(_materialize_runtime_handoff(project_dir, plan, build_dir=publish_root, force=force))
    return written
