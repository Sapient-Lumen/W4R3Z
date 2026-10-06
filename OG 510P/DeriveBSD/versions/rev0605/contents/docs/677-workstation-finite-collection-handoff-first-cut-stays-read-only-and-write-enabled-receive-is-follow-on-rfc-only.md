# Workstation finite collection handoff first cut stays read-only and write-enabled receive is follow-on RFC only

**Tier:** C (RFC shaping cut)  
**Profiles:** B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote  

`docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md` already fixed the first richer workstation transfer queue, `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md` already fixed the first retrieve-width cut inside that richer lane, `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md` already fixed the first directory-semantics cut, and `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md` already fixed the first snapshot-representation cut.

This doc makes the next small but hard decision inside that RFC queue explicit:
**the first cut of the reviewed finite collection handoff stays read-only only, and any write-enabled receive must come back as a follow-on RFC/ADR decision rather than living inside the first cut.**

See also:
- ADR: `adrs/ADR-0267-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md`
- Draft RFC: `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- queueing cut: `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- retrieve-width cut: `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md`
- directory-semantics cut: `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md`
- snapshot-representation cut: `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md`
- distinct-family intake rule: `docs/672-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`

## Why this needs a hard decision

“Read-only by default” is still too soft if the first richer lane quietly keeps a narrowed write-enabled receive exception alive inside the same RFC.
That leaves the archive paying ongoing ambiguity costs for mutation authority, source writeback pressure, conflict handling, and support/export semantics before the narrow read-only path is even implemented.

The higher-leverage move is to cut that seam now:
**the first richer finite collection handoff should stay read-only only, and write-enabled receive should be deferred entirely out of the first cut.**

## Accepted cut

For the first cut of the reviewed finite collection handoff RFC:

- the lane is **read-only only**
- write-enabled receive is **not** part of the first cut
- receiver-side mutation should re-enter explicit import / working-copy / reintegration lanes
- any later writable collection lane must come back as a **follow-on RFC/ADR decision**
- any such later lane must remain **distinct-family** rather than widening the first-cut handoff family

That gives the archive a stable first richer answer to “send these selected objects there” without silently turning that answer into shared-folder or source-authority mutation semantics.

## Why this is the right first cut

### 1) It keeps the first richer lane implementable

The archive has now settled the exact first richer-family stack in `docs/698-reviewed-finite-collection-handoff-mints-exact-artifact-family-and-first-spec-stack.md`: `ui.collection.handoff.grant` / `ui.collection.handoff.manifest` / `ui.collection.handoff.receipt`. Pulling write-enabled receive into the same first cut would still add mutation, error, and conflict semantics before the narrower read-only path exists.

### 2) It preserves the existing authoring lanes

DeriveBSD already has explicit import / working-copy / reintegration lanes for mutation-shaped flows. Keeping the first richer handoff lane read-only only avoids partially duplicating those lanes under new collection-shaped wording.

### 3) It matches the narrower external lesson

XDG FileTransfer exists as a brokered transfer lane and defaults `writable` to `False`, while broader longer-lived writable document access is a different story in document-provider / SAF-style lanes. The lesson to steal is not “leave writable as a standing maybe”; it is “keep the first handoff lane narrow, and treat broader writable authority as a separate decision.”

## What this still does not decide

This doc now points at the accepted first richer lane schema family in `docs/698-reviewed-finite-collection-handoff-mints-exact-artifact-family-and-first-spec-stack.md`; it does **not** make writable receive part of that first stack.
It does **not** settle the smallest exact per-member field set.
It does **not** decide whether a much later writable collection lane is ever worth standardizing.
It does **not** decide whether profile A should ever support that later richer lane under explicit operator posture.

Those remain explicit follow-on questions, but the archive no longer leaves a write-enabled exception half-inside the first RFC cut.

## Related docs

- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md`
- `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md`
- `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`

Last updated: 2026-03-23r428
For the canonical current-stack map over the recent `docs/674-*` through `docs/696-*` reviewed finite-collection tightening cluster, see `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full current companion list.
