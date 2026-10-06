# ADR-0205: Workstation stale supersession recovery stays denial-joined and head-pinned

Date: 2026-03-20
Status: Accepted

## Context

`ADR-0199` through `ADR-0204` now make imported-document source lineage explicit enough to implement without cheating:

- edited bytes first become a typed local successor candidate of the same authoritative origin,
- candidates are immutable snapshots,
- supersession is explicit instead of newest-wins,
- supersession is same-origin and self-describing,
- supersession is current-head exact and stale targets fail closed,
- stale-target denials carry the observed current head plus the boring recovery answer.

That still leaves one narrow but expensive ambiguity:
**what does the next act look like when the operator really is responding to that stale denial?**

If the archive leaves that open, implementations will drift toward one of three weak stories:

1. a later reintegration plan is just another generic supersession plan with no typed join back to the stale denial it answers,
2. retry tooling silently rebinds to whatever head is current at submit time instead of proving which observed head it intended to supersede,
3. support/export surfaces can prove that a stale denial happened, but not that a later success actually answered that exact denial/current-head pair.

That is too much lineage drift for DeriveBSD.
The next act should stay a **fresh explicit act**, but it should also stay **denial-joined** and **head-pinned**.

## Decision

1. `content.reintegrate.plan` and `content.reintegrate.receipt` now carry a required `recovery` object with:
   - `mode = none | from-stale-supersession-denial`
2. When `recovery.mode = from-stale-supersession-denial`, the act must also carry:
   - `stale_denial_receipt_digest`
   - `expected_current_receipt_digest`
   - `expected_current_candidate_digest`
   - `expected_current_authoritative_origin_digest`
3. That recovery object means:
   - this is a **fresh** explicit supersession act,
   - it is answering one exact stale denial,
   - and it is pinned to one exact observed current head.
4. In that recovery mode, the reintegration act must stay an explicit supersession act too:
   - `supersession.mode = supersede-prior-candidate`
   - `supersession.supersedes_receipt_digest` must match `recovery.expected_current_receipt_digest`
   - `supersession.superseded_candidate_digest` must match `recovery.expected_current_candidate_digest`
   - `supersession.superseded_authoritative_origin_digest` must match `recovery.expected_current_authoritative_origin_digest`
5. `mode = none` remains the ordinary path for reintegration acts that are not answering a stale-target denial.

## Consequences

- A stale denial stays durable evidence, but the next success can now also prove **which denial it answered**.
- Recovery does not degrade into a generic retry or ambient storage rediscovery story.
- Detached support/export tooling can follow one exact chain:
  stale denial → observed current head → fresh explicit supersession act pinned to that head.
- The archive still does **not** invent branching, merging, collaborative locking, or background retry/orchestration machinery.
