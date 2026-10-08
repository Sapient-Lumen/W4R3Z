from __future__ import annotations

"""Shared finite-input budgets for public headless screen snapshots.

The editor's internal screen model accepts renderer geometry, while public CLI,
REPL, and contract-consumer paths accept caller-controlled dimensions and JSON.
Those public paths use one small preflight so traversal/allocation is bounded
before a model or decoder does substantial work.
"""

SCREEN_MIN_LINES = 1
SCREEN_MAX_LINES = 256
SCREEN_MIN_COLS = 1
SCREEN_MAX_COLS = 512
SCREEN_MAX_CELLS = 65_536

SCREEN_CONTRACT_MAX_JSON_BYTES = 8 * 1024 * 1024
SCREEN_CONTRACT_MAX_JSON_DEPTH = 64
SCREEN_CONTRACT_MAX_INTEGER = (2**53) - 1
SCREEN_CONTRACT_MAX_CUES = 65_536
SCREEN_CONTRACT_MAX_TAGS_PER_ROW = 32
SCREEN_CONTRACT_MAX_TOKEN_CHARS = 96


class ScreenBudgetError(ValueError):
    """Raised before an unbounded public screen operation begins."""


def checked_screen_dimensions(
    lines: object,
    cols: object,
    *,
    label: str = "screen",
) -> tuple[int, int]:
    """Return positive bounded ``(lines, cols)`` or raise ``ScreenBudgetError``."""

    if (
        isinstance(lines, bool)
        or isinstance(cols, bool)
        or not isinstance(lines, int)
        or not isinstance(cols, int)
    ):
        raise ScreenBudgetError(f"{label}: lines and cols must be integers")
    h = int(lines)
    w = int(cols)

    if h < SCREEN_MIN_LINES or h > SCREEN_MAX_LINES:
        raise ScreenBudgetError(
            f"{label}: lines must be between {SCREEN_MIN_LINES} and "
            f"{SCREEN_MAX_LINES} (got {h})"
        )
    if w < SCREEN_MIN_COLS or w > SCREEN_MAX_COLS:
        raise ScreenBudgetError(
            f"{label}: cols must be between {SCREEN_MIN_COLS} and "
            f"{SCREEN_MAX_COLS} (got {w})"
        )

    cells = h * w
    if cells > SCREEN_MAX_CELLS:
        raise ScreenBudgetError(
            f"{label}: screen area {cells} exceeds cell budget {SCREEN_MAX_CELLS}"
        )
    return h, w
