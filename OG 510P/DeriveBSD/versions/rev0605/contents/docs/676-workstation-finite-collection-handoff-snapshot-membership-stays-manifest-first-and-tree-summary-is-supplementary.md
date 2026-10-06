# Workstation finite collection handoff snapshot membership stays manifest-first and tree summary is supplementary

**Tier:** C (RFC shaping cut)  
**Profiles:** B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt

`docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md` already fixed the first richer workstation transfer queue, `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md` already fixed the first retrieve-width cut inside that richer lane, and `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md` already fixed the first directory-semantics cut.

This doc makes the next small but hard decision inside that RFC queue explicit:
**the first cut of the reviewed finite collection handoff keeps snapshot membership manifest-first, and any tree/collection digest stays supplementary summary evidence rather than the primary reviewed membership surface.**

See also:
- ADR: `adrs/ADR-0266-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md`
- Draft RFC: `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- queueing cut: `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- retrieve-width cut: `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md`
- directory-semantics cut: `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md`
- distinct-family intake rule: `docs/672-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`

## Why this needs a hard decision

“Snapshot-shaped” is still too soft if the first richer lane can represent reviewed membership only as a tree digest plus a short summary.
That would make the trusted review surface, detached receipts, and support/export story depend on broker-local reconstruction or a second hidden manifest path.

The higher-leverage move is to keep the first richer lane honest:
**the reviewed finite set should be explicit as a per-member manifest first, and any tree/collection digest should be supplementary rather than a substitute.**

## Accepted cut

For the first cut of the reviewed finite collection handoff RFC:

- snapshot membership is **manifest-first**
- the first cut requires an **explicit per-member manifest** for the reviewed finite set
- directory-shaped members expand into explicit reviewed descendant-member entries at handoff creation time
- aggregate tree/collection digests may exist as **supplementary summary evidence**
- tree-digest-only or summary-only membership representation is **not** part of the first cut

That gives the archive a portable answer to “what exact set was reviewed and retrieved?” without forcing humans or tooling to reconstruct membership from hidden broker state.

## Why this is the right first cut

### 1) It keeps the review surface explicit

A trusted review surface should be able to show the exact finite set that is being handed off. An explicit per-member manifest keeps that answer available without requiring later reconstruction.

### 2) It keeps detached support/export evidence useful

Support bundles, receipts, and offline forensic tooling can explain a bounded reviewed set much more easily when exact members are explicit in the handoff story instead of recoverable only through a tree digest and broker-local expansion.

### 3) It keeps selected directories honestly collection-shaped

`docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md` already said selected directories are reviewed finite membership, not live tree authority. Manifest-first representation finishes that cut by making the reviewed members explicit instead of leaving “selected folder” details implicit.

## What this still does not decide

This doc does **not** finalize the richer lane schema family.
It does **not** settle the smallest exact per-member field set.
It does **not** decide whether aggregate tree/collection digests become mandatory alongside the explicit manifest.
It does **not** decide whether a much later live-tree lane is ever worth standardizing.
The first access-mode cut now has an explicit answer in `docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md`: the first richer finite-collection cut stays read-only only, and writable receive is deferred to a later separate decision.

Those remain RFC-level questions, but the archive no longer leaves the first-cut snapshot-membership representation ambiguous.

## Related docs

- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md`
- `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`

Last updated: 2026-03-23r427

For the canonical current-stack map over the recent `docs/674-*` through `docs/696-*` reviewed finite-collection tightening cluster, see `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full current companion list.
