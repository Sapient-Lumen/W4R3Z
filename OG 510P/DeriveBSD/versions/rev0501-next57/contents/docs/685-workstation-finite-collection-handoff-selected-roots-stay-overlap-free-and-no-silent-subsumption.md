# Workstation finite collection handoff selected roots stay overlap-free and no silent subsumption

**Tier:** C (RFC shaping cut)  
**Profiles:** B, C, D  
**Pillars:** reproducibility, operability  
**Patterns:** Broker→Lease→Receipt

`docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md` already fixed the first richer workstation transfer queue, `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md` already fixed the first retrieve-width cut inside that richer lane, `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md` already fixed the first directory-semantics cut, `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md` already fixed the first snapshot-representation cut, `docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md` already fixed the first access-mode cut, `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md` already fixed the first member-kind floor, `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md` already fixed the first exact manifest-entry floor, `docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md` already fixed deterministic authoritative manifest ordering, `docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md` already fixed the first authoritative compact collection identity, `docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md` already fixed normalized review-path grammar, `docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md` already fixed explicit top-level reviewed names, and `docs/684-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md` already fixed ancestor-closed manifest structure.

This doc makes the next small but hard decision inside that RFC queue explicit:
**the reviewed finite collection handoff now requires the accepted selected-root set to stay overlap-free after normalization, so the broker may not silently subsume a selected descendant into an ancestor directory snapshot or keep hidden overlap state.**

`docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md` now narrows the first implementation cut further: because the first implementation keeps top-level aliasing out, overlap must be resolved by revising the reviewed selection rather than by minting reviewed alias state inside the first shipped UI.

See also:
- ADR: `adrs/ADR-0275-workstation-finite-collection-handoff-selected-roots-stay-overlap-free-and-no-silent-subsumption.md`
- Draft RFC: `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- top-level naming cut: `docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md`
- ancestor-closure cut: `docs/684-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`

## Why this needs a hard decision

The archive now has a canonical manifest, canonical ordering, canonical manifest digest, explicit top-level naming, and explicit parent-directory structure. But there is still one place where honest implementations can disagree while claiming the same reviewed handoff story: **selected-root overlap**.

If the sender selects `project/` and also separately selects `project/notes/todo.txt`, one implementation can:
- silently drop the descendant as redundant,
- silently remember that the descendant was “extra selected” in local UI state,
- or silently treat the overlap as harmless because the manifest expands the same bytes anyway.

Those are not just UX differences. They change what the trusted review surface is promising about the reviewed root set, what receipts can later explain about selection intent, and whether “a few selected things” quietly turned into “one larger selected tree plus hidden broker interpretation.”

The higher-leverage move is narrower:
**the reviewed finite collection handoff should keep its accepted selected roots prefix-free inside the normalized reviewed namespace and should fail closed rather than silently collapsing overlapping roots into one reviewed story.**

## Accepted cut

For the first cut of the reviewed finite collection handoff RFC:

- the accepted selected-root set is **authoritative reviewed state** even though the full descendant membership still expands into the authoritative manifest
- after normalized top-level naming, selected roots must form an **overlap-free antichain** in the reviewed namespace
- no selected root may be identical to, an ancestor of, or a descendant of another selected root in that accepted set
- if the sender proposes both an ancestor directory root and one of its descendants, the broker **must not silently**:
  - drop the descendant as redundant,
  - treat the descendant as extra emphasis only in local UI state,
  - or reinterpret the overlap as one larger reviewed directory snapshot without trusted review
- the trusted review surface may still ask the user to revise the selection until the accepted roots are overlap-free, but the final accepted reviewed state must already be overlap-free before handoff creation succeeds
- if overlap remains after normalization, handoff creation must **fail closed**
- preserving extra “this descendant was also separately clicked” intent is **out of scope** for the first cut unless a later RFC standardizes a distinct reviewed-intent artifact instead of hiding that state inside broker-local memory

That keeps the first richer lane explicit without inventing a second shadow meaning for the same manifest membership.

## Why this is the right first cut

### 1) It keeps reviewed root intent separate from manifest expansion

A directory root already expands to reviewed descendant membership. Treating an explicit separately selected descendant as silently “the same thing” would make root intent implementation-defined again right after the archive made manifest structure portable.

### 2) It avoids hidden “ancestor wins” folklore

Silently preferring the ancestor or silently preserving the descendant as hidden local state would make support/export explanations depend on broker memory instead of the reviewed artifact.

### 3) It leaves room for a later richer selection-intent artifact without forcing it now

If preserving overlapping click intent ever proves important, it can come back as a separate reviewed artifact or review surface. The first cut stays narrower: one accepted overlap-free root set, one explicit manifest, one digest-bound reviewed collection.

## What this still does not decide

This doc does **not** finalize the richer lane schema family.
It does **not** require a first implementation to expose separate root-set UI beyond whatever trusted review is needed to revise the selection until overlap is gone.
It does **not** define a later reviewed-intent artifact for “also separately selected descendant” semantics.
It does **not** change the rule that selected directories expand into explicit snapshot membership in the authoritative manifest.

Those remain follow-on questions, but the archive no longer leaves selected-root overlap to broker folklore.

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
- `docs/684-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- `docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md`

Last updated: 2026-03-23r427

For the canonical current-stack map over the recent `docs/674-*` through `docs/696-*` reviewed finite-collection tightening cluster, see `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full current companion list.
