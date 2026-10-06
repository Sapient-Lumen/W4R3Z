# ADR-0265: Workstation finite collection handoff directory members stay snapshot-shaped and no live-tree traversal first

Date: 2026-03-22  
Status: Accepted

## Context

`ADR-0263` fixed the first richer workstation transfer RFC target: a reviewed finite collection handoff, with the draft design surface living in `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`.
`ADR-0264` then fixed the first retrieve-width cut inside that richer lane: single-retrieve by default, auto-stopping after the first successful retrieve.

That still left one high-leverage ambiguity open:
**when the first richer lane includes a selected directory, does that mean reviewed finite membership or live tree authority?**

This matters because “selected folder” language is one of the easiest ways for a narrow reviewed handoff to decay into ambient namespace authority. If the first richer lane silently grants browse/traverse authority over a live directory tree, the archive has effectively jumped from a reviewed finite collection handoff to a broader document-tree lane without admitting it.

## Decision

For the first reviewed finite collection handoff lane described by `RFC-0194`:

1. directory-shaped members in the first cut stay **snapshot-shaped**.
2. selecting a directory means a **reviewed finite member set at handoff creation time**, not live open-ended traversal of the source tree.
3. the receiver does **not** gain ambient browse/traverse authority outside the reviewed snapshot membership.
4. live tree traversal, persistent document-tree authority, or later source-tree growth visibility are **not part of the first cut** and must come back later as an explicit follow-on RFC/ADR decision.

## Consequences

- The first richer lane remains honestly collection-shaped instead of quietly becoming a tree-authority lane.
- Trusted UI, receipts, and support/export surfaces can explain one bounded story: a reviewed finite set of members crossed once, then the session ended.
- Later live-tree or bookmark-style access is still possible to discuss, but only as a visibly broader lane with its own authority and evidence burden.

## Alternatives considered

- **Treat selected directories as live traversal authority in the first cut:** rejected because it collapses the collection handoff lane into a broader namespace authority lane too early.
- **Leave directory semantics open for later:** rejected because implementation pressure would turn “selected folder” into product-local folklore before the archive had a portable answer.
- **Ban directories entirely in the first richer lane:** rejected because a reviewed directory snapshot is a credible and common selected-set handoff shape that stays much narrower than live tree authority.

## Related

- `adrs/ADR-0263-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `adrs/ADR-0264-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md`
- `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md`
- `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
