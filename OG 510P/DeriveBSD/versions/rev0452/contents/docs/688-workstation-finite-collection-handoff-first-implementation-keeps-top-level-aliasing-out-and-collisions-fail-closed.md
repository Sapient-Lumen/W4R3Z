# Workstation finite collection handoff first implementation keeps top-level aliasing out and collisions fail closed

**Tier:** C (RFC shaping cut)  
**Profiles:** B, C, D  
**Pillars:** reproducibility, operability  
**Patterns:** Broker→Lease→Receipt

`docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md` already fixed the first richer workstation transfer queue, `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md` already fixed the first retrieve-width cut inside that richer lane, `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md` already fixed the first directory-semantics cut, `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md` already fixed the first snapshot-representation cut, `docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md` already fixed the first access-mode cut, `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md` already fixed the first member-kind floor, `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md` already fixed the first exact manifest-entry floor, `docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md` already fixed deterministic authoritative manifest ordering, `docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md` already fixed the first authoritative compact collection identity, `docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md` already fixed normalized review-path grammar, `docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md` already fixed top-level reviewed names as explicit reviewed state, `docs/684-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md` already fixed authoritative manifest ancestry, `docs/685-workstation-finite-collection-handoff-selected-roots-stay-overlap-free-and-no-silent-subsumption.md` already fixed the accepted selected-root set as overlap-free reviewed state, `docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md` already fixed fresh-rooted retrieve/materialization, and `docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md` already fixed profile scope.

This doc makes the next small but hard decision inside that RFC queue explicit:
**the first implementation of the reviewed finite collection handoff does not support trusted-UI top-level aliasing, so multi-root basename collisions simply fail closed instead of reopening the first cut as a rename/disambiguation UI.**

See also:
- ADR: `adrs/ADR-0278-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md`
- Draft RFC: `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- top-level name cut: `docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md`
- selected-root cut: `docs/685-workstation-finite-collection-handoff-selected-roots-stay-overlap-free-and-no-silent-subsumption.md`
- retrieve/materialization cut: `docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md`
- profile-scope cut: `docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`

## Why this needs a hard decision

The archive already fixed one important naming boundary: top-level names are explicit reviewed state rather than silent broker repair.
But the first implementation was still carrying one more expensive maybe: should the trusted review surface also let the user rename colliding top-level roots at creation time?

That sounds small, but it changes the shape of the first implementation a lot:
- the first trusted review UI becomes a rename/disambiguation editor rather than a bounded review surface,
- the manifest/evidence story has to explain source names vs reviewed aliases before the basic lane even exists,
- and support/export inherits one more family of “what exactly was reviewed?” questions.

The higher-leverage move is to keep the first implementation boring:
**if top-level selected members collide after accepted normalization, fail closed and ask the user to revise the selection instead of turning the first cut into a reviewed rename tool.**

## Accepted cut

For the first implementation of the reviewed finite collection handoff RFC:

- trusted-UI top-level aliasing is **out of scope**
- the authoritative reviewed namespace uses normalized reviewed names directly
- the trusted review surface may explain basename collisions, but it does not mint reviewed alias state in the first implementation
- if two top-level selected members collapse to the same normalized reviewed name, handoff creation must **fail closed**
- any future alias/disambiguation support must return as a **later explicit RFC/ADR cut** with typed reviewed state and exact evidence/export semantics

That keeps the first implementation focused on reviewed membership, retrieve/materialization, and evidence rather than on disambiguation UX.

## Why this is the right first cut

### 1) It shrinks the first trusted UI to something earnable

The first implementation already has to review selected members, manifest-derived identity, bounded lifetime, and retrieve semantics.
Adding top-level alias editing would make the trusted UI significantly wider before the archive has proven the narrower lane.

### 2) It keeps support/export answers exact

A fail-closed collision answer is easy to explain later.
A partly-reviewed alias story adds more state to joins, receipts, and operator explanations before the archive knows it is worth the entropy.

### 3) It leaves the door open without paying for it now

If real practice later proves collision disambiguation is worth standardizing, the archive can still design it as an explicit reviewed state family.
The important first move is simply not to carry that cost inside the first implementation.

## What this still does not decide

This doc does **not** remove the earlier rule that top-level reviewed names are explicit reviewed state.
It does **not** decide later alias fields or UI if a future RFC earns them.
It does **not** decide richer advisory metadata for explaining collisions.
It does **not** widen the profile scope beyond B/C/D.

Those remain explicit follow-on questions, but the archive no longer leaves the first implementation's collision answer ambiguous.

## Related docs

- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md`
- `docs/685-workstation-finite-collection-handoff-selected-roots-stay-overlap-free-and-no-silent-subsumption.md`
- `docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md`
- `docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`

Last updated: 2026-03-23r427

For the canonical current-stack map over the recent `docs/674-*` through `docs/696-*` reviewed finite-collection tightening cluster, see `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full current companion list.
