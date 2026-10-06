# ADR-0270: Workstation finite collection handoff manifest order stays canonical by review path

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

That still left one high-leverage ambiguity inside `RFC-0194`:
**if reviewed membership is an explicit manifest, what makes two honest implementations serialize the same reviewed set the same way?**

Without a hard answer here, one implementation will preserve source enumeration order, another will preserve selection order, and a third will bucket by member kind before sorting. That drift would make detached review, manifest digests, support bundles, and future compare/export surfaces noisier and harder to reproduce even when the reviewed set is identical.

## Decision

For the first reviewed finite collection handoff lane described by `RFC-0194`:

1. the authoritative per-member manifest must be **canonicalized by normalized review path**.
2. authoritative manifest entries must appear in **strict ascending bytewise order of normalized review path**.
3. review-path comparison must be **locale-independent** and must not depend on host collation rules.
4. duplicate normalized review paths are forbidden; attempting to materialize two authoritative entries for the same normalized review path must fail closed.
5. the authoritative manifest must not preserve source filesystem enumeration order, drag-selection order, UI presentation order, or member-kind bucket order as semantically meaningful state.
6. if implementations want to remember operator selection order or UI grouping later, that data must stay clearly **advisory** and outside the authoritative reviewed/exported membership surface.
7. any later attempt to standardize secondary display ordering, grouping metadata, or tree-summary ordering must return as an explicit follow-on RFC/ADR decision.

## Consequences

- The first richer lane now has a deterministic manifest ordering rule that supports reproducible review/export and clean digest stability.
- Detached support bundles and future diff/export tools can compare reviewed membership without depending on broker-local reconstruction or unstable host traversal order.
- The archive still does not standardize richer display/UI ordering semantics; path order is only the authoritative manifest serialization rule.

## Alternatives considered

- **Preserve source filesystem enumeration order:** rejected because traversal order is host/filesystem dependent and weakens reproducibility.
- **Preserve drag/drop or selection order:** rejected because it turns incidental UI behavior into authoritative review state and makes detached verification harder.
- **Bucket directories before files (or vice versa):** rejected because it adds extra ordering semantics without improving the first-cut review question.
- **Leave ordering unspecified:** rejected because manifest-first review without deterministic serialization still leaves export/digest behavior implementation-defined.

## Related

- `adrs/ADR-0263-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `adrs/ADR-0264-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md`
- `adrs/ADR-0265-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md`
- `adrs/ADR-0266-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md`
- `adrs/ADR-0267-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md`
- `adrs/ADR-0268-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md`
- `adrs/ADR-0269-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md`
- `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md`
- `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md`
- `docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
