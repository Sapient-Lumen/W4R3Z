# Workstation finite collection handoff retrieve stays fresh-rooted and no silent merge into existing tree

**Tier:** C (RFC shaping cut)  
**Profiles:** B, C, D  
**Pillars:** reproducibility, operability  
**Patterns:** Broker→Lease→Receipt

`docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md` already fixed the first richer workstation transfer queue, `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md` already fixed the first retrieve-width cut inside that richer lane, `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md` already fixed the first directory-semantics cut, `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md` already fixed the first snapshot-representation cut, `docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md` already fixed the first access-mode cut, `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md` already fixed the first member-kind floor, `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md` already fixed the first exact manifest-entry floor, `docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md` already fixed deterministic authoritative manifest ordering, `docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md` already fixed the first authoritative compact collection identity, `docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md` already fixed normalized review-path grammar, `docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md` already fixed explicit top-level reviewed names, `docs/684-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md` already fixed ancestor-closed manifest structure, and `docs/685-workstation-finite-collection-handoff-selected-roots-stay-overlap-free-and-no-silent-subsumption.md` already fixed the accepted selected-root set.

This doc makes the next small but hard decision inside that RFC queue explicit:
**the first cut of the reviewed finite collection handoff now requires retrieve/materialization to land under a fresh destination root, so the receiver may not silently merge the reviewed collection into an existing tree, overwrite names, auto-rename around collisions, or treat “same bytes already there” as hidden acceptance policy.**

`docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md` then fixes the next result-evidence seam after this materialization cut: successful retrieve receipts must pin the exact created fresh root instead of leaving placement explanation to parent hints or support folklore; that later receipt cut therefore pins the exact created fresh root in evidence rather than only in operator memory. `docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md` then fixes the next locator seam too: the exact created fresh root is joined through a receiver-local stable result-root handle, while any path/display snapshot stays advisory instead of becoming mutable-path folklore. `docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md` then fixes the next product-scope seam after this materialization cut: the same richer family stays on B/C/D and out of fleet-host baseline, so host-side A workflows should keep using rollout/support/import-export/breakglass-shaped answers unless a distinct later operator lane is justified.

See also:
- ADR: `adrs/ADR-0276-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md`
- Draft RFC: `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- reviewed-root cut: `docs/685-workstation-finite-collection-handoff-selected-roots-stay-overlap-free-and-no-silent-subsumption.md`
- product-scope cut: `docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md`
- ancestor-closure cut: `docs/684-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`

## Why this needs a hard decision

The archive now says what the reviewed collection is: explicit manifest membership, canonical review paths, canonical ordering, canonical manifest digest, explicit top-level names, explicit parent directories, and overlap-free reviewed roots.
But two honest implementations can still behave differently at retrieve time while claiming the same reviewed handoff story:

- one materializes into a newly created destination root,
- one merges into a chosen existing directory tree,
- one overwrites existing names if bytes differ,
- one silently keeps the existing file if bytes happen to match,
- and one auto-renames collisions with copy-style suffixes.

Those are not harmless local differences.
They decide whether the receiver's existing tree becomes hidden authority, whether collision handling becomes local folklore, and whether support/export can later explain where the reviewed collection actually landed.

The narrower move is simpler:
**the first richer lane should retrieve into a fresh destination root and fail closed instead of silently merging the reviewed collection into pre-existing local state.**

## Accepted cut

For the first cut of the reviewed finite collection handoff RFC:

- each successful retrieve/materialization must land under a **fresh destination root** created for that retrieve
- the receiver must not silently target a pre-existing destination tree as the authoritative materialization root for the reviewed collection
- the receiver must not silently:
  - merge reviewed entries into an existing directory tree,
  - overwrite an existing file or directory,
  - auto-rename colliding paths with copy-style suffixes,
  - or short-circuit the collision because the existing bytes happen to match the reviewed payload digest
- destination-root creation remains an implementation detail, but the resulting reviewed materialization must behave as one **fresh-rooted retrieve**, not as a merge into pre-existing local namespace state
- trusted receive UI may still let the user pick or confirm where the fresh root should be created, but `docs/692-workstation-finite-collection-handoff-placement-hints-stay-advisory-and-receiver-local.md` now fixes the adjacent placement-authority seam too: any parent chooser, destination label, suggested folder, or save-into prompt remains receiver-local advisory UI state rather than reviewed authority, and if the requested placement would reuse a pre-existing tree instead of yielding a fresh destination root, the retrieve must **fail closed** until the placement is revised
- successful retrieve evidence for that created root is then kept handle-first by `docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md`, so detached support/export does not have to treat mutable path text as the authoritative local result locator
- receipts, support surfaces, and detached explanations should describe the retrieve as a fresh-rooted reviewed handoff rather than a merge/overwrite/rename story inferred from local filesystem behavior

That keeps retrieve policy boring and stops the receiver from becoming the hidden arbiter of which pre-existing local tree contents count as part of the reviewed result.

## Why this is the right first cut

### 1) It keeps reviewed collection identity separate from receiver local state

The archive already spent several cuts making collection identity explicit.
Letting retrieve merge into a pre-existing tree would immediately put hidden local namespace state back in charge of the result.

### 2) It avoids hidden overwrite, rename, and same-bytes reuse folklore

Overwriting, auto-renaming, or skipping because “the same bytes are already there” are all policy choices.
If they matter, they should come back later as explicit reviewed/import policy instead of piggybacking on the first retrieve cut.

### 3) It leaves room for later import/promote/merge lanes without forcing them now

A later lane can still standardize deliberate import into an existing working tree, promotion into a local project space, or explicit collision policy.
The first cut stays narrower: one reviewed collection, one fresh destination root, one receipt story.

## What this still does not decide

This doc does **not** define the final schema family.
It does **not** require a specific temp-dir + rename implementation strategy.
It does **not** define later explicit import/merge/promote behavior into a pre-existing working tree.
It does **not** change the earlier rules for reviewed membership, path grammar, selected roots, or manifest ancestry.

Those remain follow-on questions, but the archive no longer leaves retrieve-time merge policy to receiver folklore.

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
- `docs/685-workstation-finite-collection-handoff-selected-roots-stay-overlap-free-and-no-silent-subsumption.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`

Last updated: 2026-03-23r427

For the canonical current-stack map over the recent `docs/674-*` through `docs/696-*` reviewed finite-collection tightening cluster, see `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full current companion list.
