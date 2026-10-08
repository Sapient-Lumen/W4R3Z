# ADR 0062 — Garden work scheduling protects control plane

## Decision

Garden scheduling should protect head-watch, witness-query, and seed-gate work from bulk provider floods.

## Reason

Bulk provider/reprovide work matters, but mutable heads, witness evidence, and entrances are control-plane liveness.  A generous garden that accepts bulk work until it starves control work is failing in an unobvious way.

## Consequence

`gardenscheduler.py` plans multi-window admission/refusal schedules and flags starvation pressure for protected work.
