from __future__ import annotations

import json
import re
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from vhk.core.models import Project


def _slugify(text: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", str(text).strip()).strip("-").lower()
    return slug or "project"


@dataclass(frozen=True)
class WezTermRoute:
    route_id: str
    macro: str
    description: str
    title_pattern: str
    title_match_mode: str
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
            "title_pattern": self.title_pattern,
            "title_match_mode": self.title_match_mode,
            "match_source": self.match_source,
            "selector_snapshot": dict(self.selector_snapshot),
            "text": self.text,
            "step_index": self.step_index,
            "helper_path": str(self.helper_path),
        }


@dataclass(frozen=True)
class WezTermPackManifest:
    project: str
    out_dir: Path
    routes: tuple[WezTermRoute, ...]
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


def default_wezterm_dir(project: Project) -> Path:
    return Path(project.root_dir) / "integrations" / "wezterm"


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


def _is_wezterm_selector(selector: Any) -> bool:
    text = " ".join(_selector_texts(selector)).lower()
    return "wezterm" in text or "org.wezfurlong.wezterm" in text


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


def _title_pattern_from_selector(selector: Any) -> tuple[str | None, str, str]:
    if selector is None:
        return None, "none", "missing_selector"
    title = getattr(selector, "title", None)
    title_regex = bool(getattr(selector, "title_regex", False))
    if str(title or "").strip():
        if title_regex:
            return str(title), "regex", "selector.title_regex"
        return str(title), "exact", "selector.title"
    return None, "none", "missing_title"


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


def build_wezterm_routes(project: Project, *, out_dir: Path) -> tuple[list[WezTermRoute], list[dict[str, object]]]:
    helper_dir = Path(out_dir) / "bin"
    routes: list[WezTermRoute] = []
    skipped: list[dict[str, object]] = []

    for macro_name, macro in getattr(project, "macros", {}).items():
        selectors = [(source, selector) for source, selector in _collect_macro_selectors(project, macro_name) if _is_wezterm_selector(selector)]
        if not selectors:
            continue

        title_pattern: str | None = None
        title_match_mode = "none"
        match_source = ""
        selector_snapshot: dict[str, Any] = {}
        selector_origin = ""
        for source, selector in selectors:
            candidate, candidate_mode, why = _title_pattern_from_selector(selector)
            if candidate:
                title_pattern = candidate
                title_match_mode = candidate_mode
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
                    "detail": "wezterm pack currently exports pane text routes only from macros with TypeText steps.",
                }
            )
            continue
        if not title_pattern:
            skipped.append(
                {
                    "macro": macro_name,
                    "reason": "missing_pane_hint",
                    "detail": "wezterm CLI export currently needs an explicit title/title_regex selector so it can generate a reviewable pane-discovery rule from `wezterm cli list --format json`.",
                    "selector_sources": [source for source, _selector in selectors],
                }
            )
            continue

        description = str(getattr(macro, "description", None) or getattr(macro, "name", None) or macro_name)
        for step_index, step in text_steps:
            route_id = _slugify(f"{macro_name}-wezterm-text-{step_index + 1}")
            routes.append(
                WezTermRoute(
                    route_id=route_id,
                    macro=macro_name,
                    description=description,
                    title_pattern=str(title_pattern),
                    title_match_mode=title_match_mode,
                    match_source=f"{selector_origin}:{match_source}",
                    selector_snapshot=selector_snapshot,
                    text=str(getattr(step, "text", "")),
                    step_index=step_index,
                    helper_path=helper_dir / f"{route_id}.sh",
                )
            )
    return routes, skipped


def render_wezterm_routes_yaml(project: Project, *, routes: list[WezTermRoute], skipped: list[dict[str, object]]) -> str:
    payload = {
        "project": project.name,
        "generated_by": "vhk gen-wezterm-pack",
        "notes": [
            "This pack is a thin WezTerm CLI handoff for terminal-targeted text routes.",
            "Review pane targeting carefully: explicit pane ids are strongest, while title-based resolution via `wezterm cli list --format json` is a best-effort fallback.",
            "`wezterm cli send-text` sends text paste-style by default; use `--no-paste` only when the direct-input path is deliberate.",
        ],
        "routes": [
            {
                "id": route.route_id,
                "macro": route.macro,
                "description": route.description,
                "selector": route.selector_snapshot,
                "wezterm": {
                    "title_pattern": route.title_pattern,
                    "title_match_mode": route.title_match_mode,
                    "match_source": route.match_source,
                    "list_example": "wezterm cli list --format json",
                    "send_text_example": (
                        "wezterm cli send-text "
                        f"--pane-id <pane-id> {shlex.quote(route.text)}"
                    ),
                    "get_text_example": "wezterm cli get-text --pane-id <pane-id>",
                },
                "text": {"step_index": route.step_index, "literal": route.text},
                "helper_script": str(route.helper_path),
            }
            for route in routes
        ],
        "skipped": skipped,
    }
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)


def render_wezterm_commands_json(project: Project, *, routes: list[WezTermRoute], skipped: list[dict[str, object]]) -> str:
    payload = {
        "project": project.name,
        "route_count": len(routes),
        "routes": [
            {
                **route.to_dict(),
                "list_command": "wezterm cli list --format json",
                "send_text_command": f"wezterm cli send-text --pane-id <pane-id> {shlex.quote(route.text)}",
                "get_text_command": "wezterm cli get-text --pane-id <pane-id>",
            }
            for route in routes
        ],
        "skipped": skipped,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def render_wezterm_helper_script(project: Project, *, route: WezTermRoute) -> str:
    default_text = shlex.quote(route.text)
    return f"""#!/usr/bin/env bash
set -euo pipefail

# Generated by `vhk gen-wezterm-pack` for project: {project.name}
# Route id: {route.route_id}
# This stays intentionally thin: WezTerm owns pane targeting and transport,
# while VHK still owns the reviewed macro semantics and route catalog.

WEZTERM=${{WEZTERM:-wezterm}}
WEZTERM_PANE_ID=${{WEZTERM_PANE_ID:-${{WEZTERM_PANE:-}}}}
WEZTERM_MATCH_TITLE=${{WEZTERM_MATCH_TITLE:-{route.title_pattern}}}
WEZTERM_MATCH_MODE=${{WEZTERM_MATCH_MODE:-{route.title_match_mode}}}
WEZTERM_TEXT=${{WEZTERM_TEXT:-{default_text}}}
WEZTERM_CAPTURE_FILE=${{WEZTERM_CAPTURE_FILE:-}}
WEZTERM_SEND_MODE=${{WEZTERM_SEND_MODE:-paste}}

if [[ -z "$WEZTERM_PANE_ID" ]]; then
  WEZTERM_LIST_JSON=$("$WEZTERM" cli list --format json)
  WEZTERM_PANE_ID=$(WEZTERM_LIST_JSON="$WEZTERM_LIST_JSON" python3 - "$WEZTERM_MATCH_TITLE" "$WEZTERM_MATCH_MODE" <<'PYJSON'
import json
import os
import re
import sys

pattern = sys.argv[1]
mode = sys.argv[2]
try:
    rows = json.loads(os.environ.get("WEZTERM_LIST_JSON") or "[]")
except json.JSONDecodeError:
    sys.exit(3)

matches = []
for row in rows:
    title = str(row.get("title") or "")
    pane_id = row.get("pane_id")
    if pane_id is None:
        continue
    if mode == "regex":
        try:
            ok = re.search(pattern, title) is not None
        except re.error:
            sys.exit(4)
    else:
        ok = title == pattern
    if ok:
        matches.append(str(pane_id))

if len(matches) != 1:
    sys.exit(5)
print(matches[0])
PYJSON
  ) || {{
    printf 'Unable to resolve a unique WezTerm pane id for pattern %s (%s).\n' "$WEZTERM_MATCH_TITLE" "$WEZTERM_MATCH_MODE" >&2
    printf 'Set WEZTERM_PANE_ID explicitly or refine the selector title evidence.\n' >&2
    exit 1
  }}
fi

args=(cli send-text --pane-id "$WEZTERM_PANE_ID")
if [[ "$WEZTERM_SEND_MODE" == "direct" ]]; then
  args+=(--no-paste)
fi
printf '%s' "$WEZTERM_TEXT" | "$WEZTERM" "${{args[@]}}"

if [[ -n "$WEZTERM_CAPTURE_FILE" ]]; then
  "$WEZTERM" cli get-text --pane-id "$WEZTERM_PANE_ID" > "$WEZTERM_CAPTURE_FILE"
fi
"""


def render_wezterm_readme(project: Project, *, manifest: WezTermPackManifest) -> str:
    lines = [
        f"# {project.name} WezTerm CLI pack",
        "",
        "Generated by `vhk gen-wezterm-pack`.",
        "",
        "This pack makes the WezTerm app-native lane concrete without turning VHK into a terminal multiplexer.",
        "The generated files keep one reviewable route catalog:",
        "",
        "- `vhk.wezterm.routes.yml` — route-by-route mapping from VHK selectors to WezTerm pane targeting hints",
        "- `vhk.wezterm.commands.json` — machine-readable command examples and helper paths",
        "- `bin/*.sh` — thin helper wrappers that resolve a pane id and call `wezterm cli send-text`, with optional `wezterm cli get-text` capture",
        "",
        "## Why this exists",
        "",
        "WezTerm already exposes a CLI for pane-oriented text send and capture. This pack keeps that seam reviewable instead of replaying text through generic desktop typing.",
        "",
        "## Targeting policy",
        "",
        "- explicit `WEZTERM_PANE_ID` is strongest",
        "- `WEZTERM_PANE` from inside a pane is acceptable for current-pane helpers",
        "- title/title_regex selector evidence can drive a best-effort `wezterm cli list --format json` lookup when no pane id is available yet",
        "- ambiguous title matches should fail loudly rather than guessing",
        "",
        "## Routes",
        "",
    ]
    if not manifest.routes:
        lines.extend([
            "No WezTerm-shaped `TypeText` routes with reviewable pane hints were found in this project.",
            "",
            "Create one or more `TypeText` macros with WezTerm selectors that include `title` or `title_regex`, then regenerate the pack.",
        ])
        return "\n".join(lines) + "\n"

    for item in manifest.routes:
        lines.extend([
            f"### `{item.route_id}`",
            "",
            f"- macro: `{item.macro}`",
            f"- title pattern: `{item.title_pattern}` ({item.title_match_mode})",
            f"- helper: `{item.helper_path.name}`",
            f"- text preview: `{item.text}`",
            "",
        ])

    if manifest.skipped:
        lines.extend([
            "## Skipped",
            "",
        ])
        for item in manifest.skipped:
            lines.append(f"- `{item.get('macro')}` — {item.get('reason')}: {item.get('detail')}")
        lines.append("")

    lines.extend([
        "## Notes",
        "",
        "- WezTerm CLI targeting is pane-oriented, so the main remaining gap is better pane identity capture in future inspector flows.",
        "- Keep kitty remote control, WezTerm CLI, and generic desktop typing as separate reviewed lanes; they solve different problems.",
    ])
    return "\n".join(lines) + "\n"


def write_wezterm_pack(project: Project, *, out_dir: Path) -> WezTermPackManifest:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    helper_dir = out_dir / "bin"
    helper_dir.mkdir(parents=True, exist_ok=True)

    routes, skipped = build_wezterm_routes(project, out_dir=out_dir)
    routes_path = out_dir / "vhk.wezterm.routes.yml"
    commands_path = out_dir / "vhk.wezterm.commands.json"
    readme_path = out_dir / "README.md"

    routes_path.write_text(render_wezterm_routes_yaml(project, routes=routes, skipped=skipped), encoding="utf-8")
    commands_path.write_text(render_wezterm_commands_json(project, routes=routes, skipped=skipped), encoding="utf-8")

    helper_paths: list[Path] = []
    for route in routes:
        route.helper_path.write_text(render_wezterm_helper_script(project, route=route), encoding="utf-8")
        route.helper_path.chmod(0o755)
        helper_paths.append(route.helper_path)

    manifest = WezTermPackManifest(
        project=project.name,
        out_dir=out_dir,
        routes=tuple(routes),
        skipped=tuple(skipped),
        routes_path=routes_path,
        commands_path=commands_path,
        readme_path=readme_path,
        helper_paths=tuple(helper_paths),
    )
    readme_path.write_text(render_wezterm_readme(project, manifest=manifest), encoding="utf-8")
    return manifest
