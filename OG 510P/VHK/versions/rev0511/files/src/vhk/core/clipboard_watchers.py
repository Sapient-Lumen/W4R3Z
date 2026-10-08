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
    skipped_duplicate_window: int = 0
    skipped_cooldown: int = 0
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
    last_handled = baseline if (watcher.dedupe and watcher.dedupe_scope == "handled") else None
    event_log_path: str | None = None

    cooldown_until_ms: int = 0
    # For dedupe_window_ms we keep a bounded LRU-ish map of recent clipboard values.
    # Keys are sha256 hashes of the clipboard text.
    recent: dict[str, int] = {}
    recent_order: list[tuple[str, int]] = []

    while max_events is None or stats.events_seen < max_events:
        prev_seen = baseline
        changed = True
        if watcher.event_mode == "event":
            text, changed = watch_mod.wait_for_clipboard_event(
                clipboard_mod.read,
                selection=watcher.selection,
                initial_text=baseline,
                timeout_ms=86_400_000,
            )
        else:
            text = watch_mod.wait_for_clipboard_change(
                clipboard_mod.read,
                selection=watcher.selection,
                initial_text=baseline,
                timeout_ms=86_400_000,
            )
            changed = True
        stats.events_seen += 1
        baseline = text

        now_ms = int(time.time() * 1000.0)

        sha = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()
        base_payload: dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "watcher": watcher.name,
            "macro": watcher.macro,
            "selection": watcher.selection,
            "event_mode": watcher.event_mode,
            "changed": bool(changed),
            "text_len": len(text),
            "sha256": sha,
            "preview": _preview(text),
        }

        if watcher.cooldown_ms > 0 and now_ms < cooldown_until_ms:
            stats.skipped_cooldown += 1
            base_payload.update(
                {
                    "action": "skip_cooldown",
                    "cooldown_ms": watcher.cooldown_ms,
                    "cooldown_until_ms": cooldown_until_ms,
                }
            )
            event_log_path = _write_event(project, watcher, base_payload)
            # Still track the value for window-based de-dupe.
            if watcher.dedupe_window_ms > 0 and watcher.dedupe_max_entries > 0:
                recent[sha] = now_ms
                recent_order.append((sha, now_ms))
                while len(recent_order) > watcher.dedupe_max_entries:
                    old_sha, old_ts = recent_order.pop(0)
                    if recent.get(old_sha) == old_ts:
                        recent.pop(old_sha, None)
            continue

        if watcher.dedupe and watcher.dedupe_scope == "seen" and text == prev_seen:
            stats.skipped_duplicates += 1
            base_payload.update({"action": "skip_duplicate"})
            event_log_path = _write_event(project, watcher, base_payload)
            continue

        if watcher.dedupe and watcher.dedupe_scope == "handled" and last_handled is not None and text == last_handled:
            stats.skipped_duplicates += 1
            base_payload.update({"action": "skip_duplicate"})
            event_log_path = _write_event(project, watcher, base_payload)
            continue

        if watcher.dedupe and watcher.dedupe_window_ms > 0:
            last_ms = recent.get(sha)
            if last_ms is not None and (now_ms - last_ms) < watcher.dedupe_window_ms:
                stats.skipped_duplicate_window += 1
                base_payload.update(
                    {
                        "action": "skip_duplicate_window",
                        "dedupe_window_ms": watcher.dedupe_window_ms,
                    }
                )
                event_log_path = _write_event(project, watcher, base_payload)
                continue

            if watcher.dedupe_max_entries > 0:
                recent[sha] = now_ms
                recent_order.append((sha, now_ms))
                # Bound memory: remove oldest entries.
                while len(recent_order) > watcher.dedupe_max_entries:
                    old_sha, old_ts = recent_order.pop(0)
                    # Only delete if this key hasn't been refreshed.
                    if recent.get(old_sha) == old_ts:
                        recent.pop(old_sha, None)

        match = pattern.search(text) if pattern else None
        if pattern and not match:
            stats.skipped_nonmatching += 1
            base_payload.update({"action": "skip_nonmatching", "pattern": watcher.pattern})
            event_log_path = _write_event(project, watcher, base_payload)
            continue

        initial_vars: dict[str, Any] = {
            "clipboard_text": text,
            "clipboard_selection": watcher.selection,
            "clipboard_changed": bool(changed),
            "clipboard_event": True,
            "clipboard_event_mode": watcher.event_mode,
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
        if watcher.dedupe and watcher.dedupe_scope == "handled":
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

        if watcher.cooldown_ms > 0:
            cooldown_until_ms = now_ms + int(watcher.cooldown_ms)

        if watcher.debounce_ms > 0:
            time.sleep(watcher.debounce_ms / 1000.0)

    if event_log_path:
        con.print(f"[dim]Watcher log:[/dim] {event_log_path}")
    return stats
