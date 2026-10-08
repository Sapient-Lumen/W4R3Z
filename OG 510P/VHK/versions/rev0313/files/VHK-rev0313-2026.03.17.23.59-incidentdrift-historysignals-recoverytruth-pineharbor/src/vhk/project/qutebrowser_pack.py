from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import Any

import yaml

from vhk.core.models import Project


_QUTE_CONTEXT_VARS: tuple[str, ...] = (
    "qute_mode",
    "qute_url",
    "qute_current_url",
    "qute_title",
    "qute_selected_text",
    "qute_selected_html",
    "qute_commandline_text",
    "qute_tab_index",
    "qute_count",
    "qute_version",
    "qute_user_agent",
    "qute_html",
    "qute_text",
    "qute_fifo",
)


def _slugify(text: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", str(text).strip()).strip("-").lower()
    return slug or "project"


@dataclass(frozen=True)
class QutebrowserRoute:
    route_id: str
    macro: str
    description: str
    selector_source: str
    selector_snapshot: dict[str, Any]
    binding_keys: tuple[str, ...]
    userscript_path: Path

    def to_dict(self) -> dict[str, object]:
        script_name = self.userscript_path.name
        return {
            "route_id": self.route_id,
            "macro": self.macro,
            "description": self.description,
            "selector_source": self.selector_source,
            "selector_snapshot": dict(self.selector_snapshot),
            "binding_keys": list(self.binding_keys),
            "userscript_path": str(self.userscript_path),
            "spawn_example": f":spawn --userscript {script_name}",
            "hint_example": f":hint links userscript {script_name}",
            "context_vars": list(_QUTE_CONTEXT_VARS),
        }


@dataclass(frozen=True)
class QutebrowserPackManifest:
    project: str
    out_dir: Path
    routes: tuple[QutebrowserRoute, ...]
    skipped: tuple[dict[str, object], ...]
    routes_path: Path
    commands_path: Path
    readme_path: Path
    userscript_paths: tuple[Path, ...]

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
            "userscript_paths": [str(path) for path in self.userscript_paths],
        }



def default_qutebrowser_dir(project: Project) -> Path:
    return Path(project.root_dir) / "integrations" / "qutebrowser"



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



def _is_qutebrowser_selector(selector: Any) -> bool:
    return "qutebrowser" in " ".join(_selector_texts(selector)).lower()



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



def build_qutebrowser_routes(project: Project, *, out_dir: Path) -> tuple[list[QutebrowserRoute], list[dict[str, object]]]:
    userscript_dir = Path(out_dir) / "userscripts"
    routes: list[QutebrowserRoute] = []
    skipped: list[dict[str, object]] = []

    for macro_name, macro in getattr(project, "macros", {}).items():
        if getattr(macro, "hidden", False):
            continue
        selectors = [(source, selector) for source, selector in _collect_macro_selectors(project, macro_name) if _is_qutebrowser_selector(selector)]
        if not selectors:
            continue
        selector_source, selector = selectors[0]
        route_id = _slugify(f"{macro_name}-qutebrowser-userscript")
        routes.append(
            QutebrowserRoute(
                route_id=route_id,
                macro=macro_name,
                description=str(getattr(macro, "description", None) or getattr(macro, "name", None) or macro_name),
                selector_source=selector_source,
                selector_snapshot=_selector_snapshot(selector),
                binding_keys=tuple(_collect_binding_keys(project, macro_name)),
                userscript_path=userscript_dir / route_id,
            )
        )

    return routes, skipped



def render_qutebrowser_routes_yaml(project: Project, *, routes: list[QutebrowserRoute], skipped: list[dict[str, object]]) -> str:
    payload = {
        "project": project.name,
        "generated_by": "vhk gen-qutebrowser-pack",
        "notes": [
            "This pack is a thin qutebrowser userscript handoff for browser-targeted routes.",
            "Each generated userscript passes qutebrowser context from QUTE_* environment variables into `vhk run --vars ...`.",
            "qutebrowser userscripts can be launched with `:spawn --userscript ...` or hint-driven with `:hint links userscript ...`.",
        ],
        "routes": [
            {
                "id": route.route_id,
                "macro": route.macro,
                "description": route.description,
                "selector": route.selector_snapshot,
                "binding_keys": list(route.binding_keys),
                "qutebrowser": {
                    "selector_source": route.selector_source,
                    "userscript": route.userscript_path.name,
                    "spawn_example": f":spawn --userscript {route.userscript_path.name}",
                    "hint_example": f":hint links userscript {route.userscript_path.name}",
                    "context_vars": list(_QUTE_CONTEXT_VARS),
                },
                "helper_script": str(route.userscript_path),
            }
            for route in routes
        ],
        "skipped": skipped,
    }
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)



def render_qutebrowser_commands_json(project: Project, *, routes: list[QutebrowserRoute], skipped: list[dict[str, object]]) -> str:
    payload = {
        "project": project.name,
        "route_count": len(routes),
        "routes": [route.to_dict() for route in routes],
        "skipped": skipped,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)



def render_qutebrowser_userscript(project: Project, *, route: QutebrowserRoute, command: str) -> str:
    project_root = str(Path(project.root_dir).resolve())
    return dedent(
        f'''\
        #!/usr/bin/env bash
        set -euo pipefail

        # Generated by `vhk gen-qutebrowser-pack` for project: {project.name}
        # Route id: {route.route_id}

        VHK_COMMAND=${{VHK_COMMAND:-{command}}}
        VHK_PROJECT_DIR=${{VHK_PROJECT_DIR:-{project_root}}}
        VHK_MACRO=${{VHK_MACRO:-{route.macro}}}
        VHK_NOTIFY_QUTE=${{VHK_NOTIFY_QUTE:-1}}

        if [[ "$VHK_NOTIFY_QUTE" == "1" && -n "${{QUTE_FIFO:-}}" ]]; then
          printf 'message-info VHK userscript %s starting\n' "{route.route_id}" >> "$QUTE_FIFO" 2>/dev/null || true
        fi

        VHK_VARS=$(python3 - <<'PY'
        import json
        import os

        data = {{
            "qute_mode": os.environ.get("QUTE_MODE"),
            "qute_url": os.environ.get("QUTE_URL"),
            "qute_current_url": os.environ.get("QUTE_CURRENT_URL"),
            "qute_title": os.environ.get("QUTE_TITLE"),
            "qute_selected_text": os.environ.get("QUTE_SELECTED_TEXT"),
            "qute_selected_html": os.environ.get("QUTE_SELECTED_HTML"),
            "qute_commandline_text": os.environ.get("QUTE_COMMANDLINE_TEXT"),
            "qute_tab_index": os.environ.get("QUTE_TAB_INDEX"),
            "qute_count": os.environ.get("QUTE_COUNT"),
            "qute_version": os.environ.get("QUTE_VERSION"),
            "qute_user_agent": os.environ.get("QUTE_USER_AGENT"),
            "qute_html": os.environ.get("QUTE_HTML"),
            "qute_text": os.environ.get("QUTE_TEXT"),
            "qute_fifo": os.environ.get("QUTE_FIFO"),
        }}
        print(json.dumps({{k: v for k, v in data.items() if v not in (None, "")}}, ensure_ascii=False))
        PY
        )

        if [[ "${{VHK_RUN_MODE:-run}}" == "print-vars" ]]; then
          printf '%s\n' "$VHK_VARS"
          exit 0
        fi

        if "$VHK_COMMAND" run "$VHK_PROJECT_DIR" "$VHK_MACRO" --vars "$VHK_VARS" --quiet; then
          if [[ "$VHK_NOTIFY_QUTE" == "1" && -n "${{QUTE_FIFO:-}}" ]]; then
            printf 'message-info VHK userscript %s finished\n' "{route.route_id}" >> "$QUTE_FIFO" 2>/dev/null || true
          fi
        else
          status=$?
          if [[ "$VHK_NOTIFY_QUTE" == "1" && -n "${{QUTE_FIFO:-}}" ]]; then
            printf 'message-error VHK userscript %s failed\n' "{route.route_id}" >> "$QUTE_FIFO" 2>/dev/null || true
          fi
          exit $status
        fi
        '''
    )



def render_qutebrowser_readme(project: Project, *, manifest: QutebrowserPackManifest) -> str:
    lines = [
        f"# {project.name} qutebrowser userscript pack",
        "",
        "Generated by `vhk gen-qutebrowser-pack`.",
        "",
        "This pack turns the app-native qutebrowser lane into a concrete, reviewable userscript handoff.",
        "",
        "## What it writes",
        "",
        "- `vhk.qutebrowser.routes.yml` — route catalog with selector evidence and userscript entrypoints",
        "- `vhk.qutebrowser.commands.json` — machine-readable command ledger",
        "- `userscripts/*` — executable qutebrowser userscripts that call `vhk run ... --vars <QUTE context JSON>`",
        "",
        "## Assumptions and limits",
        "",
        "- qutebrowser userscripts can be launched via `:spawn --userscript ...` or `:hint links userscript ...`.",
        "- The generated scripts pass qutebrowser context from environment variables such as `QUTE_MODE`, `QUTE_URL`, `QUTE_TITLE`, `QUTE_SELECTED_TEXT`, and `QUTE_FIFO` into VHK via `--vars`.",
        "- When `QUTE_FIFO` is available, the scripts emit `message-info` / `message-error` status lines so browser-side feedback stays visible.",
        "- Install by copying the executable scripts into `~/.local/share/qutebrowser/userscripts/` (or another qutebrowser userscripts directory), or invoke them via absolute path.",
        "",
        "## Routes",
        "",
    ]
    if not manifest.routes:
        lines.extend(
            [
                "No qutebrowser-targeted routes were exported.",
                "",
                "Add selectors or bindings that clearly target qutebrowser and regenerate the pack.",
            ]
        )
    else:
        for route in manifest.routes:
            lines.extend(
                [
                    f"### `{route.route_id}`",
                    "",
                    f"- macro: `{route.macro}`",
                    f"- selector source: `{route.selector_source}`",
                    f"- userscript: `{route.userscript_path.name}`",
                    f"- spawn example: `:spawn --userscript {route.userscript_path.name}`",
                    f"- hint example: `:hint links userscript {route.userscript_path.name}`",
                    "",
                ]
            )
    if manifest.skipped:
        lines.extend(["## Skipped", ""])
        for item in manifest.skipped:
            lines.append(f"- `{item.get('macro')}` — {item.get('reason')}: {item.get('detail')}")
        lines.append("")
    return "\n".join(lines) + "\n"



def write_qutebrowser_pack(project: Project, *, out_dir: Path, command: str = "vhk") -> QutebrowserPackManifest:
    target_dir = Path(out_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    userscript_dir = target_dir / "userscripts"
    userscript_dir.mkdir(parents=True, exist_ok=True)

    routes, skipped = build_qutebrowser_routes(project, out_dir=target_dir)
    routes_path = target_dir / "vhk.qutebrowser.routes.yml"
    commands_path = target_dir / "vhk.qutebrowser.commands.json"
    readme_path = target_dir / "README.md"

    for route in routes:
        route.userscript_path.write_text(render_qutebrowser_userscript(project, route=route, command=command), encoding="utf-8")
        route.userscript_path.chmod(route.userscript_path.stat().st_mode | 0o111)

    manifest = QutebrowserPackManifest(
        project=project.name,
        out_dir=target_dir,
        routes=tuple(routes),
        skipped=tuple(skipped),
        routes_path=routes_path,
        commands_path=commands_path,
        readme_path=readme_path,
        userscript_paths=tuple(route.userscript_path for route in routes),
    )
    routes_path.write_text(render_qutebrowser_routes_yaml(project, routes=routes, skipped=skipped), encoding="utf-8")
    commands_path.write_text(render_qutebrowser_commands_json(project, routes=routes, skipped=skipped), encoding="utf-8")
    readme_path.write_text(render_qutebrowser_readme(project, manifest=manifest), encoding="utf-8")
    return manifest
