# ADR 0168: Finality ledger before terminal truth

Status: accepted in rev0058.

A reconciled effect is not terminal until a signed local finality marker binds the reconcile report, dead-letter/retry/journal evidence, exact boundary, sequence, and previous marker.

Decision: terminal commit/abort markers are allowed only when reconcile no longer requires retry or dead-letter memory. Retry/dead-letter outcomes remain watchful markers.
