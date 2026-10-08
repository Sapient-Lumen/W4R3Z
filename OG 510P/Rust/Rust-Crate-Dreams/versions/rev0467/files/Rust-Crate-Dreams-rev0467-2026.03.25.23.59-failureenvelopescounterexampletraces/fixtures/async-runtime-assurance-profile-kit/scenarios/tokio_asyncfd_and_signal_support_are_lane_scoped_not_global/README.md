# Scenario — Tokio AsyncFd and signal support are lane-scoped, not global

This scenario exists to stop another easy overread:

> “The crate uses Tokio, therefore Unix reactor-backed and console-signal capabilities are all globally supported.”

Tokio’s current docs keep `AsyncFd` Unix-specific, and signal surfaces split between Unix and Windows modules.
The matrix therefore records capability truth by deployment lane instead of flattening it into one runtime-family badge.
