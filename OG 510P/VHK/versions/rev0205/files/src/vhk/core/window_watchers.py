from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rich.console import Console

from vhk.core.models import Project, WindowWatcher
from vhk.core.runner import Runner
from vhk.system.active_window import get_active_window_info, selector_matches_info
from vhk.system.wm_events import WmEvent, iter_wm_events, window_info_from_event


@dataclass
class WindowWatcherStats:
    watcher: str
    events_seen: int = 0
    macro_runs: int = 0
    skipped_duplicates: int = 0
    skipped_duplicate_window: int = 0
    skipped_cooldown: int = 0
    skipped_nonmatching: int = 0
    macro_failures: int = 0


def _preview_window(info: dict[str, Any], limit: int = 120) -> str:
    cls = info.get("class") or info.get("app_id") or ""
    title = info.get("title") or ""
    txt = f"{cls} — {title}".strip(" —")
    if len(txt) <= limit:
        return txt
    return txt[: limit - 1] + "…"


def _write_event(project: Project, watcher: WindowWatcher, payload: dict[str, Any]) -> str:
    log_dir = Path(project.root_dir) / project.settings.log_dir
    log_dir.mkdir(parents=True, exist_ok=True)
    path = log_dir / f"window_watcher_{watcher.name}.jsonl"
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return str(path)


def _resolve_watcher(project: Project, watcher_name: str) -> WindowWatcher:
    for watcher in project.window_watchers:
        if watcher.name == watcher_name:
            return watcher
    available = ", ".join(w.name for w in project.window_watchers) or "(none)"
    raise KeyError(f"Unknown window watcher '{watcher_name}'. Available: {available}")


def _sig(info: dict[str, Any], *, kind: str) -> str:
    """Compute a signature for de-duplication.

    For focus watchers, the compositor-provided id/address is usually stable.
    For title/urgent watchers, mix in the changing attribute so successive
    changes on the same window are not de-duped away.
    """

    key = info.get("id") or info.get("address") or ""
    base = str(key) if key else ""

    extra = ""
    if kind == "title":
        extra = "|" + str(info.get("title") or "")
    elif kind == "urgent":
        extra = "|urgent:" + str(bool(info.get("urgent")))

    if base:
        return base + extra

    cls = str(info.get("class") or info.get("app_id") or "")
    title = str(info.get("title") or "")
    return hashlib.sha256((cls + "|" + title + extra).encode("utf-8", errors="replace")).hexdigest()


def _to_vars(info: dict[str, Any], wm: str, ev: WmEvent) -> dict[str, Any]:
    return {
        "wm": wm,
        "wm_event": ev.kind,
        "wm_event_name": ev.name,
        "wm_event_data": ev.data,
        "window": info,
        # Common convenience fields
        "window_title": info.get("title"),
        "window_class": info.get("class") or info.get("app_id"),
        "workspace": info.get("workspace"),
        "urgent": info.get("urgent"),
    }


def run_window_watcher(
    project: Project,
    watcher_name: str,
    *,
    console: Console | None = None,
    max_events: int | None = None,
    poll_ms: int = 200,
) -> WindowWatcherStats:
    """Run a project-defined window watcher loop."""

    con = console or Console()
    watcher = _resolve_watcher(project, watcher_name)
    if not watcher.enabled:
        raise RuntimeError(f"Window watcher '{watcher.name}' is disabled")

    if watcher.macro not in project.macros:
        raise RuntimeError(f"Window watcher '{watcher.name}' references missing macro '{watcher.macro}'")

    stats = WindowWatcherStats(watcher=watcher.name)
    event_log_path: str | None = None

    prev_info: dict[str, Any] | None = None
    last_sig: str | None = None

    cooldown_until_ms: int = 0
    recent: dict[str, int] = {}
    recent_order: list[tuple[str, int]] = []

    def handle_event(ev: WmEvent) -> None:
        nonlocal prev_info, last_sig, event_log_path, cooldown_until_ms

        try:
            if ev.kind in {"title", "urgent", "new", "close"}:
                info = window_info_from_event(ev) or {}
                wm = ev.wm
                # For title/urgent we can safely fall back to probing the active
                # window when the compositor event does not carry enough data.
                # For new/close, prefer the event payload; probing may pick the
                # wrong window (especially on close).
                if (not info) and ev.kind in {"title", "urgent"}:
                    info, wm = get_active_window_info()
            else:
                info, wm = get_active_window_info()
        except Exception as exc:
            info, wm = {}, ev.wm
            con.print(f"[yellow]Warning:[/yellow] cannot probe active window: {exc}")

        sig = _sig(info, kind=ev.kind)
        now_ms = int(time.time() * 1000.0)
        base_payload: dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "watcher": watcher.name,
            "macro": watcher.macro,
            "wm": wm,
            "event": ev.kind,
            "event_name": ev.name,
            "preview": _preview_window(info),
            "sig": sig,
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
            last_sig = sig
            prev_info = info
            return

        if watcher.dedupe and watcher.dedupe_window_ms > 0:
            last_ms = recent.get(sig)
            if last_ms is not None and (now_ms - last_ms) < watcher.dedupe_window_ms:
                stats.skipped_duplicate_window += 1
                base_payload.update(
                    {
                        "action": "skip_duplicate_window",
                        "dedupe_window_ms": watcher.dedupe_window_ms,
                    }
                )
                event_log_path = _write_event(project, watcher, base_payload)
                last_sig = sig
                prev_info = info
                return
            if watcher.dedupe_max_entries > 0:
                recent[sig] = now_ms
                recent_order.append((sig, now_ms))
                while len(recent_order) > watcher.dedupe_max_entries:
                    old_sig, old_ts = recent_order.pop(0)
                    if recent.get(old_sig) == old_ts:
                        recent.pop(old_sig, None)

        if watcher.dedupe and last_sig is not None and sig == last_sig:
            stats.skipped_duplicates += 1
            base_payload.update({"action": "skip_duplicate"})
            event_log_path = _write_event(project, watcher, base_payload)
            return

        if watcher.when is not None:
            if not selector_matches_info(watcher.when, info, wm):
                stats.skipped_nonmatching += 1
                base_payload.update({"action": "skip_nonmatching", "when": watcher.when.model_dump(by_alias=True)})
                event_log_path = _write_event(project, watcher, base_payload)
                last_sig = sig
                prev_info = info
                return

        initial_vars = _to_vars(info, wm, ev)
        initial_vars.update(watcher.vars)
        if watcher.include_prev:
            initial_vars["prev_window"] = prev_info

        runner = Runner(project=project, console=con)
        result = runner.run(watcher.macro, initial_vars=initial_vars)

        base_payload.update(
            {
                "action": "run_macro",
                "ok": bool(result.ok),
                "event_log": result.event_log,
                "error": result.error,
            }
        )
        event_log_path = _write_event(project, watcher, base_payload)

        last_sig = sig
        prev_info = info

        if result.ok:
            stats.macro_runs += 1
        else:
            stats.macro_failures += 1
            con.print(f"[red]Window watcher '{watcher.name}' macro failed:[/red] {result.error}")
            if not watcher.continue_on_macro_error:
                raise RuntimeError(f"Window watcher '{watcher.name}' stopped after macro failure: {result.error}")

        if watcher.cooldown_ms > 0:
            cooldown_until_ms = now_ms + int(watcher.cooldown_ms)

        if watcher.debounce_ms > 0:
            time.sleep(watcher.debounce_ms / 1000.0)

    # Optional startup event.
    if watcher.fire_on_start:
        try:
            info0, wm0 = get_active_window_info()
            prev_info = info0
            last_sig = _sig(info0, kind=watcher.event)
            fake = WmEvent(wm=wm0, kind=watcher.event, name="startup", data=None)
            handle_event(fake)
        except Exception:
            pass

    for ev in iter_wm_events(kinds={watcher.event}, poll_ms=poll_ms):
        if max_events is not None and stats.events_seen >= max_events:
            break
        stats.events_seen += 1
        handle_event(ev)

    if event_log_path:
        con.print(f"[dim]Watcher log:[/dim] {event_log_path}")

    return stats
