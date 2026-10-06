# Reviewed finite-collection handoff current contract stack and stale entrypoint firewall
**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** B, C, D  
**Pillars:** operability  
**Patterns:** Registry→Diff→Gate, Bundles  

- Status: Accepted
- Date: 2026-03-23
- Tags: workstation, archive-control, discovery, hygiene, reviewed-finite-collection
- Related: `adrs/ADR-0287-reviewed-finite-collection-handoff-current-contract-stack-stays-canonical-and-pointer-backed.md`
Last updated: 2026-03-23r428

## What this changes

The recent reviewed finite-collection tightening cluster is now dense enough that nearby entry docs, the draft RFC, and numbered reviewed-finite-collection pages can accidentally turn into stale partial companion lists.

This document fixes one canonical **current-stack map** for the recent `docs/674-*` through `docs/698-*` reviewed finite-collection cluster and acts as a stale entrypoint firewall: local docs may stay useful, but they should point back here instead of each acting like the full current register.

This is archive-control first, but the stack it points at now includes the first exact artifact-family/spec-stack cut too.
It does **not** widen the reviewed finite-collection handoff lane or reopen any closed lane question; it keeps the accepted current stack discoverable, including the spec-facing cut now fixed in `docs/698-reviewed-finite-collection-handoff-mints-exact-artifact-family-and-first-spec-stack.md`.

## Canonical current-stack map

- `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
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
- `docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md`
- `docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md`
- `docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md`
- `docs/689-workstation-finite-collection-handoff-review-ui-may-path-compress-deterministic-ancestor-only-runs.md`
- `docs/690-workstation-finite-collection-handoff-advisory-mime-stays-optional-and-non-authoritative.md`
- `docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md`
- `docs/692-workstation-finite-collection-handoff-placement-hints-stay-advisory-and-receiver-local.md`
- `docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md`
- `docs/694-workstation-finite-collection-handoff-advisory-display-snapshot-stays-retrieve-frozen.md`
- `docs/695-workstation-finite-collection-handoff-result-root-handle-stays-opaque-and-non-path-shaped.md`
- `docs/696-workstation-finite-collection-handoff-no-owner-mode-mtime-xattr-fidelity-in-this-lane.md`
- `docs/698-reviewed-finite-collection-handoff-mints-exact-artifact-family-and-first-spec-stack.md`

## Why this is worth doing

Once a contract cluster gets dense enough, stale local summaries become their own form of ambiguity.
A maintainer following one adjacent reviewed-finite-collection doc should not have to guess whether its local companion list is current.
One compact canonical current-stack map is the smaller and safer floor.

## Wire-up points

- `README.md`
- `CHANGELOG.md`
- `docs/00-index.md`
- `docs/98-archive-hygiene.md`
- `docs/99-llm-runbook.md`
- `docs/110-juicy-os-lessons.md`
- `docs/266-open-questions-and-risk-register.md`
- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `tools/check_workstation_datatransfer_finite_collection_current_stack_contract.py`

The accepted first spec-facing family for this lane is now `ui.collection.handoff.grant`, `ui.collection.handoff.manifest`, and `ui.collection.handoff.receipt`: see `docs/698-reviewed-finite-collection-handoff-mints-exact-artifact-family-and-first-spec-stack.md` for the accepted portable `grant` / `manifest` / `receipt` stack and the matching schemas/examples.

## Related

- `adrs/ADR-0287-reviewed-finite-collection-handoff-current-contract-stack-stays-canonical-and-pointer-backed.md`
- `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- `docs/696-workstation-finite-collection-handoff-no-owner-mode-mtime-xattr-fidelity-in-this-lane.md`
- `docs/698-reviewed-finite-collection-handoff-mints-exact-artifact-family-and-first-spec-stack.md`
