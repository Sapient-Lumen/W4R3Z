from __future__ import annotations

"""Macro linter / advisor.

This module is intentionally *non-blocking* by default: it surfaces common
"macro recorder" pitfalls (hard sleeps, coordinate clicks, raw down/up noise)
and suggests higher-level, more robust primitives.

It borrows ideas from mature automation ecosystems:
- Prefer condition-based waits over fixed sleeps.
- Prefer stable selectors (window criteria, template matching) over absolute
  pixel coordinates.
"""

from dataclasses import dataclass
import re
from typing import Any, Iterable

from vhk.system import input as input_mod


Step = dict[str, Any]


@dataclass(frozen=True)
class LintIssue:
    severity: str  # info|warning|error
    code: str
    path: str
    message: str
    suggestion: str | None = None
    step_type: str | None = None




_INTERP_PAT = re.compile(r"\$\{[^}]+\}")


def _literal_type_text_candidate(step: Step) -> tuple[str, str] | None:
    if _step_type(step) != "TypeText":
        return None
    text = step.get("text")
    if not isinstance(text, str) or not text:
        return None
    backend = str(step.get("backend") or "auto").strip().lower() or "auto"
    if backend in {"clipboard", "xvkbd"}:
        return None
    if int(step.get("delay_ms_per_char") or 0) != 0:
        return None
    if _INTERP_PAT.search(text):
        return None
    if not input_mod.text_looks_paste_friendly(text):
        return None
    return text, backend


_NESTED_STEP_FIELDS: tuple[str, ...] = (
    "steps",  # While / Try / ForEach
    "then_steps",
    "else_steps",
    "catch_steps",
    "finally_steps",
)


def _enabled(step: Step) -> bool:
    return bool(step.get("enabled", True))


def _step_type(step: Step) -> str:
    t = step.get("type")
    return str(t) if t is not None else ""


def _iter_step_lists(step: Step) -> Iterable[tuple[str, list[Step]]]:
    for k in _NESTED_STEP_FIELDS:
        v = step.get(k)
        if isinstance(v, list) and all(isinstance(x, dict) for x in v):
            # type: ignore[return-value]
            yield k, v  # type: ignore[misc]


def _walk_steps(steps: list[Step], *, prefix: str = "steps") -> Iterable[tuple[Step, str, list[Step], int]]:
    """Yield (step, path, parent_list, index) for all steps (recursive)."""

    for i, st in enumerate(steps):
        path = f"{prefix}[{i}]"
        yield st, path, steps, i
        for field, child in _iter_step_lists(st):
            yield from _walk_steps(child, prefix=f"{path}.{field}")


def _next_enabled(parent: list[Step], start_idx: int) -> Step | None:
    j = start_idx + 1
    while j < len(parent):
        st = parent[j]
        if _enabled(st):
            return st
        j += 1
    return None


def lint_steps(
    steps: list[Step],
    *,
    warn_long_delay_ms: int = 1500,
    warn_delay_before_action_ms: int = 600,
    warn_low_poll_ms: int = 75,
) -> list[LintIssue]:
    """Return a list of best-effort lint issues for a raw step list."""

    warn_long_typed_text_chars = 80
    warn_structured_typed_text_chars = 24

    issues: list[LintIssue] = []

    def add(
        *,
        severity: str,
        code: str,
        path: str,
        message: str,
        suggestion: str | None = None,
        step_type: str | None = None,
    ) -> None:
        issues.append(
            LintIssue(
                severity=severity,
                code=code,
                path=path,
                message=message,
                suggestion=suggestion,
                step_type=step_type,
            )
        )

    # Count raw recorder artifacts (helps suggest vhk optimize).
    raw_key_events = 0
    raw_click_events = 0
    mouse_moves = 0

    for st, path, parent, idx in _walk_steps(steps):
        if not _enabled(st):
            continue
        t = _step_type(st)

        # 1) Hard sleeps (long delays).
        if t == "Delay":
            ms = st.get("ms")
            if isinstance(ms, (int, float)):
                ms_i = int(ms)
                if ms_i >= int(warn_long_delay_ms):
                    add(
                        severity="warning",
                        code="DELAY_LONG",
                        path=path,
                        step_type=t,
                        message=f"Fixed Delay of {ms_i}ms may be brittle (UI timing varies).",
                        suggestion="Prefer a condition-based wait: WaitForImage / WaitForText / WaitForWindow / WaitForFile / WaitForFileEvent.",
                    )

                nxt = _next_enabled(parent, idx)
                if ms_i >= int(warn_delay_before_action_ms) and nxt is not None:
                    nt = _step_type(nxt)
                    if nt in {"MouseClickAt", "MouseClick", "Key", "TypeText", "ClickNeedle", "FocusWindow"}:
                        add(
                            severity="info",
                            code="DELAY_BEFORE_ACTION",
                            path=path,
                            step_type=t,
                            message=f"Delay({ms_i}ms) immediately before {nt} often means 'wait for UI'.",
                            suggestion="Consider replacing the sleep with a specific wait (e.g. WaitForImage/WaitForText) or use ClickNeedle (wait+click).",
                        )

        # 2) Coordinate-based clicks/moves.
        if t == "MouseClickAt":
            x, y = st.get("x"), st.get("y")
            if isinstance(x, int) and isinstance(y, int):
                add(
                    severity="warning",
                    code="COORD_CLICK",
                    path=path,
                    step_type=t,
                    message=f"Absolute click at ({x},{y}) can break when layouts, DPI, or window positions change.",
                    suggestion="Prefer ClickNeedle (template-match + click point) or WaitForImage + click relative to the match.",
                )

        if t == "MouseMove":
            if isinstance(st.get("x"), int) and isinstance(st.get("y"), int):
                mouse_moves += 1

        # 3) Raw down/up noise: suggest running vhk optimize.
        if t in {"KeyDown", "KeyUp"}:
            raw_key_events += 1
        if t == "MouseClick" and (st.get("down") is True or st.get("up") is True):
            raw_click_events += 1

        # 3.5) Literal text throughput: long/structured text often wants a
        # clipboard or segmented lane instead of per-character typing.
        literal_text = _literal_type_text_candidate(st)
        if literal_text is not None:
            text, backend = literal_text
            if ("\n" in text or "\t" in text) and len(text) >= warn_structured_typed_text_chars:
                add(
                    severity="info",
                    code="STRUCTURED_TYPED_TEXT_LITERAL",
                    path=path,
                    step_type=t,
                    message=(
                        f"Literal TypeText step contains structured text ({len(text)} chars with Tab/Enter separators); "
                        f"{backend} typing keeps throughput and field boundaries coupled."
                    ),
                    suggestion=(
                        "If this is a form-like snippet, consider a hybrid lane: "
                        "vhk optimize <macro.yaml> --segment-paste-text --segment-paste-min-chars 24, "
                        "or split fields manually so long values can use backend=clipboard while Tab/Enter stay explicit."
                    ),
                )
            elif len(text) >= warn_long_typed_text_chars:
                add(
                    severity="info",
                    code="LONG_TYPED_TEXT_LITERAL",
                    path=path,
                    step_type=t,
                    message=(
                        f"Literal TypeText step is long ({len(text)} chars); typed {backend} text is often slower than a clipboard/hybrid lane."
                    ),
                    suggestion=(
                        "If throughput matters more than per-character semantics, use backend=clipboard or run "
                        "vhk optimize <macro.yaml> --promote-paste-text --paste-text-min-chars 80. "
                        "Turbo profiles can also auto-promote long paste-friendly text."
                    ),
                )

        # 4) Broad screen searches: encourage regions.
        if t in {"WaitForImage", "ImageSearch", "WaitForText", "WaitForTextVanish", "WaitForTextBox", "OcrReadText", "OcrFindText", "OcrFindTextAll", "ClickText", "ClickTextAll", "WaitForRegionChange", "WaitForRegionStable"}:
            if st.get("region") is None:
                add(
                    severity="info",
                    code="NO_REGION",
                    path=path,
                    step_type=t,
                    message=f"{t} searches the full screen; a smaller region is faster and reduces false matches.",
                    suggestion="Use `vhk select-region` to capture a ROI. You can paste the mapping inline or save it under project.yaml regions and reference it as region: \"@name\" (see docs/NAMED_REGIONS.md).",
                )

        # 5) Overly aggressive polling.
        if t in {
            "WaitForImage",
            "WaitForImageVanish",
            "WaitForText",
            "WaitForTextBox",
            "WaitForImageFile",
            "WaitForPixelFile",
            "WaitForPixelVanish",
            "WaitForClipboardChange",
            "WaitForProcessExit",
            "WaitForFile",
            "WaitForNewFile",
            "WaitForFileEvent",
            "WaitForDownload",
            "WaitForHttp",
            "WaitForWindow",
            "WaitForWindowVanish",
            "WaitForRegionChange", "WaitForRegionStable",
        }:
            pm = st.get("poll_ms")
            if isinstance(pm, (int, float)) and int(pm) > 0 and int(pm) < int(warn_low_poll_ms):
                add(
                    severity="info",
                    code="POLL_LOW",
                    path=path,
                    step_type=t,
                    message=f"poll_ms={int(pm)}ms is quite low and may burn CPU.",
                    suggestion="Consider poll_ms in the 100–250ms range unless you truly need high frequency.",
                )

            sr = st.get("scan_rate_hz")
            if isinstance(sr, (int, float)) and float(sr) > 0:
                eff = int(round(1000.0 / float(sr)))
                if eff > 0 and eff < int(warn_low_poll_ms):
                    add(
                        severity="info",
                        code="SCAN_RATE_HIGH",
                        path=path,
                        step_type=t,
                        message=f"scan_rate_hz={float(sr):g} implies ~{eff}ms scans, which may burn CPU.",
                        suggestion="Consider scan_rate_hz around 4–10 for most UI waits (or use poll_ms 100–250ms).",
                    )

    # Macro-level nudge: if it looks like raw recording output, suggest optimize.
    if raw_key_events + raw_click_events + mouse_moves >= 10:
        add(
            severity="info",
            code="RECORDER_ARTIFACTS",
            path="steps",
            step_type=None,
            message=(
                "Macro looks like raw recorder output (down/up events or many mouse moves). "
                "Post-processing usually improves readability."
            ),
            suggestion="Run: vhk optimize <macro.yaml> --in-place (or vhk optimize-project <project_dir> --in-place).",
        )

    return issues
