# ADR-0272: Workstation finite collection handoff review-path normalization stays relative-clean and NFC-canonical

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

That still left one high-leverage ambiguity inside `RFC-0194`:
**what exactly is a normalized review path before ordering, duplicate detection, and canonical-manifest hashing happen?**

Leaving that open would still let honest implementations disagree about whether leading slashes, repeated separators, trailing slashes, `.` / `..` cleanup, Unicode canonical-equivalence variants, or root-like placeholders are the same reviewed member. That would make the first richer lane harder to compare, harder to export, and easier to drift back toward filesystem-local path folklore even after the archive already decided that the reviewed set is explicit, canonical, and digest-bound.

## Decision

For the first reviewed finite collection handoff lane described by `RFC-0194`:

1. every manifest entry's `review_path` is a **collection-relative identity path**, not a destination-placement hint, materialization policy, or source writeback authority.
2. every normalized review path must be a **non-empty UTF-8 text string normalized to Unicode NFC**.
3. **`/` is the only separator** for normalized review paths. Backslash may appear only as an ordinary character; it is never a separator.
4. normalized review paths must have **no leading slash** and **no trailing slash**.
5. normalized review paths must have **no empty segments**, **no repeated separators**, and **no `.` or `..` segments**.
6. normalized review paths must not contain **U+0000 NUL**.
7. explicit directories are identified by **member kind**, not by a trailing slash marker.
8. if two source members collapse to the same normalized review path after applying these rules, handoff creation must **fail closed**.
9. case-folding, host-filesystem-specific path repair, percent-decoding, or destination-placement cleanup are **not** part of normalized review-path canonicalization in the first cut.

## Consequences

- The first richer lane now has a concrete path grammar that can actually support canonical ordering and manifest hashing across implementations.
- Review/export/support surfaces can compare the same reviewed finite set without silently depending on source filesystem cleanup rules.
- The first cut stays narrow: it is a reviewed collection handoff lane, not a raw-filesystem-fidelity or placement-policy lane.

## Alternatives considered

- **Leave normalized review path implicit:** rejected because canonical ordering and canonical-manifest digesting would still vary across implementations.
- **Treat review paths as raw host filesystem names with no Unicode normalization:** rejected because canonical-equivalence variants would remain a hidden portability and duplicate-detection seam.
- **Use trailing slash to distinguish directories:** rejected because `member_kind` already carries that meaning and trailing-slash folklore would reopen path-cleanup ambiguity.
- **Apply host-specific case folding or filesystem repair rules:** rejected because the first reviewed lane needs one portable archive rule, not a replay of whichever filesystem happened to source the handoff.

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
- `adrs/ADR-0271-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md`
- `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md`
- `docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md`
- `docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md`
- `docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
