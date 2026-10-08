from __future__ import annotations

"""Macro post-processor / optimizer.

Why this exists
--------------
VHK intentionally ships a baseline lexical recorder on X11 (see `vhk record-x11`).
Like other macro recorders (xmacrorec, Pulover's Macro Creator, etc.), raw
recordings tend to contain:

- lots of tiny mouse motion events
- redundant moves to the same coordinates
- key down/up pairs that are more readable as a single key chord
- delay fragments that are easier to reason about when merged

This module provides a *pure* (side-effect free) transformer that converts a
step list into a more compact representation.

The goal is "authoring ergonomics" rather than semantic perfection.
Optimization is conservative by default; profiles allow more aggressive
changes when users explicitly opt in.
"""

from dataclasses import dataclass
from typing import Any, Iterable


Step = dict[str, Any]


@dataclass(frozen=True)
class OptimizeStats:
    in_steps: int
    out_steps: int
    merged_delays: int
    removed_mouse_moves: int
    compressed_key_presses: int
    compressed_chords: int
    compressed_clicks: int
    compressed_text_runs: int
    compressed_text_chars: int


def _is_delay(step: Step) -> bool:
    return step.get("type") == "Delay" and isinstance(step.get("ms"), (int, float))


def _delay_ms(step: Step) -> int:
    try:
        return int(step.get("ms") or 0)
    except Exception:
        return 0


def _is_mouse_move(step: Step) -> bool:
    return step.get("type") == "MouseMove" and ("x" in step and "y" in step)


def _mouse_xy(step: Step) -> tuple[int, int] | None:
    try:
        if not _is_mouse_move(step):
            return None
        return int(step.get("x")), int(step.get("y"))
    except Exception:
        return None


def _is_mouse_click(step: Step) -> bool:
    return step.get("type") == "MouseClick"


def _click_button(step: Step) -> int | None:
    if not _is_mouse_click(step):
        return None
    try:
        b = step.get("button")
        return int(b)
    except Exception:
        return None


def _is_key_down(step: Step) -> bool:
    return step.get("type") == "KeyDown" and isinstance(step.get("key"), str)


def _is_key_up(step: Step) -> bool:
    return step.get("type") == "KeyUp" and isinstance(step.get("key"), str)


def _is_modifier(key: str) -> bool:
    return key in {"ctrl", "shift", "alt", "logo"}


_MOD_ORDER = {"ctrl": 1, "shift": 2, "alt": 3, "logo": 4}


def _format_chord(mods: Iterable[str], main: str) -> str:
    ordered = sorted(set(mods), key=lambda k: (_MOD_ORDER.get(k, 99), k))
    if ordered:
        return "+".join([*ordered, main])
    return main


def _merge_delays(steps: list[Step]) -> tuple[list[Step], int]:
    out: list[Step] = []
    merged = 0
    acc = 0

    def flush() -> None:
        nonlocal acc
        if acc > 0:
            out.append({"type": "Delay", "ms": acc})
        acc = 0

    for st in steps:
        if _is_delay(st):
            ms = _delay_ms(st)
            if ms <= 0:
                # Drop zero delays.
                continue
            if acc > 0:
                merged += 1
            acc += ms
            continue
        flush()
        out.append(st)

    flush()
    return out, merged


def _cap_delays(steps: list[Step], *, cap_delay_ms: int | None) -> list[Step]:
    if cap_delay_ms is None:
        return steps
    out: list[Step] = []
    for st in steps:
        if _is_delay(st):
            ms = _delay_ms(st)
            out.append({"type": "Delay", "ms": min(ms, int(cap_delay_ms))})
        else:
            out.append(st)
    return out


def _squash_mouse_moves(steps: list[Step]) -> tuple[list[Step], int]:
    """Remove redundant consecutive mouse moves.

    We keep the *last* move in any run of MouseMove steps, because it is the
    closest to the user's intent (e.g., right before a click).
    """

    out: list[Step] = []
    removed = 0
    i = 0
    while i < len(steps):
        st = steps[i]
        if _is_mouse_move(st):
            j = i
            last = st
            while j + 1 < len(steps) and _is_mouse_move(steps[j + 1]) and _mouse_xy(steps[j + 1]) is not None:
                nxt = steps[j + 1]
                last = nxt
                j += 1
            if j > i:
                removed += (j - i)
            out.append(last)
            i = j + 1
            continue
        out.append(st)
        i += 1
    return out, removed


def _compress_clicks(
    steps: list[Step],
    *,
    max_click_hold_ms: int = 250,
    pos_tolerance_px: int = 2,
) -> tuple[list[Step], int]:
    """Collapse MouseMove + down/up click sequences into MouseClickAt.

    The X11 recorder emits:
      MouseMove(x,y), MouseClick(down), ... MouseMove(x,y), MouseClick(up)

    For a simple click (short hold and near-identical coordinates), we emit a
    single MouseClickAt step.
    """

    out: list[Step] = []
    compressed = 0
    i = 0

    def near(a: tuple[int, int], b: tuple[int, int]) -> bool:
        return abs(a[0] - b[0]) <= pos_tolerance_px and abs(a[1] - b[1]) <= pos_tolerance_px

    while i < len(steps):
        st = steps[i]
        xy = _mouse_xy(st)
        if xy and i + 1 < len(steps) and _is_mouse_click(steps[i + 1]) and steps[i + 1].get("down") is True:
            btn = _click_button(steps[i + 1])
            if btn is None:
                out.append(st)
                i += 1
                continue
            j = i + 2
            hold_ms = 0
            # Optional delay between down and up.
            while j < len(steps) and _is_delay(steps[j]):
                hold_ms += _delay_ms(steps[j])
                j += 1
            xy2 = None
            if j < len(steps) and _mouse_xy(steps[j]) is not None:
                xy2 = _mouse_xy(steps[j])
                j += 1
            if (
                j < len(steps)
                and _is_mouse_click(steps[j])
                and steps[j].get("up") is True
                and _click_button(steps[j]) == btn
                and hold_ms <= max_click_hold_ms
                and (xy2 is None or near(xy, xy2))
            ):
                out.append({"type": "MouseClickAt", "x": xy[0], "y": xy[1], "button": btn})
                compressed += 1
                i = j + 1
                continue
        out.append(st)
        i += 1
    return out, compressed


def _compress_keys(
    steps: list[Step],
    *,
    max_keypress_gap_ms: int = 250,
    max_chord_gap_ms: int = 250,
) -> tuple[list[Step], int, int]:
    """Compress KeyDown/KeyUp sequences.

    - KeyDown(a) + (Delay<=gap) + KeyUp(a) => Key("a")
    - Modifiers held around a key => Key("ctrl+shift+x")
    """

    out: list[Step] = []
    key_presses = 0
    chords = 0
    i = 0
    while i < len(steps):
        st = steps[i]
        if not _is_key_down(st):
            out.append(st)
            i += 1
            continue

        # Attempt chord pattern.
        mods: list[str] = []
        j = i
        gap_ms = 0
        while j < len(steps) and _is_key_down(steps[j]) and _is_modifier(str(steps[j].get("key"))):
            mods.append(str(steps[j].get("key")))
            j += 1
            while j < len(steps) and _is_delay(steps[j]) and gap_ms <= max_chord_gap_ms:
                gap_ms += _delay_ms(steps[j])
                j += 1

        # Now expect a main KeyDown.
        if j < len(steps) and _is_key_down(steps[j]) and not _is_modifier(str(steps[j].get("key"))):
            main = str(steps[j].get("key"))
            j += 1
            while j < len(steps) and _is_delay(steps[j]) and gap_ms <= max_chord_gap_ms:
                gap_ms += _delay_ms(steps[j])
                j += 1
            if j < len(steps) and _is_key_up(steps[j]) and str(steps[j].get("key")) == main and gap_ms <= max_chord_gap_ms:
                j += 1
                while j < len(steps) and _is_delay(steps[j]) and gap_ms <= max_chord_gap_ms:
                    gap_ms += _delay_ms(steps[j])
                    j += 1
                # Expect KeyUp for modifiers (order not guaranteed by recorder, but typically reverse).
                remaining = list(mods)
                while remaining and j < len(steps) and _is_key_up(steps[j]) and str(steps[j].get("key")) in remaining and gap_ms <= max_chord_gap_ms:
                    remaining.remove(str(steps[j].get("key")))
                    j += 1
                    while j < len(steps) and _is_delay(steps[j]) and gap_ms <= max_chord_gap_ms:
                        gap_ms += _delay_ms(steps[j])
                        j += 1
                if not remaining:
                    out.append({"type": "Key", "keys": _format_chord(mods, main)})
                    chords += 1
                    i = j
                    continue

        # Attempt simple keypress.
        k = str(st.get("key"))
        j = i + 1
        gap_ms = 0
        while j < len(steps) and _is_delay(steps[j]) and gap_ms <= max_keypress_gap_ms:
            gap_ms += _delay_ms(steps[j])
            j += 1
        if j < len(steps) and _is_key_up(steps[j]) and str(steps[j].get("key")) == k and gap_ms <= max_keypress_gap_ms:
            out.append({"type": "Key", "keys": k})
            key_presses += 1
            i = j + 1
            continue

        # Fallback: keep as-is.
        out.append(st)
        i += 1
    return out, key_presses, chords


_TEXT_KEY_TO_CHAR: dict[str, str] = {
    "space": " ",
    "tab": "\t",
}


def _key_to_text_char(keys: str) -> str | None:
    """Return a character for a Key(keys=...) step if it represents plain text.

    We keep this intentionally conservative:
    - no chords (no '+')
    - single-character keys are treated as literal characters
    - allow a small set of named keys (space, tab)
    """

    if not keys or "+" in keys:
        return None
    if len(keys) == 1:
        return keys
    return _TEXT_KEY_TO_CHAR.get(keys)


def _compress_text_runs(
    steps: list[Step],
    *,
    max_text_gap_ms: int = 250,
    min_run: int = 3,
) -> tuple[list[Step], int, int]:
    """Collapse consecutive plain-text `Key` steps into `TypeText`.

    Many macro tools treat a rapid stream of individual key presses as "insert
    text" rather than hundreds of discrete key events. This pass is optional
    because some workflows rely on per-key semantics (games, key hooks, etc.).

    We only combine steps when:
    - keys represent plain characters (no modifiers/chords)
    - inter-key delays are short (<= max_text_gap_ms)
    """

    out: list[Step] = []
    runs = 0
    chars_total = 0
    i = 0

    def base_fields(first: Step) -> dict[str, Any]:
        # Preserve common StepBase knobs if present.
        keep = {
            "enabled",
            "comment",
            "delay_ms",
            "repeat",
            "retry_count",
            "retry_delay_ms",
            "retry_backoff",
            "continue_on_error",
            "clearmodifiers",
        }
        return {k: v for k, v in first.items() if k in keep}

    while i < len(steps):
        st = steps[i]
        if st.get("type") != "Key" or not isinstance(st.get("keys"), str):
            out.append(st)
            i += 1
            continue

        first_key = str(st.get("keys"))
        first_char = _key_to_text_char(first_key)
        if first_char is None:
            out.append(st)
            i += 1
            continue

        chars: list[str] = [first_char]
        delays_between: list[int] = []
        j = i + 1
        while j + 1 < len(steps) and _is_delay(steps[j]) and steps[j + 1].get("type") == "Key":
            gap = _delay_ms(steps[j])
            if gap > max_text_gap_ms:
                break
            nxt = steps[j + 1]
            keys2 = nxt.get("keys")
            if not isinstance(keys2, str):
                break
            ch2 = _key_to_text_char(keys2)
            if ch2 is None:
                break
            delays_between.append(gap)
            chars.append(ch2)
            j += 2

        if len(chars) < min_run:
            out.append(st)
            i += 1
            continue

        delay_ms_per_char = 0
        if delays_between:
            delay_ms_per_char = int(round(sum(delays_between) / float(len(delays_between))))

        merged = {
            "type": "TypeText",
            "text": "".join(chars),
            "delay_ms_per_char": delay_ms_per_char,
            # Prefer native typing to preserve per-char key semantics.
            "backend": "native",
        }
        merged.update(base_fields(st))
        out.append(merged)

        runs += 1
        chars_total += len(chars)
        i = j
    return out, runs, chars_total


def optimize_steps(
    steps: list[Step],
    *,
    profile: str = "balanced",
    cap_delay_ms: int | None = None,
    max_click_hold_ms: int = 250,
    max_keypress_gap_ms: int = 250,
    max_chord_gap_ms: int = 250,
    compress_text: bool | None = None,
    max_text_gap_ms: int = 250,
    min_text_run: int = 3,
) -> tuple[list[Step], OptimizeStats]:
    """Optimize a step list and return (optimized_steps, stats)."""

    if profile not in {"safe", "balanced", "aggressive"}:
        raise ValueError("profile must be one of: safe|balanced|aggressive")

    # Defensive copy of dicts (callers might reuse them).
    cur: list[Step] = [dict(s) for s in steps]

    merged_delays = 0
    removed_moves = 0
    compressed_keys = 0
    compressed_chords = 0
    compressed_clicks = 0
    compressed_text_runs = 0
    compressed_text_chars = 0

    # Pass 1: merge consecutive Delay fragments.
    cur, merged_delays = _merge_delays(cur)

    # Pass 2: remove redundant mouse move runs.
    if profile in {"balanced", "aggressive"}:
        cur, removed_moves = _squash_mouse_moves(cur)

    # Pass 3: compress click sequences.
    if profile in {"balanced", "aggressive"}:
        cur, compressed_clicks = _compress_clicks(cur, max_click_hold_ms=max_click_hold_ms)

    # Pass 4: compress key events.
    if profile in {"balanced", "aggressive"}:
        cur, compressed_keys, compressed_chords = _compress_keys(
            cur,
            max_keypress_gap_ms=max_keypress_gap_ms,
            max_chord_gap_ms=max_chord_gap_ms,
        )

    # Pass 5: optionally collapse text key streams into TypeText.
    if compress_text is None:
        compress_text = (profile == "aggressive")
    if compress_text and profile in {"balanced", "aggressive"}:
        cur, compressed_text_runs, compressed_text_chars = _compress_text_runs(
            cur,
            max_text_gap_ms=max_text_gap_ms,
            min_run=min_text_run,
        )

    # Pass 6: optionally cap delays (aggressive defaults to capping).
    if profile == "aggressive" and cap_delay_ms is None:
        cap_delay_ms = 250
    cur = _cap_delays(cur, cap_delay_ms=cap_delay_ms)

    stats = OptimizeStats(
        in_steps=len(steps),
        out_steps=len(cur),
        merged_delays=merged_delays,
        removed_mouse_moves=removed_moves,
        compressed_key_presses=compressed_keys,
        compressed_chords=compressed_chords,
        compressed_clicks=compressed_clicks,
        compressed_text_runs=compressed_text_runs,
        compressed_text_chars=compressed_text_chars,
    )
    return cur, stats
