"""Hostcall resource-budget helpers.

These helpers deliberately live beside the VM instead of in the editor bridge so
standalone embeddings get the same basic output boundary.  They do not try to
measure Python object memory exactly.  The goal is a deterministic, conservative
budget over VM-visible result payloads: strings/bytes count by byte length,
containers count their visible cells recursively, and opaque host objects count
as one small cell.
"""

from __future__ import annotations

from dataclasses import dataclass
import operator
from typing import Any, Iterable


DEFAULT_HOSTCALL_RESULT_MAX_BYTES = 1_048_576
DEFAULT_HOSTCALL_RESULT_MAX_CELLS = 8192
# Core value-to-text rendering is not a hostcall, but it needs the same safe
# default ceiling so one primitive cannot expand a shared object graph into an
# arbitrarily large Python string before plugin dispatch fuel can run again.
DEFAULT_VALUE_TEXT_MAX_BYTES = DEFAULT_HOSTCALL_RESULT_MAX_BYTES
_MAX_ESTIMATE_DEPTH = 16
_INT_EXACT_TEXT_MAX_BITS = 4096


def estimate_int_text_bytes(value: int) -> int:
    """Return a bounded-cost upper estimate of decimal integer text bytes.

    Small integers retain exact accounting.  For large integers, avoid entering
    CPython's potentially expensive decimal conversion (and its configurable
    digit-limit exception path); a rational upper bound is at most one digit
    above the exact magnitude length.
    """

    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("estimate_int_text_bytes expects a non-boolean int")
    integer = int(value)
    magnitude = abs(integer)
    bits = magnitude.bit_length()
    sign = 1 if integer < 0 else 0
    if bits <= _INT_EXACT_TEXT_MAX_BITS:
        return len(str(integer))
    # 30103 / 100000 is slightly greater than log10(2), so ceil(bits *
    # 30103 / 100000) safely bounds the decimal digit count of any bits-wide
    # integer without allocating another giant object or decimal string.
    digits = max(1, ((bits * 30103) + 99_999) // 100_000)
    return sign + digits


def _effective_budget_limit(value: object, *, default: int) -> int:
    """Return a non-lossy integer limit, failing malformed values safely.

    Booleans and fractional numerics are not resource counts.  A genuine
    integer ``<= 0`` remains the explicit embedding opt-out.
    """

    try:
        if isinstance(value, bool):
            raise TypeError("bool is not a resource limit")
        if isinstance(value, str):
            parsed = int(value.strip(), 10)
        else:
            parsed = operator.index(value)
    except (TypeError, ValueError, OverflowError):
        parsed = int(default)
    return int(parsed)


def effective_hostcall_result_limits(vm: Any) -> tuple[int, int]:
    """Return fail-safe byte/cell limits for one VM or embedding object."""

    return (
        _effective_budget_limit(
            getattr(vm, "hostcall_result_max_bytes", DEFAULT_HOSTCALL_RESULT_MAX_BYTES),
            default=DEFAULT_HOSTCALL_RESULT_MAX_BYTES,
        ),
        _effective_budget_limit(
            getattr(vm, "hostcall_result_max_cells", DEFAULT_HOSTCALL_RESULT_MAX_CELLS),
            default=DEFAULT_HOSTCALL_RESULT_MAX_CELLS,
        ),
    )


def utf8_size(text: str, *, stop_after: int | None = None) -> int:
    """Return UTF-8 bytes with ``errors="replace"`` without allocating bytes.

    ``stop_after`` allows a caller to stop as soon as the result is known to be
    too large.  The returned value is exact unless that early boundary is
    crossed, in which case it is a proven lower bound greater than the limit.
    """

    if not isinstance(text, str):
        raise TypeError("utf8_size expects str")
    limit = None if stop_after is None else max(-1, int(stop_after))
    if text.isascii():
        return len(text)

    total = 0
    for char in text:
        codepoint = ord(char)
        if codepoint <= 0x7F or 0xD800 <= codepoint <= 0xDFFF:
            total += 1
        elif codepoint <= 0x7FF:
            total += 2
        elif codepoint <= 0xFFFF:
            total += 3
        else:
            total += 4
        if limit is not None and total > limit:
            return total
    return total


@dataclass(frozen=True)
class HostValueBudgetEstimate:
    """Approximate size of VM-visible hostcall result values."""

    cells: int = 0
    bytes: int = 0
    truncated: bool = False

    def add(self, other: "HostValueBudgetEstimate") -> "HostValueBudgetEstimate":
        return HostValueBudgetEstimate(
            cells=self.cells + other.cells,
            bytes=self.bytes + other.bytes,
            truncated=self.truncated or other.truncated,
        )


def _limit_exceeded(
    estimate: HostValueBudgetEstimate,
    *,
    max_bytes: int,
    max_cells: int,
) -> bool:
    return (max_bytes > 0 and estimate.bytes > max_bytes) or (
        max_cells > 0 and estimate.cells > max_cells
    )


def estimate_host_value_budget(
    value: Any,
    *,
    max_bytes: int = DEFAULT_HOSTCALL_RESULT_MAX_BYTES,
    max_cells: int = DEFAULT_HOSTCALL_RESULT_MAX_CELLS,
    _seen: set[int] | None = None,
    _depth: int = 0,
) -> HostValueBudgetEstimate:
    """Return a bounded, deterministic estimate for one VM-visible value.

    The estimator stops walking once configured limits are already exceeded.
    Cycles and excessive nesting are counted as a single opaque cell rather than
    recursing indefinitely.
    """

    if _seen is None:
        _seen = set()
    if _depth > _MAX_ESTIMATE_DEPTH:
        return HostValueBudgetEstimate(cells=1, bytes=3, truncated=True)

    # Tiny scalar values are intentionally cheap.  Booleans can appear when a
    # Python embedding calls host functions directly, even though portable VM
    # code uses 0/1.
    if value is None:
        return HostValueBudgetEstimate(cells=1, bytes=0)
    if isinstance(value, bool):
        return HostValueBudgetEstimate(cells=1, bytes=4 if value else 5)
    if isinstance(value, int):
        return HostValueBudgetEstimate(cells=1, bytes=estimate_int_text_bytes(value))
    if isinstance(value, str):
        return HostValueBudgetEstimate(cells=1, bytes=utf8_size(value))
    if isinstance(value, (bytes, bytearray)):
        return HostValueBudgetEstimate(cells=1, bytes=len(value))
    if isinstance(value, memoryview):
        return HostValueBudgetEstimate(cells=1, bytes=int(value.nbytes))

    obj_id = id(value)
    if obj_id in _seen:
        return HostValueBudgetEstimate(cells=1, bytes=8, truncated=True)

    if isinstance(value, (list, tuple, set, frozenset)):
        _seen.add(obj_id)
        total = HostValueBudgetEstimate(cells=1, bytes=0)
        for item in value:
            total = total.add(
                estimate_host_value_budget(
                    item,
                    max_bytes=max_bytes,
                    max_cells=max_cells,
                    _seen=_seen,
                    _depth=_depth + 1,
                )
            )
            if _limit_exceeded(total, max_bytes=max_bytes, max_cells=max_cells):
                break
        _seen.discard(obj_id)
        return total

    if isinstance(value, dict):
        _seen.add(obj_id)
        total = HostValueBudgetEstimate(cells=1, bytes=0)
        for key, item in value.items():
            total = total.add(
                estimate_host_value_budget(
                    key,
                    max_bytes=max_bytes,
                    max_cells=max_cells,
                    _seen=_seen,
                    _depth=_depth + 1,
                )
            )
            if _limit_exceeded(total, max_bytes=max_bytes, max_cells=max_cells):
                break
            total = total.add(
                estimate_host_value_budget(
                    item,
                    max_bytes=max_bytes,
                    max_cells=max_cells,
                    _seen=_seen,
                    _depth=_depth + 1,
                )
            )
            if _limit_exceeded(total, max_bytes=max_bytes, max_cells=max_cells):
                break
        _seen.discard(obj_id)
        return total

    # Do not call arbitrary repr(); host values can have expensive or impure
    # representations.  Count opaque handles by type-name length only.
    return HostValueBudgetEstimate(cells=1, bytes=len(type(value).__name__))


def estimate_host_values_budget(
    values: Iterable[Any],
    *,
    max_bytes: int = DEFAULT_HOSTCALL_RESULT_MAX_BYTES,
    max_cells: int = DEFAULT_HOSTCALL_RESULT_MAX_CELLS,
) -> HostValueBudgetEstimate:
    """Return the aggregate VM-visible budget estimate for hostcall results."""

    seen: set[int] = set()
    total = HostValueBudgetEstimate()
    for value in values:
        total = total.add(
            estimate_host_value_budget(
                value,
                max_bytes=max_bytes,
                max_cells=max_cells,
                _seen=seen,
            )
        )
        if _limit_exceeded(total, max_bytes=max_bytes, max_cells=max_cells):
            break
    return total


def hostcall_result_budget_violation_from_counts(
    hostcall_name: str,
    *,
    byte_count: int,
    cell_count: int,
    max_bytes: int = DEFAULT_HOSTCALL_RESULT_MAX_BYTES,
    max_cells: int = DEFAULT_HOSTCALL_RESULT_MAX_CELLS,
) -> str | None:
    """Return the standard violation message for a prospective result.

    Most hostcalls can only inspect a value after constructing it.  Operations
    with exact output geometry (for example string join/replace/split) can use
    this helper before entering the allocating primitive, while the generic
    postcondition below remains the final defense for every hostcall.
    """

    max_bytes = _effective_budget_limit(
        max_bytes, default=DEFAULT_HOSTCALL_RESULT_MAX_BYTES
    )
    max_cells = _effective_budget_limit(
        max_cells, default=DEFAULT_HOSTCALL_RESULT_MAX_CELLS
    )
    byte_count = max(0, int(byte_count))
    cell_count = max(0, int(cell_count))
    if max_bytes > 0 and byte_count > max_bytes:
        return (
            f"hostcall result budget exceeded: {hostcall_name}: "
            f"{byte_count} bytes > {max_bytes}"
        )
    if max_cells > 0 and cell_count > max_cells:
        return (
            f"hostcall result budget exceeded: {hostcall_name}: "
            f"{cell_count} cells > {max_cells}"
        )
    return None


def hostcall_result_budget_violation(
    hostcall_name: str,
    values: Iterable[Any],
    *,
    max_bytes: int = DEFAULT_HOSTCALL_RESULT_MAX_BYTES,
    max_cells: int = DEFAULT_HOSTCALL_RESULT_MAX_CELLS,
) -> str | None:
    """Return a stable error message when result values exceed a budget."""

    max_bytes = _effective_budget_limit(
        max_bytes, default=DEFAULT_HOSTCALL_RESULT_MAX_BYTES
    )
    max_cells = _effective_budget_limit(
        max_cells, default=DEFAULT_HOSTCALL_RESULT_MAX_CELLS
    )
    if max_bytes <= 0 and max_cells <= 0:
        return None
    estimate = estimate_host_values_budget(values, max_bytes=max_bytes, max_cells=max_cells)
    return hostcall_result_budget_violation_from_counts(
        hostcall_name,
        byte_count=estimate.bytes,
        cell_count=estimate.cells,
        max_bytes=max_bytes,
        max_cells=max_cells,
    )


def changed_stack_suffix(before: list[Any], after: list[Any]) -> list[Any]:
    """Return the VM stack suffix changed by a stack-top hostcall.

    Hostcalls conventionally consume and produce values at the top of the stack.
    The unchanged prefix is detected by object identity so the helper avoids
    arbitrary equality hooks on user-visible values.
    """

    prefix = 0
    max_prefix = min(len(before), len(after))
    while prefix < max_prefix and before[prefix] is after[prefix]:
        prefix += 1
    return list(after[prefix:])
