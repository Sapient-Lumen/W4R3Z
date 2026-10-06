# Workstation finite collection handoff directory members stay snapshot-shaped and no live-tree traversal first

**Tier:** C (RFC shaping cut)  
**Profiles:** B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt

`docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md` already fixed the first richer workstation transfer queue, and `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md` already fixed the first retrieve-width cut inside that richer lane.

This doc makes the next small but hard decision inside that RFC queue explicit:
**in the first cut of the reviewed finite collection handoff, directory-shaped members stay snapshot-shaped rather than granting live tree traversal or persistent tree authority.**

See also:
- ADR: `adrs/ADR-0265-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md`
- Draft RFC: `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- queueing cut: `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- retrieve-width cut: `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md`
- distinct-family intake rule: `docs/672-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md`
- snapshot-representation cut: `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`

## Why this needs a hard decision

“Selected folder” sounds harmless, but it is exactly the kind of wording that turns a finite reviewed handoff into quiet namespace authority.
If the first richer lane lets the receiver browse a live directory tree after the review step, then the archive has effectively accepted a document-tree lane without admitting it.

The higher-leverage move is to keep the first richer lane honest:
**a selected directory should mean a reviewed finite snapshot-shaped member set, not a live tree grant.**

## Accepted cut

For the first cut of the reviewed finite collection handoff RFC:

- directory-shaped members are **snapshot-shaped**
- selecting a directory means a **reviewed finite member set at handoff creation time**
- the receiver gets **no live outward browse/traverse authority** beyond that reviewed member set
- later source-tree growth or live traversal is **not** part of the first cut
- any live-tree or persistent-directory lane must come back as an explicit follow-on RFC/ADR decision

That gives the archive a credible answer to “send this small folder snapshot there” without quietly normalizing document-tree authority as a convenience default.

## Why this is the right first cut

### 1) It keeps “finite collection” honest

The richer lane is supposed to solve selected-set handoff pressure.
Snapshot-shaped directory members preserve that story; live traversal would silently widen it into “and keep exploring the tree later.”

### 2) It keeps trusted review/export surfaces portable

Support/export surfaces can explain a bounded reviewed member set much more easily than a session-local story about what a receiver might have browsed later inside a live tree.

### 3) It stays aligned with import / working-copy / reintegration discipline

If the receiver wants to edit or promote something out of that reviewed set, the archive can still re-enter explicit import/working-copy/reintegration lanes instead of letting the richer handoff lane quietly become source-tree authority.

## What this still does not decide

This doc does **not** finalize the richer lane schema family.
The exact representation of snapshot membership now has a first-cut answer in `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md`: manifest-first, with tree/collection digest only supplementary.
It does **not** decide whether a much later live-tree lane is ever worth standardizing.
The first access-mode cut now has an explicit answer in `docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md`: the first richer finite-collection cut stays read-only only, and writable receive is deferred to a later separate decision.

Those remain RFC-level questions, but the archive no longer leaves first-cut directory semantics ambiguous.

## Related docs

- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`

Last updated: 2026-03-22r407
