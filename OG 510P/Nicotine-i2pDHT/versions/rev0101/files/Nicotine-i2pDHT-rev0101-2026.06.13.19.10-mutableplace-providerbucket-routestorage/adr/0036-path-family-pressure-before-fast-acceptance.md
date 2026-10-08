# ADR 0036 — path-family pressure before fast acceptance

## Decision

Mutable lookups should not accept the fastest responses unless enough independent-ish path families have replied.

## Rationale

I2P latency and garden supernodes make fast answers attractive. A captured fast family can return stale, empty, or forked signed records. rev0010 therefore treats lookup as a pressure process and requires family diversity before acceptance.

## Status

Toy-tested in `pathpressure.py`.
