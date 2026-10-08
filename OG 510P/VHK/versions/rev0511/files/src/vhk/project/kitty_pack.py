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


def _slugify(text: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", str(text).strip()).strip("-").lower()
    return slug or "project"


@dataclass(frozen=True)
class KittyRoute:
    route_id: str
    macro: str
    description: str
    match_expr: str
    match_source: str
    selector_snapshot: dict[str, Any]
    text: str
    step_index: int
    helper_path: Path

    def to_dict(self) -> dict[str, object]:
        return {
            "route_id": self.route_id,
            "macro": self.macro,
            "description": self.description,
            "match_expr": self.match_expr,
            "match_source": self.match_source,
            "selector_snapshot": dict(self.selector_snapshot),
            "text": self.text,
            "step_index": self.step_index,
            "helper_path": str(self.helper_path),
        }


@dataclass(frozen=True)
class KittyPackManifest:
    project: str
    out_dir: Path
    routes: tuple[KittyRoute, ...]
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


def default_kitty_dir(project: Project) -> Path:
    return Path(project.root_dir) / "integrations" / "kitty"


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


def _is_kitty_selector(selector: Any) -> bool:
    return "kitty" in " ".join(_selector_texts(selector)).lower()


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


def _match_expr_from_selector(selector: Any) -> tuple[str | None, str]:
    if selector is None:
        return None, "missing_selector"
    title = getattr(selector, "title", None)
    title_regex = bool(getattr(selector, "title_regex", False))
    if str(title or "").strip():
        if title_regex:
            return f"title:{title}", "selector.title_regex"
        return f"title:^{re.escape(str(title))}$", "selector.title"
    return None, "missing_title"


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


def build_kitty_routes(project: Project, *, out_dir: Path) -> tuple[list[KittyRoute], list[dict[str, object]]]:
    helper_dir = Path(out_dir) / "bin"
    routes: list[KittyRoute] = []
    skipped: list[dict[str, object]] = []
    for macro_name, macro in getattr(project, "macros", {}).items():
        selectors = [(source, selector) for source, selector in _collect_macro_selectors(project, macro_name) if _is_kitty_selector(selector)]
        if not selectors:
            continue
        match_expr: str | None = None
        match_source = ""
        selector_snapshot: dict[str, Any] = {}
        selector_origin = ""
        for source, selector in selectors:
            candidate, why = _match_expr_from_selector(selector)
            if candidate:
                match_expr = candidate
                match_source = why
                selector_snapshot = _selector_snapshot(selector)
                selector_origin = source
                break
        text_steps = [
            (idx, step)
            for idx, step in enumerate(getattr(macro, "steps", []) or [])
            if getattr(step, "type", None) == "TypeText" and str(getattr(step, "text", "")) != ""
        ]
        if not text_steps:
            skipped.append(
                {
                    "macro": macro_name,
                    "reason": "no_type_text",
                    "detail": "kitty pack currently exports terminal text routes only from macros with TypeText steps.",
                }
            )
            continue
        if not match_expr:
            skipped.append(
                {
                    "macro": macro_name,
                    "reason": "missing_match_hint",
                    "detail": "kitty remote-control export currently needs an explicit title/title_regex selector so it can generate a reviewable --match expression.",
                    "selector_sources": [source for source, _selector in selectors],
                }
            )
            continue
        description = str(getattr(macro, "description", None) or getattr(macro, "name", None) or macro_name)
        for step_index, step in text_steps:
            route_id = _slugify(f"{macro_name}-kitty-text-{step_index + 1}")
            routes.append(
                KittyRoute(
                    route_id=route_id,
                    macro=macro_name,
                    description=description,
                    match_expr=str(match_expr),
                    match_source=f"{selector_origin}:{match_source}",
                    selector_snapshot=selector_snapshot,
                    text=str(getattr(step, "text", "")),
                    step_index=step_index,
                    helper_path=helper_dir / f"{route_id}.sh",
                )
            )
    return routes, skipped


def render_kitty_routes_yaml(project: Project, *, routes: list[KittyRoute], skipped: list[dict[str, object]]) -> str:
    payload = {
        "project": project.name,
        "generated_by": "vhk gen-kitty-pack",
        "notes": [
            "This pack is a thin kitty remote-control handoff for terminal-targeted text routes.",
            "External control needs kitty remote control enabled via allow_remote_control or a remote_control_password, and often a socket/listen-on path when used from outside kitty.",
        ],
        "routes": [
            {
                "id": route.route_id,
                "macro": route.macro,
                "description": route.description,
                "selector": route.selector_snapshot,
                "kitty": {
                    "match": route.match_expr,
                    "match_source": route.match_source,
                    "send_text_example": f"kitten @ send-text --match {shlex.quote(route.match_expr)} --stdin",
                },
                "text": {"step_index": route.step_index, "literal": route.text},
                "helper_script": str(route.helper_path),
            }
            for route in routes
        ],
        "skipped": skipped,
    }
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)


def render_kitty_commands_json(project: Project, *, routes: list[KittyRoute], skipped: list[dict[str, object]]) -> str:
    payload = {
        "project": project.name,
        "route_count": len(routes),
        "routes": [
            {**route.to_dict(), "send_text_command": f"kitten @ send-text --match {shlex.quote(route.match_expr)} --stdin"}
            for route in routes
        ],
        "skipped": skipped,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def render_kitty_helper_script(project: Project, *, route: KittyRoute) -> str:
    marker = f"__VHK_KITTY_TEXT_{route.route_id.upper().replace('-', '_')}__"
    return dedent(
        f'''\
        #!/usr/bin/env bash
        set -euo pipefail

        # Generated by `vhk gen-kitty-pack` for project: {project.name}
        # Route id: {route.route_id}

        KITTEN=${{KITTEN:-kitten}}
        KITTY_TO=${{KITTY_TO:-}}
        KITTY_MATCH=${{KITTY_MATCH:-{route.match_expr}}}

        DEFAULT_TEXT=$(cat <<'{marker}'
        {route.text}
        {marker}
        )

        if [[ -n "${{KITTY_TEXT:-}}" ]]; then
          TEXT=$KITTY_TEXT
        elif [[ ! -t 0 ]]; then
          TEXT=$(cat)
        else
          TEXT=$DEFAULT_TEXT
        fi

        cmd=("$KITTEN" @)
        if [[ -n "$KITTY_TO" ]]; then
          cmd+=(--to "$KITTY_TO")
        fi
        cmd+=(send-text --match "$KITTY_MATCH" --stdin)
        printf '%s' "$TEXT" | "${{cmd[@]}}"
        '''
    )


def render_kitty_readme(project: Project, *, manifest: KittyPackManifest) -> str:
    lines = [
        f"# {project.name} kitty remote-control pack",
        "",
        "Generated by `vhk gen-kitty-pack`.",
        "",
        "This pack turns the app-native kitty lane into a concrete, reviewable handoff for terminal text routes.",
        "",
        "## What it writes",
        "",
        "- `vhk.kitty.routes.yml` — route catalog with selector evidence, generated `--match` expressions, and literal text payloads",
        "- `vhk.kitty.commands.json` — machine-readable command ledger and skipped-route list",
        "- `bin/*.sh` — thin helper wrappers around `kitten @ send-text --match ... --stdin`",
        "",
        "## Assumptions and limits",
        "",
        "- This exporter only handles kitty-targeted macros with `TypeText` steps.",
        "- It currently needs an explicit selector title/title_regex so the exported `--match` stays reviewable. Class/app_id-only selectors are recorded as skipped until VHK grows a richer kitty inspector/match builder.",
        "- External use usually needs kitty remote control enabled with `allow_remote_control` or `remote_control_password`. When controlling kitty from outside the instance, set `KITTY_TO` to a socket target that matches kitty's `--listen-on` configuration.",
        "",
        "## Routes",
        "",
    ]
    if not manifest.routes:
        lines.extend(
            [
                "No kitty-targeted `TypeText` routes were exported.",
                "",
                "Add a terminal-targeted macro with an explicit kitty window title selector and regenerate the pack.",
            ]
        )
    else:
        for route in manifest.routes:
            lines.extend(
                [
                    f"### `{route.route_id}`",
                    "",
                    f"- macro: `{route.macro}`",
                    f"- match: `{route.match_expr}`",
                    f"- selector source: `{route.match_source}`",
                    f"- helper: `{route.helper_path.name}`",
                    "",
                ]
            )
    if manifest.skipped:
        lines.extend(["## Skipped", ""])
        for item in manifest.skipped:
            lines.append(f"- `{item.get('macro')}` — {item.get('reason')}: {item.get('detail')}")
        lines.append("")
    return "\n".join(lines) + "\n"


def write_kitty_pack(project: Project, *, out_dir: Path) -> KittyPackManifest:
    target_dir = Path(out_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    helper_dir = target_dir / "bin"
    helper_dir.mkdir(parents=True, exist_ok=True)

    routes, skipped = build_kitty_routes(project, out_dir=target_dir)
    routes_path = target_dir / "vhk.kitty.routes.yml"
    commands_path = target_dir / "vhk.kitty.commands.json"
    readme_path = target_dir / "README.md"

    for route in routes:
        route.helper_path.write_text(render_kitty_helper_script(project, route=route), encoding="utf-8")
        route.helper_path.chmod(route.helper_path.stat().st_mode | 0o111)

    manifest = KittyPackManifest(
        project=project.name,
        out_dir=target_dir,
        routes=tuple(routes),
        skipped=tuple(skipped),
        routes_path=routes_path,
        commands_path=commands_path,
        readme_path=readme_path,
        helper_paths=tuple(route.helper_path for route in routes),
    )
    routes_path.write_text(render_kitty_routes_yaml(project, routes=routes, skipped=skipped), encoding="utf-8")
    commands_path.write_text(render_kitty_commands_json(project, routes=routes, skipped=skipped), encoding="utf-8")
    readme_path.write_text(render_kitty_readme(project, manifest=manifest), encoding="utf-8")
    return manifest
