from __future__ import annotations

import json
import re
import shlex
from dataclasses import dataclass
from pathlib import Path

from vhk.core.models import Project


def _slugify(text: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", str(text).strip()).strip("-").lower()
    return slug or "project"


@dataclass(frozen=True)
class RofiModeManifest:
    mode_name: str
    script_path: str
    rofi_argv: tuple[str, ...]
    command: str

    def to_dict(self) -> dict[str, object]:
        return {
            "mode_name": self.mode_name,
            "script_path": self.script_path,
            "rofi_argv": list(self.rofi_argv),
            "command": self.command,
        }


def default_rofi_mode_name(project: Project, *, mode_name: str | None = None) -> str:
    if mode_name is not None:
        value = str(mode_name).strip()
        if value:
            return value
    return f"vhk-{_slugify(project.name)}"


def build_rofi_argv(
    project: Project,
    *,
    script_path: str | Path,
    mode_name: str | None = None,
    show_icons: bool = True,
    extra_modes: list[str] | tuple[str, ...] | None = None,
) -> list[str]:
    name = default_rofi_mode_name(project, mode_name=mode_name)
    mode_spec = f"{name}:{Path(script_path)}"
    modes: list[str] = [str(m).strip() for m in (extra_modes or []) if str(m).strip()]
    modes.append(mode_spec)
    argv = ["rofi", "-show", name, "-modes", ",".join(modes)]
    if show_icons:
        argv.append("-show-icons")
    return argv


def build_rofi_mode_manifest(
    project: Project,
    *,
    script_path: str | Path,
    mode_name: str | None = None,
    show_icons: bool = True,
    extra_modes: list[str] | tuple[str, ...] | None = None,
) -> RofiModeManifest:
    argv = tuple(build_rofi_argv(project, script_path=script_path, mode_name=mode_name, show_icons=show_icons, extra_modes=extra_modes))
    return RofiModeManifest(
        mode_name=default_rofi_mode_name(project, mode_name=mode_name),
        script_path=str(Path(script_path)),
        rofi_argv=argv,
        command=shlex.join(argv),
    )


def render_rofi_mode_json(
    project: Project,
    *,
    script_path: str | Path,
    mode_name: str | None = None,
    show_icons: bool = True,
    extra_modes: list[str] | tuple[str, ...] | None = None,
) -> str:
    manifest = build_rofi_mode_manifest(
        project,
        script_path=script_path,
        mode_name=mode_name,
        show_icons=show_icons,
        extra_modes=extra_modes,
    )
    return json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2)
