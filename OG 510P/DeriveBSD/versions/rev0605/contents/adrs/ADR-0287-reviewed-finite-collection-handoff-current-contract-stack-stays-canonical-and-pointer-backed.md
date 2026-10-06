# ADR-0287: Reviewed finite-collection handoff current contract stack stays canonical and pointer-backed

- Status: Accepted
- Date: 2026-03-23

## Context

The recent reviewed finite-collection tightening cluster from `docs/674-*` through `docs/696-*` now carries a dense sequence of small laws around retrieve width, membership, manifest identity, profile scope, review-surface behavior, and local result evidence.
That density is good for precision, but it also creates the same archive-local failure mode that showed up earlier in publish sessions: nearby entry docs and numbered reviewed-finite-collection pages can start acting like stale partial companion lists.

DeriveBSD already prefers one exact law plus one exact checker over ambient folk memory.
The same discipline should now apply to the archive's own current-stack navigation for the reviewed finite-collection tightening cluster.

## Decision

We define `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md` as the canonical current-stack map for the recent reviewed finite-collection tightening cluster spanning `docs/674-*` through `docs/696-*`, with `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md` as the draft RFC entrypoint into that stack.

Main entry surfaces, the RFC, and nearby reviewed-finite-collection docs must point back to that canonical current-stack map instead of acting as free-form partial companion lists.

This is an archive-control decision only.
It does **not** widen the reviewed finite-collection handoff contract, reopen any closed lane question, or change artifact/schema semantics.

## Consequences

- Maintainers get one compact canonical map for the current reviewed finite-collection contract stack.
- Nearby docs stay locally useful without silently becoming stale partial registries.
- Archive hygiene can verify that the main entry surfaces, the RFC, and the recent numbered reviewed-finite-collection docs still point back to the current-stack map.
- This strengthens archive self-coherence at the point where the lane is close enough to implementation to deserve one stable reading order.
