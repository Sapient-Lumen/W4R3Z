# Workstation finite collection handoff first cut rejects symlinks and special files

**Tier:** C (RFC shaping cut)  
**Profiles:** B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt

`docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md` already fixed the first richer workstation transfer queue, `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md` already fixed the first retrieve-width cut inside that richer lane, `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md` already fixed selected directories as snapshot-shaped membership, `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md` already fixed the lane as manifest-first, and `docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md` already fixed the first cut as read-only only.

This doc makes the next small but hard decision inside that RFC queue explicit:
**the first cut of the reviewed finite collection handoff rejects symlinks and special filesystem objects; it stays regular-files-plus-explicit-directories only.**

See also:
- ADR: `adrs/ADR-0268-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md`
- Draft RFC: `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- queueing cut: `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- retrieve-width cut: `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md`
- directory-semantics cut: `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md`
- snapshot-representation cut: `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md`
- access-mode cut: `docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md`
- distinct-family intake rule: `docs/672-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`

## Why this needs a hard decision

“Selected folder snapshot” still sounds simpler than it is.
If the first richer lane silently follows symlinks, preserves symlinks for later resolution, or tries to carry device nodes / FIFOs / sockets as ordinary collection members, then the archive has quietly reintroduced ambient namespace and active endpoint authority through a lane that is supposed to stay reviewable and boring.

The higher-leverage move is to keep the first richer lane honest:
**the first cut should carry only regular files and explicit directory entries, and unsupported member kinds should fail closed instead of being silently followed, preserved, or omitted.**

## Accepted cut

For the first cut of the reviewed finite collection handoff RFC:

- allowed reviewed member kinds are **regular files** and **explicit directories** only
- selected directories still expand into explicit reviewed descendant-member entries at handoff creation time
- **symlinks are not part of the first cut**
- **special filesystem objects are not part of the first cut**, including device nodes, FIFOs, sockets, and equivalent active or host-coupled objects
- unsupported member kinds **fail closed** or require explicit pre-normalization outside this lane
- the broker must not silently **follow**, **preserve for later resolution**, or **omit** unsupported member kinds
- any later symlink-preserving, symlink-following, special-object, or provider/virtual-object lane must come back as an explicit follow-on RFC/ADR decision

That gives the archive a portable answer to “send these selected objects there” without quietly turning “selected folder snapshot” into path-resolution or active-endpoint folklore.

## Why this is the right first cut

### 1) It keeps reviewed membership exact

Manifest-first review is only honest if the reviewed membership is exactly what the handoff lane will deliver. Silent symlink following or silent omission would make the reviewed set diverge from the actual authority surface.

### 2) It keeps active authority out of a file-handoff lane

Device nodes, FIFOs, sockets, and similar objects are not boring content. They are active or host-coupled authority surfaces, and they deserve a different review story than “these selected files/directories.”

### 3) It preserves directory snapshots without overbuilding

Explicit directory entries are still enough to preserve empty directories and explain directory shape in review/export, while keeping the first cut much smaller than a general filesystem-virtualization subsystem.

## What this still does not decide

This doc does **not** finalize the richer lane schema family.
It does **not** settle the full exact per-member field set beyond this member-kind floor.
It does **not** decide whether a much later lane should preserve symlink objects, follow symlinks under explicit policy, or carry special/provider-defined object kinds.
It does **not** decide whether aggregate tree/collection digests become mandatory alongside the explicit manifest.

Those remain RFC-level questions, but the archive no longer leaves the first-cut member-kind vocabulary ambiguous.

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
- `docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`

Last updated: 2026-03-22r409
