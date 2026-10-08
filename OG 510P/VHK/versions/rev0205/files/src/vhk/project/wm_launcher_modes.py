from __future__ import annotations

import json
import re
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from vhk.core.models import Project
from vhk.project.palette import build_palette_entries
from vhk.project.prompt_profiles import make_prompt_profile_store
from vhk.project.wm_bindings import format_wm_exec_command, resolve_launcher_command


_VALID_WMS = {"i3", "sway", "hyprland"}
_DEFAULT_ENTRY_KEYS = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0")


@dataclass(frozen=True)
class WMLauncherModeAction:
    key: str
    label: str
    command: str
    kind: str = "entry"
    entry_id: str | None = None
    macro: str | None = None
    preset: str | None = None
    prompt_profile: str | None = None
    action: str = "run"

    def to_dict(self) -> dict[str, object]:
        return {
            "key": self.key,
            "label": self.label,
            "command": self.command,
            "kind": self.kind,
            "entry_id": self.entry_id,
            "macro": self.macro,
            "preset": self.preset,
            "prompt_profile": self.prompt_profile,
            "action": self.action,
        }


@dataclass(frozen=True)
class WMLauncherModeManifest:
    wm: str
    mode_name: str
    mode_enter: str
    launcher: str
    one_shot: bool
    exit_keys: tuple[str, ...]
    launcher_key: str | None
    helper_path: str | None
    launcher_mode_name: str | None
    actions: tuple[WMLauncherModeAction, ...]
    snippet: str
    uwsm_app: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "wm": self.wm,
            "mode_name": self.mode_name,
            "mode_enter": self.mode_enter,
            "launcher": self.launcher,
            "one_shot": self.one_shot,
            "exit_keys": list(self.exit_keys),
            "launcher_key": self.launcher_key,
            "helper_path": self.helper_path,
            "launcher_mode_name": self.launcher_mode_name,
            "uwsm_app": self.uwsm_app,
            "actions": [row.to_dict() for row in self.actions],
            "snippet": self.snippet,
        }


def _slugify(text: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", str(text).strip()).strip("-").lower()
    return slug or "project"


def default_wm_launcher_mode_file_name(project: Project, *, wm: str) -> str:
    return f"vhk-{_slugify(project.name)}-{wm}-launcher-mode.conf"


def _wrap_hypr_uwsm(command: str, *, uwsm_app: bool = False) -> str:
    if not uwsm_app:
        return command
    return f"uwsm app -- {command}"


def _parse_i3_keys_for_hypr(keys: str) -> tuple[str, str]:
    parts = [p.strip() for p in str(keys or "").split("+") if p.strip()]
    if not parts:
        return "", ""
    key = parts[-1]
    mods_raw = parts[:-1]
    mod_map = {
        "mod4": "SUPER",
        "super": "SUPER",
        "mod1": "ALT",
        "alt": "ALT",
        "control": "CTRL",
        "ctrl": "CTRL",
        "shift": "SHIFT",
    }
    mods: list[str] = []
    for m in mods_raw:
        mm = mod_map.get(m.lower())
        mods.append(mm if mm else m)
    if len(key) == 1:
        key = key.upper()
    return " ".join(mods), key


def _normalize_keys_csv(value: str | None, *, default: tuple[str, ...]) -> tuple[str, ...]:
    if value is None:
        return tuple(default)
    out = [part.strip() for part in str(value).split(",") if part.strip()]
    if not out:
        return tuple(default)
    return tuple(out)


def _entry_command(project: Project, *, command: str, entry_id: str) -> str:
    prefix = shlex.split(str(command)) or [str(command)]
    argv = [*prefix, "palette", project.root_dir, "--entry-id", entry_id]
    return shlex.join(argv)


def build_wm_launcher_mode_manifest(
    project: Project,
    *,
    wm: str,
    mode_enter: str,
    mode_name: str = "vhk-launch",
    launcher: str = "palette-command",
    launcher_key: str | None = "p",
    launcher_label: str | None = None,
    launcher_path: str | Path | None = None,
    launcher_id: str | None = None,
    rofi_mode_name: str | None = None,
    show_icons: bool = True,
    extra_modes: list[str] | tuple[str, ...] | None = None,
    command: str = "vhk",
    include_launcher_action: bool = True,
    include_hidden: bool = False,
    include_presets: bool = True,
    include_profile_actions: bool = True,
    include_profile_management_actions: bool = False,
    alpha: bool = False,
    history_limit: int = 50,
    entry_keys: list[str] | tuple[str, ...] | None = None,
    max_entries: int | None = None,
    one_shot: bool = True,
    exit_keys: list[str] | tuple[str, ...] | None = None,
    uwsm_app: bool = False,
) -> WMLauncherModeManifest:
    normalized_wm = str(wm).strip().lower()
    if normalized_wm not in _VALID_WMS:
        raise ValueError(f"Unsupported window manager: {wm}")
    resolved_mode_name = str(mode_name or "vhk-launch").strip() or "vhk-launch"
    resolved_enter = str(mode_enter or "").strip()
    if not resolved_enter:
        raise ValueError("mode_enter is required")

    entry_key_list = tuple(str(k).strip() for k in (entry_keys or _DEFAULT_ENTRY_KEYS) if str(k).strip())
    if not entry_key_list:
        raise ValueError("Need at least one entry key")
    resolved_exit_keys = tuple(str(k).strip() for k in (exit_keys or ("Escape", "Return")) if str(k).strip())
    if max_entries is None:
        max_entries = len(entry_key_list)
    max_entries = max(0, min(int(max_entries), len(entry_key_list)))

    store = make_prompt_profile_store(project.root_dir, project.settings.prompt_profile_store)
    entries = build_palette_entries(
        project,
        include_hidden=include_hidden,
        include_presets=include_presets,
        include_profile_actions=include_profile_actions,
        include_profile_management_actions=include_profile_management_actions,
        profile_store=store,
        recent_first=not alpha,
        history_limit=history_limit,
    )
    if alpha:
        entries = sorted(entries, key=lambda row: row.label.casefold())
    selected_entries = entries[:max_entries]

    actions: list[WMLauncherModeAction] = []
    if include_launcher_action and launcher_key:
        resolved = resolve_launcher_command(
            project,
            launcher=launcher,
            launcher_path=launcher_path,
            launcher_id=launcher_id,
            mode_name=rofi_mode_name,
            show_icons=show_icons,
            extra_modes=extra_modes,
            command=command,
        )
        launcher_command = resolved.command
        if normalized_wm == "hyprland":
            launcher_command = _wrap_hypr_uwsm(launcher_command, uwsm_app=uwsm_app)
        label = launcher_label or {
            "palette-command": "Open VHK palette",
            "rofi-mode": "Open rofi launcher",
            "launcher-script": "Open launcher script",
        }.get(resolved.launcher, "Open launcher")
        actions.append(
            WMLauncherModeAction(
                key=str(launcher_key).strip(),
                label=label,
                command=launcher_command,
                kind="launcher",
                action="run",
            )
        )
        helper_path = resolved.helper_path
        launcher_mode_name_out = resolved.mode_name
    else:
        helper_path = None
        launcher_mode_name_out = None

    for key, entry in zip(entry_key_list, selected_entries):
        cmd = _entry_command(project, command=command, entry_id=entry.entry_id)
        if normalized_wm == "hyprland":
            cmd = _wrap_hypr_uwsm(cmd, uwsm_app=uwsm_app)
        actions.append(
            WMLauncherModeAction(
                key=str(key).strip(),
                label=entry.label,
                command=cmd,
                kind="entry",
                entry_id=entry.entry_id,
                macro=entry.macro,
                preset=entry.preset,
                prompt_profile=entry.prompt_profile,
                action=entry.action,
            )
        )

    lines: list[str] = []
    if normalized_wm in {"i3", "sway"}:
        lines.append(f"# VHK {normalized_wm} launcher mode for {project.name}")
        lines.append(f"# Enter mode '{resolved_mode_name}' with: {resolved_enter}")
        lines.append(f'bindsym {resolved_enter} mode "{resolved_mode_name}"')
        lines.append(f'mode "{resolved_mode_name}" {{')
        for ek in resolved_exit_keys:
            lines.append(f'    bindsym {ek} mode "default"')
        if not actions:
            lines.append("    # No launcher actions were selected.")
        for row in actions:
            exec_part = format_wm_exec_command(row.command, wm=normalized_wm, no_startup_id=(normalized_wm == "i3"))
            if one_shot:
                exec_part += '; mode "default"'
            lines.append(f"    bindsym --release {row.key} {exec_part}  # {row.label}")
        lines.append("}")
        snippet = "\n".join(lines) + "\n"
    else:
        enter_mods, enter_key = _parse_i3_keys_for_hypr(resolved_enter)
        lines.append(f"# VHK hyprland launcher submap for {project.name}")
        lines.append(f"# Enter submap '{resolved_mode_name}' with: {resolved_enter}")
        lines.append(f"bind = {enter_mods}, {enter_key}, submap, {resolved_mode_name}")
        lines.append("")
        if one_shot:
            lines.append(f"submap = {resolved_mode_name}, reset")
        else:
            lines.append(f"submap = {resolved_mode_name}")
        for ek in resolved_exit_keys:
            mods, key = _parse_i3_keys_for_hypr(ek)
            lines.append(f"bind = {mods}, {key}, submap, reset")
        if not actions:
            lines.append("# No launcher actions were selected.")
        for row in actions:
            mods, key = _parse_i3_keys_for_hypr(row.key)
            label = row.label.replace(",", " ").strip()
            if label:
                lines.append(f"bindrd = {mods}, {key}, {label}, exec, {row.command}")
            else:
                lines.append(f"bindr = {mods}, {key}, exec, {row.command}")
        lines.append("submap = reset")
        snippet = "\n".join(lines) + "\n"

    return WMLauncherModeManifest(
        wm=normalized_wm,
        mode_name=resolved_mode_name,
        mode_enter=resolved_enter,
        launcher=str(launcher).strip().lower(),
        one_shot=bool(one_shot),
        exit_keys=resolved_exit_keys,
        launcher_key=str(launcher_key).strip() if include_launcher_action and launcher_key else None,
        helper_path=helper_path,
        launcher_mode_name=launcher_mode_name_out,
        actions=tuple(actions),
        snippet=snippet,
        uwsm_app=bool(uwsm_app and normalized_wm == "hyprland"),
    )


def render_wm_launcher_mode_json(project: Project, **kwargs: Any) -> str:
    manifest = build_wm_launcher_mode_manifest(project, **kwargs)
    return json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2)
