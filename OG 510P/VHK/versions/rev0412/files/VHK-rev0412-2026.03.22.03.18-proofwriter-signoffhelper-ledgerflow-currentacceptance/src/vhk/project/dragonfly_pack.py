from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import shlex
from typing import Any, Literal

from vhk.core.models import I3WindowSelector, Macro, MacroPreset, Project


@dataclass(frozen=True)
class DragonflyEntry:
    macro: str
    preset: str | None
    label: str
    description: str | None
    spoken_forms: tuple[str, ...]
    argv: tuple[str, ...]
    command_id: str
    voice_context: dict[str, Any] | None = None
    voice_context_label: str | None = None
    skipped: bool = False
    skip_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "macro": self.macro,
            "preset": self.preset,
            "label": self.label,
            "description": self.description,
            "spoken_forms": list(self.spoken_forms),
            "argv": list(self.argv),
            "command_id": self.command_id,
            "voice_context": self.voice_context,
            "voice_context_label": self.voice_context_label,
            "skipped": self.skipped,
            "skip_reason": self.skip_reason,
        }


@dataclass(frozen=True)
class DragonflyPackManifest:
    project: str
    grammar_name: str
    module_name: str
    module_path: Path
    readme_path: Path
    commands_path: Path
    commands: tuple[DragonflyEntry, ...]
    skipped: tuple[DragonflyEntry, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "project": self.project,
            "grammar_name": self.grammar_name,
            "module_name": self.module_name,
            "module_path": str(self.module_path),
            "readme_path": str(self.readme_path),
            "commands_path": str(self.commands_path),
            "command_count": len(self.commands),
            "skipped_count": len(self.skipped),
            "commands": [item.to_dict() for item in self.commands],
            "skipped": [item.to_dict() for item in self.skipped],
        }


_WORD_RE = re.compile(r"[^a-z0-9]+")


SUPPORTED_VOICE_CONTEXT_FIELDS: dict[str, tuple[str, ...]] = {
    "dragonfly": ("class", "title", "instance", "window_role"),
    "talon": ("class", "title"),
}


BACKEND_LABELS = {
    "dragonfly": "Dragonfly",
    "talon": "Talon",
}


@dataclass(frozen=True)
class VoicePhraseCollision:
    backend: Literal["dragonfly", "talon"]
    phrase: str
    context_label: str | None
    targets: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "backend": self.backend,
            "phrase": self.phrase,
            "context_label": self.context_label,
            "targets": list(self.targets),
        }



def _slugify(text: str) -> str:
    normalized = _WORD_RE.sub("-", str(text).strip().lower()).strip("-")
    return normalized or "project"



def _normalize_spoken_form(text: str) -> str:
    value = str(text or "").strip().lower()
    value = value.replace("_", " ").replace("-", " ")
    value = re.sub(r"[^a-z0-9 ]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value



def _phrase_candidates(macro: Macro, *, preset: MacroPreset | None = None) -> list[str]:
    explicit: list[str] = []
    if preset is not None:
        explicit.extend(str(item) for item in getattr(preset, "voice_phrases", []) or [])
    if not explicit:
        explicit.extend(str(item) for item in getattr(macro, "voice_phrases", []) or [])

    candidates: list[str] = []
    for item in explicit:
        spoken = _normalize_spoken_form(item)
        if spoken:
            candidates.append(spoken)

    if preset is not None:
        candidates.append(_normalize_spoken_form(f"{macro.name} {preset.name}"))
        candidates.append(_normalize_spoken_form(f"{preset.name} {macro.name}"))
    else:
        candidates.append(_normalize_spoken_form(macro.name))
        if macro.group:
            candidates.append(_normalize_spoken_form(f"{macro.group} {macro.name}"))

    out: list[str] = []
    seen: set[str] = set()
    for item in candidates:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out



def _entry_label(macro: Macro, *, preset: MacroPreset | None = None) -> str:
    head = f"{macro.group} › {macro.name}" if macro.group else macro.name
    if preset is not None:
        head += f" [{preset.name}]"
    return head



def _entry_argv(
    project: Project,
    *,
    macro: Macro,
    preset: MacroPreset | None = None,
    command: str = "vhk",
) -> tuple[str, ...]:
    prefix = tuple(shlex.split(command)) or ("vhk",)
    argv = [*prefix, "run", project.root_dir, macro.name, "--quiet"]
    if preset is not None:
        argv.extend(["--preset", preset.name])
    return tuple(argv)



def _voice_selector(macro: Macro, *, preset: MacroPreset | None = None) -> I3WindowSelector | None:
    if preset is not None and getattr(preset, "voice_when", None) is not None:
        return preset.voice_when
    return getattr(macro, "voice_when", None)



def _selector_fields(selector: I3WindowSelector | None) -> dict[str, Any]:
    if selector is None:
        return {}
    return selector.model_dump(by_alias=True, exclude_none=True)



def _context_label_from_payload(payload: dict[str, Any] | None) -> str | None:
    if not payload:
        return None
    parts: list[str] = []
    if payload.get("cls"):
        parts.append(f"class={payload['cls']}")
    if payload.get("app"):
        parts.append(f"app={payload['app']}")
    if payload.get("title"):
        parts.append(f"title={payload['title']}")
    if payload.get("instance"):
        parts.append(f"instance={payload['instance']}")
    if payload.get("role"):
        parts.append(f"role={payload['role']}")
    return ", ".join(parts) or None



def _context_slug_from_payload(payload: dict[str, Any] | None) -> str:
    label = _context_label_from_payload(payload) or "global"
    return _slugify(label)


def _voice_scope_key(payload: dict[str, Any] | None) -> str:
    return json.dumps(payload or {}, sort_keys=True, ensure_ascii=False)


def _command_id(
    macro: Macro,
    *,
    preset: MacroPreset | None = None,
    context_payload: dict[str, Any] | None = None,
    used_ids: set[str],
) -> str:
    parts = [macro.name]
    if preset is not None:
        parts.append(preset.name)
    if context_payload:
        parts.append(_context_slug_from_payload(context_payload))
    base = _slugify(" ".join(parts))
    candidate = base
    index = 2
    while candidate in used_ids:
        candidate = f"{base}-{index}"
        index += 1
    used_ids.add(candidate)
    return candidate



def _translate_voice_context(
    selector: I3WindowSelector | None,
    *,
    backend: Literal["dragonfly", "talon"],
) -> tuple[dict[str, Any] | None, str | None, list[str]]:
    if selector is None:
        return None, None, []

    fields = _selector_fields(selector)
    if not fields:
        return None, None, []

    supported = set(SUPPORTED_VOICE_CONTEXT_FIELDS[backend])
    unsupported: list[str] = []
    payload: dict[str, Any] = {}

    if fields.get("title") is not None and fields.get("title_regex"):
        unsupported.append("title_regex")
    if fields.get("app_id") is not None:
        unsupported.append("app_id")
    if fields.get("app_id_regex"):
        unsupported.append("app_id_regex")

    for key in fields:
        if key in {"title_regex", "app_id", "app_id_regex"}:
            continue
        if key not in supported:
            unsupported.append(key)

    if backend == "dragonfly":
        if fields.get("class"):
            payload["cls"] = str(fields["class"])
        if fields.get("title") and not fields.get("title_regex"):
            payload["title"] = str(fields["title"])
        if fields.get("instance"):
            payload["instance"] = str(fields["instance"])
        if fields.get("window_role"):
            payload["role"] = str(fields["window_role"])
    elif backend == "talon":
        if fields.get("class"):
            payload["app"] = str(fields["class"])
        if fields.get("title") and not fields.get("title_regex"):
            payload["title"] = str(fields["title"])

    unsupported = sorted(set(str(item) for item in unsupported))
    if unsupported:
        return None, None, unsupported
    if not payload:
        return None, None, sorted(fields)
    return payload, _context_label_from_payload(payload), []



def build_dragonfly_entries(
    project: Project,
    *,
    command: str = "vhk",
    include_hidden: bool = False,
    include_presets: bool = True,
    include_prompt_entries: bool = False,
    backend: Literal["dragonfly", "talon"] = "dragonfly",
) -> tuple[list[DragonflyEntry], list[DragonflyEntry]]:
    commands: list[DragonflyEntry] = []
    skipped: list[DragonflyEntry] = []
    used_phrase_scopes: dict[str, set[str]] = {}
    used_command_ids: set[str] = set()

    def register(macro: Macro, *, preset: MacroPreset | None = None) -> None:
        hidden = bool(macro.hidden or (preset.hidden if preset is not None else False))
        if hidden and not include_hidden:
            return

        label = _entry_label(macro, preset=preset)
        description = preset.description if preset is not None else macro.description
        argv = _entry_argv(project, macro=macro, preset=preset, command=command)
        overlay_prompt = bool(getattr(preset, "prompt_form", None)) if preset is not None else False
        if overlay_prompt and not include_prompt_entries:
            skipped.append(
                DragonflyEntry(
                    macro=macro.name,
                    preset=preset.name if preset is not None else None,
                    label=label,
                    description=description,
                    spoken_forms=tuple(),
                    argv=argv,
                    command_id=_command_id(macro, preset=preset, used_ids=used_command_ids),
                    skipped=True,
                    skip_reason="preset prompt overlay requires interactive input",
                )
            )
            return

        selector = _voice_selector(macro, preset=preset)
        context_payload, context_label, unsupported_context = _translate_voice_context(selector, backend=backend)
        if unsupported_context:
            backend_label = BACKEND_LABELS[backend]
            skipped.append(
                DragonflyEntry(
                    macro=macro.name,
                    preset=preset.name if preset is not None else None,
                    label=label,
                    description=description,
                    spoken_forms=tuple(),
                    argv=argv,
                    command_id=_command_id(macro, preset=preset, used_ids=used_command_ids),
                    skipped=True,
                    skip_reason=(
                        f"voice context uses unsupported {backend_label} selector fields: "
                        + ", ".join(unsupported_context)
                    ),
                )
            )
            return

        command_id = _command_id(macro, preset=preset, context_payload=context_payload, used_ids=used_command_ids)
        scope_key = _voice_scope_key(context_payload)
        used_phrases = used_phrase_scopes.setdefault(scope_key, set())
        phrases = [phrase for phrase in _phrase_candidates(macro, preset=preset) if phrase not in used_phrases]
        if not phrases:
            fallback = _normalize_spoken_form(f"{macro.name} {preset.name if preset is not None else 'macro'}")
            if fallback and fallback not in used_phrases:
                phrases = [fallback]

        if not phrases:
            skipped.append(
                DragonflyEntry(
                    macro=macro.name,
                    preset=preset.name if preset is not None else None,
                    label=label,
                    description=description,
                    spoken_forms=tuple(),
                    argv=argv,
                    command_id=command_id,
                    skipped=True,
                    skip_reason="no unique spoken forms remained after deduplication",
                )
            )
            return

        for phrase in phrases:
            used_phrases.add(phrase)
        commands.append(
            DragonflyEntry(
                macro=macro.name,
                preset=preset.name if preset is not None else None,
                label=label,
                description=description,
                spoken_forms=tuple(phrases),
                argv=argv,
                command_id=command_id,
                voice_context=context_payload,
                voice_context_label=context_label,
            )
        )

    for macro in project.macros.values():
        register(macro)
        if include_presets:
            for preset in macro.presets:
                register(macro, preset=preset)

    commands.sort(key=lambda item: (item.voice_context_label or "", item.macro, item.preset or ""))
    skipped.sort(key=lambda item: (item.macro, item.preset or ""))
    return commands, skipped



def find_voice_phrase_collisions(
    project: Project,
    *,
    backend: Literal["dragonfly", "talon"],
    include_hidden: bool = False,
    include_presets: bool = True,
    include_prompt_entries: bool = False,
) -> list[VoicePhraseCollision]:
    collisions: list[VoicePhraseCollision] = []
    buckets: dict[tuple[str, str], list[str]] = {}

    def register(macro: Macro, *, preset: MacroPreset | None = None) -> None:
        hidden = bool(macro.hidden or (preset.hidden if preset is not None else False))
        if hidden and not include_hidden:
            return
        if preset is not None and bool(getattr(preset, "prompt_form", None)) and not include_prompt_entries:
            return
        selector = _voice_selector(macro, preset=preset)
        context_payload, _context_label, unsupported_context = _translate_voice_context(selector, backend=backend)
        if unsupported_context:
            return
        scope_key = _voice_scope_key(context_payload)
        label = _entry_label(macro, preset=preset)
        for phrase in _phrase_candidates(macro, preset=preset):
            buckets.setdefault((scope_key, phrase), []).append(label)

    for macro in project.macros.values():
        register(macro)
        if include_presets:
            for preset in macro.presets:
                register(macro, preset=preset)

    for (scope_key, phrase), labels in sorted(buckets.items()):
        unique = tuple(sorted(dict.fromkeys(labels)))
        if len(unique) < 2:
            continue
        payload = json.loads(scope_key)
        collisions.append(
            VoicePhraseCollision(
                backend=backend,
                phrase=phrase,
                context_label=_context_label_from_payload(payload) if payload else None,
                targets=unique,
            )
        )
    return collisions


def default_dragonfly_dir(project: Project) -> Path:
    return Path(project.root_dir) / "integrations" / "dragonfly"



def default_dragonfly_module_name(project: Project) -> str:
    return f"_vhk_{_slugify(project.name)}_commands.py"



def _module_header(*, grammar_name: str, project_name: str) -> str:
    return f'''"""Auto-generated Dragonfly command module for {project_name}.

Generated by `vhk gen-dragonfly-pack`.

This module intentionally calls back into VHK (`vhk run ...`) instead of
re-encoding the automation graph inside Dragonfly. That keeps voice triggering
as an optional adapter rather than a second execution engine.
"""'''



def _group_commands_by_context(commands: list[DragonflyEntry]) -> list[dict[str, Any]]:
    groups: dict[str, dict[str, Any]] = {}
    for entry in commands:
        key = json.dumps(entry.voice_context or {}, sort_keys=True, ensure_ascii=False)
        group = groups.get(key)
        if group is None:
            group = {
                "name_suffix": entry.voice_context_label,
                "context": entry.voice_context,
                "entries": [],
            }
            groups[key] = group
        group["entries"].append(entry)
    ordered = sorted(
        groups.values(),
        key=lambda item: (
            item["name_suffix"] is not None,
            item["name_suffix"] or "",
            [phrase for entry in item["entries"] for phrase in entry.spoken_forms],
        ),
    )
    return ordered



def render_dragonfly_module(
    project: Project,
    *,
    commands: list[DragonflyEntry],
    grammar_name: str | None = None,
    module_name: str | None = None,
) -> str:
    grammar = grammar_name or f"VHK {project.name}"
    module = module_name or default_dragonfly_module_name(project)
    command_map = {entry.command_id: list(entry.argv) for entry in commands}
    grammar_specs = []
    for group in _group_commands_by_context(commands):
        items = [
            {"phrase": phrase, "command_id": entry.command_id}
            for entry in group["entries"]
            for phrase in entry.spoken_forms
        ]
        name = grammar if not group["name_suffix"] else f"{grammar} [{group['name_suffix']}]"
        grammar_specs.append(
            {
                "name": name,
                "context": group["context"],
                "items": items,
            }
        )

    lines = [
        _module_header(grammar_name=grammar, project_name=project.name),
        "",
        "from __future__ import annotations",
        "",
        "import subprocess",
        "",
        "from dragonfly import AppContext, Function, Grammar, MappingRule",
        "",
        f"GRAMMAR_NAME = {grammar!r}",
        f"MODULE_NAME = {module!r}",
        f"PROJECT_NAME = {project.name!r}",
        f"COMMANDS = {json.dumps(command_map, ensure_ascii=False, indent=2)}",
        f"GRAMMAR_SPECS = {json.dumps(grammar_specs, ensure_ascii=False, indent=2)}",
        "",
        "",
        "def _run_vhk(command: list[str]) -> None:",
        "    subprocess.run(command, check=True)",
        "",
        "",
        "GRAMMARS: list[Grammar] = []",
        "",
        "",
        "def _build_mapping(items: list[dict[str, str]]) -> dict[str, Function]:",
        "    return {item['phrase']: Function(_run_vhk, command=COMMANDS[item['command_id']]) for item in items}",
        "",
        "",
        "for _index, _spec in enumerate(GRAMMAR_SPECS):",
        "    _context = AppContext(**_spec['context']) if _spec.get('context') else None",
        "    _grammar = Grammar(_spec['name'], context=_context)",
        "    _rule = type(f'VHKRule{_index}', (MappingRule,), {'mapping': _build_mapping(_spec['items'])})",
        "    _grammar.add_rule(_rule())",
        "    _grammar.load()",
        "    GRAMMARS.append(_grammar)",
        "",
        "",
        "def unload() -> None:",
        "    while GRAMMARS:",
        "        _grammar = GRAMMARS.pop()",
        "        _grammar.unload()",
        "",
    ]
    return "\n".join(lines)



def render_dragonfly_readme(
    project: Project,
    *,
    manifest: DragonflyPackManifest,
) -> str:
    rel_module = manifest.module_path.name
    rel_commands = manifest.commands_path.name
    lines = [
        f"# Dragonfly pack for {project.name}",
        "",
        "This pack is generated by `vhk gen-dragonfly-pack`.",
        "",
        "What this is:",
        "- a Dragonfly command module that says simple spoken phrases and calls `vhk run ...`",
        "- a JSON command ledger you can review or diff in Git",
        "",
        "What this is not:",
        "- a speech recognizer",
        "- a replacement execution engine for VHK",
        "",
        "Files:",
        f"- `{rel_module}` — Dragonfly command module (underscore-prefixed for module-loader friendly setups)",
        f"- `{rel_commands}` — reviewable command/phrase manifest",
        "",
        "Suggested workflow:",
        "1. Install/configure Dragonfly and a supported recognizer/backend for your environment.",
        f"2. Place `{rel_module}` in the directory your Dragonfly module loader scans.",
        "3. Reload the loader / recognizer, then try one of the spoken forms from the JSON ledger.",
        "",
        "Conservative defaults:",
        "- preset entries with interactive prompt overlays are skipped unless you regenerate with `--include-prompt-entries`",
        "- spoken forms are normalized to lowercase literal phrases",
        "- `voice_when` is only exported when it can be mapped honestly to Dragonfly window context fields",
        "- VHK remains the only automation runner; Dragonfly only launches it",
        "",
    ]
    if manifest.skipped:
        lines.append("Skipped entries:")
        for item in manifest.skipped:
            label = item.label
            reason = item.skip_reason or "skipped"
            lines.append(f"- `{label}` — {reason}")
        lines.append("")
    lines.append("Commands:")
    for item in manifest.commands:
        target = item.macro if item.preset is None else f"{item.macro} --preset {item.preset}"
        context_suffix = f" (context: {item.voice_context_label})" if item.voice_context_label else ""
        lines.append(f"- `{', '.join(item.spoken_forms)}` → `vhk run ... {target}`{context_suffix}")
    lines.append("")
    return "\n".join(lines)



def write_dragonfly_pack(
    project: Project,
    *,
    out_dir: Path,
    command: str = "vhk",
    grammar_name: str | None = None,
    module_name: str | None = None,
    include_hidden: bool = False,
    include_presets: bool = True,
    include_prompt_entries: bool = False,
) -> DragonflyPackManifest:
    commands, skipped = build_dragonfly_entries(
        project,
        command=command,
        include_hidden=include_hidden,
        include_presets=include_presets,
        include_prompt_entries=include_prompt_entries,
        backend="dragonfly",
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    resolved_module_name = module_name or default_dragonfly_module_name(project)
    module_path = out_dir / resolved_module_name
    commands_path = out_dir / "commands.json"
    readme_path = out_dir / "README.md"
    manifest = DragonflyPackManifest(
        project=project.name,
        grammar_name=grammar_name or f"VHK {project.name}",
        module_name=resolved_module_name,
        module_path=module_path,
        readme_path=readme_path,
        commands_path=commands_path,
        commands=tuple(commands),
        skipped=tuple(skipped),
    )
    module_path.write_text(
        render_dragonfly_module(project, commands=commands, grammar_name=manifest.grammar_name, module_name=manifest.module_name),
        encoding="utf-8",
    )
    commands_path.write_text(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    readme_path.write_text(render_dragonfly_readme(project, manifest=manifest), encoding="utf-8")
    return manifest
