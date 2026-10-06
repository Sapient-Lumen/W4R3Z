# Workstation finite collection handoff review UI may path-compress deterministic ancestor-only runs

**Tier:** C (RFC shaping cut)  
**Profiles:** B, C, D  
**Pillars:** operability, reproducibility  
**Patterns:** Broker→Lease→Receipt

`docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md` already fixed the first richer workstation transfer queue, `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md` already fixed the first retrieve-width cut inside that richer lane, `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md` already fixed the first directory-semantics cut, `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md` already fixed the first snapshot-representation cut, `docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md` already fixed the first access-mode cut, `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md` already fixed the first member-kind floor, `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md` already fixed the first exact manifest-entry floor, `docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md` already fixed deterministic authoritative manifest ordering, `docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md` already fixed the first authoritative compact collection identity, `docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md` already fixed normalized review-path grammar, `docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md` already fixed top-level reviewed names as explicit reviewed state, `docs/684-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md` already fixed authoritative manifest ancestry, `docs/685-workstation-finite-collection-handoff-selected-roots-stay-overlap-free-and-no-silent-subsumption.md` already fixed the accepted selected-root set as overlap-free reviewed state, `docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md` already fixed fresh-rooted retrieve/materialization, `docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md` already fixed profile scope, and `docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md` already fixed the first-implementation collision answer.

This doc makes the next small but hard review-surface decision explicit:
**trusted review UIs may visually path-compress deterministic ancestor-only directory runs for legibility, while the authoritative manifest itself stays fully explicit and ancestor-closed.**

See also:
- ADR: `adrs/ADR-0279-workstation-finite-collection-handoff-review-ui-may-path-compress-deterministic-ancestor-only-runs.md`
- Draft RFC: `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- ancestor-closure cut: `docs/684-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md`
- first-implementation collision cut: `docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`

## Why this needs a hard decision

The archive already decided that parent directories are explicit reviewed structural state.
That keeps the authoritative manifest honest, but it also makes the review surface noisier.
If every honest implementation reacts differently—one showing every ancestor row literally, one hiding them in breadcrumbs, one inventing ad hoc tree folding—then the first implementation still pays a support/explainability cost even though the artifact bytes are already coherent.

The high-leverage move is not to make the trusted UI into a full file manager.
It is to allow exactly one bounded compaction trick that is derivable from the authoritative manifest itself:
**compress purely structural ancestor-only path runs, but keep the manifest explicit and revealable.**

## Accepted cut

For the first implementation/review surface of the reviewed finite collection handoff family:

- the authoritative manifest remains **fully explicit and ancestor-closed**
- trusted review UIs **may** visually path-compress **deterministic ancestor-only directory runs**
- a collapsible run is a contiguous chain of explicit directory entries where each directory has exactly one reviewed child directory and no direct reviewed file children
- empty directories, branch points, and ordinary file rows remain individually visible
- collapsed presentation must be derived only from the authoritative manifest, not source-path breadcrumbs, hidden broker memory, or destination-placement state
- the trusted UI must be able to reveal the full explicit rows before approval/export/support
- support/export surfaces continue to treat the full authoritative manifest as the real reviewed state, not the collapsed shorthand
- any richer tree-editor/search/filter affordance is a **later explicit RFC/ADR cut**

## Why this is the right first cut

### 1) It reduces noise without changing authority

Ancestor closure is a structural truth of the reviewed artifact.
Path-compressing a deterministic directory chain can make that truth easier to read, but it should not become a different artifact.
This cut preserves that boundary.

### 2) It keeps the trusted UI smaller than a file manager

The archive does not need draggy tree editing, hidden lazy expansion, or source-path provenance breadcrumbs just to make a reviewed set legible.
A bounded path-compression rule gives implementations one humane move without reopening the whole UI surface.

### 3) It keeps support/export answers boring

Detached tooling, support bundles, and later receipts can continue to answer from the explicit manifest.
Nothing important depends on whether one trusted UI chose to show `a/b/c/` as three rows or one compressed path prefix.

## What this still does not decide

This doc does **not** make path-compression mandatory.
It does **not** standardize one exact detached-viewer rendering.
It does **not** add richer tree search/filtering or a file-manager-like editor to the trusted UI.
It does **not** change selected-root semantics, top-level collision handling, or fresh-rooted retrieve.

Those remain separate questions, but the archive no longer leaves the first review-surface compaction answer ambiguous.

## Related docs

- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `docs/684-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md`
- `docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`

Last updated: 2026-03-23r427

For the canonical current-stack map over the recent `docs/674-*` through `docs/696-*` reviewed finite-collection tightening cluster, see `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full current companion list.
