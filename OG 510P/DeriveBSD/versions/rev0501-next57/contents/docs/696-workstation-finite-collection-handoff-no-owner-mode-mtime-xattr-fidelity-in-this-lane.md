# Workstation finite collection handoff keeps owner/mode/mtime/xattr fidelity out of this lane

**Tier:** C (RFC shaping cut)  
**Profiles:** B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt

`docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md` already fixed the first richer workstation transfer queue, `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md` already fixed the first retrieve-width cut inside that richer lane, `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md` already fixed the first directory-semantics cut, `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md` already fixed the first snapshot-representation cut, `docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md` already fixed the first access-mode cut, `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md` already fixed the first member-kind floor, `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md` already fixed the first exact manifest-entry floor, and `docs/690-workstation-finite-collection-handoff-advisory-mime-stays-optional-and-non-authoritative.md` already fixed advisory MIME as optional descriptive metadata instead of mandatory reviewed identity.

This doc makes the next small but hard decision inside that RFC queue explicit:
**owner/group, mode-bit, mtime, xattr, ACL, and similar filesystem-metadata fidelity stay out of this lane entirely.**

See also:
- ADR: `adrs/ADR-0286-workstation-finite-collection-handoff-no-owner-mode-mtime-xattr-fidelity-in-this-lane.md`
- Draft RFC: `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- manifest-floor cut: `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md`
- advisory-MIME cut: `docs/690-workstation-finite-collection-handoff-advisory-mime-stays-optional-and-non-authoritative.md`
- result-root receipt cut: `docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md`
- handle-first locator cut: `docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md`
- opaque handle cut: `docs/695-workstation-finite-collection-handoff-result-root-handle-stays-opaque-and-non-path-shaped.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`

## Why this needs a hard decision

The archive already made the first reviewed finite-collection lane path/kind/payload-first and kept advisory MIME non-authoritative.
But that still leaves an expensive fork point open if implementations are allowed to claim that owner/group, mode bits, mtimes, xattrs, ACLs, or similar filesystem metadata might later become part of the same portable reviewed contract.

That is the wrong place to grow.
Once those fields become normative in this lane, the archive is no longer defining a reviewed selected-set handoff; it is quietly defining a filesystem-preserving archive format with larger cross-platform normalization, materialization, and support burden.

## Accepted cut

For this reviewed finite-collection handoff lane:

- owner/group fidelity is **out of this lane entirely**
- mode-bit fidelity is **out of this lane entirely**
- mtime / last-modified fidelity is **out of this lane entirely**
- xattr / ACL / capability / other extended filesystem-metadata fidelity is **out of this lane entirely**
- retrieve/materialization may still apply receiver-local defaults or policy-controlled local metadata, but those outcomes are **receiver-local realization detail**, not portable reviewed state
- detached review/export/support should keep authority on reviewed path/kind/payload identity plus the already accepted exact fresh-root receipt and opaque receiver-local result-root handle
- any future filesystem-preserving lane must return as a **separate explicit RFC/ADR cut** instead of widening this lane

## Why this is the right cut

### 1) It keeps the first richer lane portable across B/C/D

The selected-set handoff needs one coherent portable story first.
That story is already path/kind/payload-first, read-only, fresh-rooted, and reviewable without host-private reconstruction.
Keeping owner/mode/mtime/xattr fidelity out of this lane preserves that portability across workstation, general-purpose, and appliance/regulatory shapes.

### 2) It keeps local realization policy local

Receivers will still materialize the reviewed collection onto real filesystems and may apply receiver-local defaults or policy-controlled local metadata while doing so.
That is acceptable as long as those local outcomes do not become sender-reviewed portable truth or detached-evidence authority for the handoff itself.

### 3) It prevents quiet archive-format creep

Once filesystem metadata preservation becomes normative here, the lane starts behaving like a filesystem-preserving archive format rather than a reviewed selected-set handoff.
That is a valid thing to design later if it earns its own RFC, but it is too large and too host-specific to smuggle into the first lane.

## What this still does not decide

This doc does **not** decide whether some later distinct artifact family should preserve richer filesystem metadata.
It does **not** standardize one receiver-local materialization policy for local owner/mode/time defaults.
It does **not** remove the already accepted optional descriptive metadata cuts such as advisory MIME or advisory display snapshots.

Those remain distinct questions, but the archive no longer leaves this reviewed handoff lane half-way between a selected-set transfer contract and a filesystem-preserving archive format.

## Related docs

- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md`
- `docs/690-workstation-finite-collection-handoff-advisory-mime-stays-optional-and-non-authoritative.md`
- `docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md`
- `docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md`
- `docs/695-workstation-finite-collection-handoff-result-root-handle-stays-opaque-and-non-path-shaped.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`

Last updated: 2026-03-23r428
For the canonical current-stack map over the recent `docs/674-*` through `docs/696-*` reviewed finite-collection tightening cluster, see `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full current companion list.
