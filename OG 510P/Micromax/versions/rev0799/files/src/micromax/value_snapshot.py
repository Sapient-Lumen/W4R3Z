from __future__ import annotations

"""Small value-copy helpers for rollback snapshots.

Micromax stack values are usually immutable scalars, words, quotations, or small
portable host containers.  Several recovery boundaries promise to restore the
caller-visible stack/input state after a failed protected operation.  A shallow
``list(stack)`` is not enough for that promise: a quotation can mutate a list or
map value in place and then throw, leaving the restored stack pointing at the
mutated object.

These helpers intentionally deep-copy only Micromax's portable mutable
containers: ``list`` and ``dict``.  Runtime objects such as words, quotations,
cells, cursors, and host handles remain identity values.
"""

from collections.abc import Mapping
from typing import Any, Iterable, MutableMapping


_IMMUTABLE_TYPES = (str, bytes, int, float, bool, type(None))


def snapshot_value(value: Any, _memo: dict[int, Any] | None = None) -> Any:
    """Return a rollback-safe copy of portable mutable Micromax values.

    Lists and dictionaries are copied recursively, preserving self-references
    and shared container identity within one snapshot.  Everything else is kept
    by reference so execution tokens and host objects are not accidentally
    duplicated.
    """

    if isinstance(value, _IMMUTABLE_TYPES):
        return value
    if _memo is None:
        _memo = {}
    obj_id = id(value)
    if obj_id in _memo:
        return _memo[obj_id]
    if isinstance(value, list):
        out: list[Any] = []
        _memo[obj_id] = out
        out.extend(snapshot_value(item, _memo) for item in value)
        return out
    if isinstance(value, dict):
        out: dict[Any, Any] = {}
        _memo[obj_id] = out
        for key, item in value.items():
            # Map keys are normally strings.  Preserve key identity for unusual
            # hashable host objects; snapshot only the mutable values.
            out[key] = snapshot_value(item, _memo)
        return out
    return value


def snapshot_stack(values: Iterable[Any]) -> list[Any]:
    """Return a portable-container-safe snapshot of a stack-like iterable."""

    memo: dict[int, Any] = {}
    return [snapshot_value(value, memo) for value in values]


def snapshot_mapping(mapping: Mapping[str, Any] | MutableMapping[str, Any]) -> dict[str, Any]:
    """Return a portable-container-safe snapshot of string-keyed mappings."""

    memo: dict[int, Any] = {}
    return {str(key): snapshot_value(value, memo) for key, value in dict(mapping).items()}
