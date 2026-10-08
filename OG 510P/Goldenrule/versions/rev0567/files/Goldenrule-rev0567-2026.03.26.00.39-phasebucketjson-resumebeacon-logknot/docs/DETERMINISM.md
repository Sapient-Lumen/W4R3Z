# Determinism & Seeds

Determinism is a hard requirement: same inputs + seeds must yield identical artifacts.

## Seed streams

The engine uses independent RNG streams derived from the task’s `match_seed`:
- per-player decision RNGs
- per-player implementation-noise RNGs
- per-player observation-noise RNGs
- (when needed) a termination RNG stream (e.g. geometric termination)

The derived seeds are recorded in the output artifact to make debugging and reproduction mechanical.

## Trace semantics

Each round records:
- intended actions (strategy output)
- executed actions (after implementation noise)
- observed opponent actions (after observation noise; per player)

This separation is required for “intention calibration” probes under uncertainty.
