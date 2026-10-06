# ADR-0267: Workstation finite collection handoff first cut stays read-only and write-enabled receive is follow-on RFC only

Date: 2026-03-22  
Status: Accepted

## Context

`ADR-0263` fixed the first richer workstation transfer RFC target: a reviewed finite collection handoff, with the draft design surface living in `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`.
`ADR-0264` then fixed the first retrieve-width cut inside that richer lane: single-retrieve by default, auto-stopping after the first successful retrieve.
`ADR-0265` then fixed the first directory-semantics cut: selected directories stay snapshot-shaped reviewed membership instead of becoming live tree authority.
`ADR-0266` then fixed the first snapshot-representation cut: reviewed membership stays manifest-first, with any tree/collection digest only supplementary.

That still left one high-leverage access-mode ambiguity open:
**should the first reviewed finite collection handoff RFC keep a narrowed write-enabled receive exception inside the first cut, or should the first cut stay read-only only?**

This matters because write-enabled receive is not just “one more option.” It changes support/export expectations, mutation authority, conflict/error handling, and laundering pressure. The archive already has explicit import / working-copy / reintegration lanes for mutation-shaped flows; leaving a write-enabled exception inside the first richer handoff RFC would invite those responsibilities back into the handoff lane before the narrow read-only path is even implemented.

## Decision

For the first reviewed finite collection handoff lane described by `RFC-0194`:

1. the first cut stays **read-only only**.
2. no write-enabled receive exception is part of the first cut.
3. if write-enabled receive is ever worth designing, it must come back as a **follow-on RFC/ADR decision**, not as an option quietly retained inside the first cut.
4. receiver-side mutation should continue to re-enter explicit import / working-copy / reintegration lanes rather than turning the finite collection handoff lane itself into source-authority writeback or shared-folder semantics.
5. any later writable collection lane must remain distinct-family and must justify why the existing authoring lanes are insufficient.

## Consequences

- The first richer lane stays smaller and more implementation-ready: bounded reviewed collection membership + retrieve semantics can be implemented without also taking on writeback/mutation conflict semantics.
- The archive stops paying ongoing ambiguity costs for a “maybe writable later inside the same first lane” seam.
- Existing mutation lanes keep their role instead of being partially duplicated by the first richer handoff RFC.

## Alternatives considered

- **Keep a narrowed write-enabled exception inside the first RFC:** rejected because it preserves a standing scope-creep seam inside the first cut and weakens the boundary between handoff and authoring lanes.
- **Make the first richer lane write-enabled from day one:** rejected because it would blur handoff, import, working-copy, and reintegration before the archive has even implemented the simpler read-only path.
- **Leave write posture open for later without deciding now:** rejected because implementation pressure would turn that ambiguity into product-local folklore before the archive had a portable answer.

## Related

- `adrs/ADR-0263-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `adrs/ADR-0264-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md`
- `adrs/ADR-0265-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md`
- `adrs/ADR-0266-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md`
- `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md`
- `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md`
- `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md`
- `docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
