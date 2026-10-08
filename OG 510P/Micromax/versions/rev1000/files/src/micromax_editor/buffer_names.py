from __future__ import annotations

from collections.abc import Collection


class BufferNameCollisionError(RuntimeError):
    """Raised when strict buffer creation would replace a live buffer."""


def unique_buffer_name(preferred: object, occupied_names: Collection[str]) -> str:
    """Return a deterministic unused display name.

    Buffer names are lookup keys throughout the editor.  Human-facing creation
    may therefore choose a nearby unused label, but it must never achieve that
    convenience by replacing the object already stored under ``preferred``.

    Internal ``*name*`` buffers keep their visual shape (``*name-2*``), while
    ordinary names follow the familiar ``name<2>`` convention.  The search is
    bounded by the number of occupied names: among ``N`` candidate suffixes at
    least one must be free when there are only ``N`` occupied keys total.
    """

    name = str(preferred)
    if not name:
        raise ValueError("buffer name must not be empty")

    occupied = {str(item) for item in occupied_names}
    if name not in occupied:
        return name

    internal = len(name) >= 2 and name.startswith("*") and name.endswith("*")
    stem = name[1:-1] if internal else name
    for number in range(2, len(occupied) + 2):
        candidate = f"*{stem}-{number}*" if internal else f"{name}<{number}>"
        if candidate not in occupied:
            return candidate

    # The bounded pigeonhole argument above makes this unreachable.  Keep an
    # explicit failure rather than an unbounded loop if the contract changes.
    raise RuntimeError("could not allocate a unique buffer name")


__all__ = ["BufferNameCollisionError", "unique_buffer_name"]
