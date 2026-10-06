# Workstation finite collection handoff top-level review names stay explicit and no silent auto-rename

**Tier:** C (RFC shaping cut)  
**Profiles:** B, C, D  
**Pillars:** reproducibility, operability  
**Patterns:** Broker→Lease→Receipt

`docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md` already fixed the first richer workstation transfer queue, `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md` already fixed the first retrieve-width cut inside that richer lane, `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md` already fixed the first directory-semantics cut, `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md` already fixed the first snapshot-representation cut, `docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md` already fixed the first access-mode cut, `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md` already fixed the first member-kind floor, `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md` already fixed the first exact manifest-entry floor, `docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md` already fixed deterministic authoritative manifest ordering, `docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md` already fixed the first authoritative compact collection identity, and `docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md` already fixed normalized review-path grammar.

This doc makes the next small but hard decision inside that RFC queue explicit:
**the reviewed finite collection handoff now treats top-level reviewed names as explicit reviewed state, not silent broker repair output, so multi-root naming collisions cannot be hidden behind auto-rename folklore.**

`docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md` now narrows the first implementation cut further: the design still permits explicit reviewed aliases or fail closed, but the first implementation does **not** provide trusted-UI aliasing and therefore simply fails closed on top-level basename collisions.

See also:
- ADR: `adrs/ADR-0273-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md`
- Draft RFC: `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- path-grammar cut: `docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md`
- manifest-order cut: `docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md`
- manifest-digest cut: `docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`

## Why this needs a hard decision

The archive now has a canonical per-member manifest, canonical ordering, canonical manifest digest, and a precise normalized path grammar. But those rules still start **after** the broker has chosen the reviewed top-level names for the selected roots.

If top-level names remain implicit, honest implementations can still disagree in ways that change authoritative bytes:
- one broker can wrap the selection under `Transfer/`
- another can append ` (2)` or ` copy`
- another can prepend hidden parent paths or source IDs

Those are not harmless UI differences. They change `review_path`, manifest order, and authoritative manifest digest while pretending to serialize the same reviewed collection.

The higher-leverage move is to keep the namespace boring:
**the first richer lane should not silently repair multi-root naming collisions; if names need disambiguation, that disambiguation must itself become explicit reviewed state.**

## Accepted cut

For the first cut of the reviewed finite collection handoff RFC:

- the reviewed collection has **one authoritative collection-relative namespace**
- every top-level selected source member contributes its first reviewed path segment inside that namespace
- top-level reviewed names are **reviewed state**, not broker-local repair output
- the broker **must not silently** inject a synthetic wrapper root, append copy-style or numeric suffixes, or prepend hidden source identifiers / parent directories / volume labels as disambiguators
- if a later trusted review surface explicitly supports disambiguation, it may accept a **user-reviewed top-level alias** for a selected source member, but that alias must already satisfy the accepted normalized `review_path` grammar and must appear directly in the authoritative manifest
- if two top-level selected members still collapse to the same normalized reviewed name after accepted normalization, handoff creation must **fail closed**
- source absolute paths, original parent directories, volume names, provider IDs, inode numbers, and other source-local disambiguators stay **out of the authoritative reviewed namespace** in the first cut unless they are made explicit reviewed state through the final manifest paths themselves

That keeps the first richer lane reviewable without teaching it to depend on hidden broker naming policy.

## Why this is the right first cut

### 1) It makes canonical ordering and canonical-manifest hashing honest

The archive already decided that reviewed membership should be explicit, ordered, and digest-bound. Silent top-level rename policy would reintroduce hidden implementation state right where those rules start.

### 2) It keeps review/export identity separate from source-location folklore

The first richer lane is a reviewed handoff lane, not a source-path preservation or restore-placement protocol. Hidden parent-directory context and provider-local IDs should not quietly become reviewed namespace authority.

### 3) It leaves room for ergonomic disambiguation without making it ambient

A future trusted UI may still offer explicit aliases for practical multi-root handoff. The important first cut is narrower: any such alias must become reviewed manifest state, not a background broker convenience.

## What this still does not decide

This doc does **not** finalize the richer lane schema family.
It does **not** require the first implementation to offer aliasing UX; `docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md` now fixes the first implementation at fail-closed on collisions.
It does **not** decide whether a later import/materialization lane should preserve original source paths or provider IDs as advisory metadata.
It does **not** decide whether profile A should ever expose this richer lane under explicit operator posture.

Those remain explicit follow-on questions, but the archive no longer leaves top-level naming policy ambiguous.

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
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- `docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md`

Last updated: 2026-03-23r427

For the canonical current-stack map over the recent `docs/674-*` through `docs/696-*` reviewed finite-collection tightening cluster, see `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full current companion list.
