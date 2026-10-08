from __future__ import annotations

import hashlib
import os
import json
import re
import time
import signal
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rich.console import Console

from vhk.core.models import BusWatcher, Project, I3WindowSelector
from vhk.core.runner import Runner
from vhk.system.active_window import get_active_window_info, selector_matches_info
from vhk.system.event_bus import BusEvent, get_bus_socket_path, iter_bus_events
from vhk.project.loader import load_project


@dataclass
class BusWatcherStats:
    watcher: str
    events_seen: int = 0
    macro_runs: int = 0
    skipped_duplicates: int = 0
    skipped_duplicate_window: int = 0
    skipped_cooldown: int = 0
    skipped_nonmatching: int = 0
    skipped_wrong_event: int = 0
    skipped_disallowed_macro: int = 0
    skipped_dispatch_invalid: int = 0
    macro_failures: int = 0


def _compile_pattern(pattern: str | None, flags: list[str]) -> re.Pattern[str] | None:
    if not pattern:
        return None
    fl = 0
    for f in flags:
        fl |= getattr(re, f)
    return re.compile(pattern, fl)


def _preview(text: str, limit: int = 120) -> str:
    one_line = (text or "").replace("\r", " ").replace("\n", " ⏎ ")
    if len(one_line) <= limit:
        return one_line
    return one_line[: limit - 1] + "…"


def _write_event(project: Project, watcher: BusWatcher, payload: dict[str, Any]) -> str:
    log_dir = Path(project.root_dir) / project.settings.log_dir
    log_dir.mkdir(parents=True, exist_ok=True)
    path = log_dir / f"bus_watcher_{watcher.name}.jsonl"
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return str(path)


def _resolve_watcher(project: Project, watcher_name: str) -> BusWatcher:
    for w in project.bus_watchers:
        if w.name == watcher_name:
            return w
    available = ", ".join(w.name for w in project.bus_watchers) or "(none)"
    raise KeyError(f"Unknown bus watcher '{watcher_name}'. Available: {available}")


def _event_text(ev: BusEvent) -> str:
    if isinstance(ev.data, str):
        return ev.data
    if ev.data is None:
        return ""
    try:
        return json.dumps(ev.data, ensure_ascii=False)
    except Exception:
        return str(ev.data)


def run_bus_watcher(
    project: Project,
    watcher_name: str,
    *,
    console: Console | None = None,
    max_events: int | None = None,
    force_unlink: bool = False,
) -> BusWatcherStats:
    """Run a project-defined bus watcher loop.

    The bus is an IPC "escape hatch": anything that can send a UNIX socket
    datagram can trigger a VHK macro.

    This mirrors the structure of clipboard/window watchers for consistency.
    """

    con = console or Console()
    watcher = _resolve_watcher(project, watcher_name)
    if not watcher.enabled:
        raise RuntimeError(f"Bus watcher '{watcher.name}' is disabled")

    if not watcher.dispatch:
        if not watcher.macro:
            raise RuntimeError(f"Bus watcher '{watcher.name}' requires a macro")
        if watcher.macro not in project.macros:
            raise RuntimeError(f"Bus watcher '{watcher.name}' references missing macro '{watcher.macro}'")

    stats = BusWatcherStats(watcher=watcher.name)
    event_log_path: str | None = None

    pattern = _compile_pattern(watcher.pattern, watcher.flags)

    cooldown_until_ms: int = 0
    recent: dict[str, int] = {}
    recent_order: list[tuple[str, int]] = []

    sock_path = get_bus_socket_path(Path(project.root_dir), configured=project.settings.bus_socket)
    con.print(f"[dim]Bus socket:[/dim] {sock_path}")

    fdname = os.environ.get("VHK_BUS_FDNAME") or project.settings.bus_fdname
    if fdname:
        con.print(f"[dim]Bus fdname:[/dim] {fdname}")

    it = iter_bus_events(sock_path, force_unlink=force_unlink, fdname=fdname)
    try:
        while max_events is None or stats.events_seen < max_events:
            ev = next(it)
            stats.events_seen += 1

            now_ms = int(time.time() * 1000.0)
            txt = _event_text(ev)
            sig = hashlib.sha256((ev.name + "\n" + txt).encode("utf-8", errors="replace")).hexdigest()

            base_payload: dict[str, Any] = {
                "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "watcher": watcher.name,
                "macro": watcher.macro,
                "bus_event": ev.name,
                "text_len": len(txt),
                "sha256": sig,
                "preview": _preview(txt),
            }

            active_info: dict[str, Any] | None = None
            active_wm: str | None = None

            want = (watcher.event or "*").strip()
            if want != "*" and ev.name != want:
                stats.skipped_wrong_event += 1
                base_payload.update({"action": "skip_wrong_event", "want_event": want})
                event_log_path = _write_event(project, watcher, base_payload)
                continue

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
                continue

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
                    continue

                if watcher.dedupe_max_entries > 0:
                    recent[sig] = now_ms
                    recent_order.append((sig, now_ms))
                    while len(recent_order) > watcher.dedupe_max_entries:
                        old_sig, old_ts = recent_order.pop(0)
                        if recent.get(old_sig) == old_ts:
                            recent.pop(old_sig, None)

            # "when" gate: watcher-level selector.
            if watcher.when is not None:
                try:
                    info, wm = get_active_window_info()
                    active_info, active_wm = info, wm
                    if not selector_matches_info(watcher.when, info, wm):
                        stats.skipped_nonmatching += 1
                        base_payload.update({"action": "skip_nonmatching", "when": watcher.when.model_dump(by_alias=True)})
                        event_log_path = _write_event(project, watcher, base_payload)
                        continue
                except Exception as exc:
                    stats.skipped_nonmatching += 1
                    base_payload.update(
                        {
                            "action": "skip_nonmatching",
                            "error": str(exc),
                            "when": watcher.when.model_dump(by_alias=True),
                        }
                    )
                    event_log_path = _write_event(project, watcher, base_payload)
                    continue

            match = pattern.search(txt) if pattern else None
            if pattern and not match:
                stats.skipped_nonmatching += 1
                base_payload.update({"action": "skip_nonmatching", "pattern": watcher.pattern})
                event_log_path = _write_event(project, watcher, base_payload)
                continue

            # Determine the target macro.
            target_macro: str | None = watcher.macro
            dispatch_vars: dict[str, Any] = {}
            dispatch_selector: I3WindowSelector | None = None
            dispatch_binding: str | None = None
            dispatch_keys: str | None = None

            if watcher.dispatch:
                if not isinstance(ev.data, dict):
                    stats.skipped_dispatch_invalid += 1
                    base_payload.update({"action": "skip_dispatch_invalid", "reason": "data_not_object"})
                    event_log_path = _write_event(project, watcher, base_payload)
                    continue

                macro_key = (watcher.dispatch_macro_key or "macro").strip() or "macro"
                vars_key = (watcher.dispatch_vars_key or "vars").strip() or "vars"
                rw_key = (watcher.dispatch_require_window_key or "require_window").strip() or "require_window"
                bind_key = (watcher.dispatch_binding_key or "binding").strip() or "binding"
                keys_key = (watcher.dispatch_keys_key or "keys").strip() or "keys"

                target_macro = ev.data.get(macro_key)  # type: ignore[assignment]
                if target_macro is not None:
                    target_macro = str(target_macro)
                raw_vars = ev.data.get(vars_key)
                if isinstance(raw_vars, dict):
                    dispatch_vars = dict(raw_vars)

                dispatch_binding_raw = ev.data.get(bind_key)
                dispatch_binding = str(dispatch_binding_raw) if dispatch_binding_raw is not None else None
                dispatch_keys_raw = ev.data.get(keys_key)
                dispatch_keys = str(dispatch_keys_raw) if dispatch_keys_raw is not None else None

                raw_selector = ev.data.get(rw_key)
                if isinstance(raw_selector, dict):
                    try:
                        dispatch_selector = I3WindowSelector.model_validate(raw_selector)
                    except Exception:
                        dispatch_selector = None

                if not target_macro:
                    stats.skipped_dispatch_invalid += 1
                    base_payload.update({"action": "skip_dispatch_invalid", "reason": "missing_macro"})
                    event_log_path = _write_event(project, watcher, base_payload)
                    continue

                if watcher.dispatch_allowed_macros is not None and target_macro not in watcher.dispatch_allowed_macros:
                    stats.skipped_disallowed_macro += 1
                    base_payload.update(
                        {
                            "action": "skip_disallowed_macro",
                            "target_macro": target_macro,
                        }
                    )
                    event_log_path = _write_event(project, watcher, base_payload)
                    continue

                if target_macro not in project.macros:
                    stats.macro_failures += 1
                    base_payload.update(
                        {
                            "action": "dispatch_missing_macro",
                            "target_macro": target_macro,
                        }
                    )
                    event_log_path = _write_event(project, watcher, base_payload)
                    con.print(f"[red]Bus dispatch macro not found:[/red] {target_macro}")
                    if not watcher.continue_on_macro_error:
                        raise RuntimeError(f"Bus watcher '{watcher.name}' stopped: dispatch macro not found: {target_macro}")
                    continue

                # Per-event require-window gate.
                if dispatch_selector is not None:
                    try:
                        info, wm = get_active_window_info()
                        active_info, active_wm = info, wm
                        if not selector_matches_info(dispatch_selector, info, wm):
                            stats.skipped_nonmatching += 1
                            base_payload.update(
                                {
                                    "action": "skip_nonmatching",
                                    "require_window": dispatch_selector.model_dump(by_alias=True),
                                }
                            )
                            event_log_path = _write_event(project, watcher, base_payload)
                            continue
                    except Exception as exc:
                        stats.skipped_nonmatching += 1
                        base_payload.update(
                            {
                                "action": "skip_nonmatching",
                                "error": str(exc),
                                "require_window": dispatch_selector.model_dump(by_alias=True),
                            }
                        )
                        event_log_path = _write_event(project, watcher, base_payload)
                        continue

            initial_vars: dict[str, Any] = {
                **(
                    {
                        "wm": active_wm,
                        "window": active_info,
                        "window_title": (active_info or {}).get("title"),
                        "window_class": (active_info or {}).get("class") or (active_info or {}).get("app_id"),
                        "workspace": (active_info or {}).get("workspace"),
                        "urgent": (active_info or {}).get("urgent"),
                    }
                    if active_info is not None
                    else {}
                ),
                "bus_event": ev.name,
                "bus_data": ev.data,
                "bus_text": txt,
                "watcher_name": watcher.name,
            }
            initial_vars.update(watcher.vars)
            if watcher.dispatch:
                initial_vars.update(
                    {
                        "dispatch_macro": target_macro,
                        "dispatch_binding": dispatch_binding,
                        "dispatch_keys": dispatch_keys,
                    }
                )
                # Per-event vars override watcher vars.
                initial_vars.update(dispatch_vars)

            if match is not None:
                initial_vars["bus_match"] = match.group(0)
                initial_vars["bus_groups"] = list(match.groups())
                initial_vars["bus_groupdict"] = match.groupdict()
                base_payload["pattern"] = watcher.pattern
                base_payload["match"] = match.group(0)

            runner = Runner(project=project, console=con)
            assert target_macro is not None
            base_payload["macro"] = target_macro
            if watcher.dispatch:
                base_payload["dispatch"] = True
                if dispatch_binding is not None:
                    base_payload["binding"] = dispatch_binding
                if dispatch_keys is not None:
                    base_payload["keys"] = dispatch_keys
                if dispatch_selector is not None:
                    base_payload["require_window"] = dispatch_selector.model_dump(by_alias=True)

            result = runner.run(target_macro, initial_vars=initial_vars)

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
                con.print(f"[red]Bus watcher '{watcher.name}' macro failed:[/red] {result.error}")
                if not watcher.continue_on_macro_error:
                    raise RuntimeError(f"Bus watcher '{watcher.name}' stopped after macro failure: {result.error}")

            if watcher.cooldown_ms > 0:
                cooldown_until_ms = now_ms + int(watcher.cooldown_ms)

            if watcher.debounce_ms > 0:
                time.sleep(watcher.debounce_ms / 1000.0)

    finally:
        try:
            it.close()
        except Exception:
            pass

    if event_log_path:
        con.print(f"[dim]Watcher log:[/dim] {event_log_path}")

    return stats

@dataclass
class BusDaemonStats:
    """Aggregated stats for a bus daemon run."""

    watchers: list[str]
    events_seen: int = 0
    macro_runs: int = 0
    macro_failures: int = 0


@dataclass
class _BusWatcherState:
    watcher: BusWatcher
    stats: BusWatcherStats
    pattern: re.Pattern[str] | None
    cooldown_until_ms: int = 0
    recent: dict[str, int] | None = None
    recent_order: list[tuple[str, int]] | None = None

    def __post_init__(self) -> None:
        if self.recent is None:
            self.recent = {}
        if self.recent_order is None:
            self.recent_order = []


def _init_bus_watcher_state(project: Project, watcher: BusWatcher) -> _BusWatcherState:
    if not watcher.enabled:
        raise RuntimeError(f"Bus watcher '{watcher.name}' is disabled")

    if not watcher.dispatch:
        if not watcher.macro:
            raise RuntimeError(f"Bus watcher '{watcher.name}' requires a macro")
        if watcher.macro not in project.macros:
            raise RuntimeError(f"Bus watcher '{watcher.name}' references missing macro '{watcher.macro}'")

    pat = _compile_pattern(watcher.pattern, watcher.flags)
    return _BusWatcherState(watcher=watcher, stats=BusWatcherStats(watcher=watcher.name), pattern=pat)


def run_bus_daemon(
    project: Project,
    *,
    watcher_names: list[str] | None = None,
    console: Console | None = None,
    max_events: int | None = None,
    force_unlink: bool = False,
    reload_event: str | None = None,
    reload_on_signals: bool = False,
) -> BusDaemonStats:
    """Run selected bus watchers in a *single* bus socket loop.

    A UNIX datagram socket path is single-consumer: only one process can bind it.
    Use this daemon when you want multiple watchers from the same project active
    at once.

    Watchers are evaluated in project order. If a watcher sets `consume: true`
    and handles an event, later watchers will not see that event.
    """

    con = console or Console()

    watchers_all = list(project.bus_watchers or [])
    if watcher_names:
        want = set(watcher_names)
        watchers = [w for w in watchers_all if w.name in want]
        missing = [n for n in watcher_names if n not in {w.name for w in watchers_all}]
        if missing:
            available = ", ".join(w.name for w in watchers_all) or "(none)"
            raise KeyError(f"Unknown bus watcher(s): {', '.join(missing)}. Available: {available}")
    else:
        watchers = [w for w in watchers_all if w.enabled]

    if not watchers:
        raise RuntimeError("No enabled bus watchers to run")

    states = [_init_bus_watcher_state(project, w) for w in watchers]

    sock_path = get_bus_socket_path(Path(project.root_dir), configured=project.settings.bus_socket)
    con.print(f"[dim]Bus socket:[/dim] {sock_path}")
    con.print("[dim]Watchers:[/dim] " + ", ".join(st.watcher.name for st in states))

    fdname = os.environ.get("VHK_BUS_FDNAME") or project.settings.bus_fdname
    if fdname:
        con.print(f"[dim]Bus fdname:[/dim] {fdname}")

    it = iter_bus_events(sock_path, force_unlink=force_unlink, fdname=fdname)
    daemon_stats = BusDaemonStats(watchers=[st.watcher.name for st in states])

    # Live reload support
    reload_ev = reload_event if reload_event is not None else project.settings.bus_reload_event
    if reload_ev is not None:
        reload_ev = str(reload_ev).strip() or None

    stop_ev = project.settings.bus_stop_event
    if stop_ev is not None:
        stop_ev = str(stop_ev).strip() or None

    reload_requested: bool = False
    old_handlers: dict[int, object] = {}

    def _request_reload(_signum=None, _frame=None):
        nonlocal reload_requested
        reload_requested = True

    if reload_on_signals:
        # Only the main thread can register signal handlers.
        try:
            for sig_ in (signal.SIGHUP, signal.SIGUSR1):
                old_handlers[sig_] = signal.getsignal(sig_)
                signal.signal(sig_, _request_reload)
        except Exception:
            pass


    try:
        runner = Runner(project=project, console=con)

        def _select_watchers(prj: Project) -> list[BusWatcher]:
            all_ws = list(prj.bus_watchers or [])
            if watcher_names:
                want = set(watcher_names)
                return [w for w in all_ws if w.name in want]
            return [w for w in all_ws if w.enabled]

        def _reload_from_disk(reason: str) -> None:
            nonlocal project, states, runner, daemon_stats, reload_requested
            reload_requested = False
            try:
                new_project = load_project(Path(project.root_dir))
            except Exception as exc:
                con.print(f"[red]Reload failed:[/red] {exc}")
                return

            new_states = None
            try:
                new_watchers = _select_watchers(new_project)
                if not new_watchers:
                    raise RuntimeError('No enabled bus watchers after reload')
                new_states = [_init_bus_watcher_state(new_project, w) for w in new_watchers]
            except Exception as exc:
                con.print(f"[red]Reload failed:[/red] invalid bus watcher config: {exc}")
                return

            new_sock_path = get_bus_socket_path(Path(new_project.root_dir), configured=new_project.settings.bus_socket)
            if new_sock_path != sock_path:
                con.print(f"[yellow]Reload note:[/yellow] bus_socket changed to {new_sock_path}; restart busd to rebind")

            project = new_project
            states = new_states
            runner = Runner(project=project, console=con)
            daemon_stats.watchers = [st.watcher.name for st in states]
            con.print(f"[green]Reloaded[/green] ({reason}). Watchers: {', '.join(daemon_stats.watchers)}")

        if reload_ev:
            con.print(f"[dim]Reload event:[/dim] {reload_ev} (emit on the bus to reload)")
        if stop_ev:
            con.print(f"[dim]Stop event:[/dim] {stop_ev} (emit on the bus to stop)")
        if reload_on_signals:
            con.print('[dim]Reload signals:[/dim] SIGUSR1 or SIGHUP (when supported)')

        while max_events is None or daemon_stats.events_seen < max_events:
            ev = next(it)
            daemon_stats.events_seen += 1

            if reload_requested:
                _reload_from_disk('signal')

            if reload_ev and ev.name == reload_ev:
                _reload_from_disk(f"bus:{reload_ev}")
                continue

            if stop_ev and ev.name == stop_ev:
                con.print(f"[yellow]Stop requested[/yellow] ({stop_ev}). Exiting busd loop.")
                break

            txt = _event_text(ev)
            sig = hashlib.sha256((ev.name + "\n" + txt).encode("utf-8", errors="replace")).hexdigest()
            now_ms = int(time.time() * 1000.0)

            for st in states:
                watcher = st.watcher
                stats = st.stats
                stats.events_seen += 1

                base_payload: dict[str, Any] = {
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    "watcher": watcher.name,
                    "macro": watcher.macro,
                    "bus_event": ev.name,
                    "text_len": len(txt),
                    "sha256": sig,
                    "preview": _preview(txt),
                }

                want_event = (watcher.event or "*").strip()
                if want_event != "*" and ev.name != want_event:
                    stats.skipped_wrong_event += 1
                    base_payload.update({"action": "skip_wrong_event", "want_event": want_event})
                    _write_event(project, watcher, base_payload)
                    continue

                if watcher.cooldown_ms > 0 and now_ms < st.cooldown_until_ms:
                    stats.skipped_cooldown += 1
                    base_payload.update(
                        {
                            "action": "skip_cooldown",
                            "cooldown_ms": watcher.cooldown_ms,
                            "cooldown_until_ms": st.cooldown_until_ms,
                        }
                    )
                    _write_event(project, watcher, base_payload)
                    continue

                if watcher.dedupe and watcher.dedupe_window_ms > 0:
                    assert st.recent is not None
                    assert st.recent_order is not None
                    last_ms = st.recent.get(sig)
                    if last_ms is not None and (now_ms - last_ms) < watcher.dedupe_window_ms:
                        stats.skipped_duplicate_window += 1
                        base_payload.update({"action": "skip_duplicate_window", "dedupe_window_ms": watcher.dedupe_window_ms})
                        _write_event(project, watcher, base_payload)
                        continue

                    if watcher.dedupe_max_entries > 0:
                        st.recent[sig] = now_ms
                        st.recent_order.append((sig, now_ms))
                        while len(st.recent_order) > watcher.dedupe_max_entries:
                            old_sig, old_ts = st.recent_order.pop(0)
                            if st.recent.get(old_sig) == old_ts:
                                st.recent.pop(old_sig, None)

                active_info: dict[str, Any] | None = None
                active_wm: str | None = None

                if watcher.when is not None:
                    try:
                        info, wm = get_active_window_info()
                        active_info, active_wm = info, wm
                        if not selector_matches_info(watcher.when, info, wm):
                            stats.skipped_nonmatching += 1
                            base_payload.update({"action": "skip_nonmatching", "when": watcher.when.model_dump(by_alias=True)})
                            _write_event(project, watcher, base_payload)
                            continue
                    except Exception as exc:
                        stats.skipped_nonmatching += 1
                        base_payload.update({"action": "skip_nonmatching", "error": str(exc), "when": watcher.when.model_dump(by_alias=True)})
                        _write_event(project, watcher, base_payload)
                        continue

                match = st.pattern.search(txt) if st.pattern else None
                if st.pattern and not match:
                    stats.skipped_nonmatching += 1
                    base_payload.update({"action": "skip_nonmatching", "pattern": watcher.pattern})
                    _write_event(project, watcher, base_payload)
                    continue

                target_macro: str | None = watcher.macro
                dispatch_vars: dict[str, Any] = {}
                dispatch_selector: I3WindowSelector | None = None
                dispatch_binding: str | None = None
                dispatch_keys: str | None = None

                if watcher.dispatch:
                    if not isinstance(ev.data, dict):
                        stats.skipped_dispatch_invalid += 1
                        base_payload.update({"action": "skip_dispatch_invalid", "reason": "data_not_object"})
                        _write_event(project, watcher, base_payload)
                        continue

                    macro_key = (watcher.dispatch_macro_key or "macro").strip() or "macro"
                    vars_key = (watcher.dispatch_vars_key or "vars").strip() or "vars"
                    rw_key = (watcher.dispatch_require_window_key or "require_window").strip() or "require_window"
                    bind_key = (watcher.dispatch_binding_key or "binding").strip() or "binding"
                    keys_key = (watcher.dispatch_keys_key or "keys").strip() or "keys"

                    target_macro = ev.data.get(macro_key)
                    if target_macro is not None:
                        target_macro = str(target_macro)

                    raw_vars = ev.data.get(vars_key)
                    if isinstance(raw_vars, dict):
                        dispatch_vars = dict(raw_vars)

                    bind_raw = ev.data.get(bind_key)
                    dispatch_binding = str(bind_raw) if bind_raw is not None else None
                    keys_raw = ev.data.get(keys_key)
                    dispatch_keys = str(keys_raw) if keys_raw is not None else None

                    raw_selector = ev.data.get(rw_key)
                    if isinstance(raw_selector, dict):
                        try:
                            dispatch_selector = I3WindowSelector.model_validate(raw_selector)
                        except Exception:
                            dispatch_selector = None

                    if not target_macro:
                        stats.skipped_dispatch_invalid += 1
                        base_payload.update({"action": "skip_dispatch_invalid", "reason": "missing_macro"})
                        _write_event(project, watcher, base_payload)
                        continue

                    if watcher.dispatch_allowed_macros is not None and target_macro not in watcher.dispatch_allowed_macros:
                        stats.skipped_disallowed_macro += 1
                        base_payload.update({"action": "skip_disallowed_macro", "target_macro": target_macro})
                        _write_event(project, watcher, base_payload)
                        continue

                    if target_macro not in project.macros:
                        stats.macro_failures += 1
                        daemon_stats.macro_failures += 1
                        base_payload.update({"action": "dispatch_missing_macro", "target_macro": target_macro})
                        _write_event(project, watcher, base_payload)
                        con.print(f"[red]Bus dispatch macro not found:[/red] {target_macro}")
                        if not watcher.continue_on_macro_error:
                            raise RuntimeError(f"Bus watcher '{watcher.name}' stopped: dispatch macro not found: {target_macro}")
                        continue

                    if dispatch_selector is not None:
                        try:
                            info, wm = get_active_window_info()
                            active_info, active_wm = info, wm
                            if not selector_matches_info(dispatch_selector, info, wm):
                                stats.skipped_nonmatching += 1
                                base_payload.update({"action": "skip_nonmatching", "require_window": dispatch_selector.model_dump(by_alias=True)})
                                _write_event(project, watcher, base_payload)
                                continue
                        except Exception as exc:
                            stats.skipped_nonmatching += 1
                            base_payload.update({"action": "skip_nonmatching", "error": str(exc), "require_window": dispatch_selector.model_dump(by_alias=True)})
                            _write_event(project, watcher, base_payload)
                            continue

                assert target_macro is not None

                if watcher.debounce_ms > 0:
                    time.sleep(watcher.debounce_ms / 1000.0)

                initial_vars: dict[str, Any] = {
                    **(
                        {
                            "wm": active_wm,
                            "window": active_info,
                            "window_title": (active_info or {}).get("title"),
                            "window_class": (active_info or {}).get("class") or (active_info or {}).get("app_id"),
                            "workspace": (active_info or {}).get("workspace"),
                            "urgent": (active_info or {}).get("urgent"),
                        }
                        if active_info is not None
                        else {}
                    ),
                    "bus_event": ev.name,
                    "bus_data": ev.data,
                    "bus_text": txt,
                    "watcher_name": watcher.name,
                }
                initial_vars.update(watcher.vars)

                if watcher.dispatch:
                    initial_vars.update({"dispatch_macro": target_macro, "dispatch_binding": dispatch_binding, "dispatch_keys": dispatch_keys})
                    initial_vars.update(dispatch_vars)

                if match is not None:
                    initial_vars["bus_match"] = match.group(0)
                    initial_vars["bus_groups"] = list(match.groups())
                    initial_vars["bus_groupdict"] = match.groupdict()
                    base_payload["pattern"] = watcher.pattern
                    base_payload["match"] = match.group(0)

                base_payload["macro"] = target_macro
                if watcher.dispatch:
                    base_payload["dispatch"] = True
                    if dispatch_binding is not None:
                        base_payload["binding"] = dispatch_binding
                    if dispatch_keys is not None:
                        base_payload["keys"] = dispatch_keys
                    if dispatch_selector is not None:
                        base_payload["require_window"] = dispatch_selector.model_dump(by_alias=True)

                result = runner.run(target_macro, initial_vars=initial_vars)

                base_payload.update({"action": "run_macro", "ok": bool(result.ok), "event_log": result.event_log, "error": result.error})
                _write_event(project, watcher, base_payload)

                if result.ok:
                    stats.macro_runs += 1
                    daemon_stats.macro_runs += 1
                else:
                    stats.macro_failures += 1
                    daemon_stats.macro_failures += 1
                    con.print(f"[red]Bus watcher '{watcher.name}' macro failed:[/red] {result.error}")
                    if not watcher.continue_on_macro_error:
                        raise RuntimeError(f"Bus watcher '{watcher.name}' stopped after macro failure: {result.error}")

                if watcher.cooldown_ms > 0:
                    st.cooldown_until_ms = now_ms + int(watcher.cooldown_ms)

                if getattr(watcher, "consume", False):
                    break

    finally:
        # Restore previous signal handlers if we installed any.
        if old_handlers:
            try:
                for sig_, handler in old_handlers.items():
                    signal.signal(sig_, handler)
            except Exception:
                pass

        try:
            it.close()
        except Exception:
            pass

    return daemon_stats
