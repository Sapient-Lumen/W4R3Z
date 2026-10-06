# Workstation finite collection handoff authoritative collection identity stays digest-bound to canonical manifest

**Tier:** C (RFC shaping cut)  
**Profiles:** B, C, D  
**Pillars:** reproducibility, operability  
**Patterns:** Broker→Lease→Receipt

`docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md` already fixed the first richer workstation transfer queue, `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md` already fixed the first retrieve-width cut inside that richer lane, `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md` already fixed the first directory-semantics cut, `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md` already fixed the first snapshot-representation cut, `docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md` already fixed the first access-mode cut, `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md` already fixed the first member-kind floor, `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md` already fixed the first exact manifest-entry floor, and `docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md` already fixed deterministic authoritative manifest ordering.

This doc makes the next small but hard decision inside that RFC queue explicit:
**the first cut of the reviewed finite collection handoff now carries one authoritative manifest digest computed from the canonical serialized explicit manifest, while tree/collection summary digests stay supplementary rather than becoming the real compact identity.**

See also:
- ADR: `adrs/ADR-0271-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md`
- Draft RFC: `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- queueing cut: `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- retrieve-width cut: `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md`
- directory-semantics cut: `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md`
- manifest-first cut: `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md`
- member-kind floor: `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md`
- manifest-field floor: `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md`
- manifest-order cut: `docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md`
- review-path grammar cut: `docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md`
- canonical JSON rule: `adrs/ADR-0022-canonical-json-jcs.md`
- distinct-family intake rule: `docs/672-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`

## Why this needs a hard decision

Once the first richer lane already has an explicit reviewed per-member manifest and a canonical manifest order, the next drift seam is compact identity. If the archive leaves that implicit, one implementation will hash a UI-order JSON blob, another will hash a tree summary, and a third will recompute a tree digest from the source filesystem. That would make grants, receipts, detached review, compare/export, and support bundles less reproducible even when the reviewed finite set is identical.

The higher-leverage move is to keep the first richer lane boring:
**one authoritative manifest digest, computed from the canonical serialized authoritative manifest, and reused everywhere that needs a compact handle for the reviewed finite set.**

## Accepted cut

For the first cut of the reviewed finite collection handoff RFC:

- the reviewed finite set carries one authoritative compact identity: an **authoritative manifest digest**
- that digest is computed over the canonical serialized authoritative manifest, after the accepted field-floor and canonical normalized-review-path ordering rules have already been applied
- the digest rule follows the archive's canonical JSON posture: **`sha256(utf8(JCS(authoritative_manifest)))`**
- detached review, grants, receipts, compare/export tooling, and support bundles should reuse that authoritative manifest digest as the portable compact handle for the reviewed collection
- aggregate tree/collection digests may still exist as **supplementary summary evidence**, but they are not the authoritative compact identity in the first cut
- UI order, traversal order, or implementation-local tree-hash schemes are not alternative authoritative identities for the same reviewed set

That gives the archive a compact identity it can actually wire into future specs without reopening the already-decided manifest-first boundary.

## Why this is the right first cut

### 1) It makes receipt joins and detached evidence portable

A support bundle or detached receipt should be able to say “this exact reviewed finite set” without asking which broker or filesystem enumerator produced it. A canonical manifest digest gives the archive that compact answer.

### 2) It reuses the archive’s existing canonicalization discipline

DeriveBSD already relies on JCS-canonical JSON for portable digest/signature surfaces elsewhere. Reusing the same rule here keeps the richer lane aligned with the archive’s broader deterministic-by-default posture.

### 3) It keeps tree-summary evidence secondary

Tree/collection summaries can still help humans or later tooling, but they should not become the real identity surface by compactness alone. The explicit reviewed manifest stays authoritative; the digest simply gives that authoritative surface a portable short handle.

## What this still does not decide

This doc does **not** finalize the richer lane schema family.
It does **not** finalize the exact future field names that will carry the authoritative manifest digest.
It does **not** decide whether advisory MIME type should become mandatory later.
It does **not** decide whether any later lane should preserve owner/mode/mtime/xattr fidelity or richer tree-summary evidence.
It does **not** decide whether profile A should ever expose this richer lane under explicit operator posture.

Those remain explicit follow-on questions, but the archive no longer leaves compact collection identity ambiguous.

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
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`

Last updated: 2026-03-23r427

For the canonical current-stack map over the recent `docs/674-*` through `docs/696-*` reviewed finite-collection tightening cluster, see `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full current companion list.
