# ADR-0263: Workstation first richer data-transfer RFC target is reviewed finite collection handoff

Date: 2026-03-22  
Status: Accepted

## Context

`ADR-0261` froze the ordinary workstation `ui.datatransfer.*` family as the portable baseline, complete enough to implement, and `ADR-0262` fixed the intake rule that any richer transfer lane must mint a distinct artifact family instead of widening that ordinary one.

That leaves one practical archive-management question:
**if practice later forces exactly one richer workstation transfer lane, which lane should earn the first RFC instead of letting the archive reopen the ordinary baseline opportunistically?**

The archive has enough signal now to choose a priority without pretending to finish the richer design up front. The common pressure is not for ambient replay or persistent tree authority; it is for a reviewed way to hand off a finite selected set of files or directories between compartments without collapsing back into shared clipboard state, quiet writeback, or ambient document-provider authority.

## Decision

For the first richer workstation transfer RFC target:

1. the first richer lane to design is a **reviewed finite collection handoff** session.
2. that first richer lane is aimed primarily at profiles **B/C/D**, with later reuse elsewhere allowed only if the same narrow contract still fits.
3. the first RFC target stays **session-bounded**, **distinct-family**, and **read-only by default**.
4. the first RFC target is for a **finite selected set** of files and/or directories handed to one receiving lane, not for persistent directory authority, ambient shared mounts, background sync, or quiet source writeback.
5. this ADR does **not** accept a new schema family yet; it only fixes the priority. The actual richer-lane design work lives in `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md` until later acceptance.

## Consequences

- The archive now has a concrete next place to spend richer-lane design effort without reopening the frozen ordinary `ui.datatransfer.*` baseline.
- Practical “send these few files / this small folder” pressure gets a draft target before persistent document-tree or write-enabled lanes do.
- Future richer-lane debate becomes narrower: the next work is about how tight the reviewed finite collection handoff should be, not about whether the archive should go back to growing the ordinary baseline one clause at a time.

## Alternatives considered

- **Make multi-delivery clipboard or history the first richer lane:** rejected because it primarily widens replay semantics without solving the more common finite file/directory handoff pressure.
- **Make persistent document-tree authority the first richer lane:** rejected because it is broader, harder to audit, and easier to launder into ambient namespace authority than a reviewed finite collection handoff.
- **Leave the first richer lane unprioritized:** rejected because archive drift would keep reopening the frozen ordinary lane whenever practical pressure reappears.

## Related

- `adrs/ADR-0261-workstation-ordinary-datatransfer-baseline-stays-frozen-and-richer-lanes-are-rfc-first.md`
- `adrs/ADR-0262-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md`
- `docs/671-workstation-ordinary-datatransfer-baseline-stays-frozen-and-richer-lanes-are-rfc-first.md`
- `docs/672-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md`
- `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
