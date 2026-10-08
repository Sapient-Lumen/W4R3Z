from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from vhk.core.models import Project
from vhk.project.palette import PaletteEntry, build_palette_entries
from vhk.project.prompt_profiles import PromptProfileStore
from vhk.project.support_posture import summarize_support_posture


_RESERVED_CHARS = set(" \t\n\"'\\><~|&;$*?#()`")
_ACTION_LABELS = {
    "run": "Run",
    "edit_profile": "Edit profile",
    "copy_profile": "Copy profile",
    "rename_profile": "Rename profile",
    "delete_profile": "Delete profile",
}


@dataclass(frozen=True)
class DesktopAction:
    action_id: str
    name: str
    exec_argv: tuple[str, ...]
    icon: str | None = None



def desktop_exec_quote_arg(arg: str) -> str:
    """Quote one Exec= argument using desktop-entry rules.

    This is intentionally conservative for the Linux paths VHK is expected to
    generate most often: project paths, macro names, preset names, and prompt
    profile names. Literal percent signs are escaped as ``%%`` to avoid field
    code expansion, and reserved characters trigger double-quote wrapping.
    """

    value = str(arg).replace("%", "%%")
    if value and not any(ch in _RESERVED_CHARS for ch in value):
        return value
    escaped = (
        value.replace("\\", "\\\\\\\\")
        .replace('"', '\\"')
        .replace("`", "\\`")
        .replace("$", "\\\\$")
    )
    return f'"{escaped}"'



def desktop_exec_join(argv: Iterable[str]) -> str:
    return " ".join(desktop_exec_quote_arg(part) for part in argv)



def _slugify(text: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", str(text).strip()).strip("-").lower()
    return slug or "project"



def _camelize_slug(slug: str) -> str:
    parts = [part for part in re.split(r"[^A-Za-z0-9]+", slug) if part]
    if not parts:
        return "Project"
    return "".join(part[:1].upper() + part[1:] for part in parts)



def default_desktop_file_id(project: Project, *, desktop_id: str | None = None) -> str:
    if desktop_id:
        cleaned = str(desktop_id).strip()
        return cleaned[:-8] if cleaned.endswith(".desktop") else cleaned
    return f"vhk-{_slugify(project.name)}"



def default_desktop_file_name(project: Project, *, desktop_id: str | None = None) -> str:
    file_id = default_desktop_file_id(project, desktop_id=desktop_id)
    return file_id if file_id.endswith(".desktop") else f"{file_id}.desktop"



def default_desktop_install_path(
    project: Project,
    *,
    env: dict[str, str] | None = None,
    desktop_id: str | None = None,
) -> Path:
    env_map = dict(os.environ if env is None else env)
    xdg_data_home = env_map.get("XDG_DATA_HOME")
    if xdg_data_home:
        base = Path(xdg_data_home)
    else:
        base = Path.home() / ".local" / "share"
    return base / "applications" / default_desktop_file_name(project, desktop_id=desktop_id)



def _action_name(entry: PaletteEntry) -> str:
    action_head = _ACTION_LABELS.get(entry.action, entry.action.replace("_", " ").title())
    target = entry.macro
    if entry.preset:
        target += f" [{entry.preset}]"
    if entry.prompt_profile:
        target += f" ‹{entry.prompt_profile}›"
    return f"{action_head} {target}"



def _action_identifier_seed(entry: PaletteEntry) -> str:
    seed = entry.entry_id.replace("@", "-").replace("#", "-").replace("!", "-")
    seed = re.sub(r"[^A-Za-z0-9-]+", "-", seed).strip("-")
    return seed or "Action"



def _unique_action_id(seed: str, seen: set[str]) -> str:
    seed = re.sub(r"[^A-Za-z0-9-]+", "-", seed).strip("-") or "Action"
    if seed[:1].isdigit():
        seed = f"A-{seed}"
    base = seed[:48] or "Action"
    candidate = base
    idx = 2
    while candidate in seen:
        suffix = f"-{idx}"
        candidate = (base[: max(1, 48 - len(suffix))] + suffix).strip("-")
        idx += 1
    seen.add(candidate)
    return candidate



def _palette_entry_to_argv(entry: PaletteEntry, *, command: str, project_dir: str) -> tuple[str, ...]:
    argv: list[str] = [command, "run", project_dir, entry.macro]
    if entry.preset:
        argv.extend(["--preset", entry.preset])
    if entry.prompt_profile:
        argv.extend(["--prompt-profile", entry.prompt_profile])
    return tuple(argv)



def build_desktop_actions(
    project: Project,
    *,
    command: str = "vhk",
    profile_store: PromptProfileStore | None = None,
    include_hidden: bool = False,
    include_presets: bool = True,
    include_profile_actions: bool = True,
    alpha: bool = False,
    history_limit: int = 50,
    max_actions: int = 8,
) -> list[DesktopAction]:
    entries = build_palette_entries(
        project,
        include_hidden=include_hidden,
        include_presets=include_presets,
        include_profile_actions=include_profile_actions,
        include_profile_management_actions=False,
        profile_store=profile_store,
        recent_first=not alpha,
        history_limit=history_limit,
    )
    seen_ids: set[str] = set()
    actions: list[DesktopAction] = []
    for entry in entries:
        if entry.action != "run":
            continue
        actions.append(
            DesktopAction(
                action_id=_unique_action_id(_action_identifier_seed(entry), seen_ids),
                name=_action_name(entry),
                exec_argv=_palette_entry_to_argv(entry, command=command, project_dir=project.root_dir),
                icon=entry.icon,
            )
        )
        if max_actions and len(actions) >= max_actions:
            break
    return actions



def _desktop_escape_value(value: str) -> str:
    return str(value).replace("\\", "\\\\").replace("\n", "\\n")



def render_desktop_entry(
    project: Project,
    *,
    command: str = "vhk",
    desktop_id: str | None = None,
    entry_name: str | None = None,
    comment: str | None = None,
    icon: str | None = None,
    categories: tuple[str, ...] = ("Utility",),
    keywords: tuple[str, ...] = ("automation", "macro", "hotkey", "launcher"),
    include_actions: bool = True,
    profile_store: PromptProfileStore | None = None,
    include_hidden: bool = False,
    include_presets: bool = True,
    include_profile_actions: bool = True,
    alpha: bool = False,
    history_limit: int = 50,
    max_actions: int = 8,
) -> str:
    support_posture = summarize_support_posture(project.root_dir)
    file_id = default_desktop_file_id(project, desktop_id=desktop_id)
    display_name = (entry_name or f"VHK {project.name}").strip()
    headline = str(support_posture.get("headline") or "").strip()
    default_comment = f"Open the VHK palette for {project.name}"
    if headline:
        default_comment += f" — {headline}"
    display_comment = (comment or default_comment).strip()
    reference_targets = [str(x) for x in list(support_posture.get("reference_targets") or []) if str(x)]
    supported_targets = [str(x) for x in list(support_posture.get("supported_targets") or []) if str(x)]
    caveated_targets = [str(x) for x in list(support_posture.get("caveated_targets") or []) if str(x)]
    experimental_targets = [str(x) for x in list(support_posture.get("experimental_targets") or []) if str(x)]
    support_docs = [str(x) for x in list(support_posture.get("docs") or []) if str(x)]
    release_reference = [str(x) for x in list(support_posture.get("release_lane_reference_ids") or []) if str(x)]
    release_supported = [str(x) for x in list(support_posture.get("release_lane_supported_ids") or []) if str(x)]
    release_caveated = [str(x) for x in list(support_posture.get("release_lane_caveated_ids") or []) if str(x)]
    release_experimental = [str(x) for x in list(support_posture.get("release_lane_experimental_ids") or []) if str(x)]
    flagship_lane = str(support_posture.get("flagship_lane_title") or support_posture.get("flagship_lane_id") or "").strip()
    flagship_deploy_style = str(support_posture.get("flagship_deploy_style") or "").strip()
    flagship_delivery = str(support_posture.get("flagship_delivery_headline") or "").strip()
    actions = build_desktop_actions(
        project,
        command=command,
        profile_store=profile_store,
        include_hidden=include_hidden,
        include_presets=include_presets,
        include_profile_actions=include_profile_actions,
        alpha=alpha,
        history_limit=history_limit,
        max_actions=max_actions,
    ) if include_actions else []

    lines = [
        "[Desktop Entry]",
        "Version=1.5",
        "Type=Application",
        f"Name={_desktop_escape_value(display_name)}",
        f"Comment={_desktop_escape_value(display_comment)}",
        f"Exec={desktop_exec_join((command, 'palette', project.root_dir))}",
        "TryExec=vhk" if command == "vhk" else f"TryExec={_desktop_escape_value(command)}",
        f"Path={_desktop_escape_value(project.root_dir)}",
        "Terminal=false",
        f"Categories={';'.join([*categories, ''])}",
        f"Keywords={';'.join([*keywords, project.name, ''])}",
        f"X-VHK-Project={_desktop_escape_value(project.name)}",
        f"X-VHK-ProjectDir={_desktop_escape_value(project.root_dir)}",
        f"X-VHK-DesktopFileId={_desktop_escape_value(file_id)}",
        f"X-VHK-Support-Headline={_desktop_escape_value(headline)}",
        f"X-VHK-Support-ClaimSource={_desktop_escape_value(str(support_posture.get('claim_source') or 'planner_recommendations'))}",
    ]
    if reference_targets:
        lines.append(f"X-VHK-Support-Reference={_desktop_escape_value('; '.join(reference_targets))}")
    if supported_targets:
        lines.append(f"X-VHK-Support-Supported={_desktop_escape_value('; '.join(supported_targets))}")
    if caveated_targets:
        lines.append(f"X-VHK-Support-Caveated={_desktop_escape_value('; '.join(caveated_targets))}")
    if experimental_targets:
        lines.append(f"X-VHK-Support-Experimental={_desktop_escape_value('; '.join(experimental_targets))}")
    if support_docs:
        lines.append(f"X-VHK-Support-Docs={_desktop_escape_value(';'.join([*support_docs, '']))}")
    if flagship_lane:
        lines.append(f"X-VHK-Release-Flagship={_desktop_escape_value(flagship_lane)}")
    if release_reference:
        lines.append(f"X-VHK-Release-Reference={_desktop_escape_value('; '.join(release_reference))}")
    if release_supported:
        lines.append(f"X-VHK-Release-Supported={_desktop_escape_value('; '.join(release_supported))}")
    if release_caveated:
        lines.append(f"X-VHK-Release-Caveated={_desktop_escape_value('; '.join(release_caveated))}")
    if release_experimental:
        lines.append(f"X-VHK-Release-Experimental={_desktop_escape_value('; '.join(release_experimental))}")
    if flagship_deploy_style:
        lines.append(f"X-VHK-Release-DeployStyle={_desktop_escape_value(flagship_deploy_style)}")
    if flagship_delivery:
        lines.append(f"X-VHK-Release-Delivery={_desktop_escape_value(flagship_delivery)}")
    if icon:
        lines.append(f"Icon={_desktop_escape_value(icon)}")
    if actions:
        lines.append(f"Actions={';'.join([*(a.action_id for a in actions), ''])}")
    lines.append("")
    for action in actions:
        lines.extend(
            [
                f"[Desktop Action {action.action_id}]",
                f"Name={_desktop_escape_value(action.name)}",
                f"Exec={desktop_exec_join(action.exec_argv)}",
            ]
        )
        if action.icon:
            lines.append(f"Icon={_desktop_escape_value(action.icon)}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
