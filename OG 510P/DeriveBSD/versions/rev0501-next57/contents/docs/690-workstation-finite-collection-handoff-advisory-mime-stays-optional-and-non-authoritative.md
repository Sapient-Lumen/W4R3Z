# Workstation finite collection handoff advisory MIME stays optional and non-authoritative

**Tier:** C (RFC shaping cut)  
**Profiles:** B, C, D  
**Pillars:** operability, reproducibility  
**Patterns:** Broker→Lease→Receipt

`docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md` already fixed the first richer workstation transfer queue, `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md` already fixed the first retrieve-width cut inside that richer lane, `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md` already fixed the first directory-semantics cut, `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md` already fixed the first snapshot-representation cut, `docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md` already fixed the first access-mode cut, `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md` already fixed the first member-kind floor, `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md` already fixed the first exact manifest-entry floor, `docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md` already fixed deterministic authoritative manifest ordering, `docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md` already fixed the first authoritative compact collection identity, `docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md` already fixed normalized review-path grammar, `docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md` already fixed top-level reviewed names as explicit reviewed state, `docs/684-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md` already fixed authoritative manifest ancestry, `docs/685-workstation-finite-collection-handoff-selected-roots-stay-overlap-free-and-no-silent-subsumption.md` already fixed the accepted selected-root set as overlap-free reviewed state, `docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md` already fixed fresh-rooted retrieve/materialization, `docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md` already fixed profile scope, `docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md` already fixed the first-implementation collision answer, and `docs/689-workstation-finite-collection-handoff-review-ui-may-path-compress-deterministic-ancestor-only-runs.md` already fixed the first bounded legibility move.

This doc makes the next small but hard metadata decision explicit:
**advisory MIME stays optional descriptive metadata and does not become authoritative reviewed identity for the first richer lane.**

See also:
- ADR: `adrs/ADR-0280-workstation-finite-collection-handoff-advisory-mime-stays-optional-and-non-authoritative.md`
- Draft RFC: `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- manifest-entry floor: `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md`
- review-surface cut: `docs/689-workstation-finite-collection-handoff-review-ui-may-path-compress-deterministic-ancestor-only-runs.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`

## Why this needs a hard decision

The archive already decided that reviewed identity in the first richer lane is path/kind/payload-first.
If MIME remains a maybe-mandatory field, the first implementation quietly inherits detector behavior, registry drift, filename folklore, or policy-local classification quirks that the archive has not standardized.
That would make the supposedly portable authoritative manifest heavier and less explainable than the current floor actually requires.

The high-leverage move is to keep MIME available as a hint when implementations want it, but to keep it out of the first authoritative identity contract.
That preserves portability while leaving stronger classification for a later explicit lane if practice proves it necessary.

## Accepted cut

For the first implementation/review surface of the reviewed finite collection handoff family:

- advisory MIME stays **optional descriptive metadata**
- advisory MIME is **not authoritative reviewed identity**
- a valid first-cut manifest is complete without MIME when the accepted normalized review path + member kind + payload digest/byte-length floor is present
- if present, advisory MIME must not override member kind, payload digest, byte length, review-path rules, or any existing fail-closed decision
- implementations must not require a MIME detector, MIME registry, filename-extension table, or broker-local classification service to produce or verify the first-cut authoritative manifest
- any stronger mandatory content-classification contract is a **later explicit RFC/ADR cut**

## Why this is the right first cut

### 1) It keeps reviewed identity small and portable

The first richer lane already has enough exact state to be useful.
Making MIME mandatory now would add variability without solving the core reviewed-membership problem.

### 2) It preserves path/kind/payload-first reasoning

The archive has been carefully stripping hidden authority out of this lane.
Treating MIME as optional descriptive metadata continues that pattern instead of reopening identity around host-local classifiers.

### 3) It leaves room for later stronger lanes

Some future workflows may want stronger reviewed content classification.
That work is easier to design honestly if it arrives as an explicit later lane rather than as silent inflation of this baseline.

## What this still does not decide

This doc does **not** forbid implementations from computing advisory MIME.
It does **not** standardize one canonical MIME vocabulary when hints are present.
It does **not** make review UIs ignore descriptive MIME entirely.
It does **not** decide later richer metadata such as owner/mode/mtime/xattr fidelity.

Those remain separate questions, but the archive no longer leaves the first metadata posture ambiguous.

## Related docs

- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md`
- `docs/689-workstation-finite-collection-handoff-review-ui-may-path-compress-deterministic-ancestor-only-runs.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`

Last updated: 2026-03-23r427

For the canonical current-stack map over the recent `docs/674-*` through `docs/696-*` reviewed finite-collection tightening cluster, see `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full current companion list.
