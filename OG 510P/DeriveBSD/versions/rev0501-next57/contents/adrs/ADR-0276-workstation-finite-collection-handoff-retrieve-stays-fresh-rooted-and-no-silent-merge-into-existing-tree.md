# ADR-0276: Workstation finite collection handoff retrieve stays fresh-rooted and no silent merge into existing tree

Date: 2026-03-22  
Status: Accepted

## Context

`ADR-0263` fixed the first richer workstation transfer RFC target: a reviewed finite collection handoff.
`ADR-0264` fixed the first retrieve-width cut: single-retrieve by default and auto-stopping after the first successful retrieve.
`ADR-0265` fixed selected directories as snapshot-shaped reviewed membership, `ADR-0266` fixed manifest-first reviewed membership, `ADR-0267` fixed the first cut as read-only only, `ADR-0268` fixed the first member-kind floor as regular files plus explicit directories only, `ADR-0269` fixed the first manifest-entry floor as content-identity-first and stat-light, `ADR-0270` fixed canonical authoritative manifest order by normalized review path, `ADR-0271` fixed authoritative compact collection identity on the canonical manifest digest, `ADR-0272` fixed review-path normalization, `ADR-0273` fixed explicit top-level reviewed names, `ADR-0274` fixed authoritative manifest ancestor closure, and `ADR-0275` fixed the accepted selected-root set as overlap-free reviewed state.

That leaves one practical implementation seam still open: **where retrieve lands and what happens if local destination state already exists**.

Without a decision here, honest implementations can all claim to implement the same reviewed finite collection handoff while disagreeing about whether retrieve:
- materializes into a newly created destination root,
- merges into an existing directory tree,
- overwrites colliding names,
- auto-renames colliding names,
- or silently reuses an existing same-digest file as if no policy choice occurred.

That would put hidden receiver-local filesystem state back into the reviewed handoff story right after the archive spent several cuts making collection identity explicit and portable.

## Decision

For the first cut of the reviewed finite collection handoff:

1. each successful retrieve/materialization must land under a **fresh destination root** created for that retrieve.
2. the receiver must not silently materialize the reviewed collection into a pre-existing destination tree.
3. the receiver must not silently resolve collisions by overwrite, auto-rename, merge, or same-bytes reuse.
4. if the requested destination placement would reuse a pre-existing tree instead of producing a fresh destination root, retrieve must **fail closed** until the placement is revised.
5. implementation strategy remains open, but the user-visible / receipt-visible contract is one **fresh-rooted reviewed retrieve**, not a merge into local namespace history.

## Consequences

### Positive

- keeps reviewed collection identity separate from receiver-local tree state
- prevents overwrite/rename/skip policy from becoming hidden local folklore
- keeps receipts and support explanations boring and portable
- leaves room for a later explicit import/merge/promote lane without forcing it into the first retrieve cut

### Negative

- reduces convenience for users who expect “drop this into my existing folder” behavior
- may require trusted receive UI to create or confirm a fresh destination root instead of directly reusing a picked directory
- forces later explicit design work if merge/promote into an existing working tree proves important

### Follow-up

Future RFC/ADR work may still define:
- explicit import/promote/merge into a pre-existing working tree,
- richer collision policy under trusted review,
- or tighter receipt fields describing destination-root placement.

This ADR only fixes the first retrieve/materialization rule: **fresh-rooted, no silent merge into existing tree**.
