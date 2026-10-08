# Repo transition plan

This file explains how to move from the current repo shape to the intended canon without losing useful history.

## Stage 1 — Canon adoption
- replace top-level docs with the current canon
- keep historical handoffs intact
- add support-records and templates directories

## Stage 2 — Vocabulary audit
- scan docs for synonyms that should map to canonical keys
- normalize workflow, lane, and support-tier language
- update `docs/canon-keys.md` where a truly new concept is required

## Stage 3 — Record seeding
- create one support record per official surface
- mark unknowns honestly instead of filling rows with implied support
- link each record to its first baseline capture plan

## Stage 4 — Claude backfill
- map existing Claude evidence into one formal support record
- create the first release-gate artifact example
- confirm the support matrix summary language against that record

## Stage 5 — Current-output mapping
- document how doctor, readiness, probe, handoff, and attempt outputs map into the state and evidence model
- avoid immediate code rewrites where a mapping doc is enough to unblock future work

## Stage 6 — Second adapter launch
- choose the target surface
- create its first real implementation backlog slice
- record first capture and drift expectations up front

## Stage 7 — Drift and release discipline
- start baseline sweeps
- update support records when drift occurs
- use release-gate artifacts before strengthening claims

## Important rule

Do not treat the transition as “rewrite everything first.” The goal is to make the current system legible and evolvable while widening support deliberately.
