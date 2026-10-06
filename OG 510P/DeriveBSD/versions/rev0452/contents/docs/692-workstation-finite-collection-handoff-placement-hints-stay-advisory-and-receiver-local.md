# Workstation finite collection handoff placement hints stay advisory and receiver-local

**Tier:** C (RFC shaping cut)  
**Profiles:** B, C, D  
**Pillars:** operability, isolation  
**Patterns:** Broker→Lease→Receipt

`docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md` already fixed the first richer workstation transfer queue, `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md` already fixed the first retrieve-width cut inside that richer lane, `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md` already fixed the first directory-semantics cut, `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md` already fixed the first snapshot-representation cut, `docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md` already fixed the first access-mode cut, `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md` already fixed the first member-kind floor, `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md` already fixed the first exact manifest-entry floor, `docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md` already fixed deterministic authoritative manifest ordering, `docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md` already fixed the first authoritative compact collection identity, `docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md` already fixed normalized review-path grammar, `docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md` already fixed top-level reviewed names as explicit reviewed state, `docs/684-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md` already fixed authoritative manifest ancestry, `docs/685-workstation-finite-collection-handoff-selected-roots-stay-overlap-free-and-no-silent-subsumption.md` already fixed the accepted selected-root set as overlap-free reviewed state, `docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md` already fixed fresh-rooted retrieve/materialization, `docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md` already fixed profile scope, `docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md` already fixed the first-implementation collision answer, `docs/689-workstation-finite-collection-handoff-review-ui-may-path-compress-deterministic-ancestor-only-runs.md` already fixed the first bounded legibility move, `docs/690-workstation-finite-collection-handoff-advisory-mime-stays-optional-and-non-authoritative.md` already fixed metadata posture, and `docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md` already fixed success receipts on the exact created fresh root.

This doc makes the next small but hard placement-authority decision explicit:
**parent chooser, destination label, suggested folder, or “save into …” affordances stay receiver-local advisory UI state and do not become authoritative reviewed state for the first richer lane.**

See also:
- ADR: `adrs/ADR-0282-workstation-finite-collection-handoff-placement-hints-stay-advisory-and-receiver-local.md`
- draft RFC: `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- fresh-root retrieve cut: `docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md`
- result-root receipt cut: `docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`

## Why this needs a hard decision

The archive already decided what the reviewed set is and what successful retrieve must prove.
If placement hints remain half-reviewed and half-local, the first implementation becomes muddier than it needs to be.
One implementation could make a sender-suggested parent folder authoritative, another could treat a destination label as review-surface state, and another could keep placement local-only while still claiming the same protocol.

That would quietly widen the richer lane from “reviewed finite collection handoff” into “reviewed collection plus receiver-side path policy”.
This archive should not make local namespace choices part of the first portable authority story unless it is willing to standardize them explicitly.

## Accepted cut

For the first cut of the reviewed finite-collection handoff family:

- any parent chooser, destination label, suggested folder, or “save into …” affordance stays **receiver-local advisory UI state**
- such placement hints are **not authoritative reviewed state**
- the grant, authoritative manifest, and receipt-visible reviewed identity stay complete without carrying a sender-directed destination parent or reviewed placement hint
- a successful retrieve receipt still pins the exact created fresh root, but that does **not** make the earlier chooser hint or destination prompt authoritative reviewed input
- implementations may offer local placement convenience UI, but verification, review, support/export joins, and detached explanation must not depend on parent-hint text or sender-directed path folklore
- any later lane that wants reviewed placement policy, sender-directed destination targets, or profile-specific drop-zone semantics is a **later explicit RFC/ADR cut**

## Why this is the right next cut

### 1) It keeps the first richer lane about reviewed collection identity

The archive already has enough work in the reviewed set itself.
Making destination-parent hints authoritative now would add local namespace policy to the same lane without earning a smaller or safer first contract.

### 2) It preserves the exact-result evidence story

`docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md` already fixed what successful retrieve has to prove.
This doc keeps the earlier chooser prompt from becoming a competing authority surface beside that exact result evidence. `docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md` then keeps the resulting receipt shape coherent too: the authoritative local result locator stays handle-first, and any display-path snapshot remains descriptive rather than authoritative. `docs/694-workstation-finite-collection-handoff-advisory-display-snapshot-stays-retrieve-frozen.md` then keeps that optional human-facing note stable too, so it remains a retrieve-frozen advisory display snapshot rather than a mutable current-location story.

### 3) It leaves room for later stronger placement lanes

Some later factory/regulatory or compatibility workflows may want typed placement policy.
That work is easier to evaluate honestly if it arrives as a separate deliberate cut instead of as quiet inflation of this baseline.

## What this still does not decide

This doc does **not** forbid implementations from offering a local parent chooser or destination label.
It does **not** define the final locator grammar for the exact created fresh root.
It does **not** decide later profile-specific export/redaction posture for local placement detail.
It does **not** settle whether some future lane should support sender-directed placement or typed import targets.

Those remain separate questions, but the archive no longer leaves first-cut placement authority ambiguous.

## Related docs

- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md`
- `docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md`
- `docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`

Last updated: 2026-03-23r427

For the canonical current-stack map over the recent `docs/674-*` through `docs/696-*` reviewed finite-collection tightening cluster, see `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full current companion list.
