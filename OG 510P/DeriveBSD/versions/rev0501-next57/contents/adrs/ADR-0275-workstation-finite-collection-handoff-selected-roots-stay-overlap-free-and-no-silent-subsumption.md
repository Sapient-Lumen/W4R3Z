# ADR-0275: Workstation finite collection handoff selected roots stay overlap-free and no silent subsumption

Date: 2026-03-22  
Status: Accepted

## Context

`ADR-0263` fixed the first richer workstation transfer RFC target: a reviewed finite collection handoff.
`ADR-0264` fixed the first retrieve-width cut: single-retrieve by default and auto-stopping after the first successful retrieve.
`ADR-0265` fixed selected directories as snapshot-shaped membership instead of live tree authority.
`ADR-0266` fixed that reviewed snapshot membership stays manifest-first.
`ADR-0267` fixed that the first richer lane stays read-only only.
`ADR-0268` fixed the first member-kind floor: regular files plus explicit directories only, with symlinks/special objects out of scope.
`ADR-0269` fixed the first exact manifest-entry floor: normalized review path + member kind for every entry, plus exact payload digest + byte length for regular files.
`ADR-0270` fixed deterministic authoritative ordering by normalized review path.
`ADR-0271` fixed authoritative compact identity as the canonical manifest digest.
`ADR-0272` fixed the normalized review-path grammar itself.
`ADR-0273` fixed top-level reviewed names as explicit reviewed state instead of silent broker repair.
`ADR-0274` fixed authoritative manifest ancestry as explicit reviewed structure rather than retrieve-time implicit synthesis.

That still left one practical ambiguity inside `RFC-0194`:
**if a sender selects both an ancestor directory and one of its descendants, may the broker silently collapse that overlap into one reviewed root set, keep hidden overlap memory, or treat the descendant as redundant while claiming the same reviewed handoff?**

Leaving that open would keep the first richer lane portable in manifest bytes but not in reviewed root intent. One implementation might silently keep only the ancestor root, another might keep local “extra selected descendant” state that never reaches the authoritative artifact, and a third might prompt the user sometimes but auto-collapse in background flows. All three would claim to create the same reviewed finite collection while disagreeing about what root set the user actually reviewed.

## Decision

For the first reviewed finite collection handoff lane described by `RFC-0194`:

1. the accepted selected-root set is **authoritative reviewed state** even though descendant membership still expands into the authoritative manifest.
2. after normalized top-level naming plus any accepted reviewed aliasing, selected roots must form an **overlap-free antichain** in the reviewed namespace.
3. no selected root may be equal to, an ancestor of, or a descendant of another selected root in that accepted set.
4. if the sender proposes both an ancestor directory root and one of its descendants, the broker must **not silently**:
   - drop the descendant as redundant,
   - keep the descendant only as hidden local review memory,
   - or reinterpret the overlap as one larger reviewed snapshot without trusted review.
5. the trusted review surface may ask the user to revise the candidate selection until the accepted selected roots are overlap-free, but creation succeeds only once the final reviewed root set is already overlap-free.
6. if overlap remains after normalization and reviewed aliasing, handoff creation must **fail closed**.
7. preserving extra “this descendant was also separately selected” intent is **out of scope** for the first cut unless a later RFC defines a distinct reviewed-intent artifact instead of broker-local memory.

## Consequences

- The first richer lane now has one portable answer for selected-root intent, not just for manifest membership and manifest identity.
- Support/export no longer has to guess whether an explicitly separately selected descendant was silently collapsed into an ancestor directory root.
- The archive stays narrow: no new root-intent sidecar or special overlap markers are invented in the first cut.

## Alternatives considered

- **Silently let the ancestor win:** rejected because it makes reviewed root intent depend on broker-local redundancy heuristics.
- **Silently preserve descendant overlap as local UI memory only:** rejected because support/export would no longer be able to explain the reviewed root set from authoritative artifacts.
- **Add a special overlap marker or second reviewed-intent artifact now:** rejected because the queue is intentionally keeping the first richer lane small enough to implement before inventing new artifact families.
- **Ignore root overlap because the manifest bytes already cover the descendant:** rejected because explicit reviewed root intent would still vary across honest implementations even if leaf membership converged.

## Related

- `adrs/ADR-0263-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `adrs/ADR-0264-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md`
- `adrs/ADR-0265-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md`
- `adrs/ADR-0266-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md`
- `adrs/ADR-0267-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md`
- `adrs/ADR-0268-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md`
- `adrs/ADR-0269-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md`
- `adrs/ADR-0270-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md`
- `adrs/ADR-0271-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md`
- `adrs/ADR-0272-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md`
- `adrs/ADR-0273-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md`
- `adrs/ADR-0274-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md`
- `docs/685-workstation-finite-collection-handoff-selected-roots-stay-overlap-free-and-no-silent-subsumption.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
