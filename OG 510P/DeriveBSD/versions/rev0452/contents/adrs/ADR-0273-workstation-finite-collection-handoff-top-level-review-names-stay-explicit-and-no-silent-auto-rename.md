# ADR-0273: Workstation finite collection handoff top-level review names stay explicit and no silent auto-rename

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

That still left one practical ambiguity inside `RFC-0194`:
**when a multi-root reviewed handoff contains two top-level selections whose names would collide, may the broker silently repair the names, insert a wrapper root, or append copy-style suffixes?**

Leaving that open would keep the first richer lane digest-bound in theory but still broker-shaped in practice. One implementation might auto-wrap the whole selection under `Transfer/`, another might append ` (2)` or ` copy`, and a third might prepend hidden parent names or source identifiers. All three would claim to serialize the same reviewed set while producing different manifest paths, different ordering, and different authoritative manifest digests.

## Decision

For the first reviewed finite collection handoff lane described by `RFC-0194`:

1. the reviewed collection has **one authoritative collection-relative namespace**, and every top-level selected source member contributes its first reviewed path segment inside that namespace.
2. top-level reviewed names are **reviewed state**, not broker-local repair output.
3. the broker must **not silently**:
   - inject a synthetic common wrapper root,
   - append copy-style or numeric de-duplication suffixes,
   - prepend hidden source identifiers, parent directories, volume labels, or other unreviewed disambiguators.
4. if the trusted review surface supports explicit disambiguation, it may accept a **user-reviewed top-level alias** for a selected source member, but that alias must itself satisfy the accepted normalized `review_path` grammar and must appear directly in the authoritative manifest.
5. if two top-level selected members would still collapse to the same normalized reviewed name after accepted normalization, handoff creation must **fail closed**.
6. source absolute paths, original parent directories, volume names, provider IDs, inode numbers, and other source-local disambiguators are **not** implicit parts of the authoritative reviewed namespace in the first cut.

## Consequences

- The first richer lane now has a portable answer for multi-root top-level naming, not just for per-entry path grammar after names already exist.
- Authoritative manifest order and authoritative manifest digest now remain stable even when a user selects multiple roots with clashing source basenames.
- The trusted UI may later offer explicit aliasing for operator ergonomics, but silent broker repair no longer changes the reviewed collection story behind the user's back.

## Alternatives considered

- **Silently append ` (2)` / `copy` / numeric suffixes:** rejected because it makes the authoritative reviewed namespace depend on broker/UI convenience policy.
- **Silently inject a synthetic wrapper root like `Transfer/` or `Selection/`:** rejected because it changes every manifest path and digest without making that namespace change explicit reviewed state.
- **Prepend hidden parent-directory or source-ID context automatically:** rejected because it launders source-local placement history into the reviewed/exported namespace without user review.
- **Fail closed with no reviewed alias path possible ever:** rejected because the archive wants to leave room for a later trusted-UI disambiguation affordance, as long as the final reviewed names themselves become authoritative manifest state.

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
- `docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md`
- `docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
