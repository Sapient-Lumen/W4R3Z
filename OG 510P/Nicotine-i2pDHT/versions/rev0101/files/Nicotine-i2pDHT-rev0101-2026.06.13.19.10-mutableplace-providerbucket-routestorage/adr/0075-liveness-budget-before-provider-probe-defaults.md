# ADR 0075 — Liveness budget before provider probe defaults

Status: accepted in rev0018.

Adaptive lookup widening must not automatically widen provider semantic probes. The cube now requires an explicit liveness/metadata budget between lookup pressure and provider probing.
