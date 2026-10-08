from __future__ import annotations

import json
import re
import shlex
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import Any

import yaml

from vhk.core.models import Project


_MPV_ACTIONS: tuple[dict[str, Any], ...] = (
    {
        "id": "toggle-pause",
        "summary": "cycle pause",
        "command": ["cycle", "pause"],
        "key_hints": {"XF86AudioPlay"},
        "token_groups": (("pause",), ("play",), ("toggle", "pause")),
    },
    {
        "id": "stop",
        "summary": "stop",
        "command": ["stop"],
        "key_hints": {"XF86AudioStop"},
        "token_groups": (("stop",),),
    },
    {
        "id": "playlist-next",
        "summary": "playlist-next force",
        "command": ["playlist-next", "force"],
        "key_hints": {"XF86AudioNext"},
        "token_groups": (("next",), ("skip",), ("playlist", "next")),
    },
    {
        "id": "playlist-prev",
        "summary": "playlist-prev force",
        "command": ["playlist-prev", "force"],
        "key_hints": {"XF86AudioPrev"},
        "token_groups": (("prev",), ("previous",), ("playlist", "prev"), ("playlist", "previous")),
    },
    {
        "id": "seek-forward",
        "summary": "seek 5",
        "command": ["seek", 5],
        "key_hints": set(),
        "token_groups": (("seek", "forward"), ("seek", "ahead"), ("seek", "next"), ("seek", "skip"), ("forward",)),
    },
    {
        "id": "seek-backward",
        "summary": "seek -5",
        "command": ["seek", -5],
        "key_hints": set(),
        "token_groups": (("seek", "back"), ("seek", "backward"), ("seek", "rewind"), ("rewind",), ("backward",)),
    },
    {
        "id": "toggle-mute",
        "summary": "cycle mute",
        "command": ["cycle", "mute"],
        "key_hints": {"XF86AudioMute"},
        "token_groups": (("mute",),),
    },
    {
        "id": "volume-up",
        "summary": "add volume 5",
        "command": ["add", "volume", 5],
        "key_hints": {"XF86AudioRaiseVolume"},
        "token_groups": (("volume", "up"), ("volume", "raise"), ("volume", "increase"), ("louder",), ("raise", "volume")),
    },
    {
        "id": "volume-down",
        "summary": "add volume -5",
        "command": ["add", "volume", -5],
        "key_hints": {"XF86AudioLowerVolume"},
        "token_groups": (("volume", "down"), ("volume", "lower"), ("volume", "decrease"), ("quieter",), ("lower", "volume")),
    },
    {
        "id": "toggle-fullscreen",
        "summary": "cycle fullscreen",
        "command": ["cycle", "fullscreen"],
        "key_hints": set(),
        "token_groups": (("fullscreen",),),
    },
)


def _slugify(text: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", str(text).strip()).strip("-").lower()
    return slug or "project"


@dataclass(frozen=True)
class MpvRoute:
    route_id: str
    macro: str
    description: str
    selector_source: str
    selector_snapshot: dict[str, Any]
    binding_keys: tuple[str, ...]
    action_id: str
    action_summary: str
    action_source: str
    command: tuple[Any, ...]
    helper_path: Path

    def to_dict(self) -> dict[str, object]:
        return {
            "route_id": self.route_id,
            "macro": self.macro,
            "description": self.description,
            "selector_source": self.selector_source,
            "selector_snapshot": dict(self.selector_snapshot),
            "binding_keys": list(self.binding_keys),
            "action_id": self.action_id,
            "action_summary": self.action_summary,
            "action_source": self.action_source,
            "command": list(self.command),
            "helper_path": str(self.helper_path),
        }


@dataclass(frozen=True)
class MpvPackManifest:
    project: str
    out_dir: Path
    routes: tuple[MpvRoute, ...]
    skipped: tuple[dict[str, object], ...]
    routes_path: Path
    commands_path: Path
    readme_path: Path
    helper_paths: tuple[Path, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "project": self.project,
            "out_dir": str(self.out_dir),
            "route_count": len(self.routes),
            "routes": [route.to_dict() for route in self.routes],
            "skipped": [dict(item) for item in self.skipped],
            "routes_path": str(self.routes_path),
            "commands_path": str(self.commands_path),
            "readme_path": str(self.readme_path),
            "helper_paths": [str(path) for path in self.helper_paths],
        }


def default_mpv_dir(project: Project) -> Path:
    return Path(project.root_dir) / "integrations" / "mpv"


def _selector_texts(selector: Any) -> list[str]:
    if selector is None:
        return []
    values = [
        getattr(selector, "app_id", None),
        getattr(selector, "wm_class", None),
        getattr(selector, "instance", None),
        getattr(selector, "title", None),
        getattr(selector, "window_role", None),
    ]
    return [str(value).strip() for value in values if str(value or "").strip()]


def _is_mpv_selector(selector: Any) -> bool:
    return "mpv" in " ".join(_selector_texts(selector)).lower()


def _selector_snapshot(selector: Any) -> dict[str, Any]:
    if selector is None:
        return {}
    if hasattr(selector, "model_dump"):
        try:
            return dict(selector.model_dump(by_alias=True, exclude_none=True))
        except TypeError:
            return dict(selector.model_dump(exclude_none=True))
    if isinstance(selector, dict):
        return {str(k): v for k, v in selector.items() if v is not None}
    return {}


def _collect_macro_selectors(project: Project, macro_name: str) -> list[tuple[str, Any]]:
    macro = getattr(project, "macros", {}).get(macro_name)
    selectors: list[tuple[str, Any]] = []
    if macro is None:
        return selectors
    voice_when = getattr(macro, "voice_when", None)
    if voice_when is not None:
        selectors.append((f"macro:{macro_name}.voice_when", voice_when))
    for idx, step in enumerate(getattr(macro, "steps", []) or []):
        if getattr(step, "type", None) in {"WaitForWindow", "FocusWindow", "WaitForWindowVanish", "WaitForWindowEvent"}:
            selector = getattr(step, "selector", None)
            if selector is not None:
                selectors.append((f"macro:{macro_name}.steps[{idx}]", selector))
    for idx, binding in enumerate(getattr(project, "bindings", []) or []):
        if str(getattr(binding, "macro", "")).strip() != macro_name:
            continue
        selector = getattr(binding, "when", None)
        if selector is not None:
            selectors.append((f"binding:{idx}.when", selector))
    return selectors


def _collect_binding_keys(project: Project, macro_name: str) -> list[str]:
    keys: list[str] = []
    for binding in getattr(project, "bindings", []) or []:
        if str(getattr(binding, "macro", "")).strip() != macro_name:
            continue
        value = str(getattr(binding, "keys", "") or "").strip()
        if value:
            keys.append(value)
    return keys


def _hint_tokens(*values: str) -> set[str]:
    tokens: set[str] = set()
    for value in values:
        for token in re.findall(r"[A-Za-z0-9]+", str(value or "").lower()):
            if token:
                tokens.add(token)
    return tokens


def _infer_mpv_action(*, macro_name: str, description: str, binding_keys: list[str]) -> tuple[str, str, tuple[Any, ...], str] | None:
    tokens = _hint_tokens(macro_name, description, *binding_keys)
    key_values = {str(item).strip() for item in binding_keys if str(item).strip()}
    for spec in _MPV_ACTIONS:
        key_hints = {str(item) for item in (spec.get("key_hints") or set())}
        if key_values & key_hints:
            match = sorted(key_values & key_hints)[0]
            return (
                str(spec["id"]),
                str(spec["summary"]),
                tuple(spec["command"]),
                f"binding_key:{match}",
            )
        for group in spec.get("token_groups") or ():
            group_tokens = tuple(str(x) for x in group if str(x))
            if not group_tokens:
                continue
            if all(token in tokens for token in group_tokens):
                return (
                    str(spec["id"]),
                    str(spec["summary"]),
                    tuple(spec["command"]),
                    f"hint_tokens:{'+'.join(group_tokens)}",
                )
    return None


def build_mpv_routes(project: Project, *, out_dir: Path) -> tuple[list[MpvRoute], list[dict[str, object]]]:
    helper_dir = Path(out_dir) / "bin"
    routes: list[MpvRoute] = []
    skipped: list[dict[str, object]] = []
    for macro_name, macro in getattr(project, "macros", {}).items():
        selectors = [(source, selector) for source, selector in _collect_macro_selectors(project, macro_name) if _is_mpv_selector(selector)]
        if not selectors:
            continue
        selector_source, selector = selectors[0]
        selector_snapshot = _selector_snapshot(selector)
        binding_keys = _collect_binding_keys(project, macro_name)
        description = str(getattr(macro, "description", None) or getattr(macro, "name", None) or macro_name)
        action = _infer_mpv_action(macro_name=macro_name, description=description, binding_keys=binding_keys)
        if action is None:
            skipped.append(
                {
                    "macro": macro_name,
                    "reason": "no_command_hint",
                    "detail": "mpv pack currently exports macros only when their name/description/binding keys imply a reviewable JSON IPC command such as pause, stop, next, previous, volume, seek, mute, or fullscreen.",
                    "selector_source": selector_source,
                    "binding_keys": binding_keys,
                }
            )
            continue
        action_id, action_summary, command, action_source = action
        route_id = _slugify(f"{macro_name}-mpv-{action_id}")
        routes.append(
            MpvRoute(
                route_id=route_id,
                macro=macro_name,
                description=description,
                selector_source=selector_source,
                selector_snapshot=selector_snapshot,
                binding_keys=tuple(binding_keys),
                action_id=action_id,
                action_summary=action_summary,
                action_source=action_source,
                command=command,
                helper_path=helper_dir / f"{route_id}.sh",
            )
        )
    return routes, skipped


def render_mpv_routes_yaml(project: Project, *, routes: list[MpvRoute], skipped: list[dict[str, object]]) -> str:
    payload = {
        "project": project.name,
        "generated_by": "vhk gen-mpv-pack",
        "notes": [
            "This pack is a thin mpv JSON IPC handoff for mpv-targeted macros.",
            "mpv must be started with --input-ipc-server=<socket>, and the generated helpers default to ${XDG_RUNTIME_DIR:-/tmp}/mpv.socket unless MPV_SOCKET is overridden.",
        ],
        "routes": [
            {
                "id": route.route_id,
                "macro": route.macro,
                "description": route.description,
                "selector": route.selector_snapshot,
                "bindings": list(route.binding_keys),
                "mpv": {
                    "action_id": route.action_id,
                    "action_summary": route.action_summary,
                    "action_source": route.action_source,
                    "json_command": {"command": list(route.command)},
                    "ipc_example": "printf '%s\\n' '<JSON>' | socat - \"$MPV_SOCKET\"",
                    "socket_default": "${XDG_RUNTIME_DIR:-/tmp}/mpv.socket",
                },
                "helper_script": str(route.helper_path),
            }
            for route in routes
        ],
        "skipped": skipped,
    }
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)


def render_mpv_commands_json(project: Project, *, routes: list[MpvRoute], skipped: list[dict[str, object]]) -> str:
    payload = {
        "project": project.name,
        "route_count": len(routes),
        "routes": [
            {
                **route.to_dict(),
                "json_command": {"command": list(route.command)},
                "socat_command": f"printf '%s\\n' {shlex.quote(json.dumps({'command': list(route.command)}, ensure_ascii=False))} | socat - \"$MPV_SOCKET\"",
            }
            for route in routes
        ],
        "skipped": skipped,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def render_mpv_helper_script(project: Project, *, route: MpvRoute) -> str:
    default_json = json.dumps({"command": list(route.command)}, ensure_ascii=False)
    return dedent(
        f'''\
        #!/usr/bin/env bash
        set -euo pipefail

        # Generated by `vhk gen-mpv-pack` for project: {project.name}
        # Route id: {route.route_id}

        MPV_SOCKET=${{MPV_SOCKET:-${{XDG_RUNTIME_DIR:-/tmp}}/mpv.socket}}
        MPV_JSON=${{MPV_JSON:-{default_json!r}}}

        if command -v socat >/dev/null 2>&1; then
          printf '%s\n' "$MPV_JSON" | socat - "$MPV_SOCKET"
        elif command -v nc >/dev/null 2>&1; then
          printf '%s\n' "$MPV_JSON" | nc -U "$MPV_SOCKET"
        else
          echo "error: install socat or netcat with unix-socket (-U) support" >&2
          exit 1
        fi
        '''
    )


def render_mpv_readme(project: Project, *, manifest: MpvPackManifest) -> str:
    lines = [
        f"# {project.name} mpv JSON IPC pack",
        "",
        "Generated by `vhk gen-mpv-pack`.",
        "",
        "This pack turns the mpv app-native lane into a reviewable IPC handoff instead of relying on focus-sensitive key replay.",
        "",
        "## What it writes",
        "",
        "- `vhk.mpv.routes.yml` — route catalog with selector evidence, inferred IPC actions, and helper paths",
        "- `vhk.mpv.commands.json` — machine-readable command ledger and skipped-route list",
        "- `bin/*.sh` — thin helper wrappers that send JSON IPC commands over `socat`/`nc -U`",
        "",
        "## Assumptions and limits",
        "",
        "- mpv must expose a local IPC socket via `--input-ipc-server=<socket>`.",
        "- The generated helpers default to `${XDG_RUNTIME_DIR:-/tmp}/mpv.socket`; override `MPV_SOCKET` if your player uses a different path.",
        "- This exporter is intentionally conservative: it only emits routes when names, descriptions, or binding keys imply a reviewable command such as pause, stop, next, previous, seek, volume, mute, or fullscreen.",
        "",
        "## Routes",
        "",
    ]
    if not manifest.routes:
        lines.extend([
            "No mpv-targeted routes were exported.",
            "",
            "Add one or more mpv-scoped macros with reviewable action hints and regenerate the pack.",
        ])
    else:
        for route in manifest.routes:
            lines.extend([
                f"### `{route.route_id}`",
                "",
                f"- macro: `{route.macro}`",
                f"- action: `{route.action_summary}` ({route.action_source})",
                f"- helper: `{route.helper_path.name}`",
                f"- selector source: `{route.selector_source}`",
                "",
            ])
    if manifest.skipped:
        lines.extend(["## Skipped", ""])
        for item in manifest.skipped:
            lines.append(f"- `{item.get('macro')}` — {item.get('reason')}: {item.get('detail')}")
        lines.append("")
    return "\n".join(lines) + "\n"


def write_mpv_pack(project: Project, *, out_dir: Path) -> MpvPackManifest:
    target_dir = Path(out_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    helper_dir = target_dir / "bin"
    helper_dir.mkdir(parents=True, exist_ok=True)

    routes, skipped = build_mpv_routes(project, out_dir=target_dir)
    routes_path = target_dir / "vhk.mpv.routes.yml"
    commands_path = target_dir / "vhk.mpv.commands.json"
    readme_path = target_dir / "README.md"

    for route in routes:
        route.helper_path.write_text(render_mpv_helper_script(project, route=route), encoding="utf-8")
        route.helper_path.chmod(route.helper_path.stat().st_mode | 0o111)

    manifest = MpvPackManifest(
        project=project.name,
        out_dir=target_dir,
        routes=tuple(routes),
        skipped=tuple(skipped),
        routes_path=routes_path,
        commands_path=commands_path,
        readme_path=readme_path,
        helper_paths=tuple(route.helper_path for route in routes),
    )
    routes_path.write_text(render_mpv_routes_yaml(project, routes=routes, skipped=skipped), encoding="utf-8")
    commands_path.write_text(render_mpv_commands_json(project, routes=routes, skipped=skipped), encoding="utf-8")
    readme_path.write_text(render_mpv_readme(project, manifest=manifest), encoding="utf-8")
    return manifest
