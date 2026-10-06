# Workstation finite collection handoff manifest entry floor stays content-identity-first and stat-light

**Tier:** C (RFC shaping cut)  
**Profiles:** B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt

`docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md` already fixed the first richer workstation transfer queue, `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md` already fixed the first retrieve-width cut inside that richer lane, `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md` already fixed the first directory-semantics cut, `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md` already fixed the first snapshot-representation cut, `docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md` already fixed the first access-mode cut, and `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md` already fixed the first member-kind floor.

This doc makes the next small but hard decision inside that RFC queue explicit:
**the first cut of the reviewed finite collection handoff now has a small exact per-member manifest floor: normalized review path + member kind for every entry, plus exact payload digest + byte length for regular files, while richer stat fidelity stays out of the first cut.**

See also:
- ADR: `adrs/ADR-0269-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md`
- Draft RFC: `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- queueing cut: `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- retrieve-width cut: `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md`
- directory-semantics cut: `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md`
- manifest-first cut: `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md`
- member-kind floor: `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md`
- distinct-family intake rule: `docs/672-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`

## Why this needs a hard decision

“Manifest-first” is still too soft if the first richer lane does not say what a manifest entry must minimally contain.
Without that floor, one implementation will review only paths, another will treat MIME as the real identity, and a third will carry whole host-stat snapshots that are expensive to normalize and hard to keep portable across product shapes.

The higher-leverage move is to keep the first richer lane boring:
**the first reviewed manifest should carry only the fields needed to prove selected membership and exact file content identity, while richer metadata stays explicitly out of scope until it earns a later RFC.**

## Accepted cut

For the first cut of the reviewed finite collection handoff RFC:

- every manifest entry must carry a **normalized review path** that is unique within the reviewed collection
- every manifest entry must carry exact **member kind**
- every regular-file entry must carry exact **payload digest** and exact **byte length**
- explicit directory entries remain first-class reviewed members but do **not** carry file-style payload digest / byte-length fields in the first cut
- MIME type, display labels, last-modified time, owner/group, mode bits, xattrs, thumbnails, and platform-specific stat fidelity are **not required first-cut manifest fields**
- any advisory metadata that appears later must stay clearly non-authoritative relative to path/kind/payload identity

That gives the archive a portable answer to “what exact reviewed set was handed off?” without dragging filesystem-fidelity debates into the first richer lane.

## Why this is the right first cut

### 1) It keeps review and detached evidence exact where it matters most

For a reviewed file handoff, the load-bearing questions are simple: what member path was reviewed, what kind of member was it, and for files what exact bytes were approved? Path/kind/payload digest/byte length answer those directly.

### 2) It avoids platform-specific stat folklore

Full host-stat fidelity sounds precise, but in practice it pulls in platform-specific owner, mode, timestamp, and extended-attribute semantics that do not help the archive answer the first richer-lane question. Keeping the floor stat-light makes the lane easier to implement across B/C/D without inventing a filesystem-preservation subsystem.

### 3) It keeps advisory metadata advisory

Android’s SAF/document-provider model requires a narrow document metadata surface that includes display name, MIME type, size, and last-modified columns, while XDG’s FileTransfer lane stays even narrower and hands back a list of exported paths for the transfer session. DeriveBSD should steal the narrowing lesson, not the whole provider model: exact content identity belongs in the first reviewed manifest floor, while richer descriptive metadata stays optional and explicitly secondary.

## What this still does not decide

This doc does **not** finalize the richer lane schema family.
It does **not** decide whether advisory MIME type should become mandatory later.
It does **not** decide whether aggregate tree/collection digests become mandatory alongside the explicit manifest.
It does **not** decide whether a later lane should preserve owner/mode/mtime/xattr fidelity or other filesystem metadata.

Those remain explicit follow-on questions, but the archive no longer leaves the first-cut manifest entry floor ambiguous.

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
- `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`

Last updated: 2026-03-22r409
