"""Micromax editor host.

A calm, scriptable editor whose headless model is product truth. The host owns
terminal, filesystem, process, clipboard, persistence, and UI effects; Micromax
is the configuration, macro, and plugin language exposed through explicit policy.
"""

from __future__ import annotations

from .editor import Editor

__all__ = ["Editor"]

# rev0959 recovery surface
from .recovery_journal import RecoveryJournal, RecoveryStatus, RecoveryCandidate, SaveOutcome
