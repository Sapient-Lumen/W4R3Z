# ADR-0204: Workstation stale supersession denials carry current-head evidence and recovery target

Date: 2026-03-20
Status: Accepted

## Context

`ADR-0199` fixed the first source-lineage act for imported-document authoring:
`content.reintegrate.plan` / `content.reintegrate.receipt` register a **local successor candidate** for the **same authoritative origin** instead of replacing the source in place.
`ADR-0200` then fixed the next evidence boundary by making every candidate an **immutable snapshot**.
`ADR-0201` then fixed multi-candidate ordering by requiring **explicit supersession** and forbidding newest-wins behavior.
`ADR-0202` then fixed supersession scope and detached evidence by keeping supersession **same-origin** and **self-describing**.
`ADR-0203` then fixed freshness by making supersession **current-head exact** and requiring stale targets to **fail closed** instead of being rebound.

That still leaves one expensive operability gap:
**when a stale supersession request is denied, how do detached support/export/retry surfaces learn what the current head actually was without reopening ambient storage state or guessing from names/paths/timestamps?**

If the archive leaves that open, the easiest implementation path will drift toward three bad shortcuts:

1. stale-target denial becomes a generic message string, leaving operators to rediscover the live predecessor from external storage state,
2. detached support bundles can prove that a request went stale but cannot name the current candidate that won,
3. retry tooling is tempted to “helpfully” rebuild the act against whatever now looks current instead of requiring a fresh explicit supersession plan.

That is too much ambiguity for DeriveBSD’s evidence model.
If stale supersession is a real first-class denial, the denial should also carry the exact current-head evidence and the boring recovery answer.

## Decision

1. `content.reintegrate.plan.boundary` and `content.reintegrate.receipt.boundary` now carry two more required guarantees:
   - `stale_target_evidence = observed-current-head-required`
   - `stale_target_recovery = fresh-explicit-supersession-required`
2. `content.reintegrate.receipt.result` now allows a typed stale-target denial profile with:
   - `reason_code = stale-supersession-target`
   - `recovery_posture = fresh-explicit-supersession-required`
   - `observed_current_receipt_digest`
   - `observed_current_candidate_digest`
   - `observed_current_authoritative_origin_digest`
3. When `supersession.mode = supersede-prior-candidate` and apply loses because the named predecessor is no longer the current unsuperseded candidate, the receipt must stay a **deny** and must carry that observed current-head summary.
4. That denial must not silently collapse into:
   - an ambient lookup requirement,
   - an implicit rebind to the observed current head,
   - or an evidence-light “try again later” story.

## Consequences

- Stale supersession remains a real denial, but detached tooling now gets one queryable answer for **what beat me**.
- Support bundles can prove both sides of the race: the rejected target and the observed current head that made the request stale.
- Retry tooling gets a stable recovery target without mutating the durable denial into a success or auto-rewrite story.
- The local candidate lane remains linear and compare-and-swap-shaped without inventing branch/merge or collaborative locking subsystems.
