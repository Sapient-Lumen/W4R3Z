# ADR-0269: Workstation finite collection handoff manifest entry floor stays content-identity-first and stat-light

Date: 2026-03-22  
Status: Accepted

## Context

`ADR-0263` fixed the first richer workstation transfer RFC target: a reviewed finite collection handoff.
`ADR-0264` fixed the first retrieve-width cut: single-retrieve by default and auto-stopping after the first successful retrieve.
`ADR-0265` fixed selected directories as snapshot-shaped membership instead of live tree authority.
`ADR-0266` fixed that reviewed snapshot membership stays manifest-first.
`ADR-0267` fixed that the first richer lane stays read-only only.
`ADR-0268` fixed the first member-kind floor: regular files plus explicit directories only, with symlinks/special objects out of scope.

That still left one high-leverage ambiguity inside `RFC-0194`:
**what is the smallest exact per-member field set for the reviewed manifest?**

Without a hard answer here, the first richer lane remains “manifest-first” only in prose while implementations drift into incompatible mixtures of path-only review, MIME-first heuristics, or full host-stat snapshots with timestamps/owners/modes/xattrs that are expensive to normalize and hard to keep portable.

## Decision

For the first reviewed finite collection handoff lane described by `RFC-0194`:

1. each manifest entry must carry a **normalized review path** that is unique within the reviewed collection.
2. each manifest entry must carry an exact **member kind** from the accepted first-cut vocabulary.
3. each regular-file entry must also carry exact **payload digest** and exact **byte length**.
4. explicit directory entries do **not** carry file-style payload digest / byte-length fields in the first cut.
5. MIME type, display labels, last-modified time, owner/group, mode bits, xattrs, thumbnails, and platform-specific stat fidelity are **not part of the required first-cut manifest floor**.
6. if advisory metadata such as MIME or display name is present later, it must stay clearly non-authoritative relative to path/kind/payload identity.
7. any later attempt to standardize richer stat fidelity, platform-specific metadata preservation, or writeback-oriented document capability flags must return as an explicit follow-on RFC/ADR decision.

## Consequences

- The first richer lane now has a small exact manifest floor that is concrete enough to implement and portable enough to export/support without hidden broker reconstruction.
- Trusted review can answer the boring but load-bearing questions first: **what path, what kind, and for files what exact bytes?**
- The archive does not yet take on expensive cross-platform normalization for mtimes, owners, mode bits, xattrs, or provider-specific capability flags.

## Alternatives considered

- **Path-only manifest entries:** rejected because review/export would not be able to prove exact file content identity or distinguish substituted bytes from stable names.
- **Make MIME type mandatory in the first cut:** rejected because MIME is useful but advisory, can be inferred inconsistently, and is weaker than exact payload identity as the first portable truth.
- **Carry full stat fidelity from day one:** rejected because it drags platform-specific metadata normalization and support burden into the first richer lane before the basic selected-set story is even implemented.
- **Use tree/collection digest only:** already rejected by `ADR-0266`; it would turn the manifest into prose while broker-local reconstruction stayed the real membership surface.

## Related

- `adrs/ADR-0263-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `adrs/ADR-0264-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md`
- `adrs/ADR-0265-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md`
- `adrs/ADR-0266-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md`
- `adrs/ADR-0267-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md`
- `adrs/ADR-0268-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md`
- `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md`
- `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md`
- `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
