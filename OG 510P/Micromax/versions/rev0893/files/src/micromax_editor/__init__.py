"""micromax_editor

An intentionally small, micro-inspired editor prototype.

Guiding idea:
  - the host (Python) owns the world (terminal, FS, UI)
  - micromax is the plugin / configuration language

This package is *not* a full editor yet. It's a testable, headless core plus
plumbing we can grow into a terminal UI.
"""

from __future__ import annotations

from .editor import Editor

__all__ = ["Editor"]
