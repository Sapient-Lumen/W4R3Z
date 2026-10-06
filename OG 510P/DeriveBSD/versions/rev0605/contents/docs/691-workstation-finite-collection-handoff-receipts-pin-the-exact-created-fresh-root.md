# Workstation finite collection handoff receipts pin the exact created fresh root

**Tier:** C (RFC shaping cut)  
**Profiles:** B, C, D  
**Pillars:** operability, reproducibility  
**Patterns:** Broker→Lease→Receipt

`docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md` already fixed the first richer workstation transfer queue, `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md` already fixed the first retrieve-width cut, `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md` already fixed selected directories as snapshot-shaped reviewed membership, `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md` already fixed manifest-first membership, `docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md` already fixed read-only-only first-cut posture, `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md` already fixed the first member-kind floor, `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md` already fixed the first exact manifest-entry floor, `docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md` already fixed canonical manifest ordering, `docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md` already fixed authoritative compact collection identity on the canonical manifest digest, `docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md` already fixed normalized review paths, `docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md` already fixed explicit top-level reviewed names, `docs/684-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md` already fixed authoritative ancestor closure, `docs/685-workstation-finite-collection-handoff-selected-roots-stay-overlap-free-and-no-silent-subsumption.md` already fixed overlap-free reviewed roots, `docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md` already fixed fresh-rooted retrieve/materialization, `docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md` already fixed product scope, `docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md` already fixed first-implementation collision posture, `docs/689-workstation-finite-collection-handoff-review-ui-may-path-compress-deterministic-ancestor-only-runs.md` already fixed bounded manifest-derived path compression, and `docs/690-workstation-finite-collection-handoff-advisory-mime-stays-optional-and-non-authoritative.md` already fixed MIME posture.

This doc makes the next small but expensive decision inside that same RFC queue explicit:
**a successful retrieve receipt for the richer finite-collection lane must pin the exact fresh destination root that was created, not just the manifest digest, a parent chooser hint, or vague success prose.**

See also:
- ADR: `adrs/ADR-0281-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md`
- draft RFC: `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- fresh-root retrieve cut: `docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md`
- authoritative manifest digest cut: `docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`

## Why this needs a hard decision

`docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md` already fixed where retrieve is allowed to land: under one fresh destination root, not as a merge into pre-existing local tree state.
But detached support/export still cannot answer **which** fresh root was created unless the receipt contract says so explicitly.

Without that cut, honest implementations can all claim the same reviewed handoff semantics while differing on what the evidence leaves behind:

- one receipt only repeats the manifest digest,
- one only echoes the parent directory the user picked,
- one only says “retrieve succeeded”,
- and one later points support at the tree's current location after rename/move/import instead of the original retrieve result.

Those are not harmless receipt-format differences.
They decide whether the archive's already accepted fresh-root rule is actually queryable or whether local broker history and operator notes become the real explanation surface.

## Accepted cut

For the first cut of the reviewed finite-collection handoff RFC:

- every successful retrieve/materialization receipt must pin the exact **created fresh destination root** for that retrieve
- the receipt-visible locator must name the **result root that was actually created**, not merely a parent chooser hint, destination label, or requested placement prompt
- later rename/move/import/promote actions may mint their own receipts, but they do **not** retroactively redefine the original retrieve receipt's result root
- detached tooling should be able to answer both **which reviewed manifest digest was retrieved** and **which fresh root was created** without reopening broker-local memory or local filesystem history
- exact local locator syntax remains an RFC/spec follow-on, but the portable contract is already fixed: **pathless success prose or parent-only placement evidence is insufficient**

That keeps the already accepted fresh-root materialization rule legible in the evidence plane instead of leaving the last mile of explanation to implementation folklore. `docs/692-workstation-finite-collection-handoff-placement-hints-stay-advisory-and-receiver-local.md` then fixes the adjacent authority seam too: the chooser hint or destination prompt authoritative story stays out of the first cut, so exact result-root evidence does not have to compete with local advisory placement UI. `docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md` then fixes the next locator seam too: the receipt-visible result locator now stays handle-first through a receiver-local stable result-root handle, while any path/display snapshot remains advisory instead of quietly becoming the real local authority story. `docs/694-workstation-finite-collection-handoff-advisory-display-snapshot-stays-retrieve-frozen.md` then fixes the next continuity seam too: when such advisory display text exists, it stays a retrieve-frozen advisory display snapshot rather than silently rewriting itself after later local moves or renames.

## Why this is the right next cut

### 1) It turns the fresh-root rule into evidence instead of aspiration

`docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md` already fixed the result shape.
This doc fixes the detached explanation surface so that rule survives past the moment of UI interaction.

### 2) It follows the archive's exact-join discipline

Elsewhere the archive keeps choosing exact digests or exact result pointers over later reconstruction folklore.
The richer collection lane should do the same: the manifest digest says **what reviewed set** crossed, and the result-root locator says **where that exact retrieve landed**.
Both matter.

### 3) It keeps later move/import/promote lanes honest

A later explicit import/promote lane may still move or integrate the created tree somewhere else.
That is fine, but it should mint a new receipt instead of silently rewriting the meaning of the original retrieve success record.

## What this still does not decide

The accepted first richer-family stack is now fixed in `docs/698-reviewed-finite-collection-handoff-mints-exact-artifact-family-and-first-spec-stack.md`; this doc only fixes what the `ui.collection.handoff.receipt` must prove about the created fresh root.
It does **not** require one specific storage backend or handle encoding for the authoritative local result locator.
It does **not** settle later export-redaction posture for local placement details.
It does **not** define later import/promote/move behavior.

Those remain follow-on questions, but the archive no longer leaves successful retrieve placement evidence pathless or parent-only.

## Related docs

- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md`
- `docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md`
- `docs/690-workstation-finite-collection-handoff-advisory-mime-stays-optional-and-non-authoritative.md`
- `docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`

Last updated: 2026-03-23r428
For the canonical current-stack map over the recent `docs/674-*` through `docs/696-*` reviewed finite-collection tightening cluster, see `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full current companion list.
