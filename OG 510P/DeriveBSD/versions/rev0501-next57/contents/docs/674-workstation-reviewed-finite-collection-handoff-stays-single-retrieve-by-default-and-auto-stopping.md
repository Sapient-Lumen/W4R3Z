# Workstation reviewed finite collection handoff stays single-retrieve by default and auto-stopping

**Tier:** C (RFC shaping cut)  
**Profiles:** B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt  

`docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md` already fixed the first richer workstation transfer queue: if practice later forces one richer lane, start with a reviewed finite collection handoff rather than reopening the frozen ordinary baseline.

This doc makes the next small but hard decision inside that RFC queue explicit:
**the first cut of the reviewed finite collection handoff should be single-retrieve by default and the handoff session should auto-stop after the first successful retrieve.**

See also:
- ADR: `adrs/ADR-0264-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md`
- Draft RFC: `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- queueing cut: `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- distinct-family intake rule: `docs/672-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`

## Why this needs a hard decision

Once the archive finally admits one richer collection-shaped lane, there is strong convenience pressure to let the receiver retrieve it again and again “just for this session.”
That sounds small, but it silently widens replay authority, changes the support/export story, and makes the first richer lane harder to reason about before the archive has even finished defining the narrow path.

The higher-leverage move is to learn the richer **collection membership** problem first while keeping the initial **retrieve semantics** boring.

## Accepted cut

For the first cut of the reviewed finite collection handoff RFC:

- retrieval is **single-retrieve by default**
- the session **auto-stops after the first successful retrieve**
- repeated retrieve is **not** part of the first cut
- any later replay-friendly or repeated-retrieve posture must come back as an explicit follow-on RFC decision

That gives the archive a clear first richer answer to “send these selected objects there” without immediately turning that answer into session-local collection replay authority.

## Why this is the right first cut

### 1) It keeps replay semantics out of the first learning step

The archive still needs to settle collection membership, directory shaping, review surfaces, and import/working-copy joins. Adding repeated-retrieve authority to the first cut piles a second hard problem onto the first one.

### 2) It stays closer to the ordinary anti-replay posture

The ordinary reviewed transfer lane is deliberately one-shot. The first richer lane is already broader because it is collection-shaped. Keeping it single-retrieve by default prevents that broader lane from also becoming replay-friendly by inertia.

### 3) It keeps support/export evidence boring

A support bundle or detached receipt only needs to answer one simple story first: a reviewed finite set was retrieved once, then the session ended. That is easier to audit and explain than “maybe retrieved several times, maybe still live.”

## What this still does not decide

This doc does **not** finalize the richer lane schema family.
The first directory-member representation cut now has an explicit answer in `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md`: manifest-first reviewed membership, with tree/collection digest only supplementary.
The first access-mode cut now has an explicit answer in `docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md`: the first cut is read-only only, and writable receive is deferred to a separate follow-on decision.
It does **not** decide whether a much later repeated-retrieve posture is ever worth standardizing.

Those remain RFC-level questions, but the archive no longer leaves the default retrieve semantics ambiguous.

## Related docs

- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`

Last updated: 2026-03-23r428
For the canonical current-stack map over the recent `docs/674-*` through `docs/696-*` reviewed finite-collection tightening cluster, see `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full current companion list.
