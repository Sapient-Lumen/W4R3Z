# ADR-0202: Workstation candidate supersession stays same-origin and self-describing

Date: 2026-03-20
Status: Accepted

## Context

`ADR-0199` fixed the first source-lineage act for imported-document authoring:
`content.reintegrate.plan` / `content.reintegrate.receipt` register a **local successor candidate** for the **same authoritative origin** instead of replacing the source in place.
`ADR-0200` then fixed the next evidence boundary by making every candidate an **immutable snapshot**.
`ADR-0201` then fixed multi-candidate ordering by requiring **explicit supersession** and forbidding newest-wins behavior.

That still leaves one expensive ambiguity:
**what keeps an explicit supersession claim from jumping across authoritative origins or from becoming under-specified enough that detached support/export surfaces must reopen prior receipts just to learn what exact snapshot was superseded?**

If the archive leaves that open, the easiest implementation path will drift toward three bad shortcuts:

1. a newer candidate can claim to supersede an unrelated prior candidate just by pointing at some earlier receipt digest,
2. detached support/export tooling must reopen that prior receipt just to learn which snapshot bytes were displaced,
3. cross-origin or cross-document replacement pressure creeps back in through a superficially explicit but still under-specified supersession lane.

That would reintroduce exactly the kind of authority blur DeriveBSD has been removing from imported-document handling.

## Decision

1. Candidate supersession remains valid **only within the same authoritative origin**.
2. `content.reintegrate.plan.boundary` and `content.reintegrate.receipt.boundary` now carry one more required guarantee:
   - `supersession_scope = same-authoritative-origin-only`
3. When `supersession.mode = supersede-prior-candidate`, the supersession object must carry all of:
   - `supersedes_receipt_digest`
   - `superseded_candidate_digest`
   - `superseded_authoritative_origin_digest`
4. `superseded_authoritative_origin_digest` must equal the current `source.authoritative_origin_digest`.
5. A mismatched prior receipt / prior candidate / prior authoritative-origin claim must **not** silently downgrade to `mode = none` or to an unrelated sibling candidate registration. It is a deny/fail condition.

## Consequences

- Candidate supersession stays **same-origin-shaped**, not just **some-earlier-receipt-shaped**.
- Detached support/export surfaces can answer which exact prior snapshot was displaced without reopening the earlier receipt body first.
- App/cloud/finalization adapters still do not get to reinterpret reintegration as cross-document replace-in-place behavior.
- The archive remains free to add later review/finalization/promotion lanes without losing a digest-bound local candidate lineage floor.
