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
import re
from typing import Any, Iterable

from vhk.system import input as input_mod


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
    promoted_paste_texts: int
    segmented_paste_texts: int


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
    "enter": "\n",
}

_SHIFTED_TEXT_KEY_TO_CHAR: dict[str, str] = {
    "1": "!",
    "2": "@",
    "3": "#",
    "4": "$",
    "5": "%",
    "6": "^",
    "7": "&",
    "8": "*",
    "9": "(",
    "0": ")",
    "-": "_",
    "=": "+",
    "[": "{",
    "]": "}",
    "\\": "|",
    ";": ":",
    "'": '"',
    ",": "<",
    ".": ">",
    "/": "?",
    "`": "~",
}

_INTERPOLATION_PAT = re.compile(r"\$\{[^}]+\}")


_SEGMENT_PASTE_UNSAFE_FIELDS = {
    "delay_ms",
    "repeat",
    "retry_count",
    "retry_delay_ms",
    "retry_backoff",
    "retry_jitter",
    "retry_jitter_ms",
    "continue_on_error",
}


def _segment_paste_separator_to_key(token: str) -> str | None:
    if token == "\n":
        return "enter"
    if token == "\t":
        return "tab"
    return None



def _key_to_text_char(keys: str) -> str | None:
    """Return a character for a Key(keys=...) step if it represents plain text.

    We keep this intentionally conservative:
    - plain single-key presses still map directly to text
    - `shift+<single-key>` is treated as text when it clearly produces a
      printable uppercase/shifted character
    - chords with non-shift modifiers stay as semantic key actions
    """

    if not keys:
        return None
    if "+" not in keys:
        if len(keys) == 1:
            return keys
        return _TEXT_KEY_TO_CHAR.get(keys)

    parts = [part.strip() for part in keys.split("+") if part.strip()]
    if len(parts) != 2 or parts[0] != "shift":
        return None

    base = parts[1]
    if len(base) == 1 and base.isalpha():
        return base.upper()
    return _SHIFTED_TEXT_KEY_TO_CHAR.get(base)


def _key_to_text_edit(keys: str) -> tuple[str, str | None] | None:
    """Return a text-edit token for a Key(keys=...) step.

    Supported tokens are:
    - ("char", <text>) for printable characters that can be folded into
      TypeText
    - navigation/edit tokens that can be simulated inside one local text run:
      backspace, delete, left, right, home, end, ctrl+backspace, ctrl+delete,
      shift+home, shift+end
    - simple shift-selection motions that stay local to the captured run:
      shift+left, shift+right
    """

    ch = _key_to_text_char(keys)
    if ch is not None:
        return ("char", ch)
    if keys in {
        "backspace",
        "delete",
        "left",
        "right",
        "home",
        "end",
        "ctrl+backspace",
        "ctrl+delete",
        "shift+left",
        "shift+right",
        "shift+home",
        "shift+end",
    }:
        return (keys, None)
    return None


def _selection_bounds(cursor: int, selection_anchor: int | None) -> tuple[int, int] | None:
    if selection_anchor is None or selection_anchor == cursor:
        return None
    return (min(cursor, selection_anchor), max(cursor, selection_anchor))


def _is_word_char(ch: str) -> bool:
    return ch.isalnum() or ch == "_"


def _find_prev_chunk_start(chars: list[str], cursor: int) -> int:
    i = cursor
    while i > 0 and chars[i - 1].isspace():
        i -= 1
    if i <= 0:
        return 0
    if _is_word_char(chars[i - 1]):
        while i > 0 and _is_word_char(chars[i - 1]):
            i -= 1
        return i
    while i > 0 and (not chars[i - 1].isspace()) and (not _is_word_char(chars[i - 1])):
        i -= 1
    return i


def _find_next_chunk_end(chars: list[str], cursor: int) -> int:
    i = cursor
    n = len(chars)
    while i < n and chars[i].isspace():
        i += 1
    if i >= n:
        return n
    if _is_word_char(chars[i]):
        while i < n and _is_word_char(chars[i]):
            i += 1
        return i
    while i < n and (not chars[i].isspace()) and (not _is_word_char(chars[i])):
        i += 1
    return i


def _apply_text_edit(
    chars: list[str],
    cursor: int,
    selection_anchor: int | None,
    kind: str,
    value: str | None,
) -> tuple[int, int | None, bool]:
    """Apply one conservative local text edit.

    Returns (new_cursor, new_selection_anchor, ok). `ok=False` means the edit
    would require state outside the run we have captured, so the optimizer
    should stop folding.
    """

    selected = _selection_bounds(cursor, selection_anchor)

    if kind == "char":
        if selected is not None:
            lo, hi = selected
            del chars[lo:hi]
            cursor = lo
            selection_anchor = None
        text = str(value or "")
        chars.insert(cursor, text)
        return cursor + len(text), None, True

    if kind == "backspace":
        if selected is not None:
            lo, hi = selected
            del chars[lo:hi]
            return lo, None, True
        if cursor <= 0:
            return cursor, selection_anchor, False
        del chars[cursor - 1]
        return cursor - 1, None, True

    if kind == "delete":
        if selected is not None:
            lo, hi = selected
            del chars[lo:hi]
            return lo, None, True
        if cursor >= len(chars):
            return cursor, selection_anchor, False
        del chars[cursor]
        return cursor, None, True

    if kind == "ctrl+backspace":
        if selected is not None:
            lo, hi = selected
            del chars[lo:hi]
            return lo, None, True
        if cursor <= 0:
            return cursor, selection_anchor, False
        start = _find_prev_chunk_start(chars, cursor)
        if start == cursor:
            return cursor, selection_anchor, False
        del chars[start:cursor]
        return start, None, True

    if kind == "ctrl+delete":
        if selected is not None:
            lo, hi = selected
            del chars[lo:hi]
            return lo, None, True
        if cursor >= len(chars):
            return cursor, selection_anchor, False
        end = _find_next_chunk_end(chars, cursor)
        if end == cursor:
            return cursor, selection_anchor, False
        del chars[cursor:end]
        return cursor, None, True

    if kind == "left":
        if selected is not None:
            lo, _ = selected
            return lo, None, True
        if cursor <= 0:
            return cursor, selection_anchor, False
        return cursor - 1, None, True

    if kind == "right":
        if selected is not None:
            _, hi = selected
            return hi, None, True
        if cursor >= len(chars):
            return cursor, selection_anchor, False
        return cursor + 1, None, True

    if kind == "home":
        if cursor == 0 and selected is None:
            return cursor, selection_anchor, False
        return 0, None, True

    if kind == "end":
        if cursor == len(chars) and selected is None:
            return cursor, selection_anchor, False
        return len(chars), None, True

    if kind == "shift+left":
        if cursor <= 0:
            return cursor, selection_anchor, False
        if selection_anchor is None:
            selection_anchor = cursor
        cursor -= 1
        if selection_anchor == cursor:
            selection_anchor = None
        return cursor, selection_anchor, True

    if kind == "shift+right":
        if cursor >= len(chars):
            return cursor, selection_anchor, False
        if selection_anchor is None:
            selection_anchor = cursor
        cursor += 1
        if selection_anchor == cursor:
            selection_anchor = None
        return cursor, selection_anchor, True

    if kind == "shift+home":
        if cursor <= 0:
            return cursor, selection_anchor, False
        if selection_anchor is None:
            selection_anchor = cursor
        cursor = 0
        if selection_anchor == cursor:
            selection_anchor = None
        return cursor, selection_anchor, True

    if kind == "shift+end":
        if cursor >= len(chars):
            return cursor, selection_anchor, False
        if selection_anchor is None:
            selection_anchor = cursor
        cursor = len(chars)
        if selection_anchor == cursor:
            selection_anchor = None
        return cursor, selection_anchor, True

    return cursor, selection_anchor, False


def _promote_paste_friendly_text(
    steps: list[Step],
    *,
    min_chars: int = 80,
) -> tuple[list[Step], int]:
    """Rewrite long literal TypeText steps to explicit clipboard-paste mode.

    This stays conservative on purpose:
    - only literal text (no `${...}` interpolation) is eligible
    - keep Return/Tab typing semantics by skipping text that contains `\n`/`\t`
    - do not touch steps already pinned to clipboard/xvkbd or steps with an
      explicit per-character delay
    """

    promoted = 0
    out: list[Step] = []

    for st in steps:
        if st.get("type") != "TypeText":
            out.append(st)
            continue

        text = st.get("text")
        if not isinstance(text, str):
            out.append(st)
            continue

        backend = str(st.get("backend") or "auto")
        if backend in {"clipboard", "xvkbd"}:
            out.append(st)
            continue

        if int(st.get("delay_ms_per_char") or 0) != 0:
            out.append(st)
            continue

        if len(text) < max(1, int(min_chars)):
            out.append(st)
            continue

        if "\n" in text or "\t" in text:
            out.append(st)
            continue

        if _INTERPOLATION_PAT.search(text):
            out.append(st)
            continue

        if not input_mod.text_looks_paste_friendly(text):
            out.append(st)
            continue

        merged = dict(st)
        merged["backend"] = "clipboard"
        merged.setdefault("selection", "clipboard")
        merged.setdefault("preserve_clipboard", True)
        merged.setdefault("paste_shortcut", "auto")
        existing_comment = str(merged.get("comment") or "").strip()
        note = "optimized for paste-friendly text"
        merged["comment"] = f"{existing_comment}; {note}" if existing_comment else note
        out.append(merged)
        promoted += 1

    return out, promoted


def _segment_paste_friendly_text(
    steps: list[Step],
    *,
    min_chunk_chars: int = 24,
) -> tuple[list[Step], int]:
    """Split structured TypeText runs into hybrid paste + typed separator steps.

    This is intentionally opt-in and conservative. It targets form-like text where
    large literal fields are separated by `Tab`/`Enter` semantics that should
    remain visible as keys.
    """

    segmented = 0
    out: list[Step] = []

    for st in steps:
        if st.get("type") != "TypeText":
            out.append(st)
            continue

        text = st.get("text")
        if not isinstance(text, str):
            out.append(st)
            continue

        backend = str(st.get("backend") or "auto")
        if backend in {"clipboard", "xvkbd"}:
            out.append(st)
            continue

        if int(st.get("delay_ms_per_char") or 0) != 0:
            out.append(st)
            continue

        if "\n" not in text and "\t" not in text:
            out.append(st)
            continue

        if _INTERPOLATION_PAT.search(text):
            out.append(st)
            continue

        if any(name in st for name in _SEGMENT_PASTE_UNSAFE_FIELDS):
            out.append(st)
            continue

        tokens = re.split(r"([\n\t])", text)
        if len(tokens) <= 1:
            out.append(st)
            continue

        pieces: list[Step] = []
        promoted_chunks = 0
        saw_separator = False
        for token in tokens:
            if token == "":
                continue

            separator_key = _segment_paste_separator_to_key(token)
            if separator_key is not None:
                piece: Step = {"type": "Key", "keys": separator_key}
                if bool(st.get("clearmodifiers")):
                    piece["clearmodifiers"] = True
                if "enabled" in st:
                    piece["enabled"] = st.get("enabled")
                pieces.append(piece)
                saw_separator = True
                continue

            chunk_backend = "clipboard" if len(token) >= max(1, int(min_chunk_chars)) and input_mod.text_looks_paste_friendly(token) else "native"
            piece = {
                "type": "TypeText",
                "text": token,
                "backend": chunk_backend,
            }
            if bool(st.get("clearmodifiers")):
                piece["clearmodifiers"] = True
            if "enabled" in st:
                piece["enabled"] = st.get("enabled")
            if chunk_backend == "clipboard":
                piece["selection"] = str(st.get("selection") or "clipboard")
                piece["preserve_clipboard"] = bool(st.get("preserve_clipboard", True))
                piece["paste_shortcut"] = str(st.get("paste_shortcut") or "auto")
                promoted_chunks += 1
            pieces.append(piece)

        if promoted_chunks <= 0 or not saw_separator or not pieces:
            out.append(st)
            continue

        existing_comment = str(st.get("comment") or "").strip()
        note = "optimized into hybrid text/paste lanes"
        pieces[0]["comment"] = f"{existing_comment}; {note}" if existing_comment else note
        out.extend(pieces)
        segmented += 1

    return out, segmented


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
    - keys represent printable text characters (including simple shifted text
      such as `shift+h` -> `H`)
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
        first_edit = _key_to_text_edit(first_key)
        if first_edit is None or first_edit[0] != "char" or first_edit[1] is None:
            out.append(st)
            i += 1
            continue

        chars: list[str] = [str(first_edit[1])]
        cursor = len(chars)
        selection_anchor: int | None = None
        consumed_edits = 1
        delays_between: list[int] = []
        saw_structural_edit = False
        j = i + 1
        while j < len(steps):
            gap = 0
            nxt_index = j
            if _is_delay(steps[j]):
                gap = _delay_ms(steps[j])
                if gap > max_text_gap_ms or (j + 1) >= len(steps):
                    break
                nxt_index = j + 1
            elif j > i + 1:
                # Once a run starts, a bare adjacent Key implies zero extra gap.
                gap = 0
            elif j == i + 1:
                # Allow zero-gap adjacency right after the first Key.
                gap = 0
            else:
                break

            nxt = steps[nxt_index]
            if nxt.get("type") != "Key":
                break
            keys2 = nxt.get("keys")
            if not isinstance(keys2, str):
                break
            edit = _key_to_text_edit(keys2)
            if edit is None:
                break

            kind, value = edit
            next_cursor, selection_anchor, ok = _apply_text_edit(chars, cursor, selection_anchor, kind, value)
            if not ok:
                break
            cursor = next_cursor
            if kind != "char":
                saw_structural_edit = True
            delays_between.append(gap)
            consumed_edits += 1
            j = nxt_index + 1

        if consumed_edits < min_run or not chars or cursor != len(chars) or _selection_bounds(cursor, selection_anchor) is not None:
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
        if saw_structural_edit:
            existing_comment = str(merged.get("comment") or "").strip()
            note = "optimized from edited key stream"
            merged["comment"] = f"{existing_comment}; {note}" if existing_comment else note
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
    promote_paste_text: bool = False,
    paste_text_min_chars: int = 80,
    segment_paste_text: bool = False,
    segment_paste_min_chars: int = 24,
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
    promoted_paste_texts = 0
    segmented_paste_texts = 0

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

    # Pass 6: optionally rewrite long literal TypeText steps to explicit
    # clipboard-paste mode. This is opt-in because typing vs pasting can differ
    # in widget behavior, styling, and clipboard side effects.
    if promote_paste_text:
        cur, promoted_paste_texts = _promote_paste_friendly_text(
            cur,
            min_chars=paste_text_min_chars,
        )

    # Pass 7: optionally split structured text into a hybrid lane where
    # large literal chunks paste through the clipboard while Tab/Enter remain
    # explicit key semantics. This is opt-in for the same reason as paste
    # promotion: widgets differ, and clipboard side effects are real.
    if segment_paste_text:
        cur, segmented_paste_texts = _segment_paste_friendly_text(
            cur,
            min_chunk_chars=segment_paste_min_chars,
        )

    # Pass 8: optionally cap delays (aggressive defaults to capping).
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
        promoted_paste_texts=promoted_paste_texts,
        segmented_paste_texts=segmented_paste_texts,
    )
    return cur, stats
