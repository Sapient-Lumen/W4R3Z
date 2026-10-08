# ADR 0142 — telemetry retention is metadata debt

Status: accepted for the design cube.

Redacting metrics at emission time is not enough.  Retained diagnostics can accumulate scope, label-cardinality, and hard-negative evidence debt.  `telemetrydebt.py` makes retention a local safety surface.
