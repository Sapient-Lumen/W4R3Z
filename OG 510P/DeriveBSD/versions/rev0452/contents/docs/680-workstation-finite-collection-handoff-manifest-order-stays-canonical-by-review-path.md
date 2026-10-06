# Workstation finite collection handoff manifest order stays canonical by review path

**Tier:** C (RFC shaping cut)  
**Profiles:** B, C, D  
**Pillars:** reproducibility, operability  
**Patterns:** Broker→Lease→Receipt

`docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md` already fixed the first richer workstation transfer queue, `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md` already fixed the first retrieve-width cut inside that richer lane, `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md` already fixed the first directory-semantics cut, `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md` already fixed the first snapshot-representation cut, `docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md` already fixed the first access-mode cut, `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md` already fixed the first member-kind floor, and `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md` already fixed the first exact manifest-entry floor.

This doc makes the next small but hard decision inside that RFC queue explicit:
**the first cut of the reviewed finite collection handoff now serializes its authoritative per-member manifest in canonical normalized-review-path order, with duplicate review paths forbidden and any UI/source ordering kept non-authoritative.**

See also:
- ADR: `adrs/ADR-0270-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md`
- Draft RFC: `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- queueing cut: `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- retrieve-width cut: `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md`
- directory-semantics cut: `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md`
- manifest-first cut: `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md`
- member-kind floor: `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md`
- manifest-field floor: `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md`
- review-path grammar cut: `docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md`
- distinct-family intake rule: `docs/672-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`

## Why this needs a hard decision

“Manifest-first” plus “stat-light exact fields” is still too soft if the archive leaves ordering implicit.
Without a canonical ordering rule, one honest implementation will preserve source traversal order, another will preserve drag-selection order, and a third will emit directories before files. That makes manifest digests, detached review, compare/export, and support bundles noisier even when the reviewed finite set is identical.

The higher-leverage move is to keep the first richer lane boring:
**the authoritative reviewed manifest should sort only by normalized review path, in a locale-independent way, and duplicate review paths must fail closed. That path grammar is now explicitly collection-relative, clean slash-separated, and Unicode NFC.**

## Accepted cut

For the first cut of the reviewed finite collection handoff RFC:

- the authoritative per-member manifest is serialized in **strict ascending bytewise order of normalized review path**
- ordering is **locale-independent** and does not depend on host collation rules
- duplicate normalized review paths are forbidden and fail closed
- source traversal order, drag-selection order, display grouping, and member-kind bucket order are **not authoritative state**
- if later implementations preserve UI order for presentation, that data stays advisory and off the authoritative manifest surface

That gives the archive a portable answer to “what exact reviewed set was handed off, in what canonical serialized form?” without turning the first richer lane into a file-manager replay protocol.

## Why this is the right first cut

### 1) It supports reproducible detached evidence

The archive already treats receipts, digests, and exports as first-class support surfaces. Canonical path ordering keeps those surfaces stable across implementations for the same reviewed set.

### 2) It keeps incidental UI behavior out of the authority story

Selection order can matter for presentation, but it should not become hidden reviewed state. The authoritative question is the exact finite set, not how the user happened to click it.

### 3) It matches the archive’s deterministic-by-default posture

Reproducible-builds practice is blunt here: filesystem ordering and locale-sensitive sorting both create needless variance unless the build or export surface standardizes stable ordering. DeriveBSD should steal that lesson for the first reviewed collection manifest too.

## What this still does not decide

This doc does **not** finalize the richer lane schema family.
It does **not** decide whether aggregate tree/collection digests become mandatory alongside the explicit manifest.
It does **not** decide whether advisory MIME type should become mandatory later.
It does **not** decide whether a later lane should preserve owner/mode/mtime/xattr fidelity or any richer display ordering metadata.

Those remain explicit follow-on questions, but the archive no longer leaves authoritative manifest ordering ambiguous.

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
- `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`

Last updated: 2026-03-23r427

For the canonical current-stack map over the recent `docs/674-*` through `docs/696-*` reviewed finite-collection tightening cluster, see `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full current companion list.
