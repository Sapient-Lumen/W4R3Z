# Workstation finite collection handoff advisory display snapshot stays retrieve-frozen

**Tier:** C (RFC shaping cut)  
**Profiles:** B, C, D  
**Pillars:** operability, isolation  
**Patterns:** Broker→Lease→Receipt

`docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md` already fixed the first richer workstation transfer queue, `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md` already fixed the first retrieve-width cut inside that richer lane, `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md` already fixed the first directory-semantics cut, `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md` already fixed the first snapshot-representation cut, `docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md` already fixed the first access-mode cut, `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md` already fixed the first member-kind floor, `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md` already fixed the first exact manifest-entry floor, `docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md` already fixed deterministic authoritative manifest ordering, `docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md` already fixed the first authoritative compact collection identity, `docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md` already fixed normalized review-path grammar, `docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md` already fixed top-level reviewed names as explicit reviewed state, `docs/684-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md` already fixed authoritative manifest ancestry, `docs/685-workstation-finite-collection-handoff-selected-roots-stay-overlap-free-and-no-silent-subsumption.md` already fixed the accepted selected-root set as overlap-free reviewed state, `docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md` already fixed fresh-rooted retrieve/materialization, `docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md` already fixed profile scope, `docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md` already fixed the first-implementation collision answer, `docs/689-workstation-finite-collection-handoff-review-ui-may-path-compress-deterministic-ancestor-only-runs.md` already fixed the first bounded legibility move, `docs/690-workstation-finite-collection-handoff-advisory-mime-stays-optional-and-non-authoritative.md` already fixed metadata posture, `docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md` already fixed success receipts on the exact created fresh root, `docs/692-workstation-finite-collection-handoff-placement-hints-stay-advisory-and-receiver-local.md` already fixed placement hints as receiver-local advisory UI state instead of reviewed authority, and `docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md` already fixed authoritative local result location as handle-first while any path/display snapshot stays advisory only.

This doc makes the next small but practical continuity decision explicit:
**if a richer-lane retrieve receipt carries any advisory human-facing path/display snapshot, that text stays retrieve-frozen rather than silently rewriting itself after later local moves or renames.**

See also:
- ADR: `adrs/ADR-0284-workstation-finite-collection-handoff-advisory-display-snapshot-stays-retrieve-frozen.md`
- draft RFC: `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- result-root receipt cut: `docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md`
- placement-hint cut: `docs/692-workstation-finite-collection-handoff-placement-hints-stay-advisory-and-receiver-local.md`
- result-root-locator cut: `docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md`
- publish-session analog: `docs/594-publish-session-published-endpoint-surface-stays-lease-frozen.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`

## Why this needs a hard decision

`docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md` already fixed that any human-facing path/display text is **not authoritative local location**.
But that still leaves one support/UI ambiguity open: **if such text exists at all, is it describing the original retrieve or the latest local location?**

If the archive leaves that open, honest implementations can still drift in expensive ways:

- one records the retrieve-time path/display snapshot once,
- one rewrites the old receipt after a local rename,
- one shows only a current path while claiming it still describes the original retrieve,
- and one redacts or shortens the text on export without making clear that the authoritative join never moved.

Those are not harmless renderer differences.
They decide whether human-facing evidence attached to the original retrieve stays stable enough for support/export or turns back into local-history folklore.

## Accepted cut

For the first cut of the reviewed finite-collection handoff family:

- when a successful retrieve receipt carries any advisory human-facing path string, destination label, or display-path snapshot for the created fresh root, that text is a **retrieve-time snapshot**
- that advisory snapshot is **retrieve-frozen** for the lifetime of the original retrieve receipt; later local rename/move/import/promote actions do **not** silently rewrite it in place
- later acts may mint their own receipts with their own current human-facing path/display snapshots, but those are successor observations rather than retroactive edits of the original retrieve outcome
- the original retrieve receipt remains valid even when the advisory snapshot is absent, redacted, shortened, or filtered on some export/support surface
- the authoritative local result locator remains the receiver-local stable result-root handle; this cut only freezes optional descriptive text so it cannot drift under that same handle
- `docs/695-workstation-finite-collection-handoff-result-root-handle-stays-opaque-and-non-path-shaped.md` then fixes the adjacent handle-posture loophole too: the authoritative handle itself must stay **opaque and non-path-shaped** rather than quietly becoming another path/display surface
- any later lane that wants one mutable current-location story, durable bookmark semantics, or automatic “latest local path” projection is a **later explicit RFC/ADR cut**

## Why this is the right next cut

### 1) It keeps human-facing retrieve evidence stable without promoting it into authority

The archive already decided that the handle is authoritative and the display text is advisory.
This doc keeps the advisory text useful by making it clearly describe the retrieve-time observation rather than a moving current-location guess.

### 2) It lines up with an existing frozen-surface pattern

`docs/594-publish-session-published-endpoint-surface-stays-lease-frozen.md` already fixed an adjacent lesson elsewhere in the archive: copied/bookmarked/support-facing human surfaces stay more coherent when one bounded authority instance does not silently mutate under them.
The richer finite-collection lane should use the same move for its optional advisory display snapshot.

### 3) It keeps later move/import/promote lanes honest

If a later lane wants to tell the story of where the tree lives **now**, it can mint its own receipt.
That is cleaner than letting later local state silently rewrite the only human-facing note attached to the original retrieve.

## What this still does not decide

This doc does **not** require implementations to emit an advisory display snapshot at all.
It does **not** define the exact schema field names for that snapshot.
It does **not** require later move/import/promote receipts to reuse the same wording or formatting.
It does **not** settle profile-specific redaction policy for advisory display text.

Those remain follow-on questions, but the archive no longer leaves advisory display snapshots free to drift under one retrieve story.

## Related docs

- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/594-publish-session-published-endpoint-surface-stays-lease-frozen.md`
- `docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md`
- `docs/692-workstation-finite-collection-handoff-placement-hints-stay-advisory-and-receiver-local.md`
- `docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md`
- `docs/695-workstation-finite-collection-handoff-result-root-handle-stays-opaque-and-non-path-shaped.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`

Last updated: 2026-03-23r427

For the canonical current-stack map over the recent `docs/674-*` through `docs/696-*` reviewed finite-collection tightening cluster, see `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full current companion list.
