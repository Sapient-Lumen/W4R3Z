from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rich.console import Console

from vhk.core.models import ClipboardWatcher, Project
from vhk.core.runner import Runner
from vhk.system import clipboard as clipboard_mod
from vhk.system import watch as watch_mod


@dataclass
class ClipboardWatcherStats:
    watcher: str
    events_seen: int = 0
    macro_runs: int = 0
    skipped_duplicates: int = 0
    skipped_nonmatching: int = 0
    macro_failures: int = 0


def _compile_pattern(pattern: str | None, flags: list[str]) -> re.Pattern[str] | None:
    if not pattern:
        return None
    fl = 0
    for f in flags:
        fl |= getattr(re, f)
    return re.compile(pattern, fl)


def _preview(text: str, limit: int = 120) -> str:
    one_line = text.replace("\r", " ").replace("\n", " ⏎ ")
    if len(one_line) <= limit:
        return one_line
    return one_line[: limit - 1] + "…"


def _write_event(project: Project, watcher: ClipboardWatcher, payload: dict[str, Any]) -> str:
    log_dir = Path(project.root_dir) / project.settings.log_dir
    log_dir.mkdir(parents=True, exist_ok=True)
    path = log_dir / f"clipboard_watcher_{watcher.name}.jsonl"
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return str(path)


def _resolve_watcher(project: Project, watcher_name: str) -> ClipboardWatcher:
    for watcher in project.clipboard_watchers:
        if watcher.name == watcher_name:
            return watcher
    available = ", ".join(w.name for w in project.clipboard_watchers) or "(none)"
    raise KeyError(f"Unknown clipboard watcher '{watcher_name}'. Available: {available}")


def run_clipboard_watcher(
    project: Project,
    watcher_name: str,
    *,
    console: Console | None = None,
    max_events: int | None = None,
) -> ClipboardWatcherStats:
    """Continuously watch the clipboard and run a macro when the watcher matches.

    This is intentionally a small, headless analogue of clipboard-rule systems in
    tools like CopyQ. It keeps policy in project.yaml and reuses the normal macro
    runner for the actual work.
    """

    con = console or Console()
    watcher = _resolve_watcher(project, watcher_name)
    if not watcher.enabled:
        raise RuntimeError(f"Clipboard watcher '{watcher.name}' is disabled")

    if watcher.macro not in project.macros:
        raise RuntimeError(f"Clipboard watcher '{watcher.name}' references missing macro '{watcher.macro}'")

    pattern = _compile_pattern(watcher.pattern, watcher.flags)
    stats = ClipboardWatcherStats(watcher=watcher.name)
    baseline = clipboard_mod.read(selection=watcher.selection)
    last_handled = baseline if watcher.dedupe else None
    event_log_path: str | None = None

    while max_events is None or stats.events_seen < max_events:
        text = watch_mod.wait_for_clipboard_change(
            clipboard_mod.read,
            selection=watcher.selection,
            initial_text=baseline,
            timeout_ms=86_400_000,
        )
        stats.events_seen += 1
        baseline = text

        sha = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()
        base_payload: dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "watcher": watcher.name,
            "macro": watcher.macro,
            "selection": watcher.selection,
            "text_len": len(text),
            "sha256": sha,
            "preview": _preview(text),
        }

        if watcher.dedupe and text == last_handled:
            stats.skipped_duplicates += 1
            base_payload.update({"action": "skip_duplicate"})
            event_log_path = _write_event(project, watcher, base_payload)
            continue

        match = pattern.search(text) if pattern else None
        if pattern and not match:
            stats.skipped_nonmatching += 1
            base_payload.update({"action": "skip_nonmatching", "pattern": watcher.pattern})
            event_log_path = _write_event(project, watcher, base_payload)
            continue

        initial_vars: dict[str, Any] = {
            "clipboard_text": text,
            "clipboard_selection": watcher.selection,
            "watcher_name": watcher.name,
        }
        initial_vars.update(watcher.vars)

        if match:
            initial_vars["clipboard_match"] = match.group(0)
            initial_vars["clipboard_groups"] = list(match.groups())
            initial_vars["clipboard_match_groups"] = {str(i): g for i, g in enumerate(match.groups())}
            initial_vars["clipboard_groupdict"] = match.groupdict()
            base_payload["pattern"] = watcher.pattern
            base_payload["match"] = match.group(0)

        runner = Runner(project=project, console=con)
        result = runner.run(watcher.macro, initial_vars=initial_vars)
        last_handled = text

        base_payload.update(
            {
                "action": "run_macro",
                "ok": bool(result.ok),
                "event_log": result.event_log,
                "error": result.error,
            }
        )
        event_log_path = _write_event(project, watcher, base_payload)

        if result.ok:
            stats.macro_runs += 1
        else:
            stats.macro_failures += 1
            con.print(f"[red]Clipboard watcher '{watcher.name}' macro failed:[/red] {result.error}")
            if not watcher.continue_on_macro_error:
                raise RuntimeError(f"Clipboard watcher '{watcher.name}' stopped after macro failure: {result.error}")

        if watcher.debounce_ms > 0:
            time.sleep(watcher.debounce_ms / 1000.0)

    if event_log_path:
        con.print(f"[dim]Watcher log:[/dim] {event_log_path}")
    return stats
