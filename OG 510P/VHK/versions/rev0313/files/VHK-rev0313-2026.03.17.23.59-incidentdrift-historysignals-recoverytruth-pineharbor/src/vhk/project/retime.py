from __future__ import annotations

"""Macro retiming utilities.

Why this exists
--------------
Macro ecosystems routinely offer a way to adjust playback speed without
rewriting the whole workflow. For example, tools built on AutoHotkey expose
global key/mouse delay settings, and GUI macro recorders often offer speed
multipliers ("2x", "0.5x") for recorded pauses.

VHK already has a runtime "turbo" profile that scales *incidental* per-step
delays. However, macros recorded in the wild also contain explicit Delay and
RandomWait steps. Retiming is a post-processing pass to scale those explicit
timing steps (and optionally a few other delay-like fields) in a repeatable,
auditable way.

This module is intentionally side-effect free.
"""

from dataclasses import dataclass
import re
from typing import Any


Step = dict[str, Any]


@dataclass(frozen=True)
class RetimeStats:
    in_steps: int
    out_steps: int

    scaled_delay_steps: int
    scaled_random_waits: int
    scaled_step_delays: int
    scaled_retry_delays: int
    scaled_type_delays: int
    scaled_timeouts: int
    scaled_polling: int

    skipped_non_numeric: int


_RE_NUM = re.compile(r"^-?\d+(?:\.\d+)?$")


def _as_number(v: Any) -> float | None:
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        s = v.strip()
        if _RE_NUM.match(s):
            try:
                return float(s)
            except Exception:
                return None
    return None


def _scale_ms(
    value: Any,
    *,
    factor: float,
    min_ms: int | None,
    max_ms: int | None,
) -> tuple[Any, bool]:
    """Scale a delay-like field value.

    Returns
    -------
    (new_value, changed)
    """

    num = _as_number(value)
    if num is None:
        return value, False
    scaled = int(round(num * float(factor)))
    if min_ms is not None:
        scaled = max(int(min_ms), scaled)
    if max_ms is not None:
        scaled = min(int(max_ms), scaled)
    return scaled, (scaled != value)


_NESTED_STEP_KEYS = {"steps", "then_steps", "else_steps", "catch_steps", "finally_steps"}


def retime_steps(
    steps: list[Step],
    *,
    factor: float = 1.0,
    min_ms: int | None = None,
    max_ms: int | None = None,
    include_step_delay: bool = True,
    include_retry_delay: bool = True,
    include_type_delay: bool = True,
    include_timeouts: bool = False,
    include_polling: bool = False,
) -> tuple[list[Step], RetimeStats]:
    """Return a retimed copy of a step list.

    Notes
    -----
    - By default we only scale *delay-like* fields and leave wait timeouts
      unchanged. Shortening timeouts can make otherwise-correct macros flaky.
    - String-valued delays are scaled only if they are purely numeric (e.g.
      "250"). Interpolated expressions like "${foo_ms}" are left untouched.
    """

    scaled_delay_steps = 0
    scaled_random_waits = 0
    scaled_step_delays = 0
    scaled_retry_delays = 0
    scaled_type_delays = 0
    scaled_timeouts = 0
    scaled_polling = 0
    skipped_non_numeric = 0

    def retime_step(step: Step) -> Step:
        nonlocal scaled_delay_steps
        nonlocal scaled_random_waits
        nonlocal scaled_step_delays
        nonlocal scaled_retry_delays
        nonlocal scaled_type_delays
        nonlocal scaled_timeouts
        nonlocal scaled_polling
        nonlocal skipped_non_numeric

        st = dict(step)

        # Recurse into nested step blocks.
        for k in _NESTED_STEP_KEYS:
            if k in st and isinstance(st.get(k), list):
                st[k] = [retime_step(x) if isinstance(x, dict) else x for x in st[k]]

        t = str(st.get("type") or "")

        # Explicit delays.
        if t == "Delay" and "ms" in st:
            new_v, changed = _scale_ms(st.get("ms"), factor=factor, min_ms=min_ms, max_ms=max_ms)
            if _as_number(st.get("ms")) is None:
                skipped_non_numeric += 1
            st["ms"] = new_v
            if changed:
                scaled_delay_steps += 1

        if t == "RandomWait" and "min_ms" in st and "max_ms" in st:
            min_v0 = st.get("min_ms")
            max_v0 = st.get("max_ms")
            new_min, ch_min = _scale_ms(min_v0, factor=factor, min_ms=min_ms, max_ms=max_ms)
            new_max, ch_max = _scale_ms(max_v0, factor=factor, min_ms=min_ms, max_ms=max_ms)
            if _as_number(min_v0) is None:
                skipped_non_numeric += 1
            if _as_number(max_v0) is None:
                skipped_non_numeric += 1
            # Keep sane ordering.
            try:
                if isinstance(new_min, int) and isinstance(new_max, int) and new_min > new_max:
                    new_max = new_min
            except Exception:
                pass
            st["min_ms"] = new_min
            st["max_ms"] = new_max
            if ch_min or ch_max:
                scaled_random_waits += 1

        # PMC-style per-step delay knobs.
        if include_step_delay and isinstance(st.get("delay_ms"), int):
            v0 = st.get("delay_ms")
            new_v, changed = _scale_ms(v0, factor=factor, min_ms=min_ms, max_ms=max_ms)
            st["delay_ms"] = int(new_v)
            if changed:
                scaled_step_delays += 1

        # Retry delays.
        if include_retry_delay and isinstance(st.get("retry_delay_ms"), int):
            v0 = st.get("retry_delay_ms")
            new_v, changed = _scale_ms(v0, factor=factor, min_ms=min_ms, max_ms=max_ms)
            st["retry_delay_ms"] = int(new_v)
            if changed:
                scaled_retry_delays += 1

        # Text typing delays.
        if include_type_delay and t == "TypeText" and isinstance(st.get("delay_ms_per_char"), int):
            v0 = st.get("delay_ms_per_char")
            new_v, changed = _scale_ms(v0, factor=factor, min_ms=min_ms, max_ms=max_ms)
            st["delay_ms_per_char"] = int(new_v)
            if changed:
                scaled_type_delays += 1

        # Timeouts/polling knobs (off by default).
        if include_timeouts and isinstance(st.get("timeout_ms"), int):
            v0 = st.get("timeout_ms")
            new_v, changed = _scale_ms(v0, factor=factor, min_ms=min_ms, max_ms=max_ms)
            st["timeout_ms"] = int(new_v)
            if changed:
                scaled_timeouts += 1

        if include_polling:
            for key in ("poll_ms", "max_poll_ms", "jitter_ms"):
                if isinstance(st.get(key), int):
                    v0 = st.get(key)
                    new_v, changed = _scale_ms(v0, factor=factor, min_ms=min_ms, max_ms=max_ms)
                    st[key] = int(new_v)
                    if changed:
                        scaled_polling += 1

        return st

    out_steps: list[Step] = []
    for st in steps:
        if isinstance(st, dict):
            out_steps.append(retime_step(st))
        else:
            out_steps.append(st)

    stats = RetimeStats(
        in_steps=len(steps),
        out_steps=len(out_steps),
        scaled_delay_steps=scaled_delay_steps,
        scaled_random_waits=scaled_random_waits,
        scaled_step_delays=scaled_step_delays,
        scaled_retry_delays=scaled_retry_delays,
        scaled_type_delays=scaled_type_delays,
        scaled_timeouts=scaled_timeouts,
        scaled_polling=scaled_polling,
        skipped_non_numeric=skipped_non_numeric,
    )
    return out_steps, stats
