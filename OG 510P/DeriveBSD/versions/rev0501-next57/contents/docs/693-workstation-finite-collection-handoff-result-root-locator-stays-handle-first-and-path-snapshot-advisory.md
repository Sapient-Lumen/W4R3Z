# Workstation finite collection handoff result-root locator stays handle-first and path-snapshot advisory

**Tier:** C (RFC shaping cut)  
**Profiles:** B, C, D  
**Pillars:** operability, isolation  
**Patterns:** Broker→Lease→Receipt

`docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md` already fixed the first richer workstation transfer queue, `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md` already fixed the first retrieve-width cut inside that richer lane, `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md` already fixed the first directory-semantics cut, `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md` already fixed the first snapshot-representation cut, `docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md` already fixed the first access-mode cut, `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md` already fixed the first member-kind floor, `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md` already fixed the first exact manifest-entry floor, `docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md` already fixed deterministic authoritative manifest ordering, `docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md` already fixed the first authoritative compact collection identity, `docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md` already fixed normalized review-path grammar, `docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md` already fixed top-level reviewed names as explicit reviewed state, `docs/684-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md` already fixed authoritative manifest ancestry, `docs/685-workstation-finite-collection-handoff-selected-roots-stay-overlap-free-and-no-silent-subsumption.md` already fixed the accepted selected-root set as overlap-free reviewed state, `docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md` already fixed fresh-rooted retrieve/materialization, `docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md` already fixed profile scope, `docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md` already fixed the first-implementation collision answer, `docs/689-workstation-finite-collection-handoff-review-ui-may-path-compress-deterministic-ancestor-only-runs.md` already fixed the first bounded legibility move, `docs/690-workstation-finite-collection-handoff-advisory-mime-stays-optional-and-non-authoritative.md` already fixed metadata posture, `docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md` already fixed success receipts on the exact created fresh root, and `docs/692-workstation-finite-collection-handoff-placement-hints-stay-advisory-and-receiver-local.md` already fixed placement hints as receiver-local advisory UI state instead of reviewed authority.

This doc makes the next small but consequential result-evidence decision explicit:
**the exact created fresh root should be evidenced through a receiver-local stable result-root handle first, while any path/display snapshot stays advisory only.**

See also:
- ADR: `adrs/ADR-0283-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md`
- draft RFC: `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- fresh-root retrieve cut: `docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md`
- result-root receipt cut: `docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md`
- placement-hint cut: `docs/692-workstation-finite-collection-handoff-placement-hints-stay-advisory-and-receiver-local.md`
- bookmark/capability analog: `docs/198-persistent-file-capabilities-bookmarks.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`

## Why this needs a hard decision

`docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md` already fixed **what** successful retrieve must prove.
But it intentionally left one seam open: **what kind of locator is that receipt supposed to carry?**

If the first implementation uses only mutable path strings, then a later rename, move, import, or folder relabel can keep competing with the original retrieve outcome.
Detached support/export would still end up trusting whichever path text happened to survive, instead of the original retrieve result itself.
That is too much ambiguity for a lane this close to implementable.

The archive already has a better posture available in nearby patterns: stable local handles or claim tickets first, human-readable path/display text second. The reviewed finite-collection lane should use the same move instead of quietly making raw path strings the real local authority story.

## Accepted cut

For the first cut of the reviewed finite-collection handoff family:

- a successful retrieve receipt carries a **receiver-local stable result-root handle** for the exact created fresh root
- that handle is the **authoritative local result locator** for the original retrieve outcome
- an optional path string, destination label, or display-path snapshot may appear, but it stays **advisory only**
- later rename/move/import/promote acts may mint successor receipts, but they do **not** retroactively redefine the original retrieve receipt's result-root handle
- the first cut does **not** require the handle to be portable across machines or profiles
- the first cut does **not** standardize one exact backend such as bookmark ids, document ids, filesystem handles, or database keys
- any later lane that wants sender-directed placement, portable destination paths, or bookmark-like long-term reopen semantics is a **later explicit RFC/ADR cut**
- `docs/695-workstation-finite-collection-handoff-result-root-handle-stays-opaque-and-non-path-shaped.md` then fixes the next loophole too: the authoritative result-root handle itself must stay **opaque and non-path-shaped** instead of quietly degrading into a path string with a better field name
- if an advisory path/display snapshot is emitted at all, it stays a **retrieve-frozen advisory display snapshot** rather than silently rewriting itself after later local rename/move/import/promote state

## Why this is the right next cut

### 1) It keeps support joined to the original retrieve outcome

The richer lane already fixed that successful retrieve must name the exact created fresh root.
A stable local handle makes that evidence durable enough for detached explanation without pretending mutable path text is the thing that crossed the boundary.

### 2) It preserves the placement-authority cut

`docs/692-workstation-finite-collection-handoff-placement-hints-stay-advisory-and-receiver-local.md` already fixed that chooser prompts and destination labels are not authoritative reviewed state.
This doc keeps the resulting receipt shape coherent too: the authoritative local result locator stays handle-first, and any human-facing path snapshot remains descriptive rather than authoritative.

### 3) It leaves redaction/export room without losing exactness

Some profiles may later want to suppress or redact local path text in exported evidence.
A receiver-local stable result-root handle keeps the original retrieve join exact even if display-path text becomes filtered, shortened, or absent on some support/export surfaces.

## What this still does not decide

This doc does **not** define final schema field names.
It does **not** require one specific storage backend for the authoritative handle.
It does **not** settle whether later import/promote/move receipts must carry explicit predecessor-handle joins.
It does **not** define profile-specific redaction rules for any optional path/display snapshot. `docs/694-workstation-finite-collection-handoff-advisory-display-snapshot-stays-retrieve-frozen.md` then fixes the next continuity answer too: when an optional path/display snapshot exists, it remains retrieve-frozen instead of becoming a moving current-location note.

Those remain follow-on questions, but the archive no longer leaves result-root evidence half-handle and half-path folklore.

## Related docs

- `docs/198-persistent-file-capabilities-bookmarks.md`
- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md`
- `docs/692-workstation-finite-collection-handoff-placement-hints-stay-advisory-and-receiver-local.md`
- `docs/694-workstation-finite-collection-handoff-advisory-display-snapshot-stays-retrieve-frozen.md`
- `docs/695-workstation-finite-collection-handoff-result-root-handle-stays-opaque-and-non-path-shaped.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`

Last updated: 2026-03-23r427

For the canonical current-stack map over the recent `docs/674-*` through `docs/696-*` reviewed finite-collection tightening cluster, see `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full current companion list.
