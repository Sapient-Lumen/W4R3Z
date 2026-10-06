# Workstation finite collection handoff result-root handle stays opaque and non-path-shaped

**Tier:** C (RFC shaping cut)  
**Profiles:** B, C, D  
**Pillars:** operability, isolation  
**Patterns:** Broker→Lease→Receipt

`docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md` already fixed the first richer workstation transfer queue, `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md` already fixed the first retrieve-width cut inside that richer lane, `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md` already fixed the first directory-semantics cut, `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md` already fixed the first snapshot-representation cut, `docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md` already fixed the first access-mode cut, `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md` already fixed the first member-kind floor, `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md` already fixed the first exact manifest-entry floor, `docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md` already fixed deterministic authoritative manifest ordering, `docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md` already fixed the first authoritative compact collection identity, `docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md` already fixed normalized review-path grammar, `docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md` already fixed top-level reviewed names as explicit reviewed state, `docs/684-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md` already fixed authoritative manifest ancestry, `docs/685-workstation-finite-collection-handoff-selected-roots-stay-overlap-free-and-no-silent-subsumption.md` already fixed the accepted selected-root set as overlap-free reviewed state, `docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md` already fixed fresh-rooted retrieve/materialization, `docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md` already fixed profile scope, `docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md` already fixed the first-implementation collision answer, `docs/689-workstation-finite-collection-handoff-review-ui-may-path-compress-deterministic-ancestor-only-runs.md` already fixed the first bounded legibility move, `docs/690-workstation-finite-collection-handoff-advisory-mime-stays-optional-and-non-authoritative.md` already fixed metadata posture, `docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md` already fixed success receipts on the exact created fresh root, `docs/692-workstation-finite-collection-handoff-placement-hints-stay-advisory-and-receiver-local.md` already fixed placement hints as receiver-local advisory UI state instead of reviewed authority, `docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md` already fixed authoritative local result location as handle-first while any path/display snapshot stays advisory only, and `docs/694-workstation-finite-collection-handoff-advisory-display-snapshot-stays-retrieve-frozen.md` already fixed those optional display snapshots as retrieve-frozen when present.

This doc makes the next small but high-leverage locator-hardening decision explicit:
**the authoritative result-root handle should stay opaque and non-path-shaped, not a dressed-up local path string or URI.**

See also:
- ADR: `adrs/ADR-0285-workstation-finite-collection-handoff-result-root-handle-stays-opaque-and-non-path-shaped.md`
- draft RFC: `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- result-root-locator cut: `docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md`
- display-snapshot continuity cut: `docs/694-workstation-finite-collection-handoff-advisory-display-snapshot-stays-retrieve-frozen.md`
- bookmark/capability analog: `docs/198-persistent-file-capabilities-bookmarks.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`

## Why this needs a hard decision

`docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md` already fixed that the original retrieve outcome should be joined through a receiver-local stable result-root handle rather than mutable path text.
But one loophole remains: **what stops the contract-visible handle itself from just being a path string with a more respectable field name?**

If the archive leaves that open, honest implementations can still drift in expensive ways:

- one emits an opaque local id,
- one copies the current filesystem path into the handle field,
- one emits a URI or bookmark-like reopen locator,
- and one reuses a sender-visible reviewed name or destination label as the authoritative local join.

Those are not harmless renderer differences.
They decide whether the first richer lane really stayed handle-first or merely renamed path folklore into a new slot.

## Accepted cut

For the first cut of the reviewed finite-collection handoff family:

- the authoritative result-root handle stays **receiver-local and stable** for the original retrieve outcome
- the contract-visible handle must be **opaque and non-path-shaped**
- the handle must **not** be a filesystem path, URI, sender-provided reviewed name, destination-label string, or other human-facing placement text reused as the authoritative locator
- implementations may back the handle with bookmark ids, document ids, database keys, filesystem-handle adapters, or other local mechanisms, but those backend details stay non-normative as long as the exported/receipted handle remains opaque and non-path-shaped
- any human-facing path string, destination label, or display snapshot remains advisory only and follows `docs/694-workstation-finite-collection-handoff-advisory-display-snapshot-stays-retrieve-frozen.md` when present
- any later lane that wants portable destination paths, bookmark-like reopen semantics, or path-derived authoritative locator text is a **later explicit RFC/ADR cut**

## Why this is the right next cut

### 1) It actually makes the earlier handle-first decision stick

Without this cut, an implementation can satisfy the letter of `docs/693...` while still making the “handle” a mutable path string in practice.
Opaque non-path-shaped handles close that loophole.

### 2) It preserves the already accepted path/display split

`docs/693...` already made display/path text descriptive only, and `docs/694...` already froze any optional retrieve-time display snapshot.
This doc keeps those decisions coherent by ensuring the authoritative slot does not quietly become a second path/display surface.

### 3) It keeps future reopen/bookmark work explicit

The archive may later decide that some richer lane deserves bookmark-like reopen semantics or stronger portability.
That is still possible.
This cut simply prevents those larger semantics from sneaking into the first reviewed retrieve lane under a path-shaped “handle.”

## What this still does not decide

This doc does **not** define final schema field names.
It does **not** require one specific local storage backend for the opaque handle.
It does **not** settle whether some export/support surfaces should hash or redact the handle by default.
It does **not** require successor move/import/promote receipts to carry predecessor-handle joins.

Those remain follow-on questions, but the archive no longer leaves result-root handle posture loose enough to collapse back into pathname folklore.

## Related docs

- `docs/198-persistent-file-capabilities-bookmarks.md`
- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md`
- `docs/694-workstation-finite-collection-handoff-advisory-display-snapshot-stays-retrieve-frozen.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`

Last updated: 2026-03-23r427

For the canonical current-stack map over the recent `docs/674-*` through `docs/696-*` reviewed finite-collection tightening cluster, see `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full current companion list.
