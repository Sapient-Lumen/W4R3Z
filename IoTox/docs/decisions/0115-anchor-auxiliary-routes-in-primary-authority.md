# ADR 0115: anchor auxiliary routes in primary-session authority

Status: accepted

Date: 2026-08-21

## Decision

An auxiliary route cannot select the stable identity that authenticates it. The coordinator owns a
bounded route-binding registry populated only from independently authority-authenticated primary
sessions. Each trust record binds one expected remote stable principal, the exact primary peer Tox
key that a remote signed route set must name as coordinator, a minimum route-set generation, and the
primary online epoch that established the association.

For each local worker incarnation the registry accepts at most one route binding in one confirmed
auxiliary online epoch. A retry is idempotent only when its message identifier, signed route set,
binding artifact, worker incarnation, primary association, and online epoch are exact. Any conflict,
older epoch, foreign worker, or second binding in the epoch fails closed. A new worker incarnation
requires explicit retirement of the old entry.

The registry retains the highest accepted route set for each continuously trusted primary
association. It rejects an older generation and a different artifact at the same generation. Trust
replacement preserves that high-water state only when stable principal and coordinator Tox key are
unchanged; removal revokes associated worker admissions.

## Consequences

A self-signed auxiliary packet cannot nominate its own trust anchor, and a valid route set for an
unrelated primary peer cannot attach itself to a worker. Exact packet duplication is harmless while
same-epoch substitution and route-set forks are observable protocol failures. Bounds cap both trust
fan-out and retained worker state.

This registry is process-local. It does not claim durable remote-generation anti-rollback across a
complete host restore; a captured binding still cannot cross a fresh confirmed transcript. Live
supervisor dispatch, construction-gated feature advertisement, local binding creation, and
coordinator `authenticated`/`ready` transitions remain a subsequent slice.
