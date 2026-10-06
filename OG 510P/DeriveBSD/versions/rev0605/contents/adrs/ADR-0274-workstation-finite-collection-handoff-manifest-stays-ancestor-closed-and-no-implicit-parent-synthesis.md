# ADR-0274: Workstation finite collection handoff manifest stays ancestor-closed and no implicit parent synthesis

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

That still left one practical ambiguity inside `RFC-0194`:
**are parent directories of reviewed paths authoritative reviewed state, or may a receiver silently synthesize them later while still claiming to materialize the same reviewed finite collection?**

Leaving that open would keep the first richer lane explicit in theory but not in actual structure. One implementation might serialize only leaf files plus selected top-level directories, another might add some ancestors opportunistically, and a third might recreate all missing parents at retrieve/export time with host-default metadata. All three would claim to serialize the same reviewed collection while disagreeing about the exact authoritative manifest, the exact manifest digest, and whether a receiver is reconstructing structure that the user never actually reviewed.

## Decision

For the first reviewed finite collection handoff lane described by `RFC-0194`:

1. the authoritative manifest is **ancestor-closed**.
2. for every manifest entry whose normalized `review_path` contains `/`, **every proper parent path** of that `review_path` must appear exactly once in the authoritative manifest as an explicit `directory` member entry.
3. those ancestor directory entries are **authoritative reviewed structural state**, not receiver-side reconstruction hints.
4. ancestor closure is derived from the final normalized reviewed namespace: it must not be used to repair top-level collisions, invent wrapper roots, or smuggle in hidden source-parent context.
5. receiver/import/materialization code must **not silently synthesize missing parent directories** beyond the destination root when materializing the reviewed collection; if the authoritative manifest is not ancestor-closed, creation/validation should fail closed instead.
6. ancestor-only directory entries remain **stat-light** in the first cut: they carry `review_path` plus `member_kind = directory`, but no file-style payload digest, byte length, or required host-stat fidelity.

## Consequences

- The first richer lane now has one portable answer for collection structure, not just for leaf membership, path grammar, ordering, and compact identity.
- Canonical manifest ordering and manifest-digest identity now cover the reviewed directory spine too, so support/export no longer depends on receiver-side parent reconstruction folklore.
- Implementations may still choose to visually collapse deterministic ancestor-only directory rows in trusted review UIs later, but they may not omit them from the authoritative manifest without changing reviewed state.

## Alternatives considered

- **Let receivers synthesize missing parents during retrieve/export:** rejected because it makes reviewed structure depend on materializer behavior and host defaults instead of the authoritative manifest.
- **Allow partial ancestor emission as an optimization:** rejected because it keeps manifest shape implementation-defined and makes compact identity disagree across honest implementations.
- **Store ancestors only in a supplementary tree summary:** rejected because the archive already chose the explicit per-member manifest as the authoritative review/export surface.
- **Promote full directory metadata now:** rejected because the current queue is intentionally keeping directories explicit but stat-light until richer metadata proves its value in a later RFC.

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
- `docs/684-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
