# ADR-0271: Workstation finite collection handoff authoritative collection identity stays digest-bound to canonical manifest

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
`ADR-0270` fixed deterministic authoritative ordering: the reviewed manifest serializes in canonical normalized-review-path order.

That still left one high-leverage ambiguity inside `RFC-0194`:
**what compact identity should grants, receipts, detached review, and support/export tooling bind to once the reviewed set is already an explicit canonical manifest?**

Leaving that open would force one implementation to recompute identity from source trees, another to hash UI-order JSON, and a third to treat optional tree-summary digests as the real compact handle. That would make the first richer lane harder to compare, harder to export, and easier to drift back toward broker-local reconstruction even after the archive already decided the reviewed set is manifest-first.

## Decision

For the first reviewed finite collection handoff lane described by `RFC-0194`:

1. the lane must carry one authoritative compact collection identity: an **authoritative manifest digest**.
2. that digest must be computed over the **canonical serialized authoritative per-member manifest**, after the accepted manifest-entry floor and canonical normalized-review-path ordering rules have been applied.
3. the canonical manifest serialization for this digest must use the archive's existing canonical JSON rule: **`sha256(utf8(JCS(authoritative_manifest)))`**.
4. grants, receipts, detached review, compare/export tooling, and support bundles should treat that authoritative manifest digest as the portable compact identity for the reviewed finite set.
5. aggregate tree/collection digests may still appear as **supplementary summary evidence**, but they do **not** replace the authoritative manifest digest in the first cut.
6. UI grouping, source traversal order, directory-summary digests, or implementation-local tree hashing must not become alternative authoritative compact identities for the same reviewed set.
7. the exact future field names can stay RFC work, but the requirement that the first cut is **digest-bound to the canonical manifest** is no longer optional.

## Consequences

- The first richer lane now has one compact, portable, content-addressed handle for the reviewed finite set without collapsing back into tree-hash folklore.
- Receipt joins and support/export tooling can name the exact reviewed collection without re-walking source trees or reconstructing UI state.
- Supplementary tree/collection summaries remain allowed, but they stay clearly secondary to the explicit manifest plus its canonical digest.

## Alternatives considered

- **Make tree/collection digest the only compact identity:** rejected because `ADR-0266` already fixed that reviewed membership is manifest-first; tree summaries cannot become the real authority surface by compact-handle convenience.
- **Leave compact identity implicit and let each implementation choose:** rejected because detached verification and compare/export would drift across implementations.
- **Wait for final schema names before deciding this:** rejected because the compact identity contract matters before schema polish, and the archive already has an accepted JCS digest pattern.
- **Use richer filesystem metadata or UI-order serialization as the compact identity input:** rejected because those reintroduce non-portable state the previous cuts already removed.

## Related

- `adrs/ADR-0022-canonical-json-jcs.md`
- `adrs/ADR-0263-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `adrs/ADR-0264-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md`
- `adrs/ADR-0265-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md`
- `adrs/ADR-0266-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md`
- `adrs/ADR-0267-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md`
- `adrs/ADR-0268-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md`
- `adrs/ADR-0269-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md`
- `adrs/ADR-0270-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md`
- `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md`
- `docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md`
- `docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
