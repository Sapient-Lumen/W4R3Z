from __future__ import annotations

"""Macro scaffolding helpers.

This module intentionally creates *non-breaking* edits that help authors
upgrade a raw macro toward more robust patterns.

Principle
---------
Instead of rewriting semantics, we insert disabled "TODO" steps and/or
annotate existing steps with `comment:` hints.

This approach is inspired by how mature automation ecosystems steer authors
away from brittle fixed sleeps and hard-coded coordinates:

- condition-based waits over sleeps
- image/text/window selectors over absolute positions

The inserted steps are disabled by default, so executing the macro is
unchanged until the author opts in.
"""

from dataclasses import dataclass
from typing import Any


Step = dict[str, Any]


@dataclass(frozen=True)
class ScaffoldStats:
    in_steps: int
    out_steps: int
    comments_added: int
    stubs_inserted: int


_NESTED_STEP_FIELDS: tuple[str, ...] = (
    "steps",  # While / Try / ForEach
    "then_steps",
    "else_steps",
    "catch_steps",
    "finally_steps",
)


def _enabled(step: Step) -> bool:
    return bool(step.get("enabled", True))


def _append_comment(step: Step, msg: str) -> bool:
    """Append msg to `comment:`; return True if we changed anything."""

    msg = (msg or "").strip()
    if not msg:
        return False
    cur = step.get("comment")
    if cur is None or not str(cur).strip():
        step["comment"] = msg
        return True
    s = str(cur)
    if msg in s:
        return False
    step["comment"] = s.rstrip() + "\n" + msg
    return True


def scaffold_steps(
    steps: list[Step],
    *,
    warn_long_delay_ms: int = 1500,
    warn_delay_before_action_ms: int = 600,
    warn_low_poll_ms: int = 75,
    insert_stubs: bool = True,
    placeholder_needle_path: str = "assets/TODO.png",
    todo_prefix: str = "TODO:",
) -> tuple[list[Step], ScaffoldStats]:
    """Return a new step list with disabled TODO stubs and/or comments."""

    in_n = len(steps)
    comments_added = 0
    stubs_inserted = 0

    def rec(step_list: list[Step]) -> list[Step]:
        nonlocal comments_added, stubs_inserted

        out: list[Step] = []
        i = 0
        while i < len(step_list):
            st0 = step_list[i]
            st: Step = dict(st0)  # shallow copy; nested lists handled below
            t = str(st.get("type") or "")

            # Recurse into nested step lists.
            for k in _NESTED_STEP_FIELDS:
                v = st.get(k)
                if isinstance(v, list) and all(isinstance(x, dict) for x in v):
                    st[k] = rec(v)  # type: ignore[assignment]

            # Skip disabled steps (often already scaffolds).
            if not _enabled(st):
                out.append(st)
                i += 1
                continue

            def next_enabled(idx: int) -> Step | None:
                j = idx + 1
                while j < len(step_list):
                    cand = step_list[j]
                    if isinstance(cand, dict) and _enabled(cand):
                        return cand
                    j += 1
                return None

            # 1) Delay guidance.
            if t == "Delay" and isinstance(st.get("ms"), (int, float)):
                ms = int(st.get("ms") or 0)
                if ms >= int(warn_long_delay_ms):
                    if _append_comment(
                        st,
                        f"{todo_prefix} Fixed Delay({ms}ms) is brittle. Prefer a condition-based wait (WaitForImage/WaitForText/WaitForWindow/WaitForFile/WaitForFileEvent).",
                    ):
                        comments_added += 1

                    if insert_stubs:
                        out.append(
                            {
                                "type": "WaitForImage",
                                "enabled": False,
                                "needle_path": placeholder_needle_path,
                                "timeout_ms": max(ms, 1000),
                                "comment": (
                                    f"{todo_prefix} Replace Delay({ms}ms) with a real wait. "
                                    "Capture a stable needle of the UI state you need before continuing."
                                ),
                            }
                        )
                        stubs_inserted += 1

                nxt = next_enabled(i)
                if ms >= int(warn_delay_before_action_ms) and nxt is not None:
                    nt = str(nxt.get("type") or "")
                    if nt in {"MouseClickAt", "MouseClick", "Key", "TypeText", "ClickNeedle", "FocusWindow"}:
                        if _append_comment(
                            st,
                            f"{todo_prefix} This Delay is right before {nt}; consider replacing it with a specific wait for readiness.",
                        ):
                            comments_added += 1

            # 2) Coordinate click guidance.
            if t == "MouseClickAt" and isinstance(st.get("x"), int) and isinstance(st.get("y"), int):
                x, y = int(st.get("x")), int(st.get("y"))
                if _append_comment(
                    st,
                    f"{todo_prefix} Absolute click at ({x},{y}) is fragile. Prefer ClickNeedle (template-match + click point).",
                ):
                    comments_added += 1
                if insert_stubs:
                    out.append(
                        {
                            "type": "ClickNeedle",
                            "enabled": False,
                            "needle_path": placeholder_needle_path,
                            "button": st.get("button", 1),
                            "clearmodifiers": bool(st.get("clearmodifiers", False)),
                            "comment": (
                                f"{todo_prefix} Capture a needle of the element you intended to click at ({x},{y}), "
                                "then enable this step and delete/disable the MouseClickAt."
                            ),
                        }
                    )
                    stubs_inserted += 1

            # 3) Missing region guidance.
            if t in {"WaitForImage", "ImageSearch", "WaitForText", "WaitForTextBox", "OcrReadText", "OcrFindText", "OcrFindTextAll", "ClickText", "ClickTextAll", "WaitForRegionChange"}:
                if st.get("region") is None:
                    if _append_comment(
                        st,
                        "TIP: Add a `region:` (smaller searches are faster and reduce false matches). Use `vhk select-region`.",
                    ):
                        comments_added += 1

            # 4) Low polling guidance.
            if t in {
                "WaitForImage",
                "WaitForText",
                "WaitForTextBox",
                "WaitForImageFile",
                "WaitForPixelFile",
                "WaitForClipboardChange",
                "WaitForProcessExit",
                "WaitForFile",
                "WaitForNewFile",
                "WaitForFileEvent",
                "WaitForWindow",
                "WaitForRegionChange",
            }:
                pm = st.get("poll_ms")
                if isinstance(pm, (int, float)) and int(pm) > 0 and int(pm) < int(warn_low_poll_ms):
                    if _append_comment(
                        st,
                        f"TIP: poll_ms={int(pm)}ms is aggressive; consider 100–250ms unless you truly need high frequency.",
                    ):
                        comments_added += 1

            out.append(st)
            i += 1
        return out

    out_steps = rec(steps)
    stats = ScaffoldStats(
        in_steps=in_n,
        out_steps=len(out_steps),
        comments_added=comments_added,
        stubs_inserted=stubs_inserted,
    )
    return out_steps, stats
