# ADR 0070 — Adaptive alpha before live lookup optimization

## Decision

Implement deterministic adaptive alpha/beta pressure before live I2P lookup optimization.

## Rationale

On I2P, low alpha can let a captured fast family dominate early evidence; high alpha can become a metadata and bandwidth flood. The cube needs a local pressure model that can widen, hold, back off, or quarantine before any real network noise hides the bug.

## Consequence

`adaptivealpha.py` is a toy policy surface, not a measured optimizer. It protects future transport work from hard-coding constant-alpha assumptions too early.
