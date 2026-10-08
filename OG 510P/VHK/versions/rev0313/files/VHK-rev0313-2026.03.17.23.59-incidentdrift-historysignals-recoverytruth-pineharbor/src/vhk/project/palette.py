from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from vhk.core.eventlog_history import collect_history
from vhk.core.models import Project
from vhk.project.preset_prompts import resolve_preset_profile_key
from vhk.project.prompt_profiles import PromptProfileStore


@dataclass(frozen=True)
class PaletteEntry:
    entry_id: str
    macro: str
    preset: str | None
    label: str
    action: str = "run"
    prompt_profile: str | None = None
    prompt_profile_key: str | None = None
    available_prompt_profiles: tuple[str, ...] = field(default_factory=tuple)
    description: str | None = None
    group: str | None = None
    icon: str | None = None
    tags: tuple[str, ...] = field(default_factory=tuple)
    hotkeys: tuple[str, ...] = field(default_factory=tuple)
    hotstrings: tuple[str, ...] = field(default_factory=tuple)
    search_terms: tuple[str, ...] = field(default_factory=tuple)
    vars: dict[str, Any] = field(default_factory=dict)
    needs_prompt: bool = False
    prompt_fields: tuple[str, ...] = field(default_factory=tuple)
    last_run_ts: float | None = None
    recent_runs: int = 0
    hidden: bool = False
    preset_hidden: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "entry_id": self.entry_id,
            "macro": self.macro,
            "preset": self.preset,
            "label": self.label,
            "action": self.action,
            "prompt_profile": self.prompt_profile,
            "prompt_profile_key": self.prompt_profile_key,
            "available_prompt_profiles": list(self.available_prompt_profiles),
            "description": self.description,
            "group": self.group,
            "icon": self.icon,
            "tags": list(self.tags),
            "hotkeys": list(self.hotkeys),
            "hotstrings": list(self.hotstrings),
            "search_terms": list(self.search_terms),
            "vars": dict(self.vars),
            "needs_prompt": self.needs_prompt,
            "prompt_fields": list(self.prompt_fields),
            "last_run_ts": self.last_run_ts,
            "recent_runs": self.recent_runs,
            "hidden": self.hidden,
            "preset_hidden": self.preset_hidden,
        }


def _collect_recent_macro_stats(project: Project, *, limit: int = 50) -> tuple[dict[str, float], dict[str, int]]:
    log_dir = Path(project.root_dir) / project.settings.log_dir
    latest_ts: dict[str, float] = {}
    counts: dict[str, int] = {}
    for row in collect_history(log_dir, limit=limit, status="all"):
        macro = str(row.macro or "").strip()
        if not macro:
            continue
        counts[macro] = counts.get(macro, 0) + 1
        ts = row.started_ts
        if ts is None:
            continue
        prev = latest_ts.get(macro)
        if prev is None or ts > prev:
            latest_ts[macro] = ts
    return latest_ts, counts


_ACTION_ICONS = {
    "edit_profile": "document-edit",
    "copy_profile": "edit-copy",
    "rename_profile": "insert-text",
    "delete_profile": "edit-delete",
}


def _unique_terms(*parts: object) -> tuple[str, ...]:
    seen: set[str] = set()
    out: list[str] = []
    for part in parts:
        if part is None:
            continue
        if isinstance(part, (list, tuple, set)):
            for item in part:
                for term in _unique_terms(item):
                    if term not in seen:
                        seen.add(term)
                        out.append(term)
            continue
        term = str(part).strip()
        if term and term not in seen:
            seen.add(term)
            out.append(term)
    return tuple(out)


def _entry_icon(*, action: str, macro_icon: str | None, preset_icon: str | None = None) -> str | None:
    if action != "run":
        return _ACTION_ICONS.get(action) or preset_icon or macro_icon
    return preset_icon or macro_icon



def find_palette_entry(entries: list[PaletteEntry], *, entry_id: str | None = None, label: str | None = None) -> PaletteEntry | None:
    """Resolve one palette entry by stable id or display label."""

    if entry_id is not None:
        wanted = str(entry_id).strip()
        for entry in entries:
            if entry.entry_id == wanted:
                return entry
        return None
    if label is not None:
        wanted = str(label)
        for entry in entries:
            if entry.label == wanted:
                return entry
    return None


def build_palette_entries(
    project: Project,
    *,
    include_hidden: bool = False,
    include_presets: bool = True,
    include_profile_actions: bool = True,
    include_profile_management_actions: bool = False,
    profile_store: PromptProfileStore | None = None,
    recent_first: bool = False,
    history_limit: int = 50,
) -> list[PaletteEntry]:
    """Build launcher-friendly palette rows for a project.

    The label tries to stay readable inside launcher/dmenu-style UIs while still
    surfacing the most relevant context: description first, then hotkeys,
    hotstrings, and tags.
    """

    hotkeys: dict[str, list[str]] = {}
    for binding in project.bindings:
        hotkeys.setdefault(binding.macro, []).append(binding.keys)

    hotstrings: dict[str, list[str]] = {}
    for hs in project.hotstrings:
        if not hs.enabled:
            continue
        hotstrings.setdefault(hs.macro, []).append(hs.trigger)

    recent_latest, recent_counts = _collect_recent_macro_stats(project, limit=history_limit)

    entries: list[PaletteEntry] = []

    def _make_entry(
        *,
        macro_name: str,
        group: str | None,
        description: str | None,
        icon: str | None,
        tags: tuple[str, ...],
        hk: tuple[str, ...],
        hs: tuple[str, ...],
        last_run_ts: float | None,
        recent_runs: int,
        hidden: bool,
        action: str = "run",
        preset_name: str | None = None,
        preset_icon: str | None = None,
        preset_hidden: bool = False,
        vars: dict[str, Any] | None = None,
        needs_prompt: bool = False,
        prompt_fields: tuple[str, ...] = (),
        prompt_profile: str | None = None,
        prompt_profile_key: str | None = None,
        available_prompt_profiles: tuple[str, ...] = (),
    ) -> PaletteEntry:
        head = f"{group} › {macro_name}" if group else macro_name
        if preset_name:
            head += f" [{preset_name}]"
        if prompt_profile:
            head += f" ‹{prompt_profile}›"
        if action == "edit_profile":
            head += " ✎ edit"
        elif action == "copy_profile":
            head += " ⎘ copy"
        elif action == "rename_profile":
            head += " ✎ rename"
        elif action == "delete_profile":
            head += " ✕ delete"
        extras: list[str] = []
        if description:
            extras.append(description)
        if hk:
            extras.append("keys: " + ", ".join(hk[:2]))
        if hs:
            extras.append("triggers: " + ", ".join(hs[:2]))
        if tags:
            extras.append("tags: " + ", ".join(tags[:3]))
        if needs_prompt and prompt_fields:
            extras.append("asks: " + ", ".join(prompt_fields[:3]))
        if recent_runs:
            extras.append(f"recent: {recent_runs}")
        label = head + (" — " + " · ".join(extras) if extras else "")
        entry_id = f"{macro_name}@{preset_name}" if preset_name else macro_name
        if prompt_profile:
            entry_id += f"#{prompt_profile}"
        if action != "run":
            action_suffix = {
                "edit_profile": "edit",
                "copy_profile": "copy",
                "rename_profile": "rename",
                "delete_profile": "delete",
            }.get(action, action)
            entry_id += f"!{action_suffix}"
        search_terms = _unique_terms(
            entry_id,
            macro_name,
            preset_name,
            prompt_profile,
            action.replace("_", " ") if action else None,
            group,
            description,
            icon,
            preset_icon,
            tags,
            hk,
            hs,
            prompt_fields,
            available_prompt_profiles,
        )
        return PaletteEntry(
            entry_id=entry_id,
            macro=macro_name,
            preset=preset_name,
            label=label,
            action=action,
            prompt_profile=prompt_profile,
            prompt_profile_key=prompt_profile_key,
            available_prompt_profiles=available_prompt_profiles,
            description=description,
            group=group,
            icon=_entry_icon(action=action, macro_icon=icon, preset_icon=preset_icon),
            tags=tags,
            hotkeys=hk,
            hotstrings=hs,
            search_terms=search_terms,
            vars=dict(vars or {}),
            needs_prompt=needs_prompt,
            prompt_fields=prompt_fields,
            last_run_ts=last_run_ts,
            recent_runs=recent_runs,
            hidden=hidden,
            preset_hidden=preset_hidden,
        )

    for macro_name, macro in project.macros.items():
        hidden = bool(getattr(macro, "hidden", False))
        if hidden and not include_hidden:
            continue

        group = str(getattr(macro, "group", "") or "").strip() or None
        description = str(getattr(macro, "description", "") or "").strip() or None
        icon = str(getattr(macro, "icon", "") or "").strip() or None
        tags = tuple(str(x) for x in (getattr(macro, "tags", []) or []) if str(x).strip())
        hk = tuple(hotkeys.get(macro_name, []))
        hs = tuple(hotstrings.get(macro_name, []))
        last_run_ts = recent_latest.get(macro_name)
        recent_runs = int(recent_counts.get(macro_name, 0))

        entries.append(
            _make_entry(
                macro_name=macro_name,
                group=group,
                description=description,
                icon=icon,
                tags=tags,
                hk=hk,
                hs=hs,
                last_run_ts=last_run_ts,
                recent_runs=recent_runs,
                hidden=hidden,
            )
        )

        if include_presets:
            for preset in getattr(macro, "presets", []) or []:
                preset_hidden = bool(getattr(preset, "hidden", False))
                if preset_hidden and not include_hidden:
                    continue
                preset_name = str(getattr(preset, "name", "") or "").strip()
                if not preset_name:
                    continue
                preset_description = str(getattr(preset, "description", "") or "").strip() or None
                preset_icon = str(getattr(preset, "icon", "") or "").strip() or None
                preset_tags_raw = [str(x) for x in (getattr(preset, "tags", []) or []) if str(x).strip()]
                merged_tags = tuple(dict.fromkeys([*tags, *preset_tags_raw]))
                merged_desc = preset_description or description
                prompt_form = getattr(preset, "prompt_form", None)
                prompt_fields = tuple(str(f.name) for f in (getattr(prompt_form, "fields", []) or []) if str(getattr(f, "name", "")).strip())
                prompt_profile_key = None
                available_prompt_profiles: tuple[str, ...] = ()
                if prompt_form is not None:
                    prompt_ctx = {"macro": {"name": macro_name}, "preset": {"name": preset_name}, **dict(getattr(preset, "vars", {}) or {})}
                    prompt_profile_key = resolve_preset_profile_key(prompt_form, prompt_ctx, macro_name=macro_name, preset_name=preset_name)
                    if profile_store is not None and prompt_profile_key:
                        available_prompt_profiles = tuple(profile_store.list_profiles(prompt_profile_key))
                entries.append(
                    _make_entry(
                        macro_name=macro_name,
                        group=group,
                        description=merged_desc,
                        icon=icon,
                        preset_icon=preset_icon,
                        tags=merged_tags,
                        hk=hk,
                        hs=hs,
                        last_run_ts=last_run_ts,
                        recent_runs=recent_runs,
                        hidden=hidden,
                        preset_name=preset_name,
                        preset_hidden=preset_hidden,
                        vars=dict(getattr(preset, "vars", {}) or {}),
                        needs_prompt=bool(prompt_form and getattr(prompt_form, "fields", [])),
                        prompt_fields=prompt_fields,
                        prompt_profile_key=prompt_profile_key,
                        available_prompt_profiles=available_prompt_profiles,
                    )
                )
                if include_profile_actions and prompt_profile_key and available_prompt_profiles:
                    for profile_name in available_prompt_profiles:
                        entries.append(
                            _make_entry(
                                macro_name=macro_name,
                                group=group,
                                description=merged_desc,
                                icon=icon,
                                preset_icon=preset_icon,
                                tags=merged_tags,
                                hk=hk,
                                hs=hs,
                                last_run_ts=last_run_ts,
                                recent_runs=recent_runs,
                                hidden=hidden,
                                preset_name=preset_name,
                                preset_hidden=preset_hidden,
                                vars=dict(getattr(preset, "vars", {}) or {}),
                                needs_prompt=bool(prompt_form and getattr(prompt_form, "fields", [])),
                                prompt_fields=prompt_fields,
                                prompt_profile=profile_name,
                                prompt_profile_key=prompt_profile_key,
                                available_prompt_profiles=available_prompt_profiles,
                            )
                        )
                        if include_profile_management_actions:
                            for action in ("edit_profile", "copy_profile", "rename_profile", "delete_profile"):
                                entries.append(
                                    _make_entry(
                                        macro_name=macro_name,
                                        group=group,
                                        description=merged_desc,
                                        icon=icon,
                                        preset_icon=preset_icon,
                                        tags=merged_tags,
                                        hk=hk,
                                        hs=hs,
                                        last_run_ts=last_run_ts,
                                        recent_runs=recent_runs,
                                        hidden=hidden,
                                        action=action,
                                        preset_name=preset_name,
                                        preset_hidden=preset_hidden,
                                        vars=dict(getattr(preset, "vars", {}) or {}),
                                        needs_prompt=bool(prompt_form and getattr(prompt_form, "fields", [])),
                                        prompt_fields=prompt_fields,
                                        prompt_profile=profile_name,
                                        prompt_profile_key=prompt_profile_key,
                                        available_prompt_profiles=available_prompt_profiles,
                                    )
                                )

    if recent_first:
        entries.sort(
            key=lambda e: (
                -(1 if e.last_run_ts is not None else 0),
                -(e.last_run_ts or 0.0),
                str(e.group or ""),
                e.macro,
                str(e.preset or ""),
                str(e.prompt_profile or ""),
                str(e.action or ""),
            )
        )
    else:
        entries.sort(key=lambda e: (str(e.group or ""), e.macro, str(e.preset or ""), str(e.prompt_profile or ""), str(e.action or "")))
    return entries
