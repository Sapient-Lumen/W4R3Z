from __future__ import annotations

"""Small helpers for editor transient-state rollback.

The editor has a few process-local scratchpads used to ferry data between key
handling, command dispatch, and actions.  They are not durable user settings or
registries.  Lower-authority script/deferred callbacks may use them while they
run, but should not leave stale values behind for a later user action to pick
up accidentally.
"""

from dataclasses import dataclass
from typing import Any, MutableMapping

from micromax.value_snapshot import snapshot_mapping


@dataclass(frozen=True)
class InputScratchSnapshot:
    """Portable-container-safe snapshot of ``Editor.input`` membership."""

    values: dict[str, Any]


def snapshot_input_scratch(mapping: MutableMapping[str, Any]) -> InputScratchSnapshot:
    """Return a restorable copy of an editor input scratch mapping."""

    return InputScratchSnapshot(values=snapshot_mapping(mapping))


def restore_input_scratch(mapping: MutableMapping[str, Any], snapshot: InputScratchSnapshot) -> None:
    """Restore ``mapping`` membership from ``snapshot`` without replacing it."""

    mapping.clear()
    mapping.update(snapshot_mapping(snapshot.values))
