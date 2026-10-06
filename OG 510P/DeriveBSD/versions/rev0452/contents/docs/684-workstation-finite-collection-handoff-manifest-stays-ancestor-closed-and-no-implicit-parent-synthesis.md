# Workstation finite collection handoff manifest stays ancestor-closed and no implicit parent synthesis

**Tier:** C (RFC shaping cut)  
**Profiles:** B, C, D  
**Pillars:** reproducibility, operability  
**Patterns:** Broker→Lease→Receipt

`docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md` already fixed the first richer workstation transfer queue, `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md` already fixed the first retrieve-width cut inside that richer lane, `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md` already fixed the first directory-semantics cut, `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md` already fixed the first snapshot-representation cut, `docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md` already fixed the first access-mode cut, `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md` already fixed the first member-kind floor, `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md` already fixed the first exact manifest-entry floor, `docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md` already fixed deterministic authoritative manifest ordering, `docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md` already fixed the first authoritative compact collection identity, `docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md` already fixed normalized review-path grammar, and `docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md` already fixed top-level reviewed names as explicit reviewed state.

This doc makes the next small but hard decision inside that RFC queue explicit:
**the first cut of the reviewed finite collection handoff now keeps the authoritative manifest ancestor-closed, so parent directories are explicit reviewed structural state instead of retrieve-time implicit synthesis.**

See also:
- ADR: `adrs/ADR-0274-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md`
- Draft RFC: `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- top-level naming cut: `docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md`
- path-grammar cut: `docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md`
- manifest-order cut: `docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md`
- manifest-digest cut: `docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`

## Why this needs a hard decision

The archive now has a canonical per-member manifest, canonical ordering, canonical manifest digest, canonical path grammar, and explicit top-level naming rules. But those rules still left one structural loophole: they do not say whether parent directories of reviewed paths are themselves part of the authoritative reviewed artifact.

If parent directories remain implicit, honest implementations can still disagree in ways that change authoritative bytes and materialized structure:
- one broker can serialize only leaf files plus whatever directories were directly selected
- another can add some missing parents opportunistically during export
- another can reconstruct all ancestors during retrieve/materialization with host-default metadata

Those are not harmless implementation details. They change the authoritative manifest, its digest, and the exact structure the user actually reviewed.

The higher-leverage move is to keep the reviewed structure boring too:
**the first richer lane should keep the authoritative manifest ancestor-closed, and receivers should not silently synthesize missing parent directories later.**

## Accepted cut

For the first cut of the reviewed finite collection handoff RFC:

- the authoritative manifest is **ancestor-closed**
- for every manifest entry whose normalized `review_path` contains `/`, **every proper parent path** of that `review_path` must appear exactly once as an explicit `directory` member entry in the authoritative manifest
- those ancestor directory entries are **authoritative reviewed structural state**, not receiver-side reconstruction hints
- ancestor closure is derived from the final normalized reviewed namespace and must not be used to repair collisions, invent wrapper roots, or smuggle in hidden source-parent context
- receiver/import/materialization code must **not silently synthesize missing parent directories** beyond the destination root; a non-ancestor-closed authoritative manifest is invalid and should fail closed
- ancestor-only directory entries stay **stat-light** in the first cut: they carry `review_path` plus `member_kind = directory`, but not file-style payload digest, byte length, or required rich host-stat fidelity

That keeps the first richer lane structurally explicit without prematurely inflating directory metadata.

## Why this is the right first cut

### 1) It makes manifest-first review structurally honest

The archive already chose an explicit per-member manifest as the authoritative review/export surface. Ancestor closure is the next necessary step if that manifest is supposed to describe the reviewed collection rather than only its leaves.

### 2) It keeps canonical hashing aligned with the reviewed namespace

The archive already chose canonical ordering and one authoritative canonical-manifest digest. That compact identity should cover the reviewed directory spine too, not just whichever leaf rows or partially emitted ancestors a specific implementation happened to serialize.

### 3) It keeps retrieve/export from laundering structure through host defaults

Implicit parent reconstruction looks harmless until support/export, detached review, or restore tooling depends on which materializer recreated which directory tree. The first cut should keep that structural state in the reviewed artifact itself.

### 4) It stays compatible with the current stat-light directory posture

This decision does **not** require full directory metadata fidelity. The first cut still treats directories as explicit but stat-light, so the archive can tighten structure without reopening mode/mtime/xattr fidelity at the same time.

## What this still does not decide

This doc does **not** finalize the richer lane schema family.
It does **not** require a trusted review UI to display every deterministic ancestor row in fully expanded form; later UI work may still collapse ancestor-only directory rows for legibility.
It does **not** decide whether later restore/import lanes may attach richer advisory directory metadata.
It does **not** decide whether profile A should ever expose this richer lane under explicit operator posture.

Those remain explicit follow-on questions, but the archive no longer leaves parent-directory structure ambiguous.

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
- `docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md`
- `docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md`
- `docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md`
- `docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`

Last updated: 2026-03-23r427

For the canonical current-stack map over the recent `docs/674-*` through `docs/696-*` reviewed finite-collection tightening cluster, see `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full current companion list.
