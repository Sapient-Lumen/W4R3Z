from __future__ import annotations

import json
import re
import shlex
from dataclasses import dataclass
from pathlib import Path

from vhk.core.models import Project
from vhk.project.launcher_script import default_launcher_install_path
from vhk.project.rofi_mode import build_rofi_mode_manifest


_VALID_WMS = {"i3", "sway", "hyprland"}
_VALID_LAUNCHERS = {"rofi-mode", "launcher-script", "palette-command"}


@dataclass(frozen=True)
class ResolvedLauncherCommand:
    launcher: str
    command: str
    helper_path: str | None = None
    mode_name: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "launcher": self.launcher,
            "command": self.command,
            "helper_path": self.helper_path,
            "mode_name": self.mode_name,
        }


@dataclass(frozen=True)
class WMBindingManifest:
    wm: str
    launcher: str
    key: str
    command: str
    helper_path: str | None = None
    mode_name: str | None = None
    snippet: str = ""
    uwsm_app: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "wm": self.wm,
            "launcher": self.launcher,
            "key": self.key,
            "command": self.command,
            "helper_path": self.helper_path,
            "mode_name": self.mode_name,
            "uwsm_app": self.uwsm_app,
            "snippet": self.snippet,
        }


def _slugify(text: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", str(text).strip()).strip("-").lower()
    return slug or "project"


def default_wm_binding_key(wm: str) -> str:
    normalized = str(wm).strip().lower()
    if normalized in {"i3", "sway"}:
        return "$mod+Shift+p"
    if normalized == "hyprland":
        return "$mainMod, P"
    raise ValueError(f"Unsupported window manager: {wm}")


def default_wm_binding_file_name(project: Project, *, wm: str) -> str:
    return f"vhk-{_slugify(project.name)}-{wm}.conf"


def _build_palette_command(project: Project, *, command: str = "vhk") -> str:
    prefix = shlex.split(str(command)) or [str(command)]
    argv = [*prefix, "palette", project.root_dir]
    return shlex.join(argv)


def _wrap_hypr_uwsm(command: str, *, uwsm_app: bool = False) -> str:
    if not uwsm_app:
        return command
    return "uwsm app -- " + command


def _quote_wm_command(command: str, *, wm: str) -> str:
    text = str(command)
    if wm not in {"i3", "sway"}:
        return text
    if "," not in text and ";" not in text:
        return text
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def format_wm_exec_command(command: str, *, wm: str, no_startup_id: bool = True) -> str:
    text = _quote_wm_command(command, wm=wm)
    if wm == "i3":
        return f"exec {'--no-startup-id ' if no_startup_id else ''}{text}"
    if wm == "sway":
        return f"exec {text}"
    if wm == "hyprland":
        return f"exec, {text}"
    raise ValueError(f"Unsupported window manager: {wm}")


def resolve_launcher_command(
    project: Project,
    *,
    launcher: str = "rofi-mode",
    launcher_path: str | Path | None = None,
    launcher_id: str | None = None,
    mode_name: str | None = None,
    show_icons: bool = True,
    extra_modes: list[str] | tuple[str, ...] | None = None,
    command: str = "vhk",
) -> ResolvedLauncherCommand:
    normalized_launcher = str(launcher).strip().lower()
    if normalized_launcher not in _VALID_LAUNCHERS:
        raise ValueError(f"Unsupported launcher type: {launcher}")

    helper_path: str | None = None
    resolved_mode_name: str | None = None
    if normalized_launcher == "rofi-mode":
        script_path = Path(launcher_path) if launcher_path is not None else default_launcher_install_path(project, launcher_id=launcher_id)
        helper_path = str(script_path)
        rofi = build_rofi_mode_manifest(
            project,
            script_path=script_path,
            mode_name=mode_name,
            show_icons=show_icons,
            extra_modes=extra_modes,
        )
        resolved_mode_name = rofi.mode_name
        resolved_command = rofi.command
    elif normalized_launcher == "launcher-script":
        script_path = Path(launcher_path) if launcher_path is not None else default_launcher_install_path(project, launcher_id=launcher_id)
        helper_path = str(script_path)
        resolved_command = shlex.join([str(script_path)])
    else:
        resolved_command = _build_palette_command(project, command=command)

    return ResolvedLauncherCommand(
        launcher=normalized_launcher,
        command=resolved_command,
        helper_path=helper_path,
        mode_name=resolved_mode_name,
    )


def build_wm_binding_manifest(
    project: Project,
    *,
    wm: str,
    launcher: str = "rofi-mode",
    key: str | None = None,
    launcher_path: str | Path | None = None,
    launcher_id: str | None = None,
    mode_name: str | None = None,
    show_icons: bool = True,
    extra_modes: list[str] | tuple[str, ...] | None = None,
    command: str = "vhk",
    uwsm_app: bool = False,
) -> WMBindingManifest:
    normalized_wm = str(wm).strip().lower()
    if normalized_wm not in _VALID_WMS:
        raise ValueError(f"Unsupported window manager: {wm}")

    resolved = resolve_launcher_command(
        project,
        launcher=launcher,
        launcher_path=launcher_path,
        launcher_id=launcher_id,
        mode_name=mode_name,
        show_icons=show_icons,
        extra_modes=extra_modes,
        command=command,
    )

    resolved_key = str(key or default_wm_binding_key(normalized_wm)).strip()
    if normalized_wm == "hyprland":
        rendered_command = _wrap_hypr_uwsm(resolved.command, uwsm_app=uwsm_app)
        snippet = "\n".join(
            [
                f"# VHK launcher for {project.name}",
                f"bind = {resolved_key}, exec, {rendered_command}",
                "",
            ]
        )
    else:
        exec_part = format_wm_exec_command(resolved.command, wm=normalized_wm, no_startup_id=(normalized_wm == "i3"))
        snippet = "\n".join(
            [
                f"# VHK launcher for {project.name}",
                f"bindsym {resolved_key} {exec_part}",
                "",
            ]
        )

    return WMBindingManifest(
        wm=normalized_wm,
        launcher=resolved.launcher,
        key=resolved_key,
        command=resolved.command if normalized_wm != "hyprland" else _wrap_hypr_uwsm(resolved.command, uwsm_app=uwsm_app),
        helper_path=resolved.helper_path,
        mode_name=resolved.mode_name,
        snippet=snippet,
        uwsm_app=bool(uwsm_app and normalized_wm == "hyprland"),
    )


def render_wm_binding_snippet(
    project: Project,
    *,
    wm: str,
    launcher: str = "rofi-mode",
    key: str | None = None,
    launcher_path: str | Path | None = None,
    launcher_id: str | None = None,
    mode_name: str | None = None,
    show_icons: bool = True,
    extra_modes: list[str] | tuple[str, ...] | None = None,
    command: str = "vhk",
    uwsm_app: bool = False,
) -> str:
    return build_wm_binding_manifest(
        project,
        wm=wm,
        launcher=launcher,
        key=key,
        launcher_path=launcher_path,
        launcher_id=launcher_id,
        mode_name=mode_name,
        show_icons=show_icons,
        extra_modes=extra_modes,
        command=command,
        uwsm_app=uwsm_app,
    ).snippet


def render_wm_binding_json(
    project: Project,
    *,
    wm: str,
    launcher: str = "rofi-mode",
    key: str | None = None,
    launcher_path: str | Path | None = None,
    launcher_id: str | None = None,
    mode_name: str | None = None,
    show_icons: bool = True,
    extra_modes: list[str] | tuple[str, ...] | None = None,
    command: str = "vhk",
    uwsm_app: bool = False,
) -> str:
    manifest = build_wm_binding_manifest(
        project,
        wm=wm,
        launcher=launcher,
        key=key,
        launcher_path=launcher_path,
        launcher_id=launcher_id,
        mode_name=mode_name,
        show_icons=show_icons,
        extra_modes=extra_modes,
        command=command,
        uwsm_app=uwsm_app,
    )
    return json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2)
