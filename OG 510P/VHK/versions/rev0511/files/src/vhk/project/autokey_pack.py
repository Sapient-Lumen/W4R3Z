from __future__ import annotations

from dataclasses import dataclass, replace
import json
from pathlib import Path
import re
import shlex
from typing import Any, Literal

from vhk.core.models import I3WindowSelector, Project


_WORD_RE = re.compile(r"[^a-z0-9]+")
_AUTOKEY_SPECIAL_KEY_RE = re.compile(r"^f\d{1,2}$", re.IGNORECASE)


@dataclass(frozen=True)
class AutoKeyEntry:
    kind: Literal["hotstring", "binding"]
    macro: str
    preset: str | None
    label: str
    description: str | None
    trigger: str | None
    hotkey: str | None
    mode: str
    argv: tuple[str, ...]
    script_path: Path | None = None
    metadata_path: Path | None = None
    window_filter_regex: str | None = None
    window_filter_label: str | None = None
    approximate_window_filter: bool = False
    skipped: bool = False
    skip_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "macro": self.macro,
            "preset": self.preset,
            "label": self.label,
            "description": self.description,
            "trigger": self.trigger,
            "hotkey": self.hotkey,
            "mode": self.mode,
            "argv": list(self.argv),
            "script_path": str(self.script_path) if self.script_path else None,
            "metadata_path": str(self.metadata_path) if self.metadata_path else None,
            "window_filter_regex": self.window_filter_regex,
            "window_filter_label": self.window_filter_label,
            "approximate_window_filter": self.approximate_window_filter,
            "skipped": self.skipped,
            "skip_reason": self.skip_reason,
        }


@dataclass(frozen=True)
class AutoKeyPackManifest:
    project: str
    out_dir: Path
    data_dir: Path
    readme_path: Path
    manifest_path: Path
    entries: tuple[AutoKeyEntry, ...]
    skipped: tuple[AutoKeyEntry, ...]
    return_send_mode: str
    allow_window_filter_approximation: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "project": self.project,
            "out_dir": str(self.out_dir),
            "data_dir": str(self.data_dir),
            "readme_path": str(self.readme_path),
            "manifest_path": str(self.manifest_path),
            "return_send_mode": self.return_send_mode,
            "allow_window_filter_approximation": self.allow_window_filter_approximation,
            "approximate_window_filter_count": sum(1 for item in self.entries if item.approximate_window_filter),
            "entry_count": len(self.entries),
            "skipped_count": len(self.skipped),
            "entries": [item.to_dict() for item in self.entries],
            "skipped": [item.to_dict() for item in self.skipped],
        }


def _slugify(text: str) -> str:
    normalized = _WORD_RE.sub("-", str(text or "").strip().lower()).strip("-")
    return normalized or "item"


def _entry_label(kind: str, macro: str, *, trigger: str | None = None, hotkey: str | None = None) -> str:
    tail = trigger or hotkey or macro
    return f"{kind}:{macro}:{tail}"


def _entry_argv(project: Project, *, macro: str, vars_payload: dict[str, Any] | None = None, quiet: bool = True, print_return: bool = False, return_var: str = "return_value", command: str = "vhk") -> tuple[str, ...]:
    prefix = tuple(shlex.split(command)) or ("vhk",)
    argv = [*prefix, "run", project.root_dir, macro]
    if quiet:
        argv.append("--quiet")
    if vars_payload:
        argv.extend(["--vars", json.dumps(vars_payload, ensure_ascii=False)])
    if print_return:
        argv.extend(["--print-return", "--return-var", return_var])
    return tuple(argv)


def _selector_fields(selector: I3WindowSelector | None) -> dict[str, Any]:
    if selector is None:
        return {}
    return selector.model_dump(by_alias=True, exclude_none=True)


_AUTOKEY_WINDOW_FILTER_APPROXIMATION_REASON = (
    "AutoKey window filters match window title OR class with one regex; export requires approximation"
)


def _translate_window_filter(
    selector: I3WindowSelector | None,
    *,
    allow_approximation: bool = False,
) -> tuple[str | None, str | None, list[str], bool]:
    if selector is None:
        return None, None, [], False
    fields = _selector_fields(selector)
    if not fields:
        return None, None, [], False

    unsupported: list[str] = []
    if fields.get("app_id") is not None:
        unsupported.append("app_id")
    if fields.get("app_id_regex"):
        unsupported.append("app_id_regex")
    for key in fields:
        if key in {"class", "title", "title_regex", "app_id", "app_id_regex"}:
            continue
        unsupported.append(str(key))

    cls = fields.get("class")
    title = fields.get("title")
    title_regex = bool(fields.get("title_regex"))
    if cls is not None and title is not None:
        unsupported.append("class+title intersection")

    unsupported = sorted(set(unsupported))
    if unsupported:
        return None, None, unsupported, False

    if cls is not None:
        if not allow_approximation:
            return None, None, [f"{_AUTOKEY_WINDOW_FILTER_APPROXIMATION_REASON}: class={cls}"], False
        regex = re.escape(str(cls))
        return regex, f"class≈{cls}", [], True
    if title is not None:
        regex = str(title) if title_regex else re.escape(str(title))
        if title_regex:
            try:
                re.compile(regex)
            except re.error as exc:
                return None, None, [f"invalid title regex: {exc}"], False
        if not allow_approximation:
            label = f"title~={title}" if title_regex else f"title={title}"
            return None, None, [f"{_AUTOKEY_WINDOW_FILTER_APPROXIMATION_REASON}: {label}"], False
        label = f"title≈~={title}" if title_regex else f"title≈{title}"
        return regex, label, [], True
    return None, None, ["empty selector"], False


def _parse_hotkey(keys: str) -> tuple[list[str], str | None, list[str]]:
    parts = [p.strip() for p in str(keys or "").split("+") if p.strip()]
    if not parts:
        return [], None, ["empty binding"]
    raw_mods = [p.lower() for p in parts[:-1]]
    key_raw = parts[-1].strip()
    mod_map = {
        "ctrl": "<ctrl>",
        "control": "<ctrl>",
        "alt": "<alt>",
        "mod1": "<alt>",
        "shift": "<shift>",
        "super": "<super>",
        "meta": "<super>",
        "mod4": "<super>",
        "win": "<super>",
        "hyper": "<hyper>",
    }
    modifiers: list[str] = []
    unsupported: list[str] = []
    for raw in raw_mods:
        mapped = mod_map.get(raw)
        if mapped is None:
            unsupported.append(raw)
            continue
        if mapped not in modifiers:
            modifiers.append(mapped)

    key = key_raw.lower()
    if len(key) == 1:
        return modifiers, key, unsupported
    if _AUTOKEY_SPECIAL_KEY_RE.fullmatch(key):
        return modifiers, key, unsupported
    unsupported.append(f"key:{key_raw}")
    return modifiers, None, unsupported


def _autokey_send_mode_name(force_mode: str | None, default_send_mode: str) -> str:
    if force_mode == "keys":
        return "KEYBOARD"
    if force_mode == "clipboard":
        return default_send_mode
    return default_send_mode


def _render_script(entry: AutoKeyEntry, *, send_mode: str, get_output: bool) -> str:
    shell_command = " ".join(shlex.quote(item) for item in entry.argv)
    lines = [
        f"# Auto-generated by `vhk gen-autokey-pack` for {entry.label}",
        f"command = {shell_command!r}",
    ]
    if get_output:
        lines.extend(
            [
                "output = system.exec_command(command, getOutput=True)",
                "if output:",
                f"    keyboard.send_keys(output, send_mode=Keyboard.SendMode.{send_mode})",
            ]
        )
    else:
        lines.append("system.exec_command(command, getOutput=False)")
    return "\n".join(lines) + "\n"


def _script_metadata(entry: AutoKeyEntry, *, window_filter_regex: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "type": "script",
        "description": entry.label,
        "usageCount": 0,
        "showInTrayMenu": False,
    }
    if entry.kind == "hotstring":
        payload["modes"] = [1]
        payload["abbreviation"] = {
            "abbreviations": [entry.trigger],
            "backspace": True,
            "ignoreCase": False,
            "immediate": False,
            "triggerInside": False,
        }
    else:
        modifiers, hot_key, _ = _parse_hotkey(entry.hotkey or "")
        payload["modes"] = [2]
        payload["hotkey"] = {
            "modifiers": modifiers,
            "hotKey": hot_key,
        }
    if window_filter_regex:
        payload["windowInfoRegex"] = window_filter_regex
        payload["isRecursive"] = False
    return payload


def default_autokey_dir(project: Project) -> Path:
    return Path(project.root_dir) / "integrations" / "autokey"


def _entry_rel_dir(entry: AutoKeyEntry) -> str:
    return "hotstrings" if entry.kind == "hotstring" else "hotkeys"


def build_autokey_entries(
    project: Project,
    *,
    command: str = "vhk",
    include_disabled: bool = False,
    allow_window_filter_approximation: bool = False,
) -> tuple[list[AutoKeyEntry], list[AutoKeyEntry]]:
    entries: list[AutoKeyEntry] = []
    skipped: list[AutoKeyEntry] = []

    for hotstring in project.hotstrings:
        label = _entry_label("hotstring", hotstring.macro, trigger=hotstring.trigger)
        if (not hotstring.enabled) and (not include_disabled):
            skipped.append(
                AutoKeyEntry(
                    kind="hotstring",
                    macro=hotstring.macro,
                    preset=None,
                    label=label,
                    description=hotstring.description,
                    trigger=hotstring.trigger,
                    hotkey=None,
                    mode=hotstring.mode,
                    argv=(),
                    skipped=True,
                    skip_reason="hotstring disabled",
                )
            )
            continue
        regex, regex_label, unsupported, approximate_window_filter = _translate_window_filter(
            hotstring.when,
            allow_approximation=allow_window_filter_approximation,
        )
        if unsupported:
            skipped.append(
                AutoKeyEntry(
                    kind="hotstring",
                    macro=hotstring.macro,
                    preset=None,
                    label=label,
                    description=hotstring.description,
                    trigger=hotstring.trigger,
                    hotkey=None,
                    mode=hotstring.mode,
                    argv=(),
                    skipped=True,
                    skip_reason=f"AutoKey window filter cannot express selector fields honestly: {', '.join(unsupported)}",
                )
            )
            continue
        argv = _entry_argv(
            project,
            macro=hotstring.macro,
            vars_payload=dict(hotstring.vars or {}),
            command=command,
            print_return=hotstring.mode == "return",
            return_var=hotstring.return_var,
        )
        entries.append(
            AutoKeyEntry(
                kind="hotstring",
                macro=hotstring.macro,
                preset=None,
                label=label,
                description=hotstring.description,
                trigger=hotstring.trigger,
                hotkey=None,
                mode=hotstring.mode,
                argv=argv,
                window_filter_regex=regex,
                window_filter_label=regex_label,
                approximate_window_filter=approximate_window_filter,
            )
        )

    for binding in project.bindings:
        label = _entry_label("binding", binding.macro, hotkey=binding.keys)
        modifiers, key, unsupported_hotkey = _parse_hotkey(binding.keys)
        if unsupported_hotkey or key is None:
            reasons = ", ".join(sorted(set(unsupported_hotkey))) or "unknown"
            skipped.append(
                AutoKeyEntry(
                    kind="binding",
                    macro=binding.macro,
                    preset=None,
                    label=label,
                    description=binding.description,
                    trigger=None,
                    hotkey=binding.keys,
                    mode="side_effect",
                    argv=(),
                    skipped=True,
                    skip_reason=f"AutoKey hotkey export only supports simple keys/modifiers: {reasons}",
                )
            )
            continue
        regex, regex_label, unsupported, approximate_window_filter = _translate_window_filter(
            binding.when,
            allow_approximation=allow_window_filter_approximation,
        )
        if unsupported:
            skipped.append(
                AutoKeyEntry(
                    kind="binding",
                    macro=binding.macro,
                    preset=None,
                    label=label,
                    description=binding.description,
                    trigger=None,
                    hotkey=binding.keys,
                    mode="side_effect",
                    argv=(),
                    skipped=True,
                    skip_reason=f"AutoKey window filter cannot express selector fields honestly: {', '.join(unsupported)}",
                )
            )
            continue
        argv = _entry_argv(project, macro=binding.macro, vars_payload=dict(binding.vars or {}), command=command)
        entries.append(
            AutoKeyEntry(
                kind="binding",
                macro=binding.macro,
                preset=None,
                label=label,
                description=binding.description,
                trigger=None,
                hotkey=binding.keys,
                mode="side_effect",
                argv=argv,
                window_filter_regex=regex,
                window_filter_label=regex_label,
                approximate_window_filter=approximate_window_filter,
            )
        )

    entries.sort(key=lambda item: (item.kind, item.label))
    skipped.sort(key=lambda item: (item.kind, item.label))
    return entries, skipped


_RETURN_SEND_MODE_MAP = {
    "keyboard": "KEYBOARD",
    "ctrl-v": "CB_CTRL_V",
    "ctrl-shift-v": "CB_CTRL_SHIFT_V",
    "shift-insert": "CB_SHIFT_INSERT",
    "selection": "SELECTION",
}


def render_autokey_readme(project: Project, *, manifest: AutoKeyPackManifest) -> str:
    lines = [
        f"# AutoKey pack for {project.name}",
        "",
        "This pack is generated by `vhk gen-autokey-pack`.",
        "",
        "What this is:",
        "- a reviewable AutoKey/X11 adapter tree that calls back into `vhk run ...`",
        "- one script + sidecar metadata pair per exported VHK hotstring or binding",
        "- a conservative import folder under `data/` you can point AutoKey at and then restart AutoKey",
        "",
        "What this is not:",
        "- a claim that VHK has become AutoKey",
        "- a Wayland-global trigger layer",
        "- a promise that every VHK selector or hotkey shape maps cleanly to AutoKey",
        "",
        "Workflow:",
        f"1. Review `pack.json` and the generated files under `{manifest.data_dir.relative_to(manifest.out_dir)}`.",
        "2. In AutoKey, create/select a folder import target and point it at the generated `data/<project>/` tree.",
        "3. Restart AutoKey after importing or copying the files because AutoKey does not monitor its directories live.",
        "",
        "Conservative defaults:",
        "- only project hotstrings and bindings are exported",
        "- return-mode hotstrings call `vhk run --print-return` and then re-insert text through AutoKey's keyboard API",
        f"- default return send mode: `{manifest.return_send_mode}`",
        "- AutoKey window filters are one regex over window title OR class, so VHK treats selector export conservatively",
        "- by default scoped selectors are skipped rather than approximated",
        "- pass `--allow-window-filter-approximation` only when you accept that broadened AutoKey behavior",
        "- selectors that would widen scope even further (for example class+title intersections) are still skipped",
        "",
    ]
    if manifest.skipped:
        lines.append("Skipped entries:")
        for item in manifest.skipped:
            lines.append(f"- `{item.label}` — {item.skip_reason or 'skipped'}")
        lines.append("")
    lines.append("Included entries:")
    for item in manifest.entries:
        source = item.trigger or item.hotkey or item.macro
        context = f" (window filter: {item.window_filter_label})" if item.window_filter_label else ""
        if item.approximate_window_filter:
            context += " [approximate AutoKey title-or-class scope]"
        lines.append(f"- `{source}` → `{item.macro}`{context}")
    lines.append("")
    return "\n".join(lines)


def write_autokey_pack(
    project: Project,
    *,
    out_dir: Path,
    command: str = "vhk",
    include_disabled: bool = False,
    return_send_mode: str = "keyboard",
    allow_window_filter_approximation: bool = False,
) -> AutoKeyPackManifest:
    if return_send_mode not in _RETURN_SEND_MODE_MAP:
        raise ValueError(f"unsupported AutoKey return send mode: {return_send_mode}")
    entries, skipped = build_autokey_entries(
        project,
        command=command,
        include_disabled=include_disabled,
        allow_window_filter_approximation=allow_window_filter_approximation,
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    data_dir = out_dir / "data" / _slugify(project.name)
    data_dir.mkdir(parents=True, exist_ok=True)
    readme_path = out_dir / "README.md"
    manifest_path = out_dir / "pack.json"

    written: list[AutoKeyEntry] = []
    for entry in entries:
        rel_dir = data_dir / _entry_rel_dir(entry)
        rel_dir.mkdir(parents=True, exist_ok=True)
        base_name = _slugify(entry.trigger or entry.hotkey or entry.macro)
        script_path = rel_dir / f"{base_name}.py"
        metadata_path = rel_dir / f".{base_name}.json"
        send_mode_name = _autokey_send_mode_name(None, _RETURN_SEND_MODE_MAP[return_send_mode])
        if entry.kind == "hotstring":
            hotstring_force = next((hs.force_mode for hs in project.hotstrings if hs.macro == entry.macro and hs.trigger == entry.trigger), None)
            send_mode_name = _autokey_send_mode_name(hotstring_force, _RETURN_SEND_MODE_MAP[return_send_mode])
        script_path.write_text(
            _render_script(entry, send_mode=send_mode_name, get_output=entry.kind == "hotstring" and entry.mode == "return"),
            encoding="utf-8",
        )
        metadata = _script_metadata(entry, window_filter_regex=entry.window_filter_regex)
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written.append(replace(entry, script_path=script_path, metadata_path=metadata_path))

    manifest = AutoKeyPackManifest(
        project=project.name,
        out_dir=out_dir,
        data_dir=data_dir,
        readme_path=readme_path,
        manifest_path=manifest_path,
        entries=tuple(written),
        skipped=tuple(skipped),
        return_send_mode=return_send_mode,
        allow_window_filter_approximation=allow_window_filter_approximation,
    )
    readme_path.write_text(render_autokey_readme(project, manifest=manifest), encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest
