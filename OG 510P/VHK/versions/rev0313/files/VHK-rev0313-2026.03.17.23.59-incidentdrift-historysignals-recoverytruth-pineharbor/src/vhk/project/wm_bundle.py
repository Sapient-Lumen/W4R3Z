from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from vhk.core.models import Project
from vhk.project.launcher_script import (
    default_launcher_install_path,
    default_launcher_script_name,
    render_launcher_script,
)
from vhk.project.publish_pack import render_install_quickstart, render_public_support_doc
from vhk.project.rofi_mode import build_rofi_mode_manifest
from vhk.project.support_posture import load_or_build_publish_plan, summarize_support_posture
from vhk.project.wm_includes import (
    build_wm_include_manifest,
    default_wm_include_file_name,
)

_VALID_WMS = {"i3", "sway", "hyprland"}
_VALID_KINDS = {"binding", "launcher-mode"}
_VALID_LAUNCHERS = {"rofi-mode", "launcher-script", "palette-command"}
_WM_CONFIG_DIR = {
    "i3": "i3",
    "sway": "sway",
    "hyprland": "hypr",
}
_RELOAD_COMMANDS = {
    "i3": "i3-msg reload",
    "sway": "swaymsg reload",
    "hyprland": "hyprctl reload",
}


@dataclass(frozen=True)
class WMBundleManifest:
    wm: str
    kind: str
    launcher: str
    install: bool
    root_dir: str
    helper_path: str | None
    helper_written: bool
    helper_kind: str | None
    include_path: str
    bootstrap_path: str | None
    manifest_path: str | None
    bootstrap_line: str
    parent_config_path: str
    reload_command: str
    launcher_command: str
    snippet: str
    support_headline: str | None = None
    support_summary_path: str | None = None
    support_quickstart_path: str | None = None
    support_json_path: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "wm": self.wm,
            "kind": self.kind,
            "launcher": self.launcher,
            "install": self.install,
            "root_dir": self.root_dir,
            "helper_path": self.helper_path,
            "helper_written": self.helper_written,
            "helper_kind": self.helper_kind,
            "include_path": self.include_path,
            "bootstrap_path": self.bootstrap_path,
            "manifest_path": self.manifest_path,
            "bootstrap_line": self.bootstrap_line,
            "parent_config_path": self.parent_config_path,
            "reload_command": self.reload_command,
            "launcher_command": self.launcher_command,
            "snippet": self.snippet,
            "support_headline": self.support_headline,
            "support_summary_path": self.support_summary_path,
            "support_quickstart_path": self.support_quickstart_path,
            "support_json_path": self.support_json_path,
        }


def _bundle_root(project: Project, *, env: dict[str, str] | None = None) -> Path:
    env_map = dict(os.environ if env is None else env)
    xdg_state_home = env_map.get("XDG_STATE_HOME")
    if xdg_state_home:
        base = Path(xdg_state_home)
    else:
        base = Path.home() / ".local" / "state"
    return base / "vhk" / "bundles" / project.name


def default_wm_bundle_dir(
    project: Project,
    *,
    wm: str,
    kind: str = "binding",
    launcher: str = "rofi-mode",
    env: dict[str, str] | None = None,
) -> Path:
    normalized_wm = str(wm).strip().lower()
    normalized_kind = str(kind).strip().lower()
    normalized_launcher = str(launcher).strip().lower()
    if normalized_wm not in _VALID_WMS:
        raise ValueError(f"Unsupported window manager: {wm}")
    if normalized_kind not in _VALID_KINDS:
        raise ValueError(f"Unsupported WM bundle kind: {kind}")
    if normalized_launcher not in _VALID_LAUNCHERS:
        raise ValueError(f"Unsupported launcher type: {launcher}")
    return _bundle_root(project, env=env) / normalized_wm / normalized_kind / normalized_launcher


def default_wm_bundle_helper_path(
    project: Project,
    *,
    bundle_dir: str | Path,
    launcher: str,
    launcher_id: str | None = None,
) -> Path | None:
    normalized_launcher = str(launcher).strip().lower()
    if normalized_launcher not in {"rofi-mode", "launcher-script"}:
        return None
    return Path(bundle_dir) / "bin" / default_launcher_script_name(project, launcher_id=launcher_id)


def default_wm_bundle_include_path(
    project: Project,
    *,
    bundle_dir: str | Path,
    wm: str,
    kind: str,
) -> Path:
    normalized_wm = str(wm).strip().lower()
    if normalized_wm not in _WM_CONFIG_DIR:
        raise ValueError(f"Unsupported window manager: {wm}")
    return Path(bundle_dir) / "config" / _WM_CONFIG_DIR[normalized_wm] / "vhk" / default_wm_include_file_name(project, kind=kind)


def _bundle_support_artifacts(project: Project, *, bundle_dir: Path, install_mode: bool) -> tuple[dict[str, Any] | None, dict[str, str]]:
    if install_mode:
        return None, {}
    plan = load_or_build_publish_plan(project.root_dir)
    support = summarize_support_posture(project.root_dir)
    docs_dir = bundle_dir / "docs"
    return support, {
        "support_summary_path": str(docs_dir / "VHK_PUBLIC_SUPPORT.md"),
        "support_quickstart_path": str(docs_dir / "VHK_INSTALL_QUICKSTART.md"),
        "support_json_path": str(docs_dir / "VHK_BUNDLE_SUPPORT.json"),
        "support_summary_text": render_public_support_doc(plan),
        "support_quickstart_text": render_install_quickstart(plan),
        "support_json_text": json.dumps(support, ensure_ascii=False, indent=2) + "\n",
    }


def _resolve_helper_text(
    project: Project,
    *,
    launcher: str,
    helper_path: Path | None,
    command: str,
    title: str | None,
    launcher_backend: str,
    include_hidden: bool,
    include_presets: bool,
    include_profile_actions: bool,
    include_profile_management_actions: bool,
    alpha: bool,
    history_limit: int,
) -> tuple[str | None, str | None]:
    normalized_launcher = str(launcher).strip().lower()
    if normalized_launcher == "rofi-mode":
        return (
            render_launcher_script(
                project,
                command=command,
                title=title,
                launcher_backend="rofi",
                include_hidden=include_hidden,
                include_presets=include_presets,
                include_profile_actions=include_profile_actions,
                include_profile_management_actions=include_profile_management_actions,
                alpha=alpha,
                history_limit=history_limit,
            ),
            "rofi-script",
        )
    if normalized_launcher == "launcher-script":
        return (
            render_launcher_script(
                project,
                command=command,
                title=title,
                launcher_backend=launcher_backend,
                include_hidden=include_hidden,
                include_presets=include_presets,
                include_profile_actions=include_profile_actions,
                include_profile_management_actions=include_profile_management_actions,
                alpha=alpha,
                history_limit=history_limit,
            ),
            "launcher-script",
        )
    return None, None


def build_wm_bundle_manifest(
    project: Project,
    *,
    wm: str,
    kind: str = "binding",
    launcher: str = "rofi-mode",
    output_dir: str | Path | None = None,
    install: bool = False,
    env: dict[str, str] | None = None,
    launcher_path: str | Path | None = None,
    launcher_id: str | None = None,
    title: str | None = None,
    command: str = "vhk",
    launcher_backend: str = "auto",
    include_hidden: bool = False,
    include_presets: bool = True,
    include_profile_actions: bool = True,
    include_profile_management_actions: bool = False,
    alpha: bool = False,
    history_limit: int = 50,
    **kwargs: Any,
) -> WMBundleManifest:
    normalized_wm = str(wm).strip().lower()
    normalized_kind = str(kind).strip().lower()
    normalized_launcher = str(launcher).strip().lower()
    if normalized_wm not in _VALID_WMS:
        raise ValueError(f"Unsupported window manager: {wm}")
    if normalized_kind not in _VALID_KINDS:
        raise ValueError(f"Unsupported WM bundle kind: {kind}")
    if normalized_launcher not in _VALID_LAUNCHERS:
        raise ValueError(f"Unsupported launcher type: {launcher}")

    bundle_dir = Path(output_dir) if output_dir is not None else default_wm_bundle_dir(
        project,
        wm=normalized_wm,
        kind=normalized_kind,
        launcher=normalized_launcher,
        env=env,
    )
    install_mode = bool(install)

    if normalized_launcher in {"rofi-mode", "launcher-script"}:
        helper_target = Path(launcher_path) if launcher_path is not None else (
            default_launcher_install_path(project, env=env, launcher_id=launcher_id)
            if install_mode
            else default_wm_bundle_helper_path(project, bundle_dir=bundle_dir, launcher=normalized_launcher, launcher_id=launcher_id)
        )
    else:
        helper_target = None

    helper_text, helper_kind = _resolve_helper_text(
        project,
        launcher=normalized_launcher,
        helper_path=helper_target,
        command=command,
        title=title,
        launcher_backend=launcher_backend,
        include_hidden=include_hidden,
        include_presets=include_presets,
        include_profile_actions=include_profile_actions,
        include_profile_management_actions=include_profile_management_actions,
        alpha=alpha,
        history_limit=history_limit,
    )

    include_target_arg = kwargs.pop("install_path", None)
    if include_target_arg is not None:
        include_target = Path(include_target_arg)
    elif install_mode:
        from vhk.project.wm_includes import default_wm_include_install_path
        include_target = default_wm_include_install_path(project, wm=normalized_wm, kind=normalized_kind, env=env)
    else:
        include_target = default_wm_bundle_include_path(project, bundle_dir=bundle_dir, wm=normalized_wm, kind=normalized_kind)

    include_manifest = build_wm_include_manifest(
        project,
        wm=normalized_wm,
        kind=normalized_kind,
        install_path=include_target,
        launcher=normalized_launcher,
        launcher_path=helper_target,
        launcher_id=launcher_id,
        command=command,
        **kwargs,
    )

    # Keep human-facing launcher command explicit for rofi-mode.
    launcher_command = include_manifest.snippet
    if normalized_launcher == "rofi-mode" and helper_target is not None:
        rofi_manifest = build_rofi_mode_manifest(
            project,
            script_path=helper_target,
            mode_name=kwargs.get("mode_name") if normalized_kind == "binding" else kwargs.get("rofi_mode_name"),
            show_icons=bool(kwargs.get("show_icons", True)),
            extra_modes=kwargs.get("extra_modes") or (),
        )
        launcher_command = rofi_manifest.command
    elif normalized_launcher == "launcher-script" and helper_target is not None:
        launcher_command = str(helper_target)
    elif normalized_launcher == "palette-command":
        from vhk.project.wm_bindings import resolve_launcher_command
        launcher_command = resolve_launcher_command(project, launcher=normalized_launcher, command=command).command

    bootstrap_path = None if install_mode else str(bundle_dir / "BOOTSTRAP.txt")
    manifest_path = None if install_mode else str(bundle_dir / "vhk-wm-bundle.json")
    support_posture, support_artifacts = _bundle_support_artifacts(project, bundle_dir=bundle_dir, install_mode=install_mode)
    return WMBundleManifest(
        wm=normalized_wm,
        kind=normalized_kind,
        launcher=normalized_launcher,
        install=install_mode,
        root_dir=str(bundle_dir if not install_mode else Path(include_manifest.include_dir).parent),
        helper_path=str(helper_target) if helper_target is not None else None,
        helper_written=helper_target is not None and helper_text is not None,
        helper_kind=helper_kind,
        include_path=include_manifest.install_path,
        bootstrap_path=bootstrap_path,
        manifest_path=manifest_path,
        bootstrap_line=include_manifest.bootstrap_line,
        parent_config_path=include_manifest.parent_config_path,
        reload_command=_RELOAD_COMMANDS[normalized_wm],
        launcher_command=launcher_command,
        snippet=include_manifest.snippet,
        support_headline=None if support_posture is None else str(support_posture.get("headline") or ""),
        support_summary_path=support_artifacts.get("support_summary_path"),
        support_quickstart_path=support_artifacts.get("support_quickstart_path"),
        support_json_path=support_artifacts.get("support_json_path"),
    )


def write_wm_bundle(
    project: Project,
    *,
    wm: str,
    kind: str = "binding",
    launcher: str = "rofi-mode",
    output_dir: str | Path | None = None,
    install: bool = False,
    env: dict[str, str] | None = None,
    force: bool = False,
    launcher_path: str | Path | None = None,
    launcher_id: str | None = None,
    title: str | None = None,
    command: str = "vhk",
    launcher_backend: str = "auto",
    include_hidden: bool = False,
    include_presets: bool = True,
    include_profile_actions: bool = True,
    include_profile_management_actions: bool = False,
    alpha: bool = False,
    history_limit: int = 50,
    **kwargs: Any,
) -> WMBundleManifest:
    manifest = build_wm_bundle_manifest(
        project,
        wm=wm,
        kind=kind,
        launcher=launcher,
        output_dir=output_dir,
        install=install,
        env=env,
        launcher_path=launcher_path,
        launcher_id=launcher_id,
        title=title,
        command=command,
        launcher_backend=launcher_backend,
        include_hidden=include_hidden,
        include_presets=include_presets,
        include_profile_actions=include_profile_actions,
        include_profile_management_actions=include_profile_management_actions,
        alpha=alpha,
        history_limit=history_limit,
        **kwargs,
    )

    helper_text, _ = _resolve_helper_text(
        project,
        launcher=manifest.launcher,
        helper_path=Path(manifest.helper_path) if manifest.helper_path else None,
        command=command,
        title=title,
        launcher_backend=launcher_backend,
        include_hidden=include_hidden,
        include_presets=include_presets,
        include_profile_actions=include_profile_actions,
        include_profile_management_actions=include_profile_management_actions,
        alpha=alpha,
        history_limit=history_limit,
    )

    targets: list[Path] = [Path(manifest.include_path)]
    if manifest.helper_path:
        targets.append(Path(manifest.helper_path))
    if not manifest.install:
        if manifest.bootstrap_path:
            targets.append(Path(manifest.bootstrap_path))
        if manifest.manifest_path:
            targets.append(Path(manifest.manifest_path))
        if manifest.support_summary_path:
            targets.append(Path(manifest.support_summary_path))
        if manifest.support_quickstart_path:
            targets.append(Path(manifest.support_quickstart_path))
        if manifest.support_json_path:
            targets.append(Path(manifest.support_json_path))
    for target in targets:
        if target.exists() and not force:
            raise FileExistsError(str(target))

    Path(manifest.include_path).parent.mkdir(parents=True, exist_ok=True)
    Path(manifest.include_path).write_text(manifest.snippet, encoding="utf-8")

    if manifest.helper_path and helper_text is not None:
        helper_out = Path(manifest.helper_path)
        helper_out.parent.mkdir(parents=True, exist_ok=True)
        helper_out.write_text(helper_text, encoding="utf-8")
        helper_out.chmod(helper_out.stat().st_mode | 0o111)

    if manifest.bootstrap_path:
        Path(manifest.bootstrap_path).parent.mkdir(parents=True, exist_ok=True)
        Path(manifest.bootstrap_path).write_text(
            "# Add this once to {parent}\n{line}\n# Reload after changes:\n{reload}\n".format(
                parent=manifest.parent_config_path,
                line=manifest.bootstrap_line,
                reload=manifest.reload_command,
            ),
            encoding="utf-8",
        )
    if manifest.support_summary_path or manifest.support_quickstart_path or manifest.support_json_path:
        support_posture, support_artifacts = _bundle_support_artifacts(
            project,
            bundle_dir=Path(manifest.root_dir),
            install_mode=manifest.install,
        )
        _ = support_posture
        for key, path_attr in [
            ("support_summary_text", manifest.support_summary_path),
            ("support_quickstart_text", manifest.support_quickstart_path),
            ("support_json_text", manifest.support_json_path),
        ]:
            if path_attr:
                path = Path(path_attr)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(str(support_artifacts.get(key) or ""), encoding="utf-8")
    if manifest.manifest_path:
        Path(manifest.manifest_path).write_text(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest
