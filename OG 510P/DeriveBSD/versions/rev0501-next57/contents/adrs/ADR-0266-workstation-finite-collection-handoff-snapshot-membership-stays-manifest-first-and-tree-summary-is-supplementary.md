# ADR-0266: Workstation finite collection handoff snapshot membership stays manifest-first and tree summary is supplementary

Date: 2026-03-22  
Status: Accepted

## Context

`ADR-0263` fixed the first richer workstation transfer RFC target: a reviewed finite collection handoff, with the draft design surface living in `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`.
`ADR-0264` then fixed the first retrieve-width cut inside that richer lane: single-retrieve by default, auto-stopping after the first successful retrieve.
`ADR-0265` then fixed the first directory-semantics cut: selected directories stay snapshot-shaped reviewed membership instead of becoming live tree authority.

That still left one high-leverage representation ambiguity open:
**how should the first richer lane represent reviewed snapshot membership — explicit per-member manifest, tree digest plus reviewed summary, or both?**

This matters because “snapshot-shaped” is still too vague if the receiver, trusted UI, detached receipts, or support/export surfaces cannot answer which exact members were reviewed and retrieved. A tree digest alone is a good compact summary, but it is not a sufficient first-cut review/export surface: it forces every human/debugging path back to broker-local reconstruction or a second artifact family before the lane is even implemented.

## Decision

For the first reviewed finite collection handoff lane described by `RFC-0194`:

1. reviewed snapshot membership stays **manifest-first**.
2. the first cut requires an **explicit per-member manifest** for the finite reviewed set.
3. directory-shaped members expand into explicit reviewed descendant-member entries at handoff creation time rather than staying represented only by a directory handle or only by a tree digest.
4. an aggregate tree/collection digest may be included as **supplementary summary evidence**, but it does **not** replace the explicit reviewed member manifest in the first cut.
5. any later attempt to use tree-digest-only, summary-only, or browse-later reconstruction as the ordinary first-cut membership surface must come back as an explicit follow-on RFC/ADR decision.

## Consequences

- The first richer lane stays legible to trusted UI, detached receipts, support/export, and offline forensic tooling: the reviewed set is explicit instead of broker-local folklore.
- Snapshot-shaped directory membership remains honestly collection-shaped rather than drifting back toward “selected folder, details resolved later” convenience language.
- Aggregate digests are still useful, but only as compact joins/checksums on top of the explicit manifest rather than a substitute for it.

## Alternatives considered

- **Tree digest plus reviewed summary only:** rejected for the first cut because it leaves exact member identity recoverable only through extra reconstruction steps and weakens detached support/export.
- **Leave representation open for later:** rejected because implementation pressure would turn that ambiguity into product-local folklore before the archive had a portable answer.
- **Require only explicit top-level members and let directory descendants be implicit:** rejected because it reintroduces the same “selected folder means more than the review surface says” ambiguity that `ADR-0265` just removed.

## Related

- `adrs/ADR-0263-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `adrs/ADR-0264-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md`
- `adrs/ADR-0265-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md`
- `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md`
- `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md`
- `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
