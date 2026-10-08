from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from vhk.core.models import Project
from vhk.project.wm_bindings import build_wm_binding_manifest
from vhk.project.wm_launcher_modes import build_wm_launcher_mode_manifest

_VALID_WMS = {"i3", "sway", "hyprland"}
_VALID_KINDS = {"binding", "launcher-mode"}
_PARENT_CONFIG_REL = {
    "i3": Path("i3/config"),
    "sway": Path("sway/config"),
    "hyprland": Path("hypr/hyprland.conf"),
}


def _slugify(text: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", str(text).strip()).strip("-").lower()
    return slug or "project"


@dataclass(frozen=True)
class WMIncludeManifest:
    wm: str
    kind: str
    install_path: str
    include_dir: str
    include_glob: str
    bootstrap_line: str
    parent_config_path: str
    snippet: str

    def to_dict(self) -> dict[str, object]:
        return {
            "wm": self.wm,
            "kind": self.kind,
            "install_path": self.install_path,
            "include_dir": self.include_dir,
            "include_glob": self.include_glob,
            "bootstrap_line": self.bootstrap_line,
            "parent_config_path": self.parent_config_path,
            "snippet": self.snippet,
        }



def default_wm_include_dir(
    wm: str,
    *,
    env: dict[str, str] | None = None,
) -> Path:
    normalized_wm = str(wm).strip().lower()
    if normalized_wm not in _VALID_WMS:
        raise ValueError(f"Unsupported window manager: {wm}")
    env_map = dict(os.environ if env is None else env)
    xdg_config_home = env_map.get("XDG_CONFIG_HOME")
    if xdg_config_home:
        base = Path(xdg_config_home)
    else:
        base = Path.home() / ".config"
    if normalized_wm == "hyprland":
        return base / "hypr" / "vhk"
    return base / normalized_wm / "vhk"



def default_wm_include_file_name(project: Project, *, kind: str = "binding") -> str:
    normalized_kind = str(kind).strip().lower()
    if normalized_kind not in _VALID_KINDS:
        raise ValueError(f"Unsupported WM include kind: {kind}")
    suffix = "launcher-mode" if normalized_kind == "launcher-mode" else "binding"
    return f"vhk-{_slugify(project.name)}-{suffix}.conf"



def default_wm_include_install_path(
    project: Project,
    *,
    wm: str,
    kind: str = "binding",
    env: dict[str, str] | None = None,
) -> Path:
    return default_wm_include_dir(wm, env=env) / default_wm_include_file_name(project, kind=kind)



def default_wm_bootstrap_glob(
    wm: str,
    *,
    env: dict[str, str] | None = None,
) -> Path:
    return default_wm_include_dir(wm, env=env) / "*.conf"



def wm_bootstrap_line(
    wm: str,
    *,
    env: dict[str, str] | None = None,
) -> str:
    normalized_wm = str(wm).strip().lower()
    if normalized_wm not in _VALID_WMS:
        raise ValueError(f"Unsupported window manager: {wm}")
    glob = default_wm_bootstrap_glob(normalized_wm, env=env)
    if normalized_wm == "hyprland":
        return f"source = {glob}"
    return f"include {glob}"



def default_wm_parent_config_path(
    wm: str,
    *,
    env: dict[str, str] | None = None,
) -> Path:
    normalized_wm = str(wm).strip().lower()
    if normalized_wm not in _PARENT_CONFIG_REL:
        raise ValueError(f"Unsupported window manager: {wm}")
    env_map = dict(os.environ if env is None else env)
    xdg_config_home = env_map.get("XDG_CONFIG_HOME")
    if xdg_config_home:
        base = Path(xdg_config_home)
    else:
        base = Path.home() / ".config"
    return base / _PARENT_CONFIG_REL[normalized_wm]



def build_wm_include_manifest(
    project: Project,
    *,
    wm: str,
    kind: str = "binding",
    install_path: str | Path | None = None,
    env: dict[str, str] | None = None,
    **kwargs: Any,
) -> WMIncludeManifest:
    normalized_wm = str(wm).strip().lower()
    if normalized_wm not in _VALID_WMS:
        raise ValueError(f"Unsupported window manager: {wm}")
    normalized_kind = str(kind).strip().lower()
    if normalized_kind not in _VALID_KINDS:
        raise ValueError(f"Unsupported WM include kind: {kind}")

    if normalized_kind == "binding":
        snippet = build_wm_binding_manifest(project, wm=normalized_wm, **kwargs).snippet
    else:
        snippet = build_wm_launcher_mode_manifest(project, wm=normalized_wm, **kwargs).snippet

    target = Path(install_path) if install_path is not None else default_wm_include_install_path(
        project,
        wm=normalized_wm,
        kind=normalized_kind,
        env=env,
    )
    include_dir = target.parent
    include_glob = include_dir / "*.conf"
    bootstrap_line = (f"source = {include_glob}" if normalized_wm == "hyprland" else f"include {include_glob}")
    return WMIncludeManifest(
        wm=normalized_wm,
        kind=normalized_kind,
        install_path=str(target),
        include_dir=str(include_dir),
        include_glob=str(include_glob),
        bootstrap_line=bootstrap_line,
        parent_config_path=str(default_wm_parent_config_path(normalized_wm, env=env)),
        snippet=snippet,
    )



def render_wm_include_json(project: Project, **kwargs: Any) -> str:
    manifest = build_wm_include_manifest(project, **kwargs)
    return json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2)
