from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rich.console import Console

from vhk.core.models import FileWatcher, Project
from vhk.core.runner import Runner
from vhk.system import watch as watch_mod


@dataclass
class FileWatcherStats:
    watcher: str
    events_seen: int = 0
    macro_runs: int = 0
    skipped_duplicates: int = 0
    skipped_duplicate_window: int = 0
    skipped_cooldown: int = 0
    macro_failures: int = 0



def _preview_path(path: str, limit: int = 160) -> str:
    txt = path.replace("\r", " ").replace("\n", " ")
    if len(txt) <= limit:
        return txt
    return txt[: limit - 1] + "…"



def _write_event(project: Project, watcher: FileWatcher, payload: dict[str, Any]) -> str:
    log_dir = Path(project.root_dir) / project.settings.log_dir
    log_dir.mkdir(parents=True, exist_ok=True)
    path = log_dir / f"file_watcher_{watcher.name}.jsonl"
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return str(path)



def _resolve_watcher(project: Project, watcher_name: str) -> FileWatcher:
    for watcher in getattr(project, "file_watchers", []) or []:
        if watcher.name == watcher_name:
            return watcher
    available = ", ".join(w.name for w in (getattr(project, "file_watchers", []) or [])) or "(none)"
    raise KeyError(f"Unknown file watcher '{watcher_name}'. Available: {available}")



def run_file_watcher(
    project: Project,
    watcher_name: str,
    *,
    console: Console | None = None,
    max_events: int | None = None,
) -> FileWatcherStats:
    """Continuously watch a directory and run a macro on matching file events."""

    con = console or Console()
    watcher = _resolve_watcher(project, watcher_name)
    if not watcher.enabled:
        raise RuntimeError(f"File watcher '{watcher.name}' is disabled")

    if watcher.macro not in project.macros:
        raise RuntimeError(f"File watcher '{watcher.name}' references missing macro '{watcher.macro}'")

    stats = FileWatcherStats(watcher=watcher.name)
    event_log_path: str | None = None
    cooldown_until_ms: int = 0
    last_signature: str | None = None
    recent: dict[str, int] = {}
    recent_order: list[tuple[str, int]] = []
    snapshot = None

    while max_events is None or stats.events_seen < max_events:
        ev, snapshot = watch_mod.wait_for_file_event(
            watcher.directory,
            event=watcher.event,
            pattern=watcher.pattern,
            recursive=watcher.recursive,
            exclude=list(watcher.exclude or []),
            timeout_ms=86_400_000,
            min_size=int(watcher.min_size),
            stable_ms=int(watcher.stable_ms),
            quiet_ms=int(getattr(watcher, "quiet_ms", 0) or 0),
            baseline=snapshot,
        )
        stats.events_seen += 1
        now_ms = int(time.time() * 1000.0)

        batch_paths = list(getattr(ev, "batch_paths", []) or [str(ev.path)])
        batch_names = list(getattr(ev, "batch_names", []) or [ev.name])
        batch_kinds = list(getattr(ev, "batch_kinds", []) or [ev.kind])
        batch_count = int(getattr(ev, "batch_count", 1) or 1)
        sig_src = f"{ev.kind}|{ev.path}|{ev.mtime_ns}|{ev.size}|{ev.raw_event or ''}|{batch_count}|{'|'.join(batch_paths)}|{'|'.join(batch_kinds)}"
        sig = hashlib.sha256(sig_src.encode("utf-8", errors="replace")).hexdigest()
        base_payload: dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "watcher": watcher.name,
            "macro": watcher.macro,
            "event": ev.kind,
            "path": str(ev.path),
            "name": ev.name,
            "directory": ev.directory,
            "exists": bool(ev.exists),
            "size": ev.size,
            "mtime_ns": ev.mtime_ns,
            "helper": ev.helper,
            "raw_event": ev.raw_event,
            "batch_count": batch_count,
            "batch_paths": batch_paths,
            "batch_names": batch_names,
            "batch_kinds": batch_kinds,
            "sha256": sig,
            "preview": _preview_path(str(ev.path)),
        }

        if watcher.cooldown_ms > 0 and now_ms < cooldown_until_ms:
            stats.skipped_cooldown += 1
            base_payload.update({
                "action": "skip_cooldown",
                "cooldown_ms": watcher.cooldown_ms,
                "cooldown_until_ms": cooldown_until_ms,
            })
            event_log_path = _write_event(project, watcher, base_payload)
            if watcher.dedupe_window_ms > 0 and watcher.dedupe_max_entries > 0:
                recent[sig] = now_ms
                recent_order.append((sig, now_ms))
                while len(recent_order) > watcher.dedupe_max_entries:
                    old_sig, old_ts = recent_order.pop(0)
                    if recent.get(old_sig) == old_ts:
                        recent.pop(old_sig, None)
            continue

        if watcher.dedupe and last_signature == sig:
            stats.skipped_duplicates += 1
            base_payload.update({"action": "skip_duplicate"})
            event_log_path = _write_event(project, watcher, base_payload)
            continue

        if watcher.dedupe and watcher.dedupe_window_ms > 0:
            last_ms = recent.get(sig)
            if last_ms is not None and (now_ms - last_ms) < watcher.dedupe_window_ms:
                stats.skipped_duplicate_window += 1
                base_payload.update({
                    "action": "skip_duplicate_window",
                    "dedupe_window_ms": watcher.dedupe_window_ms,
                })
                event_log_path = _write_event(project, watcher, base_payload)
                continue
            if watcher.dedupe_max_entries > 0:
                recent[sig] = now_ms
                recent_order.append((sig, now_ms))
                while len(recent_order) > watcher.dedupe_max_entries:
                    old_sig, old_ts = recent_order.pop(0)
                    if recent.get(old_sig) == old_ts:
                        recent.pop(old_sig, None)

        initial_vars: dict[str, Any] = {
            "file_event": ev.kind,
            "file_path": str(ev.path),
            "file_name": ev.name,
            "file_dir": ev.directory,
            "file_exists": bool(ev.exists),
            "file_size": ev.size,
            "file_mtime_ns": ev.mtime_ns,
            "file_event_helper": ev.helper,
            "file_event_raw": ev.raw_event,
            "file_batch_count": batch_count,
            "file_batch_paths": batch_paths,
            "file_batch_names": batch_names,
            "file_batch_kinds": batch_kinds,
            "watcher_name": watcher.name,
        }
        initial_vars.update(watcher.vars)

        runner = Runner(project=project, console=con)
        result = runner.run(watcher.macro, initial_vars=initial_vars)
        last_signature = sig

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
            con.print(f"[red]File watcher '{watcher.name}' macro failed:[/red] {result.error}")
            if not watcher.continue_on_macro_error:
                raise RuntimeError(f"File watcher '{watcher.name}' stopped after macro failure: {result.error}")

        if watcher.cooldown_ms > 0:
            cooldown_until_ms = now_ms + int(watcher.cooldown_ms)

        if watcher.debounce_ms > 0:
            time.sleep(watcher.debounce_ms / 1000.0)

    if event_log_path:
        con.print(f"[dim]Watcher log:[/dim] {event_log_path}")
    return stats
