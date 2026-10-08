from __future__ import annotations

"""State-bound confirmation for editor operations that discard buffers.

A plain boolean is not enough evidence for a destructive second attempt. The
buffer set or unsaved text can change after the warning, turning a stale
"armed" bit into permission to discard data the user was never shown. This
module keeps the confirmation witness small and side-effect free: exact target
identity, mutation version, dirty state, and path must still match.
"""

import weakref
from dataclasses import dataclass, field
from typing import Iterable


DISCARD_ARMED = "armed"
DISCARD_REARMED = "rearmed"
DISCARD_CONFIRMED = "confirmed"


@dataclass(frozen=True)
class DiscardIdentityWitness:
    """Weak identity for retained context that must not be silently replaced."""

    name: str
    _ref: weakref.ReferenceType[object] = field(compare=False, repr=False)

    @classmethod
    def capture(cls, name: object, editor_buffer: object) -> "DiscardIdentityWitness":
        return cls(name=str(name), _ref=weakref.ref(editor_buffer))

    def matches(self, other: object) -> bool:
        if not isinstance(other, DiscardIdentityWitness):
            return False
        mine = self._ref()
        theirs = other._ref()
        return bool(mine is not None and mine is theirs and self.name == other.name)


@dataclass(frozen=True)
class DiscardBufferWitness:
    """One live buffer row captured for a destructive confirmation.

    The weak reference checks object identity without retaining a potentially
    large closed buffer. ``version`` is the Buffer mutation counter; including
    it deliberately invalidates a warning even when an edit is later undone
    back to identical text.
    """

    name: str
    version: int
    dirty: bool
    path: str | None
    _ref: weakref.ReferenceType[object] = field(compare=False, repr=False)

    @classmethod
    def capture(cls, name: object, editor_buffer: object) -> "DiscardBufferWitness":
        buf = getattr(editor_buffer, "buf", None)
        path = getattr(buf, "path", None)
        return cls(
            name=str(name),
            version=int(getattr(buf, "version", 0)),
            dirty=bool(getattr(buf, "dirty", False)),
            path=(str(path) if path is not None else None),
            _ref=weakref.ref(editor_buffer),
        )

    def matches(self, other: object) -> bool:
        if not isinstance(other, DiscardBufferWitness):
            return False
        mine = self._ref()
        theirs = other._ref()
        return bool(
            mine is not None
            and mine is theirs
            and self.name == other.name
            and self.version == other.version
            and self.dirty == other.dirty
            and self.path == other.path
        )


@dataclass(frozen=True)
class DiscardWitness:
    """Exact target state and retained context for one destructive operation."""

    operation: str
    buffers: tuple[DiscardBufferWitness, ...]
    keep: str = ""
    anchors: tuple[DiscardIdentityWitness, ...] = ()

    @classmethod
    def capture(
        cls,
        operation: object,
        rows: Iterable[tuple[object, object]],
        *,
        keep: object = "",
        anchors: Iterable[tuple[object, object]] = (),
    ) -> "DiscardWitness":
        captured = [DiscardBufferWitness.capture(name, eb) for name, eb in rows]
        captured.sort(key=lambda row: row.name)
        retained = [DiscardIdentityWitness.capture(name, eb) for name, eb in anchors]
        retained.sort(key=lambda row: row.name)
        return cls(
            operation=str(operation),
            buffers=tuple(captured),
            keep=str(keep or ""),
            anchors=tuple(retained),
        )

    @property
    def target_names(self) -> tuple[str, ...]:
        return tuple(row.name for row in self.buffers)

    def matches(self, other: object) -> bool:
        if not isinstance(other, DiscardWitness):
            return False
        if self.operation != other.operation or self.keep != other.keep:
            return False
        if len(self.buffers) != len(other.buffers) or len(self.anchors) != len(other.anchors):
            return False
        targets_match = all(
            left.matches(right) for left, right in zip(self.buffers, other.buffers)
        )
        anchors_match = all(
            left.matches(right) for left, right in zip(self.anchors, other.anchors)
        )
        return targets_match and anchors_match


class DiscardConfirmationGuard:
    """Own the editor's single pending destructive confirmation witness."""

    def __init__(self) -> None:
        self._witness: DiscardWitness | None = None

    @property
    def witness(self) -> DiscardWitness | None:
        return self._witness

    def clear(self) -> None:
        self._witness = None

    def clear_unless(self, operation: object) -> None:
        current = self._witness
        if current is not None and current.operation != str(operation or ""):
            self.clear()

    def is_armed(self, witness: DiscardWitness) -> bool:
        current = self._witness
        return current is not None and current.matches(witness)

    def request(self, witness: DiscardWitness) -> str:
        """Arm, refresh, or confirm ``witness``.

        Only an exact second request confirms. Any changed operation, target
        set, object identity, path, dirty bit, mutation version, or retained
        context replaces the old witness and requires another explicit attempt.
        """

        current = self._witness
        if current is not None and current.matches(witness):
            self.clear()
            return DISCARD_CONFIRMED
        result = DISCARD_REARMED if current is not None else DISCARD_ARMED
        self._witness = witness
        return result


def format_discard_warning(
    operation: object,
    dirty: Iterable[object],
    *,
    force_hint: object,
    refreshed: bool = False,
) -> str:
    """Return the shared human warning for close/quit-family commands."""

    names = sorted(str(name) for name in dirty)
    preview = ", ".join(names[:6])
    more = max(0, len(names) - 6)
    suffix = f" ... (+{more} more)" if more else ""
    command = str(operation or "").strip()
    force = str(force_hint or "").strip()
    if refreshed:
        return (
            f"discard scope or unsaved state changed; unsaved buffers: {preview}{suffix}; "
            f"confirmation refreshed; run `{command}` again or `{force}` to force"
        )
    return (
        f"unsaved changes in: {preview}{suffix}; "
        f"run `{command}` again or `{force}` to force"
    )
