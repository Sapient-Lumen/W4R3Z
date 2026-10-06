# ADR-0203: Workstation candidate supersession stays head-exact and stale-target fail-closed

Date: 2026-03-20
Status: Accepted

## Context

`ADR-0199` fixed the first source-lineage act for imported-document authoring:
`content.reintegrate.plan` / `content.reintegrate.receipt` register a **local successor candidate** for the **same authoritative origin** instead of replacing the source in place.
`ADR-0200` then fixed the next evidence boundary by making every candidate an **immutable snapshot**.
`ADR-0201` then fixed multi-candidate ordering by requiring **explicit supersession** and forbidding newest-wins behavior.
`ADR-0202` then fixed supersession scope and detached evidence by keeping supersession **same-origin** and **self-describing**.

That still leaves one expensive ambiguity:
**what keeps a stale or already-displaced prior candidate from being superseded again later, or from being silently retargeted to whatever candidate currently looks latest?**

If the archive leaves that open, the easiest implementation path will drift toward three bad shortcuts:

1. two later candidates can both claim to supersede the same earlier candidate, turning one local lineage into a retroactively rethreadable graph,
2. a stale supersession request can be silently rebound to a newer candidate head because the implementation decides “the user probably meant the current one”,
3. support/export tooling has to infer whether a supersession acted on the current live predecessor or on a stale historical candidate.

That is too much ambiguity for DeriveBSD’s local source-lineage floor.
The supersession act should behave more like compare-and-swap than like best-effort relinking.

## Decision

1. Candidate supersession remains valid only when the named prior candidate is the **current unsuperseded candidate** for that authoritative origin.
2. `content.reintegrate.plan.boundary` and `content.reintegrate.receipt.boundary` now carry two more required guarantees:
   - `supersession_target_posture = current-unsuperseded-candidate-only`
   - `stale_target_handling = fail-closed`
3. If `supersession.mode = supersede-prior-candidate`, the named `supersedes_receipt_digest` / `superseded_candidate_digest` pair must still describe the active unsuperseded candidate for the same authoritative origin at apply time.
4. If that earlier candidate has already been superseded, or if another candidate became current first, the act must **deny/fail**. It must not silently:
   - retarget to a newer candidate,
   - register a sibling candidate as though supersession succeeded,
   - or rewrite the lineage into a branch/merge story.

## Consequences

- Explicit supersession becomes **head-exact** instead of merely **some-earlier-candidate-shaped**.
- The local supersession lane behaves like a digest-bound compare-and-swap over one current unsuperseded predecessor.
- Concurrent/local race outcomes stay explainable: one candidate can win, and stale attempts fail closed instead of being normalized later.
- The archive remains free to add future branch/merge or approval/finalization lanes, but those must be explicit later topics rather than accidental behavior of the v0 reintegration lane.
