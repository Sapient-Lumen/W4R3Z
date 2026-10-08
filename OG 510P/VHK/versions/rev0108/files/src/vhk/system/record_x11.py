from __future__ import annotations

"""X11 lexical input recorder (best-effort).

This module intentionally stays "dumb": it records low-level input events and
turns them into a VHK step list. Higher-level "convert recording to robust
steps" tooling belongs in a future studio/GUI.

Design notes
------------
- We use `xinput test-xi2 --root` because it is widely available and can
  observe global XI2 events on the root window. The xinput man page documents
  `test-xi2` and its `--root` mode.
- The output contains keycodes in the `detail:` field; we translate them to
  keysyms using `xmodmap -pke` at record time.

Limitations
-----------
- In Wayland sessions, xinput typically only sees Xwayland devices (if any).
- Complex pointer motion path recording is intentionally out-of-scope here;
  we collapse motion into sampled MouseMove steps and detect simple drags.
"""

import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml


_RE_EVENT_HEADER = re.compile(r"^\s*EVENT\s+type\s+\d+\s+\((?P<name>[^)]+)\)\s*$")
_RE_KV = re.compile(r"^\s*(?P<k>[a-zA-Z_]+):\s*(?P<v>.*)$")


@dataclass(frozen=True)
class Xi2Event:
    ts_ms: float
    name: str
    detail: int | None
    root_x: float | None
    root_y: float | None
    effective_mods: str | None
    raw: dict[str, str]


def _parse_root_xy(value: str) -> tuple[float | None, float | None]:
    # e.g. "1324.55/821.81"
    if "/" not in value:
        return None, None
    a, b = value.split("/", 1)
    try:
        return float(a), float(b)
    except Exception:
        return None, None


def parse_xinput_test_xi2_timed(timed_lines: Iterable[tuple[float, str]]) -> list[Xi2Event]:
    """Parse `xinput test-xi2 --root` output with captured timestamps.

    Parameters
    ----------
    timed_lines:
        An iterable of (ts_ms, line) pairs where ts_ms is a monotonic timestamp
        captured when the line was read from xinput's stdout.
    """

    current_name: str | None = None
    current_ts: float = 0.0
    kv: dict[str, str] = {}
    out: list[Xi2Event] = []

    def flush() -> None:
        nonlocal current_name, kv, current_ts
        if not current_name:
            kv = {}
            return
        detail = None
        if "detail" in kv:
            try:
                detail = int(kv["detail"].strip().split()[0])
            except Exception:
                detail = None
        rx = ry = None
        if "root" in kv:
            rx, ry = _parse_root_xy(kv["root"].strip().split()[0])
        mods = None
        if "modifiers" in kv:
            # e.g. "locked 0x10 latched 0 base 0 effective: 0x10"
            mods = kv["modifiers"].strip()
        out.append(
            Xi2Event(
                ts_ms=current_ts,
                name=current_name,
                detail=detail,
                root_x=rx,
                root_y=ry,
                effective_mods=mods,
                raw=dict(kv),
            )
        )
        current_name = None
        kv = {}

    for ts_ms, raw in timed_lines:
        line = raw.rstrip("\n")
        m = _RE_EVENT_HEADER.match(line)
        if m:
            flush()
            current_name = m.group("name")
            current_ts = float(ts_ms)
            continue
        if not line.strip():
            flush()
            continue
        m2 = _RE_KV.match(line)
        if m2 and current_name:
            k = m2.group("k")
            v = m2.group("v")
            kv[k] = v
            continue

    flush()
    return out


def parse_xinput_test_xi2(lines: Iterable[str]) -> list[Xi2Event]:
    """Parse `xinput test-xi2 --root` output.

    This variant is primarily for unit tests and log parsing where capture-time
    timestamps are unavailable.
    """

    return parse_xinput_test_xi2_timed((0.0, l) for l in lines)


def load_xmodmap_keysyms(*, xmodmap_text: str | None = None) -> dict[int, tuple[str | None, str | None]]:
    """Return keycode -> (unshifted, shifted) keysym mapping from `xmodmap -pke`."""

    if xmodmap_text is None:
        proc = subprocess.run(["xmodmap", "-pke"], capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError((proc.stderr or proc.stdout).strip() or "xmodmap -pke failed")
        xmodmap_text = proc.stdout

    mapping: dict[int, tuple[str | None, str | None]] = {}
    for raw in xmodmap_text.splitlines():
        line = raw.strip()
        if not line.startswith("keycode") or "=" not in line:
            continue
        # Example: keycode  38 = a A a A
        left, right = line.split("=", 1)
        left_parts = left.split()
        if len(left_parts) < 2:
            continue
        try:
            code = int(left_parts[1])
        except Exception:
            continue
        syms = [s for s in right.split() if s and s != "NoSymbol"]
        unshift = syms[0] if len(syms) >= 1 else None
        shift = syms[1] if len(syms) >= 2 else None
        mapping[code] = (unshift, shift)
    return mapping


_KEYSYM_NORMALIZE: dict[str, str] = {
    "Return": "enter",
    "KP_Enter": "enter",
    "Tab": "tab",
    "space": "space",
    "Escape": "esc",
    "BackSpace": "backspace",
    "Delete": "delete",
    "Insert": "insert",
    "Home": "home",
    "End": "end",
    "Prior": "pageup",
    "Next": "pagedown",
    "Left": "left",
    "Right": "right",
    "Up": "up",
    "Down": "down",
    "Control_L": "ctrl",
    "Control_R": "ctrl",
    "Shift_L": "shift",
    "Shift_R": "shift",
    "Alt_L": "alt",
    "Alt_R": "alt",
    "Meta_L": "logo",
    "Meta_R": "logo",
    "Super_L": "logo",
    "Super_R": "logo",
}


def normalize_keysym(keysym: str | None) -> str | None:
    if not keysym:
        return None
    if keysym in _KEYSYM_NORMALIZE:
        return _KEYSYM_NORMALIZE[keysym]
    if len(keysym) == 1:
        return keysym.lower()
    # Common X keysyms come in CamelCase; keep them but normalize underscores.
    return keysym.replace("_", "")


def _is_modifier(key: str) -> bool:
    return key in {"ctrl", "shift", "alt", "logo"}


def events_to_steps(
    events: list[Xi2Event],
    *,
    keysyms: dict[int, tuple[str | None, str | None]],
    min_delay_ms: int = 40,
    mouse_sample_ms: int = 25,
    drag_min_dist: int = 3,
) -> list[dict[str, object]]:
    """Convert XI2 events into a list of VHK step dicts."""

    steps: list[dict[str, object]] = []
    # We'll initialize last_ts after we see the first event timestamp.
    last_ts = 0.0
    last_move_emit = 0.0
    last_move_xy: tuple[int, int] | None = None

    # Drag detection.
    drag_button: int | None = None
    drag_start: tuple[int, int] | None = None
    drag_last: tuple[int, int] | None = None

    def maybe_delay(now_ms: float) -> None:
        nonlocal last_ts
        gap = int(round(now_ms - last_ts))
        if gap >= min_delay_ms:
            steps.append({"type": "Delay", "ms": gap})
        last_ts = now_ms

    # Prefer the explicit `time:` field when present, otherwise use capture ts.
    def event_time_ms(ev: Xi2Event) -> float:
        t = ev.raw.get("time")
        if t:
            try:
                return float(t.split()[0])
            except Exception:
                return float(ev.ts_ms)
        return float(ev.ts_ms)

    # Track currently-held Shift to choose shifted keysyms.
    held_mods: set[str] = set()

    if events:
        last_ts = event_time_ms(events[0])

    for ev in events:
        name = ev.name
        if name.startswith("Raw"):
            # Raw events often duplicate non-raw events. For keyboard, the
            # non-raw events carry modifier interpretation by the server.
            continue
        now_ms = event_time_ms(ev)
        if now_ms < last_ts:
            # Ensure monotonicity.
            now_ms = last_ts
        if name in {"KeyPress", "KeyRelease"}:
            if ev.detail is None:
                continue
            unshift, shift = keysyms.get(ev.detail, (None, None))
            # Prefer the unshifted keysym to better approximate the physical key
            # being pressed. Modifier keys (Shift/Ctrl/Alt/etc.) are recorded as
            # their own keysyms and affect interpretation at playback time.
            ks = unshift or shift
            key = normalize_keysym(ks)
            if not key:
                # Drop unknown keys but leave a breadcrumb.
                maybe_delay(now_ms)
                steps.append({"type": "Log", "message": f"[record-x11] unmapped keycode {ev.detail}"})
                continue

            # Update held modifier state before emitting (helps with Shift keys
            # that map to themselves).
            if _is_modifier(key):
                if name == "KeyPress":
                    held_mods.add(key)
                else:
                    held_mods.discard(key)

            maybe_delay(now_ms)
            steps.append({"type": "KeyDown" if name == "KeyPress" else "KeyUp", "key": key})
            continue

        if name in {"ButtonPress", "ButtonRelease"}:
            if ev.detail is None:
                continue
            x = int(round(ev.root_x or 0.0))
            y = int(round(ev.root_y or 0.0))
            btn = int(ev.detail)

            # Wheel detection (common mapping: 4/5 vertical, 6/7 horizontal)
            if name == "ButtonPress" and btn in {4, 5, 6, 7}:
                maybe_delay(now_ms)
                axis = "vertical" if btn in {4, 5} else "horizontal"
                clicks = 1 if btn in {4, 6} else -1
                steps.append({"type": "MouseWheel", "axis": axis, "clicks": clicks})
                continue
            if name == "ButtonRelease" and btn in {4, 5, 6, 7}:
                # Ignore synthetic wheel releases.
                continue

            if name == "ButtonPress":
                # Candidate drag start.
                drag_button = btn
                drag_start = (x, y)
                drag_last = (x, y)
                maybe_delay(now_ms)
                steps.append({"type": "MouseMove", "x": x, "y": y})
                steps.append({"type": "MouseClick", "button": btn, "down": True})
                continue

            # ButtonRelease
            if drag_button == btn and drag_start and drag_last:
                dx = drag_last[0] - drag_start[0]
                dy = drag_last[1] - drag_start[1]
                dist = abs(dx) + abs(dy)
                if dist >= drag_min_dist:
                    # Replace the press+move sequence with a single MouseDrag.
                    # We keep the initial MouseMove for better determinism.
                    # Find the last two steps which should be move+down.
                    # If the structure doesn't match, we fall back to up.
                    try:
                        if len(steps) >= 2 and steps[-1].get("type") == "MouseClick" and steps[-2].get("type") == "MouseMove":
                            steps.pop()
                            steps.pop()
                            maybe_delay(now_ms)
                            steps.append(
                                {
                                    "type": "MouseDrag",
                                    "x1": drag_start[0],
                                    "y1": drag_start[1],
                                    "x2": drag_last[0],
                                    "y2": drag_last[1],
                                    "button": btn,
                                }
                            )
                            drag_button = None
                            drag_start = None
                            drag_last = None
                            continue
                    except Exception:
                        pass

            maybe_delay(now_ms)
            steps.append({"type": "MouseMove", "x": x, "y": y})
            steps.append({"type": "MouseClick", "button": btn, "up": True})
            drag_button = None
            drag_start = None
            drag_last = None
            continue

        if name == "Motion":
            x = int(round(ev.root_x or 0.0))
            y = int(round(ev.root_y or 0.0))
            # Update drag last point if dragging.
            if drag_button is not None:
                drag_last = (x, y)

            # Sample motion; avoid floods like xmacrorec does.
            if now_ms - last_move_emit < mouse_sample_ms and last_move_xy is not None:
                last_move_xy = (x, y)
                continue
            if last_move_xy == (x, y):
                continue

            maybe_delay(now_ms)
            steps.append({"type": "MouseMove", "x": x, "y": y})
            last_move_emit = now_ms
            last_move_xy = (x, y)
            continue

    return steps


def record_x11_steps(
    *,
    duration_ms: int = 3_000,
    min_delay_ms: int = 40,
    mouse_sample_ms: int = 25,
    drag_min_dist: int = 3,
    stderr_to_console: bool = True,
) -> list[dict[str, object]]:
    """Run `xinput test-xi2 --root` for a short duration and return step dicts."""

    keysyms = load_xmodmap_keysyms()

    cmd = ["xinput", "test-xi2", "--root"]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=None if stderr_to_console else subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )
    assert proc.stdout is not None

    timed_lines: list[tuple[float, str]] = []
    start = time.time()
    try:
        while True:
            if (time.time() - start) * 1000.0 >= float(duration_ms):
                break
            line = proc.stdout.readline()
            if not line:
                time.sleep(0.01)
                continue
            timed_lines.append((time.monotonic() * 1000.0, line))
    finally:
        try:
            proc.terminate()
        except Exception:
            pass
        try:
            proc.wait(timeout=1.0)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

    events = parse_xinput_test_xi2_timed(timed_lines)
    return events_to_steps(
        events,
        keysyms=keysyms,
        min_delay_ms=min_delay_ms,
        mouse_sample_ms=mouse_sample_ms,
        drag_min_dist=drag_min_dist,
    )


def dump_steps_yaml(steps: list[dict[str, object]], *, out_path: Path | None = None) -> str:
    payload = {"steps": steps}
    text = yaml.safe_dump(payload, sort_keys=False)
    if out_path:
        out_path.write_text(text)
    return text
