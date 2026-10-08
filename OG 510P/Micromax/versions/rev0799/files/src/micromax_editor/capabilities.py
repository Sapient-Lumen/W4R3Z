from __future__ import annotations

"""micromax_editor.capabilities

Tiny capability registry for optional/unsafe host surfaces.

Design goals:

- Keep the editor core + VM portable: optional features are *not* assumed.
- Keep safety boundaries explicit: anything that touches the host world
  (processes, network, UI integration) is capability-gated.
- Make it easy for humans (and future LLMs) to discover what exists.

The embedded VM already exposes `host.feature?` and `host.features`. This module
adds a small registry so the host can advertise *why* a feature exists and how
to enable it.

Conventions:

- `feature` is the string checked by `host.feature?`.
- `option` is the editor option that enables the feature.
- `kind` is informational: "safe" vs "unsafe".
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Capability:
    feature: str
    option: str
    kind: str
    doc: str


CAPS: dict[str, Capability] = {
    "ed.open-url": Capability(
        feature="ed.open-url",
        option="cap.open-url",
        kind="unsafe",
        doc="Open an external URL via the host system browser (disabled by default).",
    ),
    "ed.shell": Capability(
        feature="ed.shell",
        option="cap.shell",
        kind="unsafe",
        doc="Run a shell command and capture output (disabled by default).",
    ),
    "ed.open": Capability(
        feature="ed.open",
        option="cap.fs-open",
        kind="unsafe",
        doc="Open a file from disk into a buffer (disabled by default).",
    ),
    "ed.save": Capability(
        feature="ed.save",
        option="cap.fs-save",
        kind="unsafe",
        doc="Save the current buffer to disk (disabled by default).",
    ),
    "ed.force-save": Capability(
        feature="ed.force-save",
        option="cap.fs-force-save",
        kind="unsafe",
        doc="Force-save over a detected external disk change (disabled by default).",
    ),
    "ed.buffer-discard": Capability(
        feature="ed.buffer-discard",
        option="cap.buffer-discard",
        kind="unsafe",
        doc="Allow scripts to discard dirty in-memory buffers through forced close/revert/quit paths (disabled by default).",
    ),
    "ed.history-clear": Capability(
        feature="ed.history-clear",
        option="cap.history-clear",
        kind="unsafe",
        doc="Allow scripts to clear editor navigation/recent/message history registers (disabled by default).",
    ),
    "ed.undo-redo": Capability(
        feature="ed.undo-redo",
        option="cap.undo-redo",
        kind="unsafe",
        doc="Allow scripts to replay trusted/editor undo-redo history entries (disabled by default).",
    ),
    "ed.fs-read": Capability(
        feature="ed.fs-read",
        option="cap.fs-read",
        kind="unsafe",
        doc="Read an arbitrary file from disk as UTF-8 (disabled by default).",
    ),
    "ed.fs-list": Capability(
        feature="ed.fs-list",
        option="cap.fs-list",
        kind="unsafe",
        doc="List directory entries from disk (disabled by default).",
    ),
    "ed.fs-stat": Capability(
        feature="ed.fs-stat",
        option="cap.fs-stat",
        kind="unsafe",
        doc="Stat a path from disk (exists/kind/size/mtime) (disabled by default).",
    ),
    "ed.require": Capability(
        feature="ed.require",
        option="cap.fs-require",
        kind="unsafe",
        doc="Load and evaluate a Micromax source file from disk (disabled by default).",
    ),
    "ed.chdir": Capability(
        feature="ed.chdir",
        option="cap.fs-chdir",
        kind="unsafe",
        doc="Allow scripts to change the process current directory (disabled by default).",
    ),
    "ed.clipboard-export": Capability(
        feature="ed.clipboard-export",
        option="cap.clipboard-write",
        kind="unsafe",
        doc="Allow scripts to export clipboard to the system clipboard via UI backends (terminal OSC 52/external) (disabled by default).",
    ),
    "ed.clipboard-import": Capability(
        feature="ed.clipboard-import",
        option="cap.clipboard-read",
        kind="unsafe",
        doc="Allow scripts to import the system clipboard via external tools (disabled by default).",
    ),
    "ed.persist": Capability(
        feature="ed.persist",
        option="cap.persist",
        kind="unsafe",
        doc="Allow editor-owned persistence files (recent/history) to be read/written (disabled by default).",
    ),
}


def enabled_features(ed: Any) -> set[str]:
    """Return currently-enabled capability feature strings for this editor."""

    out: set[str] = set()
    for feat, cap in CAPS.items():
        try:
            if bool(ed.options.get(cap.option)):
                out.add(feat)
        except Exception:
            continue
    return out


def refresh_vm_features(ed: Any, vm: Any) -> None:
    """Update vm.host_features to reflect the editor's capability options.

    This intentionally only touches features declared in this registry.
    """

    want = enabled_features(ed)
    for feat in CAPS.keys():
        if feat in want:
            vm.host_features.add(feat)
        else:
            try:
                vm.host_features.discard(feat)
            except Exception:
                pass


def capability_rows(ed: Any) -> list[list[object]]:
    """Return registry rows for UI/scripts.

    Rows are: [feature option kind enabled doc]
    """

    rows: list[list[object]] = []
    for feat in sorted(CAPS.keys()):
        cap = CAPS[feat]
        enabled = 0
        try:
            enabled = 1 if bool(ed.options.get(cap.option)) else 0
        except Exception:
            enabled = 0
        rows.append([cap.feature, cap.option, cap.kind, enabled, cap.doc])
    return rows
